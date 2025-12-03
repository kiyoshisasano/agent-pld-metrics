<!--
component_id: pld_runtime_readme
kind: doc
area: runtime
status: stable
authority_level: 5
version: 2.0.1
license: Apache-2.0
purpose: Entry-point documentation for the PLD runtime directory.
-->

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

## Public API Surface (`pld_runtime/__init__.py`)

Beginning with **Runtime v2.0**, the package now exposes a **stable, intentionally minimal integration API** from the top-level namespace:

```python
from .detection.runtime_signal_bridge import (
    RuntimeSignalBridge,
    RuntimeSignal,
    SignalKind,
    EventContext,
    ValidationMode,
)
```

This surface defines the **official Level-5 boundary** for PLD runtime integrations.

It is the recommended import path for:

* LangGraph / LangChain / Swarm / AgentOps connectors
* orchestration frameworks and middleware
* examples, demos, and field experimentation
* production-facing integrations where stability matters

### ⚠️ Note on SimpleObserver

`SimpleObserver` (located under `ingestion/simple_observer.py`) is a **Level-5 convenience wrapper** that automates:

* EventContext construction
* turn sequencing
* latency measurement
* optional detector invocation

It is **not part of the stable public API surface**, and may evolve independently of the core bridge.
External integrations seeking long-term stability should rely on `RuntimeSignalBridge`.

---

## Design Intent

This API ensures that **external integrations remain stable** even if the internal folder structure evolves.

It establishes:

| Scope                                             | Status              | Notes                 |
| ------------------------------------------------- | ------------------- | --------------------- |
| `pld_runtime.<symbol>`                            | **Public / Stable** | Safe for external use |
| Internal folders (`detection/`, `logging/`, etc.) | **Private**         | Subject to change     |
| Schema, taxonomy, lifecycle rules                 | **Immutable**       | Defined by Levels 1–3 |

---

### Usage Rules

#### ✅ You SHOULD:

```python
from pld_runtime import RuntimeSignalBridge
```

* treat internal module paths as **implementation details**
* assume backward-compatibility for top-level API names only

#### ❌ You SHOULD NOT:

```python
# discouraged — bypasses stability guarantees
from pld_runtime.logging.runtime_logging_pipeline import RuntimeLoggingPipeline
```

* modify event dictionaries
* redefine or extend taxonomy values or lifecycle semantics

---

## Submodule Index

Each directory corresponds to a lifecycle stage.
Descriptions reflect current intent, not a locked standard.

| Module           | Definition                                                                                           | Notes                                     |
| ---------------- | ---------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| **schemas/**     | Canonical runtime schema envelopes                                                                   | MUST align with Level 1                   |
| **ingestion/**   | Normalize inputs into runtime-consumable structures; includes the high-level `SimpleObserver` facade | SHOULD avoid semantic inference           |
| **detection/**   | Extract drift/repair/reentry/threshold signals                                                       | SHOULD remain side-effect-free            |
| **enforcement/** | Structural + semantic validation and rule evaluation                                                 | MUST follow Level precedence              |
| **controllers/** | Runtime governance logic                                                                             | MAY route actions; MUST NOT mutate events |
| **logging/**     | Structured session traces and replay-supporting formats                                              | MUST preserve event ordering              |
| **failover/**    | Recovery, retry, and mitigation logic                                                                | SHOULD treat recovery conservatively      |

### Additional Note on `ingestion/simple_observer.py`

The `SimpleObserver` module provides an optional ergonomic interface that wraps
`RuntimeSignalBridge` and automates common runtime tasks.
It does **not** alter PLD semantics and remains within Level-5 boundaries.

---

## Built-in Drift Detection (Runtime v2.0)

The `detection/` module includes a small set of **experimental Level-5 detectors** intended for demonstration and evaluation.

Current implementations:

* `SchemaComplianceDetector` — detects missing required fields
* `SimpleKeywordDetector` — keyword-based drift detection

Detectors do not alter Levels 1–3 semantics; they simply observe runtime signals and emit compliant events.

---

## Failover Model Summary

Failover behavior is still under exploration. Current structures include:

* Backoff Policies
* Strategies
* Reconciliation Policy
* Orchestrator
* Registry

This model may evolve with field evaluation.

---

## Configuration Boundaries

| Category                           | Runtime Behavior | Expected Mutation |
| ---------------------------------- | ---------------- | ----------------- |
| Schema                             | Fixed            | ❌                 |
| Enforcement thresholds             | Configurable     | ✔                 |
| Logging transport                  | Pluggable        | ✔                 |
| Strategy behavior & failover logic | Experimental     | ✔                 |
| Event semantics                    | Immutable        | ❌                 |

---

## Minimal Integration Example

```python
from pld_runtime import (
    RuntimeSignalBridge,
    RuntimeSignal,
    SignalKind,
    EventContext,
    ValidationMode,
)

bridge = RuntimeSignalBridge(validation_mode=ValidationMode.STRICT)

signal = RuntimeSignal(kind=SignalKind.CONTINUE_NORMAL, payload={})
context = EventContext(
    session_id="demo-session",
    turn_sequence=1,
    source="runtime",
    model="gpt-4.1-mini",
    current_phase="continue",
)

event = bridge.build_event(signal, context)
print("Event:", event)
```

---

## ⚙️ System Requirements

To ensure runtime stability and correct timestamp handling:

* **Python:** **3.9+** is required.
    * The runtime relies on modern standard library features for timezone-aware timestamps (e.g., `datetime.now(timezone.utc)`).
    * Type hinting utilizes syntax consistent with modern Python standards.

> **Note:** Usage with Python 3.8 or older is **not supported** without manual backports and modification of datetime logic.

---

## Versioning and Compatibility

* Compatible with schema **v2.x**
* Behavior and naming MAY evolve during evaluation
* Breaking changes will be documented as stabilization approaches

Maintainer: **Kiyoshi Sasano**

---

This document reflects the current working understanding of the runtime and is subject to revision as research and feedback continue.

