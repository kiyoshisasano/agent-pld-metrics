# version: 2.0.0
# status: draft / template (Variant B)
# authority_level_scope: Level 5 — runtime implementation
# purpose: Orchestrate failover execution using pluggable strategies, backoff, and reconciliation
#          without constructing or mutating PLD events directly.
# scope: Module-level coordination only; event semantics and construction are handled upstream.

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Mapping, Optional, Protocol

from .backoff_policies import BackoffPolicy
from .reconciliation import (
    ReconciliationOutcome,
    ReconciliationPolicy,
    ReconciliationResult,
)


# ---------------------------------------------------------------------------
# Runtime Type Aliases (Level 5 only)
# ---------------------------------------------------------------------------

RuntimeMetadata = Mapping[str, Any]
EmitSignalFn = Callable[[str, Mapping[str, Any]], None]
LogRuntimeFn = Callable[[str, Mapping[str, Any]], None]


# ---------------------------------------------------------------------------
# Failover State Model
# ---------------------------------------------------------------------------

class FailoverStatus(str, Enum):
    """
    Runtime-local status for a failover session.

    Notes:
      - These values are purely operational and MUST NOT be mapped directly
        to PLD phases or codes.
    """
    IDLE = "idle"          # No active failover.
    ACTIVE = "active"      # Failover attempts in progress.
    EXHAUSTED = "exhausted"  # No further attempts planned.


@dataclass(frozen=True)
class FailoverState:
    """
    Immutable state snapshot for a session-level failover lifecycle.

    Fields:
      - session_id: REQUIRED runtime session identifier (matches PLD session_id).
      - attempt: 1-based count of failover attempts (0 when not yet started).
      - status: FailoverStatus flag for orchestrator coordination.
      - last_error: Optional machine-readable error code or message.
      - metadata: Optional runtime-local state (MUST NOT contain PLD events).
    """

    session_id: str
    attempt: int = 0
    status: FailoverStatus = FailoverStatus.IDLE
    last_error: Optional[str] = None
    metadata: RuntimeMetadata = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Strategy Context & Protocol
# ---------------------------------------------------------------------------

@dataclass
class FailoverContext:
    """
    Context provided to failover strategies.

    Constraints:
      - MUST NOT expose raw PLD events for mutation.
      - All PLD event emission MUST be routed through injected callbacks that
        are implemented by higher-level runtime components.
    """

    session_id: str
    attempt: int
    runtime_metadata: RuntimeMetadata
    emit_signal: EmitSignalFn
    log_runtime: Optional[LogRuntimeFn] = None

    # Core Technical Fix (required):
    # Strategy may record success or failure state in this attribute.
    last_error: Optional[str] = None

    # TODO (Open Question): Should strategy success/failure reporting use a more explicit
    # structured result model instead of a single attribute?

    def emit(self, signal_kind: str, payload: Mapping[str, Any]) -> None:
        self.emit_signal(signal_kind, payload)

    def log(self, message: str, fields: Optional[Mapping[str, Any]] = None) -> None:
        if self.log_runtime is None:
            return
        self.log_runtime(message, dict(fields or {}))


class FailoverStrategy(Protocol):
    """
    Contract for a failover strategy implementation.

    Responsibilities:
      - Use FailoverContext.emit(...) to signal failover-related events.
      - Use FailoverContext.log(...) for runtime observability.
      - MUST NOT construct or mutate PLD event dicts directly.
      - Strategy SHOULD update context.last_error to reflect current attempt outcome.
    """

    def name(self) -> str:
        ...

    def execute(self, context: FailoverContext) -> None:
        ...


# ---------------------------------------------------------------------------
# Orchestrator Result Model
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FailoverStepResult:
    """
    Result of a single orchestrated failover step.

    Fields:
      - state: Updated FailoverState snapshot.
      - reconciliation: ReconciliationResult from the configured policy.
      - backoff_delay: Optional delay in seconds suggested before the next
                       attempt (None if no further backoff is needed).
    """

    state: FailoverState
    reconciliation: ReconciliationResult
    backoff_delay: Optional[float]


# ---------------------------------------------------------------------------
# Failover Orchestrator
# ---------------------------------------------------------------------------

@dataclass
class FailoverOrchestrator:
    """
    Orchestrate failover strategies using backoff and reconciliation policies.

    Constraints:
      - MUST NOT construct or mutate PLD events directly.
      - All PLD event emission MUST pass through emit_signal callbacks that
        integrate with RuntimeSignalBridge and controllers.
      - MUST remain agnostic to PLD event schema and semantic details.
    """

    strategy: FailoverStrategy
    backoff_policy: BackoffPolicy
    reconciliation_policy: ReconciliationPolicy
    max_attempts: int = 3

    def initialize(self, session_id: str, metadata: Optional[RuntimeMetadata] = None) -> FailoverState:
        return FailoverState(
            session_id=session_id,
            attempt=0,
            status=FailoverStatus.IDLE,
            last_error=None,
            metadata=dict(metadata or {}),
        )

    def run_step(
        self,
        state: FailoverState,
        *,
        emit_signal: EmitSignalFn,
        log_runtime: Optional[LogRuntimeFn] = None,
        runtime_metadata: Optional[RuntimeMetadata] = None,
    ) -> FailoverStepResult:

        if state.status is FailoverStatus.EXHAUSTED:
            reconciliation = ReconciliationResult(
                outcome=ReconciliationOutcome.FINALIZE,
                reason_code="already_exhausted",
                detail={"attempt": state.attempt, "max_attempts": self.max_attempts},
            )
            return FailoverStepResult(state=state, reconciliation=reconciliation, backoff_delay=None)

        next_attempt = state.attempt + 1
        if next_attempt > self.max_attempts:
            exhausted_state = FailoverState(
                session_id=state.session_id,
                attempt=state.attempt,
                status=FailoverStatus.EXHAUSTED,
                last_error="max_attempts_exceeded",
                metadata=state.metadata,
            )
            reconciliation = ReconciliationResult(
                outcome=ReconciliationOutcome.FINALIZE,
                reason_code="max_attempts_exceeded",
                detail={"attempt": state.attempt, "max_attempts": self.max_attempts},
            )
            return FailoverStepResult(state=exhausted_state, reconciliation=reconciliation, backoff_delay=None)

        merged_metadata: RuntimeMetadata = {
            **dict(state.metadata or {}),
            **dict(runtime_metadata or {}),
        }

        context = FailoverContext(
            session_id=state.session_id,
            attempt=next_attempt,
            runtime_metadata=merged_metadata,
            emit_signal=emit_signal,
            log_runtime=log_runtime,
        )

        self.strategy.execute(context)

        # Core Technical Fix: Use the most recent error as reported by the strategy.
        updated_last_error = context.last_error

        reconciliation_input = {
            "session_id": state.session_id,
            "attempt_count": next_attempt,
            "strategy_name": self.strategy.name(),
            "metadata": merged_metadata,
        }

        # TODO (Open Question): Should reconciliation policies receive FailoverState directly?

        reconciliation = self.reconciliation_policy.evaluate(reconciliation_input)

        if reconciliation.outcome is ReconciliationOutcome.CONTINUE:
            next_status = FailoverStatus.ACTIVE
        elif reconciliation.outcome is ReconciliationOutcome.RECOVER:
            next_status = FailoverStatus.IDLE  # TODO: Confirm intended terminal lifecycle transition here.
        elif reconciliation.outcome is ReconciliationOutcome.FINALIZE:
            next_status = FailoverStatus.EXHAUSTED
        else:
            next_status = FailoverStatus.EXHAUSTED  # UNKNOWN treated as terminal.

        next_state = FailoverState(
            session_id=state.session_id,
            attempt=next_attempt,
            status=next_status,
            last_error=updated_last_error,   # <-- Correct state propagation
            metadata=merged_metadata,
        )

        # TODO (Open Question): Should terminal outcomes ever trigger automatic PLD emission?

        if reconciliation.outcome is ReconciliationOutcome.CONTINUE:
            backoff_delay = self.backoff_policy.next_delay(next_attempt)
        else:
            backoff_delay = None
            # TODO (Open Question): Should backoff also occur after strategy exceptions requiring retry?

        return FailoverStepResult(
            state=next_state,
            reconciliation=reconciliation,
            backoff_delay=backoff_delay,
        )
