# component_id: enforcement_thresholds
# kind: runtime_module
# area: enforcement
# status: draft
# authority_level: 5
# version: 2.0.0
# license: Apache-2.0
# purpose: Threshold templates for runtime enforcement of PLD metrics.

"""
Notes:
- Core Technical Issues from reviews integrated (sanity-bound clamping + config ordering validation).
- Architecture intent and naming preserved.
- Open Questions are captured as TODO comments and intentionally unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Mapping, Optional


class Severity(str, Enum):
    """Runtime-local severity classification for metric threshold evaluation."""

    OK = "ok"
    WARN = "warn"
    CRITICAL = "critical"
    # TODO (Open Question: Missing ANOMALY State):
    #   Determine whether a distinct ANOMALY severity is required to
    #   differentiate:
    #     - "normal CRITICAL" values within [hard_min, hard_max], vs.
    #     - values that violate hard_min/hard_max sanity bounds.
    #   If required, ANOMALY MUST be explicitly integrated into the
    #   evaluation contract and returned when clamping occurs.


@dataclass(frozen=True)
class MetricThreshold:
    """
    Threshold configuration for a single metric.

    Attributes:
        warn:
            Value at or beyond which WARN is raised (direction-dependent).
        critical:
            Value at or beyond which CRITICAL is raised (direction-dependent).
        higher_is_worse:
            If True, larger values are worse; if False, smaller values are worse.

        hard_min, hard_max:
            Sanity validation bounds only. Violations trigger clamping behavior
            before evaluation. They are NOT policy thresholds and MUST NOT
            bypass warn/critical logic.

            This resolves the earlier inconsistency between hard_min and
            hard_max handling (Core Technical Issues #1 and #2).

    Notes:
        - Configuration ordering integrity for warn/critical is validated in
          __post_init__ to ensure consistency with higher_is_worse.
    """

    warn: Optional[float]
    critical: Optional[float]
    higher_is_worse: bool = True
    hard_min: Optional[float] = None
    hard_max: Optional[float] = None

    # TODO (Open Question: Explicit Unit Definition):
    #   Consider adding an explicit `unit: Optional[str]` field (e.g., "seconds",
    #   "turns") so that threshold values for metrics like VRL can be interpreted
    #   correctly by external monitoring systems and during debugging.

    def __post_init__(self) -> None:
        """
        Enforce configuration logic integrity for warn/critical thresholds.

        Core Technical Issue: Configuration Logic Integrity
        ---------------------------------------------------
        If both warn and critical are provided, they MUST satisfy:

            - higher_is_worse == True  →  critical >= warn
            - higher_is_worse == False →  critical <= warn

        Violations indicate misconfiguration and result in a ValueError.
        This keeps Level 5 behavior robust and prevents understated severity
        due to inverted thresholds.
        """
        if self.warn is None or self.critical is None:
            return

        if self.higher_is_worse and self.critical < self.warn:
            raise ValueError(
                f"Inconsistent MetricThreshold configuration for higher_is_worse=True: "
                f"critical ({self.critical}) < warn ({self.warn})."
            )

        if not self.higher_is_worse and self.critical > self.warn:
            raise ValueError(
                f"Inconsistent MetricThreshold configuration for higher_is_worse=False: "
                f"critical ({self.critical}) > warn ({self.warn})."
            )


# ---------------------------------------------------------------------------
# Default metric thresholds (runtime template, non-normative)
# ---------------------------------------------------------------------------

DEFAULT_THRESHOLDS: Dict[str, MetricThreshold] = {
    # PRDR — Post-Repair Drift Recurrence (0–100, percent).
    "PRDR": MetricThreshold(
        warn=30.0,
        critical=50.0,
        higher_is_worse=True,
        hard_min=0.0,
        hard_max=100.0,
    ),
    # VRL — Recovery Latency (seconds or turns, implementation-defined).
    "VRL": MetricThreshold(
        warn=10.0,
        critical=30.0,
        higher_is_worse=True,
        hard_min=0.0,
        hard_max=None,
    ),
    # FR — Failover Recurrence Index (0–1 ratio).
    "FR": MetricThreshold(
        warn=0.10,
        critical=0.25,
        higher_is_worse=True,
        hard_min=0.0,
        hard_max=1.0,
    ),
}


def _apply_sanity_bounds(value: float, config: MetricThreshold) -> float:
    """
    Adjust value to sanity boundaries if necessary.

    Values falling outside [hard_min, hard_max] are clamped to the closest
    boundary and THEN evaluated against warn/critical thresholds. This ensures:

      - hard_min / hard_max remain sanity constraints, not policy thresholds.
      - Evaluation logic is not bypassed by bound violations.

    This behavior implements the corrected interpretation requested in the
    Core Technical Issues review.
    """
    if config.hard_min is not None and value < config.hard_min:
        return config.hard_min

    if config.hard_max is not None and value > config.hard_max:
        return config.hard_max

    return value


def evaluate_metric(
    metric_name: str,
    value: float,
    thresholds: Mapping[str, MetricThreshold] = DEFAULT_THRESHOLDS,
) -> Severity:
    """
    Evaluate a metric and assign a severity level.

    - Sanity bounds (hard_min/hard_max) are applied as clamping prior to
      evaluation and DO NOT override the warn/critical policy thresholds.
    - Configuration ordering integrity is enforced via MetricThreshold.__post_init__,
      which protects against misordered warn/critical values relative to
      higher_is_worse.

    This function remains a Level 5 helper:
      - It MUST only be called with metrics derived from PLD-valid events.
      - It MUST NOT perform schema or semantic validation.
    """
    config = thresholds.get(metric_name)
    if config is None:
        return Severity.OK

    # Apply corrected sanity enforcement (clamping, not bypassing policy).
    value = _apply_sanity_bounds(value, config)

    # If no actionable thresholds exist, severity remains OK.
    if config.warn is None and config.critical is None:
        return Severity.OK

    # MAIN POLICY EVALUATION
    if config.higher_is_worse:
        if config.critical is not None and value >= config.critical:
            return Severity.CRITICAL
        if config.warn is not None and value >= config.warn:
            return Severity.WARN
    else:
        # Smaller values are worse.
        if config.critical is not None and value <= config.critical:
            return Severity.CRITICAL
        if config.warn is not None and value <= config.warn:
            return Severity.WARN

    return Severity.OK


def get_threshold(metric_name: str) -> Optional[MetricThreshold]:
    """Retrieve threshold configuration for external inspection."""
    return DEFAULT_THRESHOLDS.get(metric_name)

