# Logging & Schema Validation Patterns (PLD System Layer)

📄 **Version:** 2.0 — Unified Edition
🔧 **Status:** Draft (Level 4 — Informative)
📚 **Scope:** Runtime Logging → Validation → Persistence → Analysis

---

## 1. Purpose & Scope

This document provides a **unified practical guide** for logging, validating, storing, and analyzing PLD event streams.

It combines the strengths of both:

* **Quickstart runtime examples** (for developers and experimentation)
* **System-level patterns** (for observability, governance, and analytics)

This document is **not normative**, but supports learning, prototyping, and operational readiness.

Referenced authoritative specifications:

* `quickstart/metrics/schemas/pld_event.schema.json`
* `quickstart/metrics/schemas/metrics_schema.yaml`

---

## 2. Why Logging Matters in PLD

Logging in a PLD-enabled system ensures the runtime is:

* **Observable** → we can see what occurred
* **Measurable** → event streams become metrics
* **Auditable** → decisions are reproducible and reviewable
* **Recoverable** → drift, repair, and reentry phases are traceable

PLD logs represent the **behavioral timeline of a conversation**, not just raw messages.

---

## 3. Logging Modes

A PLD runtime typically supports two categories of output:

| Mode                              | Purpose                      | Example Output                        | Best Used In                       |
| --------------------------------- | ---------------------------- | ------------------------------------- | ---------------------------------- |
| **Human-readable logs**           | Teaching, debugging, demos   | Emoji + narrative text                | Local development, onboarding      |
| **Machine-friendly logs (JSONL)** | Replay, analytics, ingestion | JSON objects per event, one line each | Production logging, data pipelines |

### Examples

**Human-mode representation:**

```
🚨 drift_detected (D4_tool_error)
Phase: drift | Turn: 2 | Event ID: 08d2b...
```

**JSONL format:**

```json
{"event_type":"drift_detected","pld":{"phase":"drift","code":"D4_tool_error"}, ...}
```

---

## 4. Schema Alignment Responsibilities

Runtime behavior and storage validation serve **different roles**.

| Layer               | Role                                         | Validation Purpose                    |
| ------------------- | -------------------------------------------- | ------------------------------------- |
| Runtime             | Ensures events follow PLD lifecycle & matrix | Prevent invalid sequence or semantics |
| Ingestion / Storage | Ensures structural adherence to schema       | Data cleanliness, analytics readiness |

### Validation modes

* **strict** → Raise error immediately for semantic violations.
* **warn** → Continue execution, log warnings.

Example warning:

```
[WARN][semantic] `repair_triggered` MUST map to phase `repair`, got `continue`.
```

---

## 5. Lifecycle Logging Examples

### 5.1 Minimal No-Drift Turn

```json
{
  "event_id": "b07cc93c-0178-4a59-b9c4-f1d78afe25fd",
  "timestamp": "2025-02-01T13:22:41Z",
  "session_id": "demo_001",
  "turn_sequence": 1,
  "event_type": "info",
  "pld": { "phase": "none", "code": "INFO_init" }
}
```

### 5.2 Canonical Drift → Repair → Reentry Chain

```json
[
  { "event_type": "drift_detected", "pld": { "phase": "drift", "code": "D2_context" }},
  { "event_type": "repair_triggered", "pld": { "phase": "repair", "code": "R1_soft_repair" }},
  { "event_type": "reentry_observed", "pld": { "phase": "reentry", "code": "RE1_intent" }}
]
```

### 5.3 Outcome Event — Session Boundary

```json
{
  "event_type": "session_closed",
  "pld": { "phase": "outcome", "code": "O1_session_closed" },
  "metrics": {
    "drift_events_count": 1,
    "repair_events_count": 1,
    "session_closed_outcome_count": 1
  }
}
```

---

## 6. Validation Examples

### 6.1 PLD Runtime Validation Example

```python
from run_minimal_engine import MinimalEngine
engine = MinimalEngine(validation_mode="strict")
```

### 6.2 Full JSON Schema Validation (Batch)

```python
from jsonschema import validate
import json

with open("quickstart/metrics/schemas/pld_event.schema.json") as f:
    schema = json.load(f)

validate(event, schema)
```

---

## 7. Analysis & Query Pipeline (End-to-End Bridge)

This section connects:

* **Quickstart engine** (`run_minimal_engine.py`)
* **Runtime logging stack** (`pld_runtime/06_logging/*`)
* **Metrics & analytics layer** (`quickstart/metrics/*`)

The goal is to show how PLD events produced in quickstart examples can flow into the
same JSONL + analytics pipelines used by the full runtime.

> ⚠️ **Execution Context Notice**
>
> This example bridges the Quickstart layer and the full PLD Runtime system.
> To run it successfully:
>
> * Execute Python from the **repository root** (NOT from inside `quickstart/`).
> * Ensure both packages can be imported:
>
> ```python
> import pld_runtime
> import quickstart
> ```
>
> * The schema path reference corresponds to the Quickstart mirror:
>
>   `quickstart/metrics/schemas/pld_event.schema.json`
>
> This is intentional: Quickstart provides a clean learning sandbox, while
> the `pld_runtime/` copy mirrors the canonical production spec.
>
> If you see:
>
> ```bash
> ModuleNotFoundError: No module named 'pld_runtime'
> ```
>
> Then run from the repository root:
>
> ```bash
> cd <repo-root>
> python quickstart/examples/minimal_pld_demo.py
> ```

### 7.1 Minimal Bridge: MinimalEngine → StructuredLogger → JSONL

The following example wires the quickstart engine into the runtime logging stack
and writes JSONL records compatible with `metrics/datasets/pld_events_demo.jsonl`.

```python
import json
from pathlib import Path

from pld_runtime.logging.logging_config import (
    LoggingConfig,
    configure_logging,
)
from quickstart.run_minimal_engine import MinimalEngine

# 1. Configure logging to use JSONL writer
cfg = LoggingConfig(
    mode="compact",              # or "debug" / "evaluation"
    writer="jsonl",             # use file-based JSONL writer
    writer_path="logs/pld_events_demo.jsonl",
)

logging_ctx = configure_logging(cfg)
logger = logging_ctx.logger

# 2. Create a MinimalEngine (quickstart reference implementation)
engine = MinimalEngine()

user_inputs = [
    "Let's continue with the main task.",
    "Can we switch topics and talk about cooking?",
    "Okay, back to the original plan.",
]

# 3. Run turns and emit PLD events through the StructuredLogger
for text in user_inputs:
    final_response, events = engine.run_turn(text)

    # Optionally inspect the response in development mode
    print("User:", text)
    print("Agent:", final_response)

    # Persist each PLD event via the runtime logging stack
    for e in events:
        # e is already a PLD v2.0 event (matches pld_event.schema.json)
        logger.log_pld_event(session_id=e["session_id"], event=e)
```

Key points:

* The quickstart engine preserves `schema_version`, `pld.phase`, `pld.code`,
  `turn_sequence`, and `ux.user_visible_state_change` in each event.
* `StructuredLogger` wraps these events into transport-friendly records and writes
  them as JSONL lines via the configured writer.
* The resulting file `logs/pld_events_demo.jsonl` can be ingested by the metrics
  tooling under `quickstart/metrics/` without additional transformation.

### 7.2 JSONL → DuckDB → Metrics

Once events are written as JSONL, they can be ingested into DuckDB (or any
columnar/analytic store) for querying and dashboarding.

```sql
CREATE TABLE events AS
SELECT * FROM read_json_auto('logs/*.jsonl');
```

Example query:

```sql
SELECT pld->>'code', COUNT(*)
FROM events
WHERE event_type = 'drift_detected'
GROUP BY 1;
```

This pattern generalizes to metrics such as PRDR, VRL, MRBF, and REI using the
aggregation rules defined in `metrics_schema.yaml` and the cookbook in
`docs/07_pld_operational_metrics_cookbook.md`.

## 8. Best Practices & Anti-Patterns

| Recommendation                                  | Status          |
| ----------------------------------------------- | --------------- |
| Always log outcome exactly once per session     | ✅ Required      |
| DO NOT mix formatting logic into schema objects | 🚫 Anti-pattern |
| Use JSONL for scalable storage                  | ⭐ Recommended   |
| Use strict mode during development              | ⭐ Recommended   |

---

## 9. Summary

Logging in PLD systems provides:

* **traceability**
* **governance alignment**
* **replayability**
* **measurement for improvement**

Structured events become evidence of runtime reasoning — not just output text.

---

📎 Suggested next steps:

* Run: `quickstart/examples/minimal_pld_demo.py`
* Inspect JSONL output
* Validate using both strict and warn modes
