"""
Quickstart Minimal PLD Runtime Demo — Variant A
------------------------------------------------
This script demonstrates the minimal lifecycle:
  1. Create a RuntimeSignal
  2. Build a PLD event via RuntimeSignalBridge
  3. Emit it via a StructuredLogger using a stdout writer

This script is intentionally simple and non-authoritative.
It does NOT define new semantics — it only consumes the runtime.
"""

from pld_runtime.runtime_signal_bridge import (
    RuntimeSignalBridge,
    RuntimeSignal,
    EventContext,
    ValidationMode,
    SignalKind,
)
from pld_runtime.logging.structured_logger import StructuredLogger
from pld_runtime.logging.event_writer import make_stdout_writer


def main() -> None:
    # Step 1 — Create a RuntimeSignal
    signal = RuntimeSignal(kind=SignalKind.CONTINUE_SYSTEM_TURN)

    # Step 2 — Define runtime event context
    context = EventContext(
        session_id="demo-session-1",
        turn_sequence=1,
        source="runtime",
        model="example-model",
    )

    # Step 3 — Initialize the PLD RuntimeSignalBridge
    bridge = RuntimeSignalBridge(validation_mode=ValidationMode.STRICT)

    # Step 4 — Build the canonical PLD event
    event = bridge.build_event(signal=signal, context=context)

    # Step 5 — Emit event via StructuredLogger
    logger = StructuredLogger(writer=make_stdout_writer())
    logger.log(event)


if __name__ == "__main__":
    main()
