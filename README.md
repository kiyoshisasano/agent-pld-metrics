# Phase Loop Dynamics™ (PLD) 
*A Runtime Phase Model for Stable Multi-Turn LLM Systems*

![License: Apache-2.0 | CC-BY-4.0](https://img.shields.io/badge/license-Apache%202.0%20%7C%20CC--BY--4.0-blue)
![Status: Active](https://img.shields.io/badge/status-active-brightgreen)

> PLD is not a framework or agent library.  
> It is a **runtime governance model** that stabilizes multi-turn LLM agents across **turns, tooling, models, and execution contexts.** 

---

## 🎯 Why PLD Exists

Multi-turn agents rarely fail because they *don't know something*—  
they fail because behavior becomes **unstable over time**.

Common patterns include:
- repeated tool calls without progress  
- hallucinated or unstable context  
- behavior shifts across models  
- drift that temporarily recovers, then returns  

PLD introduces a runtime behavioral contract:
```
Drift → Repair → Reentry → Continue → Outcome
```
This ensures alignment persists across turns — not just per isolated response.

---

## 🔁 The Runtime Loop

| Phase | Purpose | Example Signals |
|-------|---------|----------------|
| **Drift** | Detect misalignment | contradiction, tool failure |
| **Repair** | Soft → hard correction | clarification, boundary restatement |
| **Reentry** | Confirm alignment restored | checkpoint summary |
| **Continue** | Resume execution | next valid step |
| **Outcome** | End state | complete / partial / failed |

Visual summary:

<img src="./README_model.svg" width="100%" />
---

## ⚡ Quickstart — Run PLD in Under 10 Seconds

```bash
python quickstart/hello_pld_runtime.py
python quickstart/run_minimal_engine.py
python quickstart/metrics/verify_metrics_local.py
```
Next steps → `quickstart/README_quickstart.md`

---

## 🏛 Architecture: The PLD Level Model

| Level | Meaning | Folder |
|-------|---------|--------|
| **1 — Structure** | Canonical schema | `/docs/schemas/` |
| **2 — Semantics** | Event meaning, prefix-phase rules | `/docs/PLD_Event_Semantic_Spec_v2.0.md` |
| **3 — Operational Standards** | Metrics & taxonomy | `/docs/taxonomy/`, `/docs/metrics/` |
| **4 — Consumer Layer** | Examples & adoption | `/quickstart/` |
| **5 — Runtime Implementation** | Optional runtime engine | `/pld_runtime/` |

---

## 📂 Repository Guide
```
quickstart/     → start here
pld_runtime/    → runtime implementation
docs/           → specifications & conceptual core
analytics/      → datasets, evaluation, metrics
field/          → adoption and operational patterns
```
Full structure → `SUMMARY.md`
---

## 📈 Observability

Once structured events flow, the system becomes measurable:
- PRDR — Post-Repair Drift Recurrence  
- VRL — Visible Repair Load  
- MRBF — Mean Repairs Before Failover  
- FR — Failover Rate  

Metrics cookbook → `docs/07_pld_operational_metrics_cookbook.md`
---

## 🧪 When PLD Applies
✔ multi-turn  
✔ tools, planning, retrieval  
✔ recovery > latency

Less necessary when:  
⚠ single-turn  
⚠ fully deterministic

---

## 🔌 Integrations
Compatible with:
- LangGraph
- Assistants API
- Rasa
- Swarm
- Custom orchestration

Vendor-neutral — **only a runtime behavioral contract.**

---

### 📌 Current Phase

This repository is currently in an **Exploratory / Candidate Stage**.  
Components may evolve based on evaluation, implementation feedback, and research findings.

Feedback and field reports are welcome and help shape the next revision.

---


## 🌱 Community & Support

📣 Discussions: https://github.com/kiyoshisasano/agent-pld-metrics/discussions
🐛 Issues & tracking: https://github.com/kiyoshisasano/agent-pld-metrics/issues

---

## 🤝 Contribution

Contributions welcome, especially:
- bridges & adapters
- traces / evaluation datasets
- runtime patterns and observability tools

See: `CONTRIBUTING.md`

---

## 📜 License & Attribution

| Scope | License |
|--------|---------|
| Runtime & code | Apache 2.0 |
| Documentation & methodology | CC BY‑4.0 |

Full details: `LICENSES/LICENSES.md` 

---

## 🏷 Trademark Notice

"Phase Loop Dynamics" and "PLD" are claimed as common-law trademarks of **Kiyoshi Sasano**.  
Use of these marks is governed by the project's trademark policy:  
➡ `LICENSES/TRADEMARK_POLICY.md`

---

## 👤 Maintainer

**Maintainer:** Kiyoshi Sasano  
© 2025 — All rights reserved where applicable.

---

> **PLD is behavioral infrastructure —  
it ensures alignment persists *across interaction*,  
not just at initialization.**
