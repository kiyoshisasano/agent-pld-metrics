# Introduction to PLD Concepts

## 1. What This Document Is

This document provides a high-level conceptual introduction to **Predictable Lifecycle Design (PLD)**. It is written for developers, designers, and system engineers who want to understand how PLD structures multi-turn agent behavior, runtime decisions, and event observability.

This file is **non-normative**. All authoritative definitions come from:

* **Level 1 — Schema** (canonical event structure)
* **Level 2 — Semantic Matrix** (event meanings and phase rules)
* **Level 3 — Runtime Standards** (operational expectations, taxonomy, and validation)

The purpose of this document is to explain *how to think about PLD*, not to redefine it.

### 1.1 Audience

PLD concepts are primarily aimed at:

* Runtime and platform engineers implementing PLD-aligned behavior
* LLM workflow and orchestration designers
* Observability / telemetry engineers
* Governance and policy owners who need traceable agent behavior

You do **not** need to adopt a specific framework to use PLD. You only need to be able to emit structured events and enforce basic runtime rules.

### 1.2 PLD Is a Discipline, Not a Framework

PLD is **not** a new agent framework. It is a discipline:

> **Structure + governance + telemetry layered onto whatever runtime you already use.**

You can apply PLD to LangGraph, Assistants API, custom state machines, or any other orchestration model, as long as you:

* emit PLD events,
* respect the lifecycle phases,
* and keep your runtime aligned with the Level 1–3 standards.

---

## 2. Why PLD Exists

Multi-turn agents often fail for predictable reasons:

* they lose track of instruction intent,
* they drift away from task constraints,
* they repair output inconsistently,
* they continue execution when they should pause,
* they fail to provide observable, diagnosable traces.

PLD solves these problems by offering a **unified lifecycle framework** for agent behavior. Instead of treating each agent response as an ad-hoc action, PLD frames the entire session as a series of *explicit, observable lifecycle events*.

With PLD:

* drift is detected consistently,
* repair is structured rather than ad-hoc,
* continuation rules are explicit,
* outcomes are logged in a predictable way,
* every agent decision becomes traceable and auditable.

### 2.1 Governance Questions per Turn

Conceptually, PLD asks the same questions on every turn:

1. **Did drift occur?**
2. **If so, what repair is appropriate?**
3. **Did the repair stabilize behavior?**
4. **Should execution continue?**
5. **How did the interaction conclude?**

If you cannot answer these questions from your logs alone, your system is not yet fully PLD-aligned.

---

## 3. Core Lifecycle Model (High-Level)

At the heart of PLD is a structured, phase-based lifecycle. A session moves through well-defined phases:

1. **Drift** — The agent has deviated from constraints.
2. **Repair** — The system attempts to correct the deviation.
3. **Reentry** — The system validates whether it can safely resume normal execution.
4. **Continue** — The system is allowed (or blocked) from proceeding.
5. **Outcome** — The session ends or transitions into a final state.

Each phase is represented through Level 2 event types and Level 3 taxonomy codes. The conceptual model in this document mirrors—but does not override—these definitions.

### 3.1 Lifecycle Sketch

Two complementary views are useful:

**Lifecycle phases:**

```text
Drift → Repair → Reentry → Continue → Outcome
```

**Runtime execution loop:**

```text
Execute → Detect → Repair → Validate (Reentry) → Continue / Terminate → Log
```

The lifecycle describes *what state the session is in*; the execution loop describes *what the runtime is doing* on each turn.

---

## 4. Observable Events as First-Class Signals

Every decision the agent makes is captured as a PLD event guided by three invariants:

* **Schema-valid:** must satisfy Level 1 event schema.
* **Phase-valid:** must match the Level 2 semantic mapping.
* **Taxonomy-valid:** must use Level 3 codes without modification.

In practice, this means:

* lifecycle prefixes (`D`, `R`, `RE`, `C`, `O`, `F`) MUST align with the `pld.phase` field,
* `event_type` MUST agree with the phase defined in the Level 2 event matrix,
* taxonomy codes MUST NOT be redefined at runtime.

This makes PLD uniquely predictable: every session is a structured timeline of verifiable events.

### 4.1 Event-per-Turn Invariant (Conceptual)

A PLD-aligned runtime is expected to emit **at least one PLD event per turn**. This ensures that:

* no turn is invisible to observability,
* drift and repair can always be reconstructed from traces,
* metrics can be computed over real traffic.

The exact number and type of events per turn is left to runtime design, but *“no event at all”* is considered misaligned with PLD.

---

## 5. Drift and Repair at a Glance

Two phases are especially important for developers:

* **Drift Phase:** The system recognizes something has gone wrong—incorrect instructions, missing keys, invalid tool outputs, semantic mismatch, policy violations, etc.
* **Repair Phase:** The system fixes the deviation using one of several strategies (Static, Guided, Human-in-the-Loop). See `03_repair_strategies.md` for details.

These phases are not optional. They are the core of PLD’s stability guarantees.

### 5.1 Reentry Patterns (Preview)

After repair, the system must decide whether it is safe to resume. PLD distinguishes multiple Reentry patterns, for example:

* **Explicit confirmation** (user or model agrees to the plan),
* **Constraint validation** (system checks tools, state, or business rules),
* **Automatic reentry** (stability inferred from lack of further drift).

Detailed definitions and examples are provided in `02_drift_repair_model.md`.

---

## 6. Specification Levels (Level 1–4)

Concepts documents sit alongside a hierarchy of specification levels. When conflicts occur, **higher levels prevail**.

| Level | Source (indicative)                               | Role                         |
| ----- | ------------------------------------------------- | ---------------------------- |
| 1     | `pld_event.schema.json`                           | Structural invariant — MUST  |
| 2     | `event_matrix.yaml` and related semantic docs     | Semantic mapping — MUST      |
| 3     | Runtime standards and metrics specifications      | Operational rules — SHOULD   |
| 4     | Examples, demos, and tutorials (Quickstart, etc.) | Non-normative guidance — MAY |

This document lives in **Level 4** as a conceptual guide. It MUST NOT override any Level 1 or Level 2 rule.

---

## 7. Relationship to Runtime Logic

Although this document is conceptual, it aligns with how PLD runtimes actually work:

* drift detectors identify anomalies,
* controllers decide what repair strategy to apply,
* RuntimeSignalBridge (or equivalent) builds canonical events,
* structured loggers produce immutable records.

Implementers should treat PLD events as **immutable outputs**—once created, an event’s canonical fields MUST NOT be changed.

Many runtimes also operate in an explicit **validation mode** (e.g., `strict`, `warn`, or `normalize`) that configures how aggressively to enforce PLD rules. The details of validation modes are defined in the runtime and enforcement documentation; here, it is enough to know that:

* schema violations are never acceptable,
* semantic rules can be enforced strictly or with controlled normalization,
* the chosen mode should be documented as part of the system’s PLD posture.

---

## 8. Reading the Rest of the Concepts Section

The Concepts directory includes:

* **02_drift_repair_model.md** — Detailed lifecycle and flow diagrams.
* **03_repair_strategies.md** — Practical repair strategy patterns (Static / Guided / HITL).
* **operator_primitives/** — Fine-grained building blocks for detection and repair.
* **reference_map.md** — Cross-links to architecture, patterns, and specifications.

Use this introduction as the conceptual grounding before exploring the detailed design documents.

---

## 9. What This Document Does *Not* Do

* It does **not** restate the canonical schema.
* It does **not** redefine taxonomy or phases.
* It does **not** mandate any specific controller architecture.

All authoritative content lives in Levels 1–3; this document is an educational guide designed to help you understand and navigate the PLD ecosystem.

---

## 10. Summary

PLD provides a structured, predictable framework for multi-turn agents by enforcing a clear lifecycle built on drift detection, repair, reentry validation, continuation control, and observable outcomes.

A useful diagnostic question is:

> **“When this agent drifts, what happens next—and how do we know whether the repair worked?”**

If answering this requires guesswork, the system is not yet fully PLD-aligned.

This introduction establishes the foundational mindset for understanding PLD. The subsequent documents elaborate how these ideas become concrete, traceable behaviors in real-world systems.

