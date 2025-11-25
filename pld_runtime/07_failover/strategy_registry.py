# version: 0.1.1
# status: draft / template (Variant B)
# authority_level_scope: Level 5 — runtime implementation
# purpose: Provide a registry and factory helpers for wiring failover strategies,
#          backoff policies, and reconciliation policies into FailoverOrchestrators
#          without constructing or mutating PLD events.
# scope: Module-level runtime wiring only; PLD semantics are handled upstream.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Mapping, Optional

from .backoff_policies import (
    BackoffPolicy,
    ConstantBackoff,
    ExponentialBackoff,
    ExponentialJitterBackoff,
)
from .reconciliation import (
    ReconciliationPolicy,
    NoOpReconciliationPolicy,
    ThresholdReconciliationPolicy,
)
from .runtime_failover import FailoverOrchestrator, FailoverStrategy


# ---------------------------------------------------------------------------
# Factory Type Aliases (Level 5 only)
# ---------------------------------------------------------------------------

BackoffFactory = Callable[[Mapping[str, Any]], BackoffPolicy]
ReconciliationFactory = Callable[[Mapping[str, Any]], ReconciliationPolicy]


# ---------------------------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------------------------

def _to_optional_float(config: Mapping[str, Any], key: str) -> Optional[float]:
    """
    Helper for optional float casting with consistent error context.

    Used primarily for max_seconds-style parameters where None is meaningful.

    Core Technical Issue: Consolidates optional float handling to reduce
    duplication and simplify future numeric configuration extensions.
    """
    raw = config.get(key, None)
    if raw is None:
        return None
    try:
        return float(raw)
    except Exception as exc:
        raise ValueError(f"Invalid value for {key}: {raw!r}") from exc


# ---------------------------------------------------------------------------
# Default Backoff Policy Builders
# ---------------------------------------------------------------------------

def _build_constant_backoff(config: Mapping[str, Any]) -> BackoffPolicy:
    """
    Build a ConstantBackoff policy from config.

    Expected config keys (all optional):
      - delay_seconds: float (default: 1.0)

    Core Technical Issue Fix:
      - Type conversion now wrapped to provide consistent validation error context.
    """
    try:
        delay = float(config.get("delay_seconds", 1.0))
    except Exception as exc:
        raise ValueError(f"Invalid value for delay_seconds: {config.get('delay_seconds')!r}") from exc

    # TODO(CONFIG-VALIDATION-BOUNDARY): Confirm that semantic checks (e.g., delay_seconds >= 0)
    # should remain in the backoff policy implementation rather than here.
    return ConstantBackoff(delay_seconds=delay)


def _build_exponential_backoff(config: Mapping[str, Any]) -> BackoffPolicy:
    """
    Build an ExponentialBackoff policy from config.

    Expected config keys (all optional):
      - base_seconds: float (default: 1.0)
      - factor: float (default: 2.0)
      - max_seconds: float or None (default: None)

    Core Technical Issue Fix:
      - Type conversion now wrapped to provide consistent validation error context.
      - Optional max_seconds casting delegated to helper.

    TODO: max_seconds conversion shape could be simplified or consolidated further if
    additional numeric fields are added in future.
    """
    try:
        base = float(config.get("base_seconds", 1.0))
        factor = float(config.get("factor", 2.0))
    except Exception as exc:
        raise ValueError(f"Invalid configuration for exponential backoff: {config!r}") from exc

    max_seconds = _to_optional_float(config, "max_seconds")

    # TODO(CONFIG-VALIDATION-BOUNDARY): Confirm that semantic constraints (e.g., base > 0)
    # are consistently enforced in ExponentialBackoff.__post_init__ only.
    return ExponentialBackoff(
        base_seconds=base,
        factor=factor,
        max_seconds=max_seconds,
    )


def _build_exponential_jitter_backoff(config: Mapping[str, Any]) -> BackoffPolicy:
    """
    Build an ExponentialJitterBackoff policy from config.

    Expected config keys (all optional):
      - base_seconds: float (default: 1.0)
      - factor: float (default: 2.0)
      - jitter_ratio: float (default: 0.2)
      - max_seconds: float or None (default: None)

    Core Technical Issue Fix:
      - Type conversion now wrapped to provide consistent validation error context.
      - Optional max_seconds casting delegated to helper.

    TODO: Evaluate whether a shared validation helper should handle all numeric casting,
    not just optional fields like max_seconds.
    """
    try:
        base = float(config.get("base_seconds", 1.0))
        factor = float(config.get("factor", 2.0))
        jitter_ratio = float(config.get("jitter_ratio", 0.2))
    except Exception as exc:
        raise ValueError(f"Invalid configuration for exponential_jitter backoff: {config!r}") from exc

    max_seconds = _to_optional_float(config, "max_seconds")

    # TODO(CONFIG-VALIDATION-BOUNDARY): Confirm that semantic constraints (e.g., jitter_ratio in [0, 1])
    # remain enforced exclusively in ExponentialJitterBackoff.__post_init__.
    return ExponentialJitterBackoff(
        base_seconds=base,
        factor=factor,
        jitter_ratio=jitter_ratio,
        max_seconds=max_seconds,
    )


DEFAULT_BACKOFF_REGISTRY: Dict[str, BackoffFactory] = {
    "constant": _build_constant_backoff,
    "exponential": _build_exponential_backoff,
    "exponential_jitter": _build_exponential_jitter_backoff,
}


# ---------------------------------------------------------------------------
# Default Reconciliation Policy Builders
# ---------------------------------------------------------------------------

def _build_noop_reconciliation(config: Mapping[str, Any]) -> ReconciliationPolicy:
    """
    Build a NoOpReconciliationPolicy.

    Config is currently ignored; included for API symmetry.

    TODO(NOOP-CONFIG-BEHAVIOR): Clarify whether NoOpReconciliationPolicy should ever
    honor configuration (e.g., environment flags, logging hooks, or metadata stamping).
    """
    _ = config
    return NoOpReconciliationPolicy()


def _build_threshold_reconciliation(config: Mapping[str, Any]) -> ReconciliationPolicy:
    """
    Build a ThresholdReconciliationPolicy from config.

    Expected config keys (all optional):
      - threshold: int (default: 3)

    Core Technical Issue Fix:
      - Type conversion wrapped for consistent validation error context.
    """
    try:
        threshold_raw = config.get("threshold", 3)
        threshold = int(threshold_raw)
    except Exception as exc:
        raise ValueError(f"Invalid threshold value: {config.get('threshold')!r}") from exc

    # TODO(CONFIG-VALIDATION-BOUNDARY): Confirm that semantic meaning of threshold remains
    # encapsulated in ThresholdReconciliationPolicy itself.
    return ThresholdReconciliationPolicy(threshold=threshold)


DEFAULT_RECONCILIATION_REGISTRY: Dict[str, ReconciliationFactory] = {
    "noop": _build_noop_reconciliation,
    "threshold": _build_threshold_reconciliation,
}


# ---------------------------------------------------------------------------
# Failover Registry
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FailoverRegistry:
    """
    Registry for wiring strategies, backoff policies, and reconciliation policies.

    Responsibilities:
      - Provide named lookup for backoff and reconciliation policies.
      - Construct FailoverOrchestrator instances from declarative configuration.
      - MUST NOT construct, mutate, or interpret PLD events.

    TODO(STRATEGY-REGISTRATION-BOUNDARY): Confirm whether FailoverStrategy instances
    should remain application-managed (outside this registry) or if named strategy
    registration is desirable at this layer.
    """

    backoff_registry: Mapping[str, BackoffFactory] = field(
        default_factory=lambda: DEFAULT_BACKOFF_REGISTRY
    )
    reconciliation_registry: Mapping[str, ReconciliationFactory] = field(
        default_factory=lambda: DEFAULT_RECONCILIATION_REGISTRY
    )

    def create_backoff(
        self,
        *,
        name: str,
        config: Optional[Mapping[str, Any]] = None,
    ) -> BackoffPolicy:
        factory = self.backoff_registry.get(name)
        if factory is None:
            raise KeyError(f"Unknown backoff policy: {name!r}")
        return factory(config or {})

    def create_reconciliation(
        self,
        *,
        name: str,
        config: Optional[Mapping[str, Any]] = None,
    ) -> ReconciliationPolicy:
        factory = self.reconciliation_registry.get(name)
        if factory is None:
            raise KeyError(f"Unknown reconciliation policy: {name!r}")
        return factory(config or {})

    def create_orchestrator(
        self,
        *,
        strategy: FailoverStrategy,
        backoff_name: str,
        reconciliation_name: str,
        max_attempts: int = 3,
        backoff_config: Optional[Mapping[str, Any]] = None,
        reconciliation_config: Optional[Mapping[str, Any]] = None,
    ) -> FailoverOrchestrator:

        backoff = self.create_backoff(name=backoff_name, config=backoff_config)
        reconciliation = self.create_reconciliation(
            name=reconciliation_name,
            config=reconciliation_config,
        )
        return FailoverOrchestrator(
            strategy=strategy,
            backoff_policy=backoff,
            reconciliation_policy=reconciliation,
            max_attempts=max_attempts,
        )


DEFAULT_FAILOVER_REGISTRY = FailoverRegistry()
