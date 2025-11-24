# version: "2.0.0"
# status: "draft / runtime_template / runtime_extension"
# authority_level_scope: "Level 5 — runtime implementation"
# purpose: "Validate PLD runtime events against Level 1 schema and Level 2 event matrix, with optional normalization."
# scope: "Runtime-local validator; MUST NOT modify canonical schemas and MUST treat Level 1/2 as read-only."
# change_classification: "runtime-only update (addresses dependency & contract alignment)"
# dependencies: "docs/schemas/pld_event.schema.json, docs/event_matrix.yaml, PLD_Event_Semantic_Spec_v2.0.md"

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Mapping, Optional

try:
    import jsonschema  # type: ignore
except ImportError:
    jsonschema = None

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None


# ──────────────────────────────────────────────────────────────────────────────
# TODO (Open Question #1): Confirm long-term boundary: validator remains stateless,
#                         sequencing/state-based validation handled externally.
# TODO (Open Question #2): Clarify whether NORMALIZE mode events MAY become canonical log entries (VAL-005 ambiguity).
# TODO (Open Question #3): Confirm future-proofing for prefix logic (digit stripping) if taxonomy evolves.
# ──────────────────────────────────────────────────────────────────────────────

PLDEvent = Mapping[str, Any]


class ValidationMode(str, Enum):
    STRICT = "strict"
    WARN = "warn"
    NORMALIZE = "normalize"


@dataclass(frozen=True)
class SchemaValidationResult:
    is_valid: bool
    errors: List[str]


@dataclass(frozen=True)
class MatrixValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]


@dataclass(frozen=True)
class PLDValidationResult:
    """
    Core Issue #1 fix:
    Added `fatal_error` to ensure dependency or I/O failures return a structured result
    rather than raising uncontrolled runtime exceptions.
    """

    schema_valid: bool
    matrix_valid: bool
    schema: Optional[SchemaValidationResult] = None
    matrix: Optional[MatrixValidationResult] = None
    normalized_event: Optional[Dict[str, Any]] = None
    fatal_error: Optional[str] = None


# ──────────────────────────────────────────────────────────────────────────────
# Dependency Handling & Loading (updated per Core Issue #2)
# ──────────────────────────────────────────────────────────────────────────────

"""
Core Issue #2 Resolution:

Default hardcoded paths are removed because they imply assumptions about working
directory structure. The runtime MUST explicitly provide paths OR use an external
resource loader.

This prevents undeclared environmental dependencies.
"""


def load_level1_schema(path) -> Dict[str, Any]:
    if jsonschema is None:
        raise RuntimeError("jsonschema is required for Level 1 validation but is missing.")

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        raise RuntimeError(f"Failed to load Level 1 schema from {path}: {exc}") from exc


def load_event_matrix(path) -> Dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required for Level 2 validation but is missing.")

    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as exc:
        raise RuntimeError(f"Failed to load event matrix from {path}: {exc}") from exc


# ──────────────────────────────────────────────────────────────────────────────
# Level 1 Validation
# ──────────────────────────────────────────────────────────────────────────────

def validate_level1_schema(event: PLDEvent, schema: Dict[str, Any]) -> SchemaValidationResult:
    validator = jsonschema.Draft7Validator(schema)
    errors = []

    for error in validator.iter_errors(event):
        path = ".".join(str(p) for p in error.path)
        errors.append(f"{path}: {error.message}")

    return SchemaValidationResult(is_valid=not errors, errors=errors)


# ──────────────────────────────────────────────────────────────────────────────
# Level 2 Validation
# ──────────────────────────────────────────────────────────────────────────────

def validate_level2_matrix(event: PLDEvent, matrix: Dict[str, Any], mode: ValidationMode) -> MatrixValidationResult:
    errors: List[str] = []
    warnings: List[str] = []

    event_type = event.get("event_type")
    pld = event.get("pld") or {}
    phase = pld.get("phase")
    code = pld.get("code")

    # Core Issue #3 Resolution: KEEP guardrails but document justification.
    #
    # Reason: Although Level 1 SHOULD guarantee these fields exist, validation mode
    # may allow Level 1 to be bypassed in future adaptive runtimes. Therefore the
    # checks remain defensive, but are now explicitly documented.
    if event_type is None:
        errors.append("event_type missing for Level 2 validation (defensive check).")
        return MatrixValidationResult(False, errors, warnings)

    if phase is None:
        errors.append("pld.phase missing for Level 2 validation (defensive check).")
        return MatrixValidationResult(False, errors, warnings)

    prefix_to_phase = matrix.get("prefix_to_phase", {})
    lifecycle_prefix = _extract_lifecycle_prefix(code) if isinstance(code, str) else None

    if lifecycle_prefix in prefix_to_phase:
        expected = prefix_to_phase[lifecycle_prefix]
        if expected != phase:
            errors.append(
                f"Prefix mismatch: {lifecycle_prefix!r} → expected phase {expected!r}, got {phase!r}"
            )

    must_phase_map = matrix.get("must_phase_map", {})
    if event_type in must_phase_map and phase != must_phase_map[event_type]:
        errors.append(
            f"MUST rule violated: event_type={event_type} requires phase={must_phase_map[event_type]}, got {phase}"
        )

    should_phase_map = matrix.get("should_phase_map", {})
    if event_type in should_phase_map and phase != should_phase_map[event_type]:
        msg = (
            f"SHOULD rule deviation: event_type={event_type} recommends phase={should_phase_map[event_type]}, got {phase}"
        )
        if mode in (ValidationMode.WARN, ValidationMode.NORMALIZE):
            warnings.append(msg)

    return MatrixValidationResult(is_valid=not errors, errors=errors, warnings=warnings)


def _extract_lifecycle_prefix(code: Optional[str]) -> Optional[str]:
    if not code:
        return None

    head = code.split("_", 1)[0]
    while head and head[-1].isdigit():
        head = head[:-1]
    return head or None


# ──────────────────────────────────────────────────────────────────────────────
# Combined Validation with Fatal Error Wrapping
# ──────────────────────────────────────────────────────────────────────────────

def validate_pld_event(
    event: PLDEvent,
    mode: ValidationMode,
    schema_path: Optional[str],
    matrix_path: Optional[str],
) -> PLDValidationResult:
    """
    Core Issue #1 implementation:
    This function now guarantees that dependency or I/O failures return a structured
    PLDValidationResult rather than interrupting control flow.
    """

    try:
        schema = load_level1_schema(schema_path)
        matrix = load_event_matrix(matrix_path)
    except RuntimeError as fatal:
        return PLDValidationResult(
            schema_valid=False,
            matrix_valid=False,
            fatal_error=str(fatal)
        )

    schema_result = validate_level1_schema(event, schema)
    matrix_result = validate_level2_matrix(event, matrix, mode)

    normalized_event = (
        _normalize_event_if_possible(event, matrix, matrix_result)
        if mode is ValidationMode.NORMALIZE
        else None
    )

    return PLDValidationResult(
        schema_valid=schema_result.is_valid,
        matrix_valid=matrix_result.is_valid,
        schema=schema_result,
        matrix=matrix_result,
        normalized_event=normalized_event,
        fatal_error=None
    )


def _normalize_event_if_possible(event: PLDEvent, matrix: Dict[str, Any], matrix_result: MatrixValidationResult):
    if matrix_result.is_valid:
        return None

    must_phase = matrix.get("must_phase_map", {})
    event_type = event.get("event_type")
    pld = dict(event.get("pld") or {})

    if event_type in must_phase and pld.get("phase") != must_phase[event_type]:
        normalized = dict(event)
        pld = dict(pld)
        pld["phase"] = must_phase[event_type]
        normalized["pld"] = pld
        return normalized

    return None


# ──────────────────────────────────────────────────────────────────────────────

def summarize_validation(result: PLDValidationResult) -> Dict[str, Any]:
    return {
        "schema_valid": result.schema_valid,
        "matrix_valid": result.matrix_valid,
        "fatal_error": result.fatal_error,
        "schema_errors": getattr(result.schema, "errors", None),
        "matrix_errors": getattr(result.matrix, "errors", None),
        "matrix_warnings": getattr(result.matrix, "warnings", None),
        "has_normalized_event": result.normalized_event is not None,
    }

