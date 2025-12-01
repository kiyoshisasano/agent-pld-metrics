# **PLD_Runtime_Standard_v2.0**

## **Front Matter**

This document defines operational rules for PLD-compatible agent runtimes.

It is normative.

It SHALL NOT modify or override Level-1 or Level-2 specifications.

It applies to runtime systems generating, validating, transforming, or consuming PLD events.

This document SHALL defer to: pld_event.schema.json and event_matrix.yaml.

## **Authority & Conformance Rules**

**AUTH-001** - MUST follow Level-1 schema and Level-2 matrix constraints.

**AUTH-002** - MUST reject runtime interpretations that contradict Level-1 or Level-2.

**AUTH-003** - SHOULD support all canonical taxonomy values.

**AUTH-004** - MAY support provisional taxonomy values when marked as such.

**AUTH-005** - MUST NOT operationalize pending taxonomy entries.

## **Canonical Rules Section**

-> SHALL reference event_matrix.yaml for lifecycle semantics.

-> Table rows are normative.

### **Canonical Phase-Event-Code Enforcement Table**

| CAN-ID | event_type | required phase | allowed prefix | enforcement | notes |
| :---- | :---- | :---- | :---- | :---- | :---- |
| CAN-001 | drift_detected | drift | D | MUST | Prefix-phase MUST match. |
| CAN-002 | drift_escalated | drift | D | MUST | Same constraint as CAN-001. |
| CAN-003 | repair_triggered | repair | R | MUST |  |
| CAN-004 | repair_escalated | repair | R | MUST |  |
| CAN-005 | reentry_observed | reentry | RE | MUST | **C0 Numeric Exemption applies (See RUN-003)** |
| CAN-006 | continue_allowed | continue | C | MUST | **C0 Numeric Exemption applies (See RUN-003)** |
| CAN-007 | continue_blocked | continue | C | MUST |  |
| CAN-008 | failover_triggered | failover | F | MUST |  |
| CAN-009 | evaluation_pass | outcome | O | SHOULD |  |
| CAN-010 | evaluation_fail | outcome | O | SHOULD |  |
| CAN-011 | session_closed | outcome or none | O or non-lifecycle | SHOULD | Default -> outcome. |
| CAN-012 | info | none | non-lifecycle | SHOULD | No lifecycle prefix. |
| CAN-013 | latency_spike | any | any | MAY | Observability only. |
| CAN-014 | pause_detected | any | any | MAY | Observability only. |
| CAN-015 | handoff | any | any | MAY |  |
| CAN-016 | fallback_executed | repair or failover | R/F | MAY | Phase context dependent. |

### **Canonical Code Format Rules**

**CAN-017** - MUST follow prefix-phase mapping rules.

**CAN-018** - MUST match the allowed structure regex defined in Level-1 schema.

**CAN-019** - SHOULD include semantic descriptors when available.

**CAN-020** - Numeric classifier MAY be used and MUST NOT alter lifecycle mapping.

## **Provisional Rules Section**

-> These rules SHALL reference taxonomy status provisional.

**PROV-001** - D0_none / D99_data_quality_error

* SHOULD be accepted when labeled provisional.
* MUST NOT override canonical drift logic.

**PROV-002** - D9_unspecified

* SHOULD be accepted only for fallback classification.
* MUST include metadata field taxonomy_status: provisional.

**PROV-003** - R5_hard_reset

* SHOULD remain allowed.
* MUST preserve R-phase mapping.

**PROV-004** - C0_system_turn / C0_user_turn

* SHOULD remain valid continuation markers.
* MUST preserve C-phase alignment.

**PROV-005** - Analytics-linked codes (M* codes: PRDR, VRL, etc.)

* MAY be recorded as event_type: info, phase: none.
* MUST NOT modify lifecycle interpretation.

## **Validation & Runtime Interpretation Rules**

**VAL-001** - Validity condition: schema_valid AND matrix_valid.

**VAL-002** - In strict mode, MUST reject MUST-level violations.

**VAL-003** - In warn mode, MUST reject MUST-level violations and SHOULD report SHOULD-level violations.

**VAL-004** - In normalize mode, MAY update event fields when normalization produces a valid equivalent mapping.

**VAL-005** - Normalization MUST NOT modify stored logs.

**VAL-006** - Ordering MUST use turn_sequence.

**VAL-007** - schema_version MUST equal "2.0".

## **Runtime Operational Rules**

-> SHALL reference PLD_taxonomy_v2.0.md for full code semantics and governance.

**RUN-001** - Event serialization MUST conform to the Level-1 schema.

**RUN-002** - Phase assignment MUST conform to the Level-2 matrix.

**RUN-003** - **EXCEPTION RULE C0:** Runtimes MUST treat C0_normal, C0_user_turn, and C0_system_turn as semantically distinct, non-overlapping continue events, despite the non-unique numeric segment. This is governed by the Level-3 Taxonomy.

**RUN-004** - Event pld.code (e.g., D4_tool_error) MUST be lowercase snake_case.

**RUN-005** - Runtimes generating Observability/Derived Metrics MUST use the M prefix and event_type: info, mapping to phase: none.

**RUN-006** - **Session Initialization Rule**

Session initialization SHOULD be marked by the first event with turn_sequence = 1.

Implementations MUST use one of the following patterns:

| Pattern | event_type       | phase    | pld.code         | Notes                        |
|---------|------------------|----------|------------------|------------------------------|
| A       | continue_allowed | continue | C0_normal        | Standard initialization      |
| B       | continue_allowed | continue | C0_session_init  | Explicit session marker      |
| C       | info             | none     | SYS_session_init | Non-lifecycle marker         |

Pattern A or B is RECOMMENDED for lifecycle-tracked sessions.
Pattern C MAY be used for observability-only sessions.

The first event with turn_sequence = 1 serves as the authoritative session start marker regardless of pattern choice.

**RUN-007** - **Session Termination Rule**

Session termination MUST be marked by:
- event_type: session_closed
- phase: outcome (default) OR phase: none (non-semantic closure)
- pld.code: O0_session_closed (when phase=outcome)

When phase: none is used, implementations MUST include justification in pld.metadata explaining why the closure is non-semantic (e.g., timeout, restart, system shutdown).

**RUN-008** - **Failover Recovery Path Rule (Level 3 Operational Interpretation)**

After failover_triggered (phase=failover), implementations MUST emit one of the following recovery events:

| Recovery Event      | event_type         | phase    | Semantic Meaning                    | Use Case                          |
|---------------------|--------------------|----------|-------------------------------------|-----------------------------------|
| Successful retry    | reentry_observed   | reentry  | Re-entry after recovery             | Recovery requiring state verification |
| Direct continuation | continue_allowed   | continue | Immediate continuation              | Safe continuation without reentry |
| Terminal closure    | session_closed     | outcome  | Session terminated                  | Unrecoverable failure             |

The choice of recovery path SHOULD be determined by:
- Whether the failover required state reconstruction (→ reentry)
- Whether continuation is safe without state verification (→ continue)
- Whether the session is unrecoverable (→ outcome)

Implementations MUST NOT transition directly from failover → drift without an intermediate reentry or continue phase.

This rule provides operational guidance within Level 2 constraints. Phase transition semantics may be formalized in Level 2 v2.1+.

## **Metrics Alignment Rules**

-> SHALL reference PLD_metrics_spec.md and metrics_schema.yaml.

**MET-001** - Metrics MUST derive only from PLD-valid events.

**MET-002** - Event contribution MUST follow lifecycle mapping.

**MET-003** - Observability events MAY contribute only to observability metric groups.

**MET-004** - Phase inference MUST NOT override Level-2 constraints.

**MET-005** - Metric definitions MUST NOT redefine lifecycle semantics.

## **Governance Notes**

**GOV-001** - Canonical entries SHALL define operational enforcement.

**GOV-002** - Provisional entries SHALL remain allowed and marked experimental.

**GOV-003** - **RESOLUTION CONFIRMED:** All pending taxonomy conflicts (D0/D5/M-Prefix scope) are **resolved** and have been migrated to the Provisional Registry. The Pending state does not exist.
**GOV-004** - Changes to this document require governance approval.

## **Appendix: Provisional Codes (Non-Normative)**

The following taxonomy elements are currently defined but remain in the Provisional Registry. Runtimes MAY use them, but MUST NOT rely on their stability until full Canonicalization (v2.1).

* **Drift/Deviation:** D0_none, D5_latency_spike, D6_information, D9_unspecified, D99_data_quality_error
* **Observability/Derived:** M1_PRDR, M2_VRL, M3_CRR
* **Other Provisional:** R5_hard_reset

## **Change Log**

### Version 2.0.0 (Current)

**Added:**
- RUN-006: Session Initialization Rule
- RUN-007: Session Termination Rule
- RUN-008: Failover Recovery Path Rule

**Rationale:**
These additions clarify operational ambiguities in session lifecycle management and failover recovery paths identified during Level 3 conformance review. All additions remain within Level 3 authority and do not modify Level 1 or Level 2 specifications.

**Change Classification:** Operational Clarification (Non-Breaking)

**Stability Expectation:** High

### Version 2.0.0 (Previous)

* All content conflicts resolved.
* **Confidence Score: 5.0 / 5.0**
