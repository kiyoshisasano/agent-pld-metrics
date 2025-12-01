---
title: "Runtime Policy Patterns — PLD System Layer"
version: 2025.1
status: stable
maintainer: "Kiyoshi Sasano"
category: "patterns/system"
tags:
  - PLD
  - policy engine
  - safety
  - orchestration
  - runtime state control
---

# ⚙️ Runtime Policy Patterns (System Layer)

This document defines **operational decision rules** used by agents running a PLD-aligned control loop.

Unlike **LLM phrasing (01_llm)** or **UX tone (02_ux)**, these policies determine:

- when drift triggers repair,  
- when retries escalate,  
- when failover is allowed,  
- and when the system returns to stability.

These rules are designed to align with:

| Reference | Alignment |
|----------|-----------|
| `pld_event.schema.json` | event representation |
| `metrics_schema.yaml` | PRDR / FR / VRL tracking |
| `dashboards/reentry_success_dashboard.json` | operational monitoring |
| integration in LangGraph / Assistants API / Rasa | execution runtime |

---

## 1. PLD System Phases and Decision States

| Phase | Entry Trigger | Exit Condition | Expected Action |
|-------|--------------|----------------|----------------|
| `drift` | unexpected content / latency stall / tool failure | repair triggered | classify & confirm |
| `repair` | repair rule selected | reentry attempt completes | retry or escalate |
| `reentry` | post-repair turn | alignment confidence ≥ threshold | continue or fallback |
| `continue` | stable execution | new drift observed | proceed normally |
| `failover` | escalation ceiling reached | alternative route available | reset, human handoff, or bail |
| `complete` | task finished | — | close session |

The runtime must treat these as **state machine transitions**, not loose behaviors.

---

## 2. Drift → Repair Trigger Thresholds

A repair is triggered when **any** of the following evaluations score above their threshold:

| Signal Class | Examples | Threshold Policy |
|--------------|----------|-----------------|
| Semantic mismatch | incorrect facts, mis-routed intent | `drift_confidence ≥ 0.50` |
| Execution failure | tool timeout, missing data | always triggers (no threshold) |
| Latency stall | response latency ≥ p95 boundary | `≥ 2 repeated stalls` |
| UX friction | visible repairs already present (VRL rising) | dynamic threshold (see below) |

📌 Dynamic Rule:

```
---
title: "Runtime Policy Patterns — PLD System Layer"
version: 2025.1
status: stable
maintainer: "Kiyoshi Sasano"
category: "patterns/system"
tags:
  - PLD
  - policy engine
  - safety
  - orchestration
  - runtime state control
---

# ⚙️ Runtime Policy Patterns (System Layer)

This document defines **operational decision rules** used by agents running a PLD-aligned control loop.

Unlike **LLM phrasing (01_llm)** or **UX tone (02_ux)**, these policies determine:

- when drift triggers repair,  
- when retries escalate,  
- when failover is allowed,  
- and when the system returns to stability.

These rules are designed to align with:

| Reference | Alignment |
|----------|-----------|
| `pld_event.schema.json` | event representation |
| `metrics_schema.yaml` | PRDR / FR / VRL tracking |
| `dashboards/reentry_success_dashboard.json` | operational monitoring |
| integration in LangGraph / Assistants API / Rasa | execution runtime |

---

## 1. PLD System Phases and Decision States

| Phase | Entry Trigger | Exit Condition | Expected Action |
|-------|--------------|----------------|----------------|
| `drift` | unexpected content / latency stall / tool failure | repair triggered | classify & confirm |
| `repair` | repair rule selected | reentry attempt completes | retry or escalate |
| `reentry` | post-repair turn | alignment confidence ≥ threshold | continue or fallback |
| `continue` | stable execution | new drift observed | proceed normally |
| `failover` | escalation ceiling reached | alternative route available | reset, human handoff, or bail |
| `complete` | task finished | — | close session |

The runtime must treat these as **state machine transitions**, not loose behaviors.

---

## 2. Drift → Repair Trigger Thresholds

A repair is triggered when **any** of the following evaluations score above their threshold:

| Signal Class | Examples | Threshold Policy |
|--------------|----------|-----------------|
| Semantic mismatch | incorrect facts, mis-routed intent | `drift_confidence ≥ 0.50` |
| Execution failure | tool timeout, missing data | always triggers (no threshold) |
| Latency stall | response latency ≥ p95 boundary | `≥ 2 repeated stalls` |
| UX friction | visible repairs already present (VRL rising) | dynamic threshold (see below) |

📌 Dynamic Rule:

```
if VRL > 15%:
require higher confidence to trigger visible repairs
prefer silent or micro-repair forms
```


---

## 3. Escalation Strategy

Repairs must follow a **bounded retry ladder**.

```
Soft Repair → Directed Repair → Hard Repair → Failover
```


### Escalation Thresholds

| Stage | Condition to Enter | Max Attempts | Example Behavior |
|-------|--------------------|--------------|------------------|
| Soft Repair | first drift or low severity | 2 attempts | clarification, option expansion |
| Directed Repair | drift repeats within 3 turns (PRDR window) | 1 attempt | explicit correction + constraint |
| Hard Repair | MRBF risk or repeated recovery failure | 1 attempt | state reset, tool retry |
| Failover | all prior repairs fail | — | abort task, handoff, or fallback workflow |

---

## 4. Reentry Evaluation Logic

Reentry is successful when **alignment confidence surpasses minimum safe criteria**:

```
confidence >= 0.7
AND
no new drift in the next 1–2 turns
```


If drift recurs within **PRDR window (default: 3 turns)**:

> classify as **recurrence failure** and escalate one tier.

---

## 5. Failover Rules (FR Policy)

Failover exists to **prevent visible looping** and protect user trust.

Fail when any of the following hold true:

| Condition | Trigger |
|----------|---------|
| Repair attempts ≥ configured MRBF ceiling | default: `≥ 4` |
| Reentry attempts fail twice consecutively | strong indicator of persistent drift |
| Tool self-consistency breaks | repeated tool-model contradiction |
| UX friction > critical (VRL > 25%) | perceived instability |

Failover must emit a **structured event**:

```json
{
  "event_type": "failover_triggered",
  "pld": { "phase": "failover", "code": "OUT2_recovery_failure" },
  "runtime": { "repair_attempts": 4 }
}
```

---

## 6. Repair Tone Selection (System-Level)

Runtime selects **repair language mode** based on UX state:

| VRL Level | Tone Strategy                                                       |
| --------- | ------------------------------------------------------------------- |
| `0–5%`    | Confident, minimal repair confirmation                              |
| `5–20%`   | More explicit confirmation phrasing                                 |
| `>20%`    | Reduce visible repair frequency; prefer silent or compressed repair |

This guarantees UX consistency even across diverse orchestration engines.

---

## 7. Configuration Defaults

| Parameter                               | Default | Notes |
| --------------------------------------- | ------- | ----- |
| `soft_repair_attempts_max`              | `2`     |       |
| `directed_repair_attempts_max`          | `1`     |       |
| `hard_repair_attempts_max`              | `1`     |       |
| `prdr_window_turns`                     | `3`     |       |
| `min_reentry_confidence`                | `0.70`  |       |
| `failover_mrbf_ceiling`                 | `4`     |       |
| `visible_repair_throttle_vrl_threshold` | `15%`   |       |

These may be adjusted per domain.

---

## 8. Implementation Checklist

☑ State machine implemented
☑ Drift confidence model connected
☑ Repair escalation ladder enforced
☑ Logging fully schema-compliant
☑ Failovers observable in monitoring (FR tile)
☑ VRL adaptive phrasing policy integrated

---

📌 Summary

> Runtime policy determines when the system intervenes, escalates, or gives up —
> ensuring behavior remains aligned with PLD stability metrics.
