<!==
    path: docs/README.md
    component_id: docs_readme
    kind: doc
    area: meta
    status: stable
    authority_level: 2
    purpose: Top-level index for documentation tree.
    ==>

# Phase Loop Dynamics (PLD) — Documentation Index

This documentation set exists to support the design, implementation, evaluation, and governance of multi-turn AI agents using the Phase Loop Dynamics model.

> **What is PLD?**
> PLD is not just a prompt technique — it is a runtime behavior model designed to ensure that agents remain aligned across turns, recover from drift, and maintain stable reasoning and tool use under uncertainty.

## 📚 Recommended Reading Flow

If you're new to PLD, the following sequence builds understanding layer by layer—from core concepts to implementation and evaluation.

| Step | Scope | Recommended File | Purpose |
| :--- | :--- | :--- | :--- |
| **1** | **Concepts** | [`/concepts/01_introduction.md`](./concepts/01_introduction.md) | Understand the motivation, problem framing, and foundational mindset. |
| **2** | **Model** | [`/concepts/02_drift_repair_model.md`](./concepts/02_drift_repair_model.md) | Learn the `Drift → Repair → Reentry` lifecycle vs one-shot prompting. |
| **3** | **Semantics** | [`/specifications/level_2_semantics/overview_event_spec.md`](./specifications/level_2_semantics/overview_event_spec.md) | Understand behavioral logging and how drift becomes observable. |
| **4** | **Standard** | [`/specifications/level_3_standards/PLD_Runtime_Standard_v2.0.md`](./specifications/level_3_standards/PLD_Runtime_Standard_v2.0.md) | Learn enforcement states, policies, and runtime mechanics. |
| **5** | **Metrics** | [`/metrics/cookbook.md`](./metrics/cookbook.md) | Learn how to measure drift (PRDR, VRL) using PLD metrics. |

---

## 🧩 Documentation Structure

PLD documentation is organized by stability levels and functional purpose:

### 🔹 1. Concepts ([`/concepts`](./concepts/))
The "Why" and "What" of PLD — foundational mental models.
* Drift vs. Shift
* Repair patterns
* Operator Primitives

### 🔹 2. Specifications ([`/specifications`](./specifications/))
The authoritative schema and behavioral contract (**Level 1–3**).
* **Level 1:** JSON Schema (Hard Invariants)
* **Level 2:** Semantics & Event Matrix
* **Level 3:** Runtime & Metrics Standards

### 🔹 3. Architecture ([`/architecture`](./architecture/))
Implementation design, runtime layering, and control-flow rules (**Level 4–5**).
* Design Principles
* Runtime Modes (Observer vs Governor)
* Implementation Rules

### 🔹 4. Metrics ([`/metrics`](./metrics/))
Operational analytics, cookbooks, and evaluation methodology.
* **PRDR** (Precision of Repair-Driven Recovery)
* **REI** (Runtime Entropy Index)
* **VRL** (Violation-Recovery Loop score)

### 🔹 5. Patterns ([`/patterns`](./patterns/))
Reusable design and behavioral correction patterns.
* Drift response patterns
* Tool response rules
* Repair templates

---

## 🧪 Reference Traces

A dedicated folder provides realistic synthetic run logs demonstrating PLD behavior.  
If you're integrating PLD into a tracing or observability pipeline, start here.

👉 **[`../examples/reference_traces/`](../examples/reference_traces/)**
* Golden semantic repair trace
* High-entropy forensic trace

---

## ⚙️ Implementation Entry Points

If you are building or instrumenting an agent runtime, check the Quickstart guide:

👉 **[`../quickstart/metrics_quickcheck/`](../quickstart/metrics_quickcheck/)**
* `README_metrics.md`: How to verify metrics locally.
* `pld_events_demo.jsonl`: Sample event stream.
* `verify_metrics_local.py`: Diagnostic script.

---

## 🧭 Design Principles

PLD documents follow these rules:

* **📌 Stable terminology:** No silent renaming or synonym drift.
* **🧱 Composable primitives:** Reusable across frameworks (LangGraph, Assistants API, Swarm).
* **🔍 Observable over assumptive:** Runtime must expose reasoning state transitions.
* **🧪 Behavior before performance:** Correctness precedes optimization.

---

## 📜 Licensing & Status

* **Status:** Draft / Active Development
* **Documentation:** [CC-BY-4.0](../LICENSES/LICENSE-CC-BY-4.0.txt)
* **Code:** [Apache-2.0](../LICENSES/LICENSE-APACHE-2.0.txt)

**Maintainer:** Kiyoshi Sasano
Details: `/LICENSES/LICENSES.md`

---

Maintainer: **Kiyoshi Sasano**


