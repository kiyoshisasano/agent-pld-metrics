# **PLD_Runtime_Standard_v2.0**

## **Front Matter**

This document defines operational rules for PLD-compatible agent runtimes.

It is normative.

It SHALL NOT modify or override Level-1 or Level-2 specifications.

It applies to runtime systems generating, validating, transforming, or consuming PLD events.

This document SHALL defer to: `pld_event.schema.json` and `event_matrix.yaml`.  
Version Update: v2.0.1 (Final Resolution Pass, Ready for v2.1 Proposal)

## **Authority & Conformance Rules**

**AUTH-001** — MUST follow Level-1 schema and Level-2 matrix constraints.

**AUTH-002** — MUST reject runtime interpretations that contradict Level-1 or Level-2.

**AUTH-003** — SHOULD support all canonical taxonomy values.

**AUTH-004** — MAY support provisional taxonomy values when marked as such.

**AUTH-005** — MUST NOT operationalize pending taxonomy entries.

## **Canonical Rules Section**

→ SHALL reference `event_matrix.yaml` for lifecycle semantics.  
→ Table rows are normative.

### **Canonical Phase–Event–Code Enforcement Table**

| CAN-ID | event_type | required phase | allowed prefix | enforcement | notes |
| :---- | :---- | :---- | :---- | :---- | :---- |
| ... | ... | ... | ... | ... | ... |
| **CAN-005** | continue_allowed | continue | C | MUST | **C0 numeric exemption applies (See Appendix)** |
| ... | ... | ... | ... | ... | ... |

## **Runtime Operational Rules**

→ SHALL reference `PLD_taxonomy_v2.0.md` for full code semantics and governance.

**RUN-001** — Event serialization MUST conform to the Level-1 schema.

**RUN-002** — Phase assignment MUST conform to the Level-2 matrix.

**RUN-003 — EXCEPTION RULE C0:**  
Runtimes MUST treat `C0_normal`, `C0_user_turn`, and `C0_system_turn` as semantically distinct, non-overlapping continue events, despite the non-unique numeric segment. This is governed by the Level-3 taxonomy.

**RUN-004** — Event `pld.code` (e.g., `D4_tool_error`) MUST be lowercase snake_case.

**RUN-005** — Runtimes generating Observability/Derived Metrics MUST use the `M` prefix and `event_type: info`, mapping to `phase: none`.

## **Metrics Alignment Rules**

→ SHALL reference `PLD_metrics_spec.md` and `metrics_schema.yaml`.

**MET-001** — Metrics MUST derive only from PLD-valid events.

**MET-002** — Event contribution MUST follow lifecycle mapping.

**MET-003** — Observability events MAY contribute only to observability metric groups.

**MET-004** — Phase inference MUST NOT override Level-2 constraints.

**MET-005** — Metric definitions MUST NOT redefine lifecycle semantics.

## **Governance Notes**

**GOV-001** — Canonical entries SHALL define operational enforcement.

**GOV-002** — Provisional entries SHALL remain allowed and marked experimental.

**GOV-003 — RESOLVED:**  
All pending taxonomy conflicts (D0/D5) are now resolved and classified as Provisional codes (`D0`, `D6`, `D99`, `M*`). The Pending state is now clearly defined.

**GOV-004** — Changes to this document require governance approval.

## **Appendix: Provisional Codes (Non-Normative)**

The following taxonomy elements are currently defined but remain in the Provisional Registry.  
Runtimes MAY use them, but MUST NOT rely on their stability until full Canonicalization (v2.1).

* **Drift/Deviation:** `D0_none`, `D6_information`, `D9_unspecified`, `D99_data_quality_error`  
* **Observability/Derived:** `M1_PRDR`, `M2_VRL`, `M3_CRR`  
* **Other Provisional:** `D5_latency_spike` (now stable)

## **Appendix: Retired/Resolved Codes (For Historical Reference Only)**

The following previously conflicting or under-specified codes have been retired by the Final Resolution Pass:

* `D5_information` (Retired, replaced by `D6_information`)  
* `D0_unspecified` (Retired, replaced by `D99_data_quality_error`)

**Confidence Score: 4.7 / 5**

