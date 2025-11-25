"""
Quickstart Minimal Runtime Engine Loop — Variant A
-------------------------------------------------
This script demonstrates a tiny loop where runtime signals are turned
into PLD events and emitted through the runtime logging pipeline.

It shows:
  ✔ One bridge instance
  ✔ One logger instance
  ✔ A small list of runtime signals processed sequentially

This file is *non-authoritative* and serves only as a runnable demo.
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


def run_engine() -> None:
    # Initialize logging + runtime bridge
    bridge = RuntimeSignalBridge(validation_mode=ValidationMode.STRICT)
    logger = StructuredLogger(writer=make_stdout_writer())

    # Demo runtime signals processed in sequence
    signals = [
        SignalKind.CONTINUE_SYSTEM_TURN,
        SignalKind.INSTRUCTION_DRIFT,
        SignalKind.CLARIFICATION,
        SignalKind.REWRITE,
        SignalKind.SESSION_CLOSED,
    ]

    # Shared session context
    session_id = "demo-session-2"

    for turn_index, kind in enumerate(signals, start=1):
        signal = RuntimeSignal(kind=kind)

        context = EventContext(
            session_id=session_id,
            turn_sequence=turn_index,
            source="runtime",
            model="example-model",
        )

        # Build PLD event
        event = bridge.build_event(signal=signal, context=context)

        # Emit
        logger.log(event)

    print("\n[engine complete] — events written to stdout\n")


if __name__ == "__main__":
    run_engine()
