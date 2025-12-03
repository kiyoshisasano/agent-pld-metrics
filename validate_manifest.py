# component_id: validate_manifest
# kind: tooling
# area: meta
# status: stable
# authority_level: 3
# version: 0.1.0
# license: Apache-2.0
# purpose: Validate manifest coverage and metadata consistency across the repository.

#!/usr/bin/env python
"""
validate_manifest.py

Validate a PLD manifest.yaml against METADATA_MANIFEST_SPEC v0.9.0.

Levels:
  L0 - Permissive: basic structure only
  L1 - Structured: required fields + controlled vocabulary
  L2 - Enforceable: L1 + file existence + basic code-header alignment (for .py)
"""

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml  # Requires PyYAML
except ImportError:
    print("ERROR: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

SPEC_VERSION = "0.9.0"

KIND_ENUM = {
    "code",
    "schema",
    "config",
    "runtime_module",
    "metric",
    "example",
    "doc",
    "legal",
}

STATUS_ENUM = {
    "experimental",
    "draft",
    "candidate",
    "stable",
}


class ValidationError(Exception):
    pass


def load_manifest(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise ValidationError(f"Manifest file not found: {path}")
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValidationError(f"YAML parse error in {path}: {e}") from e

    if not isinstance(data, dict):
        raise ValidationError(f"Manifest root must be a mapping (dict), got {type(data).__name__}")
    return data


def validate_l0(manifest: Dict[str, Any], errors: List[str]) -> None:
    # version
    if "version" not in manifest:
        errors.append("L0: Missing top-level field: 'version'")
    # components
    if "components" not in manifest:
        errors.append("L0: Missing top-level field: 'components'")
    elif not isinstance(manifest["components"], list):
        errors.append("L0: 'components' must be a list")

    # L0 does not enforce exact version, but we can warn if it mismatches
    version = manifest.get("version")
    if version is not None and str(version) != SPEC_VERSION:
        errors.append(
            f"L0: version is '{version}', spec version is '{SPEC_VERSION}' "
            "(not fatal, but consider aligning)"
        )


def validate_l1(manifest: Dict[str, Any], errors: List[str]) -> None:
    """
    L1: assumes L0 already ran. Enforces:
      - default_license exists
      - components entries have required fields
      - kind / status use controlled vocabulary
      - authority_level is int 1–5
    """
    if "default_license" not in manifest:
        errors.append("L1: Missing top-level field: 'default_license'")
    else:
        if not isinstance(manifest["default_license"], str):
            errors.append("L1: 'default_license' must be a string (SPDX identifier)")

    components = manifest.get("components") or []
    if not isinstance(components, list):
        # L0 already complained, but keep safety.
        return

    required_fields = [
        "path",
        "component_id",
        "kind",
        "area",
        "status",
        "authority_level",
        "purpose",
    ]

    for idx, comp in enumerate(components):
        prefix = f"L1: components[{idx}]"

        if not isinstance(comp, dict):
            errors.append(f"{prefix} must be a mapping (dict), got {type(comp).__name__}")
            continue

        for field in required_fields:
            if field not in comp:
                errors.append(f"{prefix}: Missing required field '{field}'")

        # Skip deeper checks if required fields missing
        if any(field not in comp for field in required_fields):
            continue

        # path
        if not isinstance(comp["path"], str):
            errors.append(f"{prefix}: 'path' must be a string")
        # component_id
        cid = comp["component_id"]
        if not isinstance(cid, str):
            errors.append(f"{prefix}: 'component_id' must be a string")
        else:
            # simple snake_case heuristic
            if not cid.replace("_", "").isalnum() or any(ch.upper() == ch for ch in cid if ch.isalpha()):
                errors.append(
                    f"{prefix}: 'component_id' should be snake_case (got '{cid}')"
                )

        # kind
        kind = comp["kind"]
        if not isinstance(kind, str):
            errors.append(f"{prefix}: 'kind' must be a string")
        elif kind not in KIND_ENUM:
            errors.append(
                f"{prefix}: 'kind' must be one of {sorted(KIND_ENUM)}, got '{kind}'"
            )

        # area
        if not isinstance(comp["area"], str):
            errors.append(f"{prefix}: 'area' must be a string")

        # status
        status = comp["status"]
        if not isinstance(status, str):
            errors.append(f"{prefix}: 'status' must be a string")
        elif status not in STATUS_ENUM:
            errors.append(
                f"{prefix}: 'status' must be one of {sorted(STATUS_ENUM)}, got '{status}'"
            )

        # authority_level
        level = comp["authority_level"]
        if not isinstance(level, int):
            errors.append(f"{prefix}: 'authority_level' must be an integer")
        else:
            if not (1 <= level <= 5):
                errors.append(
                    f"{prefix}: 'authority_level' must be between 1 and 5 (inclusive), got {level}"
                )

        # purpose
        if not isinstance(comp["purpose"], str):
            errors.append(f"{prefix}: 'purpose' must be a string")


def _read_code_header(py_path: Path, max_lines: int = 50) -> List[str]:
    try:
        with py_path.open("r", encoding="utf-8") as f:
            lines = [next(f) for _ in range(max_lines)]
    except (StopIteration, FileNotFoundError, OSError):
        # fewer lines or missing
        try:
            with py_path.open("r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception:
            return []
    return lines


def _extract_header_field(lines: List[str], field_name: str) -> str:
    """
    Look for lines like:

        # component_id: repair_detector

    or

        # component_id:   repair_detector   # comment

    Returns the stripped value or "" if not found.
    """
    import re

    pattern = re.compile(rf"^\s*#\s*{field_name}\s*:\s*(.+)$")
    for line in lines:
        m = pattern.match(line)
        if not m:
            continue
        value = m.group(1).strip()
        # Drop trailing inline comment if present
        if "  #" in value:
            value = value.split("  #", 1)[0].rstrip()
        elif " #" in value:
            value = value.split(" #", 1)[0].rstrip()
        return value
    return ""


def validate_l2(manifest: Dict[str, Any], repo_root: Path, errors: List[str], warnings: List[str]) -> None:
    """
    L2: Enforceable.
      - All component paths must exist
      - For .py files, compare manifest fields with header metadata (best-effort)
    """
    components = manifest.get("components") or []
    if not isinstance(components, list):
        return

    for idx, comp in enumerate(components):
        prefix = f"L2: components[{idx}]"

        if not isinstance(comp, dict):
            continue

        path_val = comp.get("path")
        if not isinstance(path_val, str):
            continue

        full_path = repo_root / path_val
        if not full_path.exists():
            errors.append(f"{prefix}: path does not exist: {full_path}")
            continue

        # Only check header for Python files
        if full_path.suffix != ".py":
            continue

        lines = _read_code_header(full_path)
        if not lines:
            warnings.append(f"{prefix}: could not read file for header validation: {full_path}")
            continue

        # component_id
        header_cid = _extract_header_field(lines, "component_id")
        manifest_cid = comp.get("component_id")
        if header_cid:
            if header_cid != manifest_cid:
                errors.append(
                    f"{prefix}: component_id mismatch: manifest='{manifest_cid}', header='{header_cid}'"
                )
        else:
            warnings.append(
                f"{prefix}: header has no 'component_id' field (expected for L2); file={full_path}"
            )

        # status
        header_status = _extract_header_field(lines, "status")
        manifest_status = comp.get("status")
        if header_status:
            if header_status != manifest_status:
                errors.append(
                    f"{prefix}: status mismatch: manifest='{manifest_status}', header='{header_status}'"
                )
        else:
            warnings.append(
                f"{prefix}: header has no 'status' field (expected for L2); file={full_path}"
            )

        # authority_level
        header_level = _extract_header_field(lines, "authority_level")
        manifest_level = comp.get("authority_level")
        if header_level:
            try:
                header_level_int = int(header_level)
            except ValueError:
                errors.append(
                    f"{prefix}: authority_level in header is not an integer: '{header_level}'"
                )
            else:
                if isinstance(manifest_level, int) and header_level_int != manifest_level:
                    errors.append(
                        f"{prefix}: authority_level mismatch: manifest={manifest_level}, header={header_level_int}"
                    )
        else:
            warnings.append(
                f"{prefix}: header has no 'authority_level' field (expected for L2); file={full_path}"
            )


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate PLD manifest.yaml against METADATA_MANIFEST_SPEC v0.9.0."
    )
    parser.add_argument(
        "--manifest",
        "-m",
        type=str,
        default="manifest.yaml",
        help="Path to manifest.yaml (default: ./manifest.yaml)",
    )
    parser.add_argument(
        "--level",
        "-l",
        type=str,
        default="L1",
        choices=["L0", "L1", "L2"],
        help="Validation level: L0 (permissive), L1 (structured), L2 (enforceable). Default: L1",
    )
    parser.add_argument(
        "--repo-root",
        type=str,
        default=".",
        help="Repository root for resolving component paths (default: current directory).",
    )
    return parser.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    manifest_path = Path(args.manifest)
    repo_root = Path(args.repo_root).resolve()

    errors: List[str] = []
    warnings: List[str] = []

    try:
        manifest = load_manifest(manifest_path)
    except ValidationError as e:
        print(f"Fatal: {e}", file=sys.stderr)
        return 1

    # L0 is base for all levels
    validate_l0(manifest, errors)

    if args.level in ("L1", "L2"):
        validate_l1(manifest, errors)

    if args.level == "L2" and not errors:
        # Only run deeper checks if earlier levels passed
        validate_l2(manifest, repo_root, errors, warnings)

    # Report
    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"  - {w}")
        print()

    if errors:
        print("Errors:")
        for e in errors:
            print(f"  - {e}")
        print()
        print(f"Validation FAILED at level {args.level}.")
        return 1

    print(f"Validation PASSED at level {args.level}.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
