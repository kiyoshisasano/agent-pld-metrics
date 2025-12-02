# component_id: logging_pipeline
# kind: runtime_module
# area: logging
# status: runtime
# authority_level: 5
# version: 2.0.0
# license: Apache-2.0
# purpose: Connect session trace buffering to exporters while preserving PLD event semantics.

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence, Callable

from .session_trace_buffer import SessionTraceBuffer
from .exporters.exporter_jsonl import JsonlExporter
from .exporters.exporter_open_telemetry import OpenTelemetryExporter

PldEvent = Mapping[str, Any]
SessionId = str
SessionExporter = Callable[[SessionId, Sequence[PldEvent]], None]


class RuntimeLoggingPipeline:
    """
    RuntimeLoggingPipeline
    ----------------------

    Level 5 orchestration component that wires:

        RuntimeSignalBridge.build_event(...)  →  SessionTraceBuffer.append(...)
                                              →  JsonlExporter / OpenTelemetryExporter

    Responsibilities:
      - Accept PLD events that were already constructed by RuntimeSignalBridge.
      - Buffer events per session via SessionTraceBuffer.
      - On flush, export the same ordered event sequence to:
          * JSONL (required)
          * OpenTelemetry (optional)
      - MUST NOT:
          * construct PLD events,
          * mutate schema_version, event_id, timestamp, session_id,
            turn_sequence, source, event_type, or any pld.* fields,
          * perform normalization or semantic inference.

    Notes:
      - Ordering is delegated to SessionTraceBuffer (turn_sequence authoritative).
      - This pipeline is purely a transport/wiring layer.
    """

    __slots__ = ("_buffer", "_jsonl_exporter", "_otel_exporter")

    def __init__(
        self,
        jsonl_exporter: JsonlExporter,
        otel_exporter: Optional[OpenTelemetryExporter] = None,
        *,
        copy_on_append: bool = True,
    ) -> None:
        """
        Initialize a RuntimeLoggingPipeline.

        Arguments:
            jsonl_exporter:
                Required JsonlExporter instance. Receives all flushed events.
            otel_exporter:
                Optional OpenTelemetryExporter instance. If provided, it will
                receive the same ordered event sequence as jsonl_exporter.
            copy_on_append:
                Passed through to SessionTraceBuffer. When True, the buffer
                stores a shallow copy of each PLD event; callers MUST still
                treat events as immutable.
        """
        self._buffer = SessionTraceBuffer(copy_on_append=copy_on_append)
        self._jsonl_exporter = jsonl_exporter
        self._otel_exporter = otel_exporter

    # --------------------------------------------------------------------- #
    # Ingestion API                                                         #
    # --------------------------------------------------------------------- #

    def on_event(self, event: PldEvent) -> None:
        """
        Ingest a single PLD event into the buffer.

        Contract:
          - `event` MUST be the direct output of RuntimeSignalBridge.build_event(...).
          - This method MUST NOT modify the event.
          - Validation/normalization MUST have happened upstream if needed.
        """
        self._buffer.append(event)
        # TODO(FLUSH-POLICY-OWNERSHIP): Check if event is session_closed (event_type),
        # and if so, trigger flush_session(event["session_id"]).
        # This is a Level 5 ownership decision.

    # --------------------------------------------------------------------- #
    # Flush API                                                             #
    # --------------------------------------------------------------------- #

    def flush_session(self, session_id: SessionId) -> bool:
        """
        Flush all buffered events for a single session.

        Behavior:
          - Delegates ordering to SessionTraceBuffer (turn_sequence ascending).
          - Exports the same ordered sequence to:
              * JsonlExporter
              * OpenTelemetryExporter (if configured)
          - Returns:
              * True  → events existed and were exported.
              * False → no events for that session_id.
        """

        def _export(sid: SessionId, events: Sequence[PldEvent]) -> None:
            # Transport only — NO mutation or inference.
            # TODO(FLUSH-ASYNC): Implement asynchronous export (e.g., using a thread pool)
            # to prevent I/O blocking from one exporter delaying another or the runtime.
            self._jsonl_exporter.export_events(sid, events)
            if self._otel_exporter is not None:
                self._otel_exporter.export_events(sid, events)

        return self._buffer.drain_session(session_id, _export)

    def flush_all(self) -> None:
        """
        Flush all sessions and export each session's ordered events.

        This is typically called:
          - on graceful shutdown, or
          - at checkpoints (e.g., after N turns or M seconds).
        """

        def _export(sid: SessionId, events: Sequence[PldEvent]) -> None:
            # Same contract as flush_session: pass-through only.
            # TODO(FLUSH-ASYNC): Implement asynchronous export.
            self._jsonl_exporter.export_events(sid, events)
            if self._otel_exporter is not None:
                self._otel_exporter.export_events(sid, events)

        self._buffer.drain_all(_export)

    # --------------------------------------------------------------------- #
    # Inspection helpers (non-semantic)                                     #
    # --------------------------------------------------------------------- #

    def has_events(self, session_id: SessionId) -> bool:
        """
        Return True if there is at least one buffered event for session_id.

        This is an operational helper only (e.g., for deciding when to flush),
        and MUST NOT be used for semantic reasoning about lifecycle.
        """
        return self._buffer.has_events(session_id)

    def buffered_session_ids(self) -> Sequence[SessionId]:
        """
        Return a snapshot of session_ids currently buffered.

        The order of session_ids is NOT semantically meaningful.
        """
        return self._buffer.get_all_session_ids()
    
    # --------------------------------------------------------------------- #
    # Lifecycle API (Fix Core Technical Issue)
    # --------------------------------------------------------------------- #

    def close(self) -> None:
        """
        Perform a graceful shutdown of the logging pipeline:
        1. Flush all remaining buffered events.
        2. Close underlying file resources (JsonlExporter).
        3. Shut down telemetry resources (OpenTelemetryExporter).
        """
        # 1. Flush remaining events to ensure no data loss
        self.flush_all()
        
        # 2. Close JsonlExporter (required for file resource management)
        self._jsonl_exporter.close()

        # 3. Shut down OpenTelemetryExporter (optional for resource management)
        if self._otel_exporter is not None:
            self._otel_exporter.shutdown()
