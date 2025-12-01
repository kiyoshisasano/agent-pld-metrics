# PLD Drift–Repair Reference (Applied-AI Dictionary)

> **Purpose:** This is the canonical reference for all PLD codes used in:  
> labeling, metrics, runtime detection, auditing, and dataset annotation.

> **Scope:** Defines allowed values, required meanings, and example patterns.  
No theory, no interpretation — **just definitive ground truth.**

---

## 1. Drift Codes (D-Series)

A **drift event** means:  
> The system deviates from expected meaning, constraints, workflow, or pacing.

Only **one primary drift type** may be assigned per segment.

---

### **D1 — Information Drift**

**Definition:**  
System output contradicts available facts, tool results, or previously established truth.

| Field | Value |
|-------|-------|
| JSON Value | `"D1_information_drift"` |

**Detection Conditions:**

- DB/API returns X → system states Y  
- Model states "no result" → later acknowledges existing result  
- Factual inconsistency inside the same session  

**Example:**

> "There are no available 4-star hotels."  
> *(Later)*  
> "Here are two 4-star hotels."

---

### **D2 — Context Drift**

**Definition:**  
Loss or misuse of previously established context or constraints.

| Field | Value |
|-------|-------|
| JSON Value | `"D2_context_drift"` |

**Detection Conditions:**

- Missing constraints  
- Replaced slot value without justification  
- Misinterpreted previous user turn  

**Example:**

> User: "I need vegan options."  
> System: "Here are steakhouse recommendations."

---

### **D3 — Intent Drift**

**Definition:**  
The system shifts task direction or goal without user signal.

| Field | Value |
|-------|-------|
| JSON Value | `"D3_intent_drift"` |

**Detection Conditions:**

- Task domain switches  
- New plan proposed without context  
- System decides unrelated sub-task  

**Example:**

> User: "Book a hotel."  
> System: "Would you like to compare train tickets instead?"

---

### **D4 — Procedural Drift**

**Definition:**  
System diverges from expected workflow sequence or operational role.

| Field | Value |
|-------|-------|
| JSON Value | `"D4_procedural_drift"` |

**Detection Conditions:**

- tool-call repetition  
- missing postconditions  
- planner → executor confusion  
- execution loop without progress  

**Example:**

> Tool executed successfully, but planner retries anyway.

---

### **D5 — Pacing / Latency Drift**

**Definition:**  
Timing behavior creates confusion, expectation mismatch, or trust loss.

| Field | Value |
|-------|-------|
| JSON Value | `"D5_latency_drift"` |

**Detection Conditions:**

- silent delay without indicator  
- abrupt response pacing break  
- streaming stops prematurely  

**Example:**

> (15s silence)  
> System: "…so anyway—"

---

## 2. Repair Codes (R-Series)

A **repair event** indicates:  
> The system performs an explicit attempt to resolve a drift.

Zero or multiple repairs may occur across a session, but only **one repair per labeled segment.**

---

### **R1 — Local Repair**

**Definition:**  
Minor correction without modifying global structure or resetting context.

| Field | Value |
|-------|-------|
| JSON Value | `"R1_local_repair"` |

**Includes:**

- clarification  
- adding missing details  
- retrying tool call with corrected argument  

---

### **R2 — Structural Repair**

**Definition:**  
Fixing internal state: workflow, memory, slot values, constraint restoration.

| Field | Value |
|-------|-------|
| JSON Value | `"R2_structural_repair"` |

**Includes:**

- restoring lost parameters  
- synchronizing belief state with tool output  
- re-aligning planner/executor roles  

---

### **R3 — UX Repair**

**Definition:**  
Stabilizing pacing, timing, or feedback for perceived continuity.

| Field | Value |
|-------|-------|
| JSON Value | `"R3_ux_repair"` |

**Includes:**

- “still working…”  
- progressive disclosure  
- safe filler responses  

---

### **R4 — Hard Repair (Reset)**

**Definition:**  
Discarding current context and restarting workflow intentionally.

| Field | Value |
|-------|-------|
| JSON Value | `"R4_hard_repair"` |

**Includes:**

- “Let’s restart.”  
- memory clear  
- reinitialization  

---

## 3. Reentry Codes (RE-Series)

A **reentry event** occurs when a conversation returns to the intended workflow after drift/repair.

---

### **RE1 — Intent Reentry**

| Field | Value |
|-------|-------|
| JSON Value | `"RE1_intent_reentry"` |

**Meaning:**  
User explicitly restores the original goal.

**Example:**  
> “Let’s go back to booking the hotel.”

---

### **RE2 — Constraint Reentry**

| Field | Value |
|-------|-------|
| JSON Value | `"RE2_constraint_reentry"` |

**Meaning:**  
Previously stated parameters are restored.

**Example:**  
> "Right — a 4-star hotel under £100."

---

### **RE3 — Workflow Reentry**

| Field | Value |
|-------|-------|
| JSON Value | `"RE3_workflow_reentry"` |

**Meaning:**  
System automatically resumes task progression after correction.

**Example:**  
> (repair applied) → continues booking.

---

## 4. Special Values

| Field | Case | JSON Value |
|-------|------|------------|
| Drift not present | `"none"` | `"none"` |
| Repair not present | `"none"` | `"none"` |
| Reentry not applicable | `"none"` | `"none"` |

---

## 5. Machine-Readable Table Reference

Use this for schema mapping:

```json
{
  "drift": ["none", "D1_information_drift", "D2_context_drift", "D3_intent_drift", "D4_procedural_drift", "D5_latency_drift"],
  "repair": ["none", "R1_local_repair", "R2_structural_repair", "R3_ux_repair", "R4_hard_repair"],
  "reentry": ["none", "RE1_intent_reentry", "RE2_constraint_reentry", "RE3_workflow_reentry"]
}
```

---

## 6. File Placement

```
docs/02_pld_drift_repair_reference.md
```

---

## 7. Version

Applied-AI Edition  
Updated: 2025-02  
Maintainer: Kiyoshi Sasano