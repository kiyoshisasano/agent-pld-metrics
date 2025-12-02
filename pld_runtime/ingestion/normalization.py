# component_id: normalization
# kind: runtime_module
# area: ingestion
# status: draft
# authority_level: 5
# version: 2.0.0
# license: Apache-2.0
# purpose: Ingestion-time normalization and validation shim enforcing Level 1 structure and Level 2 semantics.

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Callable, Mapping
import copy


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

class ValidationMode(str, Enum):
    STRICT = "strict"
    WARN = "warn"
    NORMALIZE = "normalize"


class ViolationLevel(str, Enum):
    MUST = "MUST"
    SHOULD = "SHOULD"


@dataclass
class Violation:
    level: ViolationLevel
    code: str
    message: str
    field_path: str
    normalized: bool = False


@dataclass
class NormalizationResult:
    event: Dict[str, Any]
    violations: List[Violation]
    mode: ValidationMode
    is_schema_valid: bool = field(default=False)

    @property
    def is_matrix_valid(self) -> bool:
        return not any(v.level == ViolationLevel.MUST and not v.normalized for v in self.violations)

    @property
    def is_pld_valid(self) -> bool:
        return self.is_schema_valid and self.is_matrix_valid


SchemaValidator = Callable[[Dict[str, Any]], Tuple[bool, List[str]]]


def normalize_event(
    event: Dict[str, Any],
    *,
    mode: ValidationMode = ValidationMode.STRICT,
    schema_validator: Optional[SchemaValidator] = None,
    context: Optional[Dict[str, Any]] = None,
) -> NormalizationResult:
    ctx = context or {}
    working = copy.deepcopy(event)
    violations: List[Violation] = []

    result = NormalizationResult(event=working, violations=violations, mode=mode)

    # Level 1 schema validation
    if schema_validator:
        schema_ok, schema_messages = schema_validator(working)
        result.is_schema_valid = schema_ok
        if not schema_ok:
            for msg in schema_messages:
                violations.append(
                    Violation(
                        level=ViolationLevel.MUST,
                        code="SCHEMA_INVALID",
                        message=msg,
                        field_path="",
                        normalized=False,
                    )
                )

            # TODO: Should SchemaValidator provide field-level error metadata?
            # (Open Question #1)
            return result
    else:
        result.is_schema_valid = True

    _enforce_schema_version(working, mode, violations)
    _normalize_and_validate_semantics(working, mode, violations, ctx)
    _validate_runtime_operational_rules(working, mode, violations)

    return result


# ──────────────────────────────────────────────────────────────────────────────
# Level 2 semantic rules
# ──────────────────────────────────────────────────────────────────────────────

_VALID_PHASES = (
    "drift", "repair", "reentry", "continue", "outcome", "failover", "none"
)

_PREFIX_TO_PHASE: Mapping[str, str] = {
    "D": "drift",
    "R": "repair",
    "RE": "reentry",
    "C": "continue",
    "O": "outcome",
    "F": "failover",
}

_MUST_PHASE_MAP: Mapping[str, str] = {
    "drift_detected": "drift",
    "drift_escalated": "drift",
    "repair_triggered": "repair",
    "repair_escalated": "repair",
    "reentry_observed": "reentry",
    "continue_allowed": "continue",
    "continue_blocked": "continue",
    "failover_triggered": "failover",
}

_SHOULD_PHASE_MAP: Mapping[str, str] = {
    "evaluation_pass": "outcome",
    "evaluation_fail": "outcome",
    "session_closed": "outcome",
    "info": "none",
}

_MAY_EVENTS = ("latency_spike", "pause_detected", "fallback_executed", "handoff")


def _enforce_schema_version(event, mode, violations):
    if event.get("schema_version") != "2.0":
        violations.append(
            Violation(
                level=ViolationLevel.MUST,
                code="SCHEMA_VERSION_MISMATCH",
                message="schema_version must equal '2.0'.",
                field_path="schema_version",
            )
        )


def _normalize_and_validate_semantics(event, mode, violations, context):
    pld = event.get("pld") or {}
    phase = pld.get("phase")
    code = pld.get("code")
    event_type = event.get("event_type")

    if phase not in _VALID_PHASES:
        violations.append(
            Violation(
                level=ViolationLevel.MUST,
                code="INVALID_PHASE",
                message=f"Invalid pld.phase '{phase}'.",
                field_path="pld.phase",
            )
        )
        # TODO: Should invalid phase be eligible for deterministic correction?
        # (Open Question #2)
        return

    required_from_type = _MUST_PHASE_MAP.get(event_type)
    required_from_prefix: Optional[str] = None
    prefix: Optional[str] = None

    if isinstance(code, str):
        prefix = _extract_prefix(code)
        required_from_prefix = _PREFIX_TO_PHASE.get(prefix)

    # Conflict check
    if required_from_type and required_from_prefix and required_from_type != required_from_prefix:
        winning_phase = required_from_type
        if mode == ValidationMode.NORMALIZE:
            pld["phase"] = winning_phase
            violations.append(
                Violation(
                    level=ViolationLevel.MUST,
                    code="PHASE_CONFLICT_RESOLVED",
                    message=f"phase updated based on event_type rule (required='{winning_phase}').",
                    field_path="pld.phase",
                    normalized=True,
                )
            )
        else:
            # Message-only refinement: provide actionable required/found values
            violations.append(
                Violation(
                    level=ViolationLevel.MUST,
                    code="CONFLICT_EVENTTYPE_PREFIX",
                    message=(
                        "phase requirements conflict between event_type and prefix "
                        f"rules; required='{winning_phase}', found='{phase}'."
                    ),
                    field_path="pld.phase",
                )
            )
        return

    # Unified required phase (non-conflict)
    final_required = required_from_type or required_from_prefix
    source = "event_type" if required_from_type else "prefix" if required_from_prefix else None

    if final_required and phase != final_required:
        if mode == ValidationMode.NORMALIZE:
            pld["phase"] = final_required
            violations.append(
                Violation(
                    level=ViolationLevel.MUST,
                    code="PHASE_NORMALIZED",
                    message=f"phase updated based on required mapping ('{final_required}').",
                    field_path="pld.phase",
                    normalized=True,
                )
            )
        else:
            violations.append(
                Violation(
                    level=ViolationLevel.MUST,
                    code="PHASE_MISMATCH_REQUIRED",
                    message=f"phase '{phase}' does not match required value '{final_required}'.",
                    field_path="pld.phase",
                )
            )

    _enforce_event_type_phase(pld, event_type, mode, violations)

    if isinstance(code, str):
        _enforce_prefix_phase(pld, mode, violations)

    # TODO: SHOULD vs MAY precedence for phase inference is not yet formally
    #       specified in Level 2. Current behavior may emit both
    #       SHOULD_PHASE_MISMATCH and PHASE_INFERENCE_DIFFERENCE for the same
    #       event. Any suppression/prioritization logic must be coordinated
    #       with semantic spec evolution before changing this behavior.
    #       (Issue #2 — design-level, no behavior change here)

    if mode == ValidationMode.NORMALIZE and event_type in _MAY_EVENTS:
        inferred = _infer_phase_for_may_event(event_type, context, pld.get("phase"))
        if inferred != pld.get("phase"):
            violations.append(
                Violation(
                    level=ViolationLevel.SHOULD,
                    code="PHASE_INFERENCE_DIFFERENCE",
                    message=f"phase differs from inferred value ('{inferred}').",
                    field_path="pld.phase",
                )
            )


def _enforce_event_type_phase(pld, event_type, mode, violations):
    if event_type in _SHOULD_PHASE_MAP:
        recommended = _SHOULD_PHASE_MAP[event_type]
        if pld.get("phase") != recommended:
            violations.append(
                Violation(
                    level=ViolationLevel.SHOULD,
                    code="SHOULD_PHASE_MISMATCH",
                    message=f"phase SHOULD be '{recommended}' for this event_type.",
                    field_path="pld.phase",
                )
            )


def _extract_prefix(code: str) -> str:
    head = code.split("_", 1)[0] if "_" in code else code
    while head and head[-1].isdigit():
        head = head[:-1]
    return head


def _enforce_prefix_phase(pld, mode, violations):
    code = pld.get("code")
    phase = pld.get("phase")
    prefix = _extract_prefix(code)

    if phase == "none" and prefix in _PREFIX_TO_PHASE:
        violations.append(
            Violation(
                level=ViolationLevel.MUST,
                code="NONE_PHASE_LIFECYCLE_PREFIX",
                message="lifecycle prefix not permitted when phase='none'.",
                field_path="pld.code",
            )
        )
        # TODO: Are additional non-lifecycle constraints required?
        # (Open Question #5)
        return


def _infer_phase_for_may_event(event_type, context, current_phase):
    ctx_phase = context.get("current_phase")

    # TODO: Clarify authoritative source for context['current_phase'].
    # (Open Question #3)

    if event_type == "fallback_executed":
        return ctx_phase if ctx_phase in ("repair", "failover") else "failover"

    if event_type in ("latency_spike", "pause_detected", "handoff"):
        return ctx_phase or "none"

    return current_phase


# ──────────────────────────────────────────────────────────────────────────────
# Level 3 operational validation
# ──────────────────────────────────────────────────────────────────────────────

def _validate_runtime_operational_rules(event, mode, violations):
    pld = event.get("pld") or {}
    code = pld.get("code")
    event_type = event.get("event_type")
    phase = pld.get("phase")

    if event_type == "session_closed" and phase not in ("outcome", "none"):
        violations.append(
            Violation(
                level=ViolationLevel.SHOULD,
                code="SESSION_CLOSED_PHASE_SHOULD",
                message="session_closed SHOULD use outcome or none.",
                field_path="pld.phase",
            )
        )

    if isinstance(code, str) and code.startswith("M"):
        if event_type != "info" or phase != "none":
            violations.append(
                Violation(
                    level=ViolationLevel.MUST,
                    code="M_PREFIX_MAPPING",
                    message="M-prefix events require event_type='info' and phase='none'.",
                    field_path="pld.code",
                )
            )


# ──────────────────────────────────────────────────────────────────────────────
# Optional jsonschema adapter
# ──────────────────────────────────────────────────────────────────────────────

def make_jsonschema_validator(schema):
    try:
        import jsonschema
    except ImportError:
        raise RuntimeError("jsonschema required.")

    def _validate(event):
        try:
            jsonschema.validate(event, schema)
            return True, []
        except jsonschema.ValidationError as e:
            return False, [str(e)]

    return _validate





