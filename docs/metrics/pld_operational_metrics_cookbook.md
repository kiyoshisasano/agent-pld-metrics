# PLD Operational Metrics Cookbook

> **Scope:** Module-level runtime_template  
> **Status:** Draft (user-requested generation)  
> **Audience:** Runtime engineers and analysts integrating PLD operational metrics  

## 1. Overview

This cookbook provides module-scoped guidance for implementing and using PLD operational metrics within a runtime environment. It offers actionable examples derived from canonical PLD metrics while preserving Level 1–3 invariants.

Template Variant **B** focuses on **runtime-facing examples** and **module-local integration flows**.

## 2. Canonical Metrics Summary

### 2.1 Metric Metadata Template (Reference)

Module-level integrations SHOULD be aware of the metadata schema for PLD metrics. Runtime modules do **not** compute canonical metrics but may rely on this structure for advisory state tracking.

```
---
metric: <NAME>
version: <SEMVER>
status: <canonical|archived|experimental|deprecated>
validation_modes: [strict|warn|normalize]
output_unit: <percent|seconds|ratio|count>
output_range: <value space>
schema_dependency: pld_event.schema.json
semantic_dependency: event_matrix.yaml + event_matrix.md
---
```

### 2.2 Recovery Event Reference (For Runtime Advisory)

Runtime modules MAY treat the following as **recovery-class events** when computing advisory latency samples:

| event_type       | phase    |
| ---------------- | -------- |
| continue_allowed | continue |
| reentry_observed | reentry  |

These definitions are normative at Level 3 and MUST NOT be changed in runtime code.

* **PRDR** — Post-Repair Drift Recurrence
* **VRL** — Recovery Latency
* **FR** — Failover Recurrence

Each metric operates only on **PLD-valid events** and MUST follow ordering by `turn_sequence`.

## 3. Runtime Module Integration Patterns

This section outlines module-level patterns for computing and emitting operational metrics.

### 3.1 Local Runtime Metric Snapshot

A runtime module may attach ephemeral metrics snapshots under the `runtime` block of the event:

```yaml
runtime:
  latency_ms: <number>
  model: <string>
  module_metric_state:
    active_repair_count: <int>
    recent_drift_codes: <list>
```

These fields are advisory and MUST NOT conflict with Level 3 metrics rules.

### 3.2 Module-Level PRDR Detection (Advisory)

Modules may track transitions:

```
repair_triggered → drift_detected
```

and update a local counter.

```python
module_state["repair_count"] += 1
if event.event_type == "drift_detected":
    module_state["post_repair_drift"] += 1
```

### 3.3 VRL_TurnDistance (Advisory Estimator)

This estimator measures **turn-distance from the onset of drift episodes**.
It is **not** the canonical VRL metric (which is timestamp-based and analytics-only).

Modules maintain an `initial_drift_turn` marker and compute turn-distance until recovery:

```python
if event.event_type == "drift_detected":
    # Record initial drift only (do not overwrite subsequent drifts)
    if module_state.get("initial_drift_turn") is None:
        module_state["initial_drift_turn"] = event.turn_sequence
elif event.event_type in ("reentry_observed", "continue_allowed"):
    start = module_state.get("initial_drift_turn")
    if start is not None:
        vrl_turns = event.turn_sequence - start  # advisory estimator
        module_state["vrl_samples"].append(vrl_turns)
        # reset for next drift episode
        module_state["initial_drift_turn"] = None
```

### 3.4 Failover Recurrence (FR) Advisory Tracking

Modules may count failover events and lifecycle events:

```python
if event.event_type == "failover_triggered":
    module_state["failover_count"] += 1
if event.pld.phase in ("drift", "repair", "reentry", "continue", "outcome", "failover"):
    module_state["lifecycle_events"] += 1
```

## 4. Export Patterns

Modules SHOULD NOT write metric results directly into canonical logs.
They MAY:

* expose `/metrics` endpoints,
* attach snapshots to `runtime` block,
* emit module-specific INFO events using M-prefix codes (phase=`none`).

Example advisory emission:

```python
event = bridge.build_event(
    signal=RuntimeSignal(
        kind=SignalKind.INFO,
        payload={"module_vrl_mean": mean(vrl_samples)},
    ),
    context=context,
)
```

## 5. Validation Rules for Module-Scope Metrics

The following constraints reflect Level 3 normative specifications; runtime modules implement only advisory behavior and therefore must not alter canonical semantics.

* MUST NOT redefine lifecycle semantics.
* MUST NOT introduce new taxonomy prefixes.
* MUST NOT mutate PLD event fields.
* MAY maintain local counters, windows, and state.

---

## 6. Canonical Metric Definitions (Analytics-Only — Runtime MUST NOT Compute)

Runtime implementations may maintain advisory estimators (Section 3), but **canonical metrics are computed exclusively in analytics layers**. (Normative Reference – Appendix)
Runtime modules MUST NOT compute canonical metrics directly. They MAY maintain advisory counters that analytics layers later use.

### 6.1 PRDR — Post-Repair Drift Recurrence (Reference)

```
PRDR = (# of sessions where a repair event is followed by a drift event)
        ÷ (# of sessions containing at least one repair event)
      × 100
```

Required conditions:

* drift must occur **after** repair in the same session
* ordering enforced via `turn_sequence`

### 6.2 VRL — Recovery Latency (Reference)

```
VRL = mean( timestamp(recovery_event) - timestamp(initial_drift_event) )
```

Recovery events:

* continue_allowed
* reentry_observed

### 6.3 FR — Failover Recurrence (Reference)

```
FR = (# failover events)
     ÷ (# lifecycle events excluding phase="none")
```

Runtime guidance mirrors Level 3 normative definitions; modules may track advisory counts, but canonical lifecycle semantics remain fixed at the specification layer.

* MUST NOT redefine lifecycle semantics
* MUST NOT introduce new taxonomy prefixes
* MUST NOT mutate PLD event fields
* MAY maintain local counters, windows, and state

## 7. Metric Version Awareness (Module Guidance)

Runtime modules SHOULD be aware of the maturity of canonical metrics:

| Metric | Version | Review Interval |
| ------ | ------- | --------------- |
| PRDR   | 2.0.0   | 90-day          |
| VRL    | 2.0.0   | 180-day         |
| FR     | 2.0.0   | 90-day          |

---

## 8. Appendix: Recommended Module State Structure

```json
{
  "repair_count": 0,
  "post_repair_drift": 0,
  "vrl_samples": [],
  "failover_count": 0,
  "lifecycle_events": 0,
  "initial_drift_turn": null
}
```


End of Document — v2.0 Draft
