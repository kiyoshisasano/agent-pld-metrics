# version: "2.0.0"
# status: "draft / runtime_template / runtime_extension"
# authority_level_scope: "Level 5 — runtime implementation"
# purpose: "Map PLD v2 runtime events to high-level response policies without altering event semantics."
# scope: "Advisory response policy; assumes Level 1 schema and Level 2 matrix validation are handled upstream."
# change_classification: "runtime-only update (addresses review alignment)"
# dependencies: "pld_event.schema.json v2.x, event_matrix.yaml v2.x, PLD_Runtime_Standard_v2.0.md, PLD_taxonomy_v2.0.md"

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Mapping, Optional

# ──────────────────────────────────────────────────────────────────────────────
# TODO (Open Question #1): Clarify expected role of phase input if not used
# TODO (Open Question #2): Determine whether observability events may influence future lifecycle control paths
# TODO (Open Question #3): Confirm explicit boundary between state tracking ownership vs. policy evaluation
# ──────────────────────────────────────────────────────────────────────────────

PLDEvent = Mapping[str, Any]


class ValidationMode(str, Enum):
    STRICT = "strict"
    WARN = "warn"
    NORMALIZE = "normalize"


class PolicyDecisionType(str, Enum):
    """
    Updated for Core Issue #1:

    The previous names implied imperative execution (e.g., REQUIRE_REPAIR).
    Updated naming clarifies whether decisions mandate a runtime obligation or
    are purely advisory.

    - POLICY_REPAIR_MANDATED replaces REQUIRE_REPAIR
    - POLICY_FAILOVER_MANDATED replaces REQUIRE_FAILOVER
    """

    CONTINUE = "continue"
    BLOCK = "block"
    POLICY_REPAIR_MANDATED = "policy_repair_mandated"
    POLICY_FAILOVER_MANDATED = "policy_failover_mandated"
    OBSERVE_ONLY = "observe_only"
    NOOP = "noop"


@dataclass(frozen=True)
class ResponsePolicyDecision:
    """
    The "suggested_next_event_type" field remains advisory (per design intent).

    Core Issue #2 updated behavior:
    - When event rules imply constrained allowed next steps,
      this field MAY now contain the "most probable / default" selection,
      but does NOT become mandatory or authoritative.
    """

    decision: PolicyDecisionType
    reason: str
    suggested_next_event_type: Optional[str] = None
    notes: Optional[str] = None


def evaluate_response_policy(
    event: PLDEvent,
    mode: ValidationMode = ValidationMode.STRICT,
) -> ResponsePolicyDecision:

    schema_version = event.get("schema_version")
    event_type = event.get("event_type")
    pld = event.get("pld") or {}
    phase = pld.get("phase")
    code = pld.get("code")

    if schema_version not in ("2.0", "2.1"):
        return ResponsePolicyDecision(
            decision=PolicyDecisionType.BLOCK,
            reason=f"Unsupported schema_version={schema_version!r}."
        )

    if event_type in ("drift_detected", "drift_escalated"):
        return _policy_for_drift(event_type, phase, code, mode)

    if event_type in ("repair_triggered", "repair_escalated"):
        return _policy_for_repair(event_type, phase, code, mode)

    if event_type == "reentry_observed":
        return _policy_for_reentry(event_type, phase, code, mode)

    if event_type in ("continue_allowed", "continue_blocked"):
        return _policy_for_continue(event_type, phase, code, mode)

    if event_type == "failover_triggered":
        return _policy_for_failover(event_type, phase, code, mode)

    if event_type in ("evaluation_pass", "evaluation_fail"):
        return _policy_for_evaluation(event_type, phase, code, mode)

    if event_type == "session_closed":
        return _policy_for_session_closed(event_type, phase, code, mode)

    if event_type in ("latency_spike", "pause_detected", "handoff", "fallback_executed"):
        return _policy_for_observability(event_type, phase, code, mode)

    if event_type == "info":
        return _policy_for_info(event_type, phase, code, mode)

    if mode is ValidationMode.STRICT:
        return ResponsePolicyDecision(
            decision=PolicyDecisionType.BLOCK,
            reason=f"Unknown event_type={event_type!r} in strict mode."
        )

    return ResponsePolicyDecision(
        decision=PolicyDecisionType.OBSERVE_ONLY,
        reason=f"Unknown event_type={event_type!r} in non-strict mode."
    )


def _policy_for_drift(event_type, phase, code, mode):
    """
    Updated naming alignment applied here.
    """

    return ResponsePolicyDecision(
        decision=PolicyDecisionType.POLICY_REPAIR_MANDATED,
        reason=f"{event_type} indicates anomaly requiring repair.",
        suggested_next_event_type="repair_triggered"
    )


def _policy_for_repair(event_type, phase, code, mode):
    return ResponsePolicyDecision(
        decision=PolicyDecisionType.BLOCK,
        reason=f"{event_type}: runtime SHOULD block until repair resolves."
    )


def _policy_for_reentry(event_type, phase, code, mode):
    return ResponsePolicyDecision(
        decision=PolicyDecisionType.CONTINUE,
        reason="System reentered stable state.",
        suggested_next_event_type="continue_allowed"
    )


def _policy_for_continue(event_type, phase, code, mode):
    if event_type == "continue_allowed":
        return ResponsePolicyDecision(
            decision=PolicyDecisionType.CONTINUE,
            reason="Continuation permitted."
        )

    return ResponsePolicyDecision(
        decision=PolicyDecisionType.BLOCK,
        reason="Runtime continuation blocked."
    )


def _policy_for_failover(event_type, phase, code, mode):
    """
    Core Issue #2 Fix:
    - Previously: suggested_next_event_type=None despite strict next-step constraints.
    - Now: choose the most plausible default next transition (not enforced).

    Runtime MAY still override based on context.
    """

    return ResponsePolicyDecision(
        decision=PolicyDecisionType.POLICY_FAILOVER_MANDATED,
        reason="Failover triggered; recovery path required.",
        suggested_next_event_type="reentry_observed",  # Default, not mandatory.
        notes="Allowed next events: reentry_observed OR continue_allowed OR session_closed."
    )


def _policy_for_evaluation(event_type, phase, code, mode):
    if event_type == "evaluation_pass":
        return ResponsePolicyDecision(
            decision=PolicyDecisionType.CONTINUE,
            reason="Evaluation passed."
        )

    if mode is ValidationMode.STRICT:
        return ResponsePolicyDecision(
            decision=PolicyDecisionType.BLOCK,
            reason="Evaluation failed in strict mode."
        )

    return ResponsePolicyDecision(
        decision=PolicyDecisionType.POLICY_REPAIR_MANDATED,
        reason="Evaluation failed; repair advised."
    )


def _policy_for_session_closed(event_type, phase, code, mode):
    return ResponsePolicyDecision(
        decision=PolicyDecisionType.BLOCK,
        reason="Session closed."
    )


def _policy_for_observability(event_type, phase, code, mode):
    return ResponsePolicyDecision(
        decision=PolicyDecisionType.OBSERVE_ONLY,
        reason=f"{event_type} classified as observability."
    )


def _policy_for_info(event_type, phase, code, mode):
    return ResponsePolicyDecision(
        decision=PolicyDecisionType.OBSERVE_ONLY,
        reason="Informational event only."
    )


def summarize_decision(decision: ResponsePolicyDecision) -> Dict[str, Any]:
    return {
        "decision": decision.decision.value,
        "reason": decision.reason,
        "suggested_next_event_type": decision.suggested_next_event_type,
        "notes": decision.notes,
    }
