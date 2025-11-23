# docs/metrics/PLD_metrics_spec.md

**Status:** Hybrid-Aligned Candidate  
**Version:** 2.0.0  
**Audience:** Engineers and researchers implementing PLD-compatible runtimes  

**Dependencies:**

- Level 1: `pld_event.schema.json`
- Level 2: `event_matrix.yaml` + `PLD_Event_Semantic_Spec_v2.0.md`
- Level 3: `PLD_taxonomy_v2.0.md`

---

## 1. Purpose

This document defines the **canonical PLD runtime metrics specification** for systems implementing PLD v2 lifecycle semantics.

Metrics in this specification MUST:

- Operate solely on **valid events**
- Respect Level-1 schema invariants and Level-2 semantic constraints
- Align with PLD v2 taxonomy naming, lifecycle phases, and event mappings

Metrics MAY incorporate **provisional taxonomy groupings** for analysis but MUST NOT derive required logic from non-canonical or pending codes.

---

## 2. Hierarchy of Authority

| Rank | Source | Enforcement |
|------|--------|------------|
| 1 | `pld_event.schema.json` | MUST |
| 2 | `event_matrix.yaml` + supporting docs | MUST |
| 3 | This metrics specification | MUST |
| 4 | Dashboards, analysis, heuristics | MAY |

Where a conflict exists, sources MUST override this document in the order above.

---

## 3. Core Validity

> *(Content unchanged — omitted for brevity)*

---

## 7. Governance Notes

- Metrics MUST NOT create new prefixes or lifecycle categories.
- Provisional taxonomy codes MAY appear in aggregations but MAY NOT define new metrics.
- Pending governance items MUST NOT drive metric logic.

---

## 8. Version Policy

Any change affecting:

- formula semantics  
- lifecycle alignment  
- event eligibility  

➡ MUST increment the metric version.

Metric names MUST remain globally unique.

---

### End of Specification

Source alignment tracked to:

- `PLD_event.schema.json`
- `event_matrix.yaml`
- `PLD_taxonomy_v2.0.md`

---

## 📎 Mapping Notes

### ▶ Drift → `D*` family mapping

- Metrics depend solely on **event_type + phase**
- `D1–D6` (including the newly separated `D6_information`) MAY be used for segmentation only.

### ▶ Repair → `R*` family mapping

- `R1–R5` used only for analytics grouping  
- Not required for metric algorithms

### ▶ Continue / Outcome / Failover

- Must align strictly with `event_type → phase` constraints in Level-2 matrix rules

### ▶ Derived Metrics → `M*` family mapping (**NEW**)

- **M-Prefix:** Codes like `M1_PRDR`, `M2_VRL`, `M3_CRR` are **explicitly provisional** and MAY be used for segmentation.
- **Rule:** `M*` prefix events MUST NOT be included in core lifecycle counts (e.g., drift rate, repair success), as they are derived signals, not raw events.

---

## Governance Notes

- Provisional codes (`D0_none`, `D9_unspecified`, `M*`) allowed only as advisory reference.
- **RESOLUTION CONFIRMED:** The previous collision between `D5_latency_spike` and `D5_information` is **resolved** via `D6_information`. All metric systems MUST treat these as distinct signals if included in analysis.

---
