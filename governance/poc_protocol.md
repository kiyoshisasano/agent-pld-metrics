<!--
component_id: governance_legacy
kind: doc
area: meta
status: stable
authority_level: 5
purpose: Legacy protocol for proof-of-concept evaluation and governance review.
-->

# Business-Facing Summary (for Non-Technical Stakeholders)

This document outlines the practical workflow for running a shared PLD Proof-of-Concept (PoC) with another team or organization. You can use it even without deep technical knowledge of PLD. Its purpose is to ensure both sides use the same definitions of Drift, Repair, Reentry, and Outcome, and follow a lightweight, consistent process for evaluating system behavior.

Use this guide to:

* Establish the scope and expectations of a joint PoC
* Ensure both sides produce PLD-Compliant (L1–L3) behavioral logs
* Choose safe and appropriate ways to exchange data
* Review example sessions together and evaluate system performance

This is not a legal or technical specification—it is an operational agreement that helps teams collaborate safely and efficiently.

---

# PLD Collaboration Protocol

This protocol answers:

* **What are we testing?** (Scope)
* **Is the data valid?** (Compliance)
* **Is it safe to share?** (Sanitization / Policy)
* **Did it work?** (Evaluation)

It provides a lightweight governance framework ensuring that **Drift**, **Repair**, **Continue**, **Reentry**, and **Outcome** carry the same meaning across organizational boundaries.

---

## 1. Shared Scope Definition

Before implementation, collaborators jointly define the experimental boundary.

| Item                 | Value                                          |
| -------------------- | ---------------------------------------------- |
| System               | e.g., "Customer Support Agent (RAG + Tools)"   |
| Environment          | Prototype / Staging / Production (Limited)     |
| Time Box             | e.g., "2 weeks data collection, 1 week review" |
| Implementation Owner | Partner A                                      |
| Governance Reviewer  | Partner B                                      |
| Metrics Analyst      | Assigned jointly or by Partner B               |

---

## 2. The Foundation: Normative Compliance (L1–L3)

To avoid incompatible evaluations, all parties agree to the **Normative Triad**. These conditions are **mandatory**.

### **Rule 1 — Structural Compliance (Level 1)**

All logs MUST validate against the **Level 1 PLD event schema**.

* Ensures standard metric eligibility.

### **Rule 2 — Semantic Compliance (Level 2)**

Events MUST follow the official PLD v2 lifecycle phases:

* **drift → repair → reentry / continue → outcome**
* Failover paths MUST emit failover_triggered and a recovery event (continue or reentry).

### **Rule 3 — Taxonomy Compliance (Level 3)**

All classification MUST use the Level 3 PLD taxonomy:

* Canonical examples: `D1_instruction`, `D2_context`, `D3_repeated_plan`, `R1_clarify`, `C0_normal`, `RE0_reentry`, `F1_failover`.
* Deprecated or legacy forms MUST NOT be used.

**Verification:** Partner A validates logs using a PLD-compliant runtime (e.g., SimpleObserver with ValidationMode=STRICT).

---

## 3. Data Exchange Protocol (Flexible)

Two collaboration paths depending on data governance constraints.

### **Path A — Shared Logs (Preferred)**

If sharing sanitized logs is allowed:

* Format: **PLD v2 JSONL** emitted by a compliant runtime.
* Required fields: timestamps, phases, taxonomy codes, runtime metadata.
* Sensitive text MUST be masked or hashed.

Example snippet:

```
{"event_type": "drift_detected", "pld": {"code": "D1_instruction"}, "payload": {"text": "<MASKED>"}}
```

### **Path B — Results Only (High-Security Orgs)**

Raw logs remain private.

* Partner A runs evaluation scripts internally.
* Partner A shares only **aggregated metrics** (e.g., PRDR=18%, VRL=2.4 turns).
* Partner A MUST self-certify:

  * Level 1 schema validation = **True**
  * ValidationMode = **STRICT** for all events
  * No taxonomy violations

---

## 4. Joint Evaluation Ritual (Bi-weekly)

Collaborators meet to assess semantic and behavioral quality.

### Step 1 — Compliance Check

* "Do the logs pass L1 schema validation?"
* For Path B: "Did the internal strict-validation pass?"

### Step 2 — Select Sessions

Pick 5–10 representative sessions.

* Path A: share sanitized JSONL snippets.
* Path B: screen-share or share genericized examples.

### Step 3 — Walk the Phase Loop

Validate lifecycle correctness:

* **Drift** — Is the D* code accurate? (`D2_context` vs `D1_instruction`)
* **Repair** — Was the chosen repair appropriate? (`R2_soft_repair` vs `R5_hard_reset`)
* **Continue vs Reentry** — Did the agent safely continue, or did it re-enter after validation?
* **Failover** — Was a recovery event emitted (continue or reentry)?

### Step 4 — Review Metrics

Use canonical v2 metrics (Level 3):

* **PRDR** — Post-Repair Drift Recurrence
* **VRL** — Recovery Latency
* **FR** — Failover Recurrence Index
* Optional: outcome distribution, drift rate, session health indicators

---

## 5. Success Criteria Template (v2-Aligned)

Organizations predefine "good enough" thresholds.

| Dimension                   | Typical Target                |
| --------------------------- | ----------------------------- |
| Drift Rate                  | ≤ 15% (domain-dependent)      |
| PRDR                        | ≤ 10–20%                      |
| VRL                         | ≤ 3 turns (fast recovery)     |
| FR (Failover Recurrence)    | ≤ 5%                          |
| Continue/Reentry Validation | ≥ 90% correctness             |
| Critical Failures           | 0 semantic violations (L1–L3) |

---

## 6. Roles & Responsibilities

### **Implementation Owner (Partner A)**

* Integrates PLD runtime (Level 5).
* Ensures L1–L3 compliance.
* Chooses Path A or Path B.

### **Governance Reviewer (Partner B)**

* Reviews semantic correctness (phase, taxonomy, transitions).
* Ensures metrics eligibility (PRDR/VRL/FR require valid semantics).

### **Metrics Analyst**

* Computes and interprets canonical v2 metrics.
* Flags anomalies requiring taxonomy or lifecycle review.

### **Both**

* Joint Go/No-Go decision.
* Review and update Success Criteria periodically.

---

## Summary

* **Define scope** collaboratively.
* **Enforce L1–L3 compliance** (mandatory).
* Choose **Path A (logs)** or **Path B (results)**.
* Conduct bi-weekly **evaluation + metrics review**.
* Use v2 canonical metrics (PRDR, VRL, FR) for consistent evaluation.

PLD v2 governance ensures shared meaning, safe iteration, and consistent lifecycle reasoning across all collaborating organizations.
