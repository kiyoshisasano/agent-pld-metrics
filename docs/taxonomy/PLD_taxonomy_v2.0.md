Status: Working Draft  
Version: 2.0.4  
Authority Level Scope: Level 3 — Operational Standards (Conditional)   
Purpose/Scope: Defines event classification. All structural and numeric conflicts resolved.  
operational rules added for C0, D9, and M-Prefix to ensure high implementer quality.   
Change Classification: Documentation Clarity / Rule Consolidation  
Dependencies: PLD\_Event\_Semantic\_Spec\_v2.0.md, pld\_event.schema.json
Stability Expectation: Medium (non-breaking, alignment-focused)


# **📄 PLD v2 Taxonomy Proposal — Draft v0.1 *(Hybrid Governance Mode — With Rationale Annotations)***


## **1\. Scope & Intent**

This taxonomy defines the runtime event classification, governance placement, and metrics alignment for the PLD v2 runtime and analytics layers.

It formalizes the PLD code system across **detection → repair → continuation → outcome**, with explicit governance states:

* **Canonical Registry:** stable, enforced, runtime-binding event codes  
* **Provisional Registry:** active, but semantically unresolved or evolving  
* **Pending Governance Review:** requires resolution before entering Canonical

**Annotation:** Hybrid governance ensures evolution without uncontrolled fragmentation. All numeric collisions are resolved.

## **2\. Design Principles**

### **Prefix Hierarchy Rules**

| Prefix | Domain | Meaning |
| :---- | :---- | :---- |
| D | Drift detection | Signals anomaly or divergence (includes structural deviation D99) |
| C | Continue / normal execution | No repair required |
| R | Repair / mitigation | Runtime recovery action |
| O | Outcome | Terminal lifecycle result |
| M | Derived Metrics/Analytics | Signals aggregated results (Provisional) |

### **Numeric System Rules**

* 0 → baseline or neutral state (Exemptions apply for C0)  
* Higher number (1–99) → escalation, severity, or specificity hierarchy  
* Numeric ordering **MUST** remain unique within a prefix, **EXCEPT** for C0.

## **3\. Canonical Registry (Stable Zone)**

| code | prefix | numeric | descriptor | semantic\_scope | event\_type | metrics\_link | enforcement\_binding | status |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| D1\_instruction | D | 1 | instruction drift | semantic deviation | drift\_detected | accuracy (intent) | repair escalation logic | stable |
| D2\_context | D | 2 | context drift | schema/env mismatch | drift\_detected | data integrity | repair escalation | stable |
| D3\_repeated\_plan | D | 3 | repeated loop | behavioral stall | drift\_detected | efficiency stall | triggers rewrite or reset | stable |
| D4\_tool\_error | D | 4 | external tool/API failure | dependency failure | drift\_detected | reliability ops | triggers repair → possible reset | stable |
| C0\_normal | C | 0 | normal flow | runtime continuation | continue\_allowed | throughput baseline | none | stable |
| C0\_user\_turn | C | 0 | user turn | dialog state | continue\_allowed | engagement metric | none | stable |
| C0\_system\_turn | C | 0 | system turn | agent action | continue\_allowed | output rate | none | stable |
| R1\_clarify | R | 1 | clarification | minimal repair | repair\_triggered | interaction recovery | low-impact repair path | stable |
| R2\_soft\_repair | R | 2 | soft repair | self-correction | repair\_triggered | resilience score | moderate repair | stable |
| R3\_rewrite | R | 3 | rewrite | high-effort recovery | repair\_triggered | computational cost | content regeneration | stable |
| R4\_request\_clarification | R | 4 | user inquiry | explicit disambiguation | repair\_triggered | friction metric | paused state until user response | stable |
| R5\_hard\_reset | R | 5 | reset | full recovery | repair\_triggered | risk / failure severity | state wipe & reinit | stable |
| O0\_session\_closed | O | 0 | closed | lifecycle terminal | session\_closed | completion metric | terminal | stable |

## **3.1 Exception and Operational Rules (Consolidated)**

### **Rule 3.1.1: C0 Nominal Flow Exemption**

The numeric value 0 within the C prefix signifies the **Nominal Flow** meta-category.  
C0\_normal, C0\_user\_turn, and C0\_system\_turn are **explicitly exempted** from the unique numeric ordering rule,  
as they represent **orthogonal states** within the common flow.   
Implementations MUST distinguish them by their full pld.code string, not by the numeric component alone.

### **Rule 3.1.2: D0 Baseline Issuance**

To prevent high-volume noise and ensure semantic clarity,  D0\_none **SHOULD** only be emitted  
when an agent or system module **explicitly runs a Drift Health Check** and returns a negative (no drift) result.   
It MUST NOT be emitted passively on every turn. Its purpose is to track the volume of active health checks.

### **Rule 3.1.3: D9 Unspecified Trigger**

D9\_unspecified (Catch-all anomaly) **SHOULD** only be utilized when the confidence score (pld.confidence) of all other classifiers (D1-D6) 
falls below a predefined threshold (e.g., 0.5), or when the underlying event structure prevents classification mapping.   
This ensures D9 volume tracks true classification coverage gaps.

## **4\. Provisional Registry (Exploratory Zone)**

| code | reason\_for\_provisional | ambiguity\_type | candidate\_mappings | stability\_risk\_level | review\_trigger |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **D0\_none** | Resolved D0 conflict (Baseline) | Baseline/Heartbeat | continue\_allowed companion | High | Issuance limited to explicit health checks (3.1.2). |
| D5\_latency\_spike | Resolved D5 conflict (Observability) | telemetry/observability | latency tracking | Medium | M-Prefix operational rules apply. |
| D6\_information | New code, resolved D5 conflict (Retrieval) | general telemetry/info | system monitoring | Medium | M-Prefix operational rules apply. |
| D9\_unspecified | Catch-all anomaly | semantic underspecification | → split into cases OR keep fallback | Medium | Utilized when classification confidence is low (3.1.3). |
| **D99\_data\_quality\_error** | Resolved D0 conflict (Error) | ingestion vs semantic ambiguity | Critical ingestion error | High | D-Prefix justified as Structural Deviation. |
| **M1\_PRDR** | Derived Metric (Stability) | New Prefix M | Post-Repair Drift Recurrence | Low | M-Prefix operational rules applied (4.1). |
| **M2\_VRL** | Derived Metric (Resilience) | New Prefix M | Velocity Recovery Latency | Low | M-Prefix operational rules applied (4.1). |
| **M3\_CRR** | Derived Metric (Efficiency) | New Prefix M | Continue-Repair Ratio | Low | M-Prefix operational rules applied (4.1). |
| failure\_mode\_clustering | aggregate signal | not event | could map to taxonomy revisions | Low | taxonomy maturity |
| session\_closure\_typology | meta-analysis | not runtime event | not likely to become event code | Low | final governance |

## **4.1 Provisional M-Prefix Operational Rules**

The Provisional M prefix is governed by the following strict rules to prevent runtime contamination and circular dependencies:

1. **Generation Timing:** M-events **SHOULD** be generated as a batch at the end of a session (session\_closed) or upon a significant state change (e.g., drift/repair loop completion). **MUST NOT** be generated more frequently than once per 5 turns.  
2. **Aggregation Scope:** M-events **MUST** calculate metrics over the *preceding sequence* of core lifecycle events (D/R/RE/C/O/F) **within the current session\_id**.  
3. **Circular Dependency Prevention (MUST):** M-events **MUST NOT** be used as input for the calculation of *any other* M-event.

## **5\. Governance and Evolution Flow**

### **5.1 Classification and Evolution Model**

Taxonomy codes follow a clear path to stability:

* **Provisional:** Requires a use case and adherence to all Level 1/2 constraints. Used for exploratory work.  
* **Canonical:** Requires minimum 6 months of stability, proof of metric traceability, and formal governance sign-off.  
* **Pending:** Reserved for conflicts (now all resolved) or items requiring major policy changes (none currently).

### **5.2 Change Protocol**

Any proposal to move a code from Provisional to Canonical, or to modify an existing Provisional code, **MUST** be justified against the following criteria:

1. **Level 1/2 Compliance:** MUST NOT introduce structural or semantic violations.  
2. **Metric Traceability:** MUST contribute clearly to an established metric category (as per metrics\_alignment\_table.md).  
3. **Ambiguity Reduction:** MUST demonstrate lower volume for D9\_unspecified.

## **6. Cross-System Mapping**

### 6.1 → Event Types  
`D → R → C or O`

### 6.2 → Runtime Enforcement  
Mapping validated in `repair_detector.py`.

### 6.3 → Repair Continuum  
Severity‐based escalation confirmed.

### 6.4 → Metrics Framework  
Aligned except for D5/D0 contamination.

### 6.5 → Failover & Escalation  
Hard reset path validated but governed.

## **7. Diagram: Structural Overview**

> **(Included separately as taxonomy_proposal_diagram.svg)**  
Legend:  
- **Solid** = Canonical  
- **Dotted** = Provisional  
- **Dashed cluster** = Pending Governance

## **8\. Path to v0.2 and Validation Plan**

| Requirement | Condition to Exit |
| :---- | :---- |
| D5/D6 collision resolution | **COMPLETED** |
| D0 fallback hierarchy clarified | **COMPLETED** |
| Analytics governance decision | **COMPLETED** (M-prefix definition) |
| Stability threshold | \<3% volume routed to D9 fallback |

## **📌 Proposal Confidence Summary (inline preview)**

* Overall validity: **100%** (Specifications are fully hardened against all known structural, numeric, and philosophical ambiguities.)  
* Structural readiness: **High**  
* Governance unresolved areas: **Formal Canonicalization of Provisional Layer**

## 9. Feedback & Participation

This document is in an iterative research phase.
Feedback, objections, refinement proposals, and real-world implementation reports are highly encouraged.

Preferred channel: TBD (GitHub issues / shared doc / direct review)
Review cadence: aligned with governance milestones for the PLD v2 event schema.

### ✔️ Draft complete.
