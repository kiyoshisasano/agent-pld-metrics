---
title: "PLD Patterns — Runtime Behavior Guide"
version: 1.1
maintainer: "Kiyoshi Sasano"
status: stable
category: behavioral_patterns
tags:
  - PLD
  - conversational agents
  - repair patterns
  - reentry patterns
  - applied AI design
  - telemetry-driven runtime behavior
---

# 🧩 PLD Patterns — Runtime Behavior Guide

This directory provides the **practical behavior layer** of the Phase Loop Dynamics (PLD) framework.

Where the metrics system defines **what is measured**,  
patterns define **how an agent behaves** when drift, repair, and reentry conditions occur.

> In this edition, patterns are now **telemetry-driven** — meaning runtime behavior is instrumented, measurable, and actionable.

---

## 📌 Pattern Layer Structure

```txt
quickstart/patterns/
│
├── 01_llm/                  ← Model-side consistency & corrective behavior
├── 02_ux/                   ← Repair phrasing, pacing, visible alignment cues
├── 03_system/               ← Runtime orchestration, thresholds, failover logic
│   └── implementation_guides/  ← Framework bindings (LangGraph, Assistants API, Rasa)
└── 04_integration_recipes/  ← Applied, domain-level templates (RAG, tools, memory, etc.)
```

Patterns are layered intentionally:

| Layer                   | Role                                                     | When to Apply              |
| ----------------------- | -------------------------------------------------------- | -------------------------- |
| **LLM patterns**        | Ground reasoning and avoid divergence                    | Before user-facing testing |
| **UX patterns**         | Make repairs visible and non-jarring                     | During prototyping         |
| **System patterns**     | Enforce guardrails, failover logic, and runtime policies | Pre-production             |
| **Integration recipes** | Bind patterns into real frameworks                       | Production rollout         |

---

## 🔄 Mapping Patterns to the PLD Runtime Loop

PLD patterns drive behavior during the **runtime lifecycle**:
```java
User Turn
   ↓
Drift Detection (D1–D5)
   ↓
Soft/Hard Repair (R1–R4)
   ↓
Reentry (RE1–RE3)
   ↓
Outcome / Continue
```

| Phase                     | Primary Patterns                       |
| ------------------------- | -------------------------------------- |
| Drift Detection + Control | `01_llm`                               |
| Repair (Soft → Hard)      | `01_llm` + `02_ux`                     |
| Reentry Stabilization     | `02_ux` + `03_system`                  |
| Outcome / Failover        | `03_system` + `04_integration_recipes` |

---

## 📏 Standards Alignment

Patterns integrate with the measurement and governance layer:
| Component            | Reference                                                      |
| -------------------- | -------------------------------------------------------------- |
| Event Schema         | `quickstart/metrics/schemas/pld_event.schema.json`             |
| Derived Metrics      | `quickstart/metrics/schemas/metrics_schema.yaml`               |
| Dashboards           | `quickstart/metrics/dashboards/reentry_success_dashboard.json` |
| Operational Cookbook | `docs/07_pld_operational_metrics_cookbook.md`                  |
| Logging Baseline     | `03_system/logging_and_schema_examples.md`                     |

> Every pattern must be measurable — **if it cannot be logged, it cannot be governed**.

---

## 🎯 What These Patterns Solve

Without structured runtime behavior, agents exhibit:

- Silent corrections
- nmeasurable drift behavior
- Repeated loop failures
- UX instability under latency or tool calls

With patterns applied:

| Property      | Result                                          |
| ------------- | ----------------------------------------------- |
| Detectable    | Drift is surfaced and classified                |
| Corrective    | Repair strategies are proportional              |
| Recoverable   | Reentry stabilizes and avoids looping           |
| Communicative | User-facing phrasing is predictable and bounded |
| Governable    | Metrics → Policy → Runtime tuning feedback loop |

---

## 🧪 Usage Workflow

| Phase         | Task                                   | Folder                    |
| ------------- | -------------------------------------- | ------------------------- |
| Prototype     | Apply model-side patterns              | `01_llm/`                 |
| UX Validation | Add visible repair phrasing + pacing   | `02_ux/`                  |
| Stabilization | Add system policies and failover logic | `03_system/`              |
| Deployment    | Bind patterns to runtime frameworks    | `04_integration_recipes/` |

---

## 📝 Minimal Binding Model

```text
User turn
  → Drift check
     → (If drift) Apply LLM repair pattern
     → Surface visible repair (UX pattern)
     → Reentry stabilization (system policy)
     → Log event
     → Continue
```
In production:
```text
Runtime behavior → Logging → Derived metrics → Dashboard → Policy revision → Updated patterns → Rerun
```
Closed-loop governance.

---

## 🧱 Version Stability Rules
Patterns evolve when metrics show degradation:

| Trigger                              | Requires Pattern Revision |
| ------------------------------------ | ------------------------- |
| Reentry success drops                | Yes                       |
| VRL increases beyond baseline        | Yes                       |
| Hard repair exceeds soft repair rate | Yes                       |
| Drift category distribution shifts   | Yes                       |

Patterns are **living artifacts**, not static documentation.

---

## License

Creative Commons — **CC BY 4.0**
© 2025 — KyoshiSasano

> **Patterns operationalize PLD — turning behavior into a measurable, repeatable system**.

> **Patterns turn PLD from a theory into a repeatable behavior system**.


