# component_id: reconciliation
# kind: runtime_module
# area: failover
# status: draft
# authority_level: 5
# version: 2.0.0
# license: Apache-2.0
# purpose: Runtime reconciliation logic determining continuation, revert, or finalize paths in failover operations.

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol, Optional, Mapping, Any


# ---------------------------------------------------------------------------
# Result Model
# ---------------------------------------------------------------------------

class ReconciliationOutcome(str, Enum):
    """
    The reconciliation result category returned to the failover orchestrator.

    Notes:
      - Values reflect runtime operational intent, not PLD semantics.
      - The orchestrator decides how/when to act; this file only classifies inputs.
    """
    CONTINUE = "continue"          # Failover state persists.
    RECOVER = "recover"            # Suggest re-entry into normal running mode.
    FINALIZE = "finalize"          # No further reconciliation required.
    UNKNOWN = "unknown"            # Input insufficient or incomplete.


@dataclass(frozen=True)
class ReconciliationResult:
    """
    Structured result returned by reconciliation logic.

    Fields:
      - outcome: REQUIRED ReconciliationOutcome.
      - reason_code: OPTIONAL short machine-readable diagnostic.
      - detail: OPTIONAL structured notes or metadata for observability.
    """
    outcome: ReconciliationOutcome
    reason_code: Optional[str] = None
    detail: Optional[Mapping[str, Any]] = None


# ---------------------------------------------------------------------------
# Policy Protocol
# ---------------------------------------------------------------------------

class ReconciliationPolicy(Protocol):
    """
    Contract for reconciliation strategies.

    Constraints:
      - MUST NOT construct, modify, or infer new PLD events.
      - MUST operate only on already-validated runtime state.
      - SHOULD support both synchronous and async orchestration use cases.
    """

    def evaluate(self, state: Mapping[str, Any]) -> ReconciliationResult:
        """
        Evaluate runtime state and produce a reconciliation result.

        Input expectations:
          - `state` MAY include:
              * last_event_type
              * attempt_count
              * failure_reason
              * internal runtime metadata
          - The policy MUST NOT assume schema presence beyond keys it documents.
        """
        ...


# ---------------------------------------------------------------------------
# Default No-Op Policy
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class NoOpReconciliationPolicy:
    """
    A baseline reconciliation strategy that always returns UNKNOWN.

    Use Cases:
      - Placeholder policy before configuration binding.
      - Diagnostic or testing scenarios.
    """

    def evaluate(self, state: Mapping[str, Any]) -> ReconciliationResult:
        return ReconciliationResult(
            outcome=ReconciliationOutcome.UNKNOWN,
            reason_code="noop",
            detail={"state_passthrough": dict(state)},
        )


# ---------------------------------------------------------------------------
# Minimal Rule-Based Policy (Example Only — Runtime Template)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ThresholdReconciliationPolicy:
    """
    A rule-based reconciliation policy driven by retry threshold.

    Behavior:
      - If attempt_count < threshold → CONTINUE
      - If attempt_count == threshold → RECOVER
      - If attempt_count > threshold → FINALIZE

    Notes:
      - This policy does NOT interpret lifecycle semantics.
      - Threshold numbers do NOT map to PLD meanings and remain runtime-only.
    """

    threshold: int = 3

    def evaluate(self, state: Mapping[str, Any]) -> ReconciliationResult:
        attempt = state.get("attempt_count")

        # Defensive safety: avoid assuming structure beyond minimum requirement.
        if not isinstance(attempt, int) or attempt < 1:
            return ReconciliationResult(
                outcome=ReconciliationOutcome.UNKNOWN,
                reason_code="invalid_attempt_value",
                detail={"attempt_raw": attempt},
            )

        if attempt < self.threshold:
            return ReconciliationResult(
                outcome=ReconciliationOutcome.CONTINUE,
                reason_code="below_threshold",
                detail={"attempt": attempt, "threshold": self.threshold},
            )

        if attempt == self.threshold:
            return ReconciliationResult(
                outcome=ReconciliationOutcome.RECOVER,
                reason_code="threshold_reached",
                detail={"attempt": attempt, "threshold": self.threshold},
            )

        return ReconciliationResult(
            outcome=ReconciliationOutcome.FINALIZE,
            reason_code="exceeded_threshold",
            detail={"attempt": attempt, "threshold": self.threshold},
        )


# ---------------------------------------------------------------------------
# Helper Function (Optional)
# ---------------------------------------------------------------------------

def reconcile(policy: ReconciliationPolicy, state: Mapping[str, Any]) -> ReconciliationResult:
    """
    Execute reconciliation using a provided policy.

    Notes:
      - Helper for synchronous orchestration flows.
      - Caller is responsible for interpreting the returned outcome.
    """
    return policy.evaluate(state)

