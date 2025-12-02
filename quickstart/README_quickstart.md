<!--
path: quickstart/README_quickstart.md
component_id: quickstart_readme
kind: doc
area: quickstart
status: experimental
authority_level: 1
version: 2.0.0
license: Apache-2.0
purpose: Quickstart guide for PLD runtime usage examples.
-->

# PLD Runtime Quickstart Guide

This document provides a **practical introduction** to using the PLD runtime. It is designed for both:

* **Hands-on users running the examples immediately**, and
* **Developers who want to understand the reasoning, structure, and constraints of PLD-compliant event logging.**

The Quickstart scripts in this folder demonstrate how to:

```
RuntimeSignal → RuntimeSignalBridge → PLD Event → StructuredLogger → Output
```

## No manual event construction is required — **the runtime builds canonical PLD events for you.**

## 1. Requirements

### Python Version

* Python **3.10 or higher** recommended.

### Dependencies

Install required modules (if applicable):

```bash
pip install pld_runtime
```

> The Quickstart examples rely only on standard runtime APIs and do not require additional configuration.

---

## 2. Files in This Quickstart

| File                    | Purpose                                                               |
| ----------------------- | --------------------------------------------------------------------- |
| `hello_pld_runtime.py`  | Smallest "Hello World" example — one signal, one event, stdout output |
| `minimal_pld_demo.py`   | Slightly larger example using the same runtime flow                   |
| `run_minimal_engine.py` | Demonstrates a loop processing multiple signals in order              |
| `metrics_quickcheck/`   | Optional: validates example output metrics and includes a dashboard   |

These examples are intentionally lightweight and **consumer-only**, meaning they *use* the runtime but do not modify schema or enforcement logic.

---

## 3. How to Run

Run any demo script with Python:

```bash
python hello_pld_runtime.py
```

You should see output similar to:

```json
{"schema_version": "2.0", "event_type": "continue_allowed", ... }
```

Each run produces:

* A unique event ID
* A timestamp (UTC, ISO-8601 format)
* PLD taxonomy code based on the provided `RuntimeSignal`

---

## 4. How PLD Events Are Built

PLD event generation in Quickstart follows this flow:

| Stage | Component                        | Responsibility                                                       |
| ----- | -------------------------------- | -------------------------------------------------------------------- |
| 1     | `RuntimeSignal`                  | Describe the system’s internal event (e.g., drift, continue, repair) |
| 2     | `EventContext`                   | Describe session, turn index, source, model, etc.                    |
| 3     | `RuntimeSignalBridge`            | Apply semantic mapping + schema rules to build a canonical PLD event |
| 4     | `StructuredLogger + EventWriter` | Output the final PLD event (stdout, file, transport, etc.)           |

> Once created by the bridge, an event is considered **immutable**. Quickstart code must not alter structure, taxonomy, or schema fields.

---

## 5. Runtime Rules and Constraints (Important)

Quickstart code **must NOT**:

* Manually craft PLD dictionary structures
* Change taxonomy codes (`C0_*`, `D1_*`, etc.)
* Add or modify fields that contradict Level 1–3 specs
* Introduce new event types or phases

Quickstart must remain a **consumer layer**, not an implementation of runtime logic.

---

## 6. Example Usage Pattern

All valid Quickstart examples follow this structure:

```python
signal = RuntimeSignal(kind=SignalKind.CONTINUE_SYSTEM_TURN)
context = EventContext(session_id="demo", turn_sequence=1, source="runtime")
bridge = RuntimeSignalBridge(validation_mode=ValidationMode.STRICT)
event = bridge.build_event(signal, context)
logger.log(event)
```

This ensures:

* Schema compliance
* Taxonomy correctness
* Runtime translation consistency

---

## 7. Next Steps

After running the examples, you can:

🔹 Explore the event outputs in `stdout` or as `.jsonl` logs
🔹 Run the optional metric validator:

```bash
python metrics_quickcheck/verify_metrics_local.py
```

🔹 Modify Quickstart logic **only** via signals and context — not event structure

---

## Summary

* PLD Runtime ensures **repeatable, semantically aligned event generation**.
* Quickstart demonstrates the **minimum responsibilities** needed to operate the runtime.
* You interact only with **signals + context**, never raw event construction.

---

If you're ready, proceed to modify and run: `hello_pld_runtime.py`.

👍 You now have a working environment for PLD-compliant event generation.


---

> PLD is not static rules —  
> it is a sustained discipline for maintaining aligned shared reality with the user.

