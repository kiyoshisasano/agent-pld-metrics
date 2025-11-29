<!--
path: quickstart/operator_primitives/01_detect_drift.md
component_id: detect_drift_operator
kind: doc
area: runtime_operators
status: candidate
authority_level: 2
version: 2.0.0
license: CC-BY-4.0
purpose: Exploratory operator notes describing drift detection patterns in PLD runtime contexts.
-->

# Detecting Drift — Operator Notes

This document is an exploratory write-up on how "drift detection" may be understood when working with the PLD runtime. It does not define new semantics or taxonomy. Instead, it attempts to describe how the existing runtime pieces can be used in situations where the assistant or system appears misaligned with expected conversational intent or trajectory.

Interpretation and refinement are ongoing.

---

## Why Drift Detection Exists

In multi‑turn interaction, systems occasionally deviate from the intended task or user objective. "Drift" here refers to such divergence. It may present as repetition, confusion, incorrect assumptions, or operating on outdated information.

Detecting drift early may support:

* smoother recovery
* improved user experience
* more stable downstream state

At this stage, drift should be interpreted as a *signal*, not a failure.

---

## When This Operator May Be Useful

Drift detection can be relevant when:

* user intent appears unclear or has shifted
* responses become repetitive or circular
* a tool fails or produces unreliable output
* the assistant begins to respond based on outdated context

These patterns are not deterministic – implementation feedback may refine them.

---

## Runtime Intent Mapping (Observed)

The PLD runtime already provides mapping for drift‑related signals.
These are **not new definitions** — just a summary of existing values for convenience.

| SignalKind          | Event Type       | Phase   | Taxonomy Code      |
| ------------------- | ---------------- | ------- | ------------------ |
| `INSTRUCTION_DRIFT` | `drift_detected` | `drift` | `D1_instruction`   |
| `CONTEXT_DRIFT`     | `drift_detected` | `drift` | `D2_context`       |
| `REPEATED_PLAN`     | `drift_detected` | `drift` | `D3_repeated_plan` |
| `TOOL_ERROR`        | `drift_detected` | `drift` | `D4_tool_error`    |

This table mirrors existing runtime semantics.

---

## Example: Minimal Usage

*Not prescriptive — shown only to illustrate the operator in context.*

```python
from pld_runtime.runtime_signal_bridge import RuntimeSignal, RuntimeSignalBridge, EventContext, SignalKind, ValidationMode
from pld_runtime.logging.structured_logger import StructuredLogger
from pld_runtime.logging.event_writer import make_stdout_writer

# Logger and bridge setup
logger = StructuredLogger(writer=make_stdout_writer())
bridge = RuntimeSignalBridge(validation_mode=ValidationMode.STRICT)

# Example runtime observation indicating drift
signal = RuntimeSignal(kind=SignalKind.INSTRUCTION_DRIFT)

context = EventContext(
    session_id="example-session-1",
    turn_sequence=3,
    source="runtime",
    model="example-model",
)

event = bridge.build_event(signal=signal, context=context)
logger.log(event)
```

---

## Things Still Under Exploration

Some open questions worth revisiting as experience grows:

* What degree of deviation meaningfully counts as "drift"?
* Should drift detection sometimes be user‑visible?
* How frequently does early detection prevent downstream repair complexity?
* How can detection be distinguished from natural ambiguity or creative reasoning?

These questions are intentionally left open.

---

## Clarifying How Mapping Works

The taxonomy codes shown in the table above (such as `D1_instruction` or `D2_context`) are **not authored manually** during runtime usage. They are assigned automatically by the runtime through the mapping table defined in the PLD runtime (`RUNTIME_SIGNAL_MAP`).

Users typically only provide the `RuntimeSignal(kind=...)` value. The runtime then resolves the appropriate taxonomy code when building the final event via `RuntimeSignalBridge.build_event()`.

---

## Where Drift Signals Come From

At this stage, PLD does not prescribe a single mechanism for when or how drift signals should be emitted. They may originate from:

* a heuristic observer or monitoring layer
* the assistant logic itself
* a tool or external validation component

This remains flexible by design and may evolve through experimentation.

---

## Scope of This Operator

This document does **not** define a complete drift detection framework. Instead, it describes how drift, once detected, can be represented using the existing PLD runtime.

The runtime treats all drift-related events under the single lifecycle phase value `"drift"`. Any finer-grained meaning is expressed through taxonomy codes rather than expanding the phase enumeration.

---

## Feedback and Iteration Notes

Future revisions may:

* clarify boundaries between drift and repair phases
* include additional examples or counterexamples
* refine or expand usage guidance based on implementation outcomes

Feedback from experimentation or review is welcome.
