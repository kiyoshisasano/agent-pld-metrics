

# Drift Event Logging — Quickstart Guide

This guide explains how **drift events** appear in the PLD runtime and how to
interpret them when reviewing exported PLD logs.

> This document is *educational only* and does **not** define new taxonomy,
validation rules, or runtime behavior.  
Canonical rules exist in the Level 1–3 specification set.


---

## 1. What Is a Drift Event?

A **drift event** indicates that the model response or reasoning path is moving
away from the intended instruction, behavior, or expected context.

Examples of drift conditions include:

| Drift Type | Example Signal |
|-----------|----------------|
| Instruction drift | The response does not follow the user request. |
| Repetition drift | The model repeats previous responses. |
| Tooling drift | Tool call failed or produced irrelevant output. |

A drift event is always logged using:

- `event_type = drift_detected`
- `pld.phase = "drift"`
- `pld.code` indicating a subtype (mapped in runtime bridges)

Example (from the demo dataset):

```json
{
  "event_type": "drift_detected",
  "pld": {
    "phase": "drift",
    "code": "D1_instruction",
    "confidence": 0.8
  },
  "payload": {
    "note": "User request underspecified; needs clarification."
  }
}
```

This line means:
> "The model detected that it cannot execute the request correctly."

---

## 2. What Happens After Drift?

A drift event does not end the session.  
It typically triggers a **repair sequence**.

Most commonly:

```kotlin
drift_detected  →  repair_triggered  →  (reentry_observed)  →  continue
```

The `reentry_observed` step may be explicit or implicit depending on context.  
Both are valid in PLD logging.

Example snippet:

```json
{"event_type": "drift_detected", "pld": {"phase": "drift"}}
{"event_type": "repair_triggered", "pld": {"phase": "repair"}}
{"event_type": "continue_allowed", "pld": {"phase": "continue"}}
```

This indicates the runtime took corrective action and returned to normal flow.

---

## 3. Measuring Drift

When analyzing exported PLD event logs, developers often track:

| Metric              | Purpose                                                |
| ------------------- | ------------------------------------------------------ |
| Drift rate          | How often drift is detected across sessions.           |
| Repair depth        | Number of repair attempts required before recovery.    |
| Recovery success    | Whether drift resolves without escalation or failover. |
| Latency interaction | Whether drift correlates with higher latency.          |

The accompanying script
`verify_metrics_local.py`
computes a minimal set of derived drift metrics from the dataset.

---

## 4. Example Scenario (from the demo dataset)

```arduino
turn 2 → drift_detected (D1_instruction)
turn 3 → repair_triggered (R1_clarify)
turn 4 → continue_allowed (successful output)
turn 5 → latency_spike (observability-only, not drift)
turn 6 → session_closed
```

Interpretation:

- The model noticed ambiguity in the request.
- Performed a clarification repair.
- Successfully resumed normal operation.

This pattern reflects a **healthy recovery loop**.

---

## 5. When Drift Persists

If repeated drift and repair attempts fail to return the system to stability,
the runtime may escalate to failover or end the session.

Example pattern (included in dataset):
```nginx
drift_detected → repair xN → session closed
```

Persistent drift is useful for:

- Model tuning and quality evaluation
- Prompt or tool reliability analysis
- Failure mode mapping

---

## 6. Summary

- Drift logs are **signals of deviation**, not failures.
- Repair and recovery sequences help diagnose **model resilience**.
- The dataset demonstrates both **successful recovery** and **persistent drift cases**.
- Metrics derived from drift events help teams understand **quality, stability, and
runtime behavior under ambiguity**.
