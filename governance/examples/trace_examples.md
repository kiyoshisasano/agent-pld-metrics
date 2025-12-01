# PLD Trace Examples for Shared Review

This file provides **small, focused examples** of traces to use when aligning on:

- What we call “drift”  
- What counts as a “repair”  
- What “reentry” looks like in practice  
- How we label outcomes  

It is not a full dataset.  
It is a **starter kit** for field collaboration.

---

## 1. Recommended Trace Format

For joint work, we recommend a simple JSONL or Markdown structure:

- Each **session** includes:
  - `session_id`
  - `turns` (list)

- Each **turn** contains:
  - `turn_index`
  - `user_message`
  - `system_reply`
  - `pld_event`:
    - `drift.present`
    - `drift.type`
    - `repair.present`
    - `repair.mode`
    - `reentry.present`
    - `reentry.success`
    - `outcome.status` (when applicable)

This format aligns with the PLD logging model used in `quickstart/metrics/`.

---

## 2. Example 1 — Intent Drift with Soft Repair

### 2.1 Conversation Snippet

```text
User   : I need to book a flight to Berlin next Tuesday in economy.
System : There are several great hotels in Berlin. Do you prefer Mitte or Kreuzberg?
User   : I'm asking about a flight, not a hotel.
System : Right, you’re asking for a flight. Let me switch to flights for Berlin next Tuesday in economy.
System : To confirm: Berlin next Tuesday, economy class, from your current city. Is that correct?
User   : Yes, that’s right.
System : Great, I’ve found three flight options...
```

### 2.2 Annotated Turns (Simplified JSON)

```json
{
  "session_id": "example_intent_drift_001",
  "turns": [
    {
      "turn_index": 0,
      "user_message": "I need to book a flight to Berlin next Tuesday in economy.",
      "system_reply": "There are several great hotels in Berlin. Do you prefer Mitte or Kreuzberg?",
      "pld_event": {
        "drift": {
          "present": true,
          "type": "D3_intent_drift",
          "reason": "User asked for a flight, system responded with hotels."
        },
        "repair": { "present": false, "mode": null, "code": null },
        "reentry": { "present": false, "success": null },
        "outcome": { "status": "ongoing" }
      }
    },
    {
      "turn_index": 1,
      "user_message": "I'm asking about a flight, not a hotel.",
      "system_reply": "Right, you’re asking for a flight. Let me switch to flights for Berlin next Tuesday in economy.",
      "pld_event": {
        "drift": {
          "present": true,
          "type": "D3_intent_drift",
          "reason": "Drift acknowledged by user; system switches context."
        },
        "repair": { "present": true, "mode": "soft", "code": "R1_clarify_and_correct" },
        "reentry": { "present": false, "success": null },
        "outcome": { "status": "ongoing" }
      }
    },
    {
      "turn_index": 2,
      "user_message": "",
      "system_reply": "To confirm: Berlin next Tuesday, economy class, from your current city. Is that correct?",
      "pld_event": {
        "drift": { "present": false, "type": null, "reason": null },
        "repair": { "present": true, "mode": "soft", "code": "R2_reentry_confirmation" },
        "reentry": { "present": true, "success": null },
        "outcome": { "status": "ongoing" }
      }
    },
    {
      "turn_index": 3,
      "user_message": "Yes, that’s right.",
      "system_reply": "Great, I’ve found three flight options...",
      "pld_event": {
        "drift": { "present": false, "type": null, "reason": null },
        "repair": { "present": false, "mode": null, "code": null },
        "reentry": { "present": true, "success": true },
        "outcome": { "status": "complete" }
      }
    }
  ]
}
```

Use this example to align on:

- When intent drift is labeled  
- When soft repair is counted as present  
- When reentry success is marked  

---

## 3. Example 2 — Hard Repair and Failure

This example should represent a session where:

- The system cannot safely continue  
- A hard repair is applied (reset/escalation/fallback)  
- The outcome is **failed or abandoned**

```json
{
  "session_id": "example_hard_repair_001",
  "turns": [
    {
      "turn_index": 0,
      "user_message": "...",
      "system_reply": "...",
      "pld_event": {
        "drift": {
          "present": true,
          "type": "D4_safety_or_boundary",
          "reason": "..."
        },
        "repair": {
          "present": true,
          "mode": "hard",
          "code": "R9_escalate_or_abort"
        },
        "reentry": { "present": true, "success": true },
        "outcome": { "status": "failed" }
      }
    }
  ]
}
```

This example helps both teams synchronize on:

- When a hard repair is appropriate  
- How a failure outcome should be labeled and reviewed  

---

## 4. How to Use These Examples in Collaboration

When beginning a PoC with a partner:

1. Exchange:  
   - **2–3 soft repair examples** (similar to Example 1)  
   - **1–2 hard repair failure cases** (similar to Example 2)

2. Review together:

- Are drift / repair / reentry labeled consistently?
- Does the outcome classification reflect real-world expectations?

3. Decide:

- Which behaviors should be **encouraged**?
- Which require **intervention**, **guardrails**, or **runtime enforcement**?

---

Shared examples are the fastest way to ensure that:

> **“drift”, “repair”, and “reentry” mean the same thing to everyone involved.**
