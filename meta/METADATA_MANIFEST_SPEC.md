# Metadata Manifest Specification

**(Working Draft — Exploratory Stage)**

> This document defines the lightweight shared metadata format used across the PLD Runtime repository.
> It is intentionally constrained and may evolve as new use cases or tooling appear.
> Feedback, refinement, and real-world validation are welcome.

---

## 🎯 Purpose

The manifest format exists to support:

* **Discoverability** — understanding what files exist and why.
* **Traceability** — knowing the level, scope, and maturity of runtime components.
* **Consistency** — applying a predictable structure across folders without constraining experimentation.
* **Future tooling** — enabling validation, CI checks, automated docs, or dependency visualization later — without committing to them now.

This specification does *not* attempt to describe execution behavior, governance authority, or design rationale.
It focuses solely on **lightweight structured metadata for components.**

---

## 🧭 Where Manifests Live

Each high-level functional directory may optionally include a manifest.

Example:

```
pld_runtime/
  manifest.yaml  ← this file documents the components in this folder
  01_schemas/
  02_ingestion/
  ...
```

A repository **may contain multiple manifests**, but each folder should have **at most one.**
Manifests are *not* required for experimental scratch files, prototype notes, or deeply temporary artifacts.

---

## 📦 File Name Convention

```
manifest.yaml
```

* Lowercase
* Singular
* No prefix or suffix unless future tooling requires it

---

## 🧩 Minimal Required Fields

Each manifest contains two layers:

```yaml
version: <manifest format version>     # ex: 1.0.0 (increment only if the format changes)
default_license: Apache-2.0            # SPDX identifier

components:
  - path: <relative file path>
    kind: <code | schema | config | ops_guide | example>
    area: <logical domain grouping>
    status: <stable | draft | experimental | candidate>
    authority_level: <integer>         # "Level 5" → 5
    purpose: <1–3 sentence summary>
```

These fields should remain **stable** and are intended to support future automation.

---

## 🧪 Optional but Supported Fields

Use only when they add clarity — avoid over-documentation.

```yaml
    deps: [ ... ]          # explicit dependencies (schemas, standards, runtime layers)
    status_detail: "..."   # nuance or contextual notes beyond the main status field
    authority_scope: "..." # ex: runtime implementation / operational layer
```

These fields remain intentionally flexible during this exploratory phase.

---

## 🏷 Status Vocabulary

Status reflects **maturity, not correctness.**

| Status         | Meaning                                                | Tone Guidance                      |
| -------------- | ------------------------------------------------------ | ---------------------------------- |
| `experimental` | Actively evolving; design may shift                    | Encourages feedback                |
| `draft`        | Working understanding exists; expected to evolve       | Avoid definitive language          |
| `candidate`    | Candidate for stabilization and review                 | Implementation feedback encouraged |
| `stable`       | Reasonably proven in usage; future changes incremental | Still avoid “final” terminology    |

Avoid using: **final / approved / official / locked**
until governance or real-world validation supports such terms.

---

## 📚 Tone Expectations (Applies to Purpose + Notes)

* Transparent about uncertainty
* Avoids overstated confidence
* Invitation-based language is welcome

Useful phrasing examples:

* “Currently assumed…”
* “Expected to change as implementation matures.”
* “Seeking feedback from integrators and operators.”

---

## 🧵 Versioning

The `version:` field at the top of the manifest tracks the **format**, not the content.
File-level versions remain inside the artifacts themselves (schemas, code, standards).

Future automation may link `manifest.yaml` to `CHANGELOG` entries, but this is optional.

---

## 🔧 Future Extensions (Non-binding)

Possible future additions (not active yet):

* machine-readable semantic diff support
* linking status transitions to governance checkpoints
* validation tooling enforcing field presence or vocabulary constraints
* automatic documentation output

These are intentionally not implemented at this stage.

---

## 🙌 Feedback

If you have implementation experience, tooling proposals, or counterexamples, please share.
This spec is a working instrument and will evolve based on practice rather than abstraction.

> *“Document reality; don’t legislate ahead of it.”*

---

*Last updated: **Working Draft** — subject to revision.*
