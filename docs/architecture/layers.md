# PLD Runtime Architecture (Layered Model)

This document defines the conceptual architecture behind Phase Loop Dynamics (PLD).  
While the runtime loop explains **what phases occur during interaction**, this layered model describes **how responsibility is distributed across the system** to maintain alignment over time.

It is a bridge between conceptual understanding and implementation — useful for design reviews, interoperability discussions, and system-level reasoning.

---

## Runtime Layer Stack

```
Signal Layer
        ↓
Analysis Layer
        ↓
Decision Layer
        ↓
Routing Layer
        ↓
Execution Layer
```

---

## Layer Definitions

| Layer | Responsibility | Typical Outputs |
|-------|---------------|----------------|
| **Signal Layer** | Detect anomalies, drift indicators, constraint violations, uncertainty signatures | Alerts, drift markers, repair candidates |
| **Analysis Layer** | Evaluate temporal and behavioral patterns across turns | Violation classifications, contextual interpretation |
| **Decision Layer** | Select correction strategy using policies, severity models, and operational mode | Action plans (soft repair, reset, escalate, confirm) |
| **Routing Layer** | Map strategy to concrete execution path (agent/human/tool/control boundary) | Route instructions |
| **Execution Layer** | Apply repair action and continue the runtime loop | Updated state, validated checkpoint, aligned continuation |

---

## Principles

- Layers define **responsibility boundaries**, not implementation modules.
- The mapping from layers → code is **implementation-dependent** and may vary across orchestrators (LangGraph, Assistants API, Rasa, Swarm, AutoGen, custom).
- Only three elements remain constant:
  - Shared vocabulary  
  - Runtime loop  
  - Behavioral observability

---

## Scope and Positioning

This file serves as a **reference architecture**, not a runtime specification.

✔ Useful for:

- Architecture planning  
- Cross-team alignment  
- Evaluation design  
- Debugging and Ops discussions  
- Research framing  

✘ Not intended as:

- A mandated API  
- A strict module structure  
- A required code layout  

---

## Relationship to Other Documentation

| Reference | Purpose |
|----------|---------|
| `/docs/model_diagram.md` | Runtime phase transitions (Drift → Repair → Reentry → Continue) |
| `/pld_runtime/` | Reference implementation components (optional for adoption) |
| `/field/` | Collaboration protocol, shared terminology enforcement |
| `/analytics/` | Evaluation traces and benchmarking methodology |

---

## Status

📌 Version: Reference Architecture  
📌 Stability: Mature (Conceptual)  
📌 Intended Use: Understanding, comparison, interoperability, research framing  

---

> PLD layers describe **how alignment governance operates inside a system —  
not how one specific system must be built.**
