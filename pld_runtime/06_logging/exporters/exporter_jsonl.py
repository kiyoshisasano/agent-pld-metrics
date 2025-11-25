# =============================================================================
# exporter_jsonl
#
# version: 2.0.0
# status: runtime
# authority_level_scope: Level 5 — runtime implementation
# purpose: JSONL exporter for PLD runtime events, transporting Level 5 events
#          as-is without modifying PLD event semantics or structure.
# change_classification: runtime-only
# dependencies: RuntimeSignalBridge.build_event output contract (PLD v2 runtime)
# =============================================================================

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Any, Callable, Mapping, Optional, Sequence, TextIO, Union

PldEvent = Mapping[str, Any]
EnvelopeBuilder = Callable[[PldEvent], Mapping[str, Any]]


@dataclass(frozen=True)
class JsonlExporterConfig:
    """
    Configuration for JsonlExporter.

    Notes:
      - `path` is the JSONL file path.
      - `ensure_dir` controls whether parent directories are created.
      - `mode` MUST be a text mode ("a" or "w"). Binary modes are not supported.
      - `encoding` defaults to UTF-8.
    """

    path: Union[str, Path]
    ensure_dir: bool = True
    mode: str = "a"
    encoding: str = "utf-8"


class JsonlExporter:
    """
    JsonlExporter
    --------------

    Level 5 exporter that writes PLD events to a JSONL file.

    Responsibilities:
      - Transport PLD events (already constructed via RuntimeSignalBridge.build_event)
        into a JSONL sink.
      - Preserve PLD event structure and semantics:
          * MUST NOT modify or infer Level 1–3 semantics.
          * MUST NOT change any PLD fields (schema_version, event_id, timestamp,
            session_id, turn_sequence, source, event_type, or any fields inside "pld").
      - Optionally wrap events in a transport-specific envelope WITHOUT mutating
        the original PLD event.

    Non-responsibilities:
      - Does NOT construct PLD events.
      - Does NOT validate or normalize PLD events.
      - Does NOT filter events based on semantics (e.g., drift vs repair).

    Usage pattern (bare PLD event per line):

        exporter = JsonlExporter.from_config(JsonlExporterConfig("pld_events.jsonl"))
        exporter.export_events(session_id, events)
        exporter.close()

    Usage pattern (custom envelope):

        def build_envelope(event: PldEvent) -> Mapping[str, Any]:
            return {
                "log_level": "INFO",
                "pld_event": event,  # event MUST be passed through unchanged
            }

        exporter = JsonlExporter.from_config(
            JsonlExporterConfig("pld_events.jsonl")
        )
        exporter.export_events(session_id, events, envelope_builder=build_envelope)
        exporter.close()
    """

    __slots__ = ("_file", "_lock", "_own_file", "_closed")

    def __init__(self, file: TextIO, *, own_file: bool = True) -> None:
        """
        Initialize a JsonlExporter with an open text file object.

        Arguments:
            file:
                A text-mode file object opened for writing/appending.
            own_file:
                If True, `close()` will also close the underlying file object.
                If False, the caller retains ownership and is responsible for
                closing it.
        """
        self._file: TextIO = file
        self._lock: Lock = Lock()
        self._own_file: bool = own_file
        self._closed: bool = False

    # --------------------------------------------------------------------- #
    # Constructors                                                          #
    # --------------------------------------------------------------------- #

    @classmethod
    def from_config(cls, config: JsonlExporterConfig) -> "JsonlExporter":
        """
        Create a JsonlExporter from JsonlExporterConfig.

        This helper:
          - Optionally creates parent directories.
          - Opens the target file in the configured mode/encoding.
        """
        path = Path(config.path)

        if config.ensure_dir:
            path.parent.mkdir(parents=True, exist_ok=True)

        # Text mode only; we do not support binary modes here.
        file = path.open(mode=config.mode, encoding=config.encoding)
        return cls(file, own_file=True)

    # --------------------------------------------------------------------- #
    # Core export API                                                       #
    # --------------------------------------------------------------------- #

    def export_events(
        self,
        session_id: str,
        events: Sequence[PldEvent],
        *,
        envelope_builder: Optional[EnvelopeBuilder] = None,
        auto_flush: bool = True,
    ) -> None:
        """
        Export a sequence of PLD events for a single session to JSONL.

        Behavior:
          - Writes one line per event.
          - By default, writes the PLD event dict directly as JSON:
                json.dumps(event, separators=(",", ":"))
          - If `envelope_builder` is provided, writes the envelope returned by
            that callable instead of the raw event, but the original event MUST
            be embedded unchanged (e.g., under "pld_event").

        Constraints:
          - MUST NOT mutate or reconstruct the PLD event.
          - MUST NOT modify:
                event["schema_version"]
                event["event_id"]
                event["timestamp"]
                event["session_id"]
                event["turn_sequence"]
                event["source"]
                event["event_type"]
                event["pld"][...]
          - Any additional transport metadata (log_level, environment, etc.)
            MUST live outside the PLD event structure.

        Parameters:
            session_id:
                Session identifier. Included for API symmetry; not used to
                alter events. Envelope builders MAY echo it if desired.
            events:
                Sequence of PLD events for this session.
            envelope_builder:
                Optional function that receives each PLD event and returns
                a mapping to serialize instead of the raw event.
            auto_flush:
                If True (default), flushes the underlying file after writing
                all events for this call.
        """
        if self._closed:
            raise RuntimeError("JsonlExporter is closed and cannot export events.")

        # NOTE:
        #  - We do not reorder or filter events here.
        #  - Ordering responsibility lies with the caller (e.g., SessionTraceBuffer).
        with self._lock:
            for event in events:
                payload: Mapping[str, Any]
                if envelope_builder is None:
                    payload = event
                else:
                    # The envelope builder is responsible for embedding the
                    # original event without modifying it.
                    payload = envelope_builder(event)

                line = json.dumps(
                    payload,
                    separators=(",", ":"),  # compact; do not sort keys
                    ensure_ascii=False,
                )
                self._file.write(line + "\n")

            if auto_flush:
                self._file.flush()

    # --------------------------------------------------------------------- #
    # Lifecycle                                                             #
    # --------------------------------------------------------------------- #

    def flush(self) -> None:
        """Flush the underlying file buffer, if not closed."""
        if self._closed:
            return
        with self._lock:
            self._file.flush()

    def close(self) -> None:
        """
        Close the exporter.

        If the exporter owns the underlying file (own_file=True), this also
        closes the file object. Otherwise, only marks the exporter as closed.
        """
        if self._closed:
            return

        with self._lock:
            if not self._closed:
                if self._own_file:
                    self._file.close()
                self._closed = True

    # --------------------------------------------------------------------- #
    # Context manager support                                               #
    # --------------------------------------------------------------------- #

    def __enter__(self) -> "JsonlExporter":
        if self._closed:
            raise RuntimeError("Cannot re-enter a closed JsonlExporter.")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
