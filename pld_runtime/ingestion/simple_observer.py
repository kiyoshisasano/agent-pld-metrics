# component_id: simple_observer
# kind: runtime_module
# area: ingestion
# status: experimental
# authority_level: 5
# version: 2.0.0
# license: Apache-2.0
# purpose: High-level facade over RuntimeSignalBridge and StructuredLogger that auto-builds PLD v2-compliant events, manages turn sequencing, latency measurement, and optional detector execution.

# pld_runtime/ingestion/simple_observer.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Protocol

from pld_runtime.detection.runtime_signal_bridge import (
    RuntimeSignalBridge,
    RuntimeSignal,
    EventContext,
    ValidationMode,
    SignalKind,
)
from pld_runtime.logging.structured_logger import StructuredLogger
from pld_runtime.logging.event_writer import EventWriter, make_stdout_writer


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _to_utc_iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class ObserverDetector(Protocol):
    """Duck-typed detector interface for SimpleObserver.

    Detectors MAY conform to this protocol. If they do, SimpleObserver
    will call `detect_and_build_event` and expect a PLD event dict or None.

    IMPORTANT:
        - The returned dict is assumed to be PLD-valid (schema + semantics)
          and is NOT re-validated by SimpleObserver.
        - Built-in detectors are expected to construct events via Level 5
          templates that already enforce Level 1–3 constraints.
    """

    def detect_and_build_event(
        self,
        *,
        text: str,
        turn_sequence: int,
        user_visible_state_change: bool = False,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        ...


@dataclass
class _TurnContext:
    """Internal context object used inside `with observer.trace_turn(...)`.

    A _TurnContext represents ONE logical conversational turn. All events
    emitted for this turn (continue, drift annotations, errors) share the
    same `turn_sequence` value.
    """

    observer: "SimpleObserver"
    role: str
    text: str
    turn_sequence: int

    _start: Optional[datetime] = None
    _completed: bool = False

    def __enter__(self) -> "_TurnContext":
        self._start = _utc_now()
        return self

    def complete(
        self,
        response: str,
        *,
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Mark the turn as complete and emit a continue_allowed event.

        This method is idempotent; calling it multiple times has no effect
        after the first successful completion.
        """
        if self._completed:
            return

        if self._start is None:
            # Should not happen in normal usage, but guard for safety.
            self._start = _utc_now()

        end = _utc_now()
        latency_ms = (end - self._start).total_seconds() * 1000.0

        self.observer._emit_continue_with_latency(
            role=self.role,
            text=self.text,
            response=response,
            latency_ms=latency_ms,
            end_timestamp=end,
            payload=payload,
            turn_sequence=self.turn_sequence,
        )
        self._completed = True

    def __exit__(self, exc_type, exc, tb) -> None:
        """On exception, optionally emit a TOOL_ERROR event for this turn.

        - If no exception -> do nothing (complete() is explicit).
        - If exception and the turn was never completed:
            - emit a D4_tool_error drift event (SignalKind.TOOL_ERROR)
            - preserve the original exception (return False)
        """
        if exc_type is not None and not self._completed and self.observer._record_exceptions:
            self.observer._emit_turn_exception(
                turn_sequence=self.turn_sequence,
                role=self.role,
                text=self.text,
                start=self._start,
                exc=exc,
            )

        # Returning False propagates the exception.
        return False


class SimpleObserver:
    """High-level facade over RuntimeSignalBridge + StructuredLogger.

    Responsibilities:
        - Manage session_id and turn_sequence (conversation turn id).
        - Build PLD events via RuntimeSignalBridge in STRICT mode.
        - Emit events via StructuredLogger (stdout or injected writer).
        - Provide ergonomic helpers:
            - trace_turn(...) with latency measurement
            - observe_drift/observe_repair(...)
            - log_turn(...)

    Semantics:
        - `turn_sequence` is treated as a logical conversation turn id.
          All events emitted for a given turn share the same `turn_sequence`.
        - `observe_drift/observe_repair` treat each call as its own turn.

    Concurrency:
        - SimpleObserver is intended for single-threaded / per-session use.
          If you need to handle multiple concurrent sessions, create a
          separate SimpleObserver instance per session.

    This component operates at Level 5 only and MUST NOT:
        - Modify Level 1–3 specifications.
        - Introduce new event_type values or taxonomy prefixes.
    """

    def __init__(
        self,
        session_id: str,
        *,
        source: str = "runtime",
        model: Optional[str] = None,
        tool: Optional[str] = None,
        detectors: Optional[Iterable[ObserverDetector]] = None,
        writer: Optional[EventWriter] = None,
        record_exceptions: bool = True,
    ) -> None:
        if not isinstance(session_id, str) or not session_id:
            raise ValueError("session_id must be a non-empty string")

        self._session_id = session_id
        self._source = source
        self._model = model
        self._tool = tool

        # Level 5 bridge in STRICT mode (recommended).
        self._bridge = RuntimeSignalBridge(validation_mode=ValidationMode.STRICT)

        # Structured logger with pluggable writer (stdout by default).
        if writer is None:
            writer = make_stdout_writer()
        self._logger = StructuredLogger(writer=writer)

        self._turn_sequence: int = 0
        self._detectors: List[ObserverDetector] = list(detectors or [])
        self._record_exceptions: bool = bool(record_exceptions)

    # ------------------------------------------------------------------ #
    # Public API                                                         #
    # ------------------------------------------------------------------ #

    @property
    def session_id(self) -> str:
        return self._session_id

    def trace_turn(self, role: str, text: str) -> _TurnContext:
        """Create a traced turn context.

        Typical usage:

            with observer.trace_turn("user", "Complex task") as turn:
                # ... work ...
                turn.complete("Done")

        - Allocates a new logical turn_sequence for this block.
        - Records start timestamp on __enter__.
        - On complete(), measures latency and emits:
            - continue_allowed event (via RuntimeSignalBridge)
            - optional drift events via detectors
        - On exception (and no complete()), optionally emits a TOOL_ERROR
          drift event bound to the same turn_sequence.
        """
        turn_sequence = self._allocate_turn_sequence()
        return _TurnContext(
            observer=self,
            role=role,
            text=text,
            turn_sequence=turn_sequence,
        )

    def log_turn(self, role: str, text: str, response: str) -> None:
        """Log a single '1 user utterance → 1 system response' turn.

        This is a simplified variant:
            - Allocates a new turn_sequence.
            - Emits a continue_allowed event.
            - Does NOT measure or record latency.
            - Does NOT run detectors.
        """
        turn_sequence = self._allocate_turn_sequence()
        self._emit_continue_with_latency(
            role=role,
            text=text,
            response=response,
            latency_ms=None,
            end_timestamp=None,
            payload=None,
            turn_sequence=turn_sequence,
            run_detectors=False,
        )

    def observe_drift(
        self,
        code: str,
        payload: Optional[Dict[str, Any]] = None,
        *,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Manually record a drift event for convenience.

        This helper:
            - Treats the call as its own logical turn (new turn_sequence).
            - Maps the requested `code` into an existing drift SignalKind.
            - Emits a PLD event via RuntimeSignalBridge.
            - Stores the requested code under pld.metadata["requested_code"]
              (taxonomy authority remains Level 3).

        NOTE:
            - This method does NOT invent new taxonomy codes.
            - The canonical pld.code still comes from RuntimeSignalBridge's mapping.
        """
        kind = self._select_drift_signal_kind(code)
        meta = dict(metadata or {})
        if code:
            meta.setdefault("requested_code", code)

        signal = RuntimeSignal(
            kind=kind,
            payload=payload or {},
            metadata=meta,
        )

        turn_sequence = self._allocate_turn_sequence()
        self._emit_signal(
            signal=signal,
            turn_sequence=turn_sequence,
            current_phase="drift",
        )

    def observe_repair(
        self,
        code: str,
        payload: Optional[Dict[str, Any]] = None,
        *,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Manually record a repair event for convenience.

        Behavior is analogous to observe_drift, but uses R* repair codes.
        The canonical pld.code is provided by RuntimeSignalBridge; `code`
        is recorded as advisory metadata.
        """
        kind = self._select_repair_signal_kind(code)
        meta = dict(metadata or {})
        if code:
            meta.setdefault("requested_code", code)

        signal = RuntimeSignal(
            kind=kind,
            payload=payload or {},
            metadata=meta,
        )

        turn_sequence = self._allocate_turn_sequence()
        self._emit_signal(
            signal=signal,
            turn_sequence=turn_sequence,
            current_phase="repair",
        )

    # ------------------------------------------------------------------ #
    # Internal helpers                                                   #
    # ------------------------------------------------------------------ #

    def _allocate_turn_sequence(self) -> int:
        """Allocate a new logical turn_sequence (monotonic 1-based)."""
        self._turn_sequence += 1
        return self._turn_sequence

    def _emit_signal(
        self,
        *,
        signal: RuntimeSignal,
        turn_sequence: int,
        current_phase: Optional[str] = None,
        extra_runtime_fields: Optional[Dict[str, Any]] = None,
        timestamp_override: Optional[str] = None,
        user_visible_state_change: bool = False,
    ) -> None:
        """Emit a single PLD event via RuntimeSignalBridge + StructuredLogger."""
        context = EventContext(
            session_id=self._session_id,
            turn_sequence=turn_sequence,
            source=self._source,
            model=self._model,
            tool=self._tool,
            current_phase=current_phase,
        )

        event = self._bridge.build_event(
            signal=signal,
            context=context,
            user_visible_state_change=user_visible_state_change,
            timestamp_override=timestamp_override,
            extra_runtime_fields=extra_runtime_fields,
        )

        # Events produced by RuntimeSignalBridge are treated as immutable.
        self._logger.log(event)

    def _emit_continue_with_latency(
        self,
        *,
        role: str,
        text: str,
        response: str,
        latency_ms: Optional[float],
        end_timestamp: Optional[datetime],
        payload: Optional[Dict[str, Any]],
        turn_sequence: int,
        run_detectors: bool = True,
    ) -> None:
        """Emit a continue_allowed event and optionally run detectors."""
        if role.lower() == "user":
            kind = SignalKind.CONTINUE_USER_TURN
        else:
            # Default to system turn for anything non-user.
            kind = SignalKind.CONTINUE_SYSTEM_TURN

        base_payload: Dict[str, Any] = {
            "role": role,
            "request": text,
            "response": response,
        }
        if payload:
            # User payload keys override base payload keys.
            base_payload.update(payload)

        extra_runtime: Dict[str, Any] = {}
        if latency_ms is not None:
            extra_runtime["latency_ms"] = latency_ms

        ts_override = _to_utc_iso(end_timestamp) if end_timestamp is not None else None

        signal = RuntimeSignal(
            kind=kind,
            payload=base_payload,
        )

        # Emit primary continue_allowed event
        self._emit_signal(
            signal=signal,
            turn_sequence=turn_sequence,
            current_phase="continue",
            extra_runtime_fields=extra_runtime or None,
            timestamp_override=ts_override,
            user_visible_state_change=True,
        )

        # Run detectors only when explicitly requested (trace_turn path).
        if run_detectors:
            self._run_detectors_for_text(
                text=text,
                response=response,
                base_payload=base_payload,
                turn_sequence=turn_sequence,
            )

    def _emit_turn_exception(
        self,
        *,
        turn_sequence: int,
        role: str,
        text: str,
        start: Optional[datetime],
        exc: BaseException,
    ) -> None:
        """Emit a TOOL_ERROR drift event when a traced turn fails with an exception."""
        end = _utc_now()
        latency_ms: Optional[float] = None
        if start is not None:
            latency_ms = (end - start).total_seconds() * 1000.0

        payload: Dict[str, Any] = {
            "role": role,
            "request": text,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
        }

        extra_runtime: Dict[str, Any] = {}
        if latency_ms is not None:
            extra_runtime["latency_ms"] = latency_ms

        signal = RuntimeSignal(
            kind=SignalKind.TOOL_ERROR,
            payload=payload,
        )

        self._emit_signal(
            signal=signal,
            turn_sequence=turn_sequence,
            current_phase="drift",
            extra_runtime_fields=extra_runtime or None,
            timestamp_override=_to_utc_iso(end),
            user_visible_state_change=False,
        )

    def _run_detectors_for_text(
        self,
        *,
        text: str,
        response: str,
        base_payload: Dict[str, Any],
        turn_sequence: int,
    ) -> None:
        """Invoke any configured detectors and emit resulting drift events.

        Detectors:
            - Receive the same `turn_sequence` as the parent turn.
            - Are expected to return PLD-valid event dicts (or None).
            - Returned events are logged as-is via StructuredLogger.
        """
        if not self._detectors:
            return

        payload = dict(base_payload)
        payload.setdefault("response", response)

        for detector in self._detectors:
            detect = getattr(detector, "detect_and_build_event", None)
            if not callable(detect):
                continue

            event = detect(
                text=text,
                turn_sequence=turn_sequence,
                user_visible_state_change=False,
                payload=payload,
            )
            if event is not None:
                # Drift events are already PLD-compliant dicts built by the detector
                # (via Level 5 DriftDetector templates). We do not modify them.
                self._logger.log(event)

    @staticmethod
    def _select_drift_signal_kind(code: str) -> SignalKind:
        """Map a requested drift code to an existing SignalKind.

        This helper does not modify Level 2/3 semantics; it just chooses
        an appropriate existing drift signal kind.

        TODO: Consider deriving this mapping from RUNTIME_SIGNAL_MAP to
        automatically stay in sync with Level 5 signal semantics.
        """
        code = (code or "").strip()
        mapping = {
            "D1_instruction": SignalKind.INSTRUCTION_DRIFT,
            "D2_context": SignalKind.CONTEXT_DRIFT,
            "D3_repeated_plan": SignalKind.REPEATED_PLAN,
            "D4_tool_error": SignalKind.TOOL_ERROR,
        }
        return mapping.get(code, SignalKind.INSTRUCTION_DRIFT)

    @staticmethod
    def _select_repair_signal_kind(code: str) -> SignalKind:
        """Map a requested repair code to an existing SignalKind.

        TODO: Consider deriving this mapping from RUNTIME_SIGNAL_MAP to
        automatically stay in sync with Level 5 signal semantics.
        """
        code = (code or "").strip()
        mapping = {
            "R1_clarify": SignalKind.CLARIFICATION,
            "R2_soft_repair": SignalKind.SOFT_REPAIR,
            "R3_rewrite": SignalKind.REWRITE,
            "R4_request_clarification": SignalKind.REQUEST_USER_CLARIFICATION,
            "R5_hard_reset": SignalKind.HARD_RESET,
        }
        return mapping.get(code, SignalKind.CLARIFICATION)
