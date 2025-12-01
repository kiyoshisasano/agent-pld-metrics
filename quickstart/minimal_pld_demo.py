# component_id: minimal_pld_demo
# kind: example
# area: quickstart
# status: experimental
# authority_level: 1
# version: 2.0.0
# license: Apache-2.0
# purpose: End-to-end quickstart demonstration that turns a scripted flow of RuntimeSignals into PLD v2-compliant events and writes them to stdout via StructuredLogger.

"""
Minimal PLD Runtime Demonstration — Variant B
---------------------------------------------
This demonstration shows the full quickstart usage pattern:

    1. Construct runtime signals
    2. Convert them into PLD-compliant events using RuntimeSignalBridge
    3. Emit events via StructuredLogger (stdout)

This example remains **consumer-only**:
- No manual construction of PLD event dictionaries
- No schema modification
- No taxonomy modification

The goal is to provide a clean, runnable introduction.
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


# ---------------------------------------------------------------------------
# Example: Minimal processing of multiple signals
# ---------------------------------------------------------------------------

def demo() -> None:
    logger = StructuredLogger(writer=make_stdout_writer())
    bridge = RuntimeSignalBridge(validation_mode=ValidationMode.STRICT)

    # A short scripted flow
    scripted_signals = [
        SignalKind.CONTINUE_USER_TURN,
        SignalKind.INSTRUCTION_DRIFT,
        SignalKind.CLARIFICATION,
        SignalKind.REWRITE,
        SignalKind.CONTINUE_SYSTEM_TURN,
        SignalKind.SESSION_CLOSED,
    ]

    session = "demo-session-3"

    for turn, kind in enumerate(scripted_signals, start=1):
        signal = RuntimeSignal(kind=kind)

        ctx = EventContext(
            session_id=session,
            turn_sequence=turn,
            source="runtime",
            model="demo-model",
        )

        event = bridge.build_event(signal=signal, context=ctx)
        logger.log(event)

    print("\n[demo complete] — PLD events emitted to stdout\n")


# ---------------------------------------------------------------------------
# Script Entry
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    demo()
