---
path: SUMMARY.md
component_id: repo_summary
kind: doc
area: meta
status: stable
authority_level: 2
version: 2.0.0
license: Apache-2.0
purpose: High-level summary and navigation index for the PLD repository contents.
---

> A runtime governance model for stabilizing multi-turn LLM agents — making behavior measurable, recoverable, and repeatable across turns.

---

## Why PLD Exists

Multi-turn LLM agents rarely fail because they "don’t know" —  
they fail because behavior **drifts across turns**.

Without runtime governance, agents develop:

- cascading tool failures  
- hallucinated or unstable context  
- contradictory reasoning  
- silent misalignment with user intent  
- repeated retries without progress  

PLD provides a structured runtime loop that detects misalignment early, applies proportional repair, and verifies alignment before continuing.

```
Drift → Repair → Reentry → Continue → Outcome
```

---

## What PLD Is (and Is Not)

PLD is:

- a **runtime phase model** for stability  
- a method for detecting, repairing, and validating alignment  
- **observable and telemetry-driven**  
- implementation-agnostic — compatible with tool agents, retrieval systems, planners, and memory-based architectures  

PLD is **not**:

- a prompt template  
- a tuning trick  
- a static framework  
- a single metric or evaluation benchmark  

> PLD governs **how the agent behaves over time**, not how a single message is generated.

---

## Who Uses PLD

| Role | Why |
|------|------|
| Agent Engineers | Stability, fewer resets, repeatable behavior |
| UX & Conversation Design | Predictable visible repair and pacing |
| AgentOps / Evaluation Teams | Drift & repair signals mapped to telemetry |
| Applied ML / Research | Study alignment dynamics, not just accuracy |

---

## The Runtime Loop

| Phase | Purpose | Signals |
|-------|---------|---------|
| **Drift** | Detect divergence from shared state or constraints | tool errors, contradictions, missing constraints |
| **Repair** | Apply correction (soft → hard escalation) | clarification, reset, constraint restatement |
| **Reentry** | Confirm restored alignment | checkpoint summary, short acknowledgment |
| **Continue** | Resume execution | next valid step |
| **Outcome** | Resolve the interaction | complete / partial / failed / abandoned |

> Works with LangGraph, Assistants API, Rasa, Swarm, AutoGen, or custom orchestration.

---

## Repository Structure

```
/quickstart     — Learning path + implementation patterns (start here)
/pld_runtime    — Optional reference runtime
/docs           — Conceptual model + taxonomy
/analytics      — Benchmarks + evaluated traces
/field          — Operational adoption playbooks
```

A simplified conceptual map:

| Layer | Role |
|-------|------|
| Concept Model | `/docs` |
| Implementation Patterns | `/quickstart` |
| Runtime Reference | `/pld_runtime` |
| Evidence & Evaluation | `/analytics` |
| Operational Adoption | `/field` |

---

## Adoption Path

A recommended onboarding sequence:

1. Learn the lifecycle → `/quickstart/overview/`
2. Run the teaching runtime → `hello_pld_runtime.py`  
   → First behavioral intuition: Drift → Repair → Reentry → Continue
3. Run the real runtime engine → `run_minimal_engine.py`  
   → Verify ingestion, thresholds, and enforcement policy behavior
4. Apply drift/repair/reentry primitives → `/quickstart/operator_primitives/`
5. Use modular runtime patterns → `/quickstart/patterns/`
6. Implement runnable integration flows → `04_integration_recipes/`
7. Emit structured events → `/quickstart/metrics/`
8. Benchmark against traces → `/analytics/`
9. Apply operational metrics → `/docs/07_pld_operational_metrics_cookbook.md`  
   → Measure: **PRDR · REI · VRL · FR · MRBF**

> Adoption path moves from **concept → behavior → implementation → observability → operational stability.**

---

## Telemetry and Evidence

PLD is **telemetry-first**:

- events are logged every turn  
- signals map to schemas (`pld_event.schema.json`)  
- runtime is evaluated using operational metrics  
- dashboards measure whether repairs "stick" over time  

Evidence includes:

- MultiWOZ 2.4 (200 annotated dialogs)  
- tool-enabled agent traces  
- applied SaaS support cases  
- field PoCs  

---

## One Sentence Summary

> **PLD is a runtime governance model that stabilizes multi-turn LLM agents through structured drift detection, proportional repair, and confirmed reentry — making behavior measurable, recoverable, and operationally reliable.**

---

Maintainer: **Kiyoshi Sasano**  
License: **CC BY 4.0 (methodology)** • **Apache 2.0 (code)**  
Trademark usage governed by `LICENSES/TRADEMARK_POLICY.md`.




