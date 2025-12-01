# PLD Taxonomy v2.0 — Working Notes (Hybrid Governance Context)

_Last updated: Draft state — derived from v0.1 Proposal + Confidence Summary_

This document should be retained even in later stabilization or governance-lock phases to ensure decision traceability. 
Content may change as implementation feedback and governance discussions evolve.


---

## 1. Purpose of This Document

This file exists as the **historical reasoning record** behind the formation of the PLD v2 taxonomy under **Hybrid Governance mode**.
It provides:

- Context for why v2 is not yet stabilized or suitable for locking
- Rationale behind Canonical / Provisional / Pending category decisions
- Known risks, ambiguity classes, and expected validation checkpoints
- Notes to future governance reviewers (“why did we do it this way?”)

This document is not a taxonomy, but rather a governance reference.

---

## 2. Hybrid Mode Principles

Hybrid governance was selected because the taxonomy is:

- **Structurally mature enough** to define operational codes (D / C / R / O)
- **Not yet semantically stable enough** to fully freeze all observed entries
- **Actively discovered in runtime environments**, meaning taxonomy boundaries evolve as system behavior evolves

The Hybrid model defines three stability states:

| State | Meaning | Allowed Changes | Notes |
|--------|---------|----------------|--------|
| **Canonical** | Finalized, runtime enforced | No renumbering or meaning changes | Metrics + enforcement binding required |
| **Provisional** | Recognized but evolving | Can rename, merge, clarify | Must be tracked across experiments |
| **Pending Governance** | Requires explicit decision | Cannot be used as normative reference | Appears in observation, not yet validated |

---

## 3. Readiness Assessment Summary

Based on semantic, operational, and metrics alignment analysis:

> **Estimated readiness: ~93% for finalization**

Breakdown:

| Category | Confidence | Status |
|----------|------------|--------|
| Core runtime event lifecycle (D → R → C/O) | ⭐⭐⭐⭐⭐ | Stable |
| Numeric system and prefix rules | ⭐⭐⭐⭐☆ | Stable but with exceptions |
| Observational / analytics items | ⭐⭐⭐⭐☆ | Not runtime, classification boundary needed |
| Drift fallback models (D0/D9) | ⭐⭐⭐☆☆ | Requires governance clarification |
| D5 collision (latency vs information) | ⭐⭐☆☆☆ | **Stabilization blocker** |

This score reflects taxonomy structural maturity rather than readiness for stabilization or governance locking.

---

## 4. Key Design Drivers

1. **Human interpretability over compression**
2. **Metrics traceability must match event codes**
3. **Prefix + numeric value must remain unique in Canonical registry**
4. **Repair pathways (R1→R5) require stable severity hierarchy**
5. **Drift classification must remain auditable** ("why was this labeled D3, not D2?")

---

## 5. Notable Pending Questions

### **A. D5 Numeric Collision**
Two observed drifts share the same numeric code (`D5_latentcy_spike`, `D5_information`).

This breaks:
- Numeric uniqueness rules
- Metrics aggregation integrity
- Drift dashboard interpretability

**Decision required:** merge, renumber, alias, or introduce dual semantic policy.


### **B. D0/D9 Boundaries**
Observed ambiguity:
- `D0_none` = no drift, normal heartbeat
- `D0_unspecified` = ingestion or metadata failure
- `D9_unspecified` = genuinely uncategorized drift

These represent **three distinct operational meanings** but currently overlap structurally.

---

## 6. Observational Metrics and Their Place

Codes such as:
- `PRDR`
- `VRL`
- `continue_repair_ratio`
- `failure_mode_clustering`
- `session_closure_typology`

Are **derived analytical signals**, not runtime events.

Open question: should they remain documentation or receive a new prefix (e.g., `M_…`).

Until resolved, they remain **Provisional (non-runtime)**.

---

## 7. Stabilization Criteria for v2.0

v2.0 may transition out of Hybrid Mode once the following readiness criteria are met.
These criteria serve as governance gates rather than finalization or freeze requirements:

| Condition Category | Requirement | Status Type |
|--------------------|------------|-------------|
| **Numeric Integrity** | The D5 collision is resolved (unique numeric assignment enforced across prefix). | Blocking |
| **Fallback Semantics** | D0_none / D0_unspecified / D9_unspecified are formally distinguished and defined in governance rules. | Blocking |
| **Analytics Boundary** | Observational metrics are either: (a) explicitly excluded from runtime taxonomy, or (b) formally assigned a new non-runtime prefix (e.g., `M_`). | Blocking |
| **Telemetry Validation** | Real runtime logs must show **< 3% routing to `D9_unspecified`**, indicating taxonomy coverage maturity. | Quantitative Gate |
| **Lifecycle Mapping Completeness** | All Canonical codes must map to: lifecycle stage, enforcement logic, and metrics traceability. | Structural Gate |
| **Backward Compatibility Review** | Any renumbering or alias introduction must include a documented migration strategy and auditability plan. | Governance Gate |
| **Tooling Readiness** | Dashboards, query templates, and monitoring rule sets must be aligned with the final taxonomy state. | Operational Gate |


Once all above are marked complete, taxonomy enters **Formal Governance Mode** and becomes eligible for:
- Version-lock eligibility (subject to governance approval)
- External publication
- Compliance alignment
- Version-controlled extension under RFC-like change framework

---

## 8. Future Review Notes

- This document should be retained even after freeze to ensure **decision traceability**.
- If v2.1 or v3 introduces new prefixes (metrics, safety signals, alignment categories), rationale in this file should be referenced to avoid accidental taxonomy drift.
- If governance seeks automation, this file becomes the basis for validation rules.

---

### Summary Line

> **PLD v2 taxonomy is structurally mature, stabilization in progress, and awaiting governance resolution**

---

Feedback, objections, and alternative framing proposals are welcomed at this stage.
