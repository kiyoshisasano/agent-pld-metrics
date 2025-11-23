# **PLD_Runtime_Standard_v2.0**

---

## **Front Matter**

This document defines operational rules for PLD-compatible agent runtimes.  
It is normative.  
It SHALL NOT modify or override Level-1 or Level-2 specifications.  
It applies to runtime systems generating, validating, transforming, or consuming PLD events.  
This document SHALL defer to: `pld_event.schema.json` and `event_matrix.yaml`.

---

## **Authority & Conformance Rules**

**AUTH-001**  
- MUST follow Level-1 schema and Level-2 matrix constraints.

**AUTH-002**  
- MUST reject runtime interpretations that contradict Level-1 or Level-2.

**AUTH-003**  
- SHOULD support all canonical taxonomy values.

**AUTH-004**  
- MAY support provisional taxonomy values when marked as such.

**AUTH-005**  
- MUST NOT operationalize pending taxonomy entries.

---

## **Canonical Rules Section**

→ SHALL reference `event_matrix.yaml` for lifecycle semantics.  
→ Table rows are normative.

### **Canonical Phase–Event–Code Enforcement Table**

| CAN-ID | event_type | required phase | allowed prefix | enforcement | notes |
|--------|------------|---------------|----------------|-------------|-------|
| CAN-001 | drift_detected | drift | D | MUST | Prefix–phase MUST match. |
| CAN-002 | drift_escalated | drift | D | MUST | Same constraint as CAN-001. |
| CAN-003 | repair_triggered | repair | R | MUST | |
| CAN-004 | repair_escalated | repair | R | MUST | |
| CAN-005 | reentry_observed | reentry | RE | MUST | |
| CAN-006 | continue_allowed | continue | C | MUST | |
| CAN-007 | continue_blocked | continue | C | MUST | |
| CAN-008 | failover_triggered | failover | F | MUST | |
| CAN-009 | evaluation_pass | outcome | O | SHOULD | |
| CAN-010 | evaluation_fail | outcome | O | SHOULD | |
| CAN-011 | session_closed | outcome or none | O or none-prefix | SHOULD | Default → outcome. |
| CAN-012 | info | none | non-lifecycle | SHOULD | No lifecycle prefix. |
| CAN-013 | latency_spike | any | any | MAY | Observability only. |
| CAN-014 | pause_detected | any | any | MAY | Observability only. |
| CAN-015 | handoff | any | any | MAY | |
| CAN-016 | fallback_executed | repair or failover | R/F | MAY | Phase context dependent. |

### Canonical Code Format Rules

**CAN-017**  
- MUST follow prefix–phase mapping rules.

**CAN-018**  
- MUST match the allowed structure regex defined in Level-1 schema.

**CAN-019**  
- SHOULD include semantic descriptors when available.

**CAN-020**  
- Numeric classifier MAY be used and MUST NOT alter lifecycle mapping.

---

## **Provisional Rules Section**

→ These rules SHALL reference taxonomy status `provisional`.

**PROV-001**  
- `D0_none`  
- SHOULD be accepted when labeled provisional.  
- MUST NOT override canonical drift logic.

**PROV-002**  
- `D9_unspecified`  
- SHOULD be accepted only for fallback classification.  
- MUST include metadata field `taxonomy_status: provisional`.

**PROV-003**  
- `R5_hard_reset`  
- SHOULD remain allowed.  
- MUST preserve R-phase mapping.

**PROV-004**  
- `C0_system_turn` / `C0_user_turn`  
- SHOULD remain valid continuation markers.  
- MUST preserve C-phase alignment.

**PROV-005**  
- Analytics-linked codes (PRDR, VRL, etc.)  
- MAY be recorded but MUST NOT modify lifecycle interpretation.

---

## **Validation & Runtime Interpretation Rules**

**VAL-001**  
- Validity condition: `schema_valid ∧ matrix_valid`.

**VAL-002**  
- In `strict` mode, MUST reject MUST-level violations.

**VAL-003**  
- In `warn` mode, MUST reject MUST-level violations and SHOULD report SHOULD-level violations.

**VAL-004**  
- In `normalize` mode, MAY update event fields when normalization produces a valid equivalent mapping.

**VAL-005**  
- Normalization MUST NOT modify stored logs.

**VAL-006**  
- Ordering MUST use `turn_sequence`.

**VAL-007**  
- `schema_version` MUST equal `"2.0"`.

---

## **Metrics Alignment Rules**

→ SHALL reference `PLD_metrics_spec.md` and `metrics_schema.yaml`.

**MET-001**  
- Metrics MUST derive only from PLD-valid events.

**MET-002**  
- Event contribution MUST follow lifecycle mapping.

**MET-003**  
- Observability events MAY contribute only to observability metric groups.

**MET-004**  
- Phase inference MUST NOT override Level-2 constraints.

**MET-005**  
- Metric definitions MUST NOT redefine lifecycle semantics.

---

## **Governance Notes**

**GOV-001**  
- Canonical entries SHALL define operational enforcement.

**GOV-002**  
- Provisional entries SHALL remain allowed and marked experimental.

**GOV-003**  
- Pending taxonomy MUST NOT be treated as operational.

**GOV-004**  
- Changes to this document require governance approval.

---

## **Appendix: Pending Codes (Non-Normative)**

The following taxonomy elements are not approved for operational enforcement:

- `D5_latency_spike`
- `D5_information`
- `session_closure_typology`
- `failure_mode_clustering`
- `continue_repair_ratio`
- `VRL/PRDR elevation candidates`

These MAY appear in telemetry or research datasets but MUST NOT affect runtime behavior.

---

## **Change Log + Confidence**

- Content rewritten from previous draft to rule-based format.  
- Canonical + provisional enforcement aligned with T2.  
- No schema or matrix changes made.

**Confidence Score: 4.7 / 5**
