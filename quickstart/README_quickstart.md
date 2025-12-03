<!--
path: quickstart/README_quickstart.md
component_id: quickstart_readme
kind: doc
area: quickstart
status: experimental
authority_level: 1
version: 2.0.1
license: Apache-2.0
purpose: Quickstart guide for PLD runtime usage examples.
-->

# PLD Runtime Quickstart Guide

This document provides a **practical introduction** to using the PLD runtime.  
It is designed for both:

* **Hands-on users running the examples immediately**, and  
* **Developers who want to understand the reasoning, structure, and constraints of PLD-compliant event logging.**

The Quickstart scripts in this folder demonstrate how to:

```text
RuntimeSignal → RuntimeSignalBridge → PLD Event → StructuredLogger → Output
```


## No manual event construction is required — **the runtime builds canonical PLD events for you.**

---

# 1. Requirements

### Python Version
* Python **3.10 or higher** recommended.

### Dependencies

Install required modules (if applicable):

```bash
pip install pld_runtime
```

> The Quickstart examples rely only on standard runtime APIs and do not require additional configuration.

---

# 2. Files in This Quickstart

| File                    | Purpose                                                               |
| ----------------------- | --------------------------------------------------------------------- |
| `easy_pld_demo.py`      | **Simplest Quickstart** — uses SimpleObserver (high-level 3-line API) |
| `hello_pld_runtime.py`  | Minimal Level-4 example — one signal → one event → stdout             |
| `minimal_pld_demo.py`   | Slightly larger example using the Level-4 runtime flow                |
| `run_minimal_engine.py` | Demonstrates a loop processing multiple signals in order              |
| `metrics_quickcheck/`   | Optional: validates example output metrics and includes a dashboard   |

The new **SimpleObserver-based demo** (`easy_pld_demo.py`) provides the fastest path to generating PLD events.  
The other examples illustrate the **lower-level Level-4 runtime pipeline**.

---

# 🔍 3. SimpleObserver — High-Level Quickstart API (New)

SimpleObserver is the recommended entry point for most users.  
It wraps the full PLD runtime pipeline and provides:

✔ Automatic `EventContext` construction  
✔ Automatic turn sequencing  
✔ Optional latency measurement  
✔ Optional detector execution  
✔ Zero-configuration logging (stdout by default)  
✔ 3-line usage for the simplest flow  

## Minimal example (from `easy_pld_demo.py`)

```python
from pld_runtime.ingestion.simple_observer import SimpleObserver

observer = SimpleObserver("session-001")
observer.log_turn("user", "Hello", "Hi there")
```

## Advanced traced turn

```python
with observer.trace_turn("user", "Complex task") as turn:
    # do work...
    turn.complete("Done")
```

## Optional drift detector

```python
from pld_runtime.detection.builtin_detectors import SimpleKeywordDetector
from pld_runtime.detection.drift_detector import DriftDetectorContext

detector_ctx = DriftDetectorContext(
    session_id="session-x",
    source="detector",
    validation_mode="strict",
    model="example-model",
    tool_name="easy_pld_demo",
)

keyword_detector = SimpleKeywordDetector(detector_ctx,
                                        keywords=["forbidden", "NG"],
                                        code="D1_instruction")

observer = SimpleObserver("session-x", detectors=[keyword_detector])
```

## When to use SimpleObserver

Use this when you want:

- Minimal boilerplate
- High-level behavioral logging
- Auto-computed latency
- Easy drift signaling

If you need direct control over `RuntimeSignalBridge`, see the Level-4 examples below.

---

## 🔍 4. Built-In Drift Detection (Runtime v2.0)

The Quickstart includes **built-in runtime detectors** that demonstrate how PLD identifies  
drift and emits `drift_detected` events — without requiring custom logic.  

Included detectors (`pld_runtime/detection/builtin_detectors.py`):

| Detector                   | Purpose                              | Example Trigger             |
| -------------------------- | ------------------------------------ | --------------------------- |
| `SchemaComplianceDetector` | Ensures required keys exist in input | Missing `"parking"` field   |
| `SimpleKeywordDetector`    | Detects prohibited / unsafe keywords | Contains disallowed keyword |

These detectors operate **at Level 5** and do **not modify Level 1–3 semantics**.  

The `hello_pld_runtime.py` example demonstrates triggering a drift:

```ini
payload = {"address": "Tokyo"}  # Missing "parking"
```

→ results in:

```js
{"event_type": "drift_detected", "taxonomy": "D2_context", ...}
```

---

# 5. How to Run

Run any demo script with Python:

```bash
python easy_pld_demo.py
```

or the traditional Level-4 examples:

```bash
python hello_pld_runtime.py
python minimal_pld_demo.py
python run_minimal_engine.py
```

Example output:

```json
{"schema_version": "2.0", "event_type": "continue_allowed", ...}
```

Each run produces:

- A unique event ID
- A timestamp (UTC, ISO-8601)
- PLD taxonomy code based on the emitted signal

---

# 6. How PLD Events Are Built

PLD event generation follows this flow:

| Stage | Component                          | Responsibility                                              |
| ----- | ---------------------------------- | ----------------------------------------------------------- |
| 1     | `RuntimeSignal`                    | Internal event description (drift, continue, repair, etc.)  |
| 2     | `EventContext`                     | Session, turn index, source, model, etc.                    |
| 3     | `RuntimeSignalBridge`              | Semantic mapping + schema enforcement → canonical PLD event |
| 4     | `StructuredLogger` + `EventWriter` | Output (stdout, file, etc.)                                 |

> **When using SimpleObserver, all steps above are performed automatically**.  
> You interact only with:  
> ✔ turn text  
> ✔ completion text  
> ✔ optional detectors

Events remain **immutable** after construction.

---

# 7. Runtime Rules and Constraints (Important)

The following constraints reflect canonical runtime rules; Quickstart examples operate as a consumer layer and therefore must not modify underlying PLD semantics.

Quickstart code **must NOT**:

- Manually craft PLD dictionaries
- Modify taxonomy codes
- Add or remove schema-defined fields
- Introduce new phases or event types

Quickstart must remain a **consumer layer**, not a reimplementation of runtime logic.

---

# 8. Example Usage Pattern (Level-4 Runtime)

This pattern appears in the Level-4 demo files:

```python
signal = RuntimeSignal(kind=SignalKind.CONTINUE_SYSTEM_TURN)
context = EventContext(session_id="demo", turn_sequence=1, source="runtime")
bridge = RuntimeSignalBridge(validation_mode=ValidationMode.STRICT)
event = bridge.build_event(signal, context)
logger.log(event)
```

## Example Usage Pattern (High-Level SimpleObserver)

```python
observer = SimpleObserver("session-001")
observer.log_turn("user", "Hello", "Hi there")
```

---

# 9. Next Steps

After running the examples, you can:  

🔹 Explore stdout or .`jsonl` log output  
🔹 Validate metrics:  

```bash
python metrics_quickcheck/verify_metrics_local.py
```

🔹 Build more complex flows using traced turns (`trace_turn`)  
🔹 Inject detectors for drift / repair scenarios  

---

# Summary

- PLD Runtime ensures **consistent, semantically aligned event generation**.
- Quickstart now supports both:
  - **High-level SimpleObserver API**
  - **Low-level RuntimeSignalBridge API**
- You interact with `signals and natural-language turns`, never raw PLD event dicts.

---

> PLD is not static rules —
> it is a sustained discipline for maintaining aligned shared reality with the user.
