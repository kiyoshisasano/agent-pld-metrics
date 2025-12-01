# PLD Event Schema Specification  
**Version:** 2.0  
**Status:** Working Draft (Stable)  
**Stability:** API-stable; breaking changes require a major version change  
**Feedback:** Actively seeking implementation feedback  

---

## 1. Purpose

This document defines the **normative specification** for PLD Runtime Events, based exclusively on:

- `quickstart/metrics/schemas/pld_event.schema.json`  
- `docs/event_matrix.yaml`  
- `docs/event_matrix.md`  

It defines how PLD runtime events MUST be structured, validated, interpreted, and processed across systems that generate, observe, or analyze agent lifecycle behavior.

### Background

This specification originated from ongoing work in **agent runtime observability**, including efforts to model safety drift, repair behaviors, and structured evaluation outcomes across autonomous or semi-autonomous systems.  

The evolution of this specification has incorporated:

- Initial implementation experiments  
- Practical feedback from agent runtime libraries and observability discussions  
- Validation and refinement assisted by automated reasoning and rule checking  

**Current Status:**  
This is a *working draft with stable semantics*. Structure and validation rules are not expected to change within major version `2.x`, but feedback-driven improvements MAY occur.

---

## 2. Scope

This specification applies to runtime event streams produced by:

- Autonomous or semi-autonomous agents  
- Model-based controllers  
- Drift or anomaly detection subsystems  
- User or system-originated interactions  
- Observability infrastructure and failover automation  

It provides a unified structure for recording state-change conditions in adaptive or agentic runtime environments.

Legacy `1.1` formats are **not normative** and MUST NOT be used for new implementations.

---

## 3. Core Model Overview

A PLD event is a structured record describing a single observed or inferred lifecycle condition.

Every PLD event includes:

- **Required metadata fields**
- **A lifecycle-aligned PLD classification**
- **Optional runtime diagnostic metadata**
- **A user-experience impact declaration**

A PLD event is considered valid **only when both conditions below are true**:
```
schema_valid(event) ∧ matrix_valid(event)
```

Where:
- `schema_valid(event)`: The event passes JSON Schema validation (`pld_event.schema.json`)
- `matrix_valid(event)`: The event satisfies semantic constraints (`event_matrix.yaml`)

The schema enforces strict validation with `additionalProperties: false`, rejecting any fields not explicitly defined in the schema.

---

## 4. Required Fields

Every event MUST contain the following fields exactly as defined:

| Field | Type | Constraint |
|-------|------|------------|
| `schema_version` | string | MUST equal `"2.0"` |
| `event_id` | string | Unique identifier, UUIDv4 recommended |
| `timestamp` | string (ISO-8601) | MUST conform to `format="date-time"` |
| `session_id` | string | Unique session identifier |
| `turn_sequence` | integer ≥ 1 | Authoritative ordering index |
| `source` | enum | One of: `user`, `assistant`, `runtime`, `controller`, `detector`, `system` |
| `event_type` | enum | MUST follow mapping rules defined in Section 6 |
| `pld` | object | MUST follow PLD structure rules (Section 5) |
| `payload` | object | Arbitrary schema-agnostic content |
| `ux` | object | MUST contain boolean field `user_visible_state_change` |

Optional fields: `turn_id`, `runtime`, `metrics`, `extensions`.

**Schema Constraint:**  
The schema enforces `additionalProperties: false`, rejecting any fields not explicitly defined.

---

## 5. PLD Object Specification

The `pld` object MUST contain:

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `phase` | enum | yes | MUST be one of: `drift`, `repair`, `reentry`, `continue`, `outcome`, `failover`, `none` |
| `code` | string | yes | MUST follow lifecycle code rules |
| `confidence` | number | no | MUST be between `0` and `1` inclusive |
| `metadata` | object | no | Free-form contextual metadata |

### 5.1 Code Structure Rules

A valid `pld.code` MUST match the canonical pattern:

```
^[A-Z][A-Z0-9]*(?:[0-9]+)?(?:_[a-z0-9]+(?:_[a-z0-9]+)*)?$
```


Code structure consists of:

- **Prefix** (`D`, `R`, `RE`, `C`, `O`, `F`, or a non-lifecycle classifier)  
- **Optional numeric classifier**  
- **Optional semantic descriptor in lowercase snake_case**

Examples (normative):

| phase | code | Validity Basis |
|-------|------|----------------|
| drift | `D4_tool_error` | lifecycle prefix + classifier + descriptor |
| none | `INFO_debug` | non-lifecycle prefix required |
| reentry | `RE2_context_exceeded` | lifecycle prefix + numeric classifier |

### 5.2 Lifecycle Prefix Enforcement

Codes with lifecycle prefixes MUST map exactly to the corresponding PLD phase.

Validation MUST enforce:

```
pld.phase == PHASE_MAP[extract_prefix(pld.code)]
```


Where:

```python
PHASE_MAP = {
    "D": "drift",
    "R": "repair",
    "RE": "reentry",
    "C": "continue",
    "O": "outcome",
    "F": "failover"
}
```

---

### 5.3 Phase `"none"` Policy

When pld.phase = `"none"`:
- Codes MUST NOT begin with lifecycle prefixes
- Non-lifecycle naming (e.g., `INFO_debug`, `SYS_init`) is expected
- Numeric classifiers MAY be used, but are optional

---

## 6. Event Type Constraints

Event types determine required alignment with lifecycle phases.

### Enforcement Levels

| Level  | Meaning           | Enforcement             |
| ------ | ----------------- | ----------------------- |
| MUST   | Required mapping  | Violations are rejected |
| SHOULD | Expected default  | Violations MAY warn     |
| MAY    | Context-dependent | Always permissible      |

### 6.1 MUST Mappings

| event_type         | phase    |
| ------------------ | -------- |
| drift_detected     | drift    |
| drift_escalated    | drift    |
| repair_triggered   | repair   |
| repair_escalated   | repair   |
| reentry_observed   | reentry  |
| continue_allowed   | continue |
| continue_blocked   | continue |
| failover_triggered | failover |

### 6.2 SHOULD Mappings

| event_type      | expected phase                       |
| --------------- | ------------------------------------ |
| evaluation_pass | outcome                              |
| evaluation_fail | outcome                              |
| session_closed  | outcome (default) / none (justified) |
| info            | none                                 |

### 6.3 MAY Events

| event_type        | allowed phase                         |
| ----------------- | ------------------------------------- |
| latency_spike     | any                                   |
| pause_detected    | any                                   |
| fallback_executed | any (recommended: repair or failover) |
| handoff           | any                                   |

---

## 7. Validation Modes

Validation MAY operate in one of three modes:

| Mode      | MUST Violations          | SHOULD Violations | Intended Use         |
| --------- | ------------------------ | ----------------- | -------------------- |
| strict    | reject                   | ignore            | Production ingestion |
| warn      | reject                   | warn              | Staging              |
| normalize | auto-correct if possible | warn or accept    | Self-healing agents  |

---

## 8. Version Compatibility Policy

Implementations MUST enforce schema version compatibility as follows:
- Events with a different major version MUST be rejected.
- Events with the same major version and different minor version MUST NOT be rejected automatically.
- Forward compatibility MAY be supported within the same major version.

### Examples

| schema_version value | Expected result |
| -------------------- | --------------- |
| `"2.0"`              | ✅ Accept        |
| `"2.1"`              | ✅ Accept        |
| `"1.1"`              | ❌ Reject        |
| `"3.0"`              | ❌ Reject        |

---

## 9. Examples (Normative)

### 9.1 Valid Drift Detection Example

```json
{
  "schema_version": "2.0",
  "event_id": "751fb0dc-15a4-4b4d-a204-1b8e94f24e06",
  "timestamp": "2025-01-10T12:40:22Z",
  "session_id": "a4e7b593-9409-4122-b9ed-06c70bd8549d",
  "turn_sequence": 3,
  "source": "detector",
  "event_type": "drift_detected",
  "pld": {
    "phase": "drift",
    "code": "D4_tool_error",
    "confidence": 0.91
  },
  "payload": {
    "detector_output": "semantic deviation detected"
  },
  "ux": {
    "user_visible_state_change": false
  }
}
```

### 9.2 Valid Non-Lifecycle Informational Example

```json
{
  "schema_version": "2.0",
  "event_id": "cc4dc21e-dc22-4762-a3a4-e040a734c091",
  "timestamp": "2025-01-10T12:41:00Z",
  "session_id": "a4e7b593-9409-4122-b9ed-06c70bd8549d",
  "turn_sequence": 4,
  "source": "runtime",
  "event_type": "info",
  "pld": {
    "phase": "none",
    "code": "SYS_init"
  },
  "payload": {},
  "ux": {
    "user_visible_state_change": false
  }
}
```

---

## 10. Validity Definition

A PLD event is valid only when:

```scss
PLD_valid(event) ⇔ schema_valid(event) ∧ matrix_valid(event)
```

Both checks are required.

---

## 11. Specification Status

This document represents the normative Version 2.0 specification for PLD Runtime Event encoding, validation, and interpretation.

### Conformance Requirements

Implementations claiming PLD v2.0 conformance MUST satisfy:

1. JSON Schema validation (`pld_event.schema.json`)
2. Semantic matrix constraints (`event_matrix.yaml`)
3. Validation mode compliance (Section 7)

### Feedback and Evolution

This specification is:

- ✅ Stable: rules will not change within major version 2.x
- 🔄 Open: ongoing refinement informed by usage and feedback
- 📢 Community-driven: improvements encouraged

Feedback, usage reports, and improvement proposals may be submitted via:
> GitHub Issues or Discussions (repository reference TBD)

---

### End of Specification


