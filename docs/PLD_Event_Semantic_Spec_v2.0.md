# PLD_Event_Semantic_Spec_v2.0.md

**Status:** Normative
**Layer:** Level 2 — Semantic Rules
**Applies To:** All PLD-compliant runtimes and ingestion pipelines
**Document Scope:** Defines event–semantic constraints, interpretation behavior, allowable mappings, and validation conditions.
This document SHALL defer to: `pld_event.schema.json` and `event_matrix.yaml`.

---

## 1. Semantic Validity Model

**SEM-001**
A PLD event is valid only when:

```
schema_valid(event) ∧ matrix_valid(event)
```

**SEM-002**
`turn_sequence` SHALL define the authoritative temporal order.

**SEM-003**
`schema_version` MUST equal "2.0".

**SEM-004**
`event_type` semantics MUST be determined using the event-to-phase mapping rules defined in this document.

**SEM-005**
Lifecycle semantics MUST NOT be inferred from text content, payload signatures, or runtime heuristics.

---

## 2. PLD Phase Rules

**PHASE-001**
A PLD event MUST belong to exactly one phase from:
`drift`, `repair`, `reentry`, `continue`, `outcome`, `failover`, `none`.

**PHASE-002**
Lifecycle prefix in `pld.code` MUST correspond to the declared phase.

**PHASE-003**
Phase `"none"` MUST NOT use lifecycle prefixes.

**PHASE-004**
Numeric classifiers MAY exist but MUST NOT override lifecycle mapping.

---

## 3. Code Mapping Rules

**CODE-001**
Valid structure MUST match:

```
^[A-Z][A-Z0-9]*(?:[0-9]+)?(?:_[a-z0-9]+(?:_[a-z0-9]+)*)?$
```

**CODE-002**
Lifecycle prefixes MUST be one of:
`D`, `R`, `RE`, `C`, `O`, `F`.

**CODE-003**
Non-lifecycle prefixes (e.g., `INFO`, `SYS`) MAY be used only when `phase="none"`.

---

## 4. Canonical Event–Phase Enforcement Table

→ Rows are normative.

| Rule ID | event_type         | Required Phase                                     | Allowed Prefix Class | Enforcement |
| ------- | ------------------ | -------------------------------------------------- | -------------------- | ----------- |
| CAN-001 | drift_detected     | drift                                              | D                    | MUST        |
| CAN-002 | drift_escalated    | drift                                              | D                    | MUST        |
| CAN-003 | repair_triggered   | repair                                             | R                    | MUST        |
| CAN-004 | repair_escalated   | repair                                             | R                    | MUST        |
| CAN-005 | reentry_observed   | reentry                                            | RE                   | MUST        |
| CAN-006 | continue_allowed   | continue                                           | C                    | MUST        |
| CAN-007 | continue_blocked   | continue                                           | C                    | MUST        |
| CAN-008 | failover_triggered | failover                                           | F                    | MUST        |
| CAN-009 | evaluation_pass    | outcome                                            | O                    | SHOULD      |
| CAN-010 | evaluation_fail    | outcome                                            | O                    | SHOULD      |
| CAN-011 | session_closed     | outcome (default) OR none (explicit justification) | O or non-lifecycle   | SHOULD      |
| CAN-012 | info               | none                                               | non-lifecycle only   | SHOULD      |
| CAN-013 | latency_spike      | any                                                | any                  | MAY         |
| CAN-014 | pause_detected     | any                                                | any                  | MAY         |
| CAN-015 | handoff            | any                                                | any                  | MAY         |
| CAN-016 | fallback_executed  | repair or failover                                 | R or F               | MAY         |

---

## 5. Provisional Event Rules

→ Rules apply only when `taxonomy_status="provisional"` is present.

**PROV-001 — `D0_none`**

* SHOULD be accepted.
* MUST NOT override canonical drift logic.

**PROV-002 — `D9_unspecified`**

* SHOULD be accepted only as fallback.
* MUST include justification metadata.

**PROV-003 — `R5_hard_reset`**

* SHOULD remain valid.
* MUST retain R-phase mapping.

**PROV-004 — `C0_system_turn`, `C0_user_turn`**

* SHOULD remain accepted continuation classifiers.

**PROV-005 — analytics-linked identifiers (PRDR, VRL etc.)**

* MAY be stored.
* MUST NOT alter lifecycle classification.

---

## 6. Validation Modes

| Mode      | MUST-Violation Behavior                        | SHOULD-Violation Behavior | Use Case               |
| --------- | ---------------------------------------------- | ------------------------- | ---------------------- |
| strict    | reject                                         | ignore                    | ingestion + compliance |
| warn      | reject                                         | warn                      | staging                |
| normalize | auto-correct when deterministically resolvable | warn or accept            | adaptive runtimes      |

**VAL-001**
Normalization MUST NOT modify persisted logs.

---

## 7. Version Compatibility Rules

**VER-001**
Major version mismatch MUST result in rejection.

**VER-002**
Minor version differences SHOULD be accepted.

| schema_version | Result |
| -------------- | ------ |
| `"2.0"`        | accept |
| `"2.1"`        | accept |
| `"1.x"`        | reject |
| `"3.x"`        | reject |

---

## 8. Normative Examples (Minimal)

### Example A — Valid Lifecycle Event

```json
{
  "schema_version": "2.0",
  "event_id": "11111111-1111-4111-8111-111111111111",
  "timestamp": "2025-01-10T12:40:22Z",
  "session_id": "abcd",
  "turn_sequence": 1,
  "source": "detector",
  "event_type": "drift_detected",
  "pld": { "phase": "drift", "code": "D4_tool_error", "confidence": 0.91 },
  "ux": { "user_visible_state_change": false }
}
```

### Example B — Valid Non-Lifecycle Event

```json
{
  "schema_version": "2.0",
  "event_id": "22222222",
  "timestamp": "2025-01-10T12:41:00Z",
  "session_id": "abcd",
  "turn_sequence": 2,
  "source": "runtime",
  "event_type": "info",
  "pld": { "phase": "none", "code": "SYS_init" },
  "ux": { "user_visible_state_change": false }
}
```

---

## 9. Conformance Statement

A system claiming compliance with `PLD_Event_Semantic_Spec_v2.0` MUST:

* Enforce canonical mappings
* Treat provisional entries as allowed but marked
* Reject pending taxonomy items
* Apply validation mode rules consistently

---

**End of Specification**
