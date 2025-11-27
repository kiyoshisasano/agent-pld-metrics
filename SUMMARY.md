---
path: SUMMARY.md
kind: toc
status: stable
version: 2.0.0
authority_level: 2
license: Apache-2.0
purpose: High-level navigation index for the PLD repository aligned to the Level Model.
---

# SUMMARY

## 0 — Overview
- What is PLD?
- Version & Scope
- Level Model Overview (`/docs/architecture_layers.md`)
- Change Log (`/meta/CHANGELOG.md`)
- Versioning Policy (`/meta/VERSIONING_POLICY.md`)

---

## 1 — Core Specifications (Levels 1–3)

### 1.1 Level 1 — Structural Schema
- PLD Event Schema (`/docs/schemas/pld_event.schema.json`)
- Event Matrix (`/docs/schemas/event_matrix.yaml`)
- Metrics Schema (`/docs/schemas/metrics_schema.yaml`)
- Schema Examples (`/pld_runtime/01_schemas/runtime_event_envelope.examples.md`)

### 1.2 Level 2 — Semantic Specification
- PLD Event Semantic Spec v2.0 (`/docs/PLD_Event_Semantic_Spec_v2.0.md`)
- Event Matrix Reference (`/docs/event_matrix.md`)
- Phase and Prefix Rules
- Taxonomy Diagram (`/docs/taxonomy/PLD_taxonomy_v2.0_diagram.svg`)

### 1.3 Level 3 — Operational Standards
- PLD Runtime Standard v2.0 (`/docs/PLD_Runtime_Standard_v2.0.md`)
- Metrics Specification (`/docs/metrics/PLD_metrics_spec.md`)
- Taxonomy v2.0 (`/docs/taxonomy/PLD_taxonomy_v2.0.md`)
- Validation Traceability Map (`/docs/validation/PLD_v2_Traceability_Map.md`)

---

## 2 — Runtime Implementation (Level 5)

### 2.1 Runtime Core
- Runtime Event Envelope (`/pld_runtime/01_schemas/runtime_event_envelope.json`)
- RuntimeSignalBridge (`/pld_runtime/03_detection/runtime_signal_bridge.py`)
- Enforcement Rules (`/pld_runtime/04_enforcement/`)
- Controller Logic (`/pld_runtime/05_controllers/`)

### 2.2 Logging & Telemetry
- Structured Logger (`/pld_runtime/06_logging/structured_logger.py`)
- Event Writers (`/pld_runtime/06_logging/event_writer.py`)
- Runtime Logging Pipeline (`/pld_runtime/06_logging/runtime_logging_pipeline.py`)
- Session Trace Buffer

### 2.3 Ingestion & Normalization
- Ingestion Config (`/pld_runtime/02_ingestion/ingestion_config.py`)
- MultiWOZ Loader
- Normalization Logic

### 2.4 Failover & Recovery
- Failover Strategies (`/pld_runtime/07_failover/`)
- Backoff Policies
- Strategy Registry

### 2.5 Integration Surface (Public Runtime API)

- Public API (`/pld_runtime/__init__.py`)
- Specification & Stability Contract (`/pld_runtime/README.md#public-api-surface`)
- Lifecycle Notes:
  - `init_pld_observer()` — initialize observer stack
  - `shutdown_pld_observer()` — optional finalization step for flushing buffered logs

---

## 3 — Level 4: Quickstart (Consumer Layer)

### 3.1 Getting Started
- hello_pld_runtime.py
- run_minimal_engine.py
- Minimal Demo (`/quickstart/examples/minimal_pld_demo.py`)

### 3.2 Operator Primitives
- Drift Detection
- Soft Repair
- Hard Repair
- Latency Control
- Reentry Operators

### 3.3 Patterns & Recipes
- Runtime Patterns (`/quickstart/patterns/`)
- Integration Recipes (`/quickstart/patterns/04_integration_recipes/`)
- Tooling Patterns
- RAG / LangGraph / Rasa Integration

### 3.4 Metrics Quickstart
- Verification Scripts (`/quickstart/metrics/verify_metrics_local.py`)
- Dashboards (`/quickstart/metrics/dashboards/`)
- Example Logs (`/quickstart/metrics/datasets/pld_events_demo.jsonl`)
- Reporting Examples

---

## 4 — Analytics & Evaluation

- PRDR Framework (`/analytics/PRDR_framework.md`)
- VRL Framework (`/analytics/VRL_framework.md`)
- Clustering & Observability Studies
- Benchmarks & Datasets (MultiWOZ 2.4)
- Case Studies

---

## 5 — Field Adoption Playbooks

- Trace Examples
- Anti-Patterns
- Role Alignment Guide
- Operational Onboarding
- Conversation Protocols

---

## 6 — Meta & Governance

- ROADMAP (`/meta/ROADMAP.md`)
- Manifest Spec (`/meta/METADATA_MANIFEST_SPEC.md`)
- Contribution Guidelines (`/docs/contributing/PLD_Runtime_Implementation_Rules.md`)
- Licenses & Trademark Policy (`/LICENSES/`)
- Citation (`/LICENSES/citation.bib`)
