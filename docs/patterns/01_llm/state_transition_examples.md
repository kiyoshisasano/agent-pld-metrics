<!--
component_id: llm_patterns_state_transitions
kind: doc
area: quickstart_patterns
status: draft
authority_level: 3
version: 2.0.0
purpose: Illustrative examples defining expected lifecycle transitions between drift, repair, reentry, and normal execution.
-->

# State Transition Examples (LLM Reactive Layer)

> **Purpose:** This file provides high-level conversational examples of how responses may shift across lifecycle phases once a Runtime Signal has already been emitted. It does **not** determine when transitions occur — those decisions belong to the Level 5 Runtime.

---

## 1. Overview

These examples illustrate how an LLM may **react** to runtime signals as the system progresses through the PLD lifecycle:

```
Drift → Repair → Reentry → Continue → Outcome
```

Transitions shown here are conceptual communication paths — not enforcement rules.

---

## 2. Transition: Drift → Repair

**Trigger:** Runtime emits a drift-related signal (example: `INSTRUCTION_DRIFT`, `CONTEXT_DRIFT`).

| Aspect           | Example Behavior                                                                                                      |
| ---------------- | --------------------------------------------------------------------------------------------------------------------- |
| Goal             | Acknowledge misalignment and move toward clarification or adjustment                                                  |
| Tone             | Neutral, factual, non-defensive                                                                                       |
| Example Response | "It looks like my previous response may not have aligned with your request. To help resolve this, could you clarify…" |

**Notes:** No apology requirement. No assumption on cause. Avoid prescriptive action beyond clarification.

---

## 3. Transition: Repair → Reentry

**Trigger:** Runtime reaches confidence that alignment has been restored.

| Aspect           | Example Behavior                                                                                                                      |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Goal             | Confirm shared understanding and re-establish task direction                                                                          |
| Tone             | Concise and stabilizing                                                                                                               |
| Example Response | "Thanks — based on your clarification, here's the updated approach I'm following… Does this match what you expect before I continue?" |

**Notes:** Encourage confirmation when meaningful, but avoid loops.

---

## 4. Transition: Reentry → Continue

**Trigger:** System judges the session stable and normal task execution may resume.

| Aspect           | Example Behavior                                                     |
| ---------------- | -------------------------------------------------------------------- |
| Goal             | Proceed with the task without signaling remediation                  |
| Tone             | Normal operational tone                                              |
| Example Response | "Great — continuing with the requested task. Here is the next step…" |

**Notes:** Avoid referencing prior drift or repair unless context demands it.

---

## 5. Transition: Continue → Outcome

**Trigger:** System determines completion or closure behavior (example: `SESSION_CLOSED`).

| Aspect           | Example Behavior                                                                                   |
| ---------------- | -------------------------------------------------------------------------------------------------- |
| Goal             | Provide final result, summary, or closure depending on task type                                   |
| Tone             | Stable, explicit, non-ambiguous                                                                    |
| Example Response | "This completes the requested work. If you'd like to continue or explore variations, let me know." |

---

## 6. Observability-Only Signals (Non-Lifecycle)

Some signals (example: `latency_spike`, `pause_detected`, `INFO_generic`) do not change lifecycle phase.

In these cases, no structural transition occurs.
The response pattern may instead focus on pacing, user reassurance, or silence depending on context.

| Signal           | Expected Behavior                                                |
| ---------------- | ---------------------------------------------------------------- |
| `latency_spike`  | Optional acknowledgment of delay if user-facing                  |
| `pause_detected` | Optional check-in if user-facing                                 |
| `info`           | Purely internal trace; usually no conversational output required |

---

## 7. Important Boundaries

* Transitions shown here are **illustrative**, not enforceable
* Runtime governs:

  * Transition logic
  * Signal emission
  * Validation
* LLM patterns govern:

  * **How to phrase a response once a transition has been externally triggered**

---

**End of state_transition_examples.md**
