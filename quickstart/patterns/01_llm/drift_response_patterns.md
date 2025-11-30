# Drift Response Patterns (Reactive LLM Layer)

> **Scope:** These patterns provide conversational guidance for responding **after a Drift-related Runtime Signal has been emitted.** They do not determine drift detection or trigger criteria.
> **Status:** Draft — reactive use only.

---

## 1. Purpose

Drift occurs when the model's previous response deviates from the expected task, intent, or domain context.
Once the **Runtime has emitted a Drift signal**, the LLM should respond in a way that:

* Helps restore alignment
* Reduces uncertainty
* Maintains a neutral and stabilizing tone
* Avoids assumptions about the cause of drift

This file provides reusable phrasing frameworks, not logic or enforcement rules.

---

## 2. Applicable Runtime Signals

These patterns apply only when Runtime has emitted one of the following:

| Runtime Signal      | Mapping Code       | Meaning (high-level)                                             |
| ------------------- | ------------------ | ---------------------------------------------------------------- |
| `INSTRUCTION_DRIFT` | `D1_instruction`   | Response diverged from explicit instructions                     |
| `CONTEXT_DRIFT`     | `D2_context`       | Response does not reflect conversation context                   |
| `REPEATED_PLAN`     | `D3_repeated_plan` | The model is looping or repeating a step rather than progressing |
| `TOOL_ERROR`        | `D4_tool_error`    | Tool invocation response was misaligned or misinterpreted        |

*Patterns below do not replace Runtime logic or alter mapping behavior.*

---

## 3. Shared Response Principles

| Principle           | Description                                                                |
| ------------------- | -------------------------------------------------------------------------- |
| Neutrality          | Avoid blame language ("my mistake") unless explicitly designed for UX tone |
| Brevity             | Keep responses concise to avoid compounding drift                          |
| Clarification-first | Prioritize request clarification before advancing content                  |
| No hidden inference | Avoid guessing user intent unless explicitly requested                     |
| Stability           | Maintain consistent formatting and structure                               |

### Runtime Context & Fallback Handling

If required context (such as user goal, constraints, or prior-turn reference) is missing from the prompt, the model must not guess or reconstruct it. Instead, the model should fall back to a minimal clarification response such as:

> "Before continuing, I need a brief clarification to ensure accuracy: {single focused question}."

### Runtime / LLM Responsibility Boundary

- **Runtime owns:** drift detection, signal emission, severity classification, and any structured context injection.
- **LLM owns:** applying the drift response pattern using only the context explicitly provided, without inference or hidden reconstruction.

---

## 4. Base Drift Response Template

```
Acknowledgment (brief)
↓
Clarifying question or reorientation
↓
Optional next-step framing
```

Example phrasing:

> "It seems my last response may not have aligned with your request. To proceed accurately, could you confirm which of the following you intended: A) … B) … or C)…?"

---

## 5. Pattern Variants by Drift Type

### 5.1 Instruction Drift Pattern

**When:** Response ignored part of a request or reframed the task incorrectly.

**Response Example:**

> "It appears my previous response missed part of your instruction. Before I continue, could you clarify which format you'd prefer: summary, full explanation, or step-by-step output?"

---

### 5.2 Context Drift Pattern

**When:** Response disconnects from the prior interaction or loses conversation thread.

**Response Example:**

> "To realign with the context, I want to confirm the current focus. Are we continuing from the last topic or switching to a new direction?"

---

### 5.3 Repeated Plan Pattern

**When:** The response repeats content already given or loops over previous steps.

**Response Example:**

> "It looks like I repeated earlier content. To continue effectively, which next step should I prioritize?"

---

### 5.4 Tool Error Pattern

**When:** The mismatch involves tool invocation, tool output interpretation, or tool execution context.

**Response Example:**

> "There may have been a mismatch between the tool result and your expected output. Would you like me to retry, adjust parameters, or provide an interpreted summary instead?"

---

## 6. Optional Soft Recovery Add‑Ons

These are **not required**, but may improve user clarity:

* Offer structured options (A / B / C)
* Restate task parameters in bullet form
* Briefly repeat user goal before action
* Confirm whether the user expects automation or manual reasoning

Example:

> "To confirm, your goal is: *{restated objective}*. Should I proceed with Option 1, Option 2, or revise the approach first?"

---

## 7. Anti‑Patterns

🚫 The following should be avoided as they may reinforce drift:

* Excessive apology loops
* Introducing new task scopes unprompted
* Speculating on intent without user confirmation
* Continuing execution without checking alignment after drift

---

## 8. Boundary Reminder

* Drift patterns are **reactive templates only**
* Runtime owns detection, emission, and lifecycle management
* The LLM should only apply these patterns **after signal receipt**, not based on self-judgment

---

**End of drift_response_patterns.md**
