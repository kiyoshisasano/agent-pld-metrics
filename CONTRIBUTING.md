<!--
path: CONTRIBUTING.md
component_id: contributing_guide
kind: doc
area: meta
status: stable
authority_level: 3
version: 2.0.0
license: Apache-2.0
purpose: Contribution guidelines for maintainers and external collaborators.
-->

# Business-Facing Summary (for Non-Technical Stakeholders)

This document explains how contributions to PLD should be made, with a focus on clarity, safety, and standardization. Non-technical team members can use this summary to understand the rules of engagement without needing deep knowledge of schemas or runtimes.

Use this guide to understand:

* What kinds of contributions move fast (runtime examples, docs, adapters)
* What requires formal review (core specifications L1–L3)
* How to ensure any contribution remains PLD-Compliant
* When sanitized logs or validation evidence are needed

This document ensures that engineers, PMs, analysts, and partner teams can contribute effectively while protecting the integrity of the PLD standard.

---

# Business-Facing Summary (for Non-Technical Stakeholders)

This document provides a high-level, business-friendly view of how PLD evolves over time. You do not need technical expertise in schemas or runtimes to understand it. The roadmap explains how PLD grows through real-world usage, evidence-based refinement, and community alignment.

Use this roadmap to understand:

* Where PLD is today (specification maturity & runtime stability)
* What improvements are planned next (metrics, adapters, validation tools)
* How your organization can influence the direction of PLD
* How PLD moves from concept → standard → field-proven practice

This is not a technical manual—it is a strategic guide for decision-makers, PMs, and partner organizations evaluating how PLD will evolve and support long-term stability efforts.

---

# Business-Facing Summary (for Non-Technical Stakeholders)

This document explains the roles involved in PLD collaboration—both within a single organization and across partners. You do not need technical knowledge of schemas or runtimes. Its purpose is to clarify who owns what, how responsibilities are divided, and how decisions about Stability, Drift, and Compliance are made.

Use this document to understand:

* **The Maintainer's role** (keeps the core PLD definitions consistent)
* **The Partner/Implementer’s role** (runs experiments and provides data)
* **How responsibilities split between specification and runtime work**
* **How teams collaborate during PoCs and ongoing evaluation**

This guide ensures everyone—PMs, engineers, analysts, and partner teams—shares the same expectations about how PLD evolves and who contributes what.

---

# Contributing to PLD (v2-Aligned)

**Status:** Stable (Level 5 Governance Guide)

Thank you for your interest in contributing to **Phase Loop Dynamics (PLD)**! 🚀
This document defines the standard contribution process for PLD under the **PLD v2** specification model.

PLD follows a **Standard-First** philosophy. We distinguish strictly between the:

* **Core Specification (Levels 1–3 — Immutable)**
* **Runtime Implementation (Level 5 — Flexible)**

Maintaining this separation ensures the scientific integrity and comparability of PLD experiments across teams.

---

# ⚡ The Golden Rule: The Normative Triad

To contribute to PLD (runtime, adapters, or logs), your output **MUST comply** with the complete normative stack:

| Layer                            | Requirement                                           | Why It Is Mandatory                                                       |
| -------------------------------- | ----------------------------------------------------- | ------------------------------------------------------------------------- |
| **Level 1 — Structure**          | Valid runtime envelope (strict schema)                | Ensures logs are structurally interoperable                               |
| **Level 2 — Semantics**          | Valid lifecycle transitions                           | Ensures drift/repair/reentry/continue/failover mean the same across teams |
| **Level 3 — Taxonomy & Metrics** | Canonical D*/R*/RE*/C*/F*/O* codes + v2 metric schema | Ensures PRDR/VRL/FR metrics remain comparable                             |

**Warning:**
Meeting Level 1 alone (**valid JSON**) is **not** PLD compliance.
Violating Level 2 or 3 produces only *"PLD-style JSON"* — not valid data.

---

# 🚦 What Can I Contribute?

Before opening an issue or PR, determine which **Zone** your contribution belongs to.

## 🟢 Green Zone — High-Velocity Contributions (Level 4 & 5)

Implementation, documentation, examples.
We actively encourage contributions here.

**Scope:**

* quickstart/
* examples/
* docs/
* analytics/
* runtime adapters (LangGraph, AutoGen, custom frameworks)

**Goal:** Improve usability, documentation, demonstrations.

**Constraint:**
Level 5 code **must not violate Level 1–3 specifications**.

**Review Process:** Lightweight.

---

## 🔴 Red Zone — Core Specification & Governance (Levels 1–3)

Changes here affect the **definition of PLD**.

**Scope:**

* docs/specifications/
* meta/
* canonical runtime invariants
* manifest-controlled components

**Includes:**

* Schema changes (L1)
* Lifecycle semantics (L2)
* Taxonomy & Metrics (L3 canonical registry)

**Process:**
Requires Maintainer + Governance Reviewer approval.
Submit a **Discussion** BEFORE filing a PR.

---

# 🛠 Validation (How to Ensure Compliance)

Because PLD is a standard, all contributions must be validated.

## Option A — Use the PLD v2 Reference Runtime (Python)

Use **RuntimeSignalBridge** with **STRICT mode** to enforce Level 1/2 logic.

```python
from pld_runtime import RuntimeSignalBridge, ValidationMode, RuntimeSignal

bridge = RuntimeSignalBridge(validation_mode=ValidationMode.STRICT)

sig = RuntimeSignal(
    source="assistant",
    payload={"text": "Test"},
)

# STRICT mode checks:
# - L1 envelope validity
# - L2 legal transitions
# - L3 taxonomy alignment (when codes are provided)

event = bridge.build_event(sig)
print("✅ Event accepted (L1/L2 enforced)")
```

Strict Mode ensures:

* required fields are present
* illegal transitions are rejected
* INFO-only codes respect phase rules
* taxonomy prefixes are canonical

You MUST self-validate taxonomy correctness (Level 3).

---

## Option B — Custom Implementations (TS/Go/Rust/etc.)

If implementing PLD outside Python:

### **L1 Check**

Your output MUST match the v2 runtime envelope schema.

### **L2 Check** (examples of illegal transitions)

* `reentry` without a preceding `repair`
* `continue` after `drift` without recovery
* emitting `failover` directly from `stable`
* skipping recovery validation (reentry/continue)

### **L3 Check**

* Drift codes MUST come from canonical families:

  * `D1_instruction`
  * `D2_context`
  * `D3_repeated_plan`
  * `D4_response`
  * `D5_safety`
* Repair codes MUST use R1–R5
* Outcomes MUST use O* codes from L3
* No custom taxonomy forks

---

# 🧩 Metadata & Manifest Rules

PLD uses **manifest.yaml** to track authority and provenance.

## Implicit Tracking (Directory-Level)

**Green Zone** files automatically inherit context.
You do NOT need to modify `manifest.yaml`.

## Explicit Tracking (File-Level)

**Red Zone** contributions require manifest entries.

Required file header:

```python
# component_id: my_new_component
# status: experimental
# authority_level: 5
```

Validate via:

```
python validate_manifest.py --level L2
```

---

# 📝 Pull Request Checklist (v2)

Before submitting, confirm:

### **Scope**

[ ] My change is in the Green Zone OR
[ ] I opened a Discussion for Red Zone changes

### **Standard Compliance**

[ ] **L1**: Valid runtime envelope structure (schema passes)
[ ] **L2**: All lifecycle transitions are legal under v2
[ ] **L3**: Taxonomy codes use the canonical registry (no forks)

### **Evidence (Policy Permitting)**

Option A:
[ ] I included sanitized v2-compliant traces (payload masked only)

Option B:
[ ] I cannot share logs, but I validated locally with STRICT mode

### **Metadata**

[ ] I updated `manifest.yaml` if touching Red Zone components

---

# 🤝 Collaboration Philosophy

PLD is not a finished product — it is a shared scientific exploration.
We iterate based on **evidence**, not speculation.

We value:

### **Clarity of Intent**

Explain *why* your change is needed.

### **Operational Reality**

Document real observations, not hypothetical behavior.

### **Flexible Data Sharing**

Sanitized logs help improve the standard — but are not required.
Internal validation is fully acceptable.

### **Canonical Registry Stewardship**

All contributors help maintain the integrity of:

* the lifecycle model (L2)
* the taxonomy registry (L3)
* the metric schema

This ensures that PLD remains interoperable across teams and organizations.

---

Thank you for helping build and refine PLD. 🎉

— Maintainer: *Kiyoshi Sasano*
