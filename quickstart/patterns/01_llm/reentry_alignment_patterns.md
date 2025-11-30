# Reentry Alignment Patterns (Reactive LLM Layer)

> **Scope:** These patterns guide the LLM in returning to normal task execution **after a successful repair phase** and runtime confirmation.
> **Status:** Draft — reactive only.

---

## 1. Purpose

Reentry patterns ensure the conversation transitions smoothly from a repair state back into standard task progression.

They serve to:

* Confirm the repaired alignment
* Re-establish task momentum without expanding scope
* Signal to the user that normal execution has resumed

These patterns only apply **after the runtime emits a reentry-related signal**.

---

## 2. Applicable Runtime Signals (Reentry Family)

These patterns activate only in response to specific runtime signals (examples shown; semantics assume lower-layer ownership):

| Runtime SignalKind     | Canonical Code       | High-level meaning (LLM view)                                          |
| ---------------------- | -------------------- | ---------------------------------------------------------------------- |
| `REENTRY`              | `RE1_resume`         | Alignment is restored and normal execution may continue                |
| `REENTRY_CONFIRMATION` | `RE2_user_confirmed` | User has explicitly validated the correction and approved continuation |

> **Note:** The Pattern Layer does **not** determine when reentry occurs. The runtime decides and signals.

---

## 3. Shared Reentry Principles

| Principle                | Description                                                                |
| ------------------------ | -------------------------------------------------------------------------- |
| Resume without drift     | Resume the original task without introducing new scope or assumptions      |
| Maintain user confidence | Reinforce clarity and stability through concise acknowledgment             |
| Avoid repeating content  | Do not restate the full repair or task history unless explicitly requested |
| Maintain stability       | Tone and structure remain steady — avoid abrupt stylistic shifts           |

---

### Runtime Context & Fallback Handling

If the reentry signal arrives **without supporting context** (goal, constraints, or final confirmation), the LLM should:

* **Not infer or reconstruct history**
* **Fall back to a light clarification prompt**, e.g.:

> "Before continuing, I need one confirmation to ensure we are aligned: {focused confirmation question}."

### Runtime / LLM Responsibility Boundary

* **Runtime owns:** reentry signal emission, confirmation of alignment, tone policy, and delivery of necessary context.
* **LLM owns:** applying the reentry structure, without adding assumptions or reconstructing missing context.

---

## 4. Base Reentry Template

This minimal structure applies to both RE1 and RE2 variations:

```text
1. Optional brief acknowledgment of completion of repair
2. State alignment with the confirmed goal or constraints
3. Transition into standard execution of the task
```

Example (neutral tone):

> "Thanks — alignment confirmed. Based on your goal ({restated goal}), I'll continue from here. Let’s continue with the next step: {next step or answer}."

---

## 5. Pattern Variants by Reentry Type

### 5.1 RE1_resume — Runtime-triggered continuation

Used when the system determines alignment is restored.

Template:

> "Alignment is confirmed. Continuing based on the objective: {restated goal}. Next step: {task continuation}."

Notes:

* Avoid apologetic language unless tone requires it.
* Keep the acknowledgment brief.

---

### 5.2 RE2_user_confirmed — User-validated reentry

Used when reentry follows an explicit user confirmation.

Template:

> "Great — thanks for confirming. I'll continue based on your goal: {restated goal}. Next, I'll proceed with: {task continuation}."

Optional UX variant:

> "Appreciate the confirmation — continuing now."

---

## 6. Anti-Patterns

Avoid the following during reentry:

* Re-explaining the repair unless requested
* Resetting the topic or tone unless runtime instructs it
* Adding new steps beyond the confirmed task scope
* Introducing new assumptions or reframing user intent

---

## 7. Boundary Reminder

* Reentry patterns apply **only after** a reentry-related runtime signal.
* The Pattern Layer does not initiate reentry or determine alignment.
* No schema, taxonomy, or lifecycle modification is permitted.

---

**End of reentry_alignment_patterns.md**
