# =============================================================================
# session_trace_buffer
#
# version: 2.0.0
# status: runtime
# authority_level_scope: Level 5 — runtime implementation
# purpose: In-memory buffer for PLD runtime events, preserving per-session
#          turn_sequence ordering for downstream exporters without changing
#          PLD event semantics.
# change_classification: runtime-only
# dependencies: RuntimeSignalBridge.build_event output contract (PLD v2 runtime)
# =============================================================================

from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from typing import Any, Callable, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Tuple

# Type aliases for readability. These DO NOT redefine the schema; they only
# document the minimal expectations of this module.
PldEvent = Mapping[str, Any]
MutablePldEvent = MutableMapping[str, Any]
SessionId = str

# Exporters are expected to treat incoming events as read-only. They MAY attach
# additional transport metadata in their own envelopes, but MUST NOT mutate or
# reinterpret the PLD event dict itself.
SessionExporter = Callable[[SessionId, Sequence[PldEvent]], None]


@dataclass(frozen=True)
class SessionTraceSnapshot:
    """
    Immutable snapshot of a single session's event sequence.

    - events are ordered by event["turn_sequence"] (ascending).
    - events MUST NOT be mutated by consumers of this API.
    """

    session_id: SessionId
    events: Tuple[PldEvent, ...]


class SessionTraceBuffer:
    """
    SessionTraceBuffer
    ------------------

    Level 5 in-memory buffer for PLD runtime events.

    Responsibilities:
      - Accept PLD events that were already constructed by RuntimeSignalBridge.build_event(...).
      - Partition events by event["session_id"].
      - Preserve ordering based on event["turn_sequence"] (authoritative key).
      - Provide read-only accessors and flush APIs for logging/export.
      - MUST NOT:
          * construct PLD events,
          * infer or normalize Level 1–3 semantics,
          * modify schema_version, event_id, timestamp, session_id,
            turn_sequence, source, event_type, or any fields inside "pld".

    Notes:
      - This buffer treats incoming events as opaque PLD dictionaries.
      - All semantic validation and normalization MUST happen upstream
        (e.g., in RuntimeSignalBridge or detection/validation layers).
    """

    __slots__ = ("_lock", "_events_by_session", "_copy_on_append")

    def __init__(self, *, copy_on_append: bool = True) -> None:
        """
        Initialize a new SessionTraceBuffer.

        Arguments:
            copy_on_append:
                If True (default), the buffer stores a shallow copy of each
                incoming event dict to reduce the risk of accidental mutation
                by callers after append. The copy operation MUST NOT modify
                any PLD fields; it is a structural snapshot only.

                If False, the buffer stores the exact dict objects passed in.
                Callers MUST then treat those dicts as immutable.
        """
        self._lock: Lock = Lock()
        self._events_by_session: Dict[SessionId, List[PldEvent]] = {}
        self._copy_on_append: bool = copy_on_append

    # --------------------------------------------------------------------- #
    # Core API                                                              #
    # --------------------------------------------------------------------- #

    def append(self, event: PldEvent) -> None:
        """
        Append a PLD event to the buffer.

        Requirements on `event` (Logging Contract assumptions):
          - event["session_id"]: str
          - event["turn_sequence"]: int (monotonic within session, Level 2/3)
          - event["schema_version"] == "2.0" (guaranteed upstream)
          - event["pld"]["phase"]: str
          - event["pld"]["code"]: str
          - payload/runtime/ux/metrics/extensions MAY be present.

        This method:
          - DOES NOT construct or normalize PLD events.
          - DOES NOT modify any PLD fields.
          - ONLY partitions and stores events for later retrieval/flush.
        """
        # Rely on upstream to guarantee presence of required keys. If they are
        # missing, we allow KeyError to surface rather than "fixing" anything.
        session_id = event["session_id"]  # type: ignore[index]
        _ = event["turn_sequence"]        # ensure key exists, but do not use here

        if self._copy_on_append:
            # Shallow copy: preserves all field values without reinterpretation.
            stored: Dict[str, Any] = dict(event)
        else:
            stored = event  # type: ignore[assignment]

        with self._lock:
            self._events_by_session.setdefault(session_id, []).append(stored)

    def get_snapshot(self, session_id: SessionId) -> Optional[SessionTraceSnapshot]:
        """
        Return an immutable snapshot of the events for a given session_id.

        - Events are ordered by event["turn_sequence"] (ascending).
        - Returns None if the session has no buffered events.
        - The returned events MUST be treated as read-only by callers.
        """
        with self._lock:
            events = self._events_by_session.get(session_id)
            if not events:
                return None

            ordered = sorted(
                events,
                key=lambda e: e["turn_sequence"],  # type: ignore[index]
            )

            # Expose as an immutable tuple to discourage mutation.
            return SessionTraceSnapshot(session_id=session_id, events=tuple(ordered))

    def get_all_session_ids(self) -> Sequence[SessionId]:
        """
        Return a list of all session_ids currently present in the buffer.

        The order is not semantically significant; callers MUST NOT rely on it
        for lifecycle reasoning (use turn_sequence within snapshots instead).
        """
        with self._lock:
            return list(self._events_by_session.keys())

    def has_events(self, session_id: SessionId) -> bool:
        """Return True if the buffer contains at least one event for session_id."""
        with self._lock:
            events = self._events_by_session.get(session_id)
            return bool(events)

    # --------------------------------------------------------------------- #
    # Flush / draining API                                                  #
    # --------------------------------------------------------------------- #

    def drain_session(
        self,
        session_id: SessionId,
        exporter: SessionExporter,
    ) -> bool:
        """
        Atomically drain (remove) all events for a single session and pass them
        to the provided exporter callback.

        Behavior:
          - If the session has no events, returns False and does nothing.
          - Otherwise:
              * Retrieves and removes all buffered events for session_id.
              * Orders them by turn_sequence (ascending).
              * Invokes exporter(session_id, events).
              * Returns True.

        The exporter MUST treat events as read-only and MUST NOT modify any PLD
        fields (schema_version, event_id, timestamp, session_id, turn_sequence,
        source, event_type, or pld.*).
        """
        with self._lock:
            events = self._events_by_session.pop(session_id, None)

        if not events:
            return False

        ordered = sorted(
            events,
            key=lambda e: e["turn_sequence"],  # type: ignore[index]
        )
        exporter(session_id, tuple(ordered))
        return True

    def drain_all(self, exporter: SessionExporter) -> None:
        """
        Atomically drain all sessions and pass each session's ordered events to
        the exporter callback.

        This method:
          - Copies and clears the internal mapping under lock to avoid holding
            the lock during exporter I/O.
          - For each session_id:
              * Orders events by turn_sequence.
              * Calls exporter(session_id, events).

        Exporters MUST NOT mutate the event dicts.
        """
        with self._lock:
            # Take ownership of current buffer contents and reset internal state.
            all_events = self._events_by_session
            self._events_by_session = {}

        for session_id, events in all_events.items():
            ordered = sorted(
                events,
                key=lambda e: e["turn_sequence"],  # type: ignore[index]
            )
            exporter(session_id, tuple(ordered))

    # --------------------------------------------------------------------- #
    # Maintenance / utilities                                               #
    # --------------------------------------------------------------------- #

    def clear(self) -> None:
        """
        Remove all buffered events for all sessions.

        This is a hard reset of the in-memory buffer only. It MUST NOT be used
        as a substitute for lifecycle semantics (e.g., session_closed events).
        """
        with self._lock:
            self._events_by_session.clear()

    def __len__(self) -> int:
        """
        Return the total number of buffered events across all sessions.

        This method is observational only and MUST NOT be used for lifecycle
        reasoning or metrics; it is purely an operational convenience.
        """
        with self._lock:
            return sum(len(events) for events in self._events_by_session.values())
