
# 05 — PLD Applied AI Lexicon Mapping Guide  
_For Agent Developers, Evaluators, and Tool-Oriented Engineers_

Version: 1.0  
Maintainer: **Kiyoshi Sasano**  
Standard: PLD Applied Edition  
Lifecycle: Drift → Repair → Reentry → Resonance → Outcome

---

## 1. Purpose

This file ensures consistent terminology across:

- PLD schemas  
- evaluation reports  
- logging pipelines  
- LLM agent frameworks  
- UX timing patterns  
- repair automation  
- prompt and runtime policy enforcement  

It replaces past research terminology with a standardized, engineering-grade vocabulary.

> **Rule:** Terms behave like API contracts — not metaphors.

---

## 2. Canonical Concepts (Required Vocabulary)

These five terms define the PLD interaction cycle and must be used across all files, prompts, and logs.

| Interaction Stage | Canonical Label | Machine Namespace |
|------------------|----------------|------------------|
| Breakdown | **Drift** | `D*` |
| Corrective Action | **Repair** | `R*` |
| Return to Workflow | **Reentry** | `RE*` |
| Stabilization | **Resonance** | `resonance: true/false` |
| Result | **Outcome** | `OUT*` |

Example (valid assignment):

```json
{
  "drift": "D2_context",
  "repair": "R2_soft_repair",
  "reentry": "RE3_auto",
  "resonance": true,
  "outcome": "OUT1_complete"
}
```

---

## 3. Secondary Allowed Terms (Context Required)

These can be used only when mapped to canonical classes.

| Secondary Term | Mapping Rule | Example Mapping |
|---------------|--------------|----------------|
| Latency | Must map to Drift class | `D3_latency` |
| Clarification | Must map to Repair type | `R1_clarify` |
| Retry | Must specify repair level | `R3_hard_reset` |
| Confirmation | Must map to Reentry | `RE2_user_guided` |

Example (correct):

> “Latency Drift occurred → system triggered Soft Repair (Clarify) → Automatic Reentry restored flow.”

Incorrect:

> “It regained rhythm.”

---

## 4. Deprecated Terms (Remove in Applied Edition)

These terms originated in research materials and are no longer valid in implementation.

| Deprecated Term | Status | Replacement |
|-----------------|--------|-------------|
| Phase Boundary | ❌ remove | Drift / Workflow Transition |
| Field | ❌ remove | — |
| Structural Tension | ❌ remove | — |
| Latent Phase | ❌ remove | RE2_system_guided |
| Rhythm (as metaphor) | ⚠ allowed only as metric (“latency pacing”), not metaphor | Timing / Latency Interval |

If these appear in old files, annotate with:

```
@deprecated — replaced by PLD Applied taxonomy
```

---

## 5. Framework Mapping Tables

### 5.1 LangChain / Tool Execution

| LangChain Concept | PLD Mapping |
|-------------------|------------|
| Tool call error | D1_information |
| Wrong parameters | D2_context |
| Retry logic | R3_hard_reset |
| Memory validation | RE2_system_guided |

---

### 5.2 LangGraph / Runtime Flow

| LangGraph Feature | PLD Label |
|------------------|-----------|
| Interrupt / fallback branch | Drift detection |
| Recovery branch | Repair |
| Reset node | Hard Repair (R3) |
| Confirm intent node | Reentry trigger |

---

### 5.3 Rasa / Dialogue Pipelines

| Rasa Function | PLD Equivalent |
|--------------|----------------|
| Fallback intent | R3_hard_reset |
| Slot clarification | R1_soft_repair |
| Form repair | R2_soft_repair |

---

### 5.4 UX / Interaction Timing

| UX Artefact | PLD Equivalent |
|-------------|----------------|
| Typing indicator | Drift prevention (latency awareness) |
| Guided options | R2_soft_repair |
| Confirmation prompt | RE1_user_guided |

---

## 6. Enforcement Grammar

All machine-readable labels must follow this schema:

```
D* → Drift Type
R* → Repair Type
RE* → Reentry Type
RES → Stability Boolean
OUT* → Outcome Category
```

Invalid examples include:

- custom wording
- synonyms
- invented categories
- metaphoric labels

---

## 7. LLM-Safe Final Rule (Copy/Paste)

```
Use only these terms: Drift, Repair, Reentry, Resonance, Outcome.
Never invent new vocabulary.
Always label using the format: D*, R*, RE*, OUT*.
If unsure: classify using the closest available category.
```

---

## 8. File Status

This file **replaces and permanently archives**:

- `PLD_LEXICON_SAFE_USAGE_GUIDE.md`
- `PLD_Lexicon_Connectivity_Map.md`

It is now the **single active lexicon authority** for the Applied specification.

---

Maintainer: **Kiyoshi Sasano**  
Status: **ACTIVE — Required for compliance**