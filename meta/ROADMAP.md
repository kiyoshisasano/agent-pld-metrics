<!--
path: meta/ROADMAP.md
component_id: roadmap
kind: doc
area: meta
status: working_draft
authority_level: 3
version: 2.1.0
license: Apache-2.0
purpose: Define the living evolution path for the PLD model, runtime ecosystem, and community participation.
-->

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

# PLD Roadmap — v2 Evolution Path

**Status:** Stable (Meta / Governance)

PLD follows a **Standard‑First** philosophy.
Multi‑turn stability requires strict adherence to observable behavioral rules that are:

* structurally defined (Level 1)
* semantically constrained (Level 2)
* taxonomically comparable (Level 3)

This roadmap defines how PLD evolves under the **v2 architecture**.
It reflects three forces:

* field evidence (real traces)
* reference implementations (runtime & adapters)
* shared refinement (RFCs & governance)

The goal is **evidence‑based evolution of the Normative Triad (L1–L3)** and a stable ecosystem of compatible runtimes.

---

# 🧭 Evolution Model (v2)

PLD matures through a repeating loop:

graph LR
A[Concept] --> B[Specification (L1-3)]
B --> C[Reference Runtime & Test Suites]
C --> D[Field Evidence (Compliant Traces)]
D --> E[Refinement (RFC Process)]
E --> B

Each cycle strengthens:

* Normative Triad (L1 schema, L2 lifecycle, L3 taxonomy & metrics)
* Runtime invariants (immutability, strict validation)
* Shared vocabulary (D*/R*/RE*/C*/F*/O*)
* Observable metrics (PRDR, VRL, FR)

---

# 📌 Current Phase (2025)

| Track                     | Status                | Notes                                             |
| ------------------------- | --------------------- | ------------------------------------------------- |
| **L1–L3 Specifications**  | Stable                | Canonical; required for interoperability          |
| **Runtime v2.x (Python)** | Stable                | Reference: `RuntimeSignalBridge` with STRICT mode |
| **Metrics & Evaluation**  | Candidate→Stabilizing | PRDR / VRL / FR grounded in field data            |
| **Taxonomy Registry**     | Stable                | Full families: D*, R*, RE*, C*, F*, O*            |
| **Community & Adapters**  | Growing               | LangGraph / Swarm / LlamaIndex integrations       |

State:
The core specifications are mature enough for production‑grade PoC evaluations.

---

# 🎯 Near-Term Focus (Next 3 Months)

| Priority                  | Output                         | Purpose                                                         |
| ------------------------- | ------------------------------ | --------------------------------------------------------------- |
| **PoC Collaborations**    | Compliant sanitized v2 traces  | Validate that L1–L3 capture real drift/repair/failover patterns |
| **Metrics Stabilization** | PRDR / VRL / FR definitions    | Align evaluation across orgs                                    |
| **Lifecycle Precision**   | Continue/failover refinements  | Reduce ambiguous transitions in field logs                      |
| **Runtime Adapters**      | LangGraph / Swarm / LlamaIndex | Demonstrate PLD portability                                     |
| **Governance Process**    | RFC + Reviewer Roles           | Formalize Red Zone change flow                                  |

These efforts move PLD from **theory → validated standard**.

---

# 🚧 Mid-Term Goals (6–12 Months)

| Area                              | Direction                                                      |
| --------------------------------- | -------------------------------------------------------------- |
| **Shared Datasets**               | Public anonymized v2-compliant drift traces                    |
| **Cross‑Framework Compatibility** | Automated conformance suites (schema + transitions + taxonomy) |
| **Metric Stabilization**          | Mathematical formalization of PRDR/VRL/FR                      |
| **Validation Tooling**            | CLI validators for L1–L3 (non‑Python runtimes)                 |
| **Pattern Library**               | Industry‑specific integration recipes                          |

---

# 🌍 Long-Term Possibilities (Community‑Driven)

| Pathway                      | Trigger Condition                                              |
| ---------------------------- | -------------------------------------------------------------- |
| **Formal Standardization**   | Multiple independent runtime implementers (W3C/OpenSpec style) |
| **Multi‑Language Runtimes**  | TS/Go/Rust runtimes requiring compatibility tests              |
| **Governance Working Group** | >3 orgs maintaining core implementations                       |

These are optional outcomes driven by adoption, not goals by themselves.

---

# ❌ What PLD Will Not Prioritize (v2 Position)

* **Model internals** or hidden psychological states → PLD is observable‑only.
* **“Black‑box” drift detection** → taxonomy is grounded in surface behavior.
* **Opaque or proprietary metrics** → all metrics must be derivable from the envelope.
* **Runtime‑enforced only logic** → v2 emphasizes *bridge‑enforced immutability & validation*.
* **Custom taxonomy forks** → standard codes ensure comparability.

PLD grows from **real usage**, not imagined requirements.

---

# 🤝 How to Influence This Roadmap

PLD evolves based on **evidence**, not speculation.

Ways to contribute:

* **Share sanitized v2 traces** (payload masked only)
* **Build adapters** for new frameworks
* **Open RFCs** for L1–L3 changes (Red Zone)
* **Provide metrics reports** (PRDR/VRL/FR)

The roadmap adapts as the community uncovers new patterns and stability challenges.

---

# Summary

PLD is a shared scientific exploration of multi‑turn stability.
We maintain a Normative Standard not to restrict developers, but to enable **open collaboration with trust, comparability, and scientific rigor**.

— Maintainer: *Kiyoshi Sasano*
