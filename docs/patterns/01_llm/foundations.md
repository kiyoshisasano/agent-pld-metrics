<!--
component_id: llm_patterns_foundations
kind: doc
area: quickstart_patterns
status: draft
authority_level: 3
version: 2.0.0
purpose: Foundational conventions and layer boundaries for all pattern files in the LLM Pattern family.
-->

# PLD LLM Pattern Foundations

> **Scope:** This document defines the foundational conventions for the `patterns/01_llm` directory. It clarifies purpose, boundaries, and allowed pattern structures.
> **Status:** Draft — non-authoritative.

---

## 1. Purpose

> **Reactive Scope Guarantee:** Patterns in this directory are **reactive only** — they respond to runtime signals but never determine when a signal should be emitted or which phase is active. Runtime decision‑making remains fully owned by Level 5 (SignalBridge + controller logic).

This directory provides **LLM-side interaction patterns** that assist runtime behavior aligned with PLD Runtime signals and phases.

Patterns here are:

* **Usage guidance**, not schema or semantic expansion
* **Consumer layer only**, above Level 4 runtime examples
* **Non‑normative**, unless later promoted to spec

These files help an LLM remain aligned when processing runtime signals such as:

* Drift detection
* Repair phases
* User clarification sequences
* Reentry alignment

---

## 2. Position Within the PLD Layer Model

> **Consumer Definition:** "Consumer Layer" refers to the layer where application logic or LLM prompts make use of runtime signals and respond conversationally. The LLM consumes these patterns as guidance for output; the runtime consumes the resulting output. The Pattern Layer does **not** modify system logic, enforcement, or schema-level behavior.

| Layer                          | Description                                               | Allowed in Patterns       | Notes                                  |
| ------------------------------ | --------------------------------------------------------- | ------------------------- | -------------------------------------- |
| Level 1                        | Schema                                                    | ❌ No modifications        | Reference only                         |
| Level 2                        | Semantic Rules + Event Matrix                             | ❌ No modifications        | Used for reasoning consistency         |
| Level 3                        | Metrics + Runtime Contracts                               | ❌ No modifications        | Patterns may reference terminology     |
| Level 4                        | Quickstart Runtime Examples                               | ✔ Reference + reuse style | Do not alter logic                     |
| Level 5                        | Runtime Implementation (Signal Bridge, Structured Logger) | ✔ Reference context       | DO NOT override behavior               |
| Pattern Layer (this directory) | Conversational guidance & response patterns               | ✔ Create and refine       | Must NOT create new taxonomy or phases |

---

## 3. Constraints

Patterns operate under the following rules of responsibility separation:

* Runtime (Level 5) owns:

  * Signal detection
  * Phase determination
  * Enforcement, validation, and lifecycle control
* Pattern Layer owns:

  * How the LLM should phrase a response **once a signal has already been emitted**

Patterns **must NOT**:

* Invent or redefine lifecycle phases
* Introduce new event types or taxonomy codes
* Modify runtime validation or enforcement logic
* Act as controllers, detectors, or system logic

Patterns **may**:

* Provide examples of aligned LLM responses per runtime signal
* Suggest safe recovery dialogue structures
* Support repair, drift handling, or reentry flow
* Include reusable templates or phrasing guidelines

---

### 3.1 Runtime → Pattern Context Contract (I/O Agreement)

Some patterns require additional context supplied by the runtime to operate safely without inference or reconstruction.

#### Baseline Rule
The Pattern Layer must operate only on the context explicitly present in the prompt.  
It must **not infer or recreate missing goals, history, tool execution state, or constraints.**

#### Runtime Responsibilities (when applicable):
- Inject required context when emitting signals that depend on it.
- Context payload **may include:**
  - Restated goal
  - Summary of relevant past interaction
  - Constraints (policy, formatting, safety)
  - Tool execution details for `D4_tool_error`
- Communicate tone preference through system prompt or metadata (e.g., neutral vs UX-optimized).

#### Pattern Layer Responsibilities:
- Use pattern structures only with the provided context.
- If required context is missing:
  - Degrade gracefully to clarification, rather than reconstructing state.

##### Examples:
- `D4_tool_error` requires tool name, parameters, and output/summary to avoid hallucinated corrections.
- `R5_hard_reset` requires: goal, summary, constraints.  
  Without these, the correct fallback behavior is prompting the user for confirmation or missing pieces—not reconstructing.

---

## 4. Core Alignment Concepts

Patterns rely on existing PLD primitives:

| Concept      | Definition Summary                                   |
| ------------ | ---------------------------------------------------- |
| **Drift**    | Output deviates from expected intent or task framing |
| **Repair**   | Guided correction process to restore alignment       |
| **Reentry**  | Transition back to normal task execution             |
| **Continue** | User/system confirm stability and proceed            |

These concepts are applied conversationally — patterns must not assign new semantic behavior.

---

## 5. Pattern Structure Guidelines

Patterns describe **conversational structures and phrasing guidance only.**
They do **not** define schemas, machine‑readable response formats, or new structural output protocols.

Each pattern document (drift, repair, reentry, tool usage) should follow this layout:

1. **Context / When Applicable**
2. **Goals**
3. **Recommended LLM Response Formula**
4. **Examples**
5. **Notes / Cautions**

This ensures patterns are consistent and comparable.

---

## 6. Versioning Philosophy

* Major changes require confirmation that the update does **not conflict with Level 1–3 rules**.
* Incremental additions are allowed if they do not introduce control behavior.

Proposed maturity scale:

| Status  | Meaning                                     |
| ------- | ------------------------------------------- |
| Draft   | Early exploration, may change               |
| Stable  | Reviewed and compatible with runtime rules  |
| Adopted | Used consistently in multiple pattern files |

---

## 7. Next Steps

Once this foundation is confirmed, subsequent files will be created in this order:

1. `state_transition_examples.md`
2. `drift_response_patterns.md`
3. `repair_templates.md`
4. `reentry_alignment_patterns.md`
5. `tool_response_rules.md`

---

**End of foundations.md


