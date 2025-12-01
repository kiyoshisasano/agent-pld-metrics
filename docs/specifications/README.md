# PLD Specifications (Levels 1–3)

This directory contains the **Normative Specifications** of Phase Loop Dynamics (PLD).
Files in this hierarchy represent the authoritative "Constitution" of PLD.

## 🏛️ Structure

| Level | Layer | Description | Mutable? |
|-------|-------|-------------|----------|
| **Level 1** | **Schema** | Hard invariants (JSON Schema). The absolute physics of the runtime. | 🔒 Fixed |
| **Level 2** | **Semantics** | Meaning of events, phases, and matrix rules. | 🔒 Review Req |
| **Level 3** | **Standards** | Operational metrics definitions and taxonomy. | ⚠️ Versioned |

---
> **Note:** For operational guides, cookbooks, or implementation patterns, see `../metrics/` or `../patterns/`.