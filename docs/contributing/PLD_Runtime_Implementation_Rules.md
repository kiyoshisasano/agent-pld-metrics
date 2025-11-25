# PLD Runtime Implementation Rules

**Status:** Working Draft — subject to refinement during implementation and review.
**Scope:** Runtime layer (`pld_runtime/**`) only.
**Audience:** Contributors implementing or modifying runtime behavior.

---

## 1. Purpose

This document defines development rules for the **runtime layer**, ensuring:

* architectural integrity across files
* alignment with PLD Levels 1–3
* predictable behavior during execution
* maintainability and upgrade safety

It is not a normative specification but guides implementation decisions.

---

## 2. Responsibility Boundaries

The runtime layer MUST NOT redefine or reinterpret:

| PLD Layer                   | Runtime Behavior                             | Allowed?                        |
| --------------------------- | -------------------------------------------- | ------------------------------- |
| Level 1 — Schema            | validate against / emit fields               | ✔ required                      |
| Level 2 — Semantics         | interpret `event_type`, `phase`, or taxonomy | ⚠ only when explicitly required |
| Level 3 — Runtime Standards | enforce rules at boundaries                  | ✔ required                      |
| Level 4 — Examples          | reference but not depend on                  | ✔ optional                      |
| Level 5 — Implementation    | extend behavior safely                       | ✔ allowed                       |

Runtime MAY extend functionality **only when explicitly scoped as Level 5 behavior**.

---

## 3. Change Control Rules

### 3.1 Allowed changes

✔ Implementing new runtime modules
✔ Adding exporters, buffers, or pipeline enhancements
✔ Adding instrumentation, telemetry, or performance logging
✔ Extending internal signal → event mapping (with justification)

### 3.2 Requires justification + documentation

⚠ Changing mapping rules for: `event_type`, `phase`, or taxonomy code
⚠ Altering default validation behavior
⚠ Modifying event envelope structure

### 3.3 Never permitted (without upstream spec change)

❌ Breaking schema alignment with Level 1 event format
❌ Creating new event types not in semantic registry
❌ Overriding prefix→phase alignment enforcement

---

## 4. Implementation Principles

### 4.1 Determinism

Runtime behavior MUST be deterministic under identical input conditions.

### 4.2 Stateless ↔ Stateful Boundary

* Modules SHOULD remain stateless unless defined as buffers or lifecycle components.
* State retention MUST be intentional and documented.

### 4.3 Extensibility

Runtime modules SHOULD:

* use dependency injection when possible
* avoid hard-coded IO targets
* support configurable transports and validation modes

---

## 5. Logging and Observability Rules

* Logging MUST NOT modify event content.
* Logging pipeline MUST treat emitted events as immutable.
* Instrumentation MUST NOT depend on semantic interpretation unless explicitly intended.

Runtime logging MUST follow this pipeline pattern:

```
signal → RuntimeSignalBridge → event(dict) → buffer → exporter(s)
```

---

## 6. Pull Request Acceptance Criteria

A change is eligible only if it includes:

* [ ] Alignment with this document
* [ ] Traceability to a requirement or design decision
* [ ] Tests (unit or scenario‑based)
* [ ] No regression in schema compliance
* [ ] Documentation update if behavior changes

If a change cannot meet one or more criteria, the pull request MUST include a rationale and proposed resolution before review continues.

---

## 7. Future Evolution

This document will evolve as:

* stabilization milestones are reached,
* runtime behavior becomes reusable across implementations,
* Level 3 governance resolves remaining undefined behaviors.

Revisions SHOULD be incremental and traceable.

---

**Feedback Welcome.** This document remains open to improvement during the exploration and validation phase.
