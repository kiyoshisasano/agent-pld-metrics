# Phase Loop Dynamics (PLD) — Documentation Index

> This documentation set exists to support **design, implementation, evaluation, and governance** of multi-turn AI agents using the Phase Loop Dynamics model.

PLD is not just a prompt technique — it is a **runtime behavior model** designed to ensure that agents remain aligned across turns, recover from drift, and maintain stable reasoning and tool use under uncertainty.

This README provides an entry point into the documentation stack.

---

## 📚 Recommended Reading Flow

If you're new to PLD, the following reading order helps build intuition before implementation:

| Stage | Folder / File                                                         | Goal                                                              |
| ----- | --------------------------------------------------------------------- | ----------------------------------------------------------------- |
| **1** | `/docs/concepts/01_introduction.md`                                   | Understand the core motivation and principles behind PLD.         |
| **2** | `/docs/concepts/02_drift_repair_model.md`                             | Learn the Drift → Repair → Reentry → Continue lifecycle.          |
| **3** | `/docs/specifications/level_2_semantics/overview_event_spec.md`       | Understand the semantic event model and logging contract.         |
| **4** | `/docs/specifications/level_3_standards/PLD_Runtime_Standard_v2.0.md` | Runtime enforcement model, policy layering, and lifecycle states. |
| **5** | `/docs/metrics/07_pld_operational_metrics_cookbook.md`                | Learn how to evaluate agent stability using PLD metrics.          |

Optional but useful:

* `/analytics/multiwoz_2.4_n200/` — annotated corpus for drift identification.

---

## 🧩 Documentation Structure

PLD documentation is organized by stability and purpose:

### 🔹 1. Concepts (`/docs/concepts/`)

The "Why" and "What" of PLD — foundational mental models.

* Drift vs. Shift
* Repair patterns
* Taxonomy reference map

### 🔹 2. Specifications (`/docs/specifications/`)

The authoritative schema and behavioral contract.

* Level 1: JSON schema
* Level 2: Semantics and event matrices
* Level 3: Runtime and metric standards

### 🔹 3. Architecture (`/docs/architecture/`)

Implementation design, runtime layering, and control-flow rules.

* Principles
* Implementation guardrails
* Layer dependency model

### 🔹 4. Metrics (`/docs/metrics/`)

Operational analytics, dashboards, and evaluation methodology.

* PRDR (Precision of Repair-Driven Recovery)
* REI (Runtime Entropy Index)
* VRL (Violation-Recovery Loop score)

### 🔹 5. Patterns (`/docs/patterns/`)

Reusable design and behavioral correction patterns.

* Drift response patterns
* Tool response rules
* Repair templates

---

## 🧪 Reference Traces

A dedicated folder provides **realistic synthetic run logs** demonstrating PLD behavior:

📂 `examples/reference_traces/`

* Golden semantic repair trace
* High-entropy forensic trace
* Trace generator

If you're integrating PLD into a tracing or observability pipeline, start there.

---

## ⚙️ Implementation Entry Points

If you are building or instrumenting an agent runtime:

```
docs/
 ├── operator_primitives/
 ├── patterns/
 └── metrics/
```

These contain:

* enforcement and observer modes
* control-loop primitives
* telemetry mapping

---

## 🧭 Design Principles

PLD documents follow these rules:

* 📌 **Stable terminology** — no silent renaming or synonym drift
* 🧱 **Composable primitives** — reusable across frameworks (LangGraph, Assistants API, Swarm, RAG-based agents)
* 🔍 **Observable over assumptive** — runtime must expose reasoning state transitions
* 🧪 **Behavior before performance** — correctness precedes optimization

---

## 📝 Status and Roadmap

* Stage 1 — Concepts and standards (complete)
* Stage 2 — Trace examples and reference tooling (complete)
* Stage 3 — Notebook metrics and visualization demos (in progress)
* Stage 4 — Framework integration guides (planned)

---

## 📜 Licensing Model

Documentation is licensed under **CC-BY-4.0**.
Runtime code, generation scripts, and examples are licensed under **Apache-2.0**.

Details: `/LICENSES/LICENSES.md`

---

Maintainer: **Kiyoshi Sasano**

