---
path: meta/CHANGELOG.md
component_id: changelog
kind: doc
area: meta
status: stable
authority_level: 5
version: 2.0.0
license: Apache-2.0
purpose: Official change history for the PLD runtime and metadata ecosystem.
---

# PLD Repository — Unified CHANGELOG

**Version:** 2.0  
**Status:** Working Draft (Actively Evolving)  
**Last Updated:** 2025-11  

This project is currently in an early experimentation and refinement phase.  
Contents may evolve as feedback and implementation experience accumulate.

This changelog consolidates repository-level history and replaces:

- `/quickstart/_meta/CHANGELOG.md`
- `/quickstart/patterns/04_integration_recipes/_meta/CHANGELOG.md`
- Status notes previously embedded in `/docs/03_pld_event_schema.md`

Beginning with Version `2.0`, this file serves as the primary reference record for major changes across the repository.

---

## 📌 Version `2.0` — Specification-Centric Architecture

**Date:** 2025-11  
**Classification:** Major structural and normative draft update

### Summary

This release marks a transition from an exploratory research repository toward an early specification-driven model.

In this phase:

- The **PLD Event Schema** and **semantic event matrix** function as the current normative baseline.
- Runtime examples and supporting documentation are aligned to these definitions.
- Concepts such as lifecycle enforcement, schema validation, and naming format rules are now defined.

These elements are expected to evolve as testing, implementation experience, and community discussion continue.

---

### Key Changes

| Category | Update |
|----------|--------|
| Normative Draft | Introduced `docs/03_pld_event_schema.md` as the Working Draft specification |
| Lifecycle Enforcement | Added lifecycle prefix validation (`D/R/RE/C/O/F → phase mapping`) |
| Schema Correctness | Updated PLD code regex to the **current expected form** |
| Version Governance | Defined major-version compatibility expectations (minor versions MAY remain forward-compatible) |
| Repository Organization | Aligned folder structure with terminology and quickstart hierarchy |
| Examples | Updated example events to conform to lifecycle rules and event types |
| Metadata Consolidation | Historical and distributed metadata merged under `/meta/` |

#### 🔧 Update: Metrics & Traceability Alignment (Post-schema refinement)

- Added `docs/validation/PLD_v2_Traceability_Map.md` as a traceability and compliance reference  
- Updated `metrics_schema.yaml` to the Hybrid Compliance Model (non-breaking)  
- Updated `PLD_metrics_spec.md` to align with PLD Taxonomy v2 and Level-2 Event Matrix semantics  
- Clarified handling of **provisional** and **pending** taxonomy codes  
- Clarified numeric classifier role (**MAY be used for segmentation; MUST NOT determine metric eligibility**)  

**Classification:** Minor update (non-breaking, still under 2.0 scope)

---

### Breaking Changes

| Scope | Change |
|-------|--------|
| Previous Versions | Version `1.1` is now considered non-normative and SHOULD NOT be used for conformance testing |
| Schema Version | Validators MUST reject event records where `schema_version != 2.x` |
| Code Format | Earlier PLD code patterns are no longer supported |

---

### Migration Notes

Implementations transitioning from `1.1` SHOULD:

- Update event log formatting to match lifecycle prefix enforcement rules  
- Replace deprecated naming conventions and non-aligned field structures  
- Use `schema_version = "2.0"` (or a compatible `2.x` minor release)  

---

## Version `1.1` — Vocabulary & Alignment Refinement

**Date:** 2025-11  
**Classification:** Non-breaking editorial and semantic update

### Summary

Version `1.1` introduced consistent terminology and structural alignment across the repository.  
This release aimed to establish shared vocabulary before formal specification work began.

---

### Changes

| Category | Update |
|----------|--------|
| Terminology | Lifecycle terminology standardized |
| Quickstart Docs | Tone updated to neutral, framework-agnostic guidance |
| Examples | Improved alignment with PLD lifecycle narrative |
| Repository Layout | Introduced sequential naming conventions (`01_`, `02_`, etc.) |
| UX Guidelines | Defined visible repair as the default behavioral model |

---

### Compatibility

- Fully backward compatible with Version `1.0`  
- Schema validation was **not enforced** in this phase  

---

## Version `1.0` — Initial Public Repository Publication

**Date:** 2025-11  
**Classification:** Exploratory Release

### Summary

Version `1.0` marks the first public availability of PLD materials.  
Content at this stage reflects exploratory and conceptual thinking rather than standardization.

---

### Included Components

- Early PLD schema prototype (non-normative)  
- First drift/repair taxonomy draft  
- Prototype quickstart documentation  
- Initial runtime examples  

---

### Characteristics

| Attribute | State |
|----------|-------|
| Schema | Prototype / Informal |
| Naming Rules | Unstandardized |
| Validation Rules | Not enforced |
| Tone | Research-oriented |
| Intended Usage | Experimental |

---

## Historical Notes (Non-Versioned)

- Earlier materials existed in fragmented internal draft form before formal versioning.  
- Terminology evolved iteratively until alignment work completed in Version `1.1`.  
- The shift toward a specification-first approach began formally in the Version `2.0` cycle.  

---

## Future Change Recording

All future updates SHOULD:

- Follow semantic version numbering  
- Document changes in this file before merging  
- Reference affected areas (`docs/`, `runtime/`, `quickstart/`, etc.)  

### Versioning Guidance

| Change Type | Version Increment |
|------------|------------------|
| Editorial / Clarification | PATCH |
| New non-breaking rules or examples | MINOR |
| Structural or breaking change | MAJOR |

---

## Feedback & Participation

This project is **actively seeking feedback** from early adopters, researchers, and implementation testers.

Feedback channels (tentative until formal RFC process begins):

- GitHub Issues (planned)
- Discussion threads (planned)
- Community review cycles (future consideration)

---

Maintainer: **Kiyoshi Sasano**
