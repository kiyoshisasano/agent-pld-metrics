\===== FILE: 01\_PLd\_for\_Agent\_Engineers\_v2.0.md \=====

# **01\_PLd\_for\_Agent\_Engineers\_v2.0**

## **Front Matter**

This document defines operational rules for PLD-compatible agent runtimes.

It is normative.

It SHALL NOT modify or override Level-1 or Level-2 specifications.

It applies to runtime systems generating, validating, transforming, or consuming PLD events.

This document SHALL defer to: pld\_event.schema.json and event\_matrix.yaml.  
Version Update: v2.0.1 (Final Resolution Pass, Ready for v2.1 Proposal)

## **Authority & Conformance Rules**

**AUTH-001** \- MUST follow Level-1 schema and Level-2 matrix constraints.

**AUTH-002** \- MUST reject runtime interpretations that contradict Level-1 or Level-2.

**AUTH-003** \- SHOULD support all canonical taxonomy values.

**AUTH-004** \- MAY support provisional taxonomy values when marked as such.

**AUTH-005** \- MUST NOT operationalize pending taxonomy entries.

## **Canonical Rules Section**

→ SHALL reference event\_matrix.yaml for lifecycle semantics.

→ Table rowsは規範的です。

### **Canonical Phase–Event–Code Enforcement Table**

| CAN-ID | event\_type | required phase | allowed prefix | enforcement | notes |
| :---- | :---- | :---- | :---- | :---- | :---- |
| ... | ... | ... | ... | ... | ... |
| **CAN-005** | continue\_allowed | continue | C | MUST | **C0 numeric exemption applies (See Appendix)** |
| ... | ... | ... | ... | ... | ... |

## **Runtime Operational Rules**

→ SHALL reference PLD\_taxonomy\_v2.0.md for full code semantics and governance.

**RUN-001** \- Event serialization MUST conform to the Level-1 schema.

**RUN-002** \- Phase assignment MUST conform to the Level-2 matrix.

**RUN-003** \- **EXCEPTION RULE C0:** Runtimes MUST treat C0\_normal, C0\_user\_turn, and C0\_system\_turn as semantically distinct, non-overlapping continue events, despite the non-unique numeric segment. This is governed by the Level-3 Taxonomy.

**RUN-004** \- Event pld.code (e.g., D4\_tool\_error) MUST be lowercase snake\_case.

**RUN-005** \- Runtimes generating Observability/Derived Metrics MUST use the M prefix and event\_type: info, mapping to phase: none.

## **Metrics Alignment Rules**

→ SHALL reference PLD\_metrics\_spec.md and metrics\_schema.yaml.

**MET-001** \- Metrics MUST derive only from PLD-valid events.

**MET-002** \- Event contribution MUST follow lifecycle mapping.

**MET-003** \- Observability events MAY contribute only to observability metric groups.

**MET-004** \- Phase inference MUST NOT override Level-2 constraints.

**MET-005** \- Metric definitions MUST NOT redefine lifecycle semantics.

## **Governance Notes**

**GOV-001** \- Canonical entries SHALL define operational enforcement.

**GOV-002** \- Provisional entries SHALL remain allowed and marked experimental.

**GOV-003** \- **RESOLVED:** All pending taxonomy conflicts (D0/D5) are now resolved and classified as Provisional codes (D0, D6, D99, M\*). The Pending状態は明確になりました。

**GOV-004** \- Changes to this document require governance approval.

## **Appendix: Provisional Codes (Non-Normative)**

The following taxonomy elements are currently defined but remain in the Provisional Registry. Runtimes MAY use them, but MUST NOT rely on their stability until full Canonicalization (v2.1).

* **Drift/Deviation:** D0\_none, D6\_information, D9\_unspecified, D99\_data\_quality\_error  
* **Observability/Derived:** M1\_PRDR, M2\_VRL, M3\_CRR  
* **Other Provisional:** D5\_latency\_spike (now stable)

## **Appendix: Retired/Resolved Codes (For Historical Reference Only)**

The following previously conflicting or under-specified codes have been retired by the Final Resolution Pass:

* D5\_information (Retired, replaced by D6\_information)  
* D0\_unspecified (Retired, replaced by D99\_data\_quality\_error)
**Confidence Score: 4.7 / 5**
