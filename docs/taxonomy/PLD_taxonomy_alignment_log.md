# **PLD Taxonomy Alignment Log**

Status: Working Draft — Finalized Alignment Record (Ready for v2.1 Proposal)  
Audience: Contributors, reviewers, and implementation testers involved in PLD v2 alignment work.

---

## **1\. Purpose of This Log**

This document serves as a traceable record of the alignment work conducted between the following layers of the PLD v2 model:

* **Level 1 — Structural Specification** (pld\_event.schema.json)  
* **Level 2 — Semantic Matrix** (event\_matrix.yaml)  
* **Level 3 — Taxonomy Proposal** (PLD\_taxonomy\_v2.0.md)  
* **Level 4 — Observational and Example Data** (optional, non-normative)

The intent is to document decisions, clarifications, and open questions as the system evolves. This record is exploratory and subject to revision based on feedback and implementation experience.

---

## **2\. Alignment Scope**

This alignment focuses on the following areas:

| Scope Area                  | Included            | Notes                                                      |
| :---- | :---- | :---- |
| Prefix governance          | Yes                  | Ensures consistency across schema and taxonomy.            |
| Lifecycle mapping          | Yes                  | Confirmed based on Level 2 semantic rules.                |
| Numeric classifier meaning | Yes (advisory only) | Meaning remains taxonomy-controlled, not schema-enforced. |
| Event type mapping          | Yes                  | Verified against matrix constraints.                      |
| Analytics-only signals      | Fully Resolved      | Encoded via M-Prefix (Provisional).                        |

---

## **3\. Layer Boundary Summary**

The alignment effort confirmed that each layer maintains a specific responsibility boundary:

| Layer                              | Role                                                                              | Enforcement Strength    |
| :---- | :---- | :---- |
| **Level 1: Schema**                | Defines the full structural contract for valid runtime events.                    | MUST                    |
| **Level 2: Event Matrix**          | Defines semantic interpretation rules for event types and lifecycle consistency. | MUST / SHOULD          |
| **Level 3: Taxonomy**              | Proposes naming, categorization, and governance evolution patterns.              | PROPOSED / MAY          |
| **Level 4: Observational Signals** | Used for research and evaluation purposes.                                        | Optional, not required |

This separation supports clarity, extensibility, and safe iteration.

---

## **4\. Final Alignment Result**

The alignment produced the following outcome:

**No schema structural changes were required.** Numeric classifiers remain fully allowed by the existing pattern and do not require additional enforcement.

The only update applied was a **non-functional clarification to documentation language**, ensuring that numeric classifiers are acknowledged as:

* syntactically valid in Level 1,  
* semantically advisory in Level 2,  
* and meaningfully defined by Level 3\.

No validator, ingestion system, or runtime logic is affected by this clarification.

---

## **5\. Cross-Layer Consistency Table**

| Element                                | Schema (L1)        | Matrix (L2)          | Taxonomy (L3)                  | Final State                |
| :---- | :---- | :---- | :---- | :---- |
| Prefix families (D/R/RE/C/O/F)      | Allowed & required | Enforced              | Used                            | Aligned                    |
| Numeric classifiers (1–5)            | Allowed (optional) | Not enforced          | Semantically meaningful        | Aligned under Hybrid Model |
| Non-lifecycle codes (INFO\_, SYS\_) | Allowed            | Phase must be none | Used for runtime states        | Aligned                    |
| Descriptor naming                      | Pattern-controlled | Meaning referenced    | Human-readable semantic intent | Aligned                    |

---

## **6\. Known Ambiguities and Pending Governance**

Some taxonomy entries remain unfinalized. These are intentionally preserved as “pending” and not rejected by Level 1 or Level 2\.

| Case                                    | Issue Type          | Notes                                                        |
| :---- | :---- | :---- |
| D5\_latency\_spike vs D5\_information | Numeric collision  | Requires taxonomy resolution. Schema does not block either. |
| D0\_none vs D0\_unspecified          | Semantic ambiguity | Future ingestion rules may clarify meaning.                  |
| Analytics-derived clusters              | Scope question      | May remain non-runtime annotations unless elevated.          |

These items will be revisited when taxonomy maturity increases.

---

## **7\. Compatibility and Impact Summary**

| Area                    | Impact                                                                              |
| :---- | :---- |
| Existing logs          | Fully compatible — no reprocessing required.                                        |
| Validator behavior      | Unchanged.                                                                          |
| Runtime logic          | No required changes. Optional improvements may reference taxonomy numeric guidance. |
| Tooling and dashboards | May optionally display numeric classifier semantics in future.                      |

---

## **8\. Next Review Stage**

This document is expected to evolve as implementation feedback becomes available.

Future checkpoints may include:

* stability of the taxonomy numeric hierarchy,  
* evaluation of edge-case events in production test data,  
* potential candidate promotion from provisional to canonical status,  
* investigation of whether analytics clusters should remain outside runtime encoding.

---

## **9\. Feedback Invitation**

Feedback, implementation reports, and proposed revisions are welcome. Perspectives from runtime engineers, annotation teams, and observability researchers are especially valuable.

"This log represents the current understanding and remains open to refinement."

---

## **10\. Governance Action: D5 Collision Resolution (2025-11-23)**

**Action:** Numeric reassignment to resolve the conflict between an operational metric (latency) and a cognitive metric (information retrieval failure).

**Issue:** The numeric code D5 was used for two semantically distinct concepts, resulting in potential metric contamination:

1. **D5\_latency\_spike**: Observable, phase-agnostic runtime performance signal. (Operational)  
2. **D5\_information**: Drift related to retrieval quality or hallucination. (Cognitive)

Resolution Decision:  
The operational signal (D5\_latency\_spike) is considered higher priority for its current numeric assignment as it is often emitted by low-level, high-volume instrumentation. The cognitive signal was renumbered.

* **D5** remains assigned to: D5\_latency\_spike (Provisional Registry)  
* **New Code:** D6\_information created for the cognitive signal.

**Affected Files:**

* PLD\_taxonomy\_v2.0.md (Updated, moving D5\_information to D6\_information)  
* analytics/taxonomy/metrics\_alignment\_table.md (Updated, reflecting separated D5/D6 for cleaner aggregation)

**Impact Summary:** Numeric collision resolved. The integrity of observability metrics derived from D5 is secured. The primary pending governance issue is now the D0 overlap.

---

## **11\. Governance Action: D0 Collision Resolution (2025-11-23)**

**Action:** Separation of Baseline Health signal from Data Quality Error signal to ensure clean metric aggregation.

**Issue:** The numeric code D0 was used for two semantically incompatible concepts:

1. **D0\_none**: Represents **NO DRIFT** detected (a positive health signal/baseline).  
2. **D0\_unspecified**: Represents a **data quality error** (missing pld.code) originating from the ingestion layer.

Resolution Decision:  
The baseline signal (D0\_none) is retained to represent system health. The error signal must be moved to a code that clearly signifies a high-severity, data quality-related anomaly.

* **D0** remains assigned to: D0\_none (Provisional Registry \- Baseline/Health Check)  
* **New Code:** D99\_data\_quality\_error created for the malformed event/missing code error. This high number signifies its criticality and analytic separation from lower D-codes (D1-D6).

**Affected Files:**

* PLD\_taxonomy\_v2.0.md (Updated, moving D0\_unspecified to D99\_data\_quality\_error)  
* analytics/taxonomy/metrics\_alignment\_table.md (Updated, reflecting separated D0/D99 for accurate health/error reporting)

**Impact Summary:** D0 numerical ambiguity resolved. Baseline metrics (e.g., drift rate denominator) are now protected from contamination by data quality errors. All numerical prefix collisions are now resolved.

---

## **12\. Governance Action: Analytics Scope Resolution (2025-11-23)**

**Action:** Introduction of the 'M' (Metrics) prefix to Provisional Registry to safely encode derived analytical signals within the event stream, adhering to Level 2/3 constraints.

**Issue:** Derived analytical metrics (PRDR, VRL, continue\_repair\_ratio) were mixed with raw events. The governance question was whether these should be events (requiring a prefix) or remain outside the stream.

Resolution Decision:  
To allow advanced runtimes (Level 5\) to consume derived metrics as "events" for adaptive reasoning, but without violating core Level 2 lifecycle rules, the 'M' prefix is introduced.

* **New Prefix:** M (Provisional Registry \- Derived Metrics/Analytics)  
* **Encoding Rule:** Events using the M prefix **MUST** use event\_type: info and pld.phase: none. This satisfies Level 2's rule that non-lifecycle prefixes must map to phase: none.  
* **New Codes:** M1\_PRDR, M2\_VRL, M3\_CRR added to Provisional Registry.

**Impact Summary:** The analytics/runtime boundary is clarified. Derived signals can now be safely encoded into the event stream as non-lifecycle info events, protecting the integrity of core lifecycle phases (D/R/C/O/F). All outstanding governance issues are now addressed.

---

## **13\. Governance Action: Definition Hardening (2025-11-23)**

**Action:** Final hardening of definitions for D0, C0, and M-Prefix to address philosophical and implementation ambiguities identified in the alignment review.

### **A. M-Prefix Operational Boundaries (M1, M2, M3)**

To prevent circular dependency risks and define implementation scope:

* **Generation Timing (Provisional Rule):** M-events **SHOULD** be generated as a batch at the end of a session (session\_closed) or upon a significant state change (e.g., drift/repair loop completion) to minimize real-time generation cost. **MUST NOT** be generated more frequently than once per 5 turns.  
* **Aggregation Scope (Provisional Rule):** M-events **MUST** calculate metrics over the *preceding sequence* of core lifecycle events (D/R/RE/C/O/F) **within the current session\_id**.  
* **Circular Dependency Prevention (MUST):** M-events **MUST NOT** be used as input for the calculation of *any other* M-event.

---

### **B. D0\_none Baseline Operational Policy**

To prevent high-volume noise and ensure clear signal meaning:

* **Issuance Condition (Provisional Rule):** D0\_none **SHOULD** only be emitted when an agent or system module explicitly runs a **Drift Health Check** and returns a negative (no drift) result. **MUST NOT** be emitted passively or automatically on every user/system turn.  
* **Purpose:** D0\_none explicitly tracks the *volume* of health checks, not the absence of drift, which is inferred by the *absence* of D1-D99 events.

---

### **C. C0 Prefix Semantic Exemption**

To clarify the numeric structure:

* **Exemption Justification:** The C0 codes (C0\_normal, C0\_user\_turn, C0\_system\_turn) are **explicitly exempted** from the "numeric ordering must remain unique within a prefix" rule, as they represent **orthogonal states** within the **'Continuation' meta-category**.  
* **Rule:** The numeric value 0 within the C prefix signifies **Nominal Flow (Default/Baseline)**, which is then refined by the descriptor (\_normal, \_user\_turn, \_system\_turn). The C prefix is not intended to track severity or escalation via its numeric component.

---

### **D. D99 (Data Quality Error) Context**

* **Clarification:** The D prefix is broadly defined as **Drift or Deviation**. D99\_data\_quality\_error is considered a **Structural Deviation** originating at the edge (ingestion/runtime), justifying its inclusion in the D family rather than introducing a new E (Error) prefix that would break Level 2 alignment.

**Impact Summary:** All structural, numeric, and philosophical ambiguities are addressed. The taxonomy is ready for v2.1 Canonicalization proposal.

---

## **14\. Governance Action: Final Specification Quality & Alignment (2025-11-23)**

**Action:** Implementation of Quality of Specification recommendations to enhance maintainability and reduce implementation ambiguity (Final Quality Pass).

**Changes:**

1. **Exception Rules Consolidation:** Unified the operational rules for C0, D0, and D9 into a dedicated section in PLD_taxonomy_v2.0.md (3.1 Exception and Operational Rules). This centralizes previously scattered exception handling and improves readability.

2. **D9 Quantification:** Added Rule 3.1.3, restricting the use of `D9_unspecified` only to cases where confidence scores for all other classifiers are low.

3. **Governance Flow Clarification:** Added section 5.2 Change Protocol to clearly define promotion requirements from Provisional to Canonical status.

**Impact Summary:** The overall specification quality has been improved, ensuring clearer governance processes and greater predictability for future transitions from Provisional to Canonical classifications.
