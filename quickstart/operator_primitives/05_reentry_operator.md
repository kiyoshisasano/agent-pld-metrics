<!--
path: quickstart/operator_primitives/05_reentry_operator.md
component_id: reentry_operator
kind: doc
area: runtime_operators
status: candidate
authority_level: 2
version: 2.0.0
license: CC-BY-4.0
purpose: Exploratory framing for stabilization transitions following repair sequences.
-->

# Reentry Operator — Stabilization Notes

This document completes the current operator exploration series.
It does **not** define new lifecycle semantics or taxonomy values.
Instead, it describes how "reentry" can be interpreted in the context of the PLD runtime.

Reentry reflects the moment when the system attempts to return from a disrupted or uncertain state into a stable conversational flow.

Interpretation and refinement are ongoing.

---

## What Reentry Represents

Reentry can be seen as the *transition point* after drift or repair work has occurred, where the system attempts to resume normal interaction.

It does not imply that the conversation resets or that the past context is invalid.
Instead, reentry suggests:

* enough stabilization has occurred,
* the previous uncertainty or misalignment has been resolved or reduced,
* the assistant can continue in a forward, productive manner.

---

## When This Operator May Be Relevant

Reentry signals can be useful in situations such as:

* following a soft or hard repair event
* after a clarification step completes
* when a new plan or corrected assumption replaces an earlier incorrect one
* when the model returns to a coherent state after interruption or confusion

The boundary between repair and reentry may be ambiguous — this document does not attempt to formalize it.

---

## Runtime Intent Mapping (Observed)

The runtime schema reserves a lifecycle phase for reentry and an event type for reentry observation. A typical interpretation is:

| Event Type         | Phase     | Example Taxonomy Code |
| ------------------ | --------- | --------------------- |
| `reentry_observed` | `reentry` | `RE1_reentry`         |

This table mirrors the existing event matrix and taxonomy; it does **not** introduce new SignalKind values. In many implementations, reentry events may be produced by higher-level controllers or orchestration logic rather than directly from the quickstart-level signal mapping.

Taxonomy codes are assigned automatically at event construction time by the runtime or associated controllers; quickstart examples are consumers of those events rather than their definitive source.

---

## Example: Minimal Usage (Conceptual)

*Not normative — shown as a conceptual representation rather than a guaranteed API surface.*

```python
from pld_runtime.runtime_signal_bridge import (
    RuntimeSignal, RuntimeSignalBridge, EventContext, SignalKind, ValidationMode
)
from pld_runtime.logging.structured_logger import StructuredLogger
from pld_runtime.logging.event_writer import make_stdout_writer

logger = StructuredLogger(writer=make_stdout_writer())
bridge = RuntimeSignalBridge(validation_mode=ValidationMode.STRICT)

# NOTE:
# As of the current runtime version, reentry events may be emitted by
# higher-level controllers rather than a dedicated SignalKind. This
# example illustrates the *shape* of such a flow only.

signal = RuntimeSignal(kind=SignalKind.INFO)  # placeholder for a future or controller-specific signal

context = EventContext(
    session_id="example-session-5",
    turn_sequence=12,
    source="assistant",
    model="example-model",
)

event = bridge.build_event(signal=signal, context=context)
logger.log(event)
```

```

---

---

## Source of Reentry Decisions

In the example above, `source="assistant"` is used to reflect a scenario where the model or assistant logic judges that the interaction is ready to resume normal flow.

The runtime does not require that reentry decisions come from the assistant itself. Depending on architecture, reentry may be:
- inferred by a controller or coordinator,
- emitted by a monitoring or evaluation component,
- or represented indirectly by other event patterns.

Implementations are free to route reentry-related signals through whichever component owns conversation control.

---

## Relationship to Repair, Drift, and Normal Operation

A loose representation of reentry may look like:

```

(repair or clarification) → reentry → continuation

```

Reentry is not a confirmation of success — it is a **transition attempt**.

Current PLD semantics do not define an explicit "repair complete" signal. In practice, reentry is often interpreted as "the system believes repair has reached a good-enough point to attempt continuation", but the exact boundary between repair and reentry remains implementation-dependent. This operator note does not introduce new SignalKind values such as `REPAIR_COMPLETE`; instead, it documents how a reentry phase can be interpreted when such events appear in the log stream.  
Systems may return to repair or drift if inconsistencies reappear.

Reentry events are best treated as markers in the event stream rather than exclusive turn owners. The runtime does not guarantee that no other lifecycle events (for example, `continue_*` or outcome-related events) will occur near the same turn. Implementations may choose to emit reentry events just before, with, or immediately after other events that reflect ongoing conversation progress.

In this sense, reentry can be seen as:
- an optimistic pivot back to progress,  
- a checkpoint, rather than a guarantee.

---

## Open Exploration Areas

Some open areas worth documenting for future consideration:
- Should reentry be explicit or implicit when repair completes successfully?
- How many reentry attempts are reasonable before reconsidering the repair stage?
- Should user-visible acknowledgments exist to signal stabilization?
- Do reentry strategies differ between tool-driven workflows and pure conversational models?

No assumptions are made here — these are open design questions.

---

## Feedback Notes

This document, like the rest of the series, is exploratory.  
Future revisions may clarify sequencing, examples, or distinctions based on usage feedback.

```
