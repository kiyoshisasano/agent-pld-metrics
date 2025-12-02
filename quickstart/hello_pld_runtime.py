# component_id: hello_pld_runtime
# kind: example
# area: quickstart
# status: experimental
# authority_level: 1
# version: 2.0.0
# license: Apache-2.0
# purpose: Minimal quickstart script that builds PLD v2-compliant events via Level 5 runtime
#          components and emits them using the logging pipeline.

"""
Quickstart PLD Runtime Demo — Bridge + Built-in Drift Detector
--------------------------------------------------------------

This script demonstrates two minimal flows:

  1. RuntimeSignalBridge path (canonical hello world)
     - Create a RuntimeSignal
     - Build a PLD event via RuntimeSignalBridge
     - Emit it via a StructuredLogger using a stdout writer

  2. Built-in drift detector path (schema compliance example)
     - Use SchemaComplianceDetector to check required keys in a dict
     - Missing `"parking"` triggers a drift event (D*-family code)
     - Emit the resulting PLD event via the same logging pipeline

This script is intentionally simple and non-authoritative.
It does NOT define new semantics — it only consumes the runtime.
"""

from pld_runtime.detection.runtime_signal_bridge import (
    RuntimeSignalBridge,
    RuntimeSignal,
    EventContext,
    ValidationMode,
    SignalKind,
)
from pld_runtime.logging.structured_logger import StructuredLogger
from pld_runtime.logging.event_writer import make_stdout_writer
from pld_runtime.detection.drift_detector import DriftDetectorContext
from pld_runtime.detection.builtin_detectors import SchemaComplianceDetector


def run_bridge_hello(logger: StructuredLogger) -> None:
    """
    Demo 1 — Canonical RuntimeSignalBridge hello world.

    Builds a single continue_allowed event via RuntimeSignalBridge and
    emits it through the StructuredLogger.
    """
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
    logger.log(event)


def run_schema_compliance_demo(logger: StructuredLogger) -> None:
    """
    Demo 2 — SchemaComplianceDetector-based drift detection.

    Scenario:
      - We expect a dict payload to include a required key "parking".
      - The example payload intentionally omits "parking".
      - The SchemaComplianceDetector treats the missing key as context drift
        and emits a PLD drift_detected event.

    The resulting event:
      - Uses a D*-family taxonomy code (default: D2_context).
      - Is constructed by the Level 5 detector template, not by this script.
    """
    # Detector context for this session.
    detector_ctx = DriftDetectorContext(
        session_id="demo-session-1",
        source="detector",
        validation_mode="strict",
        model="example-model",
        tool_name="hello_pld_runtime",
    )

    # Require "parking" to be present; its absence will be treated as drift.
    detector = SchemaComplianceDetector(
        detector_ctx,
        required_keys=["parking"],
        # Default code is "D2_context"; it remains in the D* family as required.
    )

    # Example payload missing the required "parking" key.
    location_payload = {
        "address": "Tokyo",
        # "parking": False,  # Intentionally omitted to trigger drift.
    }

    drift_event = detector.detect_dict(
        data=location_payload,
        turn_sequence=2,
        user_visible_state_change=False,
    )

    # When all required keys are present, detect_dict returns None.
    if drift_event is not None:
        # The event dict is built by Level 5 runtime code and treated as immutable here.
        logger.log(drift_event)


def main() -> None:
    # Shared logger for both demos, writing JSONL to stdout.
    logger = StructuredLogger(writer=make_stdout_writer())

    # 1) Canonical RuntimeSignalBridge hello world.
    run_bridge_hello(logger)

    # 2) Built-in drift detector demo (missing "parking" key).
    run_schema_compliance_demo(logger)


if __name__ == "__main__":
    main()
