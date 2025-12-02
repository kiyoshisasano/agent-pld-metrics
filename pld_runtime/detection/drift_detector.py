# component_id: drift_detector
# kind: runtime_module
# area: detection
# status: experimental
# authority_level: 5
# version: 2.0.0
# license: Apache-2.0
# purpose: Template for drift detection that emits PLD v2-compliant drift events.

from __future__ import annotations

import dataclasses
import datetime as _dt
import typing as _t
import uuid


# ──────────────────────────────────────────────────────────────────────────────
# Public Types
# ──────────────────────────────────────────────────────────────────────────────


@dataclasses.dataclass
class DriftSignal:
    """
    Implementation-specific drift signal.

    This represents the *result* of whatever detection logic you run
    (model comparison, policy checks, tool failures, etc.).

    Fields here are runtime-only and are NOT part of the PLD schema; they
    are used to construct PLD events that DO conform to Level 1 & 2.
    """

    code: str
    confidence: float = 1.0
    metadata: dict[str, _t.Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class DriftDetectorContext:
    """
    Minimal context required to emit PLD-compliant drift events.

    You may extend this dataclass locally, but MUST NOT remove or change
    the semantics of the existing fields.
    """

    session_id: str

    source: str = "detector"

    validation_mode: str = "strict"

    # Optional runtime hints (non-canonical; safe to extend)
    model: str | None = None
    tool_name: str | None = None
    agent_state: str | None = None


# ──────────────────────────────────────────────────────────────────────────────
# Core Template Class
# ──────────────────────────────────────────────────────────────────────────────


class DriftDetector:
    """
    Template drift detector.

    Responsibilities (non-exhaustive):

    - Run implementation-specific logic to determine whether drift exists
      for the current turn.
    - Map detection results to taxonomy-aligned codes in the D* family.
    - Emit events that satisfy:

        schema_valid(event) ∧ matrix_valid(event)

    This class operates purely at Level 5 and MUST NOT alter or weaken
    Level 1–3 rules.
    """

    def __init__(self, ctx: DriftDetectorContext) -> None:
        self._ctx = ctx

    def detect_and_build_event(
        self,
        *,
        turn_sequence: int,
        user_visible_state_change: bool = False,
        payload: dict[str, _t.Any] | None = None,
    ) -> dict[str, _t.Any] | None:

        drift_signal = self._run_detection(turn_sequence=turn_sequence)

        if drift_signal is None:
            return None

        return self._build_drift_event(
            turn_sequence=turn_sequence,
            drift_signal=drift_signal,
            user_visible_state_change=user_visible_state_change,
            payload=payload or {},
        )

    def _run_detection(self, *, turn_sequence: int) -> DriftSignal | None:
        raise NotImplementedError("Override _run_detection with concrete logic.")

    def _build_drift_event(
        self,
        *,
        turn_sequence: int,
        drift_signal: DriftSignal,
        user_visible_state_change: bool,
        payload: dict[str, _t.Any],
    ) -> dict[str, _t.Any]:

        code = drift_signal.code
        self._assert_drift_code_prefix(code)

        # Removed redundant int(...) cast based on review requirement.
        event: dict[str, _t.Any] = {
            "schema_version": "2.0",
            "event_id": str(uuid.uuid4()),
            "timestamp": _utc_now_iso(),
            "session_id": self._ctx.session_id,
            "turn_sequence": turn_sequence,
            "source": self._ctx.source,
            "event_type": "drift_detected",
            "pld": {
                "phase": "drift",
                "code": code,
            },
            "payload": payload,
            "ux": {
                "user_visible_state_change": bool(user_visible_state_change),
            },
            "runtime": {},
            "metrics": {},
            "extensions": {},
        }

        if drift_signal.confidence is not None:
            event["pld"]["confidence"] = float(drift_signal.confidence)

        if drift_signal.metadata:
            event["pld"]["metadata"] = dict(drift_signal.metadata)

        self._populate_runtime_overlay(event)

        return event

    @staticmethod
    def _assert_drift_code_prefix(code: str) -> None:
        prefix = _extract_prefix(code)
        if prefix != "D":
            raise ValueError(
                f"DriftDetector can only emit D* codes; got code={code!r} with prefix={prefix!r}"
            )

        # TODO: Confirm whether prefix extraction logic must be delegated
        # to a Level-2 compliant shared validator rather than implemented here.

    def _populate_runtime_overlay(self, event: dict[str, _t.Any]) -> None:
        runtime_meta: dict[str, _t.Any] = event.get("runtime") or {}

        # Added to resolve Core Issue: validation_mode must propagate.
        runtime_meta.setdefault("validation_mode", self._ctx.validation_mode)

        if self._ctx.model is not None:
            runtime_meta.setdefault("model", self._ctx.model)
        if self._ctx.tool_name is not None:
            runtime_meta.setdefault("tool", self._ctx.tool_name)
        if self._ctx.agent_state is not None:
            runtime_meta.setdefault("agent_state", self._ctx.agent_state)

        event["runtime"] = runtime_meta

        # TODO: Confirm whether turn-level runtime metadata belongs here
        # or should be provided dynamically per detect_and_build_event call.


# ──────────────────────────────────────────────────────────────────────────────
# Utility Functions
# ──────────────────────────────────────────────────────────────────────────────


def _utc_now_iso() -> str:
    return _dt.datetime.utcnow().replace(microsecond=0, tzinfo=_dt.timezone.utc).isoformat().replace(
        "+00:00", "Z"
    )


def _extract_prefix(code: str) -> str:
    head = code.split("_", 1)[0]
    i = len(head)
    while i > 0 and head[i - 1].isdigit():
        i -= 1
    return head[:i] or head


# TODO: Clarify whether drift events must be co-emitted alongside primary
# conversational events or replace them in cases of detected divergence.


