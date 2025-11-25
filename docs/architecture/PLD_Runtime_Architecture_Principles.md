<!--
version: 2.0.0
status: working draft
authority_level_scope: Architecture reference (repository-wide)
purpose: Capture shared architectural values and constraints guiding runtime implementation.
note: This document reflects the current understanding and may evolve based on feedback and runtime validation.
-->

# PLD Runtime Architecture Principles

This document defines the architectural principles guiding the design, extension, and maintenance of the PLD runtime.
It serves as a reference point for contributors and an anchor for design consistency across modules.

While several concepts are stabilizing, this document remains a **working draft** and may evolve as implementation feedback accumulates.

---

## 1. Separation of Concerns — Clear Layer Boundaries

The runtime architecture prioritizes **strict functional separation**, designed to ensure clarity, testability, and predictable behavior.

| Layer             | Responsibility                                          | Mutation Allowed?              |
| ----------------- | ------------------------------------------------------- | ------------------------------ |
| Signal Detection  | Detect runtime conditions (drift, repair cues, metrics) | ✔ internal state only          |
| Semantic Mapping  | Convert signals → PLD events (`RuntimeSignalBridge`)    | ✔ within bridge rules          |
| Envelope + Schema | Apply Level 1–3 compliance constraints                  | ✔ via controlled normalization |
| Logging + Export  | Store/write/transport events                            | ❌ PLD event mutation禁止         |

> **Key invariant:**
> After `RuntimeSignalBridge.build_event()` returns, a PLD event becomes **immutable**.

---

## 2. Single Source of Truth for Event Semantics

Event meaning MUST be derived only from:

1. Level 1 schema
2. Level 2 semantic rules & taxonomy
3. Level 3 runtime standard
4. Level 5 runtime bridge mappings

No downstream component (logging, exporters, visualizers, analytics samplers) may reinterpret or correct semantics.

If a downstream component behaves inconsistently with semantics, the upstream mapping must be reviewed—not patched downstream.

---

## 3. Transparency and Traceability Over Optimization

Runtime design favors:

* **Observability**
* **Auditability**
* **Debuggability**

over early ergonomics or performance tuning.

Examples of traceability rules:

* Every event MUST be timestamped.
* Events MUST retain session/turn ordering.
* Local inference or heuristics MUST NOT replace governed semantics.

Performance tuning may be introduced later, but MUST NOT obscure evidence or runtime reasoning.

---

## 4. Progressive Validation Strategy

The runtime allows three explicit modes:

| Mode        | Behavior                   | Intended Use                         |
| ----------- | -------------------------- | ------------------------------------ |
| `STRICT`    | reject deviations          | schema conformance testing, research |
| `WARN`      | allow but log deviation    | experimentation, review              |
| `NORMALIZE` | align values when possible | production or soft integration       |

These modes DO NOT change semantics — only how deviations are handled.

---

## 5. Extensibility Without Spec Mutation

The runtime may evolve but must:

* Introduce new runtime signals before new event types.
* Treat new behavior as **experimental** unless mapped to Level 2 taxonomy.
* Preserve backward compatibility unless governed spec changes.

> New capability → runtime signal → mapping → governed event
> Never bypass mapping.

---

## 6. Documentation and Communication Culture

Because PLD is still evolving, documentation SHOULD:

* acknowledge uncertainty where applicable
* prefer “current understanding” to “final truth”
* invite implementation feedback
* use standard terminology consistently

Changes to architecture MUST include rationale or design notes when non-obvious.

---

## 7. Design Ethos

The runtime adheres to four guiding values:

| Value           | Meaning                                                        |
| --------------- | -------------------------------------------------------------- |
| **Predictable** | Same signal → same output → same downstream behavior           |
| **Minimal**     | No redundant logic or competing mapping paths                  |
| **Observable**  | System state should be measurable, reviewable, inspectable     |
| **Honest**      | Runtime must not guess user intent or silently rewrite meaning |

---

## Change Policy

| Type of Change                   | Requires Review?            | Notes |
| -------------------------------- | --------------------------- | ----- |
| Logging transport implementation | ❌ No semantic impact        |       |
| Mapping logic (signal → event)   | ✔ Mandatory                 |       |
| Schema or lifecycle behavior     | ✔✔ Formal governance review |       |
| Example renaming or wording      | ❌ unless meaning changes    |       |

---

## Feedback and Evolution

This is an actively maintained architectural reference.
Contributors are encouraged to raise questions, propose refinements, and record implementation discrepancies.

Suggested phrase for PRs affecting this document:

> “This update reflects implementation learning and seeks alignment with runtime behavior.”

---

**End of Document**
