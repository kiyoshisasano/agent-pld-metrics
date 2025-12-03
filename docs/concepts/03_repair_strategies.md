# Repair Strategies in PLD Runtimes

## 1. Motivation and Scope

This document provides non-normative implementation guidance for the **Repair phase** within the PLD lifecycle. It clarifies how runtime developers can choose among three repair strategies—Static, Guided, and Human-in-the-Loop—while remaining fully compliant with Level 1 (schema), Level 2 (semantic matrix), and Level 3 (runtime standards).

The Repair phase corresponds to PLD events such as `repair_triggered` and `repair_escalated`, which MUST align with R*-family taxonomy codes and the `phase="repair"` requirement. This document does not modify or extend any canonical semantics.

## 2. Lifecycle Recap: From Drift to Repair

### 2.1 Drift Phase Recap

A session enters the Drift phase when a deviation is detected—examples include instruction misunderstanding, missing required fields, or external tool failures. These conditions are surfaced through PLD events such as:

* `drift_detected`
* `drift_escalated`

These events use D*-family taxonomy codes and always belong to `phase="drift"`.

### 2.2 Repair Phase Recap

Following drift detection, the runtime enters the Repair phase. PLD mandates that:

* `repair_triggered` and `repair_escalated` MUST use R*-family taxonomy codes.
* All R*-family codes MUST align with `phase="repair"`.

### 2.3 Allowed Transitions

After Repair, the runtime may transition into one of several phases depending on the repair result:

* **Reentry** → `reentry_observed` (state re-validation)
* **Continue** → `continue_allowed` or `continue_blocked`
* **Outcome** → `session_closed`
* **Failover** → `failover_triggered`

### 2.4 High-Level Diagram

```
Drift (D*) → Repair (R*) → [ Reentry | Continue | Outcome | Failover ]
```

## 3. Strategy Overview

The following table compares the three Repair strategies defined in this document.

| Strategy              | Engine                                  | Typical Flow                                            | Pros                               | Cons                                 |
| --------------------- | --------------------------------------- | ------------------------------------------------------- | ---------------------------------- | ------------------------------------ |
| **Static Repair**     | Deterministic rules (regex, type casts) | Drift → Repair → Fix → Continue/Reentry                 | Fast, predictable, no LLM          | Limited to structural fixes          |
| **Guided Repair**     | LLM-assisted correction                 | Drift → Repair → LLM self-correction → Continue/Reentry | Handles semantic drift, flexible   | Requires model invocation            |
| **Human-in-the-Loop** | Human approval gate                     | Drift → Repair → Continue Blocked → Human decision      | Suitable for safety-critical cases | Slow, requires operator availability |

## 4. Static Repair Strategy

### 4.1 Concept

Static Repair applies deterministic transformations to correct structural or syntactic errors. Examples include ensuring required schema fields exist, patching malformed JSON, normalizing types, or sanitizing tool outputs. No LLM is used.

### 4.2 Drift → Repair Mapping

Typical event sequence:

1. `drift_detected` (e.g., `D2_context`)
2. `repair_triggered` (e.g., `R2_soft_repair`)
3. Repair logic applies a rule-based fix
4. If successful:

   * `continue_allowed` or `reentry_observed`
5. If unsuccessful:

   * Another drift → loop, or
   * `repair_escalated`, or
   * `failover_triggered`

Static Repair **MUST NOT** override any canonical PLD fields after event construction. All structural changes occur before building the PLD event.

### 4.3 Recommended Use Cases

* Tool or API responses with predictable structure
* ETL pipelines and data transformation
* Simple schema or type mismatches
* Environments requiring deterministic behavior

## 4.4 Repair Budget and Retry Limits

To prevent infinite drift/repair oscillation, every repair strategy SHOULD implement a **strategy-level Repair Budget** (maximum retry count).

### 4.4.1 Strategy-Level Repair Budget

* Each repair strategy (Static, Guided, Human) MAY define its own retry budget.
* When a strategy-level budget is exhausted:

  * If a **higher-order strategy** exists (e.g., Static → Guided, Guided → Human), the runtime SHOULD emit `repair_escalated` to transition into the next strategy.
  * If no higher-order strategy exists, the runtime MUST transition to `failover_triggered` or `session_closed`.

### 4.4.2 Global Repair Budget (Optional)

* A runtime MAY additionally define a **global Repair Budget** covering the entire Drift→Repair cycle.
* When this global budget is exhausted:

  * The runtime MUST transition to `failover_triggered` or `session_closed`.
  * Returning to Drift (`drift_detected` / `drift_escalated`) is NOT allowed.

### 4.4.3 Budget Exhaustion and Phase Safety

* Exhausting a budget MUST NOT result in re-entering the Drift phase.
* `repair_escalated` is the only valid path to another repair strategy.
* These rules ensure controlled termination without infinite oscillation.

## 5. Guided Repair Strategy (LLM-Assisted)

### 5.1 Concept

Guided Repair uses the model as a reasoning component. Upon detecting drift, the runtime routes error context and the problematic content back to the LLM, asking for self-correction.

This strategy is appropriate when semantic drift occurs—cases where deterministic rules cannot resolve ambiguity.

### 5.2 Drift → Repair Mapping

All Guided Repair flows MUST observe the Repair Budget. When retries are exhausted, the runtime transitions to `failover_triggered` or `session_closed` without re-entering Drift.
Example flow:

1. `drift_detected` (e.g., `D1_instruction`, `D3_repeated_plan`)
2. `repair_triggered` using an appropriate R*-family code (e.g., `R3_rewrite`)
3. LLM performs correction:

   * rewriting instructions
   * clarifying intent
   * restructuring responses
4. Success:

   * `continue_allowed` or `reentry_observed`
5. Failure:

   * repeated drift and additional repair cycles

The LLM is treated only as a repair **tool**—its usage does not create new event types or taxonomy values.

### 5.3 Recommended Use Cases

* Misinterpreted user instructions
* Multi-step plans drifting off-target
* Conversation requiring clarification or reformulation
* Natural language content correction

## 5.4 Clarifying repair_escalated vs drift_escalated

* **repair_escalated**: Used when strengthening the repair strategy (Static → Guided → HITL) while remaining in the Repair phase.
* **drift_escalated**: Used when revising the drift classification before repair begins.

## 6. Human-in-the-Loop (Governor) Strategy

### 6.1 Concept

This strategy inserts a governance gate for high-risk contexts. The system blocks automated continuation after Repair until a human operator makes a decision.

This is not a new PLD phase; it is an implementation pattern using existing Continue and Outcome semantics.

### 6.2 Drift → Repair → Governed Continue

HITL requires asynchronous suspension support in the runtime implementation. `continue_allowed` MAY be emitted by the runtime or by a human-facing system callback.
Example flow:

1. Severe `drift_detected` (e.g., tool failure affecting financial operations)
2. `repair_triggered` (e.g., `R4_request_clarification` or `R5_hard_reset`)
3. System blocks automatic continuation using:

   * `continue_blocked`
4. Human intervention:

   * **Approve** → `continue_allowed`
   * **Reject** → `session_closed` (Outcome) or `failover_triggered`

Because this pattern may halt automated execution, it is effective in domains where unreviewed actions could cause harm.

### 6.3 Recommended Use Cases

* Financial transactions or compliance-sensitive workflows
* Medical, legal, or safety-critical decisions
* Enterprise governance processes requiring auditable human approval

## 7. Choosing a Strategy

Selecting a strategy depends on latency constraints, risk tolerance, and semantic complexity.

### 7.1 Guidelines

* **Static Repair**: use when structural correctness is the goal.
* **Guided Repair**: use when semantic understanding or rewriting is required.
* **Human-in-the-Loop**: use when human oversight is mandatory.

### 7.2 Hybrid Patterns

A robust system may combine strategies:

```
Static → Guided → Human Escalation
```

This ensures low-latency fixes for simple issues, LLM-powered recovery for semantic drift, and human governance for safety-critical failures.

## 8. Implementation Notes (Non-Normative)

* Reentry should be interpreted as *state integrity validation* before resuming the task.
* Static Repair SHOULD include payload information describing the original error to preserve observability.
  (Non-Normative)
* Use Level 5 components such as `RuntimeSignalBridge`, detectors, and controllers to implement these strategies.
* Do not modify PLD schema, taxonomy, or semantic rules.
* Events MUST be considered immutable once constructed.
* Ensure all event emissions follow the Level 1 schema and Level 2 event matrix.
