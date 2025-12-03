# Phase Loop Dynamics™ (PLD)

[![License: Apache-2.0 | CC-BY-4.0](https://img.shields.io/badge/license-Apache%202.0%20%7C%20CC--BY--4.0-blue)](LICENSE)
[![SPDX-License](https://img.shields.io/badge/SPDX-Apache--2.0_AND_CC--BY--4.0-blue)](LICENSE)
![Status: Active](https://img.shields.io/badge/status-active-brightgreen)

*A Runtime Phase Model for Stable Multi-Turn LLM Systems*

### 👋 Welcome to PLD

**Phase Loop Dynamics (PLD)** is a runtime governance model designed to help  
multi-turn LLM systems remain **stable, aligned, and predictable — across turns, tools, and models.**

This repository contains **specifications, runtime components, examples, adoption resources, and evaluation patterns.**

## 🧭 Start Here Based on Your Role

| You Are…                           | Recommended Entry Point                                                                                           |
| ---------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| 🧑‍💻 **Developer / Engineer**     | Start with: `quickstart/` → run an example such as `easy_pld_demo.py`, which provides a concise high-level usage flow. |
| 🧪 **Researcher / Architect**      | Explore: `docs/` (Levels 1–3) → semantics, schema, taxonomy, runtime reasoning.                                   |
| 🧑‍💼 **Product / Decision Maker** | View: `pitch/` → understand why multi-turn systems fail and how PLD stabilizes them.                              |
| 🧭 Evaluating or Integrating | Check: `examples/` and `analytics/` for patterns, metrics, and field workflows.  
  Selected examples also illustrate how structured PLD traces can be viewed or explored through lightweight dashboards. |


---

## ⚠️ Repository Maturity & Governance Model

> **Status: Candidate — actively evolving.  
> Behavioral patterns, taxonomy, and runtime conventions may continue to evolve based on implementation feedback.**

Community feedback and field reports are encouraged.

---

## 🛑 Scope of This Repository

PLD follows a **Standard-First** philosophy, similar to protocols such as OpenTelemetry, OAuth, or Matrix.

### This Repository **IS:**

* **A Governance Standard:** Defining the logic and lifecycle of Drift → Repair → Reentry (Levels 1–3).
* **A Reference Implementation:** Minimal runtime (`pld_runtime/`) to validate the specification.
* **A Behavioral Contract:** Ensuring alignment across agents, frameworks, and evaluation pipelines.

### This Repository **IS NOT:**

* ❌ A production SDK or turnkey agent framework
* ❌ A batteries-included AI runtime with ecosystem integrations
* ❌ A replacement for LangChain, LangGraph, Semantic Kernel, or AgentOps

Such layers belong in **Level 4+ ecosystem extensions** — not inside the core repository.

---

### Maintainer Role & Change Boundary

The maintainer functions primarily as:

1. **Semantic Steward** — preserving the conceptual integrity of Drift/Repair semantics
2. **Schema Governor** — maintaining Levels 1–3 as stable, versioned specification assets

> **Contributors Welcome:**
> Community contributions are encouraged — especially **Level-4 adapters**
> (e.g., LangGraph nodes, RAG controllers, Semantic Kernel plug-ins, tracing exporters).

---

## 🔗 Quick Links

* 📄 [Core Specifications](/docs/specifications/)
* ⚙️ [Runtime Implementation](/pld_runtime/)
* 🚀 [Quickstart](/quickstart/)
* 🎨 [Adoption & Communication](/pitch/)
* 🤝 [Governance & Roles](/governance/)

PLD does not replace architectures like LangGraph, Assistants API, or custom orchestration.
Instead, it **observes, labels, and stabilizes behavior across the stack — without requiring workflow redesign.**

---

## 🌱 Community & Support

PLD is actively evolving, and real-world usage and shared traces play a key role in refinement.

If you're experimenting with multi-turn agents or runtime stability workflows, you're welcome to participate:

* 📣 Discussions:
  [https://github.com/kiyoshisasano/agent-pld-metrics/discussions](https://github.com/kiyoshisasano/agent-pld-metrics/discussions)
* 🐛 Issues:
  [https://github.com/kiyoshisasano/agent-pld-metrics/issues](https://github.com/kiyoshisasano/agent-pld-metrics/issues)

> If PLD sparks something — share it.

⭐ Want to contribute?
Look for **“good first issue”** labels or start a discussion.  
Even small contributions (examples, tests, docs, traces) are valuable.

---

## 🎯 Why PLD Exists

## ⚡ Runtime Modes: Observer vs. Governor

You can deploy PLD in two architectural modes depending on your performance requirements:

* **👀 Observer Mode (Async)**
    * **Impact:** **0ms Latency** (Fire-and-forget).
    * **Mechanism:** PLD operates parallel to the user response.
    * **Use Case:** Monitoring, Analytics, Post-incident analysis.

* **🛡️ Governor Mode (Sync)**
    * **Impact:** Intercepts & blocks actions before execution.
    * **Mechanism:** PLD acts as a gatekeeper for high-risk actions.
    * **Use Case:** Safety enforcement, Budget control, Autonomous agents.

👉 *See [`/docs/architecture/runtime_modes.md`](/docs/architecture/runtime_modes.md)*

---


Multi-turn agents rarely fail because they *don't know something*—  
they fail because behavior becomes **unstable over time**.  

Common patterns include:

* repeated tool calls without progress
* hallucinated or unstable context
* behavior shifts across models
* drift that temporarily recovers, then returns

PLD introduces a runtime behavioral contract:

```
Drift → Repair → Reentry → Continue → Outcome
```

This ensures alignment persists across turns — not just per isolated response.

---

## 🔁 The Runtime Loop

### 🛡️ Supported Repair Strategies

PLD defines three authoritative patterns for fixing drift, allowing you to balance latency vs. safety:

| Strategy | Mechanism | Best For |
| :--- | :--- | :--- |
| **Static Repair** | Rule-based / Regex fix | Schema errors (Zero latency) |
| **Guided Repair** | LLM Self-Correction | Context/Tone drift |
| **Human-in-the-Loop** | Governance Escalation | High-stakes financial ops |

👉 *See [`/docs/concepts/03_repair_strategies.md`](/docs/concepts/03_repair_strategies.md)*

---


| Phase        | Purpose                    | Example Signals                     |
| ------------ | -------------------------- | ----------------------------------- |
| **Drift**    | Detect misalignment        | contradiction, tool failure         |
| **Repair**   | Soft → hard correction     | clarification, boundary restatement |
| **Reentry**  | Confirm alignment restored | checkpoint summary                  |
| **Continue** | Resume execution           | next valid step                     |
| **Outcome**  | End state                  | complete / partial / failed         |

Visual summary:

<img src="./README_model.svg" width="100%" />

---

### 🧪 Minimal Example: The Repair Loop in Action

A micro-scale real-world example showing how PLD governs behavior:

```jsonc
// 1️⃣ Agent attempts API call — "parking" is missing
{"event_type": "info", "log_class": "tool_call_attempt", "pld_event": false,
 "payload": {"args": {"amenities": ["wifi"]}}}  // ⚠️ parking omitted

// 2️⃣ PLD detects violation (drift)
{"event_type": "drift_detected", "phase": "drift", "pld_event": true,
 "payload": {"status": "VIOLATION", "missing_constraints": ["parking"]}}

// 3️⃣ PLD blocks continuation (paired with continue_allowed later)
{"event_type": "continue_blocked", "phase": "continue", "pld_event": true,
 "payload": {"block_reason_code": "MANDATORY_CONSTRAINT_OMISSION"}}

// 4️⃣ PLD triggers repair (soft repair pattern)
{"event_type": "repair_triggered", "phase": "repair", "pld_event": true,
 "payload": {"repair_code": "soft_repair_triggered",
             "repair_context": {"missing_constraint": "parking"}}}

// 5️⃣ Agent retries with fix
{"event_type": "info", "log_class": "tool_call_attempt", "pld_event": false,
 "payload": {"args": {"amenities": ["wifi", "parking"]}}}  // ✅ Fixed

// 6️⃣ PLD evaluates and passes (reentry check)
{"event_type": "evaluation_pass", "phase": "outcome", "pld_event": true,
 "payload": {"check_kind": "drift_check", "status": "PASS"}}

// 7️⃣ PLD allows continuation (completion of repair loop)
{"event_type": "continue_allowed", "phase": "continue", "pld_event": true,
 "payload": {"approved_call_id": "call_2a3b4c5d"}}
```

| Stage                 | Before PLD              | After PLD                          |
| --------------------- | ----------------------- | ---------------------------------- |
| Tool call             | `"amenities": ["wifi"]` | `"amenities": ["wifi", "parking"]` |
| Phase                 | `drift → repair`        | `reentry → continue`               |
| User intent alignment | ❌ broken                | ✅ restored                         |

see `examples/reference_traces`

> This demonstrates the full PLD loop:  
> **Agent attempt** → **Drift detected** → **Repair** → **Verification** → **Resume**

---

## ⚡ Quickstart — Run PLD in Under 10 Seconds
> A working drift detection demo powered by the built-in runtime detectors is included in the Quickstart.

```bash
python quickstart/easy_pld_demo.py      # Recommended: simplest demo using SimpleObserver
python quickstart/hello_pld_runtime.py
python quickstart/run_minimal_engine.py
python quickstart/metrics_quickcheck/verify_metrics_local.py
```

Next steps → `quickstart/README_quickstart.md`

### High-Level Usage Example

Some workflows benefit from a concise interface that prepares `EventContext`,
manages turn sequencing, and emits structured events through the runtime.
`quickstart/easy_pld_demo.py` illustrates this pattern using `SimpleObserver`,
showing how a turn can be logged with only a few lines of code while still
producing canonical PLD events.

This example is useful when evaluating the runtime from an integration
perspective or when experimenting with lightweight interaction loops.

### 🚀 What the Quickstart Demos Show

1. **`hello_pld_runtime.py`**

   * Emits a canonical `continue_allowed` event via `RuntimeSignalBridge`.
   * Demonstrates **schema-compliance drift detection** using the built-in `SchemaComplianceDetector`.
   * Example: a payload missing the required key `"parking"` is treated as context drift and emits a `drift_detected` event.

2. **`run_minimal_engine.py`**

   * Runs a miniature runtime loop, emitting PLD events across multiple turns.
   * Shows how Drift / Repair / Continue phases appear over time.

3. **`metrics_quickcheck/verify_metrics_local.py`**

   * Reads emitted JSONL logs and validates that **PLD metrics** and **taxonomy** align with the Level-3 standards.
   * Useful as a **sanity check** when extending or integrating PLD runtime.

---

<details>
<summary>🧪 Built-In Runtime Detectors (Experimental)</summary>

PLD Runtime includes **Level-5 built-in detectors**, allowing you to experience drift detection in Quickstart without writing custom detection logic.

Current experimental detectors (see `pld_runtime/detection/builtin_detectors.py`):

| Detector                   | Purpose                                                   | Typical Taxonomy Code |
| -------------------------- | --------------------------------------------------------- | --------------------- |
| `SimpleKeywordDetector`    | Detect mismatched or harmful instruction patterns in text | `D1_instruction`      |
| `SchemaComplianceDetector` | Ensure required keys exist in structured payloads         | `D2_context`          |

These detectors:

* Extend the `DriftDetector` template from `pld_runtime/detection/drift_detector.py`.
* Emit PLD-compliant `drift_detected` events with `phase = "drift"` and `D*`-family codes.
* Do **not** modify Level 1–3 semantics — they operate purely as Level-5 runtime components.

The updated `quickstart/hello_pld_runtime.py` uses `SchemaComplianceDetector` to demonstrate a simple scenario:

* Expected: payload must contain `"parking"`.
* Actual: payload omits `"parking"`.
* Result: a `drift_detected` event with metadata indicating the missing key.

This provides a concrete code-level counterpart to the earlier **repair loop example**, making it easier to map JSON traces back to the runtime implementation.

</details>

---

## 🏛 Architecture: The PLD Level Model

| Level                  | Meaning                            | Folder                                    |
| ---------------------- | ---------------------------------- | ----------------------------------------- |
| **1 — Structure**      | Canonical schema (Hard Invariants) | `/docs/specifications/level_1_schema/`    |
| **2 — Semantics**      | Event meaning & matrix rules       | `/docs/specifications/level_2_semantics/` |
| **3 — Standards**      | Operational metrics & taxonomy     | `/docs/specifications/level_3_standards/` |
| **4 — Implementation** | Runtime design & Patterns          | `/docs/architecture/` & `/docs/patterns/` |
| **5 — Runtime**        | Reference Python Engine            | `/pld_runtime/`                           |

---

## 📂 Repository Guide

```
quickstart/     → start here (code, demos, and built-in drift detectors)
pld_runtime/    → runtime reference implementation
docs/           → specifications (L1-3) & architecture (L4-5)
analytics/      → evaluation datasets & reports
governance/     → collaboration, roles, and PoC protocols
```

Full structure → `SUMMARY.md`

---

## 📈 Observability

Once structured events flow, the system becomes measurable:

<img src="docs/metrics/visuals/dashboard_mockup.svg" width="100%" alt="PLD Analytics Dashboard View" />

* **PRDR — Post-Repair Drift Recurrence**
* **VRL — Visible Repair Load**
* **FR — Failover Rate**

Metrics cookbook → `docs/metrics/cookbook.md`

---

## 🧪 PLD is most useful when:

✔ interaction spans multiple turns  
✔ tools, retrieval, memory, or planning are involved  
✔ alignment persistence matters more than single-response quality  

Less relevant for:  
⚠ single-turn Q&A  
⚠ fully deterministic scripted flows

---

### 🧩 Where PLD Fits in the Agent Stack

PLD is a **behavioral stability layer** that observes and governs system dynamics across turns.

#### 📍 Conceptual Position

```
┌───────────────────────────────────────────────┐
│ Application Logic / Domain Tools / UX        │
└───────────────────────────────────────────────┘
                      ▲
        ┌─────────────────────────────────┐
        │      **PLD Runtime Layer**      │
        │   (Behavioral Governance)       │
        └─────────────────────────────────┘
                      ▼
┌───────────────────────────────────────────────┐
│ LangGraph | Assistants API | Rasa | AgentOps │
└───────────────────────────────────────────────┘
                      ▼
                Foundation Models
```

#### 🧠 What PLD Actually Does

| Area                              | Owned by PLD? | Owner                       |
| --------------------------------- | ------------- | --------------------------- |
| Model inference                   | ❌             | Foundation model            |
| Tool execution                    | ❌             | Agent / orchestrator        |
| Memory strategy                   | ❌             | Framework or design pattern |
| Behavioral stability across turns | ✔             | **PLD Runtime Layer**       |

PLD observes runtime signals and governs the stability loop:

> **Drift → Repair → Reentry → Continue → Outcome**

#### 🚫 What PLD Does **Not** Do

| Area                              | Owned by PLD? | Owner                       |
| --------------------------------- | ------------- | --------------------------- |
| Model inference                   | ❌             | Foundation model            |
| Tool execution                    | ❌             | Agent / orchestrator        |
| Memory strategy                   | ❌             | Framework or design pattern |
| Behavioral stability across turns | ✔             | **PLD Runtime Layer**       |

---

#### 🎯 Summary

PLD is a **governance and stabilization layer — not a replacement for frameworks or agents.**
It can be **added, removed, or run in observer-mode** without altering existing business logic.

```
If your agent already works — PLD helps it stay stable.
If your agent drifts — PLD makes the drift visible and recoverable.
```

---

## 🔌Integrations

Compatible with:

* LangGraph
* Assistants API
* Rasa
* Swarm
* Custom orchestration

Vendor-neutral — only a runtime behavioral contract.

🆕 **Observer-Mode Integration Example (Experimental)**
A minimal reference integration is available under:
`examples/langgraph_assistants/`
This example shows how PLD Runtime v2.0 can be attached to a LangGraph + OpenAI Assistants-style agent without modifying its behavior.
It demonstrates:

* PLD as a non-intrusive observer layer
* automatic emission of structured runtime events (`continue`, `drift`, `outcome`)
* JSONL logging via the Level-5 runtime (`RuntimeSignalBridge` + `RuntimeLoggingPipeline`)
* a simple lifecycle pattern: `init → emit → shutdown`

Try it:
`export OPENAI_API_KEY=your_key_here`
`python examples/langgraph_assistants/run.py`
Logs will appear in:
`logs/langgraph_pld_demo.jsonl`
Status: **Experimental — seeking evaluation feedback**.

---

### 📌 Current Phase

This repository is currently in an **Exploratory / Candidate Stage**.  
Components may evolve based on evaluation, implementation feedback, and research findings.

Feedback and field reports are welcome and help shape the next revision.

---

## 🤝 Contribution

Contributions welcome, especially:

* bridges & adapters
* traces / evaluation datasets
* runtime patterns and observability tools

See: `CONTRIBUTING.md`

---

## 📜 License & Attribution

| Scope                       | License    |
| --------------------------- | ---------- |
| Runtime & code              | Apache 2.0 |
| Documentation & methodology | CC BY‑4.0  |

Full details: `LICENSES/OVERVIEW.md`

---

## 🏷 Trademark Statement

“Phase Loop Dynamics” and “PLD” are names and identifiers associated with the work of **Kiyoshi Sasano** and are treated as common-law trademarks.  
Please follow the trademark policy when referring to or using these names:  
➡ `LICENSES/TRADEMARK_POLICY.md`

---

## 👤 Maintainer

**Maintainer:** Kiyoshi Sasano
© 2025 — All rights reserved where applicable.

---

> **PLD is behavioral infrastructure —
> it ensures alignment persists *across interaction*,
> not just at initialization.**
