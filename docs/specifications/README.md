# PLD Specifications (Levels 1–3)

Status: Working Draft (Candidate Normative Specification)  

This document represents the current understanding of PLD normative specifications.
While certain terminology and rules are expressed normatively (MUST/SHOULD/MAY),
the overall framework remains under evaluation and may evolve based on governance review
and implementation feedback.


> **Change Control Guidelines**

These specifications are governed under the PLD documentation hierarchy and MUST follow the rules below:

- **Level 1 (Schema):** Changes require a version bump and formal governance approval.
- **Level 2 (Semantics):** Changes require justification, semantic traceability, and compatibility review.
- **Level 3 (Operational Standards):** Changes MUST be versioned and SHOULD remain backward-compatible unless explicitly stated.

---

This directory contains the **Normative Specifications** of Phase Loop Dynamics (PLD).  
Files in this hierarchy represent the authoritative "Constitution" of the PLD framework.

---

## 🏛️ Specification Structure

| Level | Layer | Description | Mutable? |
|-------|-------|-------------|----------|
| **Level 1** | **Schema** | Hard invariants (JSON Schema). The absolute physics of the runtime. | 🔒 Fixed |
| **Level 2** | **Semantics** | Meaning of events, phases, and matrix rules. | 🔒 Review Req |
| **Level 3** | **Standards** | Operational metrics definitions and taxonomy. | ⚠️ Versioned |

> For operational guides, cookbooks, or implementation patterns, see `../metrics/` or `../patterns/`.




