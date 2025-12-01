# PLD v2 Traceability Map

**Document Role:** Alignment and validation reference across Metrics, Taxonomy, and Event Matrix.
**Authority Level:** Level 3 — Derived Specification (subordinate to Level 1 + Level 2).
**Status:** Normative for metrics and observability.

---

## 1. Purpose

This document ensures traceability between:

* **Metrics definitions**
* **PLD Taxonomy v2 code structure**
* **Event Matrix semantic rules**

This enables consistent validation, auditing, and governance alignment. Metrics MUST follow phase and event-type semantics defined in Level-2 Event Matrix and MAY use taxonomy numeric groupings for segmentation.

---

## 2. Core Alignment Principles

| Rule                                                                            | Enforcement Level | Meaning                                                         |
| ------------------------------------------------------------------------------- | ----------------- | --------------------------------------------------------------- |
| Metrics MUST align with lifecycle semantics from the Event Matrix               | MUST              | Metrics eligibility derives from event_type + phase constraints |
| Taxonomy prefixes MAY support grouping but MUST NOT change eligibility          | SHOULD/MAY        | Prefix is advisory classification, not validation logic         |
| Numeric classifier segments (e.g., D1–D5, R1–R5) MAY be used for analytics only | MAY               | Optional segmentation, not required for correctness             |
| Pending taxonomy codes MUST remain opaque and MUST NOT alter metric logic       | MUST              | Metrics must treat these as non-semantic identifiers            |

---

## 3. Lifecycle → Event Type → Metric Mapping Table

| Lifecycle Phase      | Allowed Event Types (per Event Matrix)                          | Valid Prefix (Taxonomy) | Metrics Associated                                                                               |
| -------------------- | --------------------------------------------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------ |
| drift                | drift_detected, drift_escalated                                 | D*                      | drift_events_count, drift_detected_count, drift_escalated_count                                  |
| repair               | repair_triggered, repair_escalated                              | R*                      | repair_events_count, repair_triggered_count, repair_escalated_count                              |
| reentry              | reentry_observed                                                | RE*                     | reentry_events_count, reentry_observed_count                                                     |
| continue             | continue_allowed, continue_blocked                              | C*                      | continue_events_count, continue_allowed_count, continue_blocked_count                            |
| outcome              | evaluation_pass, evaluation_fail, session_closed                | O*                      | outcome_events_count, evaluation_pass_count, evaluation_fail_count, session_closed_outcome_count |
| failover             | failover_triggered (MUST); fallback_executed (MAY)              | F*                      | failover_events_count, failover_triggered_count, fallback_executed_failover_count                |
| none (observability) | latency_spike, pause_detected, handoff, fallback_executed, info | INFO*, SYS*, etc.       | latency_spike_count, pause_detected_count, handoff_count, fallback_executed_count, info_count    |

---

## 4. Eligibility Logic Summary

A metric MUST count an event if:

```
schema_valid(event)
AND event_type is included in metric definition
AND phase alignment satisfies MUST/SHOULD rules (per validation_mode)
```

Taxonomy prefix and numeric classifier MUST NOT determine eligibility.
They MAY assist grouping or drill-down analysis.

---

## 5. Validation Modes Impact

| Validation Mode | Behavior                                      | Notes                                                     |
| --------------- | --------------------------------------------- | --------------------------------------------------------- |
| strict          | Only semantically compliant events contribute | Provisional taxonomy codes allowed but ignored for logic  |
| warn            | SHOULD violations included with warnings      | Useful for staging and integration                        |
| normalize       | System MAY infer or correct phase mappings    | MUST NOT normalize provisional or pending taxonomy values |

---

## 6. Governance Notes

* Metrics MUST remain aligned with Level-1 schema and Level-2 event semantics.
* If taxonomy evolves, metrics MUST NOT change eligibility rules.
* Provisional categories MAY be referenced but MUST NOT become canonical without governance approval.
* Pending taxonomy items MUST NOT be used as classifier dimensions or eligibility conditions.

---

## 7. Future Auditing Requirements

* Ensure periodic alignment checks across:

  * event_matrix.yaml
  * PLD_taxonomy_v2.0.md
  * metrics_schema.yaml
* A review MUST occur if:

  * New event types are added
  * Numeric families expand
  * Any lifecycle semantic changes occur

---

**End of Document**
