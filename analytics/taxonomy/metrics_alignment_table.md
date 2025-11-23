# **Metrics Alignment Table (Initial Draft)**

Role: PLD v2 Observability/Analytics Layer Analyst    
Source: taxonomy\_observation\_sheet.csv    
Reference Specs: PLD\_metrics\_spec.md, event\_matrix.yaml

## **1\. Metrics Alignment Table**

| code | lifecycle\_phase | tentative\_metric\_category | measurable\_signal | notes | confidence (1-5) |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **D0\_none** | Interaction (Loop) | **Baseline (No Drift)** | Signal of system health checks returning negative for drift. (Silence verification) | **Issuance Condition:** SHOULD only be emitted when an explicit Drift Health Check is run. | 5 |
| **D1\_instruction** | Interaction (Loop) | **Accuracy (Intent)** | Signal that the agent's action diverged from user instruction. | Core quality metric. Critical for "Alignment" score. | 5 |
| **D2\_context** | Interaction (Loop) | **Data Integrity / Context** | Signal of schema violation or context window corruption. | Indicates pipeline fragility rather than model logic error. | 4 |
| **D3\_repeated\_plan** | Interaction (Loop) | **Efficiency (Stall)** | Signal of loop/stalemate where agent cannot progress. | High correlation with user frustration (churn risk). | 5 |
| **D4\_tool\_error** | Interaction (Loop) | **Reliability (dependency)** | Signal of downstream tool/API failure. | External dependency metric. Distinct from cognitive drift. | 5 |
| **D5\_latency\_spike** | Interaction (Loop) | **Performance (Latency)** | Signal of processing time exceeding QoS thresholds. | Purely operational metric. | 5 |
| **D6\_information** | Interaction (Loop) | **Accuracy (Retrieval)** | Signal of hallucination or failure to retrieve necessary knowledge. | Code reassigned from D5 to resolve collision. | 5 |
| **D9\_unspecified** | Interaction (Loop) | **Coverage (Unknown)** | Signal of unclassified anomaly. | High volume here indicates gap in taxonomy. | 4 |
| **D99\_data\_quality\_error** | Interaction (Loop) | **Data Quality (Ingestion)** | Signal of malformed event missing pld.code. | Code reassigned from D0 to resolve conflict. | 5 |
| **C0\_normal** | Interaction (Loop) | **Throughput (Success)** | Signal of nominal progression. | Baseline for "Success Rate" denominator. | 5 |
| **C0\_user\_turn** | Interaction (Loop) | **Engagement (Input)** | Signal of user activity/input. | Used to normalize drift rates per turn. | 5 |
| **C0\_system\_turn** | Interaction (Loop) | **Engagement (Output)** | Signal of system response generation. |   | 5 |
| **O0\_session\_closed** | Resolution | **Completion Rate** | Signal of session termination. | Does not inherently imply success/failure without qualifier. | 4 |
| **R1\_clarify** | Recovery | **Intervention (Soft)** | Signal of agent seeking user guidance. | Low cost repair. | 5 |
| **R2\_soft\_repair** | Recovery | **Intervention (Auto)** | Signal of internal self-correction mechanism triggering. |   | 5 |
| **R3\_rewrite** | Recovery | **Intervention (Intensive)** | Signal of active plan rewriting. | Higher computational cost repair. | 5 |
| **R4\_request\_clarification** | Recovery | **Intervention (User-Loop)** | Signal of explicit delegation to user. | High friction repair. | 5 |
| **R5\_hard\_reset** | Recovery | **Intervention (Critical)** | Signal of state wipe/restart. | Indicates severe failure recovery. | 5 |
| **M1\_PRDR** | **Analysis (Derived)** | **Stability (Recurrence)** | Derived: Probability of drift $D\\\_x$ occurring after repair $R\\\_y$. | **New M-Prefix.** Encoded as event\_type: info, phase: none. | 5 |
| **M2\_VRL** | **Analysis (Derived)** | **Resilience (Time-to-Recover)** | Derived: Time delta $\\Delta t$ between Drift detection and Stable state. | **New M-Prefix.** Encoded as event\_type: info, phase: none. | 5 |
| **M3\_CRR** | **Analysis (Derived)** | **Efficiency (Ratio)** | Derived: Ratio $\\frac{\\sum C}{\\sum R}$. | **New M-Prefix.** Encoded as event\_type: info, phase: none. | 5 |
| failure\_mode\_clustering | **Analysis (Post-Hoc)** | **Defect Taxonomy** | Derived: Aggregate clusters of D-codes. | Remains analytic-only (not M-event). | 5 |
| session\_closure\_typology | **Analysis (Post-Hoc)** | **Outcome Taxonomy** | Derived: Classification of $O\\\_0$ events context. | Remains analytic-only (not M-event). | 5 |

## **2\. Unresolved Items & Conflicts**

### **A. Code Collision: D0 (RESOLVED)**

* **Conflict**: D0 was overloaded (No Drift vs. Ingestion Error).  
* **Resolution**: Separation of **D0\_none** and **D99\_data\_quality\_error**. Resolved.

### **B. Code Collision: D5/D6 (RESOLVED)**

* **Conflict**: D5 was overloaded (Latency vs. Information).  
* **Resolution**: Separation of **D5\_latency\_spike** and **D6\_information**. Resolved.

### **C. Observational Rows in Taxonomy (RESOLVED)**

* **Ambiguity**: Derived metrics (PRDR, VRL, CRR) mixed with raw events.  
* **Resolution**: Introduced **M-Prefix** and defined encoding rule (event\_type: info, pld.phase: none). Solved the structural conflict.

## **3\. Summary**

* **Alignment Confidence**: **99%** (All structural and numerical conflicts resolved.)  
* **Major Ambiguity Cluster**: None. The system is structurally sound for v2.1 advancement.  
* **Recommendation for Next Governance Step**: Formal review and **Canonicalization** of Provisional codes (M1, M2, M3, D0, D5, D6, D99).
