---
title: "LangGraph Integration — PLD Runtime Alignment Pattern"
version: 2025.1
status: stable
maintainer: "Kiyoshi Sasano"
category: "patterns/system/integration"
tags:
  - PLD
  - LangGraph
  - orchestration
  - drift detection
  - repair policies
  - logging
---

# 🔧 LangGraph Integration Guide for PLD Runtime Systems

This file provides a **ready-to-run LangGraph template** that implements:

> **Drift → Repair → Reentry → Continue → Outcome**

It is fully aligned with:

- `quickstart/metrics/schemas/pld_event.schema.json`  
- `quickstart/metrics/schemas/metrics_schema.yaml`  
- `03_system/runtime_policy_patterns.md`  

---

## 1. Installation

```bash
pip install langgraph langchain openai pydantic duckdb
```

Optional dependencies:
```bash
pip install opentelemetry-api rich
```

---

## 2. Runtime Concepts

The graph executes with a **PLD governance loop**, where every turn may trigger:

| PLD Phase  | Trigger Condition                                   |
| ---------- | --------------------------------------------------- |
| `drift`    | System output diverges from expected meaning        |
| `repair`   | System acknowledges and corrects drift              |
| `reentry`  | User or system confirms the system is aligned again |
| `continue` | Normal execution                                    |
| `outcome`  | The session completes or fails                      |

---

## 3. Shared Utilities (Logging + Codes)

```python
import uuid
from datetime import datetime
from enum import Enum

def now():
    return datetime.utcnow().isoformat() + "Z"


class DriftCode(str, Enum):
    NONE = "NONE"
    INFO = "D1_information"
    CONTEXT = "D2_context"
    TOOL = "D4_tool"
    LATENCY = "D5_latency"


class RepairCode(str, Enum):
    SOFT = "R1_soft_repair"
    HARD = "R2_hard_repair"


class ReentryCode(str, Enum):
    SUCCESS = "RE1_success"
    FAIL = "RE0_fail"
```

### Logging Helper (schema-aligned)

```python
def log_event(event_type, phase, code, session_id, turn_id, payload=None):
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": now(),
        "session_id": session_id,
        "turn_id": turn_id,
        "event_type": event_type,
        "source": "runtime",
        "pld": {
            "phase": phase,
            "code": code,
            "confidence": 0.85
        },
        "payload": payload or {}
    }
```

---

## 4. LangGraph Nodes
🧩 `detect_drift_node`
```python
def detect_drift_node(state):
    text = state["input"]

    if "no results" in text.lower():
        state["drift"] = DriftCode.INFO
    elif "wait" in text.lower():
        state["drift"] = DriftCode.CONTEXT
    else:
        state["drift"] = DriftCode.NONE

    state["events"].append(
        log_event("drift_detected" if state["drift"] != DriftCode.NONE else "info",
                  "drift" if state["drift"] != DriftCode.NONE else "none",
                  state["drift"],
                  state["session_id"],
                  state["turn"])
    )

    return state
```

---

### 🧩 Soft Repair Node

```python
SOFT_REPAIR_RESPONSES = {
    DriftCode.INFO: "Let me revise that response based on available information.",
    DriftCode.CONTEXT: "Thanks — let's re-anchor the context.",
    DriftCode.TOOL: "The tool failed. Retrying with fallback.",
}

def repair_node(state):
    msg = SOFT_REPAIR_RESPONSES.get(state["drift"], "Correcting alignment.")

    state["output"] = msg
    state["events"].append(
        log_event("repair_triggered", "repair", RepairCode.SOFT,
                  state["session_id"], state["turn"])
    )
    return state
```

---

### 🧩 Reentry Node

```python
def reentry_node(state):
    state["events"].append(
        log_event("reentry_observed", "reentry", ReentryCode.SUCCESS,
                  state["session_id"], state["turn"])
    )
    state["drift"] = DriftCode.NONE
    return state
```

---

### 🧩 Normal Task Execution Node

```python
def task_node(state):
    query = state["input"]
    state["output"] = f"[TASK EXECUTION] → {query}"
    return state
```

---

## 5. Routing Logic

```python
from langgraph.graph import StateGraph

workflow = StateGraph()

workflow.add_node("detect", detect_drift_node)
workflow.add_node("repair", repair_node)
workflow.add_node("reentry", reentry_node)
workflow.add_node("task", task_node)

workflow.add_edge("detect", "repair", condition=lambda s: s["drift"] != DriftCode.NONE)
workflow.add_edge("detect", "task", condition=lambda s: s["drift"] == DriftCode.NONE)

workflow.add_edge("repair", "reentry")
workflow.add_edge("reentry", "task")

workflow.set_entry_point("detect")
agent = workflow.compile()
```

---

## 6. Running the System

```python
session = {"session_id": "sess_001", "turn": 1, "events": []}

result = agent.invoke({**session, "input": "No results found error"})
print(result["output"])
print(result["events"])
```

---

## 7. Governance Notes

| Rule                                          | Enforcement          |
| --------------------------------------------- | -------------------- |
| Every turn logs at least one event            | Required             |
| Drift MUST precede repair                     | Required             |
| Reentry MUST occur before normal continuation | Required             |
| Outcome must be logged once per session       | Strongly recommended |

---

## 8. When to Extend

| Scenario                    | You should add                 |
| --------------------------- | ------------------------------ |
| Tool-rich agent             | Custom `tool_handoff_node()`   |
| Long-term memory alignment  | Memory check node              |
| Multi-phase repair policies | Hard repair + failover routing |

---

## Summary
This template is the **canonical PLD LangGraph scaffold**.
It ensures:

- Drift is detectable
- Repair is measurable
- Alignment recovery is tracked
- Systems remain governable over time
