# Metadata Manifest Specification — Candidate Version (v0.9.0)

> **Status:** Candidate Specification
> **SPDX-License-Identifier:** CC-BY-4.0

This specification defines the shared metadata manifest format used across the **Phase Loop Dynamics (PLD) Runtime Repository**.
It establishes a minimal, predictable structure intended for collaboration, scaling, and future automation, while preserving experimentation.

This document replaces the prior **Working Draft** and advances the specification toward stabilization.

---

## 🎯 Scope & Intent

The manifest format supports:

* **Discoverability** — what exists and why
* **Traceability** — maturity, intent, and role of runtime artifacts
* **Consistency** — shared conventions without restricting design
* **Future automation** — CI validation, documentation generation, dependency mapping

This specification **does not** define runtime behavior, architectural governance, or certification rules. Those belong to separate standards.

---

## 📍 File Location & Naming

A manifest **may exist at the folder level**, documenting components contained within.

```
pld_runtime/
  manifest.yaml   ← Manifest describes items in this folder
  detectors/
  operators/
  schemas/
```

**Rules:**

* File name must be: `manifest.yaml`
* One manifest per folder
* Manifests are optional for early-stage or experimental folders

---

## 🧩 Manifest Structure

A manifest consists of a small header and a list of component entries.

```yaml
version: 0.9.0                # Format version (this spec)
default_license: Apache-2.0   # SPDX identifier

components:
  - path: <relative-path>
    component_id: <snake_case_identifier>
    kind: <kind_enum>
    area: <free-text domain grouping>
    status: <status_enum>
    authority_level: <integer>
    purpose: <1–3 sentence summary>

    # Optional
    authority_scope: <text>
    status_detail: <text>
    deps: [ ... ]
```

---

## 📖 Field Definitions

| Field             | Required | Type          | Description                                                               |
| ----------------- | -------- | ------------- | ------------------------------------------------------------------------- |
| `version`         | Yes      | SemVer        | Tracks the manifest **spec format** — not component versions.             |
| `default_license` | Yes      | SPDX string   | License applied when component metadata does not specify otherwise.       |
| `components`      | Yes      | List          | List of described items.                                                  |
| `path`            | Yes      | Relative path | Location of the referenced resource.                                      |
| `component_id`    | Yes      | snake_case    | Machine-readable stable identifier. Must align with code header metadata. |
| `kind`            | Yes      | Enum          | See controlled vocabulary below.                                          |
| `area`            | Yes      | Free-text     | Logical domain or conceptual grouping.                                    |
| `status`          | Yes      | Enum          | Declares maturity level.                                                  |
| `authority_level` | Yes      | Integer (1–5) | Governance maturity and operational tolerance.                            |
| `purpose`         | Yes      | Text          | One to three sentences describing intent.                                 |
| Optional Fields   | No       | *Various*     | Add when clarity increases signal, not noise.                             |

---

## 🧭 Controlled Vocabulary

### `kind`

```
code | schema | config | runtime_module | metric | example | doc
```

### `status`

```
experimental | draft | candidate | stable
```

### `authority_level`

```
1–5 (integer)
```

Meaning is aligned with runtime maturity tiers but not yet normative.

---

## 🔗 Mapping to Code Metadata Headers

A manifest entry must correspond to metadata inside the associated runtime file.

| Concept         | Manifest Field    | Python Header Field     | Rules                                              |
| --------------- | ----------------- | ----------------------- | -------------------------------------------------- |
| Identifier      | `component_id`    | `component_id:`         | Must match exactly (snake_case).                   |
| Status          | `status`          | `status:`               | Must use controlled vocabulary.                    |
| Version         | —                 | `version:` (file-local) | **Component version lives in code, not manifest.** |
| Purpose         | `purpose`         | `purpose:`              | Free-text alignment expected.                      |
| Authority Level | `authority_level` | `authority_level:`      | Must match.                                        |

> A future CI validator may enforce one-to-one alignment.

---

## 🧪 Validation Levels

To enable gradual adoption, validation occurs in three strictness tiers:

| Level                | Name                  | Enforced Elements                                  |
| -------------------- | --------------------- | -------------------------------------------------- |
| **L0 — Permissive**  | Minimal schema exists | `version`, `components[]` present                  |
| **L1 — Structured**  | Format consistency    | All required fields valid vocabulary               |
| **L2 — Enforceable** | Tool-compatible       | Paths resolvable and metadata matches code headers |

At present, tooling validation is **optional**, but future versions may require L1 for contribution acceptance.

---

## 🧱 Versioning Rules

* Manifests do **not** track component versioning.
* Component-level lifecycle remains stored within the artifact (e.g., inside `.py` runtime metadata blocks).
* The manifest’s `version` changes **only when the format specification changes**.

---

## 🚧 Future Extension Directions (Non-Normative)

Potential future additions may include:

* Automated manifest generation from runtime files
* Machine-readable dependency graphs
* Governance maturity audits
* Component status transitions linked to operational telemetry

These possibilities do not affect the v0.9 format.

---

## 📩 Feedback & Contributions

This specification is a candidate. Feedback from integrators, researchers, and runtime implementers is encouraged.

Submit feedback via issues or discussion threads.

> *“Specifications should reflect reality, not precede it.”*

---

**Maintainer:** Kiyoshi Sasano
Copyright © 2025
