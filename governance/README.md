<!--
component_id: governance_legacy
kind: doc
area: meta
status: stable
authority_level: 5
purpose: Governance legacy docs (root index).
-->

# Business-Facing Summary (for Non-Technical Stakeholders)

This document provides a practical, collaboration-focused guide for running Joint PLD Proof-of-Concepts (PoCs) across teams or organizations. You do not need deep technical knowledge of PLD to use it. The goal is to ensure both sides share a common understanding of what Drift, Repair, Reentry, and Outcome mean, and how to evaluate system behavior consistently.

Use this document when:

* Starting a PLD-based PoC with another group
* Exchanging logs or behavioral patterns in a safe and compliant way
* Aligning definitions, expectations, and evaluation criteria

This folder is not a technical specification—it's an operational playbook to help teams work together smoothly, safely, and with shared clarity.

---

# PLD Governance & Collaboration Guide

**Status:** Stable (Level 5 Governance Guide)

This document is the operational playbook for cross-team and cross-organization collaboration using **PLD v2**. It defines how to run shared PLD experiments, how to exchange compliant traces, and how to align interpretation of lifecycle events, taxonomy codes, and metrics.

This folder focuses on **collaboration**, not implementation.
While the rest of the repository addresses:

* implementing PLD runtime patterns
* running detectors and operators
* generating compliant logs
* evaluating model behavior

governance/ describes:

* how to run a shared PoC
* how to align definitions across teams
* how to exchange sanitized, PLD-Compliant traces (L1–L3)
* how to determine if a PLD integration is successful

It is not a legal agreement.
It is a lightweight, repeatable operational playbook.

---

# When to Use This Folder

Use **governance/** when:

* collaborating with another team or external partner
* sharing behavioral patterns without exposing proprietary details
* running a PoC where both parties need a consistent mental model
* validating that both sides read traces and taxonomy the same way

You typically arrive here after:

1. You have a **local PLD prototype** (quickstart/).
2. You are **emitting PLD-Compliant events** (validating against L1–L3).
3. You have real **interaction traces** ready for initial evaluation.

```
Local Prototype → Compliance Check → Shared PoC → Field Deployment
```

---

# Files in This Folder

| File                   | Purpose                                                         |
| ---------------------- | --------------------------------------------------------------- |
| **poc_protocol.md**    | How to run a shared PoC (operational workflow)                  |
| **onboarding.md**      | First-week diagnostics & alignment guide                        |
| **community_roles.md** | Roles: Maintainer / Implementers / Reviewers / Metrics Analysts |

---

# Audience

This playbook is for:

* External collaborators evaluating PLD
* Product + Applied AI teams piloting PLD internally
* Research teams validating PLD behavior on new surfaces
* Anyone who needs a shared operational language (drift/repair/recovery/failover)

> PLD describes **observable system behavior**, not psychology or intent inference.
> We align on *“what happened”* — not *“why the model thought that way.”*

---

# 1 — Shared Scope

Before starting, clarify these dimensions:

| Dimension            | Notes                                              |
| -------------------- | -------------------------------------------------- |
| **Target System**    | e.g., tool-based agent, RAG pipeline, workflow bot |
| **Interaction Type** | chat, task API, scripted scenario                  |
| **Risk Level**       | prototype → staging → guarded production           |
| **Time Box**         | e.g., 2–4 weeks before review                      |

---

# 2 — Shared PLD Definitions (Normative Triad)

All shared PLD work must follow the **Normative Triad**.
Violating any level produces **"PLD-style JSON"** that is **not valid** for joint evaluation.

| Layer                            | Requirement                               | Why It Matters                                                             |
| -------------------------------- | ----------------------------------------- | -------------------------------------------------------------------------- |
| **Level 1 — Structure**          | Valid runtime envelope (strict schema)    | Ensures logs are machine-interoperable                                     |
| **Level 2 — Semantics**          | Valid lifecycle transitions               | Ensures drift/repair/reentry/continue/failover mean the same to both sides |
| **Level 3 — Taxonomy & Metrics** | Canonical codes only (D*/R*/RE*/C*/F*/O*) | Ensures metrics (PRDR, VRL, FR) are comparable                             |

PLD v2 Lifecycle:
**drift → repair → reentry → continue → outcome → failover**

PLD v2 Taxonomy (examples):

* `D1_instruction`
* `D2_context`
* `D3_repeated_plan`
* `D4_response`
* `D5_safety`
* `R1_clarify`, `R2_soft_repair`, `R5_hard_reset`
* `RE1_verified`, `C0_normal`, `F1_fallback`, `O1_completed`

> Shared evaluation only works when both sides use **canonical, unforked Level 3 codes**.

---

# 3 — Minimal Data Protocol (Safe Sharing)

**We share system behavior, not secrets.**
Adhering to L1–L3 enables deep analysis even if all content is masked.

## 3.1 What We Share (Sanitized Logs)

* PLD event stream (`JSONL`) **validating against Level 1 Schema**
* Metadata: timestamps, phases, taxonomy codes
* Payload text masked (PII/IP replaced)

Example:

```json
{
  "turn_sequence": 1,
  "role": "assistant",
  "payload": {
    "text": "Confirming flight to <MASKED_CITY>..."
  },
  "pld": {
    "event_type": "drift_detected",
    "phase": "drift",
    "code": "D1_instruction"
  }
}
```

## 3.2 What We Do *Not* Require

* raw production logs
* model weights
* prompts or proprietary code
* PII / unmasked data
* API keys

Only **compliant, sanitized behavioral traces** are required.

---

# 4 — Joint Evaluation Ritual (v2 Lifecycle)

This is the core shared evaluation process.

### Step 1 — Review 5–10 Sessions

* 3 stable (no drift)
* 3 recovered (drift → repair → reentry → continue)
* 3 failed or escalated (drift → failover)

### Step 2 — Walk the Lifecycle

Check, for each drift:

* Was the `D*` code correct (Level 3)?
* Was the repair strategy (`R*`) correct?
* Was recovery validated via:

  * `reentry_observed` or
  * `continue_allowed`?
* Were failovers used correctly?
* Was the final outcome (`O*`) correct?

### Step 3 — Evaluate Metrics (v2 Metrics)

Use official v2 metrics:

* **PRDR** — Post-Repair Drift Recurrence
* **VRL** — Verification / Recovery Latency
* **FR** — Failover Recurrence Index

Supportive signals (non-canonical but still useful):

* drift rate
* repair ratio
* outcome distribution

### Step 4 — Decide Next Action

* UX adjustments
* operator/prompt refinement
* routing logic updates
* monitoring improvements

---

# 5 — Shared Success Criteria Template (v2)

Targets depend on domain/risk, but typical benchmarks:

| Dimension             | v2 Target (Example)              |
| --------------------- | -------------------------------- |
| **PRDR**              | ≤ 10% recurrence after repair    |
| **VRL**               | ≤ 1.5 turns to validate recovery |
| **FR**                | ≤ 5% failover recurrence         |
| **Outcomes (O*)**     | ≥ 80% valid completion           |
| **Critical Failures** | 0 in N sessions                  |

---

# 6 — Roles & Cadence (Aligned with community_roles_v2)

| Role                    | Responsibility                                         |
| ----------------------- | ------------------------------------------------------ |
| **Maintainer**          | Stewards L1–L3, resolves taxonomy/lifecycle questions  |
| **Implementer**         | Integrates runtime; generates compliant logs           |
| **Governance Reviewer** | Audits lifecycle validity and taxonomy correctness     |
| **Metrics Analyst**     | Computes v2 metrics; identifies anomalies              |
| **Both Teams**          | Participate in bi-weekly review and go/no-go decisions |

Minimal protocol → minimal friction → maximal alignment.

Maintainer: *Kiyoshi Sasano*
