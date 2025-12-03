# PLD Concepts Reference Map

This document is a **navigation guide** for the PLD Concepts section. It connects high-level concepts to:

* authoritative specifications (Levels 1–3),
* architecture and runtime design docs,
* operator primitives,
* practical pattern libraries,
* analytics and evaluation materials.

It is **non-normative**: it does not define new schema, phases, or taxonomy. It simply explains *where to look* for each topic.

---

## 1. How to Use This Map

Use this file when you are asking questions like:

* "Where is the canonical definition of this PLD term?"
* "Which doc explains how Drift and Repair work at runtime?"
* "Where can I find concrete examples or patterns for this concept?"

You can treat it as a **table of contents across directories**, not just within `docs/concepts/`.

---

## 2. Concepts Stack Overview

The PLD documentation is organized in layers:

| Layer        | Location               | Purpose                                  |
| ------------ | ---------------------- | ---------------------------------------- |
| Specs        | `docs/specifications/` | Canonical schema, semantics, standards   |
| Concepts     | `docs/concepts/`       | Mental models and lifecycle explanations |
| Architecture | `docs/architecture/`   | System design, runtime structure         |
| Patterns     | `docs/patterns/`       | Implementation patterns and recipes      |
| Runtime      | `pld_runtime/`         | Executable runtime components            |
| Quickstart   | `quickstart/`          | Minimal examples and demos               |
| Analytics    | `analytics/`           | Metrics frameworks and case studies      |

This file focuses on bridging **Concepts ↔ Specs ↔ Architecture ↔ Patterns**.

---

## 3. Core Concepts Files

The `docs/concepts/` directory contains the primary conceptual guides:

| File                       | Role                                                               |
| -------------------------- | ------------------------------------------------------------------ |
| `01_introduction.md`       | Why PLD exists, what problems it solves, and who it is for         |
| `02_drift_repair_model.md` | Drift → Repair → Reentry → Continue → Outcome lifecycle model      |
| `03_repair_strategies.md`  | Static / Guided / Human-in-the-Loop repair strategies              |
| `operator_primitives/`     | Atomic actions for detection, repair, reentry, and latency control |

If you are new to PLD, read them in order: **01 → 02 → 03**, then dip into `operator_primitives/` when you need implementation detail.

---

## 4. Lifecycle Reference: Human Concept → Machine Taxonomy

PLD uses a small set of lifecycle concepts that map to machine-readable taxonomy prefixes.

> **Authoritative taxonomy definitions live in** `docs/specifications/level_3_standards/PLD_taxonomy_v2.0.md`.

This table is a conceptual bridge only:

| Concept  | Phase      | Taxonomy Prefix (Level 3) | Description                                                         |
| -------- | ---------- | ------------------------- | ------------------------------------------------------------------- |
| Drift    | `drift`    | `D*`                      | System deviates from expected task, state, or constraints           |
| Repair   | `repair`   | `R*`                      | System attempts to correct a detected drift                         |
| Reentry  | `reentry`  | `RE*`                     | System verifies that it has returned to a stable, intended workflow |
| Continue | `continue` | `C*`                      | System decides whether execution may proceed or must be blocked     |
| Outcome  | `outcome`  | `O*`                      | Final session state or terminal classification                      |
| Failover | `failover` | `F*`                      | Handoff or controlled abandonment when recovery is impossible       |

Conceptual rule of thumb:

* **Human side**: think in terms of Drift → Repair → Reentry → Continue → Outcome (with Failover as a safety rail).
* **Machine side**: emit events with `pld.phase` and `pld.code` aligned to these prefixes and the Level 2 event matrix.

---

## 5. Runtime Decision Guide (Concept → Where to Look)

This table helps you find the right document depending on what you are trying to design or debug.

| Question                                                 | Look Here                                                                                                           |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| "What is Drift, conceptually?"                           | `docs/concepts/02_drift_repair_model.md` (Drift phase section)                                                      |
| "How do I detect Drift at runtime?"                      | `docs/concepts/operator_primitives/01_detect_drift.md`, `pld_runtime/detection/`                                    |
| "What repair strategies can I use?"                      | `docs/concepts/03_repair_strategies.md`, `docs/concepts/operator_primitives/02_soft_repair.md`, `03_hard_repair.md` |
| "How does Reentry work?"                                 | `docs/concepts/02_drift_repair_model.md` (Reentry section), `operator_primitives/05_reentry_operator.md`            |
| "How should I decide between continue vs block?"         | `02_drift_repair_model.md` (Continue phase), `docs/patterns/03_system/runtime_policy_patterns.md`                   |
| "Where are the canonical event types and codes defined?" | `docs/specifications/level_2_semantics/`, `docs/specifications/level_3_standards/PLD_taxonomy_v2.0.md`              |
| "How do I log PLD events in code?"                       | `docs/patterns/03_system/logging_and_schema_examples.md`, `pld_runtime/logging/`                                    |
| "How do I measure Drift/Repair outcomes?"                | `analytics/metrics_frameworks/`, `docs/metrics/pld_operational_metrics_cookbook.md`                                 |

---

## 6. Correct Vocabulary Usage (Concept Layer)

To keep PLD terminology consistent across docs, code, and dashboards:

### ✔ Recommended

* Use **Drift / Repair / Reentry / Continue / Outcome / Failover** as the core lifecycle concepts.
* When referring to event classification, speak in terms of **taxonomy prefixes** (D*, R*, RE*, C*, O*, F*).
* Keep terms **machine-interpretable**: every concept you use in code or labels should correspond to a defined schema and taxonomy entry.

### ❌ Avoid

* Inventing new lifecycle terms that are not present in Level 2 or Level 3.
* Using vague labels such as "fallback mode" or "recovery attempt" without a clear Drift/Repair mapping.
* Logging generic "retry" or "reset" events without indicating which drift they address and which repair they represent.

If a behavior cannot be expressed using existing schema, semantics, and taxonomy, it should be documented as *exploratory* rather than treated as part of the core PLD lifecycle.

---

## 7. Example Situations → PLD Concepts

This section gives high-level examples of how runtime situations map to PLD concepts. Exact codes and event_types MUST be chosen from Level 2 and Level 3 specifications.

| Situation                                                  | PLD Concept (Human)               |
| ---------------------------------------------------------- | --------------------------------- |
| System misunderstands a user constraint                    | Drift (context / intent)          |
| System asks a clarifying question to fix misunderstanding  | Repair (local / soft)             |
| After clarification, system resumes the original task      | Reentry (intent / workflow)       |
| System stabilizes and continues without further deviations | Continue (allowed)                |
| Session ends successfully                                  | Outcome (successful completion)   |
| Session ends due to unrecoverable error                    | Outcome (failure) and/or Failover |

These mappings are conceptual only; for concrete code values, refer to `PLD_taxonomy_v2.0.md` and related Level 2/3 materials.

---

## 8. Anti-Patterns and Misuse (Where to Be Careful)

Common pitfalls to avoid when applying PLD concepts:

| Anti-Pattern                                          | Problem                                                          |
| ----------------------------------------------------- | ---------------------------------------------------------------- |
| Unclassified "retry" after errors                     | Hides whether a Drift was detected and what Repair was attempted |
| Hard resets without prior Drift classification        | Obscures the root cause and overuses R4-style behavior           |
| Logging only outcomes (success/failure)               | Prevents reconstruction of Drift/Repair/Reentry history          |
| Mixing non-PLD terms into metrics (e.g., "vibes off") | Breaks machine interpretability and taxonomy alignment           |

When in doubt, ensure you can answer:

> "What kind of Drift occurred, what Repair was tried, and how did we determine whether it worked?"

If this cannot be answered from your traces and metrics, your usage of PLD concepts is incomplete.

---

## 9. Cross-Links to Other Sections

For deeper dives beyond the Concepts directory:

* **Specifications (Levels 1–3)**

  * `docs/specifications/level_1_schema/pld_event.schema.json`
  * `docs/specifications/level_2_semantics/` (semantic spec and event matrix)
  * `docs/specifications/level_3_standards/PLD_taxonomy_v2.0.md`, `PLD_Runtime_Standard_v2.0.md`, `PLD_metrics_spec.md`

* **Architecture**

  * `docs/architecture/layers.md`
  * `docs/architecture/implementation_rules.md`
  * `docs/architecture/runtime_modes.md`

* **Patterns and Recipes**

  * `docs/patterns/01_llm/` (LLM behavior patterns)
  * `docs/patterns/02_ux/` (UX repair and pacing patterns)
  * `docs/patterns/03_system/` (runtime policy, failover, logging)
  * `docs/patterns/04_integration_recipes/` (integration recipes)

* **Runtime and Quickstart**

  * `pld_runtime/` (controllers, detection, enforcement, logging, schemas)
  * `quickstart/` (hello runtime, minimal demos, metrics quickcheck)

* **Analytics**

  * `analytics/metrics_frameworks/` (PRDR, VRL, and related frameworks)
  * `docs/metrics/pld_operational_metrics_cookbook.md`

Use this map as a **compass** while working with PLD: start from a concept in `docs/concepts/`, then follow links here to find the exact specifications, patterns, and runtime components you need.
