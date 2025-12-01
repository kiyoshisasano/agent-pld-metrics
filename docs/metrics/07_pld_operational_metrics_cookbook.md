# 📄 07 — PLD Operational Metrics Cookbook

Version: 2.0.0  
*Status*: Candidate — Stabilizing based on implementation feedback
This document is part of an ongoing research and early adoption effort to explore operational metrics for PLD-aligned systems. The definitions and interpretations may evolve as real-world implementation feedback is collected.

Authority Level: 3 — Derived operational rule (proposed canonical baseline)  
Governance Approach: Experimental dual-track metrics versioning  
Maintainer: TBD

---

## 0. Specification Purpose

This document defines the proposed canonical operational metrics used to evaluate runtime health and lifecycle stability within PLD-aligned systems.

It combines:

- Machine-parseable, versioned metric definitions (normative)  
- Operational interpretation guidance such as thresholds, queries, dashboards, and rollout heuristics (non-normative and subject to iteration)

These metrics are intended to support:

- Longitudinal benchmark comparability  
- Runtime regression detection  
- Drift management evaluation  
- Observability standardization across implementations  

---

## 1. Reference and Dependency Layers

| Level       | Purpose / Role                              | Referenced Sources                                                                                                                                                               | Enforcement / Status                              |
| ----------- | ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| **Level 1** | **Schema Definition**                       | `docs/schemas/pld_event.schema.json`                                                                                                                                             | **MUST pass schema validation**                   |
| **Level 2** | **Semantic Rules & Constraints**            | `docs/event_matrix.md`, `docs/schemas/event_matrix.yaml`, `docs/03_pld_event_spec.md`                                                                                            | **MUST satisfy semantic alignment**               |
| **Level 3** | **Operational Guidance & Metric Standards** | `docs/01_pld_for_agent_engineers.md`, `docs/07_pld_operational_metrics_cookbook.md`, `docs/schemas/metrics_schema.yaml`                                                          | Proposed canonical operational metric definitions |
| **Level 4** | **Examples and Illustrative Materials**     | `quickstart/hello_pld_runtime.py`, `quickstart/run_minimal_engine.py`, `quickstart/examples/minimal_pld_demo.py`, `quickstart/patterns/03_system/logging_and_schema_examples.md` | Informative only (non-normative)                  |


If conflicting conditions arise, apply the following resolution order:

> **Level 1 → Level 2 → Level 3 → Level 4**

---

## 2. Metric Specification Format (Required)

Each metric MUST follow this metadata template:

```
---
metric: <NAME>
version: <SEMVER>
status: <canonical|archived|experimental|deprecated>
validation_modes: [strict|warn|normalize]
output_unit: <percent|seconds|ratio|count>
output_range: <required value space>
schema_dependency: pld_event.schema.json
semantic_dependency: event_matrix.yaml + event_matrix.md
---
```

All metric formulas MUST be deterministic and computable solely from PLD-valid event streams.

---

## 3. Canonical Metrics (Baseline Proposal for v2.0)

These metrics represent the current recommended baseline for evaluating PLD-aligned systems and may be refined as broader implementation feedback emerges.

---

### 3.1 PRDR — Post-Repair Drift Recurrence

```
---
metric: PRDR
version: 2.0.0
status: proposed_canonical
validation_modes: [strict, warn]
output_unit: percent
output_range: [0.0, 100.0]
---
```

**Normative Definition:**

```
PRDR = (# of sessions where a repair event is followed by a drift event)
        ÷ (# of sessions containing at least one repair event)
      × 100
```

**Required Conditions:**

- Drift detection MUST occur after a repair event within the same session using strictly increasing `turn_sequence`.  
- A recurrence time window MAY be applied, but MUST be declared in metadata.

**Interpretation Guidance (Non-Normative):**

| Result | Meaning | Suggested Action |
|--------|---------|------------------|
| 🟢 0–10% | Durable repair behavior | No action |
| ⚠ 10–30% | Partial improvement | Evaluate drift detectors or repair policy |
| 🔴 >30% | Fragile repair strategy | Investigation recommended |

**Example SQL (Informative only):**

```sql
WITH repairs AS (
  SELECT session_id, turn_sequence AS repair_turn
  FROM pld_events
  WHERE event_type = 'repair_triggered'
),
drifts AS (
  SELECT DISTINCT r.session_id
  FROM repairs r
  JOIN pld_events e USING(session_id)
 WHERE e.turn_sequence > r.repair_turn
   AND e.event_type = 'drift_detected'
)
SELECT 
  (COUNT(*) * 100.0) / NULLIF((SELECT COUNT(*) FROM repairs), 0) AS prdr
FROM drifts;
```

---

### 3.2 VRL — Recovery Latency

Legacy VRL (“Visible Repair Load”) is archived. The revised definition measures **time to stabilization**.

```
---
metric: VRL
version: 2.0.0
status: proposed_canonical
output_unit: seconds
output_range: [0, ∞)
validation_modes: [strict, normalize]
---
```

**Normative Definition:**

```
VRL = mean( timestamp(recovery_event) - timestamp(initial_drift_event) )
```

Valid recovery events MUST be one of:

| event_type | phase |
|------------|--------|
| continue_allowed | continue |
| reentry_observed | reentry |

If no recovery occurs, serialize as `"NaN"`.

**Interpretation (Informative):**

| Time | Interpretation |
|------|---------------|
| 🟢 <2s | Fast and minimally perceptible |
| ⚠ 2–8s | Noticeable, borderline |
| 🔴 >8s | User-visible instability |

---

### 3.3 FR — Failover Recurrence Index

```
---
metric: FR
version: 2.0.0
status: proposed_canonical
output_unit: ratio
output_range: [0.0, ∞)
validation_modes: [strict]
---
```

**Normative Definition:**

```
FR = (# failover events)
     ÷ (# lifecycle events excluding phase="none")
```

**Threshold Guidance (Non-Normative):**

| Value | Meaning | Suggested Action |
|--------|---------|------------------|
| 🟢 0–5% | Expected variance | None |
| ⚠ 5–15% | Elevated | Review drift → repair cycle |
| 🔴 ≥15% | Possible systemic issue | Escalation recommended |

---

## 4. Archived Metrics

| Metric | Status | Notes |
|--------|--------|--------|
| REI | archived | MAY return in v2.0 depending on workload feedback |
| MRBF | archived | Deprecated due to overlap with VRL + PRDR |

---

## 5. Dashboard + BI Integration Layer (Informative)

This section supports implementation in:

- Grafana / Supabase / Looker / Metabase  
- Alerting and rollout guardrails  
- Visual exploration of event-driven metrics  

These artifacts operationalize metrics — they do not define them.

---

### 5.1 Operational Visualization Reference (Informative)

The following mock dashboard illustrates how the metrics defined in this document may be operationalized.  
This visualization is **not a requirement**, but a reference target to support early implementation efforts.

<p align="center">
<img src="assets/dashboard_mockup.svg" width="100%" />
</p>

Teams may begin with individual metric queries and expand toward full dashboards depending on maturity, tooling, and operational needs.


---

## 6. Version Lifecycle Table

| Metric | Current Version | Previous | Next Review |
|--------|----------------|----------|-------------|
| PRDR | 2.0.0 | 1.0.0 | 90-day |
| VRL | 2.0.0 | semantic fork (archived) | 180-day |
| FR | 2.0.0 | 1.0.0 | 90-day |

---

## 7. Revision Log

- v1.1: Early operational guidance version  
- v2.0: First combined normative + operational draft with versioned metrics

---

### Feedback & Iteration

This document remains a working draft.  
If you apply these metrics in real implementations or discover limitations, edge cases, or improvements, feedback is welcome and encouraged.

End of Document — v2.0 Draft
