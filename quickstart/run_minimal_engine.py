# component_id: run_minimal_engine
# kind: example
# area: quickstart
# status: experimental
# authority_level: 1
# version: 2.0.0
# license: Apache-2.0
# purpose: Minimal engine loop that processes a small sequence of RuntimeSignals into PLD v2-compliant events and emits them through the Level 5 logging stack.

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
