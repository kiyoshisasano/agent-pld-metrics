📄 docs/metrics/PLD_metrics_spec.md  
Status: Hybrid-Aligned Candidate  
Version: 2.0.0  
Audience: Engineers and researchers implementing PLD-compatible runtimes
Dependencies:  
Level 1: pld_event.schema.json  
Level 2: event_matrix.yaml + PLD_Event_Semantic_Spec_v2.0.md  
Level 3: PLD_taxonomy_v2.0.md  

# 1. Purpose

This document defines the **canonical PLD runtime metrics specification** for systems implementing PLD v2 lifecycle semantics.
Metrics in this specification MUST:

* Operate solely on **valid events**
* Respect Level-1 schema invariants and Level-2 semantic constraints
* Align with PLD v2 taxonomy naming, lifecycle phases, and event mappings

Metrics MAY incorporate **provisional taxonomy groupings** for analysis but MUST NOT derive required logic from non-canonical or pending codes.

---

# 2. Hierarchy of Authority

| Rank | Source                                | Enforcement |
| ---- | ------------------------------------- | ----------- |
| 1    | `pld_event.schema.json`               | MUST        |
| 2    | `event_matrix.yaml` + supporting docs | MUST        |
| 3    | This metrics specification            | MUST        |
| 4    | Dashboards, analysis, heuristics      | MAY         |

Where a conflict exists, sources MUST override this document in the order above.

---

# 3. Core Validity Requirements

### 3.1 Event Eligibility

A metric MUST count only events where:

schema_valid(event) AND matrix_valid(event)
Events failing MUST-level semantic rules MUST NOT contribute to metrics.

Events violating SHOULD-level rules MAY contribute **only under warn or normalize modes.**

---

### 3.2 Ordering Rule

`turn_sequence` is the authoritative ordering rule for any temporal metric.

If timestamps disagree with `turn_sequence`, ordering MUST defer to turn_sequence.

---

### 3.3 Phase Independence and Enforcement Modes

| Validation Mode | MUST Violations               | SHOULD Violations | Metric Contribution                  |
| --------------- | ----------------------------- | ----------------- | ------------------------------------ |
| strict          | reject                        | ignore            | canonical events only                |
| warn            | reject                        | warn              | allowed if phase logically derivable |
| normalize       | normalize if fully resolvable | warn or accept    | permitted                            |

---

# 4. Lifecycle-Aligned Metric Categories

This specification recognizes **six lifecycle metric families**, aligned with PLD v2 taxonomy and event mapping.

| Metric Family    | Source Phase | Event Types                                                        |
| ---------------- | ------------ | ------------------------------------------------------------------ |
| Drift Metrics    | drift        | `drift_detected`, `drift_escalated`                                |
| Repair Metrics   | repair       | `repair_triggered`, `repair_escalated`                             |
| Reentry Metrics  | reentry      | `reentry_observed`                                                 |
| Continue Metrics | continue     | `continue_allowed`, `continue_blocked`                             |
| Outcome Metrics  | outcome      | `evaluation_pass`, `evaluation_fail`, `session_closed`             |
| Failover Metrics | failover     | `failover_triggered`, `fallback_executed` (only if phase=failover) |

Observability metrics (`latency_spike`, `pause_detected`, `handoff`, `info`) MAY be tracked separately.

---

# 5. Canonical Metrics

The following metrics comprise the PLD v2 canonical baseline set.

---

## 5.1 PRDR — Post-Repair Drift Recurrence

Category: Drift+Repair Cross Phase Metric
Status: Canonical
Version: v2.0.0
Output Unit: percent (0–100)

### Definition

A session is recurrent if:

* It contains ≥1 `repair_triggered`, and
* A subsequent drift occurs after repair.

### Formula

$$\text{PRDR} = \frac{|\text{sessions with repair and post-repair drift}|}{|\text{sessions with repair}|} \times 100$$

### Phase Alignment Rule

This metric MUST use only:

* `repair_triggered`, `repair_escalated` (phase=repair)
* `drift_detected`, `drift_escalated` (phase=drift)

Numeric classifiers MAY be used as aggregation dimensions but MUST NOT change eligibility.

---

## 5.2 VRL — Recovery Latency

Category: Recovery Efficiency
Status: Canonical
Version: v2.0.0
Output: seconds / turns

Recovery cycle:

$$\text{drift} \to (\text{zero or more repair events}) \to \text{recovery event}$$

Recovery event MUST be one of:

| event_type         | phase      |
| ------------------ | ---------- |
| `reentry_observed` | `reentry`  |
| `continue_allowed` | `continue` |

If no recovery event arrives within cutoff, result is `NaN`.

---

## 5.3 FR — Failover Recurrence Index

Category: Failover Stability Index
Status: Canonical
Version: v2.0.0
Output: ratio (0–1)

Formula

$$
FR = \frac{\text{count}(failover\_triggered)}{\text{count}(lifecycle\_events)}
$$

`fallback_executed` MUST count only when its phase is `failover`.

---

# 6. Optional / Advisory Grouping Rules

Numeric taxonomy classifiers (e.g., `D1_instruction`, `R3_rewrite`, `D6_information`) MAY be used:

* for aggregation
* heatmaps
* model comparison

…but MUST NOT be prerequisite filters or affect metric validity.

---

# 7. Governance Notes

* Metrics MUST NOT create new prefixes or lifecycle categories.
* Provisional taxonomy codes MAY appear in aggregations but MAY NOT define new metrics.
* Pending governance items MUST NOT drive metric logic.
* **RESOLUTION CONFIRMED:** The prior collision between `D5_latency_spike` and `D5_information` is **resolved** via `D6_information`.

---

# 8. Version Policy

Any change affecting:

* formula semantics
* lifecycle alignment
* event eligibility
  → MUST increment metric version.

Metric names MUST remain globally unique.

---

# End of Specification

Source alignment tracked to:
`PLD_event.schema.json`, `event_matrix.yaml`, and `PLD_taxonomy_v2.0.md`.

---

## 📎 Mapping Notes

### Drift → D* family mapping

* Metrics depend solely on **event_type + phase**
* D1–D99 (including resolved codes **D6_information** and **D99_data_quality_error**) MAY be used for segmentation only.

### Repair → R* family mapping

* R1–R5 used only for analytics grouping
* Not required for metric algorithm

### Continue / Outcome / Failover

* Align strictly with event_type → phase constraints in Level-2 matrix rules

### Derived Metrics → M* family mapping (CRITICAL RULE)

* **M-Prefix:** Codes like `M1_PRDR`, `M2_VRL` are **Provisional Derived Metrics**.
* **Rule:** M-Prefix events MUST NOT be included in core lifecycle metric counts (e.g., Drift Rate, Repair Success) as they are derived signals, not raw events.

---

## Governance Notes

* Provisional codes (`D0_none`, `D9_unspecified`, `D99_data_quality_error`, `M*` codes) allowed only as advisory reference.
* **RESOLUTION CONFIRMED:** All prior numerical and scope conflicts (`D0`, `D5/D6`, `Analytics Scope`) are **resolved** and reflected in the Level 3 Taxonomy.

