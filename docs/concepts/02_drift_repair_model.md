# Drift–Repair Lifecycle Model

## 1. Purpose of This Document

This document defines the **conceptual Drift–Repair lifecycle model** used throughout PLD. It is a non-normative companion to the authoritative definitions in:

* **Level 1 Schema** — event envelope and required fields
* **Level 2 Semantic Matrix** — event meanings and phase structure
* **Level 3 Runtime Standards** — taxonomy codes, operational phases, validation expectations

Its purpose is to provide a clear mental model of how multi-turn agents transition between phases, how drift is detected, how repair is performed, and how continuation and outcomes are determined.

This document MUST NOT override canonical definitions in Levels 1–3.

---

# 2. High-Level Lifecycle Overview

A PLD session progresses through a predictable set of phases:

```
Drift → Repair → Reentry → Continue → Outcome
```

Each phase is represented through canonical event types and validated through Level 2 semantics. The Drift–Repair model describes **why** those transitions occur and **how** runtime implementations should think about them.

---

# 3. Drift Phase

The Drift phase begins when the system detects that the agent has deviated from expectations. Drift may originate from:

* user instruction misunderstanding,
* incorrect tool outputs,
* missing or malformed fields,
* semantic divergence from task intent,
* policy or safety boundary violations.

### 3.1 Drift Signals and Events

Drift is represented using D*-family taxonomy codes and MUST use a Drift-phase event type such as:

* `drift_detected`
* `drift_escalated`

These events articulate **what failed** and provide the context required for downstream repair.

### 3.2 Drift Classification (Conceptual Categories)

Although code-level definitions live in Level 3, conceptually Drift generally falls into five categories:

* **Information Drift** — factual inconsistency
* **Context Drift** — loss or misuse of established constraints
* **Intent Drift** — deviation from the user’s goal
* **Procedural Drift** — workflow or sequencing issues
* **Pacing / Latency Drift** — timing or pacing failures

**Only one primary drift type should be assigned per segment**, ensuring clear diagnosis and predictable repair behavior.

A drift MAY be absent, represented conceptually as `none`.

### 3.3 Goals of the Drift Phase

The Drift phase is not about fixing the error; it is about:

* detecting the deviation,
* classifying its severity,
* capturing metadata for diagnosis,
* deciding which repair strategy to attempt.

The Drift phase ends when the system decides that repair must begin.

---

# 4. Repair Phase

The Repair phase attempts to correct the deviation identified in the Drift phase. It is represented using R*-family taxonomy codes and MUST use a Repair-phase event type such as:

* `repair_triggered`
* `repair_escalated`

Repair does not automatically imply success. It is a structured attempt to resolve drift.

### 4.1 Repair Strategies

PLD defines three practical repair strategies:

* **Static Repair** — deterministic transformations
* **Guided Repair** — LLM-assisted self-correction
* **Human-in-the-Loop (HITL)** — manual governance gate

See `03_repair_strategies.md` for full details.

### 4.2 Conceptual Repair Categories

Independent of strategy, repairs can be understood across four conceptual categories:

* **Local Repair** — small, localized corrections
* **Structural Repair** — restoring internal workflow or state
* **UX Repair** — stabilizing pacing or feedback
* **Hard Repair (Reset)** — discarding context and restarting

These conceptual categories do not override Level 3 taxonomy rules but help frame the nature of corrective actions.

A repair MAY be absent, represented conceptually as `none`.

### 4.3 Entering Repair

The system transitions from Drift → Repair when one of the following holds:

* A deviation requires correction before safe continuation
* The drift severity demands immediate intervention
* Runtime policy mandates correction before progressing

Repair may escalate between strategies (e.g., Static → Guided → Human) using `repair_escalated`.

### 4.4 Repair Budget and Retry Limits

To prevent infinite oscillation between Drift and Repair:

* Each repair strategy SHOULD define a **strategy-level Repair Budget**
* If a strategy’s budget is exhausted and a higher-order strategy exists, the system SHOULD emit `repair_escalated`
* If no higher-order strategy exists, the runtime MUST transition to:

  * `failover_triggered`, or
  * `session_closed`

A system MAY define a **global Repair Budget**. When exhausted, the session MUST terminate safely and MUST NOT return to Drift.

---

# 5. Reentry Phase

After Repair, the system may enter the Reentry phase. Reentry is **state-integrity validation**—a lightweight checkpoint confirming whether the system can safely resume the intended task.

Reentry uses `reentry_observed` and aligns with Level 2 semantics.

### 5.1 Purpose of Reentry

Reentry ensures:

* the repair succeeded,
* no new drift is latent in the agent state,
* task constraints are still coherent,
* the next continuation step will not cause compounding errors.

Reentry is NOT a rollback mechanism. It is a validation gateway.

### 5.2 Reentry Classification (Conceptual Categories)

Reentry commonly falls into three conceptual categories:

* **Intent Reentry** — goal alignment is restored
* **Constraint Reentry** — parameters and constraints are coherent again
* **Workflow Reentry** — execution flow resumes normally

A reentry MAY be absent, represented conceptually as `none`.

### 5.3 Possible Outcomes of Reentry

From Reentry, the system may:

* proceed to Continue (`continue_allowed`),
* block continuation (`continue_blocked`),
* identify new drift (leading to a new Drift phase),
* close the session due to inconsistencies.

---

# 6. Continue Phase

The Continue phase determines whether execution proceeds, pauses, or is blocked. It is represented by C*-family taxonomy codes, using event types such as:

* `continue_allowed`
* `continue_blocked`

### 6.1 Safe Continuation

A continuation is safe when:

* repair was successful,
* state integrity has been validated,
* no policy or safety thresholds prevent continuation.

### 6.2 Blocked Continuation

Continuation may be intentionally blocked when:

* HITL approval is required,
* safety or compliance rules are triggered,
* additional runtime checks are pending.

Blocked continuation is explicitly represented through `continue_blocked`.

---

# 7. Outcome Phase

The Outcome phase represents final session states. It includes O*-family taxonomy codes and event types such as:

* `session_closed`
* `outcome_generated`

Outcome marks the end of a lifecycle. It may reflect:

* normal task completion,
* human-terminated sessions,
* failover-triggered termination,
* policy-driven shutdown.

---

# 8. Failover Path (Optional but Recommended)

The Failover path provides a safety mechanism when recovery is impossible or unsafe. It uses F*-family codes and event types like `failover_triggered`.

Failover MUST be used when:

* both strategy-level and global repair budgets are exhausted,
* the system cannot recover from severe drift,
* continuation would violate policy or safety constraints.

---

# 9. Summary

The Drift–Repair lifecycle model provides a predictable sequence:

```
Drift → Repair → Reentry → Continue → Outcome
```

Each phase has clear entry/exit conditions and aligns strictly with the Level 2 Semantic Matrix and Level 3 Runtime Standards.

This conceptual model underpins the practical repair strategies, runtime policies, and transition patterns described throughout the PLD documentation ecosystem.
