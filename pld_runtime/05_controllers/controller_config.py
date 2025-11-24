# version: 1.0.0
# status: runtime
# authority_level_scope: Level 5 — runtime implementation
# purpose: Controller configuration template binding validation mode, taxonomy handling, and metrics usage for PLD-compatible runtimes.
# change_classification: runtime-only
# dependencies: PLD structural schema, semantic matrix, runtime standard, and metrics specification.

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import FrozenSet, Mapping, Optional


class ValidationMode(str, Enum):
    """
    Validation modes are aligned with Level 2 / Level 3 rules:
    - strict: reject MUST violations, ignore SHOULD violations.
    - warn:   reject MUST violations, warn on SHOULD violations.
    - normalize: attempt deterministic normalization for MUST violations.

    NOTE:
    - Deterministic normalization rules and algorithms are defined at Level 2/3
      (event matrix + semantic spec + runtime standard). This configuration
      only enables or disables their use at Level 5.
    """
    STRICT = "strict"
    WARN = "warn"
    NORMALIZE = "normalize"


# Canonical phases from Level 1 / Level 2 (includes "none" as a valid, reserved
# non-lifecycle state per the semantic matrix and none_phase_policy).
LIFECYCLE_PHASES: FrozenSet[str] = frozenset(
    [
        "drift",
        "repair",
        "reentry",
        "continue",
        "outcome",
        "failover",
        "none",
    ]
)

# Canonical event_type enumeration (mirrors Level 1 schema).
EVENT_TYPES: FrozenSet[str] = frozenset(
    [
        "drift_detected",
        "drift_escalated",
        "repair_triggered",
        "repair_escalated",
        "reentry_observed",
        "continue_allowed",
        "continue_blocked",
        "failover_triggered",
        "latency_spike",
        "pause_detected",
        "fallback_executed",
        "handoff",
        "evaluation_pass",
        "evaluation_fail",
        "session_closed",
        "info",
    ]
)

# Updated mapping per specification alignment requirement (Core Technical Issue #1).
EVENT_TYPE_PHASE_POLICY: Mapping[str, str] = {
    # MUST-level mappings
    "drift_detected": "drift",
    "drift_escalated": "drift",
    "repair_triggered": "repair",
    "repair_escalated": "repair",
    "reentry_observed": "reentry",
    "continue_allowed": "continue",
    "continue_blocked": "continue",
    "failover_triggered": "failover",

    # SHOULD-level defaults
    "evaluation_pass": "outcome",
    "evaluation_fail": "outcome",
    "session_closed": "outcome",
    "info": "none",

    # MAY-level events mapped with default allowed phase "none"
    # (actual allowed phases remain governed by Level 2 semantics).
    "latency_spike": "none",
    "pause_detected": "none",
    "fallback_executed": "none",
    "handoff": "none",
}

# Canonical metrics names (toggles only; definitions live in Level 3 metrics schema/spec).
CANONICAL_METRIC_NAMES: FrozenSet[str] = frozenset(
    [
        # Drift
        "drift_events_count",
        "drift_detected_count",
        "drift_escalated_count",
        # Repair
        "repair_events_count",
        "repair_triggered_count",
        "repair_escalated_count",
        # Reentry
        "reentry_events_count",
        "reentry_observed_count",
        # Continue
        "continue_events_count",
        "continue_allowed_count",
        "continue_blocked_count",
        # Outcome
        "outcome_events_count",
        "evaluation_pass_count",
        "evaluation_fail_count",
        "session_closed_outcome_count",
        # Failover
        "failover_events_count",
        "failover_triggered_count",
        "fallback_executed_failover_count",
        # Observability
        "latency_spike_count",
        "pause_detected_count",
        "handoff_count",
        "fallback_executed_count",
        "info_count",
    ]
)

# Canonical derived metric identifiers (M-prefix) are handled via runtime staging only.
DERIVED_METRIC_IDENTIFIERS: FrozenSet[str] = frozenset(
    [
        "M1_PRDR",  # Post-Repair Drift Recurrence
        "M2_VRL",   # Recovery Latency / Velocity Recovery Latency
        # Additional M-prefix identifiers may be governed at taxonomy level.
    ]
)


@dataclass(frozen=True)
class PhaseEnforcementConfig:
    """
    Controls how strictly the controller enforces phase / prefix / event_type rules.
    All logic MUST remain compatible with Level 1 and Level 2 constraints.

    NOTE:
    - Phase "none" is treated as a valid, reserved non-lifecycle state. Lifecycle
      prefix rules (D/R/RE/C/O/F) apply only when phase != "none", consistent
      with the Level 2 none_phase_policy.
    """

    # Enforce pld.phase membership in canonical phases (including "none").
    enforce_known_phases: bool = True

    # Enforce prefix ↔ phase mapping for lifecycle prefixes (D/R/RE/C/O/F),
    # excluding the reserved non-lifecycle state "none".
    enforce_prefix_phase_consistency: bool = True

    # Enforce event_type → phase mapping according to EVENT_TYPE_PHASE_POLICY
    # for MUST/SHOULD-level events.
    enforce_event_type_phase: bool = True

    # Require justification metadata when session_closed uses phase="none".
    require_session_closed_justification_for_none_phase: bool = True

    # Allow context-dependent MAY-level events in any phase (subject to EVENT_TYPES).
    allow_may_events_any_phase: bool = True

    # TODO: Where is the normalization logic or reference defined for NORMALIZE mode?
    #       A Level 2/3 specification link or identifier is needed. (Open Question)


@dataclass(frozen=True)
class TaxonomyConfig:
    """
    Controls treatment of taxonomy codes (pld.code) at the controller layer.
    This configuration MUST NOT redefine lifecycle semantics.

    NOTE:
    - "none" is a valid, reserved non-lifecycle state. When phase="none",
      lifecycle prefixes MUST NOT be used, and non-lifecycle prefixes
      (INFO, SYS, META, etc.) apply, per Level 2 semantics.
    - The two enforcement flags below form a two-way constraint:
        * enforce_none_phase_non_lifecycle_only ensures that when phase="none"
          lifecycle prefixes (D/R/RE/C/O/F) are disallowed.
        * restrict_non_lifecycle_prefixes_to_none_phase ensures that non-lifecycle
          prefixes (INFO, SYS, META, etc.) are only used when phase="none".
      When both are True (the default), the configuration enforces a strict
      division between lifecycle prefixes and non-lifecycle prefixes in line
      with Level 2 semantics. Turning either off relaxes one direction of this
      constraint and may deviate from the canonical none_phase_policy.
    """

    # Allow provisional codes when taxonomy_status="provisional" is present in pld.metadata.
    allow_provisional_codes: bool = True

    # When provisional codes are used, require justification metadata fields such as
    # taxonomy_status, reason, or evaluator notes.
    require_provisional_justification: bool = True

    # Enforce that lifecycle prefixes (D/R/RE/C/O/F) are not used with phase="none".
    enforce_none_phase_non_lifecycle_only: bool = True

    # Allow non-lifecycle prefixes (e.g., INFO, SYS, META) only with phase="none".
    restrict_non_lifecycle_prefixes_to_none_phase: bool = True


@dataclass(frozen=True)
class MetricsConfig:
    """
    Metrics configuration for the controller.
    This file enumerates which canonical metrics MAY be computed by the runtime.
    Definitions and formulas remain governed by Level 3 specifications.
    """

    # Global switch: if False, the controller MUST NOT emit any metrics payloads.
    enabled: bool = True

    # Whether the controller is allowed to pre-compute or stage derived metrics
    # into the "runtime" field for later aggregation.
    allow_runtime_staging_for_derived_metrics: bool = True

    # Set of canonical metric names that the runtime MAY compute.
    # Implementations SHOULD treat this as an allowlist, not a definition source.
    enabled_metric_names: FrozenSet[str] = field(
        default_factory=lambda: CANONICAL_METRIC_NAMES
    )

    # Whether M-prefix derived metric identifiers (e.g., M1_PRDR, M2_VRL)
    # are allowed to be attached as runtime-local staging data.
    enable_m_prefix_identifiers: bool = True

    # Config flag to define behavior when a `fallback_executed` should increment
    # phase-specific vs general metric. When True, phase-specific failover
    # counting must follow the Level 3 failover metric semantics.
    enforce_phase_specific_failover_counting: bool = True

    # TODO: Confirm whether derived metric calculation is Level 3 responsibility
    #       with Level 5 only staging data, or if Level 5 is expected to host
    #       the algorithms themselves. (Open Question)
    # TODO: Future-stage concern: if other event types gain phase-specific
    #       metrics, this flag may need to evolve into a more general policy
    #       (e.g., phase_specific_counting_policy). (Open Question)


@dataclass(frozen=True)
class ControllerConfig:
    """
    Top-level controller configuration for PLD-compatible runtimes.

    This configuration is a Level 5 runtime implementation artifact and MUST
    remain consistent with:
      - Level 1 structural schema (PLD event schema)
      - Level 2 semantic event matrix
      - Level 3 runtime standard and metrics specification

    NOTE:
    - Normalization behavior (NORMALIZE mode) MUST follow the Level 2/3
      normalization guidance (event matrix validation_modes.normalize and
      the semantic spec). This configuration does not define algorithms.
    - TODO: Provide a canonical identifier or version tag for the external
      normalization specification referenced here (e.g., "Normalization Spec vX.Y").
      (Open Question)
    """

    # Controller configuration version (independent of schema_version).
    version: str = "1.0.0"

    # Structural schema version the controller expects.
    schema_version: str = "2.0"

    # Default validation mode for runtime operation.
    validation_mode: ValidationMode = ValidationMode.STRICT

    # Whether the controller is allowed to perform deterministic normalization
    # in NORMALIZE mode, without mutating persisted logs.
    allow_normalization_in_normalize_mode: bool = True

    # Whether events with schema_version != expected schema_version are rejected.
    reject_major_version_mismatch: bool = True

    # Configure whether the controller should enforce that turn_sequence is:
    # - present
    # - >= 1
    # - monotonically increasing within a given session_id.
    enforce_turn_sequence_monotonicity: bool = True

    # Enforcement for phases / prefixes / event_type mappings.
    phase_enforcement: PhaseEnforcementConfig = field(
        default_factory=PhaseEnforcementConfig
    )

    # Taxonomy handling policy for pld.code and metadata.
    taxonomy: TaxonomyConfig = field(default_factory=TaxonomyConfig)

    # Metrics computation / staging configuration.
    metrics: MetricsConfig = field(default_factory=MetricsConfig)

    # Optional human-readable identifier for the controller profile (e.g., "prod", "staging").
    profile_name: Optional[str] = None

    # TODO: Confirm whether minor version parsing (2.x) acceptance and compatibility
    #       guarantees for v2.x events are provided by the runtime standard when
    #       reject_major_version_mismatch is True. (Open Question)


# Default configuration instance.
DEFAULT_CONTROLLER_CONFIG = ControllerConfig()
