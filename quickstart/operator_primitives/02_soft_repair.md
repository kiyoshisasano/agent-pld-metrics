Status: Working Draft
Audience: Developers exploring PLD runtime behavior
Feedback: Welcome and encouraged

---

# Soft Repair — Operator Notes

This document is part of an ongoing exploration of runtime operator patterns. It does **not** introduce new PLD semantics or taxonomy. Instead, it aims to describe how "soft repair" can be understood and applied within existing runtime behavior.

The content may evolve as more implementation experience is collected.

---

## What Soft Repair Refers To

Soft repair can be considered a lightweight intervention used when the system experiences *minor drift* or uncertainty, but the interaction still feels recoverable without a restart or strong correction.

It sits between two extremes:

* continuing normally
* performing a hard reset or reentry flow

Soft repair may reflect attempts to:

* request clarification
* rewrite a response for accuracy or relevance
* adjust tone or interpretation
* refine assumptions based on new input

Some systems perform soft repair implicitly; others treat it as an observable event.

---

## When This Operator May Be Useful

Patterns where soft repair may help:

* the assistant continues correctly, but tone or specificity feels slightly off
* user intent was partially understood but requires refining
* previous output needs adjustment rather than replacement
* tool or reasoning step produced a usable but flawed result

These patterns are intentionally flexible — they may change with feedback and experimentation.

---

## Runtime Intent Mapping (Observed)

Soft repair aligns with several existing signal kinds. The following table reflects current runtime defaults (not new definitions):

| SignalKind                   | Event Type         | Phase    | Taxonomy Code              |
| ---------------------------- | ------------------ | -------- | -------------------------- |
| `CLARIFICATION`              | `repair_triggered` | `repair` | `R1_clarify`               |
| `SOFT_REPAIR`                | `repair_triggered` | `repair` | `R2_soft_repair`           |
| `REWRITE`                    | `repair_triggered` | `repair` | `R3_rewrite`               |
| `REQUEST_USER_CLARIFICATION` | `repair_triggered` | `repair` | `R4_request_clarification` |

As with drift detection, these codes are automatically resolved by the runtime using the PLD `RuntimeSignalBridge` mapping table.

---

## Example: Minimal Usage

*Not normative — only an example of how a soft repair event may be represented using existing runtime APIs.*

```python
from pld_runtime.runtime_signal_bridge import RuntimeSignal, RuntimeSignalBridge, EventContext, SignalKind, ValidationMode
from pld_runtime.logging.structured_logger import StructuredLogger
from pld_runtime.logging.event_writer import make_stdout_writer

logger = StructuredLogger(writer=make_stdout_writer())
bridge = RuntimeSignalBridge(validation_mode=ValidationMode.STRICT)

# Example soft repair signal
signal = RuntimeSignal(kind=SignalKind.REWRITE)

context = EventContext(
    session_id="example-session-2",
    turn_sequence=5,
    source="assistant",
    model="example-model",
)

event = bridge.build_event(signal=signal, context=context)
logger.log(event)
```

---

## Relation to Drift and Hard Repair

Soft repair does not require a preceding detected drift signal, although that may happen in some workflows. It may also precede or prevent:

* repeated drift events
* user-visible confusion
* escalation into a harder recovery strategy

In some cases, soft repair may be sufficient to bring the system back into alignment.

---

---

## Additional Notes on Event Type and Lifecycle Role

The `event_type="repair_triggered"` value is part of the PLD runtime schema and indicates the point at which the repair lifecycle begins. While taxonomy codes (such as `R1_clarify` or `R3_rewrite`) convey specific meaning, the event type provides a consistent classification boundary that may support filtering, routing, or downstream reasoning. These roles are complementary rather than redundant.

---

## How Soft Repair Signals Are Initiated

The runtime does not prescribe a single component responsible for generating soft repair signals. Implementations may explore different approaches. For example, a signal may be emitted by:

* a heuristic observer or monitoring layer,
* the model or assistant generating the response,
* or an external reasoning or evaluation component.

This flexibility is intentional and reflects ongoing exploration.

---

## A Note on `REQUEST_USER_CLARIFICATION`

Soft repair may involve both internal adjustments and lightweight interactive repairs. `REQUEST_USER_CLARIFICATION` reflects the latter case, where the model or system seeks a short user-visible correction rather than applying internal restructuring or resetting.

---

## Future Direction: Hard Repair

The distinction between soft and hard repair remains an open question. Whether future work introduces additional phases or continues refining taxonomy codes under the existing `repair` phase is still under consideration.

---

## Open Questions and Ongoing Exploration

Soft repair sits in a nuanced space, and the following areas may benefit from future refinement:

* When should soft repair be visible to the user (if at all)?
* Should repeated soft repairs escalate automatically to a hard repair pattern?
* How can tooling or heuristics detect the transition between "soft" and "hard" repair conditions?
* Are there useful counterexamples where soft repair makes outcomes worse?

These are left open intentionally.

---

## Feedback Notes

As with other operator notes in this series, this document remains iterative.
Feedback, examples, and real-world usage reports may inform future versions.
