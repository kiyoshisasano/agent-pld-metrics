📄 docs/metrics/PLD\_metrics\_spec.md

Status: Hybrid-Aligned Candidate

Version: 2.0.0 
Audience: Engineers and researchers implementing PLD-compatible runtimes  
Dependencies:

* Level 1: pld\_event.schema.json  
* Level 2: event\_matrix.yaml \+ PLD\_Event\_Semantic\_Spec\_v2.0.md  
* Level 3: PLD\_taxonomy\_v2.0.md

\# 1\. Purpose

This document defines the \*\*canonical PLD runtime metrics specification\*\* for systems implementing PLD v2 lifecycle semantics.    
Metrics in this specification MUST:

\- Operate solely on \*\*valid events\*\*  
\- Respect Level-1 schema invariants and Level-2 semantic constraints    
\- Align with PLD v2 taxonomy naming, lifecycle phases, and event mappings  

Metrics MAY incorporate \*\*provisional taxonomy groupings\*\* for analysis but MUST NOT derive required logic from non-canonical or pending codes.

\---

\# 2\. Hierarchy of Authority

| Rank | Source | Enforcement |  
|------|--------|------------|  
| 1 | \`pld\_event.schema.json\` | MUST |  
| 2 | \`event\_matrix.yaml\` \+ supporting docs | MUST |  
| 3 | This metrics specification | MUST |  
| 4 | Dashboards, analysis, heuristics | MAY |

Where a conflict exists, sources MUST override this document in the order above.

\---

\# 3\. Core Validity... (unchanged)

... (omitted for brevity, content unchanged) ...

\---

\# 7\. Governance Notes

\- Metrics MUST NOT create new prefixes or lifecycle categories.  
\- Provisional taxonomy codes MAY appear in aggregations but MAY NOT define new metrics.  
\- Pending governance items MUST NOT drive metric logic.

\---

\# 8\. Version Policy

Any change affecting:

\- formula semantics    
\- lifecycle alignment    
\- event eligibility    
→ MUST increment metric version.

Metric names MUST remain globally unique.

\---

\# End of Specification

Source alignment tracked to:    
\`PLD\_event.schema.json\`, \`event\_matrix.yaml\`, and \`PLD\_taxonomy\_v2.0.md\`.

\---

\#\# 📎 Mapping Notes

\#\#\# Drift → D\* family mapping

\- Metrics depend solely on \*\*event\_type \+ phase\*\*  
\- D1–D6 (including the newly separated \*\*D6\_information\*\*) MAY be used for segmentation only.

\#\#\# Repair → R\* family mapping

\- R1–R5 used only for analytics grouping    
\- Not required for metric algorithm

\#\#\# Continue / Outcome / Failover

\- Align strictly with event\_type → phase constraints in Level-2 matrix rules

\#\#\# Derived Metrics → M\* family mapping (NEW)

\- \*\*M-Prefix:\*\* Codes like \`M1\_PRDR\`, \`M2\_VRL\` are \*\*explicitly defined\*\* as provisional metrics and MAY be used for segmentation.  
\- \*\*Rule:\*\* M-Prefix events MUST NOT be included in core lifecycle metric counts (e.g., Drift Rate, Repair Success) as they are derived signals, not raw events.

\---

\#\# Governance Notes

\- Provisional codes (\`D0\_none\`, \`D9\_unspecified\`, \`M\*\` codes) allowed only as advisory reference.  
\- \*\*RESOLUTION CONFIRMED:\*\* The prior collision between \`D5\_latency\_spike\` and \`D5\_information\` is \*\*resolved\*\* by the introduction of \`D6\_information\`. All metric systems MUST now segment these two events separately if they wish to include them in analysis.

\---  
