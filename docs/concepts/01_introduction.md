<!-- License: CC BY 4.0 -->

## 📌 01 — PLD for Agent Engineers

**How to build agents that remain stable, observable, and recoverable**.

Version: `2.0`  
Status: Candidate (Working Draft, Normative for operational rules)

**Referenced authoritative sources**:

- **Level 1** — Schema: `docs/schemas/pld_event.schema.json`
- **Level 2** — Semantics: `docs/event_matrix.md`, `docs/schemas/event_matrix.yaml`, `docs/03_pld_event_spec.md`
- **Level 3** — Operations: `docs/01_pld_for_agent_engineers.md` (this document), `docs/07_pld_operational_metrics_cookbook.md`, `docs/schemas/metrics_schema.yaml`
- **Level 4** — Examples: `quickstart/hello_pld_runtime.py`, `quickstart/run_minimal_engine.py`, `quickstart/examples/minimal_pld_demo.py`, `quickstart/patterns/03_system/logging_and_schema_examples.md`
  
**Audience**: Engineers implementing PLD-aligned runtime behavior and logging.

---

## Table of Contents

0. Purpose  
1. Why PLD Exists  
2. Reference Model for Specification  
3. Core Runtime Model  
4. Engineering Requirements  
5. Integration Pattern (Runtime Execution Model)  
    - 5.1 Drift Detection Requirements  
    - 5.2 Repair Strategy Selection  
    - 5.3 Execution Pseudocode (Reference Only)  
    - 5.4 Optional Enhancements  
6. Logging Requirements  
7. Reentry Requirements  
    - 7.1 Classification Rules  
    - 7.2 Deferred Reentry Rules  
    - 7.3 Implementation Patterns  
8. Validation Modes  
    - 8.1 Violation Categorization  
    - 8.2 Auto-Correction Rules  
    - 8.3 Operational Guidance  
9. Alignment Checklist  
10. Summary Statement & Next Steps  

Appendix A — Implementation Examples (Non-Normative)  
- A.1 Drift Detection Example: Repeated Plan  
- A.2 Extended Repair Strategy Table  
- A.3 `emit_pld` Helper Implementation  
- A.4 Reentry Patterns (Recap)

---

## 0. Purpose

If you're already familiar with building tools, planning systems, memory scaffolds, and LLM workflows, PLD focuses on a different question:

> **How do we keep multi-turn agents stable and governable over time—not only when things work, but especially when they don't?**

PLD provides:

- A runtime lifecycle model
- A shared vocabulary for drift, repair, and recovery
- A logging structure aligned with schema + semantics
- A validation and governance loop
- Metrics indicating whether changes improved or degraded behavior

PLD is **not a framework**. It is a discipline:  
→ **Structure + governance + telemetry**, layered onto whatever runtime you already use.

---

## 1. Why PLD Exists

Multi-turn agents commonly fail in recognizable patterns:

- Repeating tools
- Repeating plans
- Fixing a problem, only to drift again later
- Breaking after model/tool changes
- Behaving fine in development but collapsing under real user variance

These failures are usually not random bugs — they are symptoms of **missing runtime governance**.

PLD formalizes that governance as a lifecycle:

```
Drift → Repair → Reentry → Continue → Outcome
```

Each turn is evaluated using structured prompts:

- Did drift occur?
- If so, what repair is appropriate?
- Did the repair stabilize behavior?
- Should execution continue?
- How did the interaction conclude?

---

## 2. Reference Model for Specification

When conflicts occur, higher levels prevail.

| Level | Source                                    | Role                        |
| ----- | ----------------------------------------- | --------------------------- |
| 1     | `pld_event.schema.json`                   | Structural invariant — MUST |
| 2     | `event_matrix.md` / `event_matrix.yaml`   | Semantic mapping — MUST     |
| 3     | `03_pld_event_spec.md` + this document    | Operational rules — SHOULD  |
| 4     | Examples (this doc, demo code, tutorials) | Optional reference — MAY    |

This hierarchy is intended as a practical guide:  
`no rule in this document may override Level 1 or Level 2.`

Examples in Appendix A are always non-normative.

---

## 3. Core Runtime Model

Lifecycle prefixes MUST match the declared `pld.phase`.

| Prefix | Phase    | Meaning                                          |
| ------ | -------- | ------------------------------------------------ |
| `D`    | drift    | deviation from goal, user intent, or constraints |
| `R`    | repair   | corrective action                                |
| `RE`   | reentry  | stability validation after repair                |
| `C`    | continue | normal execution under stable conditions         |
| `O`    | outcome  | terminal condition                               |
| `F`    | failover | handoff or abandonment                           |

If `pld.phase = "none"`, lifecycle prefixes (`D/R/RE/C/O/F`) MUST NOT be used.

---

## 4. Engineering Requirements (Normative)

A turn is considered PLD-valid when:

```
schema_valid(event) AND semantic_valid(event)
```

Where:
- `schema_valid(event)` enforces Level 1 (structural rules).
- `semantic_valid(event)` enforces Level 2 (matrix + mapping rules).

Examples of required `event_type` → `phase` mapping:

| event_type           | required phase |
| -------------------- | -------------- |
| `drift_detected`     | `drift`        |
| `drift_escalated`    | `drift`        |
| `repair_triggered`   | `repair`       |
| `reentry_observed`   | `reentry`      |
| `continue_allowed`   | `continue`     |
| `continue_blocked`   | `continue`     |
| `failover_triggered` | `failover`     |

Informational events (`info`, some `session_closed` cases) SHOULD use `phase = "none"` unless a different lifecycle phase is clearly justified by the semantics.

---

## 5. Integration Pattern (Runtime Execution Model)

A PLD-aligned runtime MUST follow the sequence:

> **Execute → Detect → Repair → Validate (Reentry) → Continue/Terminate → Log**

Logical steps per turn:

1. Execute the agent turn (LLM + tools + memory).
2. Detect drift.
3. If drift is present → emit a `drift_detected` event.
4. Select and apply a repair strategy (soft → hard → failover).
5. Emit a `repair_triggered` (and optionally escalation) event.
6. Validate stabilization via reentry (explicit, constraint-based, or automatic).
7. Emit a `reentry_observed` event.
8. Continue execution or conclude with an outcome event.
9. **MUST** emit at least one PLD event per turn.

This pattern is framework-agnostic and applies regardless of whether you use LangGraph, the Assistants API, custom orchestration, or hybrid controllers. 

---

### 5.1 Drift Detection Requirements

A drift detector MUST always produce a structured result:

- A lifecycle drift code (`D1–D5`, etc.), or
- A neutral `"D0_none"` code indicating **no drift detected**.

Signals MAY be derived from:

| Source Type       | Examples                                                 |
| ----------------- | -------------------------------------------------------- |
| System state      | tool failures, timeouts, latency spikes                  |
| Behavior analysis | repeated tools, repeated plans, missing expected actions |
| LLM evaluation    | task misalignment, policy violations, user-goal mismatch |

Non-normative minimal example:

```python
def detect_drift(turn_state):
    if turn_state.get("tool_error"):
        return {"code": "D4_tool_error", "confidence": 0.95}

    if turn_state.get("latency_ms", 0) > 3500:
        return {"code": "D5_latency_spike", "confidence": 0.7}

    if detect_repeated_plan(turn_state["history"]):
        return {"code": "D3_repeated_plan", "confidence": 0.80}

    return {"code": "D0_none", "confidence": 1.0}
```

A more detailed example of `detect_repeated_plan` is provided in **Appendix A.1**.

---

### 5.2 Repair Strategy Selection

Repair MUST follow **predictable escalation rules** rather than ad hoc retries.

At minimum, implementations MUST distinguish:

- **Soft repair** — low-impact corrective action (rephrase, add context, retry once).
- **Hard repair** — stronger action (plan regeneration, context reset, tool change).
- **Failover** — abandon or hand off when recovery is not feasible or safe.

Normative behavior:

| Condition                             | Required Action (high level)          |
| ------------------------------------- | ------------------------------------- |
| First occurrence of correctable drift | Try soft repair (`R1*`)               |
| Drift repeats under same conditions   | Escalate to hard repair (`R2*`/`R3*`) |
| Repeated failure or unsafe state      | Transition to failover (`F*`)         |

Non-normative minimal example:

```python
def choose_repair(drift, repair_count):
    if drift["code"].startswith("D4") and repair_count < 2:
        return "R1_soft_repair"
    if repair_count >= 2:
        return "R3_hard_reset"
    return "R1_soft_repair"
```

A more expressive mapping-based strategy (`REPAIR_STRATEGIES`) is provided in **Appendix A.2**.

---

### 5.3 Execution Pseudocode (Reference Only)

The following is a non-normative template showing how drift detection, repair, reentry, and logging may be wired together:

```python
async def pld_turn(agent, state):
    # 1. Execute the main agent step
    response = await agent.step(state)

    # 2. Detect drift
    drift = detect_drift(state)

    if drift["code"] != "D0_none":
        # 3. Emit drift event
        emit_pld("drift_detected", phase="drift", code=drift["code"])
        
        # 4. Select and apply repair
        repair_mode = choose_repair(drift, state["repair_count"])
        repaired = await apply_repair(agent, repair_mode)
        
        # 5. Emit repair event
        emit_pld("repair_triggered", phase="repair", code=repair_mode)

        # 6. Validate reentry
        if evaluate_reentry(state, repair_mode):
            emit_pld("reentry_observed", phase="reentry", code="RE3_auto")
    else:
        # No drift → continue allowed
        emit_pld("continue_allowed", phase="continue", code="C0_normal")

    return response
```

A concrete example of `emit_pld` wired to a logging pipeline is provided in **Appendix A.3**.

---

### 5.4 Optional Enhancements

The following enhancements are not required, but are recommended for production systems:

| Enhancement                             | Benefit                                               |
| --------------------------------------- | ----------------------------------------------------- |
| Confidence-weighted escalation          | Avoid unnecessary resets and failovers                |
| Strategy registry (`REPAIR_STRATEGIES`) | Centralizes repair behavior per drift type            |
| Shadow validation pipelines             | Safely test new detection/repair logic in parallel    |
| Drift clustering and analytics          | Identify systemic issues in tools, prompts, or models |

---

## 6. Logging Requirements

Every runtime MUST emit at least one PLD event per turn.

Required fields (derived from Level 1 schema and Level 2 semantics) include:

| Field                          | Constraint                                  |
| ------------------------------ | ------------------------------------------- |
| `schema_version`               | MUST equal `"2.0"`                          |
| `event_id`                     | Required; unique identifier                 |
| `timestamp`                    | Required; RFC 3339 / ISO 8601               |
| `session_id`                   | Required; stable for an interaction         |
| `turn_sequence`                | Required; monotonic integer                 |
| `source`                       | MUST be a recognized enum value             |
| `event_type`                   | MUST align with lifecycle phase constraints |
| `pld.phase`                    | MUST follow lifecycle prefix rules          |
| `pld.code`                     | MUST follow naming and prefix rules         |
| `ux.user_visible_state_change` | REQUIRED boolean                            |

Additional objects such as `payload`, `runtime`, `metrics`, `extensions` MAY be populated as long as the event remains schema-valid.

A concrete helper for emitting PLD events (`emit_pld`) is provided in **Appendix A.3**.

---

## 7. Reentry Requirements

Reentry evaluates whether a repair successfully restored stable behavior.  
A system MUST perform reentry evaluation after any repair action that modifies agent state or behavior.

Reentry MUST:

1. Decide whether drift has been resolved (or sufficiently mitigated).
2. Produce a `reentry_observed` event with an appropriate `RE*` code.
3. Either authorize continuation (`continue_allowed`) or trigger further repair/failover.

---

### 7.1 Classification Rules

Reentry codes are grouped into three conceptual classes:

| Code Class | Meaning               | Typical Use                                                               |
| ---------- | --------------------- | ------------------------------------------------------------------------- |
| `RE1_*`    | Explicit confirmation | User or LLM explicitly agrees that the course of action is correct.       |
| `RE2_*`    | Constraint validation | System-level verification (tools, DB state, business constraints) passes. |
| `RE3_auto` | Automatic reentry     | Stability is inferred from the absence of further drift signals.          |

If uncertainty exists regarding the reentry type, implementations SHOULD prefer `RE2_*` (constraint validation) over `RE3_auto`.

---

### 7.2 Deferred Reentry Rules

Deferred reentry is allowed only in `normalize` mode.

In this case:
- Current turn performs repair but does not immediately assert reentry.
- Next turn's drift detection outcome determines whether the prior repair succeeded.

Informal rule:

```
If next turn drifts again → prior repair failed → escalate (harder repair or failover).
If next turn does not drift → treat prior repair as successful → implicit RE3_auto.
```

Deferred reentry MUST still be represented by a `reentry_observed` event once a verdict is available.

---

### 7.3 Implementation Patterns

Non-normative examples of reentry patterns:

#### Pattern 1 — Explicit Confirmation (RE1_*)

```python
async def explicit_reentry(agent, repair_result):
    ok = await agent.ask_user_or_model("Should I continue with this plan?")
    if ok:
        emit_pld(
            "reentry_observed",
            phase="reentry",
            code="RE1_intent_confirmed",
        )
        return True
    return False
```

#### Pattern 2 — Constraint Validation (RE2_*)

```python
def constraint_reentry(agent, state):
    validation = agent.validate_state()
    if validation.is_aligned:
        emit_pld(
            "reentry_observed",
            phase="reentry",
            code="RE2_constraints_validated",
        )
        return True
    return False
```

#### Pattern 3 — Automatic (RE3_auto)

```python
def auto_reentry():
    emit_pld(
        "reentry_observed",
        phase="reentry",
        code="RE3_auto",
    )
    return True
```

Additional discussion and examples are provided in **Appendix A.4**.

---

## 8. Validation Modes

Validation mode defines how strictly the runtime enforces PLD structure and semantics, and how it responds to violations.

A runtime MUST operate in exactly one declared mode:

| Mode        | Enforcement Style                                                  |
| ----------- | ------------------------------------------------------------------ |
| `strict`    | Fail-fast; reject any invalid event                                |
| `warn`      | Reject MUST violations; accept with warnings for SHOULD violations |
| `normalize` | Attempt automatic correction of safe violations; reject others     |

Systems MUST declare the selected mode at configuration/init time.

---

### 8.1 Violation Categorization

Violations are grouped into:

| Type                       | Examples                                            | Handling (high-level)                                                      |
| -------------------------- | --------------------------------------------------- | -------------------------------------------------------------------------- |
| Schema violations          | Missing required fields, wrong types, invalid enums | MUST be rejected in all modes.                                             |
| MUST semantic violations   | `drift_detected` with `phase="continue"`            | Reject in `strict`/`warn`; may auto-correct in `normalize` if unambiguous. |
| SHOULD semantic violations | Non-standard but harmless mappings                  | Ignore in `strict`; warn in `warn`; may auto-correct in `normalize`.       |

---

### 8.2 Auto-Correction Rules (Normalize Mode Only)

`normalize` mode MAY correct:

- **Phase mismatches** where the mapping is uniquely determined by the event type.
  - e.g., `event_type="evaluation_pass"` but `pld.phase="drift"` → corrected to `"outcome"`.
- **Missing descriptors** when a safe default exists.
  - e.g., `code="D"` → `"D0_unspecified"`.
- **Prefix/phase misalignment** when prefix has a unique corresponding phase.
  - e.g., `code="R1_soft_repair"` and `phase="drift"` → `phase` corrected to `"repair"`.

`normalize` mode MUST NOT attempt correction when:

- Required schema structure is missing.
- Lifecycle semantics are ambiguous or contradictory (`repair_triggered` with `phase="continue"` and a non-`R*` code).
- There is no unique, safe correction consistent with Level 2 rules.

---

### 8.3 Operational Guidance

Recommended defaults:

| Deployment Stage                 | Recommended Mode   |
| -------------------------------- | ------------------ |
| Production                       | `strict` or `warn` |
| Staging / pre-production         | `warn`             |
| Experimental self-healing agents | `normalize`        |

`normalize` MUST be gated by careful monitoring, as auto-correction itself can introduce risk if misconfigured.

---

## 9. Alignment Checklist

A system may be considered PLD-aligned when all of the following hold:

- ☐ Schema validation is enforced (`pld_event.schema.json`).
- ☐ Semantic matrix rules (prefix-phase and event_type-phase mappings) are enforced.
- ☐ Exactly one validation mode is configured and documented (`strict` / `warn` / `normalize`).
- ☐ At least one PLD event is emitted per turn.
- ☐ Reentry logic is implemented (explicit, constraint-based, auto, or deferred where allowed).
- ☐ Outcome state is recorded at session end (`outcome` or `failover` events).

Diagnostic question:

> **"When this agent drifts, what happens next — and how do we know whether the repair worked?"**

If answering this requires guesswork, PLD alignment is not yet complete.

---

## 10. Summary Statement & Next Steps

> **PLD provides the lifecycle, structure, and telemetry required to make multi-turn agents governable, resilient, and measurable over time.**

Recommended next steps for implementers:

1. Add schema + semantic validation to your logging pipeline.
2. Integrate a minimal drift detector returning `D0_none` or `D*` codes.
3. Implement a simple repair escalation policy and reentry pattern.
4. Choose and document a validation mode.
5. Add dashboards for drift, repair, and outcome metrics over real traffic.

---

## Appendix A — Implementation Examples (Non-Normative)

> **Important**: This appendix is **non-normative**.  
> It illustrates one way to implement PLD-aligned behavior, but MUST NOT be treated as mandatory.

---

### A.1 Drift Detection Example: Repeated Plan

An example of detecting repeated plans using a simple similarity check:

```python
import difflib
from typing import List

class Turn:
    def __init__(self, plan_description: str):
        self.plan_description = plan_description

def detect_repeated_plan(history: List[Turn]) -> bool:
    """Example implementation of plan repetition detection.
    Implementers are encouraged to refine this based on their domain.
    """
    if len(history) < 2:
        return False
    
    current = history[-1].plan_description
    previous = history[-2].plan_description
    
    # Simple similarity check (can be replaced with embedding-based methods)
    similarity = difflib.SequenceMatcher(None, current, previous).ratio()
    return similarity > 0.9
```

This function can be plugged into `detect_drift` as shown in Section 5.1.

---

### A.2 Extended Repair Strategy Table

A more expressive configuration-based repair strategy example:

```python
from dataclasses import dataclass

@dataclass
class RepairEscalation:
    soft: str
    hard: str
    threshold: int  # max soft attempts before escalation

REPAIR_STRATEGIES = {
    "D1": RepairEscalation(
        soft="R1_add_context",
        hard="R2_force_different_tool",
        threshold=3,
    ),
    "D2": RepairEscalation(
        soft="R1_rephrase_goal",
        hard="R2_regenerate_plan",
        threshold=2,
    ),
    "D3": RepairEscalation(
        soft="R1_add_constraint",
        hard="R2_full_reset",
        threshold=2,
    ),
    "D4": RepairEscalation(
        soft="R1_retry",
        hard="R2_fallback",
        threshold=2,
    ),
    "D5": RepairEscalation(
        soft="R1_wait_backoff",
        hard="R2_skip_tool",
        threshold=3,
    ),
}

def choose_repair(drift, repair_count):
    # Take the first two characters as a simple prefix (e.g., "D1", "D2"...)
    drift_prefix = drift["code"][:2]
    strategy = REPAIR_STRATEGIES.get(drift_prefix)
    
    if not strategy:
        # Unknown drift type — conservative default could be failover
        return "F1_unknown_drift"
    
    if repair_count == 0:
        return strategy.soft
    elif repair_count < strategy.threshold:
        return strategy.hard
    else:
        return "F1_max_retries_exceeded"
```

This pattern allows you to centralize repair policies and adjust behavior per drift category without touching core control flow.

---

### A.3 `emit_pld` Helper Implementation

A non-normative helper for emitting PLD events into a logging pipeline:

```python
import uuid
from datetime import datetime

def get_current_session_id() -> str:
    # Implementation-specific: derive from context, request, or orchestration layer
    ...

def get_current_turn_sequence() -> int:
    # Implementation-specific: monotonic counter per session
    ...

def emit_pld(event_type: str, phase: str, code: str, **kwargs):
    """
    Emit a PLD event to the logging pipeline.

    Args:
        event_type: One of the canonical event types (e.g., "drift_detected").
        phase: PLD lifecycle phase (e.g., "drift", "repair").
        code: Classification code (e.g., "D4_tool_error").
        **kwargs: Additional fields such as payload, ux flags, metrics, etc.
    """
    event = {
        "schema_version": "2.0",
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "session_id": get_current_session_id(),
        "turn_sequence": get_current_turn_sequence(),
        "source": kwargs.get("source", "runtime"),
        "event_type": event_type,
        "pld": {
            "phase": phase,
            "code": code,
        },
        "payload": kwargs.get("payload", {}),
        "ux": {
            "user_visible_state_change": kwargs.get("user_visible", False)
        },
    }

    # Optional: runtime or metrics blocks
    runtime = kwargs.get("runtime")
    if runtime is not None:
        event["runtime"] = runtime

    metrics = kwargs.get("metrics")
    if metrics is not None:
        event["metrics"] = metrics

    # Send to logging pipeline (example: structured logging)
    logger = kwargs.get("logger")
    if logger is not None:
        logger.info("pld_event", extra=event)
    else:
        print(event)
```

Implementers should align this helper with:

- Their logging framework (e.g., OpenTelemetry, structured logs).
- Their schema validation and ingestion pipeline.

---

### A.4 Reentry Patterns (Recap)

For convenience, here are the three typical reentry patterns in one place:

```python
# Pattern 1: Explicit Confirmation (RE1_*)
async def explicit_reentry(agent, repair_result):
    ok = await agent.ask_user_or_model("Should I continue?")
    if ok:
        emit_pld("reentry_observed", phase="reentry", code="RE1_confirmed")
        return True
    return False


# Pattern 2: Constraint Validation (RE2_*)
def constraint_reentry(agent, state):
    validation = agent.validate_state()
    if validation.is_aligned:
        emit_pld("reentry_observed", phase="reentry", code="RE2_verified")
        return True
    return False


# Pattern 3: Automatic (RE3_auto)
def auto_reentry():
    emit_pld("reentry_observed", phase="reentry", code="RE3_auto")
    return True
```

These patterns are **examples**, not requirements. Implementers may define additional `RE1_*`, `RE2_*`, or `RE3_*` codes as long as they remain consistent with the Level 2 semantic rules.

---

**End of Document**

