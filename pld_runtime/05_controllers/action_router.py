# version: 2.0.0
# status: runtime
# authority_level_scope: Level 5 — runtime implementation
# purpose: Route PLD runtime events between controllers based on lifecycle phase and event_type.
# scope: Applies Level 1–3 PLD rules to derive next action, without modifying canonical specs.
# change_classification: runtime-only + selective integration of technical review
# dependencies: Level1_pld_event.schema.json, Level2_event_matrix_schema.yaml, Level3_PLD_Runtime_Standard_v2.0.md, Level5_runtime_event_envelope.schema.json
# runtime_label: runtime_extension (experimental)

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Callable


class ValidationMode(str, Enum):
    """Runtime mirror of Level 2 / Level 3 validation modes.

    - strict: MUST-level violations → reject, SHOULD-level → ignore
    - warn:   MUST-level violations → reject, SHOULD-level → warn
    - normalize: MUST-level violations → normalize when deterministically resolvable
    """

    STRICT = "strict"
    WARN = "warn"
    NORMALIZE = "normalize"


# NOTE: Modified per Core Technical Issue #2
# These maps were previously global constants. They are now class attributes
# to allow override/testing and future dynamic spec loading.
class ActionRouterConfig:
    # TODO (Open Question #2): Determine whether spec-driven dynamic rule loading replaces constant definitions.
    MUST_PHASE_MAP: Dict[str, str] = {
        "drift_detected": "drift",
        "drift_escalated": "drift",
        "repair_triggered": "repair",
        "repair_escalated": "repair",
        "reentry_observed": "reentry",
        "continue_allowed": "continue",
        "continue_blocked": "continue",
        "failover_triggered": "failover",
    }

    SHOULD_PHASE_MAP: Dict[str, str] = {
        "evaluation_pass": "outcome",
        "evaluation_fail": "outcome",
        "session_closed": "outcome",
        "info": "none",
    }

    VALID_PHASES = {
        "drift",
        "repair",
        "reentry",
        "continue",
        "outcome",
        "failover",
        "none",
    }


@dataclass(frozen=True)
class RouteDecision:
    next_action: str
    reason: str
    is_pld_valid: bool
    validation_details: Dict[str, Any]


class ActionRouter:
    """Level 5 runtime controller for event → action routing.

    Responsibilities:
    - Apply Level 1/2/3 constraints when interpreting incoming events.
    - Provide a next_action hint to the orchestrator.
    - NEVER mutate persisted logs (VAL-005).
    """

    # ---------------------------
    # Modified per Core Issue #1:
    # Introduced a routing table to avoid hardcoded if/elif dispatch.
    # ---------------------------
    _ROUTE_TABLE: Dict[str, Callable] = {}

    def __init__(
        self,
        *,
        validation_mode: ValidationMode = ValidationMode.STRICT,
        config: ActionRouterConfig = ActionRouterConfig(),
    ) -> None:
        self._validation_mode = validation_mode
        self._config = config

        # Initialize routing table only once per instance.
        # The handlers map event_types → method references.
        # NOTE: This preserves architecture intent while improving evolvability.
        self._ROUTE_TABLE = {
            # Lifecycle MUST events
            "drift_detected": self._route_drift,
            "drift_escalated": self._route_drift,
            "repair_triggered": self._route_repair,
            "repair_escalated": self._route_repair,
            "reentry_observed": self._route_reentry,
            "continue_allowed": self._route_continue,
            "continue_blocked": self._route_continue,
            "failover_triggered": self._route_failover,

            # SHOULD events
            "evaluation_pass": self._route_outcome_eval,
            "evaluation_fail": self._route_outcome_eval,
            "session_closed": self._route_session_closed,
            "info": self._route_info,

            # MAY-level events
            "latency_spike": self._route_observability,
            "pause_detected": self._route_observability,
            "handoff": self._route_observability,
            "fallback_executed": self._route_observability,
        }

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def route(self, event: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> RouteDecision:
        context = context or {}

        validation = self._validate_event_semantics(event)
        is_pld_valid = validation["is_pld_valid"]

        if not is_pld_valid and validation["must_violation"]:
            return RouteDecision(
                next_action="reject_event",
                reason=f"Rejected due to MUST-level semantic violation: {validation['must_violation']}",
                is_pld_valid=False,
                validation_details=validation,
            )

        event_type = event.get("event_type")

        handler = self._ROUTE_TABLE.get(event_type)
        if handler:
            return handler(event, context, validation)

        return RouteDecision(
            next_action="noop",
            reason=f"Unsupported event_type '{event_type}', no routing applied.",
            is_pld_valid=is_pld_valid,
            validation_details=validation,
        )

    # -------------------------------------------------------------------------
    # Validation
    # -------------------------------------------------------------------------

    def _validate_event_semantics(self, event: Dict[str, Any]) -> Dict[str, Any]:
        schema_version = event.get("schema_version")
        event_type = event.get("event_type")
        phase = self._extract_phase(event)

        must_violation: Optional[str] = None
        should_violation: Optional[str] = None

        if schema_version != "2.0":
            must_violation = f"schema_version != '2.0' (got {schema_version!r})"

        if phase not in self._config.VALID_PHASES and must_violation is None:
            must_violation = f"invalid phase {phase!r}"

        if event_type in self._config.MUST_PHASE_MAP and must_violation is None:
            expected = self._config.MUST_PHASE_MAP[event_type]
            if phase != expected:
                must_violation = (
                    f"event_type={event_type!r} MUST have phase={expected!r}, got phase={phase!r}"
                )

        if event_type in self._config.SHOULD_PHASE_MAP:
            expected = self._config.SHOULD_PHASE_MAP[event_type]
            if phase != expected:
                should_violation = (
                    f"event_type={event_type!r} SHOULD have phase={expected!r}, got phase={phase!r}"
                )

        is_pld_valid = must_violation is None

        suggested_normalized_phase: Optional[str] = None
        if (
            self._validation_mode is ValidationMode.NORMALIZE
            and not is_pld_valid
            and event_type in self._config.MUST_PHASE_MAP
        ):
            suggested_normalized_phase = self._config.MUST_PHASE_MAP[event_type]

        return {
            "is_pld_valid": is_pld_valid,
            "must_violation": must_violation,
            "should_violation": should_violation,
            "suggested_normalized_phase": suggested_normalized_phase,
            "validation_mode": self._validation_mode.value,
        }

    # -------------------------------------------------------------------------
    # Extraction
    # -------------------------------------------------------------------------

    @staticmethod
    def _extract_phase(event: Dict[str, Any]) -> Optional[str]:
        # TODO (Open Question #1): Confirm Level 1 guarantees the `pld` key structure.
        pld = event.get("pld") or {}
        return pld.get("phase") if isinstance(pld.get("phase"), str) else None

    @staticmethod
    def _extract_code(event: Dict[str, Any]) -> Optional[str]:
        pld = event.get("pld") or {}
        return pld.get("code") if isinstance(pld.get("code"), str) else None

    # -------------------------------------------------------------------------
    # Routing Handlers
    # -------------------------------------------------------------------------

    def _route_drift(self, event, context, validation):
        return RouteDecision(
            next_action="route_to_drift_handler",
            reason=f"Drift event {event['event_type']} → drift controller.",
            is_pld_valid=validation["is_pld_valid"],
            validation_details=validation,
        )

    def _route_repair(self, event, context, validation):
        return RouteDecision(
            next_action="route_to_repair_handler",
            reason="Repair event → repair controller.",
            is_pld_valid=validation["is_pld_valid"],
            validation_details=validation,
        )

    def _route_reentry(self, event, context, validation):
        return RouteDecision(
            next_action="route_to_reentry_handler",
            reason="Reentry observed.",
            is_pld_valid=validation["is_pld_valid"],
            validation_details=validation,
        )

    def _route_continue(self, event, context, validation):
        return RouteDecision(
            next_action="route_to_continue_handler",
            reason="Continuation event processed.",
            is_pld_valid=validation["is_pld_valid"],
            validation_details=validation,
        )

    def _route_failover(self, event, context, validation):
        return RouteDecision(
            next_action="route_to_failover_handler",
            reason="Failover triggered.",
            is_pld_valid=validation["is_pld_valid"],
            validation_details=validation,
        )

    def _route_outcome_eval(self, event, context, validation):
        return RouteDecision(
            next_action="route_to_evaluation_handler",
            reason="Outcome evaluation received.",
            is_pld_valid=validation["is_pld_valid"],
            validation_details=validation,
        )

    def _route_session_closed(self, event, context, validation):
        phase = self._extract_phase(event)
        if phase == "outcome":
            action = "close_session"
        elif phase == "none":
            action = "close_session_non_semantic"
        else:
            action = "close_session_with_warning"

        return RouteDecision(
            next_action=action,
            reason=f"Session closure event ({phase}).",
            is_pld_valid=validation["is_pld_valid"],
            validation_details=validation,
        )

    def _route_info(self, event, context, validation):
        return RouteDecision(
            next_action="route_to_observability_sink",
            reason="Info event routed to observability.",
            is_pld_valid=validation["is_pld_valid"],
            validation_details=validation,
        )

    def _route_observability(self, event, context, validation):
        return RouteDecision(
            next_action="route_to_observability_sink",
            reason=f"Observability event {event['event_type']}.",
            is_pld_valid=validation["is_pld_valid"],
            validation_details={**validation, "context_snapshot": context},
        )

    # -------------------------------------------------------------------------
    # TODO Items from Open Questions
    # -------------------------------------------------------------------------
    # TODO (#1): Confirm whether Level 1 guarantees the event['pld'] structure.
    # TODO (#2): Confirm orchestrator responsibility for normalization behavior.
    # TODO (#3): Clarify whether future routing requires richer session context integration.
