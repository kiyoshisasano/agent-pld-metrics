# Tool Response Rules (Reactive LLM Layer)

> **Scope:** These rules describe how the LLM should respond **after a tool has already been executed by the runtime** and the tool result has been passed into the prompt.
> These rules do **not** determine when tools are invoked, which tool is selected, or whether a retry occurs.
>
> **Status:** Draft — reactive only.

---

## 1. Purpose

Tool response rules ensure that tool outputs are conveyed clearly, safely, and consistently to the user without introducing inference, scope expansion, or unintended assumptions.

These rules exist to:

* Present tool results in a readable format
* Confirm understanding before continuing
* Avoid misinterpretation or hallucinated explanation of the tool's output
* Maintain alignment with the user's goal

These guidelines only apply **after** the runtime has completed tool execution and delivered the results.

---

## 2. Applicable Runtime Signals (Tool Result Family)

These patterns activate only after tool execution and receipt of a tool result.

| Runtime SignalKind           | Canonical Code          | Meaning (LLM view)                                                              |
| ---------------------------- | ----------------------- | ------------------------------------------------------------------------------- |
| `TOOL_RESULT`                | `T1_result_available`   | Tool output is available and ready for interpretation                           |
| `USER_CONFIRMATION_REQUIRED` | `T2_needs_confirmation` | Runtime requires the user to approve or decide next action based on tool output |

> The Pattern Layer does **not** decide when these signals occur.

---

## 3. Shared Tool Response Principles

| Principle                 | Description                                                                                 |
| ------------------------- | ------------------------------------------------------------------------------------------- |
| No hidden inference       | Do **not** explain or reinterpret results unless context in the prompt explicitly allows it |
| Preserve tool authority   | The tool’s output is the source of truth and must not be altered                            |
| Minimal framing           | Add only enough structure for readability and alignment — no extra meaning                  |
| Confirm before continuing | Where appropriate, validate user intent before proceeding                                   |
| Maintain scope boundaries | Do not introduce new tasks, goals, formats, or assumptions                                  |

---

### Runtime Context & Fallback Handling

If tool output is provided **without supporting context** (goal, requested operation, or input reference), the LLM must:

* Not infer missing meaning
* Avoid speculative interpretation
* Respond with a clarification request instead, such as:

> "I have the tool results, but I need one detail to continue accurately: {focused clarification question}."

### Runtime / LLM Responsibility Boundary

* **Runtime owns:** tool selection, execution, retry policy, tone metadata, and structured result payload.
* **LLM owns:** presenting the result conversationally, without inferring missing context or altering meaning.

---

## 4. Response Modes

The LLM may use one of the following conversational framing modes, depending on the prompt and signal.

### 4.1 Readback Mode (Default)

> "Here is the tool result:
> {raw or formatted result}
> Should I continue, summarize, or apply the result?"

Used when the runtime has not specified the next action.

---

### 4.2 Structured Summary Mode

> "The tool returned the following key points:
>
> * {item}
> * {item}
> * {item}
>
> Let me know if you'd like a rewrite, deeper explanation, or next step."

Used when summarization is requested in the prompt.

---

### 4.3 Interpretation Mode (Conditional)

> "Based on your request, here's the tool output interpreted in context:
> {interpretation}
>
> Would you like to proceed with this direction?"

Only used when the runtime explicitly authorizes interpretation.

---

### 4.4 Confirmation-Required Mode

> "Before continuing, I need your confirmation:
>
> * Next step A: {description}
> * Next step B: {description}
> * Next step C: {description}
>
> Which option would you like to proceed with?"

The model should **not invent new options.**

---

## 5. Error-Aware Variants

These modes may apply when paired with `D4_tool_error` or repair signals.

Example neutral phrasing:

> "It looks like the tool result didn't match the expected format. Should I: revise inputs, retry, or ask for clarification?"

Error handling must remain reactive — the Runtime owns retry or failover logic.

---

## 6. Tone and Formatting Variants

* Neutral tone is the default.
* UX-optimized variants may use lighter acknowledgment if policy allows.

Example:

> "Thanks — here's what the tool returned."

Tone selection is runtime-controlled, **not inferred**.

---

## 7. Anti-Patterns

The LLM must avoid:

* Explaining tool results not understood from the prompt
* Suggesting actions the runtime did not authorize
* Rewriting or "fixing" tool output
* Inventing missing context, options, or interpretations
* Treating tool output as incorrect unless signaled

---

## 8. Boundary Reminder

* These rules apply **only after** tool output is provided.
* The Pattern Layer does **not** determine tool usage strategy, retry policies, or execution control.
* No schema, taxonomy, or lifecycle modification is allowed.

---

**End of tool_response_rules.md**

