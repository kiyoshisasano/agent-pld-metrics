<!--
component_id: llm_patterns_repair_templates
kind: doc
area: quickstart_patterns
status: draft
authority_level: 3
version: 2.0.0
purpose: Structured repair response templates for R1–R5 repair signals, defining reactive conversational alignment behavior.
-->

# Repair Templates (Reactive LLM Layer)

> **Scope:** These templates describe conversational repair patterns **after a Repair-related Runtime Signal has been emitted.** They do not decide when repair is needed or which repair strategy to use.
> **Status:** Draft — reactive use only.

---

## 1. Purpose and Position

Repair templates help the LLM **restore alignment** once the runtime has decided that a repair action is required.

They are used to:

* Clarify missing or ambiguous information
* Correct prior outputs without expanding scope
* Re-establish goals, constraints, and next steps

They operate **on top of**:

* Drift response patterns (initial recognition and acknowledgment)
* Runtime decisions about repair type and timing

They **do not**:

* Detect drift or decide that repair is needed
* Choose which repair category (R1–R5) to apply
* Modify schema, phases, taxonomy, or runtime rules

---

## 2. Applicable Runtime Signals (Repair Family)

These templates apply when the runtime has emitted one of the following repair-related signals and made it available to the LLM:

| Runtime SignalKind           | Canonical Code             | High-level Meaning (LLM view)                                         |
| ---------------------------- | -------------------------- | --------------------------------------------------------------------- |
| `CLARIFICATION`              | `R1_clarify`               | More information is needed to reduce ambiguity                        |
| `SOFT_REPAIR`                | `R2_soft_repair`           | A small correction is needed; most of the prior answer remains usable |
| `REWRITE`                    | `R3_rewrite`               | The previous answer should be replaced with a new version             |
| `REQUEST_USER_CLARIFICATION` | `R4_request_clarification` | The user must actively choose or specify how to proceed               |
| `HARD_RESET`                 | `R5_hard_reset`            | The conversation or plan needs a major reset and restart              |

> **Runtime Ownership:** Defining, emitting, or extending these signals is solely the responsibility of the runtime implementation. The Pattern Layer is reactive: it assumes a signal is already present and does not invent new signals or codes.

---

## 3. Shared Repair Principles

Repair templates follow these principles:

| Principle             | Description                                                                                                |
| --------------------- | ---------------------------------------------------------------------------------------------------------- |
| Alignment-first       | Focus on re-aligning with the user’s stated goals and constraints before adding new content                |
| Minimal change        | Prefer the smallest effective correction; avoid unnecessary rewriting or expansion                         |
| History anchoring     | Use existing context to avoid re-asking everything; only revisit what is necessary                         |
| Safe choices          | When offering options, prefer simple, well-understood categories (e.g., summary / detailed / step-by-step) |
| No semantic expansion | Do not introduce new tasks, commitments, or assumptions during repair                                      |

These principles are intended to **reduce secondary drift** during the repair process.

---

### Runtime Context & Fallback Handling

If required context (goal, summary, constraints, or tool metadata) is **not present in the prompt**, the LLM must **not reconstruct or infer it**. Instead, it should fall back to a clarification-style repair response such as:

> "Before continuing, I need one clarification to ensure accuracy: {single focused question}."

### Runtime / LLM Responsibility Boundary

* **Runtime owns:** signal emission, severity classification, available options, tone policy, and structured context injection.
* **LLM owns:** applying the conversational pattern using provided context and avoiding inference or context reconstruction.

---

## 4. Base Repair Flow Template

The following structure is a generic repair flow. Individual repair types (R1–R5) specialize this pattern.

```text
1. State what is being repaired (briefly)
2. Reconfirm the user’s goal and key constraints (only what is necessary)
3. Propose a correction or updated plan
4. Offer a simple next step (confirm / choose / continue)
```

Example (neutral tone):

> "Let’s adjust the previous answer to better match your goal. I understand that your objective is: {restated goal}. Based on that, here is an updated version: {corrected content}. If this direction looks correct, I can continue or refine the details next."

This structure is a **conversational template**, not a schema. The runtime decides when and how to inject it.

---

## 5. Templates by Repair Type (R1–R5)

Each subsection below applies **after** the corresponding runtime signal has been emitted.

### 5.1 R1_clarify — Clarification Template

**When:** The runtime indicates that more information is needed to resolve ambiguity.

**Goal:** Ask focused questions that reduce uncertainty while reusing known context.

**Template (neutral):**

> "To make sure I proceed correctly, I need a bit more detail. I understand that your current goal is: {restated goal}. Could you clarify one point: {specific question}? After that, I can adjust the answer or plan accordingly."

**Notes:**

* Prefer 1–2 targeted questions over broad, open-ended inquiries.
* Assume previous conversation turns are available in the prompt; avoid asking the user to repeat everything.

---

### 5.2 R2_soft_repair — Soft Repair Template

**When:** The existing answer is mostly correct, but one or two parts need adjustment.

**Goal:** Correct the relevant portion while preserving useful content.

**Template (neutral):**

> "I’ll adjust part of the earlier answer to better match your request. The main points still hold, but I will update these specific parts: {brief list of corrections}. Here is the revised version with those changes applied: {updated segment}."

**Notes:**

* Keep the correction scope narrow.
* Highlight only what changed, rather than rewriting everything.

---

### 5.3 R3_rewrite — Rewrite Template

**When:** The previous answer should be replaced rather than patched.

**Goal:** Provide a new answer that respects the clarified goal and constraints.

**Template (neutral):**

> "I will provide a new version of the answer that better fits your goal. Based on our current understanding that you want: {restated goal and key constraints}, here is a rewritten answer: {new answer}. If this matches what you expect, I can expand or refine any part you choose."

**Notes:**

* Do not rely on the earlier mistaken structure; build the answer from the current alignment.
* Avoid introducing new topics that were not requested.

---

### 5.4 R4_request_user_clarification — Explicit User Choice

**When:** The runtime requires the user to explicitly choose how to continue.

**Goal:** Present safe, understandable options instead of open-ended branching.

**Template (options-based):**

> "To move forward, I need your choice on how to proceed. Based on the current situation, here are a few safe options:
>
> 1. Proceed with a concise summary
> 2. Provide a more detailed explanation
> 3. Walk through the steps one by one
>
> Please tell me which option (1, 2, or 3) you prefer, or describe an alternative if these don’t fit."

**Notes:**

* Options should be drawn from stable, generic categories (summary / detailed / step-by-step), not invented ad-hoc.
* Runtime MAY further constrain or customize options via prompt context; the Pattern Layer does not decide which options are allowed.

---

### 5.5 R5_hard_reset — Hard Reset Template

**When:** The runtime determines that the current path should be reset (for example, after repeated drift or severe misalignment).

**Goal:** Close the current line of reasoning and clearly restart from a stable baseline.

**Expected Prompt Context (runtime responsibility):**

* A short summary of the prior interaction or problem state
* The user’s current goal as understood by the system
* Any constraints that must be preserved (e.g., safety, policy, format)

**Template (neutral):

> "To avoid compounding earlier issues, I will restart from a clean summary. Here is my current understanding of your goal: {restated goal}. Key constraints are: {bullet list of constraints}. Starting from this baseline, I will now provide a fresh approach: {new plan or answer}. If this baseline is incorrect, please tell me what to change before we continue."

**Notes:**

* Make the reset explicit to the user, but keep the tone calm and task-focused.
* Use the runtime-provided summary instead of reconstructing history from scratch.

---

## 6. UX Tone Variants (Neutral and UX-Optimized)

The templates above use a neutral tone by default. In some deployments, a more UX-optimized tone (including light apologies or appreciation) may be desired.

* The Pattern Layer may provide **alternative phrasing variants** (e.g., with "sorry" or "thank you") as examples.
* **Choice of variant is owned by the runtime / application policy.** The Pattern Layer does not decide when an apology or stronger UX tone is required.

Example UX-optimized variant (for clarification):

> "Thanks for your patience—to make sure I get this right, I need a bit more detail. I understand that your current goal is: {restated goal}. Could you clarify one point: {specific question}?"

---

## 7. Options and Secondary Drift Risk

When offering options (e.g., 1/2/3), implementations should consider:

* Prefer fixed, stable categories such as:

  * "summary"
  * "detailed explanation"
  * "step-by-step walkthrough"
* Avoid letting the model invent arbitrary options that might themselves drift away from the user’s intent.

The Pattern Layer provides **structure and examples**, but:

* The runtime may inject concrete option labels into the prompt.
* The LLM should avoid extrapolating options beyond what is presented.

---

## 8. Anti-Patterns

Repair templates should avoid:

* Expanding the task scope during repair (adding new goals or promises)
* Repeatedly asking the same clarification question without change
* Overwriting user-provided constraints without explicit confirmation
* Introducing new policy or safety assumptions not present in the runtime

These behaviors can create new drift or reduce user trust.

---

## 9. Boundary Reminder

* Repair templates are **reactive conversational guides**, not control logic.
* The runtime governs drift detection, signal emission, repair strategy selection, and lifecycle management.
* The Pattern Layer does not change schema fields, phases, taxonomy codes, or metrics.

Once a repair signal is emitted and passed into the prompt, these templates describe **how the LLM can phrase its response**, while respecting the constraints defined by lower layers.

---

**End of repair_templates.md**
