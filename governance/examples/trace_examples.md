<!--
component_id: governance_legacy
kind: doc
area: meta
status: stable
authority_level: 5
purpose: Legacy trace examples used for governance and semantic evaluation.
-->

# Business-Facing Summary (for Non-Technical Stakeholders)

This document provides a set of small, standardized PLD trace examples that help teams align on how to interpret system behavior. You do not need technical experience with schemas or runtimes to understand them. The examples are designed to show what Drift, Repair, Reentry, Continue, and Outcome look like in real conversations.

Use this document to:

* Quickly learn how PLD-compliant logs should look
* Align with partners on which Drift Code (D*) applies in a scenario
* Understand what a good Repair or Reentry response looks like
* Verify that sanitized logs still preserve required PLD metadata

These examples act as a shared “calibration kit” so that two different teams can evaluate behavior consistently—even if they cannot share raw data.

---

# PLD Trace Examples for Shared Review (v2-Aligned)

**Status:** Stable (Level 5 Governance Guidance)

These examples provide a shared calibration standard for:

* **L2 Semantics** — Correct lifecycle transitions
* **L3 Standards** — Canonical taxonomy usage
* **Safety** — Proper sanitization of payload content

All examples use the **PLD Runtime Event Envelope (schema v2.0)**.
This ensures that collaborators interpret *Drift*, *Repair*, *Reentry*, *Continue*, and *Failover* consistently.

---

# 1. Standard Sanitized JSONL Format (v2-Aligned)

Sanitized logs MUST:

* preserve **PLD metadata** (phase, code, event_type)
* mask **payload.text** only
* keep **runtime / metrics / pld** unmasked

### **Example Format**

```json
{
  "schema_version": "2.0",
  "event_id": "<UUID>",
  "timestamp": "2025-01-01T00:00:00Z",
  "session_id": "sess_001",
  "turn_sequence": 1,
  "source": "assistant",
  "event_type": "repair_triggered",
  "pld": {
    "phase": "repair",
    "code": "R1_clarify"
  },
  "payload": {
    "text": "Confirming flight to <MASKED_CITY>..."
  },
  "runtime": {
    "model": "model-v1"
  },
  "ux": {
    "user_visible_state_change": true
  }
}
```

**Mask only payload fields.**
Taxonomy, phases, metrics MUST remain intact.

---

# 2. Example 1 — Instruction Drift → Soft Repair → Reentry → Continue

## 2.1 Context

The user asks for a flight, the model responds about hotels.
This is an **instruction drift** (`D1_instruction`). The assistant performs a **soft repair** (`R1_clarify`).

## 2.2 Lifecycle Flow (v2)

```
User → Assistant
    drift_detected (D1_instruction)
→  repair_triggered (R1_clarify)
→  reentry_observed
→  continue_allowed
→  outcome (success)
```

## 2.3 Compliant PLD v2 JSONL Trace

```json
[
  {
    "schema_version": "2.0",
    "event_id": "<UUID0>",
    "timestamp": "2025-01-01T00:00:00Z",
    "session_id": "sess_001",
    "turn_sequence": 1,
    "source": "assistant",
    "event_type": "drift_detected",
    "pld": {
      "phase": "drift",
      "code": "D1_instruction"
    },
    "payload": {
      "text": "I found great hotels in <MASKED_CITY>."
    },
    "runtime": {},
    "ux": { "user_visible_state_change": true }
  },
  {
    "schema_version": "2.0",
    "event_id": "<UUID1>",
    "timestamp": "2025-01-01T00:00:01Z",
    "session_id": "sess_001",
    "turn_sequence": 2,
    "source": "assistant",
    "event_type": "repair_triggered",
    "pld": {
      "phase": "repair",
      "code": "R1_clarify"
    },
    "payload": {
      "text": "Apologies — confirming: Flight to <MASKED_CITY>, correct?"
    },
    "runtime": {},
    "ux": { "user_visible_state_change": true }
  },
  {
    "schema_version": "2.0",
    "event_id": "<UUID2>",
    "timestamp": "2025-01-01T00:00:02Z",
    "session_id": "sess_001",
    "turn_sequence": 3,
    "source": "user",
    "event_type": "reentry_observed",
    "pld": {
      "phase": "reentry",
      "code": "RE0_reentry"
    },
    "payload": {
      "text": "Yes."
    },
    "runtime": {},
    "ux": { "user_visible_state_change": false }
  }
]
```

---

# 3. Example 2 — Safety Drift → Hard Repair → Failover → Outcome

## 3.1 Context

The user attempts a disallowed action.
A **safety drift** is detected (`D5_safety`). The agent performs a **hard repair** (`R5_hard_reset`) and triggers failover.

## 3.2 Lifecycle Flow (v2)

```
drift_detected (D5_safety)
→ repair_triggered (R5_hard_reset)
→ failover_triggered
→ outcome (session_closed)
```

## 3.3 Compliant PLD v2 JSONL Trace

```json
[
  {
    "schema_version": "2.0",
    "event_id": "<UUID10>",
    "timestamp": "2025-01-01T01:00:00Z",
    "session_id": "sess_900",
    "turn_sequence": 1,
    "source": "user",
    "event_type": "drift_detected",
    "pld": {
      "phase": "drift",
      "code": "D5_safety"
    },
    "payload": {
      "text": "<MASKED_MALICIOUS_INPUT>"
    },
    "runtime": {},
    "ux": { "user_visible_state_change": true }
  },
  {
    "schema_version": "2.0",
    "event_id": "<UUID11>",
    "timestamp": "2025-01-01T01:00:01Z",
    "session_id": "sess_900",
    "turn_sequence": 2,
    "source": "assistant",
    "event_type": "repair_triggered",
    "pld": {
      "phase": "repair",
      "code": "R5_hard_reset"
    },
    "payload": {
      "text": "I cannot perform that action."
    },
    "runtime": {},
    "ux": { "user_visible_state_change": true }
  },
  {
    "schema_version": "2.0",
    "event_id": "<UUID12>",
    "timestamp": "2025-01-01T01:00:02Z",
    "session_id": "sess_900",
    "turn_sequence": 3,
    "source": "system",
    "event_type": "failover_triggered",
    "pld": {
      "phase": "failover",
      "code": "F1_failover"
    },
    "payload": {
      "text": "Session terminated due to policy violation."
    },
    "runtime": {},
    "ux": { "user_visible_state_change": true }
  }
]
```

---

# 4. Example 3 — Tool Misuse → Context Drift → Soft Repair → Reentry

## 4.1 Context (New)

A tool is repeatedly invoked with missing or invalid parameters.
This is a **context drift** (`D2_context`).

## 4.2 Lifecycle Flow

```
drift_detected (D2_context)
→ repair_triggered (R2_soft_repair)
→ reentry_observed
→ continue_allowed
```

## 4.3 Compliant PLD v2 JSONL

```json
[
  {
    "schema_version": "2.0",
    "event_id": "<UUID20>",
    "timestamp": "2025-01-01T02:00:00Z",
    "session_id": "sess_777",
    "turn_sequence": 1,
    "source": "assistant",
    "event_type": "drift_detected",
    "pld": {
      "phase": "drift",
      "code": "D2_context"
    },
    "payload": {
      "text": "Tool failed due to missing parameter <MASKED>."
    },
    "runtime": { "tool": "search_api" },
    "ux": { "user_visible_state_change": false }
  },
  {
    "schema_version": "2.0",
    "event_id": "<UUID21>",
    "timestamp": "2025-01-01T02:00:01Z",
    "session_id": "sess_777",
    "turn_sequence": 2,
    "source": "assistant",
    "event_type": "repair_triggered",
    "pld": {
      "phase": "repair",
      "code": "R2_soft_repair"
    },
    "payload": {
      "text": "Could you confirm the missing parameter?"
    },
    "runtime": {},
    "ux": { "user_visible_state_change": true }
  }
]
```

---

# 5. How to Use These Examples

During joint PoC onboarding:

* Copy these JSONL templates
* Replace **session_id**, **payload.text**, **runtime fields** with your values
* Confirm:

  * Drift codes use canonical Level 3 taxonomy
  * Repairs follow v2 lifecycle
  * Masking applies only to payload
  * Failover examples match your governance requirements

Shared trace examples ensure that **“Drift” means the same thing to all partners** and accelerate lifecycle alignment.
