---
title: "Failover & Recovery Flows — PLD System Layer"
version: 2025.1
status: stable
maintainer: "Kiyoshi Sasano"
category: "patterns/system"
tags:
  - PLD
  - failover
  - recovery
  - runtime policies
  - escalation
---

# 🚨 Failover & Recovery Flows

Failover exists to protect **trust, stability, and pacing** when an agent becomes unreliable or stuck in repeated repair loops.

A well-designed failover system should:

- **prevent infinite repair cycles**
- provide a **graceful UX handoff**
- preserve necessary state for analysis
- ensure the next attempt (or user) does not repeat the pattern blindly

Failover is **not an error** — it is a **controlled exit condition** of the PLD loop.

---

## 1. When Should Failover Activate?

Failover triggers when the system determines recovery is unlikely.

### Activation Rules (Any Condition)

| Condition | Example Signal | Source |
|----------|----------------|--------|
| 📌 MRBF exceeded | `mean repairs before failover >= 4` | metrics schema |
| 📌 Reentry failures repeat | `RETRY → REENTRY → DRIFT (repeat)` | runtime logs |
| 📌 Tool conflict persists | model vs tool mismatch | integration runtime |
| 📌 High UX friction | `VRL > 25%` (visible repair overload) | user-facing telemetry |
| 📌 Latency collapse | repeated ≥ p95 turnaround thresholds | pacing analysis |

Failover must be **deterministic and bounded**, not subjective.

---

## 2. Failover State Flow

```java
         ┌─────────────────────────────────┐
         │   DRIFT DETECTED (D*)          │
         └───────────────┬────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   REPAIR ATTEMPTS  │
              └───────┬────────────┘
                      │
          repair success? ──► YES ──► REENTRY
                      │
                      ▼
              ┌─────────────────────┐
              │  ESCALATION LADDER │
              │ Soft → Directed → Hard │
              └───────┬─────────────┘
                      │ max attempts reached?
                      ▼
           ┌────────────────────────────┐
           │        FAILOVER            │
           └─────────────┬─────────────┘
                         │
                         ▼
           ┌────────────────────────────┐
           │   RECOVERY PATH SELECTOR   │
           └────────────────────────────┘
```

---

## 3. Recovery Path Types

Failover does **not always mean abandon** — it selects a recovery path.

| Recovery Path | When It Applies | Example Action |
|---------------|----------------|----------------|
| 🔁 **Reset with memory preserved** | task ambiguous or conflicting | “Let’s restart from step 1 with constraints applied.” |
| 🧹 **Soft restart (partial wipe)** | recent turns toxic or corrupted | “Resetting context and continuing.” |
| 🚪 **Safe abandonment** | user no longer benefits | “I couldn’t resolve this — would you like alternatives?” |
| 🧑‍💻 **Human / Operator handoff** | high-stakes or regulated domain | Route to support agent |

Each must be logged as a structured event:

```json
{
  "event_type": "failover_triggered",
  "pld": {
    "phase": "failover",
    "code": "OUT3_abandoned",
    "confidence": 0.98
  },
  "runtime": {
    "repair_attempts": 4,
    "reason": "repair_ceiling_exceeded"
  }
}
```

---

## 4. UX Requirements During Failover

A failover response should be:

| Attribute      | Required? | Notes                             |
| -------------- | --------- | --------------------------------- |
| Transparent    | ✔         | User must know a failure occurred |
| Short          | ✔         | Avoid additional friction         |
| Forward-moving | ✔         | Always propose a next step        |
| Neutral tone   | ✔         | Avoid apologizing repeatedly      |

Example phrasing:
> “It looks like my last attempts didn’t resolve things.
> I can restart, clarify the request, or hand off to a human — which do you prefer?”

---

## 5. Automatic Retry Policy (Optional)
In some systems, failover may allow **one automated reset-retry cycle**:
```scss
FAILOVER → RESET → RETRY → (evaluate)
```

Enable only when:
- user intent is explicit
- errors were caused by ephemeral instability
- retry success rate > 50% historically (tracked in REI/PRDR)

📌 This retry must not include visible looping behavior.

---

## 6. Post-Failover Telemetry Requirements
Failover must emit **all three**:

| Required Log Type     | Example                                     |
| --------------------- | ------------------------------------------- |
| Raw event log         | `"event_type": "failover_triggered"`        |
| Session-level metrics | updated FR, MRBF values                     |
| Recovery audit trail  | path taken: restart / abandonment / handoff |

This ensures dashboards like:
PRDR | REI | VRL | MRBF | FR

remain accurate.

---

## 7. Validation Checklist

☑ Failover threshold configurable
☑ Escalation ladder enforced
☑ Recovery path deterministic
☑ Visible repair suppression active during failover
☑ Proper logging aligned with schema
☑ UI/UX text consistent with patterns in 02_ux/
☑ Metrics update reflected in FR and MRBF tiles

---

## Summary

> Failover is a **governance control**, not an error state.
> It protects users from instability and restores a predictable experience.
