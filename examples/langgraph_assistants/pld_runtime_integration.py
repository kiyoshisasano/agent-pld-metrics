#!/usr/bin/env python
# component_id: langgraph_pld_bridge
# kind: example
# area: integration
# status: experimental
# authority_level: 2
# purpose: Observer-only bridge from LangGraph state into PLD runtime events (JSONL logging).

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import logging

from pld_runtime.runtime_signal_bridge import (
    RuntimeSignalBridge,
    RuntimeSignal,
    SignalKind,
    EventContext,
    ValidationMode,
)
from pld_runtime.logging.runtime_logging_pipeline import RuntimeLoggingPipeline
from pld_runtime.logging.exporters.exporter_jsonl import JsonlExporter

logger = logging.getLogger(__name__)

# Module-level singletons for the observer.
_bridge: Optional[RuntimeSignalBridge] = None
_logging_pipeline: Optional[RuntimeLoggingPipeline] = None


# ---------------------------------------------------------------------------
# Public initialization
# ---------------------------------------------------------------------------


def init_pld_observer(
    *,
    jsonl_path: str,
    validation_mode: str = "strict",
) -> None:
    """Initialize the PLD observer stack (bridge + logging pipeline).

    This MUST be called once from the application entry point (e.g., run.py)
    before any emit_* functions are used.

    - Creates parent directories for jsonl_path if needed.
    - Constructs a RuntimeSignalBridge with the requested ValidationMode.
    - Constructs a RuntimeLoggingPipeline with a JsonlExporter targeting jsonl_path.
    """
    global _bridge, _logging_pipeline

    if _bridge is not None and _logging_pipeline is not None:
        # Already initialized; be idempotent.
        logger.debug("PLD observer already initialized, skipping re-init")
        return

    path = Path(jsonl_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Map string -> ValidationMode enum safely.
    mode_normalized = (validation_mode or "strict").lower()
    if mode_normalized == "warn":
        vm = ValidationMode.WARN
    elif mode_normalized == "normalize":
        vm = ValidationMode.NORMALIZE
    else:
        vm = ValidationMode.STRICT

    _bridge = RuntimeSignalBridge(validation_mode=vm)

    exporter = JsonlExporter(path=path)
    _logging_pipeline = RuntimeLoggingPipeline(jsonl_exporter=exporter)

    logger.info(
        "Initialized PLD observer: validation_mode=%s, jsonl_path=%s",
        vm.value,
        str(path),
    )


# ---------------------------------------------------------------------------
# Public emit functions (observer-only)
# ---------------------------------------------------------------------------


def emit_continue_event(state: Dict[str, Any]) -> None:
    """Emit a 'continue' PLD event for a nominal assistant turn (observer-only)."""

    _emit_signal(
        state=state,
        kind=SignalKind.CONTINUE_NORMAL,
        current_phase="continue",
        payload={},
    )


def emit_tool_error(state: Dict[str, Any], reason: str) -> None:
    """Emit a 'tool_error' drift event (simple observer for failures)."""

    _emit_signal(
        state=state,
        kind=SignalKind.TOOL_ERROR,
        current_phase="drift",
        payload={"reason": reason},
    )


def emit_session_closed(state: Dict[str, Any]) -> None:
    """Emit a 'session_closed' outcome event when the conversation ends."""

    _emit_signal(
        state=state,
        kind=SignalKind.SESSION_CLOSED,
        current_phase="outcome",
        payload={},
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _ensure_initialized() -> bool:
    """Check whether the observer stack is initialized.

    Returns:
        True if initialized, False otherwise.

    This function is deliberately non-fatal: if the observer has not been
    initialized, we log a warning and return False. The caller can treat this
    as a no-op, preserving the LangGraph agent behavior.
    """
    if _bridge is None or _logging_pipeline is None:
        logger.warning(
            "PLD observer has not been initialized. "
            "Call init_pld_observer(...) before emitting events."
        )
        return False
    return True


def _emit_signal(
    *,
    state: Dict[str, Any],
    kind: SignalKind,
    current_phase: str,
    payload: Optional[Dict[str, Any]] = None,
) -> None:
    """Common logic for emitting PLD events from a LangGraph state.

    Responsibilities:
    - Extract session_id, turn, model from the LangGraph state.
    - Construct RuntimeSignal and EventContext.
    - Use RuntimeSignalBridge.build_event(...) to obtain a PLD-compliant event dict.
    - Forward that event dict to the RuntimeLoggingPipeline.

    Constraints:
    - PLD event dicts are NEVER manually constructed here.
    - After build_event(...), the event dict is treated as immutable and
      passed through without mutation.
    """

    if not _ensure_initialized():
        return

    assert _bridge is not None
    assert _logging_pipeline is not None

    try:
        session_id = state["session_id"]
        turn_sequence = state["turn"]
        model = state.get("model")
    except KeyError as exc:
        logger.warning(
            "Missing required key in state for PLD emission (%s). "
            "Skipping PLD event.", exc
        )
        return

    if not isinstance(turn_sequence, int) or turn_sequence < 1:
        logger.warning(
            "Invalid turn_sequence in state: %r (must be 1-based integer). "
            "Skipping PLD event.",
            turn_sequence,
        )
        return

    signal = RuntimeSignal(
        kind=kind,
        payload=payload or {},
    )

    context = EventContext(
        session_id=session_id,
        turn_sequence=turn_sequence,
        source="runtime",
        model=model,
        current_phase=current_phase,
    )

    try:
        # Build PLD-compliant event dict via Level 5 API.
        event = _bridge.build_event(signal=signal, context=context)

        # IMPORTANT: event is treated as immutable after this point.
        _logging_pipeline.on_event(event)

    except Exception:
        # Observer failures must NOT break the main LangGraph flow.
        logger.exception("Failed to emit PLD event for signal kind=%s", kind)
