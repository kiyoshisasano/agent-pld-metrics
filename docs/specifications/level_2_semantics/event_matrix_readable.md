---
title: "PLD Event Matrix Specification"
version: "2.0"
status: "Candidate"
authority: "Hard Invariant (Semantic Layer)"
stability: "Stable - Breaking changes require major version bump"
---

# PLD Event Matrix — Normative Rules

## 0. Purpose

This document defines the **semantic validation layer** for PLD runtime events.

The JSON Schema ensures **structural validity**, while this matrix ensures **semantic correctness and operational consistency**.

> A PLD event MUST satisfy both layers to be considered valid.

---

## 1. Phase ↔ Code Prefix Constraint (MUST)

### Required Mapping

| Prefix | Required Phase |
|--------|----------------|
| `D`    | drift          |
| `R`    | repair         |
| `RE`   | reentry        |
| `C`    | continue       |
| `O`    | outcome        |
| `F`    | failover       |

These are **lifecycle prefixes**. They are only valid when `phase != "none"`.

---

### Hard Rule

For **lifecycle prefixes only**:

```sql
If extract_prefix(pld.code) is in {D, R, RE, C, O, F},
then it MUST correspond to pld.phase.
```

#### Equivalent executable form:

```python
PREFIX_MAP = {
    "D":  "drift",
    "R":  "repair",
    "RE": "reentry",
    "C":  "continue",
    "O":  "outcome",
    "F":  "failover",
}

def assert_prefix_phase_consistency(code: str, phase: str) -> None:
    prefix = extract_prefix(code)
    if prefix in PREFIX_MAP:
        # Lifecycle prefixes MUST match the lifecycle phase
        assert PREFIX_MAP[prefix] == phase
    else:
        # Non-lifecycle prefixes are only allowed with phase="none"
        assert phase == "none"
```

#### Prefix Extraction Rules

```sql
Prefix = <characters before first "_"> minus trailing digits.
Example: "D4_tool_error" → "D"
```

---

#### Special Case: `phase="none"` (Normative)

Events whose `pld.phase` is `"none"`:

- **MUST NOT** use lifecycle prefixes (`D/R/RE/C/O/F`)
- **MUST** use non-lifecycle prefixes (e.g., `INFO`, `META`, `SYS`) if a prefix is present
- **SHOULD** use free-form semantic label codes (e.g., `INFO_debug`)
- MAY omit numeric classifier segments (e.g., `INFO_debug`, `SYS_init`) or include them (e.g., `INFO1_debug`)
Non-lifecycle prefixes implicitly correspond to `phase="none"`.

Example:

| code          | phase | valid?             | notes                      |
| ------------- | ----- | ------------------ | -------------------------- |
| `INFO_debug`  | none  | ✔                  | non-lifecycle prefix       |
| `SYS_init`    | none  | ✔                  | non-lifecycle prefix       |
| `INFO1_debug` | none  | ✔                  | numeric classifier used    |
| `D4_error`    | none  | ❌ prefix violation | lifecycle prefix with none |

---

## 2. Event Type → Phase Alignment

### 2.1 Constraint Levels

| Level  | Meaning                  | Enforcement         |
| ------ | ------------------------ | ------------------- |
| MUST   | Required mapping         | Reject on violation |
| SHOULD | Expected/default mapping | Warn on violation   |
| MAY    | Context-controlled       | Always allowed      |

---

### 2.2 Canonical Matrix

| event_type         | allowed phase | constraint |
| ------------------ | ------------- | ---------- |
| drift_detected     | drift         | MUST       |
| drift_escalated    | drift         | MUST       |
| repair_triggered   | repair        | MUST       |
| repair_escalated   | repair        | MUST       |
| reentry_observed   | reentry       | MUST       |
| continue_allowed   | continue      | MUST       |
| continue_blocked   | continue      | MUST       |
| failover_triggered | failover      | MUST       |

---

### 2.3 Evaluative Events (SHOULD)

| event_type      | recommended phase        | constraint |
| --------------- | ------------------------ | ---------- |
| evaluation_pass | outcome                  | SHOULD     |
| evaluation_fail | outcome                  | SHOULD     |
| session_closed  | outcome (default) / none | SHOULD     |
| info            | none                     | SHOULD     |

---

### 2.4 Context-Dependent Events (MAY)

| event_type        | allowed phases | constraint                            | notes                 |
| ----------------- | -------------- | ------------------------------------- | --------------------- |
| latency_spike     | any            | MAY                                   | observability         |
| pause_detected    | any            | MAY                                   | idle                  |
| handoff           | any            | MAY                                   | system/human transfer |
| fallback_executed | any            | MAY (recommended: repair or failover) | operational override  |

---

## 3. Phase Inference Guidance (Reference Code)

```python
VALID_PHASES = ["drift", "repair", "reentry", "continue", "outcome", "failover", "none"]

def infer_phase(event_type: str, context: dict) -> str:
    current = context.get("current_phase")
    if current not in VALID_PHASES:
        current = None

    if event_type == "fallback_executed":
        if current in ["repair", "failover"]:
            return current
        return "failover"

    if event_type in ["latency_spike", "pause_detected", "handoff"]:
        return current or "none"

    return "none"
```

---

## 4. Machine Mapping Source of Truth

This document is paired with:
```bash
docs/event_matrix.yaml
```
→ That file is the normative mapping used by CI, validators, and SDKs.

---

## 5. Validation Modes

| Mode          | MUST Violations | SHOULD Violations | Intended Use                             |
| ------------- | --------------- | ----------------- | ---------------------------------------- |
| **strict**    | Reject ❌        | Ignore            | Production ingestion                     |
| **warn**      | Reject ❌        | Warn ⚠            | Staging / Model tuning                   |
| **normalize** | Auto-repair     | Warn ⚠ or accept  | Autonomous agents / runtime self-healing |

These correspond directly to the `validation_modes` block in `docs/event_matrix.yaml`.

---

## 6. Validity Condition (Formal)

### Natural Language:
> An event is considered PLD-valid **only if both its schema and its semantic mapping are valid**.

### Logical Form:

```scss
PLD_valid(event) ⇔ schema_valid(event) ∧ matrix_valid(event)
```

### Machine Expression:

```python
is_valid = schema_valid(event) and matrix_valid(event)
```

---

End of Specification
