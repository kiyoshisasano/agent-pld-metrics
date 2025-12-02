# component_id: schema_validator
# kind: runtime_module
# area: enforcement
# status: draft
# authority_level: 5
# version: 2.0.0
# license: Apache-2.0
# purpose: Validate PLD runtime events against Level 1 schema and Level 2 event matrix.

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
# NOTE:
#   - This module is intentionally STATELESS: all functions operate on the
#     given event + schema/matrix inputs and do not retain cross-call state.
#   - Level 1 / Level 2 specifications are treated as read-only; this module
#     MUST NOT modify schema or matrix content at runtime.
#   - NORMALIZE mode MAY propose a corrected event as "normalized_event", but
#     MUST NOT modify the input event or any stored logs. Adoption of the
#     normalized form is strictly an upper-layer policy decision.
#
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
    Structured result for PLD event validation.

    Notes:
      - `schema_valid` / `matrix_valid` reflect the raw outcomes of Level 1 / 2 checks.
      - `fatal_error` is non-None when dependencies (schema/matrix) could not be
        loaded or when validation infrastructure failed. In that case, the event
        itself is left untouched and callers SHOULD treat the result as
        "validation infrastructure unavailable".
      - `normalized_event` is ONLY populated in NORMALIZE mode when a strictly
        correctable deviation is detected (e.g., phase mismatch resolvable via
        must_phase_map). It is a candidate representation and MUST NOT be
        applied to stored logs at this layer.
    """

    schema_valid: bool
    matrix_valid: bool
    schema: Optional[SchemaValidationResult] = None
    matrix: Optional[MatrixValidationResult] = None
    normalized_event: Optional[Dict[str, Any]] = None
    fatal_error: Optional[str] = None


# ──────────────────────────────────────────────────────────────────────────────
# Dependency Handling & Loading
# ──────────────────────────────────────────────────────────────────────────────

"""
Default hardcoded paths are intentionally avoided.

The runtime (or configuration layer) MUST provide schema/matrix locations or
pre-loaded objects. This prevents undeclared environmental dependencies and
keeps this module stateless.
"""


def load_level1_schema(path) -> Dict[str, Any]:
    """
    Load Level 1 PLD schema from the given path.

    Raises:
        RuntimeError: if jsonschema is unavailable or the file cannot be read.
    """
    if jsonschema is None:
        raise RuntimeError(
            "jsonschema is required for Level 1 validation but is missing."
        )

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:  # pragma: no cover - defensive
        raise RuntimeError(f"Failed to load Level 1 schema from {path}: {exc}") from exc


def load_event_matrix(path) -> Dict[str, Any]:
    """
    Load Level 2 event matrix from the given path.

    Raises:
        RuntimeError: if PyYAML is unavailable or the file cannot be read.
    """
    if yaml is None:
        raise RuntimeError(
            "PyYAML is required for Level 2 validation but is missing."
        )

    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as exc:  # pragma: no cover - defensive
        raise RuntimeError(f"Failed to load event matrix from {path}: {exc}") from exc


def _format_fatal_error(prefix: str, exc: Exception) -> str:
    """
    Format fatal errors in a stable, machine- and human-readable way.

    This keeps error reporting consistent across dependency failures while
    avoiding exceptions escaping into calling code.
    """
    return f"{prefix}: {exc}"


# ──────────────────────────────────────────────────────────────────────────────
# Level 1 Validation
# ──────────────────────────────────────────────────────────────────────────────


def validate_level1_schema(event: PLDEvent, schema: Dict[str, Any]) -> SchemaValidationResult:
    """
    Validate a PLD event against the Level 1 JSON schema.

    This function treats `event` and `schema` as read-only; it MUST NOT mutate
    either argument.
    """
    validator = jsonschema.Draft7Validator(schema)  # type: ignore[attr-defined]
    errors: List[str] = []

    for error in validator.iter_errors(event):
        path = ".".join(str(p) for p in error.path)
        errors.append(f"{path}: {error.message}")

    return SchemaValidationResult(is_valid=not errors, errors=errors)


# ──────────────────────────────────────────────────────────────────────────────
# Level 2 Validation
# ──────────────────────────────────────────────────────────────────────────────


def validate_level2_matrix(
    event: PLDEvent,
    matrix: Dict[str, Any],
    mode: ValidationMode,
) -> MatrixValidationResult:
    """
    Validate a PLD event against the Level 2 event matrix.

    This enforces:
      - prefix_to_phase: lifecycle code prefix MUST align with pld.phase.
      - must_phase_map: event_type MUST map to a single required phase.
      - should_phase_map: event_type SHOULD map to a recommended phase
        (warnings emitted when WARN/NORMALIZE mode is used).

    The input `event` and `matrix` are treated as read-only.
    """
    errors: List[str] = []
    warnings: List[str] = []

    event_type = event.get("event_type")
    pld = event.get("pld") or {}
    phase = pld.get("phase")
    code = pld.get("code")

    # Defensive guards; Level 1 SHOULD guarantee these, but modes or future
    # adaptive runtimes might bypass L1. We keep checks explicit here.
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
    """
    Extract lifecycle prefix (e.g., D, C, R) from a PLD code such as 'D3_repeated_plan'.

    Numeric suffixes are stripped so that taxonomy expansions (D1..D99) remain
    compatible with a single prefix mapping.
    """
    if not code:
        return None

    head = code.split("_", 1)[0]
    while head and head[-1].isdigit():
        head = head[:-1]
    return head or None


# ──────────────────────────────────────────────────────────────────────────────
# Combined Validation (public API)
# ──────────────────────────────────────────────────────────────────────────────


def validate_pld_event(
    event: PLDEvent,
    mode: ValidationMode,
    schema_path: Optional[str],
    matrix_path: Optional[str],
) -> PLDValidationResult:
    """
    Validate a PLD event against Level 1 schema and Level 2 event matrix.

    This is the primary entry point and remains API-stable.

    Behavior:
      - Attempts to load schema/matrix from the given paths.
      - On dependency or I/O failure, returns a PLDValidationResult with
        `fatal_error` populated and no normalized_event, without raising.
      - Otherwise delegates to a stateless helper that operates on the
        already-loaded schema/matrix objects.
    """
    try:
        schema = load_level1_schema(schema_path)
        matrix = load_event_matrix(matrix_path)
    except RuntimeError as fatal:
        return PLDValidationResult(
            schema_valid=False,
            matrix_valid=False,
            schema=None,
            matrix=None,
            normalized_event=None,
            fatal_error=_format_fatal_error("VALIDATOR_DEPENDENCY_ERROR", fatal),
        )

    return validate_pld_event_with_resources(event, mode, schema, matrix)


def validate_pld_event_with_resources(
    event: PLDEvent,
    mode: ValidationMode,
    schema: Dict[str, Any],
    matrix: Dict[str, Any],
) -> PLDValidationResult:
    """
    Variant of validate_pld_event that operates on pre-loaded schema/matrix.

    This helper keeps the core validation logic stateless while allowing callers
    to manage schema/matrix loading and caching outside this module.
    """
    schema_result = validate_level1_schema(event, schema)
    matrix_result = validate_level2_matrix(event, matrix, mode)

    if mode is ValidationMode.NORMALIZE:
        normalized_event = _normalize_event_if_possible(
            event=event,
            schema_result=schema_result,
            matrix_result=matrix_result,
            matrix=matrix,
        )
    else:
        normalized_event = None

    return PLDValidationResult(
        schema_valid=schema_result.is_valid,
        matrix_valid=matrix_result.is_valid,
        schema=schema_result,
        matrix=matrix_result,
        normalized_event=normalized_event,
        fatal_error=None,
    )


def _normalize_event_if_possible(
    event: PLDEvent,
    schema_result: SchemaValidationResult,
    matrix_result: MatrixValidationResult,
    matrix: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """
    Attempt to construct a normalized copy of the event in NORMALIZE mode.

    Design constraints:
      - NEVER mutate the original event.
      - ONLY handle the specific case where:
          * Level 1 schema validation has succeeded; AND
          * Level 2 validation reports errors; AND
          * there exists a MUST phase mapping for this event_type; AND
          * updating pld.phase to that MUST phase yields a matrix-valid event.
      - If any of the above is not satisfied, returns None.

    IMPORTANT:
      - The returned dict is a candidate event only. Adoption into canonical
        logs is the responsibility of higher layers and MUST follow VAL-004–005
        policies. This module does not write logs or persist events.
    """
    # If the schema is invalid, we cannot safely propose a normalized variant.
    if not schema_result.is_valid:
        return None

    # If matrix is already valid, nothing to normalize.
    if matrix_result.is_valid:
        return None

    must_phase_map = matrix.get("must_phase_map", {})
    event_type = event.get("event_type")
    raw_pld = event.get("pld") or {}
    current_phase = raw_pld.get("phase")

    if not isinstance(must_phase_map, dict):
        return None

    if event_type not in must_phase_map:
        return None

    required_phase = must_phase_map[event_type]

    # If phase already matches required phase, we cannot "normalize" anything.
    if current_phase == required_phase:
        return None

    # Build a tentative normalized copy with phase corrected.
    normalized: Dict[str, Any] = dict(event)
    new_pld: Dict[str, Any] = dict(raw_pld)
    new_pld["phase"] = required_phase
    normalized["pld"] = new_pld

    # Re-run Level 2 validation in STRICT mode against the normalized copy.
    candidate_matrix_result = validate_level2_matrix(
        normalized,
        matrix,
        ValidationMode.STRICT,
    )

    # Only accept the normalized candidate if the matrix is fully valid now.
    if not candidate_matrix_result.is_valid:
        return None

    return normalized


# ──────────────────────────────────────────────────────────────────────────────
# Summary helper
# ──────────────────────────────────────────────────────────────────────────────


def summarize_validation(result: PLDValidationResult) -> Dict[str, Any]:
    """
    Produce a compact, transport-friendly summary of a PLDValidationResult.

    This helper does not mutate `result` and is suitable for logging or metrics
    layers that only need high-level outcomes.
    """
    return {
        "schema_valid": result.schema_valid,
        "matrix_valid": result.matrix_valid,
        "fatal_error": result.fatal_error,
        "schema_errors": getattr(result.schema, "errors", None),
        "matrix_errors": getattr(result.matrix, "errors", None),
        "matrix_warnings": getattr(result.matrix, "warnings", None),
        "has_normalized_event": result.normalized_event is not None,
    }

