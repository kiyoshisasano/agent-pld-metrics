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

# PLD Roadmap — A Living Evolution Path

PLD is **not a finished framework** — it is a **runtime reasoning model**
for stabilizing multi-turn AI systems.

This roadmap reflects how PLD is expected to evolve:

- through **implementation**
- through **real-world traces**
- through **shared refinement**, not unilateral design.

The goal is **evidence-based evolution**, not premature standardization.

---

## 🧭 Evolution Model

PLD matures through a repeating loop:

```
Concept → Prototype → Field Implementation → Evidence → Refinement
```


Each cycle strengthens:

- the conceptual model
- the runtime patterns
- the documentation
- the shared operational vocabulary

PLD evolves through use — not theory alone.

---

## 📌 Current Phase (2025)

| Track | Status | Notes |
|-------|--------|-------|
| Core Runtime Loop (Drift → Repair → Reentry → Continue → Outcome) | Stable | Expected to remain the foundation |
| Runtime v2.0 (Python reference) | Working | Observer-mode reference implementation |
| Schema + Event Envelope | Stable enough | Minor refinements may continue |
| Metrics + evaluation patterns | Draft | Requires more field data |
| Community + adoption | Beginning | Next priority |

> PLD is stable enough to trial — and still flexible enough to evolve.

---

## 🎯 Near-Term Focus (Next 3 Months)

| Priority | Output | Purpose |
|----------|--------|---------|
| PoC collaborations | Field traces + feedback | Validate runtime behavior in real environments |
| Refinement of taxonomy & drift/repair patterns | Updated spec notes | Align language with observed patterns |
| Additional runtime integrations | LangGraph / Assistants API / Rasa / AgentOps | Demonstrate flexibility and neutrality |
| Community structure | Contributor onboarding, RFC process | Support external participation |

These efforts help shift PLD from **idea → usable practice**.

---

## 🚧 Mid-Term Goals (6–12 Months)

| Area | Direction |
|------|-----------|
| Shared evaluation datasets | Anonymized PLD-labeled traces |
| Metric stabilization | PRDR, VRL, REI, failure modes |
| Optional validation tooling | “Good enough” conformance checks |
| Patterns & Playbooks | Integration recipes across frameworks |

These do **not** imply standardization — but enable comparability across implementations.

---

## 🌍 Long-Term Possibilities (Community-Driven)

| Pathway | Trigger Condition |
|---------|------------------|
| Standard-like formalization (OpenSpec/W3C-style) | If adoption reaches multiple independent implementers |
| Governance working group | If >3 independent organizations maintain implementations |
| Version compatibility guidelines | If multiple runtimes exist and interoperate |

These outcomes are **not goals themselves** — they are **optional consequences** of real adoption.

---

## ❌ What PLD Will Not Prioritize (For Now)

- Certifications or compliance programs  
- Fixed universal taxonomies  
- Enforcement-first runtime design  
- Enterprise "standards before usage" mindset  

PLD grows from reality, not imagined future requirements.

---

## 🤝 How to Influence This Roadmap

PLD evolves based on:

- real implementations  
- real behavioral evidence  
- real system constraints  
- shared reasoning from the community  

Ways to contribute:

- share PoC experience  
- submit traces or logs  
- propose improvements  
- open an RFC in Discussions  

---

## Summary

> **PLD is a shared exploration — not a finished product.  
It exists to help multi-turn AI systems behave predictably over time.  
Its future will be shaped by the people who use it.**

Maintainer: **Kiyoshi Sasano**
