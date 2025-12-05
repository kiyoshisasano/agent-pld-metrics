<!--
component_id: governance_legacy
kind: doc
area: meta
status: stable
authority_level: 5
purpose: Legacy examples of anti-patterns for governance and runtime behavior.
-->

# Business-Facing Summary (for Non-Technical Stakeholders)

This document explains the most common failure modes (“anti-patterns”) that appear when teams begin using PLD. You do not need deep technical knowledge to understand these examples. Each anti-pattern highlights a recognizable behavioral mistake—such as skipping verification or looping apologies—and connects it to the correct PLD interpretation (Drift, Repair, Reentry).

Use this document to:

* Identify problematic agent behavior during early PoCs
* Understand which part of the PLD lifecycle is being violated
* Align teams on why certain behaviors lead to instability
* Apply the correct fix by restoring the PLD loop

These anti-patterns help engineers, PMs, QA reviewers, and partner teams quickly diagnose issues without reading the full PLD specification. They serve as a shared vocabulary for spotting and correcting unstable behavior.

---

# PLD Anti-Patterns

**Status:** Stable (Level 5 Governance Guidance)

These anti-patterns represent common violations of the **Normative Triad**:

* **Level 1 — Structure**
* **Level 2 — Semantics (Lifecycle)**
* **Level 3 — Taxonomy / Standards**

This v2-aligned version categorizes anti-patterns by lifecycle phase, corrects taxonomy codes, and clarifies expected PLD event sequences.

Use this document during PoC Reviews, Debug Sessions, and Compliance Audits.

---

## 1. How to Use This Document

1. Identify the observed behavior.
2. Map it to the violated PLD level:

   * L2: incorrect phase loop
   * L3: wrong/missing taxonomy code
   * L1: structurally invalid events
3. Apply the correct lifecycle fix.
4. Log the appropriate **D*** and **R*** codes to improve reproducibility.

---

# Category A — Drift Detection Failures

## ❌ A1 — Silent Failure (Missed D2_context)

**Symptom:**
The system confidently continues despite having lost track of tool state or conversation context.

**Violation:** Level 2 — Drift was not detected (missing `D2_context`).

**Root Cause:**
A drift detector for context/state loss is absent or inactive.

**Correct Behavior:**

```
drift_detected (D2_context)
→ repair_triggered (R5_hard_reset OR R1_clarify)
→ reentry_observed (state validation)
→ continue_allowed (C0_normal)
```

---

## ❌ A2 — Tool Spin (Repeated Tool Errors)

**Symptom:**
The agent repeatedly calls a tool with invalid or incomplete parameters.

**Violation:** Level 3 — Missing `D2_context` or erroneous continue.

**Root Cause:**
Errors are treated as “ordinary turns” instead of drift.

**Correct Behavior:**

```
drift_detected (D2_context)
→ repair_triggered (R2_soft_repair or R4_request_clarification)
→ reentry_observed
→ continue_allowed
```

---

# Category B — Repair Misuse

## ❌ B1 — Politeness Loop (Text Instead of Structural Repair)

**Symptom:**
The model repeatedly apologizes without fixing the underlying issue.

**Violation:** Level 2 — Still in drift; no repair event occurred.

**Root Cause:**
Agent substitutes social language for structural correction.

**Correct Behavior:**

```
drift_detected (D1_instruction or D2_context)
→ repair_triggered (R1_clarify or R2_soft_repair)
→ reentry_observed
```

---

## ❌ B2 — Sledgehammer (Over-Repair)

**Symptom:**
The agent uses hard resets or handoff for minor issues.

**Violation:** Level 3 — Misuse of repair mapping (`R5_hard_reset`).

**Root Cause:**
Repair strategy calibration is missing.

**Correct Behavior:**

```
D2_context (minor)
→ R1_clarify or R2_soft_repair
```

---

# Category C — Phase Loop Breakage

## ❌ C1 — Skip-Check (Repair → Continue without Validation)

**Symptom:**
After repairing an issue, the agent continues without verifying correctness.

**Violation:** Level 2 — Missing `reentry_observed`.

**Correct Behavior:**

```
repair_triggered
→ reentry_observed (state verification)
→ continue_allowed
```

**Bad:** “I fixed it. Moving on.”

**Good:** “I updated it to July 5th. Does this look correct?”

---

## ❌ C2 — Continue Without Validation

**Symptom:**
The agent uses `continue_allowed` even when state is uncertain.

**Violation:** Level 2 — Incorrect phase selection.

**Correct Behavior:**
Use **reentry_observed** when validation is required.

---

# Category D — Failover Misinterpretation

## ❌ D1 — Failover Without Recovery Event

**Symptom:**
After emitting `failover_triggered`, the agent does not emit a recovery event.

**Violation:** Level 2 — Illegal transition (CAN-008 → recovery required).

**Correct Behavior:**

```
failover_triggered
→ reentry_observed OR continue_allowed OR session_closed
```

---

## ❌ D2 — Failover → Drift (Illegal Transition)

**Symptom:**
A failover event is followed immediately by a drift.

**Violation:** Level 2 — Must pass through recovery.

**Correct Behavior:**

```
failover_triggered
→ recovery event (reentry or continue)
→ drift_detected (if new drift occurs)
```

---

# Summary Table (v2-Aligned)

| Anti-Pattern            | Category | Violated Spec | Severity | Correct Fix                                 |
| ----------------------- | -------- | ------------- | -------- | ------------------------------------------- |
| Silent Failure          | A        | L2            | ⭐⭐⭐⭐     | Add D2 detector & repair cycle              |
| Tool Spin               | A        | L3            | ⭐⭐⭐⭐⭐    | Trigger soft/hard repair; reentry           |
| Politeness Loop         | B        | L2            | ⭐⭐⭐      | Replace content-only response with repair   |
| Sledgehammer            | B        | L3            | ⭐⭐       | Use proportional R* mapping                 |
| Skip-Check              | C        | L2            | ⭐⭐⭐⭐     | Insert reentry before continue              |
| Continue w/o Validation | C        | L2            | ⭐⭐⭐      | Select correct phase (reentry)              |
| Failover w/o Recovery   | D        | L2            | ⭐⭐⭐⭐⭐    | Emit recovery event                         |
| Failover → Drift        | D        | L2            | ⭐⭐⭐⭐     | Require recovery between failover and drift |

---

# Closing Note

When these anti-patterns appear, do not simply "fix the code."
Always log:

* The missing **Drift Code (D*)**
* The missing or misused **Repair Code (R*)**

This improves cross-team consistency and strengthens the PLD Standard for everyone.
