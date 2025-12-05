<!--
component_id: governance_legacy
kind: doc
area: meta
status: stable
authority_level: 5
purpose: Legacy description of community roles and responsibilities.
-->

# Business-Facing Summary (for Non-Technical Stakeholders)

This document explains the roles involved in PLD collaboration—both within a single organization and across partners. You do not need technical knowledge of schemas or runtimes. Its purpose is to clarify who owns what, how responsibilities are divided, and how decisions about Stability, Drift, and Compliance are made.

Use this document to understand:

* **The Maintainer's role** (keeps the core PLD definitions consistent)
* **The Partner/Implementer’s role** (runs experiments and provides data)
* **How responsibilities split between specification and runtime work**
* **How teams collaborate during PoCs and ongoing evaluation**

This guide ensures everyone—PMs, engineers, analysts, and partner teams—shares the same expectations about how PLD evolves and who contributes what.

---

# ROLE ALIGNMENT — Collaboration Model

This document clarifies how collaborators participate in the PLD ecosystem under the **v2 Governance Model**.

PLD remains an evolving research-driven standard focused on solving **Agent Stability**.
To iterate safely and consistently, we maintain clear boundaries between the **canonical specifications (L1–L3)** and the **runtime implementation (Level 5)**.

---

# 1. The Architect (Maintainer)

**Role:** Steward of the Canonical Specification (Levels 1–3)

**Responsibilities:**

* Maintains the **PLD lifecycle model**:
  **drift → repair → reentry → continue → outcome → failover**
* Defines and curates the **Normative Triad**:

  * **Level 1 — Structure** (event schema)
  * **Level 2 — Semantics** (lifecycle rules, transitions)
  * **Level 3 — Taxonomy & Metrics** (D*/R*/RE*/C*/F*/O* codes, PRDR/VRL/FR metrics)
* Ensures that all collaborators interpret the canonical codes and phases consistently.
* Reviews evidence from partners and merges changes into L1–L3 based on **evidence-driven consensus**.

**Why this matters:**
Consistency in L1–L3 is the foundation for scientific comparison.
If two partners disagree on what "Drift" means, no cross-experiment learning is possible.

---

# 2. The Implementers (Partners)

**Role:** Field Researchers / Applied Experimenters

**Responsibilities:**

* Apply PLD in real-world agents and pipelines.
* Ensure **strict L1–L3 compliance** so logs retain metric eligibility.
* Surface edge cases such as:

  * Missing taxonomy codes
  * Ambiguous lifecycle transitions
  * Domain-specific failure patterns
* Provide evidence (traces) that can inform L1–L3 evolution.

Partners are not just “users.”
They are co-authors of the standard via real-world experimentation.

---

# 3. The Governance Reviewer

**Role:** Semantic & Lifecycle Auditor

**Responsibilities:**

* Validates lifecycle correctness (no illegal transitions).
* Confirms taxonomy usage (canonical Level 3 codes only).
* Ensures reentry vs continue is selected correctly.
* Reviews failover behavior for correctness.

This role ensures experiments remain **scientifically comparable** and free of semantic drift.

---

# 4. The Metrics Analyst

**Role:** Evaluator of PLD v2 Metrics

**Responsibilities:**

* Computes and interprets key metrics:

  * **PRDR** (Post-Repair Drift Recurrence)
  * **VRL** (Verification/Recovery Latency)
  * **FR** (Failover Recurrence Index)
* Ensures metrics are used only when logs satisfy L1–L3 eligibility.
* Identifies anomalies requiring governance review.

---

# 5. Collaboration Boundaries

To maintain agility while ensuring comparability, collaborators divide focus:

| Area                     | Architect's Focus          | Partner's Focus                     |
| ------------------------ | -------------------------- | ----------------------------------- |
| **Core Specs (L1–L3)**   | Defines & Curates          | Uses & Validates (no private forks) |
| **Runtime / Adapters**   | Provides Reference         | Builds & Customizes Freely          |
| **Metrics**              | Defines Canonical Formulas | Generates Real-World Data           |
| **Production Decisions** | Advises                    | Owns (Partner decides safety)       |

---

# 6. How We Evolve (Evidence-Driven)

PLD evolves through a structured loop:

1. **Hypothesis** — Maintainer proposes a spec change (e.g., new drift code).
2. **Experiment** — Partners test in PoCs or prototypes.
3. **Evidence** — Shared traces validate or disprove the proposal.
4. **Consensus** — Maintainer merges change into L1–L3.

*Working logs outperform theoretical arguments.*

---

# Summary

* **Architect:** Maintains canonical definitions (L1–L3) and lifecycle correctness.
* **Partners (Implementers):** Test hypotheses with real-world agents.
* **Governance Reviewer:** Ensures semantic & taxonomic compliance.
* **Metrics Analyst:** Computes v2 metrics and flags anomalies.

Together we evolve PLD through research, evidence, and shared standards—
not bureaucracy, but **scientific rigor and reproducibility**.
