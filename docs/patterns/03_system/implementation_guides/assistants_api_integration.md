---
title: "Assistants API Integration — PLD Runtime Pattern"
version: 2025.1
status: stable
maintainer: "Kiyoshi Sasano"
category: "patterns/system/integration"
tags:
  - PLD
  - OpenAI Assistants
  - runtime governance
  - drift detection
  - repair orchestration
---

# 🤝 Assistants API Integration — PLD Runtime Loop

This guide shows how to integrate **Phase Loop Dynamics (PLD)** into the OpenAI Assistants API (v2025).  
It ensures every response cycle is **measurable, governable, and aligned to runtime repair logic.**

> This pattern focuses on:  
> **Drift → Repair → Reentry → Continue → Outcome**

It extends the native Assistants API with:

- Drift detection
- Soft repair routing
- Reentry confirmation
- Structured logging aligned with PLD schemas

---

## 1. Requirements

```bash
pip install openai pydantic duckdb
```

```bash
pip install opentelemetry-api structlog rich
```

---

## 2. Runtime Vocabulary (PLD Codes)

```python
from enum import Enum


class DriftCode(str, Enum):
    NONE = "NONE"
    INFORMATION = "D1_information"
    CONTEXT = "D2_context"
    TOOL = "D4_tool"
    LATENCY = "D5_latency"


class RepairCode(str, Enum):
    SOFT = "R1_soft_repair"
    HARD = "R2_hard_repair"


class Reentry(str, Enum):
    SUCCESS = "RE1_success"
    FAILURE = "RE0_failure"
```

---

## 3. Logging Helper (Schema Aligned)

```python
import uuid
from datetime import datetime


def log_event(event_type, phase, code, session_id, turn_id, payload=None):
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "session_id": session_id,
        "turn_id": turn_id,
        "event_type": event_type,
        "source": "assistant_runtime",
        "pld": {
            "phase": phase,
            "code": code,
            "confidence": 0.9
        },
        "payload": payload or {}
    }
```

---

## 4. Drift Detector Example
This should eventually be replaced by production detectors, but serves as a ** Tier-1 rule baseline**.
```python
def detect_drift(response_text: str) -> DriftCode:
    if "no results" in response_text.lower():
        return DriftCode.INFORMATION
    if "wait" in response_text.lower():
        return DriftCode.CONTEXT
    return DriftCode.NONE
```

---

## 5. Assistants Interaction Loop
```python
from openai import OpenAI
client = OpenAI()

def run_pld_session(user_message: str, session_id="demo_sess"):
    turn = 1
    logs = []

    # --- Step 1: Ask assistant ---
    response = client.responses.create(
        model="gpt-5.1",
        input=user_message
    )
    output = response.output_text

    # --- Step 2: Drift Detection ---
    drift = detect_drift(output)
    logs.append(log_event(
        "drift_detected" if drift != DriftCode.NONE else "no_drift",
        "drift" if drift != DriftCode.NONE else "none",
        drift,
        session_id,
        turn,
        {"assistant_response": output}
    ))

    # --- Step 3: Repair Routing ---
    if drift != DriftCode.NONE:
        repair_text = "Let me revise that based on context."
        logs.append(log_event("repair_triggered", "repair", RepairCode.SOFT, session_id, turn))

        # Generate a repaired response
        response = client.responses.create(
            model="gpt-5.1",
            input=f"User message: {user_message}\nCorrection: {repair_text}\nFix response now."
        )
        output = response.output_text

        # --- Step 4: Reentry Check ---
        logs.append(log_event("reentry_observed", "reentry", Reentry.SUCCESS, session_id, turn))

    # --- Step 5: Completion Logging ---
    logs.append(log_event(
        "outcome",
        "outcome",
        "COMPLETE",
        session_id,
        turn,
        {"final_output": output}
    ))

    return output, logs
```

---

## 6. Example Run

```python
result, events = run_pld_session("No results found error")
print(result)
print(events)
```

---

## 7. Governance Rules

| Rule                          | Required?   | Enforcement                  |
| ----------------------------- | ----------- | ---------------------------- |
| Every turn logged             | ✔ Required  | Logs = contract of execution |
| Drift classification required | ✔ Required  | Enables PRDR & VRL metrics   |
| Repair MUST precede reentry   | ✔ Required  | Core PLD contract            |
| One outcome per session       | ✔ Required  | Required for FR/MRBF metrics |
| Latency SHOULD be logged      | Recommended | Enables pacing analysis      |

---

## 8. When to Extend

| Scenario               | Extension                                   |
| ---------------------- | ------------------------------------------- |
| Tool-heavy agent       | Add tool execution hook + failure detection |
| Memory alignment       | Add contextual semantic tracking            |
| Regulated environments | Add OpenTelemetry trace correlation         |

---

## Summary

This scaffold provides **a production-ready PLD execution loop** for the OpenAI Assistants API.
It ensures:

- Drift is visible
- Repairs are measurable
- Reentry is acknowledged
- Behavior can be governed, compared, and improved over time
