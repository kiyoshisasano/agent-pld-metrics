# PLD Labeling Prompt  
### (Applied-AI Edition — Fully Taxonomy-Aligned — GitHub Release)

This document defines the **official annotation prompt** for identifying Drift, Repair, and Reentry
events in interactive AI systems.

It is aligned with:

| Layer | Source |
|-------|--------|
| Taxonomy Authority | `docs/drift_repair_taxonomy.md` |
| Interaction Model | `docs/pld_applied_interaction_model.md` |
| Evaluation Standard | `metrics/multiwoz_2.4_n200/` |

This version is optimized for:

- LLM agent trace analysis  
- Tool execution logs  
- Task-oriented dialogue evaluation  
- Multi-agent orchestration workflows  
- Latency and pacing behavior auditing  

No HCI or conversation-analysis terminology is used.

---

## 1. Purpose of Annotation

Given a sequence of interaction turns (system responses, user input, and tool outputs), classify:

1. **Drift Type (D1–D5)**  
2. **Repair Type (R1–R4)**  
3. **Reentry Type (RE1–RE3)**  
4. Whether the task achieved **Outcome Completion**  
5. A short rationale explaining the decision  

This taxonomy enables:

- automated evaluation pipelines  
- agent debugging  
- human/LLM collaborative annotation  
- runtime interaction monitoring  
- reproducible benchmarks  

---

## 2. Drift Categories (D1–D5)

> Select **at most one** Drift category per annotated segment.

| Code | Name | Definition |
|------|------|------------|
| **D1 — Information Drift** | System contradicts prior facts, constraints, or tool results. (Examples: “no result” → later shows results, inconsistent DB state, hallucinated attributes.) |
| **D2 — Context Drift** | System loses or corrupts previously established context (missing slot, forgotten constraint, switching tasks unintentionally). |
| **D3 — Intent Drift** | System diverges from the user’s stated task or goal (domain switch, irrelevant response, changed plan without signal). |
| **D4 — Procedural Drift** | Workflow or sequence breakdown (looping planner, misordered tool calls, inconsistent multi-agent roles). |
| **D5 — Pacing / Latency Drift** | Timing disruption affecting responsiveness (long silence, confusing streaming, unacknowledged pause). |

If no drift occurs, set `"drift": "none"`.

---

## 3. Repair Categories (R1–R4)

> Repairs may occur **with or without** a detected Drift.

| Code | Name | Definition |
|------|------|------------|
| **R1 — Local Repair (Soft Repair)** | Minimal correction while keeping context intact — clarify, retry a tool with corrected arguments, offer options, restore missing detail verbally. |
| **R2 — Structural Repair** | Internal or workflow-level correction — restoring memory, synchronizing tool results, fixing planner/executor mismatch. |
| **R3 — UX Repair** | Repair via pacing, acknowledgments, or user reassurance — “still checking…”, gradual disclosure, timing stabilization. |
| **R4 — Hard Repair (Restart / Reset)** | Explicit reset when state is unrecoverable — context discard and restart. |

If no repair occurs, set `"repair": "none"`.

---

## 4. Reentry Categories (RE1–RE3)

> Reentry indicates the system is back on task following Drift or Repair.

| Code | Name | Definition |
|------|------|------------|
| **RE1 — Intent Reentry** | User or system explicitly returns to the original task. |
| **RE2 — Constraint Reentry** | Previously supplied constraints or requirements are restored or re-validated. |
| **RE3 — Workflow Reentry** | The workflow stabilizes and resumes the intended execution sequence. |

If no reentry occurs, use `"reentry": "none"`.

---

## 5. Required Output Format

All responses must follow **this exact schema**:

```json
{
  "drift": "D2_context_drift",
  "repair": "R1_local_repair",
  "reentry": "RE3_workflow_reentry",
  "outcome_complete": false,
  "rationale": "The system ignored a previously stated constraint, performed clarification, and workflow resumed implicitly."
}
```

### Allowed Values Summary

| Field | Accepted Values |
|-------|----------------|
| `drift` | `"none"` or `D1–D5` |
| `repair` | `"none"` or `R1–R4` |
| `reentry` | `"none"` or `RE1–RE3` |
| `outcome_complete` | `true` / `false` |
| `rationale` | short natural-language justification |

---

## 6. Full Prompt (Copy-Paste-Ready)

```
You are an expert annotator for interactive AI system logs.

Classify the interaction using the PLD Applied-AI scheme.

Identify:
- Drift type (D1–D5)
- Repair type (R1–R4)
- Reentry type (RE1–RE3)
- Outcome completion
- A short rationale

### Drift
D1 Information  
D2 Context  
D3 Intent  
D4 Procedural  
D5 Pacing/Latency  

### Repair
R1 Local (Soft Repair)  
R2 Structural  
R3 UX Repair  
R4 Hard Repair (Restart/Reset)  

### Reentry
RE1 Intent  
RE2 Constraint  
RE3 Workflow  

### Output Format (JSON only)

{
  "drift": "D2_context_drift",
  "repair": "R1_local_repair",
  "reentry": "RE3_workflow_reentry",
  "outcome_complete": false,
  "rationale": "..."
}

Respond ONLY with the JSON. Do not include commentary outside the JSON.
```

---

## 7. Annotation Rules

- Drift may occur without repair.  
- Repair may occur without drift.  
- Reentry requires a return to the objective, not just a continued conversation.  
- If multiple choices apply, select the category with the **highest structural impact**.  
- Information Drift (D1) should always be checked when tool outputs contradict system statements.

---

## 8. Repository Placement

```
docs/labeling_prompt.md
```

---

## 9. Version

PLD Applied-AI Edition  
Taxonomy-Aligned Release  
2025-11 
Maintainer: DeepZenSpace
