---
title: "Rasa Integration Templates — PLD Runtime Hooks"
version: "2025.1"
status: stable
maintainer: "Kiyoshi Sasano"
category: "integration/system"
tags:
  - PLD
  - Rasa
  - NLU
  - action server
  - conversational governance
---

# 🤖 Rasa Action Templates for PLD Runtime

This guide contains **copy-paste integration templates** to embed  
**Phase Loop Dynamics (PLD)** into a Rasa environment.

> Goal: enable **Drift → Repair → Reentry → Continue → Outcome logging**  
inside an existing conversational assistant without replacing its core logic.

---

## 1. Prerequisites

```bash
pip install rasa-sdk pydantic
```

Optional (recommended):

```bash
pip install opentelemetry-api structlog
```

---

```bash
pip install opentelemetry-api structlog
```

---

## 2. PLD Runtime Vocabulary

```python
from enum import Enum


class DriftCode(str, Enum):
    NONE = "NONE"
    CONTEXT = "D2_context"
    INFORMATION = "D1_information"
    CONTRADICTION = "D3_contradiction"


class RepairCode(str, Enum):
    SOFT = "R1_soft_repair"
    HARD = "R2_hard_repair"


class ReentryCode(str, Enum):
    SUCCESS = "RE1_success"
    FAILURE = "RE0_failure"
```

---

## 3. PLD Logging Utility (Schema-Aligned)

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
        "source": "rasa_action_server",
        "pld": {
            "phase": phase,
            "code": code,
            "confidence": 0.9
        },
        "payload": payload or {}
    }
```

---

## 4. Drift Detection Hook (Middleware-Style)

Place this in `your action.py` file:
```python
def detect_drift(user_message: str) -> DriftCode:
    if "wait" in user_message.lower():
        return DriftCode.CONTEXT
    if "that's wrong" in user_message.lower():
        return DriftCode.CONTRADICTION
    return DriftCode.NONE
```

---

## 5.Example PLD-Aware Action

```python
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionHotelSearch(Action):
    def name(self):
        return "action_hotel_search"

    def run(self, dispatcher, tracker: Tracker, domain):
        session_id = tracker.sender_id
        turn_id = tracker.latest_message.get("metadata", {}).get("turn_id", tracker.events_since_last_restart())

        user_text = tracker.latest_message.get("text", "")
        drift = detect_drift(user_text)

        logs = []

        # --- Step 1: Drift detection logging ---
        logs.append(log_event(
            "drift_detected" if drift != DriftCode.NONE else "no_drift",
            "drift" if drift != DriftCode.NONE else "none",
            drift,
            session_id,
            turn_id,
            {"user_text": user_text}
        ))

        # --- Step 2: Soft repair if drift found ---
        if drift != DriftCode.NONE:
            repair_msg = "Let me correct that—adjusting context..."
            dispatcher.utter_message(text=repair_msg)

            logs.append(log_event(
                "repair_triggered",
                "repair",
                RepairCode.SOFT,
                session_id,
                turn_id,
                {"repair_message": repair_msg}
            ))

            # Soft repair → then reentry
            logs.append(log_event(
                "reentry_observed",
                "reentry",
                ReentryCode.SUCCESS,
                session_id,
                turn_id
            ))

        # --- Step 3: Task execution ---
        response_text = "Here are available hotels: The University Arms, Hilton Cambridge City Centre."

        dispatcher.utter_message(text=response_text)

        logs.append(log_event(
            "outcome",
            "outcome",
            "OUTCOME_COMPLETE",
            session_id,
            turn_id,
            {"system_text": response_text}
        ))

        # You can persist logs to DB, file, or telemetry pipeline here
        print("--- PLD EVENTS ---")
        for entry in logs:
            print(entry)

        return []
```

---

## 6. Governance Checklist

| Rule                                            | Required? | Notes                        |
| ----------------------------------------------- | --------- | ---------------------------- |
| Every Rasa turn produces at least one PLD event | ✔         | Enables dashboards           |
| Repair must occur before reentry                | ✔         | Core PLD sequencing          |
| One outcome per session                         | ✔         | Required for FR/MRBF metrics |
| Latency recommended                             | Optional  | Attach via Rasa metadata     |

---

## 7. When to Extend

| Situation           | Extension                       |
| ------------------- | ------------------------------- |
| Tool orchestration  | Add `tool_event` logging schema |
| Memory-aware agents | Add slot confidence drift rules |
| Regulated apps      | Add OpenTelemetry trace IDs     |

---

## Summary

This file provides a **production-ready Rasa integration pattern** for PLD:

> Detect drift → trigger repair → verify reentry → log outcome → measure system stability.

It enables:
- Consistent data for dashboards
- Runtime evaluation
- Model + policy benchmarking
- CI/CD behavior regression testing
