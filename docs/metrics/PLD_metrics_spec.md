# docs/metrics/PLD_metrics_spec.md

**Status:** Hybrid-Aligned Candidate
**Version:** 2.0.0
**Audience:** Engineers and researchers implementing PLD-compatible runtimes

**Dependencies:**

* Level 1: `pld_event.schema.json`
* Level 2: `event_matrix.yaml` + `PLD_Event_Semantic_Spec_v2.0.md`
* Level 3: `PLD_taxonomy_v2.0.md`

---

## 1. Purpose

This document defines the **canonical PLD runtime metrics specification** for systems implementing PLD v2 lifecycle semantics.

Metrics in this specification MUST:

* Operate solely on **valid events**
* Respect Level-1 schema invariants and Level-2 semantic constraints
* Align with PLD v2 taxonomy naming, lifecycle phases, and event mappings

Metrics MAY incorporate **provisional taxonomy groupings** for analysis but MUST NOT derive required logic from non-canonical or pending codes.

---

## 2. Hierarchy of Authority

| Rank | Source                                | Enforcement |
| ---- | ------------------------------------- | ----------- |
| 1    | `pld_event.schema.json`               | MUST        |
| 2    | `event_matrix.yaml` + supporting docs | MUST        |
| 3    | This metrics specification            | MUST        |
| 4    | Dashboards, analysis, heuristics      | MAY         |

Where a conflict exists, sources MUST override this document in the order above.

---

## 3. Core Validity

### 3.1 Event Eligibility

A metric MUST count only events where:

```
schema_valid(event) AND matrix_valid(event)
```

Events violating MUST-level semantic constraints MUST NOT be included.

Events violating SHOULD-level constraints MAY be counted under **warn** or **normalize** enforcement modes.

---

### 3.2 Ordering Rule

`turn_sequence` MUST be treated as the authoritative ordering primitive.

If timestamp ordering conflicts with `turn_sequence`, metrics MUST defer to `turn_sequence`.

---

### 3.3 Enforcement Modes

| Mode      | MUST Violations         | SHOULD Violations | Metric Use Allowed     |
| --------- | ----------------------- | ----------------- | ---------------------- |
| strict    | reject                  | ignore            | canonical only         |
| warn      | reject                  | warn              | if logically derivable |
| normalize | normalize if resolvable | allow             | permitted              |

---

## 4. Lifecycle-Aligned Metric Categories

Metrics SHALL classify input events according to lifecycle phases defined in Level-2 semantics.

| Category         | Phase    | Event Types                                            |
| ---------------- | -------- | ------------------------------------------------------ |
| Drift Metrics    | drift    | `drift_detected`, `drift_escalated`                    |
| Repair Metrics   | repair   | `repair_triggered`, `repair_escalated`                 |
| Reentry Metrics  | reentry  | `reentry_observed`                                     |
| Continue Metrics | continue | `continue_allowed`, `continue_blocked`                 |
| Outcome Metrics  | outcome  | `evaluation_pass`, `evaluation_fail`, `session_closed` |
| Failover Metrics | failover | `failover_triggered`, `fallback_executed`              |

Observability events (`latency_spike`, `pause_detected`, `handoff`, `info`) MAY be measured separately but MUST NOT alter lifecycle metric requirements.

---

## 5. Canonical Metrics

### 5.1 PRDR — Post-Repair Drift Recurrence

```
Category: Drift + Repair Cross-Phase Metric
Status: Canonical
Output: Percent (0–100)
```

A session is recurrent when:

* ≥1 repair occurred, **and**
* drift is detected after that repair.

**Formula:**

```math
PRDR =
(|sessions_with_repair_and_post_repair_drift| /
 |sessions_with_repair|) × 100
```

Only the following phases/events count:

* Drift: `drift_detected`, `drift_escalated`
* Repair: `repair_triggered`, `repair_escalated`

---

### 5.2 VRL — Recovery Latency

```
Category: Recovery Efficiency
Status: Canonical
Output: seconds / turns
```

Recovery path:

```
drift → repair events (optional) → recovery event
```

Valid recovery events:

| event_type         | phase    |
| ------------------ | -------- |
| `reentry_observed` | reentry  |
| `continue_allowed` | continue |

If no recovery occurs before cutoff → result = `NaN`.

---

### 5.3 FR — Failover Recurrence Index

```
Category: Failover Stability
Status: Canonical
Output: ratio (0–1)
```

```math
FR = count(failover_triggered) / count(lifecycle_events)
```

`fallback_executed` MUST count only when its phase is `failover`.

---

## 6. Optional / Advisory Grouping Rules

Numeric taxonomy classifiers (e.g., `D1_instruction`, `R3_rewrite`, `D6_information`) MAY be used for segmentation, visualization, or research — but MUST NOT alter:

* eligibility
* canonical formulas
* lifecycle interpretation
* validation behavior

---

## 7. Governance Notes

* Metrics MUST NOT create new prefixes or lifecycle categories.
* Provisional taxonomy codes MAY appear in aggregations but MAY NOT define new metrics.
* Pending governance items MUST NOT drive metric logic.
* **RESOLUTION CONFIRMED:** The previous collision between `D5_latency_spike` and `D5_information` is resolved via `D6_information`.

---

## 8. Version Policy

Any change affecting:

* formula semantics
* lifecycle alignment
* event eligibility

➡ MUST increment the metric version.

Metric names MUST remain globally unique.

---

### End of Specification

Source alignment tracked to:

* `PLD_event.schema.json`
* `event_matrix.yaml`
* `PLD_taxonomy_v2.0.md`

---

## 📎 Mapping Notes

### ▶ Drift → `D*` family mapping

* Metrics depend solely on **event_type + phase**
* `D1–D6` (including `D6_information`) MAY be used for segmentation only.

### ▶ Repair → `R*` family mapping

* `R1–R5` MAY be used for analytics grouping.
* Not required for metric algorithms.

### ▶ Continue / Outcome / Failover

* Must align strictly with Level-2 `event_type → phase` enforcement.

### ▶ Derived Metrics → `M*` family mapping (**NEW**)

* `M1_PRDR`, `M2_VRL`, `M3_CRR` are **explicitly provisional**
* `M*` MUST NOT be included in lifecycle metric counts.

---

### Confidence Score: **Finalized**
