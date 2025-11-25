# =============================================================================
# PLD Runtime Ingestion Configuration
# version: 2.0.0
# status: candidate  # runtime config; reasonably proven but still subject to change
# authority_level: 5
# authority_scope: runtime implementation
# purpose: Configure PLD v2 ingestion so that accepted events align with
#          Level 1 schema, Level 2 event matrix, and Level 3 runtime/metrics
#          expectations.
# change_classification: runtime extension (non-breaking)
# dependencies: pld_event.schema.json,
#               event_matrix.yaml,
#               PLD_Event_Semantic_Spec_v2.0.md,
#               PLD_Runtime_Standard_v2.0.md,
#               PLD_metrics_spec.md,
#               PLD_taxonomy_v2.0.md,
#               runtime_event_envelope.schema.json
# =============================================================================

"""
FILE MODE: runtime_template

This module provides a Level 5 ingestion configuration overlay for PLD v2
events. It MUST NOT redefine any rules from Levels 1–3. Instead, it binds
runtime behavior (paths, modes, and operational flags) to the canonical
specifications.

This file is a runtime extension / proposal and MUST be treated as Level 5
only. Any conflicts MUST be resolved in favor of Levels 1–3.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Literal, Mapping, Optional, Sequence


# ---------------------------------------------------------------------------
# Validation Modes
# ---------------------------------------------------------------------------
ValidationMode = Literal["strict", "warn", "normalize"]


# ---------------------------------------------------------------------------
# Core Ingestion Configuration
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SchemaRefs:
    """
    Canonical specification references used by the ingestion pipeline.

    NOTE:
    - Paths are repository-relative templates. Deployments MAY override them
      via environment-specific configuration, but MUST NOT change the
      underlying semantics of the referenced specifications.

    TODO: Clarify which Markdown specs are advisory-only versus intended for
          machine consumption, and whether parallel machine-readable artifacts
          are required beyond Level 1/2.
          (Source: Technical review — Open Questions: machine-consumability)
    """

    # Level 1 — Hard structural schema for events
    event_schema_path: str = "docs/schemas/pld_event.schema.json"

    # Level 2 — Semantic event matrix and supporting spec
    event_matrix_path: str = "docs/schemas/event_matrix.yaml"
    event_semantic_spec_path: str = "docs/PLD_Event_Semantic_Spec_v2.0.md"

    # Level 3 — Taxonomy, runtime operational standard, metrics schema/spec
    taxonomy_path: str = "docs/taxonomy/PLD_taxonomy_v2.0.md"
    runtime_standard_path: str = "docs/PLD_Runtime_Standard_v2.0.md"
    metrics_schema_path: str = "docs/schemas/metrics_schema.yaml"
    metrics_spec_path: str = "docs/metrics/PLD_metrics_spec.md"

    # Level 5 — Runtime overlay JSON Schema for the envelope
    runtime_envelope_schema_path: str = (
        "pld_runtime/01_schemas/runtime_event_envelope.schema.json"
    )


@dataclass(frozen=True)
class IngestionGuards:
    """
    Enforcement flags controlling how the ingestion pipeline applies Level 1–3
    rules at runtime.

    Updated based on Core Technical Issue (Level 1/2 MUSTs):
    - Level 1 and Level 2 enforcement MUST NOT be optional.
    - These fields are now read-only invariant constants.

    TODO: Clarify whether Level 3 enforcement will gain a dedicated guard
          structure analogous to Level 1/2 or remain distributed across
          multiple policy objects.
          (Source: Technical review — Open Questions: Level 3 scope)
    """

    # These MUST remain True and are no longer runtime configurable.
    enforce_level1_schema: bool = field(default=True, init=False)
    enforce_level2_matrix: bool = field(default=True, init=False)

    # Handling of SHOULD-level cases remains configurable.
    allow_should_violations_in_warn: bool = True
    allow_should_violations_in_normalize: bool = True

    # AUTH-004/005: handling of provisional vs pending taxonomy
    allow_provisional_taxonomy: bool = True
    reject_pending_taxonomy: bool = True


@dataclass(frozen=True)
class NormalizationPolicy:
    """
    Normalization behavior for events that are not trivially valid but may be
    made valid without contradicting Level 1–2 semantics.

    TODO: Define precise boundary of "persisted logs" and when normalization
          is forbidden (e.g., pre-ingestion vs replay pipelines).
          (Source: Technical review — Open Questions: normalization boundary)

    TODO: Define deterministic criteria for “clearly justified by context”
          during semantic correction (e.g., concrete rule sources and examples).
          (Source: Technical review — Open Questions: contextual correction)
    """

    enabled: bool = True

    # When True, the runtime MAY normalize pld.phase from event_type
    # using the Level 2 event matrix in "normalize" mode only.
    normalize_phase_from_event_type: bool = True

    # When True, the runtime MAY correct phase="none" to outcome for
    # session_closed / evaluation_* events when justified by higher-level rules.
    normalize_outcome_events: bool = True


@dataclass(frozen=True)
class ObservabilityPolicy:
    """
    Configuration for handling observability-only events and derived metrics
    staging data at ingestion time.

    TODO: Clarify canonical ownership of "observability-only" and M-prefix
          semantics (Level 2 matrix vs runtime standard vs taxonomy) and how
          this policy should behave in non-conversational contexts.
          (Source: Technical review — Open Questions: observability semantics)
    """

    # Whether to accept observability events (latency_spike, pause_detected,
    # handoff, info, etc.) in the ingestion pipeline.
    accept_observability_events: bool = True

    # Whether to accept M-prefix (derived metrics) codes as info/none events,
    # storing any staging data exclusively under runtime/extensions fields.
    accept_m_prefix_events: bool = True

    # Advisory constraint on how frequently M-prefix events should occur.
    min_turns_between_m_events: int = 5


@dataclass(frozen=True)
class RuntimeFieldPolicy:
    """
    Policies governing runtime/ux/metrics/extension fields within events.

    TODO: Clarify ownership and change-governance for runtime_reserved_keys
          and the UX/metrics responsibilities across Levels 3 and 5.
          (Source: Technical review — Open Questions: runtime field ownership)
    """

    # Whether ingestion enforces additional UX semantics beyond Level 1.
    enforce_ux_semantics: bool = False

    # Whether to allow ingestion of events that provide a non-empty "metrics"
    # object. Metrics MUST remain advisory and MUST NOT override canonical
    # metrics_schema.yaml logic.
    allow_inline_metrics_snapshots: bool = True

    # Reserved keys that runtimes SHOULD prefer inside `runtime` for
    # observability and derived metric staging. This list is advisory only.
    runtime_reserved_keys: Sequence[str] = field(
        default_factory=lambda: (
            "latency_ms",
            "model",
            "tool",
            "agent_state",
        )
    )


@dataclass(frozen=True)
class IngestionConfig:
    """
    Top-level configuration for PLD v2 ingestion.

    NOTE:
    - Singleton INGESTION_CONFIG is provided as a convenience only.

    TODO: Clarify whether a DI-first model will be required (config passed
          explicitly into ingestion pipeline constructors) or whether the
          module-level singleton remains an accepted pattern, and who binds
          environment-specific schema paths.
          (Source: Technical review — Open Questions: DI vs singleton)
    """

    schema_version: str = "2.0"
    validation_mode: ValidationMode = "strict"

    schema_refs: SchemaRefs = field(default_factory=SchemaRefs)
    guards: IngestionGuards = field(default_factory=IngestionGuards)
    normalization: NormalizationPolicy = field(default_factory=NormalizationPolicy)
    observability: ObservabilityPolicy = field(default_factory=ObservabilityPolicy)
    runtime_fields: RuntimeFieldPolicy = field(default_factory=RuntimeFieldPolicy)

    # Extra, implementation-specific configuration. This is normalized to an
    # immutable mapping in __post_init__ to preserve the frozen snapshot model.
    extra: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Core Technical Issue: ensure that `extra` is not a mutable side channel
        # on a frozen configuration object. Always store an immutable snapshot.
        object.__setattr__(self, "extra", MappingProxyType(dict(self.extra)))

    def is_normalization_enabled(self) -> bool:
        """Return True if normalization is permitted under the current mode."""
        return self.validation_mode == "normalize" and self.normalization.enabled

    def should_reject_must_violation(self) -> bool:
        """
        Indicate whether MUST-level violations are always rejected.

        This method intentionally encodes the invariant that Level 1 and Level 2
        MUST constraints are non-optional for ingestion; it does not attempt to
        distinguish between different classes of MUSTs that may be introduced
        at higher levels in the future.
        """
        return True

    def allows_should_violation(self) -> bool:
        """
        Return whether SHOULD-level violations are eligible for acceptance
        under the current validation_mode.

        This method does NOT incorporate per-event normalization outcomes.
        Callers MUST still:
        - perform any required normalization, and
        - apply their own logic to decide final acceptance on a per-event basis.

        Mode semantics:
        - strict: SHOULD violations are not eligible (always False).
        - warn: Eligible, but ingestion SHOULD surface warnings.
        - normalize: Eligible; caller MUST additionally check normalization
          results before final acceptance.
        """
        if self.validation_mode == "strict":
            return False

        if self.validation_mode == "warn":
            return self.guards.allow_should_violations_in_warn

        if self.validation_mode == "normalize":
            return self.guards.allow_should_violations_in_normalize

        # Defensive default: treat unknown modes as disallowing SHOULD-level
        # violations; mode validation may be tightened in the future.
        return False


# ---------------------------------------------------------------------------
# Default configuration factory
# ---------------------------------------------------------------------------

def default_ingestion_config(
    *,
    validation_mode: Optional[ValidationMode] = None,
) -> IngestionConfig:
    """
    Factory for the canonical default ingestion configuration.

    Args:
        validation_mode:
            Optional override for the validation mode. If None, "strict"
            is used, matching the Level 3 metrics schema default.

    TODO: Decide whether to enforce runtime validation of validation_mode
          values (e.g., raising on invalid strings) versus relying on static
          type checking at call sites.
          (Source: Technical review — Open Questions: mode validation)

    Returns:
        IngestionConfig: an immutable configuration instance suitable for
        use across the ingestion pipeline.
    """
    mode: ValidationMode = validation_mode or "strict"
    return IngestionConfig(validation_mode=mode)


# Singleton-style default used by simple integrations. More complex runtimes
# SHOULD inject their own IngestionConfig instance explicitly.
INGESTION_CONFIG: IngestionConfig = default_ingestion_config()


