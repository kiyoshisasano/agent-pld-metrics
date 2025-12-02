# component_id: state_machine
# kind: runtime_module
# area: controller
# status: runtime
# authority_level: 5
# version: 2.0.0
# license: Apache-2.0
# purpose: Maintain PLD-aware session state machine enforcing lifecycle rules.

from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Dict, List, Optional


class Phase(str, Enum):
    DRIFT = "drift"
    REPAIR = "repair"
    REENTRY = "reentry"
    CONTINUE = "continue"
    OUTCOME = "outcome"
    FAILOVER = "failover"
    NONE = "none"


# NOTE: Hardcoded maps remain by governance rules.
# TODO (Open Question — canonical lifecycle map): Determine authority responsible
#       for publishing the final Phase→Phase ruleset and align when available.
_MUST_PHASE_MAP: Dict[str, Phase] = {
    "drift_detected": Phase.DRIFT,
    "drift_escalated": Phase.DRIFT,
    "repair_triggered": Phase.REPAIR,
    "repair_escalated": Phase.REPAIR,
    "reentry_observed": Phase.REENTRY,
    "continue_allowed": Phase.CONTINUE,
    "continue_blocked": Phase.CONTINUE,
    "failover_triggered": Phase.FAILOVER,
}

_SHOULD_PHASE_MAP: Dict[str, Phase] = {
    "evaluation_pass": Phase.OUTCOME,
    "evaluation_fail": Phase.OUTCOME,
    "session_closed": Phase.OUTCOME,
    "info": Phase.NONE,
}

_VALID_PHASES = {p.value for p in Phase}

_ALLOWED_TRANSITIONS: Dict[Phase, List[Phase]] = {
    Phase.NONE: [Phase.CONTINUE, Phase.DRIFT, Phase.REPAIR, Phase.FAILOVER, Phase.REENTRY, Phase.OUTCOME],
    Phase.CONTINUE: [Phase.CONTINUE, Phase.DRIFT, Phase.REPAIR, Phase.FAILOVER, Phase.OUTCOME],
    Phase.DRIFT: [Phase.REPAIR, Phase.FAILOVER, Phase.CONTINUE],
    Phase.REPAIR: [Phase.REENTRY, Phase.CONTINUE, Phase.FAILOVER],
    Phase.REENTRY: [Phase.CONTINUE, Phase.OUTCOME],
    Phase.FAILOVER: [Phase.REENTRY, Phase.CONTINUE, Phase.OUTCOME],
    Phase.OUTCOME: [],
}


@dataclass(frozen=True)
class StateSnapshot:
    current_phase: Phase
    session_open: bool
    last_event_type: Optional[str]
    last_pld_code: Optional[str]
    last_turn_sequence: Optional[int]
    failover_active: bool

    def to_dict(self) -> Dict[str, Any]:
        return {**asdict(self), "current_phase": self.current_phase.value}


@dataclass(frozen=True)
class StateTransition:
    previous_state: StateSnapshot
    next_state: StateSnapshot
    reason: str
    violations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "previous_state": self.previous_state.to_dict(),
            "next_state": self.next_state.to_dict(),
            "reason": self.reason,
            "violations": self.violations,
        }


class PLDStateMachine:
    def __init__(self) -> None:
        self._state = StateSnapshot(
            current_phase=Phase.NONE,
            session_open=False,
            last_event_type=None,
            last_pld_code=None,
            last_turn_sequence=None,
            failover_active=False,
        )

        # TODO (Open Question — dynamic config): confirm whether this class will support runtime spec ingestion.
        # TODO (Open Question — first-turn policy / RUN-006): clarify allowed set of first-turn events
        #       and whether non-whitelisted first events MUST be rejected vs. flagged-only.
        # TODO (Open Question — turn_sequence boundary): confirm that turn_sequence is
        #       top-level in Level5_runtime_event_envelope.schema.json and not duplicated
        #       under the Level 1 PLD object.

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    @property
    def state(self) -> StateSnapshot:
        return self._state

    def apply_event(self, event: Dict[str, Any]) -> StateTransition:
        prev = self._state
        violations: List[str] = []

        # Extract event fields once to avoid repeated lookups (Core Issue #2)
        pld_block = event.get("pld") or {}

        event_type = event.get("event_type")
        phase_str = pld_block.get("phase")
        code = pld_block.get("code")
        turn_sequence = event.get("turn_sequence")  # TODO (Open Question) confirm schema boundary & uniqueness

        # Phase validation
        if phase_str not in _VALID_PHASES:
            violations.append(f"invalid_phase_value: {phase_str!r}")
            phase: Optional[Phase] = None
        else:
            phase = Phase(phase_str)  # type: ignore[arg-type]

        # MUST-level event_type → phase rules
        expected_must = _MUST_PHASE_MAP.get(event_type)
        if expected_must is not None and phase != expected_must:
            violations.append(
                f"must_phase_mismatch: event_type={event_type!r} "
                f"expected={expected_must.value!r} got={phase_str!r}"
            )

        # SHOULD-level event_type → phase rules
        expected_should = _SHOULD_PHASE_MAP.get(event_type)
        if expected_should is not None and phase != expected_should:
            violations.append(
                f"should_phase_mismatch: event_type={event_type!r} "
                f"expected={expected_should.value!r} got={phase_str!r}"
            )

        next_state, reason = self._next_state_from_event(
            prev_state=prev,
            phase=phase,
            event_type=event_type,
            code=code,
            turn_sequence=turn_sequence,
            violations=violations,
        )

        self._state = next_state
        return StateTransition(previous_state=prev, next_state=next_state, reason=reason, violations=violations)

    # -------------------------------------------------------------------------
    # Core transition logic
    # -------------------------------------------------------------------------

    def _next_state_from_event(
        self,
        *,
        prev_state: StateSnapshot,
        phase: Optional[Phase],
        event_type: Optional[str],
        code: Optional[str],
        turn_sequence: Optional[int],
        violations: List[str],
    ) -> StateSnapshot:

        current_phase = prev_state.current_phase
        session_open = prev_state.session_open
        failover_active = prev_state.failover_active
        reason = "transition"

        invalid_transition = False
        if phase is not None:
            allowed_next = _ALLOWED_TRANSITIONS.get(current_phase, [])
            if phase not in allowed_next:
                invalid_transition = True
                violations.append(
                    f"invalid_transition: {current_phase.value} → {phase.value} not allowed"
                )

        # --- Terminal state check (session_closed has highest precedence) ---
        if event_type == "session_closed":
            session_open = False
            failover_active = False

            if phase is not None and not invalid_transition:
                current_phase = phase

            return StateSnapshot(
                current_phase=current_phase,
                session_open=session_open,
                last_event_type=event_type,
                last_pld_code=code,
                last_turn_sequence=turn_sequence,
                failover_active=failover_active,
            ), "session_terminated"

        # --- Session Initialization (RUN-006) ---
        if not session_open and turn_sequence == 1:
            if event_type == "continue_allowed":
                session_open = True
                current_phase = Phase.CONTINUE
                reason = "session_initialized"
            elif event_type == "info" and code == "SYS_session_init":
                session_open = True
                reason = "session_initialized_via_system"
            else:
                # Core Technical Issue: non-whitelisted first events must not be silently accepted.
                # Record a violation and DO NOT implicitly open the session.
                violations.append(
                    f"invalid_session_init_event: event_type={event_type!r}, code={code!r}"
                )
                reason = "invalid_session_start"

        # --- Failover Handling (RUN-008) ---
        if event_type == "failover_triggered" and phase == Phase.FAILOVER:
            failover_active = True
            current_phase = Phase.FAILOVER
            return StateSnapshot(
                current_phase=current_phase,
                session_open=session_open,
                last_event_type=event_type,
                last_pld_code=code,
                last_turn_sequence=turn_sequence,
                failover_active=failover_active,
            ), "failover_active"

        if failover_active:
            # Resolution events
            if event_type == "reentry_observed" and phase == Phase.REENTRY:
                failover_active = False
                current_phase = Phase.REENTRY
                reason = "failover_recovered_via_reentry"
            elif event_type == "continue_allowed" and phase == Phase.CONTINUE:
                failover_active = False
                current_phase = Phase.CONTINUE
                reason = "failover_recovered_via_continue"
            # Disallowed transition
            elif event_type in ("drift_detected", "drift_escalated") and phase == Phase.DRIFT:
                violations.append("failover_rule_violation: drift_after_failover")
                reason = "invalid_failover_state"
            else:
                # Non-resolving, non-violating events during failover:
                # allow transition only if the phase transition is valid.
                if phase is not None and not invalid_transition:
                    current_phase = phase
                    reason = "failover_nonterminal_transition"
                else:
                    reason = "failover_context"

            return StateSnapshot(
                current_phase=current_phase,
                session_open=session_open,
                last_event_type=event_type,
                last_pld_code=code,
                last_turn_sequence=turn_sequence,
                failover_active=failover_active,
            ), reason

        # ---- Normal Transition ----
        if phase is not None and not invalid_transition:
            current_phase = phase

        return StateSnapshot(
            current_phase=current_phase,
            session_open=session_open,
            last_event_type=event_type,
            last_pld_code=code,
            last_turn_sequence=turn_sequence,
            failover_active=failover_active,
        ), reason

