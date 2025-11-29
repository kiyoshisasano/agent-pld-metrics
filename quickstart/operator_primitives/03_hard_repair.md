<!--
path: quickstart/operator_primitives/03_hard_repair.md
component_id: hard_repair_operator
kind: doc
area: runtime_operators
status: candidate
authority_level: 2
version: 2.0.0
license: CC-BY-4.0
purpose: Notes defining exploratory framing for structural reset conditions and escalation boundaries.
-->

# Hard Repair — Operator Notes

This document is part of the ongoing operator exploration series. It does **not** define new PLD semantics or modify existing taxonomy. Instead, it attempts to describe how "hard repair" can be conceptually understood and represented using the current runtime system.

The framing may evolve as more implementation experience becomes available.

---

## What Hard Repair Refers To

Hard repair represents a stronger corrective action than soft repair. It may be used when:

* the system has drifted substantially from the intended task
* repeated soft repair attempts have not resolved misalignment
* the conversation requires structural reset or reframing
* the assistant’s internal assumptions are no longer reliable

Hard repair is not necessarily a failure state — it can be a recovery strategy.

---

## Examples of Situations That May Lead to Hard Repair

These patterns are not prescriptive, but may serve as reference points:

* the assistant repeatedly answers a different question than the one asked
* tool reasoning or state becomes corrupted or contradictory
* context window references outdated or inconsistent assumptions
* partial recovery attempts lead to further confusion

Some systems may trigger hard repair proactively; others only after a threshold of uncertainty or repair churn.

---

---

## Notes on Signal Source

In the example earlier in this document, `source="runtime"` is used as a neutral placeholder.
This is not intended to prescribe a single responsible component.

Depending on implementation architecture, a hard repair signal may come from:

* a monitoring or observer component,
* a system-level controller or repair manager,
* the assistant or reasoning engine itself.

The PLD runtime does not define the origin boundaries, and this remains an area where implementations may diverge.

---

## Runtime Intent Mapping (Observed)

Hard repair currently aligns with the following runtime signal:

| SignalKind   | Event Type         | Phase    | Taxonomy Code   |
| ------------ | ------------------ | -------- | --------------- |
| `HARD_RESET` | `repair_triggered` | `repair` | `R5_hard_reset` |

As with earlier operators, taxonomy codes are resolved automatically by the PLD runtime via the `RuntimeSignalBridge` mapping table.

---

## Example: Minimal Usage

*Not normative — shown only as a representation pattern.*

```python
from pld_runtime.runtime_signal_bridge import (
    RuntimeSignal, RuntimeSignalBridge, EventContext, SignalKind, ValidationMode
)
from pld_runtime.logging.structured_logger import StructuredLogger
from pld_runtime.logging.event_writer import make_stdout_writer

logger = StructuredLogger(writer=make_stdout_writer())
bridge = RuntimeSignalBridge(validation_mode=ValidationMode.STRICT)

signal = RuntimeSignal(kind=SignalKind.HARD_RESET)

context = EventContext(
    session_id="example-session-3",
    turn_sequence=8,
    source="runtime",
    model="example-model",
)

event = bridge.build_event(signal=signal, context=context)
logger.log(event)
```

---

## How Hard Repair Relates to Soft Repair and Drift

A possible conceptual sequence may look like:

```
Drift detected → soft repair attempts → persistent misalignment → hard repair
```

Hard repair is typically a **pivot point**: it represents a structural checkpoint rather than incremental adjustment.

However, the runtime does not require this ordering — implementations may emit hard repair signals directly.

---

---

## Future Evolution

At present, the mapping includes a single hard repair taxonomy code.
This should not be interpreted as final — additional structural repair types may emerge over time.
If they do, they would likely appear as additional `SignalKind` entries under the existing `repair` phase rather than requiring new lifecycle phases.

---

## Implementation Boundary

This document does not define how a system must respond to a hard repair signal.
Whether the system resets context fully, partially, or chooses another recovery strategy is implementation-dependent.

---

## Unresolved Questions and Open Exploration

Some areas may benefit from later clarification or real-world usage patterns:

* Should hard repair revert or discard prior conversational context?
* Is user-visible acknowledgment expected or optional?
* Are there thresholds or heuristics that determine escalation from soft to hard repair?
* Should future iterations introduce extended categories or phases for repair severity?

No conclusion is assumed at this stage.

---

## Feedback Notes

As with the rest of this series, this document is exploratory.
Feedback and implementation examples may guide future refinement.
