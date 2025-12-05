<!--
component_id: governance_legacy
kind: doc
area: meta
status: stable
authority_level: 5
purpose: Legacy onboarding guide for governance processes and contribution flow.
-->

# Business-Facing Summary (for Non-Technical Stakeholders)

This document provides a simple, practical onboarding guide for teams beginning to use PLD in a joint Proof-of-Concept (PoC) or internal evaluation. You do not need deep technical knowledge of PLD to benefit from this guide. Its purpose is to help new collaborators quickly understand the core loop—Drift, Repair, Reentry, Outcome—and learn how to review logs and verify compliance.

Use this guide to:

* Become "PLD-literate" in the first week
* Learn how to spot Drift and understand why it matters
* Understand the basics of safe log sharing and sanitization
* Follow a structured 90-minute onboarding session template
* Run early diagnostics to confirm that your PLD integration is healthy and compliant

This document focuses on practical alignment, not implementation details. After reading the summary and the first sections, most teams can begin meaningful PLD evaluation work immediately.

---

# PLD Onboarding & Diagnostics for Collaborators

**Status:** Stable (Level 5 Governance Guidance)

This onboarding guide helps new collaborators quickly become **PLD-literate**, understand the **Normative Triad (L1–L3)**, and perform early diagnostics on their PLD integration.

PLD terminology describes **observable system behavior**, not model psychology or intent inference.

This document answers:

* How do we make a new team PLD-compliant in the first week?
* What should we examine together early on?
* How do we run a health check on a PLD integration?

---

# 1. Onboarding Objectives (v2-Aligned)

By the end of onboarding, collaborators should be able to:

### **Understand the Lifecycle (Two Views)**

* **Simplified Loop for beginners:** Drift → Repair → Reentry → Outcome
* **Formal PLD v2 Lifecycle:**
  **drift → repair → reentry → continue → outcome → failover**

### **Map Reality to Spec**

Given a transcript, collaborators should be able to:

* Identify where drift occurs.
* Assign correct **Level 3 taxonomy codes**:

  * `D1_instruction`
  * `D2_context`
  * `D3_repeated_plan`
  * `D4_response`
  * `D5_safety`
* Distinguish types of repair (`R1–R5`).

### **Verify Compliance**

* Validate logs against the **Level 1 Schema**.
* Confirm lifecycle correctness (Level 2 Semantics).
* Ensure taxonomy codes follow **Level 3 Canonical Registry**.

### **Ensure Safety**

* Perform **sanitization of payload only** (mask PII in payload.text).
* Never mask PLD metadata or taxonomy information.

**Not Required:**

* Deep understanding of the reference runtime internals.
* Memorizing all operator codes.

---

# 2. 90-Minute Onboarding Session (Template)

Use this structure before writing code or analyzing data.

## **Part 1 — The Standard (20–30 min)**

Cover the core definitions:

### Lifecycle (L2 Semantics)

* Drift is a **state of misalignment**, not just an error.
* Repair is a **functional correction** attempt.
* Reentry validates that the system has recovered.
* Continue indicates safe forward progress.
* Failover is a recovery path triggered when repairs are insufficient.

### Taxonomy (L3 Standards)

Present the Level 3 code families:

* `D*` — Drift codes (instruction, context, repeated plan, safety, …)
* `R*` — Repair strategies (R1–R5)
* `RE*` — Reentry codes
* `C*` — Continue states
* `F*` — Failover
* `O*` — Outcome

Emphasize: **Canonical codes only. No private forks.**

### Compliance & Schema (L1)

Explain:

* Why strict validation of the runtime envelope matters.
* Why canonical metadata enables shared metrics.

---

## **Part 2 — Live Trace Mapping (30–40 min)**

Walk through 3–5 demo or real transcripts.

Perform **The Mapping Exercise**:

1. **Spot the Drift** — Identify the misalignment.
2. **Assign the Code** — Choose the correct `D*` (taxonomy v2).
3. **Check the Repair** — Which `R*` strategy was used?
4. **Check Recovery** — Was recovery validated properly?

   * **reentry_observed** (explicit validation)
   * **continue_allowed** (system-safe forward progress)
5. **Check the Outcome** — Which `O*` code applies?

Goal: Align human intuition with the **canonical lifecycle**.

---

## **Part 3 — Safety & Metrics (15–20 min)**

### Sanitization Protocol

Show examples of:

* **Good Log:** payload.text masked, metadata preserved.
* **Bad Log:** raw PII, missing schema fields, taxonomy errors.

### Metrics Preview (v2)

Introduce the core v2 metrics:

* **PRDR** — Post-Repair Drift Recurrence
* **VRL** — Verification / Recovery Latency
* **FR** — Failover Recurrence

Key takeaway:

> **Metrics are meaningful only when logs satisfy L1–L3 eligibility.**

---

## **Part 4 — Next Steps (10 min)**

Agree on:

* Producing 5–10 **sanitized, compliant traces**.
* Scheduling the first **Joint Evaluation Ritual**.
* Using a shared working document for diagnostics.

---

# 3. Early Diagnostics Checklist (v2-Aligned)

Use after 1–2 weeks of running a PLD-equipped system.

## **3.1 Compliance & Safety**

* [ ] Logs pass **Level 1 Schema** validation.
* [ ] Sanitization affects **payload only**.
* [ ] `event_id`, `turn_sequence` are unique & consistent.

## **3.2 Drift (Level 3 Taxonomy)**

* [ ] Drift events are logged where appropriate.
* [ ] Drift codes come from the canonical registry.
* [ ] D0/Unclassified usage is minimal.

## **3.3 Repair (Level 2)**

* [ ] Correct `R*` strategy chosen (R1–R5).
* [ ] Repairs occur **before** recovery.
* [ ] Hard repairs (`R5_hard_reset`) are rare & justified.

## **3.4 Recovery & Outcome**

* [ ] Recovery validation exists:

  * `reentry_observed` or `continue_allowed`.
* [ ] Every session has a clear `O*` outcome code.

---

# 4. Shared Diagnostics Document

Each collaboration should maintain a shared document containing:

### Baseline Metrics

* PRDR, VRL, FR (v2 metrics)

### Canonical Traces

* 2–3 **Golden** sessions (ideal flow)
* 2–3 **Borderline** sessions (recovered drift)
* 1–2 **Failure** sessions (catastrophic drift)

### Known Issues

Examples:

* "We struggle with D2_context on booking tool."
* "High VRL in tool-heavy flows."

This becomes the reference point for evaluating progress.

---

# 5. What Not to Over-Optimize in Early PoC

Avoid early premature optimization:

* Do not micro-optimize tiny drift swings.
* Do not create custom Drift Codes.

Focus instead on:

* **Valid Data (Compliance)**
* **Safety (Sanitization)**
* **Capturing major system failures (Utility)**

Onboarding is calibration.
It ensures Partner A & Partner B interpret each log **consistently and canonically**.
