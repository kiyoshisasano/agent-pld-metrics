# path: examples/dashboard/app.py
# component_id: pld_metrics_dashboard_app
# kind: example
# area: metrics
# status: experimental
# authority_level: 2
# version: 2.0.0
# license: Apache-2.0
# purpose: Text-based analytics dashboard demo for PRDR, VRL, and FR over PLD v2 events.
# maintainer: TBD

#!/usr/bin/env python
"""
examples/dashboard/app.py

PLD Operational Metrics Demo Dashboard (Text-Only)

This example script:

  * Reads PLD v2 runtime events from a JSONL log file
  * Groups events by session_id
  * Computes analytics-layer metrics related to:
      - PRDR  (Post-Repair Drift Recurrence)
      - VRL   (Recovery Latency)
      - FR    (Failover Recurrence)
  * Prints a textual dashboard-style summary to stdout

IMPORTANT:
  - This module operates strictly as an ANALYTICS-LAYER example.
  - It DOES NOT mutate PLD events or redefine Level 1–3 semantics.
  - It only reads already-emitted PLD-compliant events and derives
    advisory metrics from them.

Default input:
  quickstart/metrics_quickcheck/pld_events_demo.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from statistics import mean
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class Event:
    """Thin wrapper around a raw PLD event dict.

    This wrapper never mutates the underlying event structure; it only exposes
    convenience accessors for fields used by the demo dashboard.
    """

    raw: Dict[str, Any]

    @property
    def schema_version(self) -> Optional[str]:
        return self.raw.get("schema_version")

    @property
    def session_id(self) -> Optional[str]:
        return self.raw.get("session_id")

    @property
    def event_id(self) -> Optional[str]:
        return self.raw.get("event_id")

    @property
    def turn_sequence(self) -> Optional[int]:
        return self.raw.get("turn_sequence")

    @property
    def event_type(self) -> Optional[str]:
        return self.raw.get("event_type")

    @property
    def phase(self) -> Optional[str]:
        pld = self.raw.get("pld") or {}
        return pld.get("phase")

    @property
    def code(self) -> Optional[str]:
        pld = self.raw.get("pld") or {}
        return pld.get("code")

    @property
    def timestamp(self) -> Optional[str]:
        return self.raw.get("timestamp")

    @property
    def payload(self) -> Dict[str, Any]:
        payload = self.raw.get("payload")
        return payload if isinstance(payload, dict) else {}

    @property
    def ux(self) -> Dict[str, Any]:
        ux = self.raw.get("ux")
        return ux if isinstance(ux, dict) else {}


@dataclass
class SessionTrace:
    """Container for all events belonging to a single session_id."""

    session_id: str
    events: List[Event] = field(default_factory=list)

    def sorted_events(self) -> List[Event]:
        """Return events sorted by turn_sequence, then timestamp.

        PLD-compliant events SHOULD always have turn_sequence >= 1 and a
        monotonically increasing sequence within a session. For robustness
        when facing partial or slightly malformed logs, this method also
        uses timestamp as a secondary key and places events without a
        turn_sequence after those that do have one.
        """

        def _key(e: Event) -> Tuple[bool, int, str]:
            # Events with a missing turn_sequence are sorted last (True > False).
            missing_turn = e.turn_sequence is None
            turn = e.turn_sequence if e.turn_sequence is not None else 0
            # ISO-8601 UTC timestamps sort lexicographically, so we can use
            # the raw string as a secondary key. When missing, treat as empty.
            ts = e.timestamp or ""
            return (missing_turn, turn, ts)

        return sorted(self.events, key=_key)

    def lifecycle_events(self) -> List[Event]:
        """Events with a lifecycle phase (phase != 'none')."""
        return [e for e in self.events if e.phase and e.phase != "none"]

    def is_closed(self) -> bool:
        """Return True if this session has an explicit session_closed event.

        This is used to avoid treating incomplete (rolling) sessions as
        successfully resolved when computing PRDR / VRL / FR aggregates.
        """
        return any(e.event_type == "session_closed" for e in self.events)

    def has_repair(self) -> bool:
        return any(
            e.event_type in ("repair_triggered", "repair_escalated")
            for e in self.events
        )

    def has_post_repair_drift(self) -> bool:
        """Return True if any drift occurs AFTER a repair in this session.

        This helper implements the canonical PRDR session-level test:
        "a session contains at least one repair event, and any drift event
        appears after that repair" (event_type-level only). It does NOT
        attempt to match taxonomy codes or drift domains; those would be
        separate, more granular metrics.
        """
        events = self.sorted_events()
        first_repair_turn: Optional[int] = None
        for e in events:
            if e.event_type in ("repair_triggered", "repair_escalated"):
                first_repair_turn = e.turn_sequence
                break

        if first_repair_turn is None:
            return False

        for e in events:
            if (
                e.event_type in ("drift_detected", "drift_escalated")
                and e.turn_sequence is not None
                and e.turn_sequence > first_repair_turn
            ):
                return True
        return False

    def failover_events(self) -> List[Event]:
        """Failover-related events for FR metric.

        We treat:
          - event_type == 'failover_triggered'
          - event_type == 'fallback_executed' with phase == 'failover'
        as failover events.
        """
        events: List[Event] = []
        for e in self.events:
            if e.event_type == "failover_triggered":
                events.append(e)
            elif e.event_type == "fallback_executed" and e.phase == "failover":
                events.append(e)
        return events


@dataclass
class MetricsSummary:
    """Aggregated metrics across all sessions."""

    num_sessions: int
    prdr_sessions_with_repair: int
    prdr_sessions_with_post_repair_drift: int
    vrl_samples_seconds: List[float] = field(default_factory=list)
    fr_failover_events: int = 0
    fr_lifecycle_events: int = 0

    @property
    def prdr_percent(self) -> Optional[float]:
        if self.prdr_sessions_with_repair == 0:
            return None
        return 100.0 * (
            self.prdr_sessions_with_post_repair_drift / self.prdr_sessions_with_repair
        )

    @property
    def vrl_mean_seconds(self) -> Optional[float]:
        if not self.vrl_samples_seconds:
            return None
        return mean(self.vrl_samples_seconds)

    @property
    def fr_ratio(self) -> Optional[float]:
        if self.fr_lifecycle_events == 0:
            return None
        return self.fr_failover_events / self.fr_lifecycle_events


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------


def _parse_iso8601(s: str) -> datetime:
    """Parse an ISO-8601/RFC3339 timestamp string as UTC.

    This helper assumes that PLD runtime events emit timestamps in UTC, either
    with a trailing 'Z' or with an explicit offset. If a naive timestamp
    (without offset) is provided, it is interpreted as UTC for the purpose
    of delta computations in this demo dashboard. This keeps the example
    simple but may not be appropriate when correlating with external logs
    that use local timezones.
    """
    # Python's fromisoformat does not accept bare 'Z', so normalize it.
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        # Assume UTC if no timezone provided
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


# ---------------------------------------------------------------------------
# IO & grouping
# ---------------------------------------------------------------------------


def load_events_from_jsonl(path: str) -> List[Event]:
    """Load PLD events from a JSONL file.

    Lines containing a metadata envelope ({"_meta": true, ...}) are skipped.
    """
    events: List[Event] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError as exc:
                    print(
                        f"[WARN] Skipping invalid JSON on line {line_no}: {exc}",
                        file=sys.stderr,
                    )
                    continue

                if isinstance(obj, Mapping) and obj.get("_meta"):
                    # Treat metadata records as file-level metadata, not events.
                    continue

                if not isinstance(obj, dict):
                    print(
                        f"[WARN] Skipping non-object record on line {line_no}",
                        file=sys.stderr,
                    )
                    continue

                events.append(Event(raw=obj))
    except FileNotFoundError:
        print(f"[ERROR] File not found: {path}", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"[ERROR] Failed to read file {path}: {exc}", file=sys.stderr)
        sys.exit(1)

    return events


def group_events_by_session(events: Iterable[Event]) -> Dict[str, SessionTrace]:
    """Group events by session_id, returning a mapping of session_id → SessionTrace."""
    sessions: Dict[str, SessionTrace] = {}
    for e in events:
        sid = e.session_id
        if not sid:
            # Ignore events without a session_id; they cannot participate in session metrics.
            continue
        if sid not in sessions:
            sessions[sid] = SessionTrace(session_id=sid)
        sessions[sid].events.append(e)
    return sessions


# ---------------------------------------------------------------------------
# Metrics computation
# ---------------------------------------------------------------------------


def compute_prdr(
    sessions: Iterable[SessionTrace],
    *,
    include_incomplete: bool = False,
) -> Tuple[int, int]:
    """Compute PRDR numerator and denominator across sessions.

    Returns:
        (sessions_with_repair, sessions_with_post_repair_drift)

    By default, sessions that do not contain a session_closed event are
    excluded to avoid falsely treating truncated (rolling) sessions as
    successful.
    """
    sessions_with_repair = 0
    sessions_with_post_repair_drift = 0

    for session in sessions:
        if not include_incomplete and not session.is_closed():
            continue

        if not session.has_repair():
            continue

        sessions_with_repair += 1
        if session.has_post_repair_drift():
            sessions_with_post_repair_drift += 1

    return sessions_with_repair, sessions_with_post_repair_drift


def _compute_vrl_samples_for_session(session: SessionTrace) -> List[float]:
    """Compute VRL samples (seconds) for a single session.

    We iterate through the sorted event stream and track drift→recovery
    episodes:

      drift_detected / drift_escalated
        → (zero or more repair events)
        → recovery_event in {continue_allowed, reentry_observed}

    For each such episode we compute:

      timestamp(recovery) - timestamp(drift)

    and append the value (seconds) to the session's sample list.

    failover_triggered events do NOT count as recovery; they are handled
    separately via FR (Failover Recurrence) metrics.
    """
    episodes: List[float] = []
    events = session.sorted_events()

    current_drift_event: Optional[Event] = None

    for e in events:
        etype = e.event_type

        if etype in ("drift_detected", "drift_escalated"):
            # Start a new drift episode only if we are not already in one.
            if current_drift_event is None:
                current_drift_event = e
            # If already in an episode, treat additional drift as part of the
            # same episode and ignore for VRL start purposes.
            continue

        if etype in ("continue_allowed", "reentry_observed"):
            # Candidate recovery event.
            if current_drift_event is None:
                continue

            if not current_drift_event.timestamp or not e.timestamp:
                # Missing timestamps → cannot compute a valid delta.
                current_drift_event = None
                continue

            try:
                t_drift = _parse_iso8601(current_drift_event.timestamp)
                t_recovery = _parse_iso8601(e.timestamp)
            except Exception:
                # If parsing fails, drop this episode and continue.
                current_drift_event = None
                continue

            delta = (t_recovery - t_drift).total_seconds()
            if delta >= 0:
                episodes.append(delta)

            # Close current episode; subsequent drift can start a new one.
            current_drift_event = None

        # All other event types, including failover_triggered, do not affect
        # VRL episode boundaries in this demo implementation.

    return episodes


def compute_vrl_samples(
    sessions: Iterable[SessionTrace],
    *,
    include_incomplete: bool = False,
) -> List[float]:
    """Compute VRL samples (seconds) across sessions.

    By default, only sessions that contain a session_closed event are
    considered, to avoid bias from truncated logs.
    """
    samples: List[float] = []

    for session in sessions:
        if not include_incomplete and not session.is_closed():
            continue

        samples.extend(_compute_vrl_samples_for_session(session))

    return samples


def compute_fr(
    sessions: Iterable[SessionTrace],
    *,
    include_incomplete: bool = False,
) -> Tuple[int, int]:
    """Compute FR components (failover_events, lifecycle_events).

    FR is defined as:
        # failover events / # lifecycle events (phase != "none")

    By default, only sessions with an explicit session_closed event are
    included in the aggregates.
    """
    failover_events = 0
    lifecycle_events = 0

    for session in sessions:
        if not include_incomplete and not session.is_closed():
            continue

        failover_events += len(session.failover_events())
        lifecycle_events += len(session.lifecycle_events())

    return failover_events, lifecycle_events


def compute_metrics_summary(session_map: Dict[str, SessionTrace]) -> MetricsSummary:
    sessions = list(session_map.values())
    num_sessions = len(sessions)

    prdr_den, prdr_num = compute_prdr(sessions)
    vrl_samples = compute_vrl_samples(sessions)
    fr_failover, fr_lifecycle = compute_fr(sessions)

    return MetricsSummary(
        num_sessions=num_sessions,
        prdr_sessions_with_repair=prdr_den,
        prdr_sessions_with_post_repair_drift=prdr_num,
        vrl_samples_seconds=vrl_samples,
        fr_failover_events=fr_failover,
        fr_lifecycle_events=fr_lifecycle,
    )


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def format_float(value: Optional[float], *, digits: int = 2) -> str:
    if value is None:
        return "N/A"
    return f"{value:.{digits}f}"


def render_metrics_summary(metrics: MetricsSummary) -> str:
    lines: List[str] = []
    lines.append("=== Metrics Summary ===")
    lines.append(f"Sessions: {metrics.num_sessions}")
    lines.append(
        "PRDR (Post-Repair Drift Recurrence): "
        f"{format_float(metrics.prdr_percent)}%"
        f"  ({metrics.prdr_sessions_with_post_repair_drift}/"
        f"{metrics.prdr_sessions_with_repair} sessions with repair)"
    )
    lines.append(
        "VRL (Recovery Latency): "
        f"mean={format_float(metrics.vrl_mean_seconds)}s  "
        f"samples={len(metrics.vrl_samples_seconds)}"
    )
    lines.append(
        "FR (Failover Recurrence): "
        f"{format_float(metrics.fr_ratio)}  "
        f"(failover_events={metrics.fr_failover_events}, "
        f"lifecycle_events={metrics.fr_lifecycle_events})"
    )
    return "\n".join(lines)


def render_session_summary(session: SessionTrace) -> str:
    events = session.sorted_events()
    lines: List[str] = []
    lines.append(f"=== Session {session.session_id} ===")
    if not events:
        lines.append("(no events)")
        return "\n".join(lines)

    lines.append(
        f"status: {'closed' if session.is_closed() else 'incomplete (no session_closed event)'}"
    )
    lines.append("")
    lines.append(
        "turn | timestamp                | event_type         | phase     | code"
    )
    lines.append(
        "-----+--------------------------+--------------------+-----------+----------------------"
    )

    for e in events:
        turn = e.turn_sequence if e.turn_sequence is not None else "-"
        ts = (e.timestamp or "")[:26]  # trim for compact display
        etype = (e.event_type or "")[:18]
        phase = (e.phase or "")[:9]
        code = (e.code or "")[:22]
        lines.append(f"{turn:>4} | {ts:<24} | {etype:<18} | {phase:<9} | {code}")

    # Small per-session derived stats
    drift_count = sum(
        1 for e in events if e.event_type in ("drift_detected", "drift_escalated")
    )
    repair_count = sum(
        1 for e in events if e.event_type in ("repair_triggered", "repair_escalated")
    )
    cont_count = sum(
        1 for e in events if e.event_type in ("continue_allowed", "continue_blocked")
    )
    failover_count = len(session.failover_events())

    lines.append("")
    lines.append(
        f"drift_events={drift_count}, repair_events={repair_count}, "
        f"continue_events={cont_count}, failover_events={failover_count}"
    )
    lines.append(
        f"has_repair={session.has_repair()}, "
        f"has_post_repair_drift={session.has_post_repair_drift()}"
    )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Text-based PLD metrics dashboard example.\n"
            "Reads PLD v2 JSONL logs and prints PRDR/VRL/FR-style summaries."
        )
    )
    parser.add_argument(
        "-f",
        "--file",
        default="quickstart/metrics_quickcheck/pld_events_demo.jsonl",
        help=(
            "Path to a PLD JSONL events file "
            "(default: quickstart/metrics_quickcheck/pld_events_demo.jsonl)"
        ),
    )
    parser.add_argument(
        "-s",
        "--session",
        metavar="SESSION_ID",
        help="If provided, print details only for this session_id.",
    )
    parser.add_argument(
        "--no-sessions",
        action="store_true",
        help="Print only the metrics summary (omit per-session breakdown).",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    events = load_events_from_jsonl(args.file)
    if not events:
        print("[INFO] No events loaded; nothing to display.", file=sys.stderr)
        return 0

    session_map = group_events_by_session(events)
    metrics = compute_metrics_summary(session_map)

    # Metrics summary first
    print(render_metrics_summary(metrics))
    print("")

    if not args.no_sessions:
        if args.session:
            session = session_map.get(args.session)
            if not session:
                print(
                    f"[WARN] No session found with id={args.session}", file=sys.stderr
                )
            else:
                print(render_session_summary(session))
        else:
            # Print all sessions in sorted order
            for sid in sorted(session_map.keys()):
                print(render_session_summary(session_map[sid]))
                print("")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
