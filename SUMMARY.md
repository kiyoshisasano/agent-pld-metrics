<!--
path: SUMMARY.md
kind: toc
status: stable
version: 2.0.0
authority_level: 2
license: Apache-2.0
purpose: High-level navigation index for the PLD repository aligned to the Level Model.
-->

# SUMMARY

## 0 — Overview & Orientation
- What is PLD?
- Level Model (`/docs/architecture/layers.md`)
- Roadmap (`/meta/ROADMAP.md`)
- Licensing & Policy (`/LICENSES/OVERVIEW.md`)
- Internal Pitch Kit (`/pitch/`)

---

## 1 — Core Specifications (Levels 1–3)

### 1.1 Structure — Level 1
- PLD Event Schema (`/docs/specifications/level_1_schema/pld_event.schema.json`)
- Envelope Examples (`/pld_runtime/schemas/runtime_event_envelope.examples.md`)

### 1.2 Semantics — Level 2
- Semantic Specification (`/docs/specifications/level_2_semantics/PLD_Event_Semantic_Spec_v2.0.md`)
- Event Matrix (`/docs/specifications/level_2_semantics/event_matrix.yaml`)
- Taxonomy Diagram (`/docs/specifications/level_3_standards/reference/PLD_taxonomy_v2.0_diagram.svg`)

### 1.3 Operational Standards — Level 3
- Runtime Standard (`/docs/specifications/level_3_standards/PLD_Runtime_Standard_v2.0.md`)
- Metrics Specification (`/docs/specifications/level_3_standards/PLD_metrics_spec.md`)
- Traceability Matrix (`/docs/specifications/validation/traceability_matrix.md`)

---

## 2 — Runtime Implementation (Level 5)

- Runtime Core (`/pld_runtime/`)
- Detection Components (`/pld_runtime/detection/`)
- Enforcement (`/pld_runtime/enforcement/`)
- Logging & Telemetry (`/pld_runtime/logging/`)
- Controllers (`/pld_runtime/controllers/`)
- Ingestion (`/pld_runtime/ingestion/`)
- Failover & Recovery (`/pld_runtime/failover/`)

---

## 3 — Quickstart & Recipes (Level 4)

### 3.1 Quickstart
- hello_pld_runtime.py
- run_minimal_engine.py
- metrics quickcheck (`/quickstart/metrics_quickcheck/`)

### 3.2 Integration Recipes
- LangGraph Integration (`/docs/patterns/03_system/implementation_guides/langgraph_integration.md`)
- Assistants API Integration (`/docs/patterns/03_system/implementation_guides/assistants_api_integration.md`)
- Rasa Template (`/docs/patterns/03_system/implementation_guides/rasa_action_templates.md`)
- Observer Mode Example (`/examples/langgraph_assistants/`)

---

## 4 — Patterns, Concepts & Practices
- Operator Primitives (`/docs/concepts/operator_primitives/`)
- System Patterns (`/docs/patterns/03_system/`)
- UX Patterns (`/docs/patterns/02_ux/`)
- Repair Strategies & Drift Model (`/docs/concepts/`)

---

## 5 — Analytics & Evaluation

- Metrics Frameworks (`/analytics/metrics_frameworks/`)
- Benchmarks (`/analytics/multiwoz_2.4_n200/`)
- Case Studies (`/analytics/case_study_end_to_end.md`)

---

## 6 — Field Adoption Playbooks
- Anti-Patterns
- Trace Examples
- Operational Onboarding
- Alignment Protocols

