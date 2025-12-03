# quickstart/easy_pld_demo.py

"""
easy_pld_demo.py

SimpleObserver quickstart examples:

1) Simple mode:
    observer = SimpleObserver("session-001")
    observer.log_turn("user", "Hello", "Hi there")

2) Advanced mode (with trace_turn):
    with observer.trace_turn("user", "Complex task") as turn:
        # ... do some work ...
        turn.complete("Done")

3) Optional detectors injection:
    observer = SimpleObserver("session-x", detectors=[keyword_detector])

Note:
    In this demo, detectors are executed synchronously when `trace_turn.complete()`
    is called, so the call will block until all detectors finish.
"""

from __future__ import annotations

from pld_runtime.ingestion.simple_observer import SimpleObserver
from pld_runtime.detection.drift_detector import DriftDetectorContext
from pld_runtime.detection.builtin_detectors import SimpleKeywordDetector


def simple_mode_demo() -> None:
    """1) Simple mode demo: one user turn, one system response."""
    observer = SimpleObserver("session-001")
    observer.log_turn("user", "Hello", "Hi there")


def advanced_mode_demo() -> None:
    """2) Advanced mode demo using with-traced turns."""
    observer = SimpleObserver("session-002")

    with observer.trace_turn("user", "Complex task") as turn:
        # In a real system, some work would be done here.
        # For demo purposes, we just synthesize a response.
        result = "Done"
        turn.complete(result)


def detectors_injection_demo() -> None:
    """3) Optional demo of injecting detectors into SimpleObserver."""
    # Single source of truth for the session id used by both observer and detector.
    session_id = "session-x"

    # Build a DriftDetectorContext for the SimpleKeywordDetector,
    # following the existing built-in detectors pattern.
    detector_ctx = DriftDetectorContext(
        session_id=session_id,
        source="detector",
        validation_mode="strict",
        model="example-model",
        tool_name="easy_pld_demo",
    )

    # SimpleKeywordDetector already matches the ObserverDetector protocol shape,
    # so we can pass it directly to SimpleObserver without any adapter.
    keyword_detector = SimpleKeywordDetector(
        detector_ctx,
        keywords=["forbidden", "NG"],
        code="D1_instruction",
    )

    # SimpleObserver runs detectors synchronously when trace_turn.complete() is called.
    observer = SimpleObserver(session_id, detectors=[keyword_detector])

    # Any text containing "forbidden" or "NG" will trigger a drift event
    # in addition to the continue_allowed event.
    with observer.trace_turn("user", "This contains a forbidden term") as turn:
        turn.complete("We noticed your term and handled it.")


def main() -> None:
    simple_mode_demo()
    advanced_mode_demo()
    detectors_injection_demo()


if __name__ == "__main__":
    main()
