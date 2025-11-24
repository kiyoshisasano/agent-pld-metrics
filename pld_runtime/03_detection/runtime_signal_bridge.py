# =============================================================================
# PLD Runtime Signal Bridge
#
# version: 0.1.1
# status: draft
# authority_level_scope: Level 5 — runtime implementation
# purpose: Bridge internal runtime signals into PLD v2-compliant events for
#          emission, enforcing Level 1–3 constraints at the mapping boundary.
# change_classification: runtime-only
# dependencies: PLD runtime event schema v2.0, PLD event matrix v2.0,
#               PLD runtime event envelope v2.0
# =============================================================================

from __future__ import annotations

import enum
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, MutableMapping, Optional, Sequence


# ---------------------------------------------------------------------------
# Validation Modes (aligned with Level 2/3 semantics: strict / warn / normalize)
# ---------------------------------------------------------------------------


class ValidationMode(str, enum.Enum):
    STRICT = "strict"
    WARN = "warn"
    NORMALIZE = "normalize"


# ---------------------------------------------------------------------------
# Canonical constants (mirroring Level 1–3, WITHOUT redefining them)
# ---------------------------------------------------------------------------

PLD_SCHEMA_VERSION = "2.0"

# Event types: MUST remain compatible with Level 1 schema.
EVENT_TYPES_MUST_PHASE = {
    "drift_detected": "drift",
    "drift_escalated": "drift",
    "repair_triggered": "repair",
    "repair_escalated": "repair",
    "reentry_observed": "reentry",
    "continue_allowed": "continue",
    "continue_blocked": "continue",
    "failover_triggered": "failover",
}

EVENT_TYPES_SHOULD_PHASE = {
    "evaluation_pass": "outcome",
    "evaluation_fail": "outcome",
    "session_closed": "outcome",  # MAY be "none" with justification
    "info": "none",
}

EVENT_TYPES_MAY_PHASE = {
    "latency_spike",
    "pause_detected",
    "fallback_executed",
    "handoff",
}

VALID_PHASES: Sequence[str] = (
    "drift",
    "repair",
    "reentry",
    "continue",
    "outcome",
    "failover",
    "none",
)


# Prefix → phase mapping for lifecycle prefixes (Level 2 Phase ↔ Prefix rules).
PREFIX_TO_PHASE = {
    "D": "drift",
    "R": "repair",
    "RE": "reentry",
    "C": "continue",
    "O": "outcome",
    "F": "failover",
}


# ---------------------------------------------------------------------------
# Runtime signal model (Level 5 only)
# ---------------------------------------------------------------------------


class SignalKind(str, enum.Enum):
    """
    Internal signal identifiers used by the runtime.

    These are runtime-local and MAY be extended.
    The mapping to PLD semantics is defined in RUNTIME_SIGNAL_MAP below.
    """

    # Drift detection signals
    INSTRUCTION_DRIFT = "instruction_drift"
    CONTEXT_DRIFT = "context_drift"
    REPEATED_PLAN = "repeated_plan"
    TOOL_ERROR = "tool_error"

    # Repair / mitigation
    CLARIFICATION = "clarification"
    SOFT_REPAIR = "soft_repair"
    REWRITE = "rewrite"
    REQUEST_USER_CLARIFICATION = "request_user_clarification"
    HARD_RESET = "hard_reset"

    # Continue / nominal flow
    CONTINUE_NORMAL = "continue_normal"
    CONTINUE_USER_TURN = "continue_user_turn"
    CONTINUE_SYSTEM_TURN = "continue_system_turn"

    # Outcome / lifecycle closure
    SESSION_CLOSED = "session_closed"

    # Observability / metrics-adjacent
    LATENCY_SPIKE = "latency_spike"
    PAUSE_DETECTED = "pause_detected"

    # Derived metrics / analytics (M-prefix, Phase=none, event_type=info)
    METRIC_PRDR = "metric_prdr"
    METRIC_VRL = "metric_vrl"

    # Generic info / diagnostic
    INFO = "info"


@dataclass(frozen=True)
class RuntimeSignal:
    """
    Level 5 structure describing an internal signal to be bridged into PLD.

    Fields:
        kind:      Internal runtime signal kind (SignalKind).
        payload:   Arbitrary data associated with the signal (tool outputs, scores, etc.).
        confidence: Optional classifier confidence in [0, 1].
        metadata:  Optional additional metadata that should be propagated into pld.metadata.
    """

    kind: SignalKind
    payload: Mapping[str, Any] = field(default_factory=dict)
    confidence: Optional[float] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass
class EventContext:
    """
    Level 5 context for event emission.

    This context does NOT redefine schema; it provides values required
    to construct structurally valid events.

    Fields:
        session_id:    PLD session identifier (UUID RECOMMENDED).
        turn_sequence: Monotonic 1-based turn index.
        source:        Logical origin of the event (user, assistant, runtime, etc.).
        model:         Optional model identifier.
        tool:          Optional tool identifier when applicable.
        agent_state:   Optional opaque agent state key.
        current_phase: Optional current lifecycle phase to use as default when
                       the event_type allows any phase (MAY-level events).
    """

    # TODO(RUNTIME-CONTEXT-COVERAGE): Clarify in Level 3 Runtime Standard whether
    # model/tool/agent_state are expected to be present for all events or only a
    # subset, and what guarantees exist about their freshness at signal emission.
    session_id: str
    turn_sequence: int
    source: str
    model: Optional[str] = None
    tool: Optional[str] = None
    agent_state: Optional[str] = None
    current_phase: Optional[str] = None


# ---------------------------------------------------------------------------
# Runtime signal → PLD semantics mapping (Level 5 only)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PldSemanticMapping:
    """
    Derived mapping from a runtime signal into PLD semantics.

    Fields:
        event_type:  PLD event_type (must be within Level 1 enumeration).
        phase:       PLD lifecycle phase.
        code:        PLD taxonomy code string.
        default_confidence: Optional default confidence if signal lacks one.
    """

    event_type: str
    phase: str
    code: str
    default_confidence: Optional[float] = None


# NOTE:
# - Lifecycle mappings below are aligned with Level 2 / Level 3 rules.
# - Mappings for derived metrics (M-prefix) use event_type = "info" and phase = "none".
RUNTIME_SIGNAL_MAP: Dict[SignalKind, PldSemanticMapping] = {
    # Drift family (D prefix, phase=drift)
    SignalKind.INSTRUCTION_DRIFT: PldSemanticMapping(
        event_type="drift_detected",
        phase="drift",
        code="D1_instruction",
        default_confidence=0.9,
    ),
    SignalKind.CONTEXT_DRIFT: PldSemanticMapping(
        event_type="drift_detected",
        phase="drift",
        code="D2_context",
        default_confidence=0.9,
    ),
    SignalKind.REPEATED_PLAN: PldSemanticMapping(
        event_type="drift_detected",
        phase="drift",
        code="D3_repeated_plan",
        default_confidence=0.9,
    ),
    SignalKind.TOOL_ERROR: PldSemanticMapping(
        event_type="drift_detected",
        phase="drift",
        code="D4_tool_error",
        default_confidence=0.9,
    ),
    # Repair family (R prefix, phase=repair)
    SignalKind.CLARIFICATION: PldSemanticMapping(
        event_type="repair_triggered",
        phase="repair",
        code="R1_clarify",
        default_confidence=0.9,
    ),
    SignalKind.SOFT_REPAIR: PldSemanticMapping(
        event_type="repair_triggered",
        phase="repair",
        code="R2_soft_repair",
        default_confidence=0.9,
    ),
    SignalKind.REWRITE: PldSemanticMapping(
        event_type="repair_triggered",
        phase="repair",
        code="R3_rewrite",
        default_confidence=0.9,
    ),
    SignalKind.REQUEST_USER_CLARIFICATION: PldSemanticMapping(
        event_type="repair_triggered",
        phase="repair",
        code="R4_request_clarification",
        default_confidence=0.9,
    ),
    SignalKind.HARD_RESET: PldSemanticMapping(
        event_type="repair_triggered",
        phase="repair",
        code="R5_hard_reset",
        default_confidence=0.9,
    ),
    # Continue family (C prefix, phase=continue)
    SignalKind.CONTINUE_NORMAL: PldSemanticMapping(
        event_type="continue_allowed",
        phase="continue",
        code="C0_normal",
        default_confidence=None,
    ),
    SignalKind.CONTINUE_USER_TURN: PldSemanticMapping(
        event_type="continue_allowed",
        phase="continue",
        code="C0_user_turn",
        default_confidence=None,
    ),
    SignalKind.CONTINUE_SYSTEM_TURN: PldSemanticMapping(
        event_type="continue_allowed",
        phase="continue",
        code="C0_system_turn",
        default_confidence=None,
    ),
    # Outcome closure (O prefix, phase=outcome)
    SignalKind.SESSION_CLOSED: PldSemanticMapping(
        event_type="session_closed",
        phase="outcome",
        code="O0_session_closed",
        default_confidence=None,
    ),
    # Observability / MAY-level (prefix & phase derived from context or set to none)
    SignalKind.LATENCY_SPIKE: PldSemanticMapping(
        event_type="latency_spike",
        phase="none",  # MAY be normalized from context.current_phase if desired.
        code="INFO_latency_spike",
        default_confidence=None,
    ),
    SignalKind.PAUSE_DETECTED: PldSemanticMapping(
        event_type="pause_detected",
        phase="none",
        code="INFO_pause_detected",
        default_confidence=None,
    ),
    # Derived metrics / analytics (M-prefix, event_type=info, phase=none)
    SignalKind.METRIC_PRDR: PldSemanticMapping(
        event_type="info",
        phase="none",
        code="M1_PRDR",
        default_confidence=None,
    ),
    SignalKind.METRIC_VRL: PldSemanticMapping(
        event_type="info",
        phase="none",
        code="M2_VRL",
        default_confidence=None,
    ),
    # Generic info
    SignalKind.INFO: PldSemanticMapping(
        event_type="info",
        phase="none",
        code="INFO_generic",
        default_confidence=None,
    ),
}


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _extract_lifecycle_prefix(code: str) -> str:
    """
    Extract the lifecycle prefix from pld.code according to Level 2 rules:

    - prefix is characters before first "_" minus trailing digits.
    - Example: "D4_tool_error" -> "D"
    """
    # TODO(TAXONOMY-PREFIX-SHARED-UTIL): Confirm whether a Level 2/3-governed
    # shared utility exists for taxonomy prefix extraction/validation and, if so,
    # depend on it instead of maintaining this local implementation.
    head = code.split("_", 1)[0]
    # Strip trailing digits
    i = len(head)
    while i > 0 and head[i - 1].isdigit():
        i -= 1
    return head[:i]


def _ensure_phase_prefix_consistency(code: str, phase: str) -> None:
    """
    Assert phase ↔ code prefix consistency for lifecycle prefixes.
    Non-lifecycle prefixes are only allowed with phase="none".
    """
    prefix = _extract_lifecycle_prefix(code)
    if prefix in PREFIX_TO_PHASE:
        expected_phase = PREFIX_TO_PHASE[prefix]
        if expected_phase != phase:
            raise ValueError(
                f"prefix/phase mismatch: code={code!r} implies phase={expected_phase!r} "
                f"but phase={phase!r} was provided"
            )
    else:
        # Non-lifecycle prefix: phase MUST be none.
        if phase != "none":
            raise ValueError(
                f"non-lifecycle prefix {prefix!r} requires phase='none', got phase={phase!r}"
            )


def _event_type_phase_policy(event_type: str) -> Optional[str]:
    """
    Return the required (MUST) or recommended (SHOULD) phase for event_type,
    or None when any phase is allowed (MAY-level).

    NOTE: This helper is advisory only. MUST vs SHOULD enforcement is handled
    explicitly in _resolve_phase.
    """
    if event_type in EVENT_TYPES_MUST_PHASE:
        return EVENT_TYPES_MUST_PHASE[event_type]
    if event_type in EVENT_TYPES_SHOULD_PHASE:
        return EVENT_TYPES_SHOULD_PHASE[event_type]
    return None


# ---------------------------------------------------------------------------
# RuntimeSignalBridge implementation (Level 5)
# ---------------------------------------------------------------------------


class RuntimeSignalBridge:
    """
    RuntimeSignalBridge
    -------------------

    Level 5 component responsible for translating internal runtime signals
    into PLD v2-compliant event dictionaries that conform to:

      - Level 1: structural schema (PLD runtime event schema)
      - Level 2: semantic matrix and prefix/phase rules
      - Level 3: runtime standard and metrics alignment rules

    This class does NOT modify or reinterpret Level 1–3 specifications.
    It only applies them to ensure that emitted events are valid.

    The public interface is intentionally narrow:

        build_event(signal: RuntimeSignal, context: EventContext) -> dict

    Runtimes MAY wrap this bridge with transport-specific logic (e.g. Kafka,
    HTTP ingestion) without changing this module.
    """

    def __init__(
        self,
        *,
        validation_mode: ValidationMode = ValidationMode.STRICT,
    ) -> None:
        self._validation_mode = validation_mode

    # ------------------------------------------------------------------ #
    # Public API                                                         #
    # ------------------------------------------------------------------ #

    def build_event(
        self,
        signal: RuntimeSignal,
        context: EventContext,
        *,
        user_visible_state_change: bool = False,
        timestamp_override: Optional[str] = None,
        extra_runtime_fields: Optional[Mapping[str, Any]] = None,
        extra_extensions: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Build a PLD runtime event (as a dict) from a RuntimeSignal and EventContext.

        The result is intended to conform to the Level 5 runtime envelope schema
        layered on top of the Level 1 PLD event schema.

        Arguments:
            signal:
                Internal runtime signal to be mapped.
            context:
                EventContext providing session, turn, and source information.
            user_visible_state_change:
                Whether this event results in user-visible output.
            timestamp_override:
                Optional RFC3339/ISO-8601 timestamp string (UTC). If not provided,
                the current UTC time is used.
            extra_runtime_fields:
                Additional runtime.* fields for observability (e.g. latency_ms).
            extra_extensions:
                Additional extensions.* fields for experiment tracking.

        Raises:
            KeyError, ValueError if mapping violates Level 1–3 constraints in
            STRICT mode. In WARN or NORMALIZE modes, behavior MAY be more lenient
            but MUST NOT produce events that conflict with hard invariants.
        """
        mapping = self._resolve_mapping(signal)

        # event_type/phase constraints from Level 2 & runtime standard
        phase = self._resolve_phase(mapping, context)

        # prefix/phase consistency rule
        _ensure_phase_prefix_consistency(mapping.code, phase)

        # Construct PLD event dict.
        event: Dict[str, Any] = {
            "schema_version": PLD_SCHEMA_VERSION,
            "event_id": str(uuid.uuid4()),
            "timestamp": timestamp_override or _now_utc_iso(),
            "session_id": context.session_id,
            "turn_sequence": context.turn_sequence,
            # turn_id is optional; leave empty by default (runtime may override).
            "source": context.source,
            "event_type": mapping.event_type,
            "pld": self._build_pld_block(signal, mapping, phase),
            "payload": dict(signal.payload),  # Level 1 leaves payload unconstrained.
            "runtime": self._build_runtime_block(context, extra_runtime_fields),
            "ux": {
                "user_visible_state_change": bool(user_visible_state_change),
            },
            "metrics": {},  # Reserved for runtime metrics snapshots (Level 3).
            "extensions": dict(extra_extensions or {}),
        }

        return event

    # ------------------------------------------------------------------ #
    # Internal helpers                                                   #
    # ------------------------------------------------------------------ #

    def _resolve_mapping(self, signal: RuntimeSignal) -> PldSemanticMapping:
        try:
            return RUNTIME_SIGNAL_MAP[signal.kind]
        except KeyError as exc:
            raise KeyError(
                f"No PLD semantic mapping configured for runtime signal kind={signal.kind!r}"
            ) from exc

    def _resolve_phase(
        self,
        mapping: PldSemanticMapping,
        context: EventContext,
    ) -> str:
        """
        Determine the final phase for the event:

        - For MUST-level event_types, enforce required phase with rejection or
          normalization depending on validation_mode.
        - For SHOULD-level event_types, never reject solely on a phase mismatch;
          normalization MAY occur in NORMALIZE mode.
        - For MAY-level events (e.g., latency_spike), we MAY use context.current_phase,
          falling back to the mapping's phase if none is provided.
        """
        event_type = mapping.event_type

        # MAY-level events: phase is context-dependent.
        if event_type in EVENT_TYPES_MAY_PHASE:
            if context.current_phase in VALID_PHASES:
                return context.current_phase
            phase = mapping.phase
            if phase not in VALID_PHASES:
                raise ValueError(
                    f"invalid phase {phase!r} for MAY-level event_type={event_type!r}"
                )
            return phase

        required = EVENT_TYPES_MUST_PHASE.get(event_type)
        recommended = EVENT_TYPES_SHOULD_PHASE.get(event_type)
        phase = mapping.phase

        # MUST-level enforcement
        if required is not None:
            if phase == required:
                return phase

            if self._validation_mode in (ValidationMode.STRICT, ValidationMode.WARN):
                raise ValueError(
                    f"MUST violation: event_type={event_type!r} requires phase="
                    f"{required!r}, got phase={phase!r}"
                )

            if self._validation_mode is ValidationMode.NORMALIZE:
                # Normalize to the required phase.
                return required

            # Fallback: be conservative and return the required phase.
            return required

        # SHOULD-level guidance (never hard-reject based solely on this)
        if recommended is not None:
            if phase == recommended:
                return phase

            if self._validation_mode is ValidationMode.NORMALIZE:
                # In normalize mode we MAY normalize to the recommended phase.
                return recommended

            if self._validation_mode is ValidationMode.WARN:
                # TODO(SHOULD-VIOLATION-LOGGING): Decide whether RuntimeSignalBridge
                # should emit explicit warnings for SHOULD-level violations in WARN
                # mode, or delegate that responsibility to higher-level callers.
                pass

            return phase

        # Unknown event_type with respect to MUST/SHOULD maps: ensure phase is valid.
        if phase not in VALID_PHASES:
            raise ValueError(
                f"invalid phase {phase!r} for event_type={event_type!r}"
            )
        return phase

    def _build_pld_block(
        self,
        signal: RuntimeSignal,
        mapping: PldSemanticMapping,
        phase: str,
    ) -> Dict[str, Any]:
        confidence = (
            signal.confidence
            if signal.confidence is not None
            else mapping.default_confidence
        )

        pld: MutableMapping[str, Any] = {
            "phase": phase,
            "code": mapping.code,
        }
        if confidence is not None:
            pld["confidence"] = confidence

        # Metadata is advisory and may include taxonomy_status, justification, etc.
        if signal.metadata:
            pld["metadata"] = dict(signal.metadata)

        return dict(pld)

    def _build_runtime_block(
        self,
        context: EventContext,
        extra_runtime_fields: Optional[Mapping[str, Any]],
    ) -> Dict[str, Any]:
        # TODO(RUNTIME-BLOCK-COMPLETENESS): Confirm whether all fields in EventContext
        # are expected to be populated for every event, or only for conversational
        # turns, and how missing values should be interpreted by downstream systems.
        runtime_block: Dict[str, Any] = {}

        # Duplicate turn_sequence into runtime block for observability alignment.
        runtime_block["turn_sequence"] = context.turn_sequence

        if context.model is not None:
            runtime_block["model"] = context.model
        if context.tool is not None:
            runtime_block["tool"] = context.tool
        if context.agent_state is not None:
            runtime_block["agent_state"] = context.agent_state

        if extra_runtime_fields:
            # Additional fields (e.g., latency_ms) are allowed by Level 1/5.
            runtime_block.update(extra_runtime_fields)

        return runtime_block


# ---------------------------------------------------------------------------
# Minimal example usage (non-normative, for implementers only)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # This block is for local smoke-testing only and MUST NOT be treated as a
    # normative example. Runtimes SHOULD integrate the bridge via their own
    # wiring code and test infrastructure.
    bridge = RuntimeSignalBridge(validation_mode=ValidationMode.STRICT)

    ctx = EventContext(
        session_id="example-session-id",
        turn_sequence=1,
        source="detector",
        model="example-model",
        current_phase="drift",
    )

    sig = RuntimeSignal(
        kind=SignalKind.TOOL_ERROR,
        payload={"error": "timeout", "tool_name": "search"},
        confidence=0.92,
        metadata={"taxonomy_status": "stable"},
    )

    event = bridge.build_event(
        signal=sig,
        context=ctx,
        user_visible_state_change=False,
        extra_runtime_fields={"latency_ms": 123.4},
    )

    # For debugging purposes only; actual runtimes SHOULD send the event to
    # their logging/ingestion pipeline instead of printing it.
    import json

    print(json.dumps(event, indent=2, sort_keys=True))
