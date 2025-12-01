# PLD Documentation Index (Applied-AI)
> Metrics support decision-making — they are not permanent KPIs.

This folder contains the core documentation required to understand, label, evaluate, and integrate **Phase Loop Dynamics (PLD)** into applied LLM systems, tool-based agents, and multi-turn orchestration workflows.

These documents serve as a **reference set**.  
They can be read in sequence or selectively depending on your goals—whether you're labeling transcripts, implementing runtime policies, or evaluating an agent's stability.

---

## 📘 How to Use This Folder

If you are new to PLD or implementing it for the first time, the following reading sequence may help:

| Step | File | Purpose |
|------|------|---------|
| **1** | `01_pld_for_agent_engineers.md` | Starting point — what PLD solves and how it applies to real systems. |
| **2** | `02_pld_drift_repair_reference.md` | Source of truth: Drift, Repair, Reentry codes used in runtime and analysis. |
| **3** | `06_pld_concept_reference_map.md` | High-level taxonomy relationships and conceptual overview. |
| **4** | `07_pld_operational_metrics_cookbook.md` | How to measure runtime behavior: PRDR, REI, VRL, and evaluation strategy. |
| **5** | `04_pld_labeling_prompt_llm.md` | Official prompt for machine-assisted labeling of transcripts and logs. |

> You may move between these documents based on your role—  
> engineering, research, UX, or evaluation.

---

## 🔄 After Core Reading: Where to Continue

| Category | Destination | Purpose |
|----------|------------|---------|
| Runtime integration | `/quickstart/operator_primitives/` | Add drift detection, repair, and reentry logic into a control loop. |
| Reference examples | `/quickstart/patterns/04_integration_recipes/` | See PLD applied to RAG, tools, memory, and orchestration. |
| Logging and evaluation | `/quickstart/metrics/` | Map runtime behavior into telemetry and dashboards. |
| Operational metrics | `/docs/07_pld_operational_metrics_cookbook.md` | Operational signals for release decisions, regression monitoring, and repair strategy evaluation. |
| Applied examples | `/analytics/multiwoz_2.4_n200/` | Explore annotated dialogues and pattern recognition. |

Optional but helpful:

📄 `architecture_layers.md` —  
A conceptual view of PLD as a layered runtime governance model.

---

## 📄 File Overview

| File | Status | Role |
|------|--------|------|
| `01_pld_for_agent_engineers.md` | Core | Conceptual + practical introduction. |
| `02_pld_drift_repair_reference.md` | Core | Source of truth for PLD event codes. |
| `06_pld_concept_reference_map.md` | Reference | Taxonomy relationships and model overview. |
| `07_pld_operational_metrics_cookbook.md` | Reference | Metrics framework (PRDR, VRL, REI). |
| `04_pld_labeling_prompt_llm.md` | Core | Machine-usable labeling template. |
| `architecture_layers.md` | Reference | Conceptual runtime architecture. |
| `model_diagram.md` | Reference | Visual model of runtime phases. |

---

## 📐 Documentation Principles

Core documents in this directory follow these principles:

- **Stable terminology** — values align with the official taxonomy file.  
- **No hidden synonyms** — code values remain single source of truth.  
- **Reverse compatibility** — deprecations are explicit, never silent.  
- **Consistent footer** — each file ends with:

```
Maintainer: Kiyoshi Sasano
```

---

## 🧩 Contribution Notes

Before adding or modifying documentation, consider:

| Question | Action |
|---------|--------|
| Does it change a code value or definition? | Update `02_pld_drift_repair_reference.md`. |
| Does it describe applied usage or implementation? | Check consistency with `01_pld_for_agent_engineers.md`. |
| Is it about labeling or automation? | Place near `04_pld_labeling_prompt_llm.md`. |
| Is it experimental or research-focused? | Place under `/research/` rather than core docs. |

---

## 📁 Directory Layout

```
docs/
  ├── README_docs.md        ← (this file)
  ├── 01_pld_for_agent_engineers.md
  ├── 02_pld_drift_repair_reference.md
  ├── 04_pld_labeling_prompt_llm.md
  ├── 06_pld_concept_reference_map.md
  ├── 07_pld_operational_metrics_cookbook.md
  ├── architecture_layers.md
  └── model_diagram.md
```

---

Maintainer: **Kiyoshi Sasano**



# Documentation Map

PLD documentation is structured by **Stability Levels**:

## 📚 For Readers & Learners
* **[`/concepts`](./concepts/)**: Start here. The "Why" and "What" of Drift & Repair.
* **[`/patterns`](./patterns/)**: Practical patterns for LLM prompts, UX, and System integration.

## 🏛️ For Architects (The Specs)
* **[`/specifications`](./specifications/)**: **Level 1–3**. The authoritative schema, semantics, and metrics definitions.

## 🛠️ For Contributors (The Implementation)
* **[`/architecture`](./architecture/)**: **Level 4–5**. Runtime design principles and internals.
* **[`/metrics`](./metrics/)**: Operational cookbooks and case studies.