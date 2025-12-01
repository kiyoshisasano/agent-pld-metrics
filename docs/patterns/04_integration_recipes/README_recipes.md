---
title: "Integration Recipes Index"
version: "1.1"
status: "Entry Point"
maintainer: "Kiyoshi Sasano"
updated: "2025-01-15"
visibility: "Public"
scope: "Quickstart — Practical Implementation Patterns"
---

# Integration Recipes (PLD Applied)

> **If you're here directly:**  
> A commonly used entry path is:

```
/quickstart/README_quickstart.md → /patterns/README_patterns.md → (this folder)
```



These recipes demonstrate how the **PLD runtime loop** can be applied to real agent components and orchestration layers.

They are **reference implementation patterns** — not tutorials — designed to show how PLD behaviors may appear in applied environments.

---

## Framework Context

⚠️ **These recipes use LangGraph for demonstration purposes.**

PLD itself is **framework-agnostic**.  
The same integration concepts can apply to:

- OpenAI Assistants API
- AutoGen / CrewAI
- Rasa
- Swarm
- Custom orchestrators or step-based policy controllers

LangGraph is used here because it provides a modular structure suitable for illustrating the runtime loop.

---

## 2 — Available Recipes

Recipes are grouped into two functional tiers:

> **Tier 1 → Component Patterns (Stabilize each subsystem)**  
> **Tier 2 → System Pattern (Assemble components into a governed runtime)**

---

### **Tier 1 — Component Patterns (Building Blocks)**

These recipes make individual subsystems **PLD-aware and recoverable.**

| File | Component | Operational Drift Type | PLD Pattern Illustrated |
|------|-----------|------------------------|-------------------------|
| `rag_repair_recipe.md` | Retrieval | `D5_information` | Detect and repair retrieval failure without hallucination amplification |
| `tool_agent_recipe.md` | Tool Execution | `D4_tool` | Structured response to invalid/failed tool calls with retry logic |
| `memory_alignment_recipe.md` | Memory | `D2_context` | Detect and repair misaligned state, constraints, persona, or intent |

> These modules help stabilize single components — they do *not* yet form a full runtime agent.

---

### **Tier 2 — System Pattern (Capstone)**

This tier shows **how PLD components behave when orchestrated as a runtime system rather than isolated techniques**.

| File | System Role | Drift Focus | Integration Focus |
|------|-------------|-------------|-------------------|
| `reentry_orchestration_recipe.md` | **Orchestrator** | `RE* orchestration` | Routing after repair: continue, retry, fallback, or exit |
| `failover_recipe.md` | **Failover policy** | `D4_tool → bounded retry` | Controlled abort/fallback to prevent infinite repair loops |

> 📌 If **Tier 1 = parts**, then **Tier 2 = the operational control plane.**  
> `failover_recipe.md` formalizes the **termination behavior** of the PLD loop.

---

## 3 — Suggested Adoption Sequence

```
langgraph_example.md  
        ↓
rag_repair_recipe.md  
        ↓  
tool_agent_recipe.md  
        ↓  
memory_alignment_recipe.md  
        ↓  
reentry_orchestration_recipe.md  ← (capstone)
```

This sequence reflects a pattern frequently seen in real engineering teams:

🔹 First stabilize individual failure modes →  
🔹 Then enable centralized governance.

(Your order may vary depending on priorities and architecture.)

---

## 4 — Maturity Mapping (Aligned with `07_cookbook`)

| Level | Capability | Achieved After |
|-------|------------|----------------|
| **1 — Detect** | Drift signals emitted (`D*`) | After first recipe |
| **2 — Repair** | Soft/hard repairs executed (`R*`) | After Tier 1 |
| **3 — Reentry** | Controlled continuation (`RE*`) | After Tier 2 |
| **4 — Monitor** | Stability observable w/ PRDR / VRL / REI | After operational instrumentation |

---

## 5 — Before Extending

Review:

- `/docs/06_pld_concept_reference_map.md`
- `/docs/07_pld_operational_metrics_cookbook.md`
- `/quickstart/_meta/MIGRATION.md`

This supports:

- Consistent taxonomy (`D*`, `R*`, `RE*`, `OUT*`)
- Alignment with runtime governance semantics
- Measurability across deployments

---

## Final Note

> These patterns are **reference implementations — not prescriptive recipes.**  
> Adapt them based on your domain complexity, reliability targets, latency constraints, and UX requirements.

If your implementation demonstrates measurable stability improvements (typically across ≥200 turns), contributions are welcome.

Maintainer: **Kiyoshi Sasano**
