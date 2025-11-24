# version: 1.0.0
# status: draft
# authority_level_scope: Level 5 — runtime implementation
# purpose: PLD runtime controller template for validation, normalization routing, and metrics staging.
# change_classification: runtime extension (non-breaking)
# dependencies: Level 1 PLD event schema, Level 2 event matrix + semantic spec, Level 3 runtime standard + metrics spec.

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple

try:
    from .controller_config import (
        ControllerConfig,
        DEFAULT_CONTROLLER_CONFIG,
        EVENT_TYPE_PHASE_POLICY,
        LIFECYCLE_PHASES,
        ValidationMode,
    )
except ImportError:  # Standalone execution or no package context
    try:
        # Fallback to absolute import when running as a script
        from controller_config import (
            ControllerConfig,
            DEFAULT_CONTROLLER_CONFIG,
            EVENT_TYPE_PHASE_POLICY,
            LIFECYCLE_PHASES,
            ValidationMode,
        )
    except ImportError:
        # NOTE: Fallback definitions are intended for standalone / smoke-test
        #       scenarios only. They are not a replacement for the canonical
        #       Level 3 configuration and MUST NOT be treated as production
        #       defaults.
        # Minimal self-contained fallback definitions so this module can run by itself
        from dataclasses import dataclass
        from enum import Enum
        from typing import Any, Mapping, Tuple

        class ValidationMode(Enum):
            STRICT = "strict"
            WARN = "warn"
            NORMALIZE = "normalize"

        @dataclass(frozen=True)
        class PhaseEnforcementConfig:
            enforce_known_phases: bool = True
            enforce_event_type_phase: bool = True

        @dataclass(frozen=True)
        class MetricsConfig:
            enabled: bool = False
            enforce_phase_specific_failover_counting: bool = False
            enabled_metric_names: Tuple[str, ...] = ()

        @dataclass(frozen=True)
        class ControllerConfig:
            schema_version: str = "2.0"
            reject_major_version_mismatch: bool = True
            validation_mode: ValidationMode = ValidationMode.STRICT
            allow_normalization_in_normalize_mode: bool = True
            phase_enforcement: PhaseEnforcementConfig = PhaseEnforcementConfig()
            metrics: MetricsConfig = MetricsConfig()
            taxonomy: Optional[Mapping[str, Any]] = None

        LIFECYCLE_PHASES: Tuple[str, ...] = (
            "drift",
            "repair",
            "reentry",
            "continue",
            "outcome",
            "failover",
            "none",
        )

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

        DEFAULT_CONTROLLER_CONFIG = ControllerConfig()


class ValidationSeverity(Enum):
    MUST = auto()
    SHOULD = auto()
    MAY = auto()


@dataclass(frozen=True)
class ValidationIssue:
    """
    Represents a single validation issue detected by the controller.

    NOTE:
    - This structure is Level 5 only and MUST NOT be used to redefine Level 1/2 rules.
    - `rule_id` may reference Level 2 matrix rules or Level 3 runtime rules.
    """

    rule_id: str
    message: str
    severity: ValidationSeverity
    field_path: str


@dataclass(frozen=True)
class ValidationResult:
    """
    Aggregated validation result for a single event.

    NOTE:
    - `is_valid` is interpreted in terms of the active ValidationMode
      and the distinction between MUST / SHOULD violations.
    - `has_should_violations` allows embedding runtimes (particularly in WARN
      mode) to surface warnings for SHOULD-level issues even when the event
      remains valid.
    """

    is_valid: bool
    has_should_violations: bool
    issues: Tuple[ValidationIssue, ...]


@dataclass
class PldController:
    """
    PLD runtime controller template.

    Responsibilities (Level 5 — runtime implementation):
    - Route events through:
        * Level 1 structural validation (external)
        * Level 2 semantic validation and phase rules (external)
        * Level 3 runtime standard alignment rules (external)
      without redefining them.
    - Apply Level 5 configuration from ControllerConfig to:
        * decide how to treat MUST vs SHOULD violations by ValidationMode
        * optionally invoke normalization in NORMALIZE mode
        * toggle metrics staging behavior for downstream aggregation.
    - Stage inputs (events, phases, sequences, metadata) for derived metrics;
      calculation and stateful aggregation for metrics (including M-prefix
      derived metrics like M1_PRDR, M2_VRL) are owned by Level 3/4 metrics
      systems invoked via `metrics_engine`.

    IMPORTANT:
    - This controller does NOT embed Level 1/2/3 specifications. It is a
      runtime template that assumes those specifications are enforced by
      dedicated validators and metric engines.
    """

    # NOTE:
    # - DEFAULT_CONTROLLER_CONFIG is a shared instance and is intended to be
    #   treated as effectively immutable. For per-controller customization,
    #   prefer passing an explicit config instance to PldController(config=...)
    #   instead of mutating this default in place.
    config: ControllerConfig = DEFAULT_CONTROLLER_CONFIG

    # TODO: Wire in actual Level 1 schema validator (e.g., JSON Schema) via dependency injection.
    schema_validator: Optional[Any] = None

    # NOTE: The semantic validator dependency MUST expose a canonical diagnostic
    #       structure defined at Level 2/3. Its `validate(event)` method is
    #       expected to return an iterable of ValidationIssue instances (or an
    #       equivalent type that already encodes rule_id, field_path, and
    #       ValidationSeverity) so that this controller can aggregate diagnostics
    #       without redefining Level 2 semantics.
    semantic_validator: Optional[Any] = None

    # NOTE: The metrics_engine is responsible for applying Level 3/4 metric
    #       formulas and stateful aggregation. This controller ONLY stages
    #       inputs according to MetricsConfig and MUST NOT implement metric
    #       calculation logic itself.
    metrics_engine: Optional[Any] = None

    # TODO: Clarify whether derived metric calculation (M1_PRDR, M2_VRL, etc.)
    #       is expected to run inside this controller or in a Level 3/4 system.
    #       This directly impacts Level 5 runtime complexity and dependencies.

    def validate_event(self, event: Mapping[str, Any]) -> ValidationResult:
        """
        Validate a single PLD event under the active ControllerConfig.

        This method is responsible for:
        - Invoking structural validation (Level 1) if `schema_validator` is provided.
        - Invoking semantic validation (Level 2) if `semantic_validator` is provided.
        - Applying ControllerConfig.phase_enforcement and taxonomy rules at Level 5.
        - Interpreting issues according to ValidationMode (STRICT/WARN/NORMALIZE).

        NOTE:
        - Normalization is NOT performed here; see `normalize_event_if_allowed`.
        - This template intentionally leaves actual validator wiring as TODOs,
          to avoid redefining Level 1/2 logic at Level 5.
        """
        issues: List[ValidationIssue] = []

        # Basic schema_version check (Level 2/3 behavior; actual compatibility rules external).
        schema_version = event.get("schema_version")
        if schema_version is not None:
            if not self._is_schema_version_compatible(schema_version):
                issues.append(
                    ValidationIssue(
                        rule_id="VER-001",
                        message=f"Incompatible schema_version: {schema_version}",
                        severity=ValidationSeverity.MUST,
                        field_path="schema_version",
                    )
                )

        # Phase membership check against LIFECYCLE_PHASES.
        self._check_phase_membership(event, issues)

        # Optional Level 1 structural validation hook.
        if self.schema_validator is not None:
            self._run_schema_validator(event, issues)

        # Optional Level 2 semantic validation hook.
        if self.semantic_validator is not None:
            self._run_semantic_validator(event, issues)

        # Event type / phase enforcement based on EVENT_TYPE_PHASE_POLICY.
        self._check_event_type_phase_policy(event, issues)

        # Taxonomy / prefix constraints are delegated to a future extension
        # that consumes ControllerConfig.taxonomy; this template only reserves
        # the hook without implementing enforcement rules here.
        # TODO: Implement prefix/phase consistency checks using config.taxonomy
        #       once the enforcement wiring is defined.

        is_valid = self._interpret_validation_result(issues)
        has_should_violations = any(
            i.severity is ValidationSeverity.SHOULD for i in issues
        )
        return ValidationResult(
            is_valid=is_valid,
            has_should_violations=has_should_violations,
            issues=tuple(issues),
        )

    def normalize_event_if_allowed(self, event: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """
        Apply normalization in NORMALIZE mode when permitted by configuration.

        Behavior:
        - If validation_mode != NORMALIZE or allow_normalization_in_normalize_mode is False,
          this method MUST NOT mutate the event and MUST return it as-is.
        - If NORMALIZE mode is active and allowed, this method MAY delegate to an
          external normalization engine that implements the Level 2/3 rules.

        NOTE:
        - This method MUST NOT alter persisted logs; it is intended to operate
          on in-flight runtime events only.
        - Actual normalization algorithms are defined by Level 2/3 specifications
          (event matrix + semantic spec + runtime standard).
        - This template intentionally leaves the normalization implementation
          as a TODO for the embedding runtime.
        - TODO: Attach a canonical normalization specification identifier/version
          (e.g., "Normalization Spec vX.Y") once defined at Level 2/3.
        """
        if (
            self.config.validation_mode is not ValidationMode.NORMALIZE
            or not self.config.allow_normalization_in_normalize_mode
        ):
            return event

        # TODO: Delegate to external normalization engine with a canonical
        #       identifier/version for the normalization spec when available.
        #       Example (pseudo-code):
        #       normalized = self.normalization_engine.normalize(event)
        #       return normalized
        return event

    def stage_metrics_for_event(self, event: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Stage metric contributions for a single event based on MetricsConfig.

        Behavior:
        - If metrics are disabled in config.metrics.enabled, return None.
        - Otherwise, construct a minimal structure that downstream metrics
          engines can consume to compute canonical metrics as defined at Level 3.
        - This method MUST NOT define new metrics or alter Level 3 semantics.

        NOTE:
        - Phase-specific counting (e.g., failover vs generic fallback_executed)
          MUST follow Level 3 semantics when config.metrics.enforce_phase_specific_failover_counting
          is True. This template only reserves the hook; metric details are
          delegated to the metrics engine.
        """
        if not self.config.metrics.enabled:
            return None

        # TODO: Implement staging logic that:
        #       - Honors enabled_metric_names
        #       - Applies enforce_phase_specific_failover_counting
        #       - Leaves canonical metric formulas to the metrics engine.
        return None

    # -------------------------------------------------------------------------
    # Internal helper methods (Level 5 only; MUST NOT redefine Level 1/2 rules)
    # -------------------------------------------------------------------------

    def _is_schema_version_compatible(self, schema_version: str) -> bool:
        """
        Check compatibility of schema_version against ControllerConfig.

        This helper is intentionally conservative:
        - When reject_major_version_mismatch is True, non-"2.x" versions
          SHOULD be treated as incompatible for this template.
        - Detailed compatibility behavior for minor versions is governed
          by Level 2/3 specifications and is NOT redefined here.

        TODO:
        - Confirm whether the Level 3 Runtime Standard explicitly guarantees
          that all v2.x minor versions are compatible with this controller, or
          whether a stricter version-gating mechanism is required.
        """
        target = self.config.schema_version
        if not self.config.reject_major_version_mismatch:
            return True

        # Simple major version comparison (e.g., "2.0", "2.1", "2.5").
        try:
            major_current = schema_version.split(".", 1)[0]
            major_target = target.split(".", 1)[0]
        except Exception:
            return False

        if major_current != major_target:
            return False

        return True

    def _check_phase_membership(
        self,
        event: Mapping[str, Any],
        issues: List[ValidationIssue],
    ) -> None:
        phase = (event.get("pld") or {}).get("phase")
        if phase is None:
            issues.append(
                ValidationIssue(
                    rule_id="PHASE-001",
                    message="Missing pld.phase",
                    severity=ValidationSeverity.MUST,
                    field_path="pld.phase",
                )
            )
            return

        if phase not in LIFECYCLE_PHASES and self.config.phase_enforcement.enforce_known_phases:
            issues.append(
                ValidationIssue(
                    rule_id="PHASE-001",
                    message=f"Unknown phase '{phase}'",
                    severity=ValidationSeverity.MUST,
                    field_path="pld.phase",
                )
            )

    def _run_schema_validator(
        self,
        event: Mapping[str, Any],
        issues: List[ValidationIssue],
    ) -> None:
        """
        Invoke the Level 1 structural validator, if configured.

        NOTE:
        - This method assumes `schema_validator` exposes a `validate(event)`-style
          interface that raises or returns diagnostics. Exact API is left open.
        """
        try:
            # TODO: Adapt this call to the actual schema validator interface.
            if hasattr(self.schema_validator, "validate"):
                self.schema_validator.validate(event)  # type: ignore[call-arg]
        except Exception as exc:  # pragma: no cover - implementation-specific
            issues.append(
                ValidationIssue(
                    rule_id="SCHEMA-VALIDATION",
                    message=f"Schema validation error: {exc}",
                    severity=ValidationSeverity.MUST,
                    field_path="",
                )
            )

    def _run_semantic_validator(
        self,
        event: Mapping[str, Any],
        issues: List[ValidationIssue],
    ) -> None:
        """
        Invoke the Level 2 semantic validator / event matrix engine, if configured.

        NOTE:
        - The injected `semantic_validator` MUST implement a `validate(event)`
          method that returns an iterable of ValidationIssue instances whose
          rule_id, field_path, and severity already reflect Level 2/3 semantics.
        - This contract avoids ambiguous translation at Level 5 and ensures
          that severity (MUST/SHOULD/MAY) is defined by the Level 2/3 layer.
        """
        try:
            if hasattr(self.semantic_validator, "validate"):
                result = self.semantic_validator.validate(event)  # type: ignore[call-arg]
                if result is not None:
                    for diag in result:
                        # The contract requires ValidationIssue instances; no
                        # additional translation logic is performed here.
                        issues.append(diag)
        except Exception as exc:  # pragma: no cover - implementation-specific
            issues.append(
                ValidationIssue(
                    rule_id="SEMANTIC-VALIDATION",
                    message=f"Semantic validation error: {exc}",
                    severity=ValidationSeverity.MUST,
                    field_path="",
                )
            )

    def _check_event_type_phase_policy(
        self,
        event: Mapping[str, Any],
        issues: List[ValidationIssue],
    ) -> None:
        """
        Apply event_type → phase checks based on EVENT_TYPE_PHASE_POLICY when enabled.

        NOTE:
        - MUST/SHOULD/MAY semantics are governed by Level 2; this helper only
          checks consistency against the configured mapping and reports issues.
        - TODO: Future-stage refinement should align reported severity with the
          actual constraint level from Level 2 (MUST vs SHOULD vs MAY). The
          current template simplification of treating all mismatches as MUST-
          level is intentionally conservative but not semantically precise.
        """
        if not self.config.phase_enforcement.enforce_event_type_phase:
            return

        event_type = event.get("event_type")
        phase = (event.get("pld") or {}).get("phase")

        if event_type is None or phase is None:
            return

        expected_phase = EVENT_TYPE_PHASE_POLICY.get(event_type)
        if expected_phase is None:
            # Unknown or unmapped event_type; Level 2 may still accept it,
            # so we do not treat this as a MUST violation in the template.
            return

        if phase != expected_phase:
            issues.append(
                ValidationIssue(
                    rule_id="CAN-EVENT-TYPE-PHASE",
                    message=f"event_type '{event_type}' should use phase '{expected_phase}', got '{phase}'",
                    severity=ValidationSeverity.MUST,
                    field_path="pld.phase",
                )
            )

    def _interpret_validation_result(
        self,
        issues: Iterable[ValidationIssue],
    ) -> bool:
        """
        Interpret the aggregated issues according to the active ValidationMode.

        STRICT:
            - MUST violations → invalid
            - SHOULD violations → ignored for validity
        WARN:
            - MUST violations → invalid
            - SHOULD violations → valid but SHOULD be reported/warned by callers
              using `has_should_violations` on ValidationResult.
        NORMALIZE:
            - MUST violations → invalid after any attempted normalization. The
              external normalization engine is responsible for resolving
              resolvable MUST violations before (re)validation; any remaining
              MUST-level issues are treated as unresolvable and cause the event
              to be considered invalid at this Level 5 controller layer.
        """
        mode = self.config.validation_mode
        must_violations = any(i.severity is ValidationSeverity.MUST for i in issues)

        if mode is ValidationMode.STRICT:
            return not must_violations

        if mode is ValidationMode.WARN:
            return not must_violations

        if mode is ValidationMode.NORMALIZE:
            # In NORMALIZE mode, any remaining MUST violations after normalization
            # attempts are treated as unresolvable at this layer and invalidate
            # the event.
            return not must_violations

        return False


if __name__ == "__main__":
    # Simple smoke tests to exercise core validation paths when this file is run
    # directly. These are not a replacement for full unit tests but help ensure
    # the controller and fallback config are wired correctly.

    controller = PldController()

    # 1) Happy-path event: matching schema_version and phase
    ok_event = {
        "schema_version": "2.0",
        "event_type": "drift_detected",
        "pld": {"phase": "drift"},
    }
    ok_result = controller.validate_event(ok_event)
    print("[SMOKE] ok_event is_valid=", ok_result.is_valid)

    # 2) Bad schema_version and mismatched phase should yield invalid result
    bad_event = {
        "schema_version": "1.0",
        "event_type": "drift_detected",
        "pld": {"phase": "outcome"},
    }
    bad_result = controller.validate_event(bad_event)
    print("[SMOKE] bad_event is_valid (expected False)=", bad_result.is_valid)

    # 3) event_type-phase mismatch should be invalid
    mismatch_event = {
        "schema_version": "2.0",
        "event_type": "evaluation_pass",
        "pld": {"phase": "drift"},
    }
    mismatch_result = controller.validate_event(mismatch_event)
    print(
        "[SMOKE] mismatch_event is_valid (expected False)=",
        mismatch_result.is_valid,
    )
