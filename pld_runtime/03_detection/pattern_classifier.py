# version: 2.0.0
# status: draft runtime_template (experimental)
# authority_level_scope: Level 5 — runtime implementation
# purpose: Pattern classification runtime template for producing taxonomy-aligned signals to feed PLD v2 event generation.
# change_classification: runtime-only, non-breaking + technical review alignment
# dependencies: PLD event schema v2.0, PLD Event Matrix v2.0, PLD Runtime Standard v2.0, PLD Taxonomy v2.0
# notes: Template only. Does not emit PLD events directly; integrates with Level 5 runtime envelope and detectors.

"""
Pattern classifier template for PLD-compatible runtimes.

This module remains Level 5 (runtime implementation only). It assists in
classifying runtime state and generating hints for downstream components
but does NOT emit PLD-valid events.

Changes applied per technical review:
- Added required Level 1-aligned source hint to PatternClassification.

All open questions have been converted into TODOs and must not be resolved yet.
"""

from __future__ import annotations

import dataclasses
import typing as _t


# ──────────────────────────────────────────────────────────────────────────────
# Public Data Structures
# ──────────────────────────────────────────────────────────────────────────────


@dataclasses.dataclass
class TurnSnapshot:
    """
    Minimal view of a single turn or step in the runtime.

    The classifier remains agnostic to PLD schema here; mapping responsibility
    belongs to the PatternClassifier or downstream event builders.

    NOTE:
    This accepts implementation-specific role values.
    The corresponding PLD-conforming source MUST be output in PatternClassification.
    """

    turn_sequence: int
    role: str
    content: str | None = None
    metadata: dict[str, _t.Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class PatternClassification:
    """
    Output from the PatternClassifier for a single analyzed unit.

    Now includes `source_hint` to satisfy Level 1 source alignment expectations.
    """

    code: str
    phase: str | None = None
    event_type_hint: str | None = None
    confidence: float | None = None

    # NEW — resolves Core Technical Issue #1:
    source_hint: str = dataclasses.field()
    """
    REQUIRED — MUST contain a Level 1-valid source enum value.
    Example valid values per Level 1 schema:
        "user", "assistant", "runtime", "controller", "detector", "system"

    Classifiers MUST set this explicitly — the event builder must not infer it.
    """

    tags: list[str] = dataclasses.field(default_factory=list)
    extra: dict[str, _t.Any] = dataclasses.field(default_factory=dict)

    # TODO: Confirm whether classifier should validate taxonomy correctness
    # (e.g., ensure D* → phase=drift before returning).
    # Current assumption: downstream builder performs authoritative enforcement.


@dataclasses.dataclass
class PatternClassifierContext:
    """
    Session-scoped or run-scoped context for pattern classification.

    Does NOT contain PLD schema-specific values.
    """

    session_id: str
    enable_drift_patterns: bool = True
    enable_repair_patterns: bool = True
    enable_continue_patterns: bool = True
    enable_observability_patterns: bool = True

    max_repetition_window: int = 8
    loop_threshold: int = 3

    options: dict[str, _t.Any] = dataclasses.field(default_factory=dict)


# ──────────────────────────────────────────────────────────────────────────────
# Core Template Class
# ──────────────────────────────────────────────────────────────────────────────


class PatternClassifier:
    """
    Base template for Level 5 pattern classifiers.

    This class ONLY produces PatternClassification objects — never PLD events.

    Subclasses should implement actual classification rules in `_classify()`.
    """

    def __init__(self, ctx: PatternClassifierContext) -> None:
        self._ctx = ctx

        # History is append-only unless reset manually.
        # TODO: Clarification needed — should this be bounded (deque) instead of unbounded?
        self._history: list[TurnSnapshot] = []

    def observe_and_classify(
        self,
        turn: TurnSnapshot,
    ) -> list[PatternClassification]:
        """
        Store the turn and compute pattern classifications.

        Current behavior: turn is added BEFORE classification.

        TODO: Clarification needed — should classification see history BEFORE or AFTER adding the new turn?
              (i.e., should this append occur before or after invoking `_classify()`?)
        """

        self._history.append(turn)
        return self._classify(turn, history=self._history)

    def _classify(
        self,
        turn: TurnSnapshot,
        *,
        history: list[TurnSnapshot],
    ) -> list[PatternClassification]:
        """
        IMPLEMENTATION HOOK to detect behavioral/runtime patterns.

        Default: no detected patterns.
        """
        return []

    @property
    def context(self) -> PatternClassifierContext:
        return self._ctx

    @property
    def history(self) -> tuple[TurnSnapshot, ...]:
        return tuple(self._history)

    def reset_history(self) -> None:
        """
        Clears stored turn history.

        Caller is responsible for ensuring this aligns with PLD session semantics.
        """
        self._history.clear()

