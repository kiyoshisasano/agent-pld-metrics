<!--
path: meta/ROADMAP.md
component_id: roadmap
kind: doc
area: meta
status: draft
authority_level: 3
version: 2.0.0
license: Apache-2.0
purpose: Roadmap and future development plans for the PLD repository and runtime ecosystem.
-->

## Purpose of This Roadmap

PLD is transitioning from exploratory research toward early standardization and practical application.  
The goal of this roadmap is to:

- Provide clarity on direction and intent  
- Align contributors and early adopters  
- Support long-term maintainability and ecosystem consistency  
- Communicate maturity realistically: **stable core, evolving edges**

---

## Phase Overview

| Phase | Status | Focus |
|-------|--------|--------|
| **Phase 0 — Exploration** | ✔ Completed | Draft models, prototypes, early terminology |
| **Phase 1 — Specification Foundation** | ✔ In progress | Schema, event model, lifecycle alignment |
| **Phase 2 — Tooling & Reference Implementation** | ⏳ Planned | Validator, examples, optional runtime bridges |
| **Phase 3 — Community Review & Refinement** | ⏳ Planned | Feedback cycles, testing, adjustments |
| **Phase 4 — Ecosystem Stabilization** | ⏳ Future | Governance, compatibility guidance, sustainability |

> While terminology and structure are stabilizing, best practices and reference tooling are expected to evolve.

---

## Current Priority Areas (Near-Term Focus)

These represent active areas of work, without strict deadlines.

| Priority | Status | Notes |
|----------|--------|-------|
| Finalize Working Draft specification language | In progress | Refinement, clarity, consistency |
| Expand example event set to represent real-world edge cases | Planned | Needed for validation and reference implementations |
| Begin design of lightweight validation tooling | Under evaluation | Likely to start as scripts before frameworks |
| Improve onboarding flow through documentation pass | Planned | Align quickstart principles with specification |

---

## Mid-Term Direction (Exploratory but Probable)

| Area | Intent |
|------|--------|
| Optional reference validator tool | Support interoperability and automated conformance |
| Runtime integrations | Provide optional, not mandatory, adapters to existing frameworks |
| Reference patterns and operational heuristics | Build working examples driven by field usage |
| Drafting early RFC process | Prepare for proposals from implementers and collaborators |

---

## Long-Term Possibilities (Speculative and Community-Driven)

| Area | Potential Outcome |
|------|------------------|
| Governance | Working group or structured stewardship model |
| Validation ecosystem | Conformance tooling, badges, or CI checks |
| Documentation Models | Full specification format (IETF/W3C-like or OpenSpec style) |
| Ecosystem Adoption | Patterns for applying PLD across agents, tools, and evaluation stacks |

These directions remain intentionally flexible.

---

## What Is **Not** Planned at This Stage

To avoid premature standardization, the following are deferred:

- Formal certification programs  
- Fixed enumerated code taxonomies beyond prefix and structure rules  
- Locked compatibility guarantees across frameworks  
- Enterprise governance models  

These may become relevant only if broader community adoption occurs.

---

## How Feedback Shapes This Roadmap

Feedback from early adopters, implementers, and researchers is welcome and helps guide priorities.

Planned participation channels:

- GitHub Issues
- Discussion threads
- Structured review rounds (future consideration)

Roadmap updates will continue to be recorded in:

```
/meta/CHANGELOG.md
```

---

Maintainer: **Kiyoshi Sasano**
