# =============================================================================
# repair detector
# version: 2.0.0
# status: experimental  # runtime template; subject to refinement
# authority_level: 5
# authority_scope: runtime implementation
# purpose: Provide a template for runtime repair detection and emitting PLD
#          v2-compliant repair events.
# change_classification: runtime-only, non-breaking (technical review alignment)
# dependencies: PLD event schema v2.0,
#               PLD Event Matrix v2.0,
#               PLD Runtime Standard v2.0,
#               PLD Taxonomy v2.0
# notes: Proposal-level runtime extension; detection logic intentionally left
#        implementation-specific.
# =============================================================================

"""
Only Core Technical Issues from the review have been integrated.
All “Open Questions” are now TODOs and MUST NOT be resolved here.
"""

from __future__ import annotations

import dataclasses
import datetime as _dt
import typing as _t
import uuid


# ──────────────────────────────────────────────────────────────────────────────
# Public Types
# ──────────────────────────────────────────────────────────────────────────────


@dataclasses.dataclass
class RepairSignal:
    """Implementation-specific repair signal used to construct PLD events."""

    code: str
    confidence: float = 1.0
    metadata: dict[str, _t.Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class RepairDetectorContext:
    """
    Minimal context required to emit PLD-compliant repair events.

    NOTE: Updated default source per Core Technical Issue #1.
    """

    session_id: str

    # Core Issue Fix: Default changed from "runtime" → "detector"
    # Justification: Aligns with DriftDetector behavior and prevents implicit
    # Level 1/2 semantic conflict regarding source meaning.
    source: str = "detector"

    validation_mode: str = "strict"

    # Optional runtime hints (non-canonical; safe to extend)
    model: str | None = None
    tool_name: str | None = None
    agent_state: str | None = None

    # TODO: Confirm whether these fields should be dynamic per turn rather than session-scoped.
    # Current assumption: session-scoped until Level 3 runtime standard clarifies intent.


# ──────────────────────────────────────────────────────────────────────────────
# Core Template Class
# ──────────────────────────────────────────────────────────────────────────────


class RepairDetector:
    """
    Template repair detector.

    This class operates purely at Level 5 and MUST NOT alter or weaken Level 1–3 rules.
    """

    def __init__(self, ctx: RepairDetectorContext) -> None:
        self._ctx = ctx

    def detect_and_build_event(
        self,
        *,
        turn_sequence: int,
        user_visible_state_change: bool = False,
        payload: dict[str, _t.Any] | None = None,
    ) -> dict[str, _t.Any] | None:

        repair_signal = self._run_detection(turn_sequence=turn_sequence)

        if repair_signal is None:
            return None

        return self._build_repair_event(
            turn_sequence=turn_sequence,
            repair_signal=repair_signal,
            user_visible_state_change=user_visible_state_change,
            payload=payload or {},
        )

    def _run_detection(self, *, turn_sequence: int) -> RepairSignal | None:
        raise NotImplementedError("Override _run_detection with concrete logic.")

    def _build_repair_event(
        self,
        *,
        turn_sequence: int,
        repair_signal: RepairSignal,
        user_visible_state_change: bool,
        payload: dict[str, _t.Any],
    ) -> dict[str, _t.Any]:

        code = repair_signal.code
        self._assert_repair_code_prefix(code)

        event: dict[str, _t.Any] = {
            "schema_version": "2.0",
            "event_id": str(uuid.uuid4()),
            "timestamp": _utc_now_iso(),
            "session_id": self._ctx.session_id,
            "turn_sequence": turn_sequence,
            "source": self._ctx.source,
            "event_type": "repair_triggered",
            "pld": {"phase": "repair", "code": code},
            "payload": payload,
            "ux": {"user_visible_state_change": bool(user_visible_state_change)},
            "runtime": {},
            "metrics": {},
            "extensions": {},
        }

        if repair_signal.confidence is not None:
            event["pld"]["confidence"] = float(repair_signal.confidence)

        if repair_signal.metadata:
            event["pld"]["metadata"] = dict(repair_signal.metadata)

        self._populate_runtime_overlay(event)
        return event

    @staticmethod
    def _assert_repair_code_prefix(code: str) -> None:
        prefix = _extract_prefix(code)
        if prefix != "R":
            raise ValueError(
                f"RepairDetector can only emit R* codes; got code={code!r} with prefix={prefix!r}"
            )

        # TODO: Confirm whether prefix extraction must be delegated
        # to a Level 2/3-governed canonical taxonomy utility.

    def _populate_runtime_overlay(self, event: dict[str, _t.Any]) -> None:
        runtime_meta: dict[str, _t.Any] = event.get("runtime") or {}

        runtime_meta.setdefault("validation_mode", self._ctx.validation_mode)

        if self._ctx.model is not None:
            runtime_meta.setdefault("model", self._ctx.model)
        if self._ctx.tool_name is not None:
            runtime_meta.setdefault("tool", self._ctx.tool_name)
        if self._ctx.agent_state is not None:
            runtime_meta.setdefault("agent_state", self._ctx.agent_state)

        event["runtime"] = runtime_meta

        # TODO: Clarify if repair-triggered events are:
        # - co-emitted alongside conversational events
        # - sequential signaling events representing intent
        # - replacements for invalid conversational content

        # TODO: Confirm whether runtime overlay should require dynamic turn metadata
        # rather than storing session metadata from context.


# ──────────────────────────────────────────────────────────────────────────────
# Utility Functions
# ──────────────────────────────────────────────────────────────────────────────


def _utc_now_iso() -> str:
    return _dt.datetime.utcnow().replace(microsecond=0, tzinfo=_dt.timezone.utc).isoformat().replace(
        "+00:00", "Z"
    )


def _extract_prefix(code: str) -> str:
    """
    Local helper implementing a non-normative taxonomy prefix rule.

    TODO: Replace with authoritative shared validator once defined.
    """
    head = code.split("_", 1)[0]
    i = len(head)
    while i > 0 and head[i - 1].isdigit():
        i -= 1
    return head[:i] or head


