# component_id: sequence_rules
# kind: runtime_module
# area: enforcement
# status: draft
# authority_level: 5
# version: 2.0.0
# license: Apache-2.0
# purpose: Evaluate ordering constraints in runtime event sequences.

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

PLDEvent = Mapping[str, Any]


# ──────────────────────────────────────────────────────────────────────────────
# TODO (Open Question #1): Sorting cost vs. external guarantee:
#   Should Level 5 assume caller gives turn_sequence-sorted input to avoid O(N log N)?
#
# TODO (Open Question #2): Replace assert for session_id contract enforcement?
#   If assertions are disabled, enforcement disappears. Should this be a guaranteed runtime exception instead?
#
# TODO (Open Question #3): Observability classification SHOULD be replaced with
#   taxonomy-driven lookup rather than heuristic fallback.
#
# TODO (Open Question #4): Clarify whether session_id MUST be globally unique.
#   If reused across parallel sessions, validation merges unrelated event streams.
#
# TODO (Open Question #5): Allowed recovery events SHOULD be sourced from the
#   event matrix or taxonomy. Parameterization implemented here is a temporary fix.
# ──────────────────────────────────────────────────────────────────────────────


class SequenceSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass(frozen=True)
class SequenceRuleViolation:
    rule_id: str
    severity: SequenceSeverity
    message: str
    session_id: Optional[str]
    turn_sequence: Optional[int]
    event_index: Optional[int]
    event_type: Optional[str]
    details: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class SequenceValidationResult:
    session_id: str
    is_valid: bool
    violations: List[SequenceRuleViolation]


def evaluate_sequence_rules(
    events: Sequence[PLDEvent],
    observability_classifier: Optional[Callable[[Optional[str], Optional[str]], bool]] = None,
    allowed_recovery_events: Optional[Sequence[str]] = None,   # <-- Core Issue #1 resolved
) -> List[SequenceValidationResult]:
    """
    Evaluate lifecycle ordering rules for grouped PLD events.

    Core Fixes:
    - The set of allowed recovery events is now caller-controlled rather than
      hardcoded, resolving the evolvability issue.
      If not supplied, a safe default aligned with v2.0 is applied.
    """
    if allowed_recovery_events is None:
        allowed_recovery_events = ("reentry_observed", "continue_allowed", "session_closed")

    by_session: Dict[str, List[Tuple[int, PLDEvent]]] = {}

    for idx, ev in enumerate(events):
        session_id = ev.get("session_id")

        # Contract relies on L1/L2 compliance. Assertion retained per spec intent.
        assert isinstance(session_id, str) and session_id.strip(), (
            "Invalid event: session_id must be non-empty after Level 1 validation."
        )

        by_session.setdefault(session_id, []).append((idx, ev))

    results: List[SequenceValidationResult] = []

    for session_id, indexed_events in by_session.items():
        violations = _evaluate_session_sequence(
            session_id,
            indexed_events,
            observability_classifier,
            set(allowed_recovery_events),  # normalized to set
        )
        is_valid = not any(v.severity is SequenceSeverity.ERROR for v in violations)
        results.append(SequenceValidationResult(session_id, is_valid, violations))

    return results


def _evaluate_session_sequence(
    session_id: str,
    indexed_events: List[Tuple[int, PLDEvent]],
    observability_classifier: Optional[Callable[[Optional[str], Optional[str]], bool]],
    allowed_recovery_events: set[str],
) -> List[SequenceRuleViolation]:

    violations: List[SequenceRuleViolation] = []

    violations.extend(_check_turn_sequence_monotonicity(session_id, indexed_events))
    violations.extend(_check_session_closed_terminal(session_id, indexed_events, observability_classifier))
    violations.extend(_check_failover_recovery_path(session_id, indexed_events, observability_classifier, allowed_recovery_events))

    # Multiple closure rule still enforced
    closure_count = sum(1 for _, ev in indexed_events if ev.get("event_type") == "session_closed")
    if closure_count > 1:
        violations.append(
            SequenceRuleViolation(
                rule_id="SR-004",
                severity=SequenceSeverity.ERROR,
                message="Multiple session_closed events detected; closure MUST be unique.",
                session_id=session_id,
                turn_sequence=None,
                event_index=None,
                event_type="session_closed",
                details={"count": closure_count},
            )
        )

    return violations


def _check_turn_sequence_monotonicity(session_id: str, indexed_events: List[Tuple[int, PLDEvent]]) -> List[SequenceRuleViolation]:
    violations: List[SequenceRuleViolation] = []
    last_ts: Optional[int] = None

    for idx, ev in indexed_events:
        turn = ev.get("turn_sequence")
        assert isinstance(turn, int), "turn_sequence MUST be integer after Level 1 validation."

        if last_ts is not None and turn <= last_ts:
            violations.append(
                SequenceRuleViolation(
                    rule_id="SR-001",
                    severity=SequenceSeverity.ERROR,
                    message="turn_sequence MUST strictly increase within session.",
                    session_id=session_id,
                    turn_sequence=turn,
                    event_index=idx,
                    event_type=ev.get("event_type"),
                    details={"previous_turn_sequence": last_ts},
                )
            )
        last_ts = turn

    return violations


def _check_session_closed_terminal(
    session_id: str,
    indexed_events: List[Tuple[int, PLDEvent]],
    observability_classifier: Optional[Callable[[Optional[str], Optional[str]], bool]],
) -> List[SequenceRuleViolation]:

    violations: List[SequenceRuleViolation] = []
    closure_turn = max(
        (ev.get("turn_sequence") for _, ev in indexed_events if ev.get("event_type") == "session_closed"),
        default=None,
    )
    if closure_turn is None:
        return violations

    for idx, ev in indexed_events:
        turn = ev.get("turn_sequence")
        assert isinstance(turn, int), "turn_sequence MUST be integer after Level 1 validation."

        if turn <= closure_turn:
            continue

        etype = ev.get("event_type")
        phase = (ev.get("pld") or {}).get("phase")

        if _is_observability_or_info(etype, phase, observability_classifier):
            severity = SequenceSeverity.WARNING
            rule_id = "SR-002B"
            message = "Event after session_closed is observability/info."
        else:
            severity = SequenceSeverity.ERROR
            rule_id = "SR-002A"
            message = "Lifecycle event emitted after terminal session_closed."

        violations.append(
            SequenceRuleViolation(
                rule_id=rule_id,
                severity=severity,
                message=message,
                session_id=session_id,
                turn_sequence=turn,
                event_index=idx,
                event_type=etype,
                details={"terminal_turn": closure_turn},
            )
        )

    return violations


def _check_failover_recovery_path(
    session_id: str,
    indexed_events: List[Tuple[int, PLDEvent]],
    observability_classifier: Optional[Callable[[Optional[str], Optional[str]], bool]],
    allowed_recovery_events: set[str],
) -> List[SequenceRuleViolation]:
    violations: List[SequenceRuleViolation] = []

    # Core Issue #2: Sorting required to ensure correct next-event logic.
    sorted_events = sorted(indexed_events, key=lambda pair: pair[1].get("turn_sequence", 0))

    for pos, (orig_idx, ev) in enumerate(sorted_events):
        if ev.get("event_type") != "failover_triggered":
            continue

        failover_turn = ev.get("turn_sequence")
        assert isinstance(failover_turn, int)

        next_event = None
        next_idx = None

        for j in range(pos + 1, len(sorted_events)):
            c_idx, cand = sorted_events[j]
            c_type = cand.get("event_type")
            c_phase = (cand.get("pld") or {}).get("phase")

            if _is_observability_or_info(c_type, c_phase, observability_classifier):
                continue

            next_event = cand
            next_idx = c_idx
            break

        if next_event is None:
            violations.append(
                SequenceRuleViolation(
                    rule_id="SR-003C",
                    severity=SequenceSeverity.WARNING,
                    message="No lifecycle recovery event after failover_triggered.",
                    session_id=session_id,
                    turn_sequence=failover_turn,
                    event_index=orig_idx,
                    event_type="failover_triggered",
                    details={"allowed_expected": sorted(allowed_recovery_events)},
                )
            )
            continue

        recovery_type = next_event.get("event_type")
        recovery_turn = next_event.get("turn_sequence")
        assert isinstance(recovery_turn, int)

        if recovery_type not in allowed_recovery_events:
            violations.append(
                SequenceRuleViolation(
                    rule_id="SR-003A",
                    severity=SequenceSeverity.ERROR,
                    message="Invalid lifecycle transition after failover_triggered.",
                    session_id=session_id,
                    turn_sequence=recovery_turn,
                    event_index=next_idx,
                    event_type=recovery_type,
                    details={"allowed_recovery_events": sorted(allowed_recovery_events)},
                )
            )

    return violations


# ──────────────────────────────────────────────────────────────────────────────
# Observability classification (pluggable, heuristic fallback)
# ──────────────────────────────────────────────────────────────────────────────

def _is_observability_or_info(
    event_type: Optional[str],
    phase: Optional[str],
    classifier: Optional[Callable[[Optional[str], Optional[str]], bool]] = None,
) -> bool:
    """
    Core Issue #2: Safety refinement — heuristic tightened to positive-value rule.

    Instead of allowing ANY unexpected phase to be treated as observability,
    the logic now explicitly checks known-safe observability cases.

    This reduces unintended classification for unknown phases.
    """
    if classifier is not None:
        return classifier(event_type, phase)

    if event_type is None:
        return False

    if event_type in ("latency_spike", "pause_detected", "handoff", "info"):
        return True

    # fallback_executed is observability ONLY when explicitly in non-failover context.
    if event_type == "fallback_executed" and phase in {"none", "continue", "reentry", "outcome"}:
        return True

    return False


