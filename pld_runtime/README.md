---
path: pld_runtime/README.md
component_id: pld_runtime_readme
kind: doc
area: runtime
status: stable
authority_level: 5
version: 2.0.0
license: Apache-2.0
purpose: Entry-point documentation for the PLD runtime directory.
---

# PLD Runtime Package

Operational Engine for Phase Loop Dynamics
**Status: Working Draft (Exploration Stage)**

> This runtime is still evolving. Behavior, naming, and configuration may change as research continues and implementation feedback is collected.

⚠️ **This is a reference implementation.**
It is not positioned as a finalized or canonical runtime. Teams MAY choose to adopt components selectively or embed PLD behaviors within their own orchestration frameworks.

This runtime attempts to answer an operational question under evaluation:

> **“Given real turns, signals, and system behavior — what should the system do next?”**

The implementation reflects the current working interpretation of PLD runtime execution. It is intended to be testable, inspectable, and falsifiable.

---

## Overview

`pld_runtime` provides a Level 5 operational execution layer within the PLD ecosystem.

It consumes normalized turns, evaluates detection signals, applies structural and semantic enforcement rules, executes phase-driven control logic, and emits structured trace output suitable for replay and evaluation.

This package may evolve based on refinement of Levels 1–3 specifications, operational feedback, and observed performance characteristics across domains.

---

## Architecture Alignment

The runtime aligns to the PLD authority stack:

| Level | Purpose                                | Enforcement Role                             |
| ----- | -------------------------------------- | -------------------------------------------- |
| **1** | Canonical schema requirements          | MUST be followed                             |
| **2** | Semantic rules + event matrix          | MUST interpret but NOT modify                |
| **3** | Operational runtime expectations       | SHOULD align                                 |
| **5** | Implementation and orchestration layer | MAY add behavior but MAY NOT alter semantics |

This runtime DOES NOT redefine event semantics.
It reads PLD events, but MAY NOT modify their meaning, order, or structure.

### Non-Mutation Principle

Runtime components MUST NOT:

* rewrite PLD event fields such as `event_id`, `schema_version`, `timestamp`, or `session_id`
* alter lifecycle semantics or taxonomies defined in Levels 1–3
* generate inferred events outside the runtime signaling pathway

The implementation MAY:

* read and evaluate PLD state
* determine operational actions
* produce failover or runtime decisions

---

## Runtime Processing Flow

Runtime execution follows a staged pattern aligned to the conceptual PLD lifecycle.

### Canonical Flow

```
ingestion → detection → enforcement → controller → logging → failover (if applicable)
```

### Expanded Operational View

```
 ┌───────────┐     ┌───────────┐     ┌─────────────┐     ┌─────────────┐
 │ ingestion │ --> │ detection │ --> │ enforcement │ --> │ controller  │
 └─────┬─────┘     └──────┬────┘     └──────┬──────┘     └──────┬──────┘
       │                  │                │                    │
       │                  │                │                    ▼
       │                  ▼                ▼              failover (conditional)
       └──────────────→ logging → structured trace export
```

Failover is invoked only when standard policy resolution and control logic cannot restore a valid trajectory.

---

---

## Public API Surface (`pld_runtime/__init__.py`)

Beginning with **Runtime v2.0**, the package now exposes a **stable, intentionally minimal integration API** from the top-level namespace:

```python
from pld_runtime import (
    RuntimeSignalBridge,
    RuntimeSignal,
    SignalKind,
    EventContext,
    ValidationMode,
    RuntimeLoggingPipeline,
    JsonlExporter,
)

bridge = RuntimeSignalBridge(validation_mode=ValidationMode.STRICT)

signal = RuntimeSignal(kind=SignalKind.CONTINUE_NORMAL, payload={})
context = EventContext(
    session_id="demo",
    turn_sequence=1,
    source="runtime",
    model="gpt-4.1-mini",
    current_phase="continue",
)

event = bridge.build_event(signal, context)

pipeline = RuntimeLoggingPipeline(jsonl_exporter=JsonlExporter("logs/demo.jsonl"))
pipeline.on_event(event)

```

This surface defines the **official Level-5 boundary** for PLD runtime integrations.

It is the recommended import path for:

* LangGraph / LangChain / Swarm / AgentOps connectors
* orchestration frameworks and middleware
* examples, demos, and field experimentation
* production-facing integrations where stability matters

---

### Design Intent

This API exists to ensure that **external integrations remain stable** even if the internal folder structure evolves.

It establishes:

| Scope                                             | Status              | Notes                 |
| ------------------------------------------------- | ------------------- | --------------------- |
| `pld_runtime.<symbol>`                            | **Public / Stable** | Safe for external use |
| Internal folders (`detection/`, `logging/`, etc.) | **Private**         | Subject to change     |
| Schema, taxonomy, lifecycle rules                 | **Immutable**       | Defined by Levels 1–3 |

---

### Usage Rules

#### ✅ You SHOULD:

* import only from the top-level namespace:

  ```python
  from pld_runtime import RuntimeSignalBridge
  ```

* treat internal module paths as **implementation details**

* assume backward-compatibility for top-level API names only

#### ❌ You SHOULD NOT:

* import directly from internal paths:

  ```python
  # discouraged — bypasses stability guarantees
  from pld_runtime.logging.runtime_logging_pipeline import RuntimeLoggingPipeline
  ```

* modify event dictionaries built by the runtime

* redefine or extend taxonomy values (`event_type`, `phase`, `pld.code`, etc.)

---

### Why This Matters

The goal of PLD is to act as a **runtime reasoning layer**, not a library of loosely defined helper utilities.
By defining a **stable API boundary**, the system preserves:

* interoperability across agent frameworks
* predictable behavior under refactors
* replay-safe event semantics
* versioned compatibility with schema levels

> *“There may be many frameworks — but only one governing runtime boundary.”*

---

## Submodule Index (01–07)

Each directory corresponds to a lifecycle stage.
Descriptions reflect current intent, not a locked standard.

| Module              | Definition                                           | Notes                                     |
| ------------------- | ---------------------------------------------------- | ----------------------------------------- |
| **01_schemas/**     | Canonical runtime schema envelopes                   | MUST align with Level 1                   |
| **02_ingestion/**   | Normalize inputs into runtime-consumable structures  | SHOULD avoid semantic inference           |
| **03_detection/**   | Extract drift/repair/reentry/threshold signals       | SHOULD remain side-effect-free            |
| **04_enforcement/** | Structural + semantic validation and rule evaluation | MUST follow Level precedence              |
| **05_controllers/** | Runtime governance logic                             | MAY route actions; MUST NOT mutate events |
| **06_logging/**     | Structured session traces, replay-supporting formats | MUST preserve event ordering              |
| **07_failover/**    | Recovery, retry, and mitigation logic                | SHOULD treat recovery conservatively      |

---

## Failover Model Summary

Failover behavior is still under exploration. Current structure includes:

* **Backoff Policies** — timing strategy (constant/exponential/jitter)
* **Strategies** — operational mitigation attempts
* **Reconciliation Policy** — determine whether to continue, finalize, or recover
* **Orchestrator** — coordinates attempts and backoff windows
* **Registry** — factory interface for assembling runtime failover configurations

This model may evolve based on feedback and evaluation in long-horizon conversational settings.

---

## Configuration Boundaries

| Category                           | Runtime Behavior | Expected Mutation    |
| ---------------------------------- | ---------------- | -------------------- |
| Schema                             | Fixed            | ❌                    |
| Enforcement thresholds             | Configurable     | ✔                    |
| Logging transport                  | Pluggable        | ✔                    |
| Strategy behavior & failover logic | Experimental     | ✔ (under evaluation) |
| Event semantics                    | Immutable        | ❌                    |

Configuration is intended to be explicit and observable—silent fallbacks are discouraged.

---

## Extension and Implementation Notes

This implementation is intended to be extended through:

* strategy injection
* custom exporters
* alternative detectors
* experimental orchestration patterns

Developers SHOULD treat this runtime as a test harness for exploring PLD-aligned system behaviors.

---

## Compliance Notes

* Validation order MUST follow: **Level 1 → Level 2 → (Level 3 expectations) → Level 5**
* Trace immutability is required for reproducibility
* Normalization MUST NOT conceal or infer meaning

---

## Minimal Integration Example

```python
from pld_runtime import ingestion, detection, enforcement, controller, logging

turn = ingest(raw_input)
signals = detect(turn)
result = enforce(turn, signals)
decision = controller.process(turn, result)

logging_pipeline.on_event(decision.event)
```

Actual production integration MAY differ depending on orchestration frameworks.

---

## Versioning and Compatibility

* Compatible with schema **v2.x**
* Behavior and naming MAY evolve during evaluation
* Breaking changes will be documented once stabilization begins

Maintainer: **Kiyoshi Sasano**
Feedback is welcome and may influence future revisions.

---

This document reflects the current working understanding of the runtime and is subject to revision as research and feedback continue.






