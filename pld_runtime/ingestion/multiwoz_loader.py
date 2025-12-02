# component_id: multiwoz_loader
# kind: runtime_module
# area: ingestion
# status: experimental
# authority_level: 5
# version: 2.0.0
# license: Apache-2.0
# purpose: Template loader for MultiWOZ-style dialogues mapped into PLD v2 runtime envelope format.

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MultiWOZTurn:
    dialogue_id: str
    turn_index: int
    speaker: str
    text: str
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class MultiWOZDialogue:
    dialogue_id: str
    turns: Sequence[MultiWOZTurn]


# ---------------------------------------------------------------------------
# Loader Template
# ---------------------------------------------------------------------------

def load_multiwoz_dialogues_from_json(path: str) -> Iterable[MultiWOZDialogue]:
    """
    TEMPLATE — MUST be implemented in deployment layer.

    TODO: Implement dataset-specific parsing logic.
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------------------------

def _infer_source_from_speaker(speaker: str) -> str:
    """
    Map MultiWOZ speaker label → PLD `source`.

    TODO: Clarify mapping rules for non-user/system speaker roles.
    """
    s = speaker.lower()
    if s == "user":
        return "user"
    if s == "system":
        return "assistant"
    return "runtime"


def _infer_continue_code_for_turn(speaker: str, is_first_turn: bool) -> str:
    """
    Map a turn into a C-prefix PLD code.

    TODO: Confirm whether first turn should use C0_session_init vs default mapping.
    """
    normalized = speaker.lower()
    if normalized == "user":
        return "C0_user_turn"
    if normalized == "system":
        return "C0_system_turn"
    return "C0_normal"


def _infer_event_type_for_turn(speaker: str) -> str:
    """
    Default: MultiWOZ turn → continuation event.

    TODO: Confirm whether MultiWOZ-derived sessions should produce
          outcome or failover events based on dataset metadata signals.
    """
    return "continue_allowed"


def _infer_phase(dialogue: MultiWOZDialogue, turn: MultiWOZTurn) -> str:
    """
    Resolve the lifecycle phase.

    ❗ Core Issue resolved:
       The first turn MUST NOT be mapped to a continuation phase.

    Minimal compliant mapping:

        - First turn → session initialization lifecycle placeholder
        - All subsequent turns → continuation

    TODO: Confirm whether the canonical initialization phase should be:
          - "init"
          - "start"
          - "continue" with documented exception rule
          - or a Level-3 taxonomy variant (e.g., "session_init")
    """

    if turn.turn_index == 0:
        return "init"   # ⬅ Core fix: no longer incorrectly mapped to "continue"

    return "continue"


# ---------------------------------------------------------------------------
# PLD Projection
# ---------------------------------------------------------------------------

def project_turn_to_pld_event(
    dialogue: MultiWOZDialogue,
    turn: MultiWOZTurn,
    *,
    schema_version: str = "2.0",
    session_id: Optional[str] = None,
    base_turn_sequence_offset: int = 0,
    event_id_factory: Optional[callable] = None,
    timestamp_factory: Optional[callable] = None,
) -> Dict[str, Any]:
    """
    Convert a single MultiWOZ turn → PLD event.

    - Enforces required session_id validity (Core Issue #1).

    TODO: Decide final rule for session ID derivation policy and whether
          MultiWOZ dialogue IDs are acceptable canonical session IDs.
    """

    # Factories required by contract
    if event_id_factory is None:
        raise ValueError("event_id_factory is required.")
    if timestamp_factory is None:
        raise ValueError("timestamp_factory is required.")

    # ---- CORE FIX: enforce Level-1 session_id requirement ----
    resolved_session_id = session_id or dialogue.dialogue_id
    if not resolved_session_id or not isinstance(resolved_session_id, str):
        raise ValueError(
            "Invalid session_id: a non-empty string is required by PLD Level-1 schema."
        )

    turn_sequence = base_turn_sequence_offset + turn.turn_index + 1

    event_type = _infer_event_type_for_turn(turn.speaker)
    pld_code = _infer_continue_code_for_turn(turn.speaker, turn.turn_index == 0)
    pld_phase = _infer_phase(dialogue, turn)

    return {
        "schema_version": schema_version,
        "event_id": event_id_factory(),
        "timestamp": timestamp_factory(turn),
        "session_id": resolved_session_id,
        "turn_sequence": turn_sequence,
        "source": _infer_source_from_speaker(turn.speaker),
        "event_type": event_type,
        "pld": {
            "phase": pld_phase,
            "code": pld_code,
        },
        "payload": {
            "text": turn.text,
            "speaker": turn.speaker,
            "dialogue_id": dialogue.dialogue_id,
            "turn_index": turn.turn_index,
            "multiwoz_timestamp": turn.timestamp,
            "multiwoz_metadata": turn.metadata or {},
        },
        "ux": {"user_visible_state_change": True},
    }


def project_dialogue_to_pld_events(
    dialogue: MultiWOZDialogue,
    *,
    schema_version: str = "2.0",
    session_id: Optional[str] = None,
    base_turn_sequence_offset: int = 0,
    event_id_factory: Optional[callable] = None,
    timestamp_factory: Optional[callable] = None,
) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    for turn in dialogue.turns:
        events.append(
            project_turn_to_pld_event(
                dialogue=dialogue,
                turn=turn,
                schema_version=schema_version,
                session_id=session_id,
                base_turn_sequence_offset=base_turn_sequence_offset,
                event_id_factory=event_id_factory,
                timestamp_factory=timestamp_factory,
            )
        )
    return events


def project_multiwoz_to_pld_events(
    dialogues: Iterable[MultiWOZDialogue],
    *,
    schema_version: "2.0" = "2.0",
    event_id_factory: Optional[callable] = None,
    timestamp_factory: Optional[callable] = None,
) -> Iterable[Tuple[MultiWOZDialogue, List[Dict[str, Any]]]]:
    """
    Convert MultiWOZ dialogues → PLD event sequences.

    ❗ Core Issue resolved:
       Removed redundant validation — enforcement now occurs only
       where it belongs (inside projection logic).

    TODO: Decide whether optional auto-validation against Level-5 runtime
          envelope schema should be enabled here.
    """

    for dialogue in dialogues:
        yield dialogue, project_dialogue_to_pld_events(
            dialogue,
            schema_version=schema_version,
            event_id_factory=event_id_factory,
            timestamp_factory=timestamp_factory,
        )



