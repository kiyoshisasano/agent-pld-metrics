# SPDX-License-Identifier: Apache-2.0
"""
run_minimal_engine.py — Minimal PLD Engine (Reference Example, v2.0)

This script implements a minimal but complete engine that follows the
PLD lifecycle:

    Execute → Detect Drift → Repair → Reentry → Continue/Outcome

Role:
    - Reference implementation for PLD v2.0 semantics (minimal subset)
    - Fully working example of a PLD-aligned engine
    - Simpler than a full runtime stack, but more complete than a
      single-turn quickstart script.

Design goals:
    1. Minimal but complete PLD cycle per turn.
    2. Clear separation between:
        - the PLD engine loop (mechanism, relatively fixed), and
        - drift/repair/reentry strategies (policy, easily swappable).
    3. Validation mode that supports both strict learning and flexible
       experimentation ("strict" / "warn").

NOTE:
    The validation logic in this file implements a minimal subset of
    the PLD v2.0 rules (prefix/phase and event_type/phase mapping).
    For production use, events SHOULD also be validated against the
    authoritative JSON Schema and the full event matrix.
"""

from __future__ import annotations

import argparse
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Tuple


# ----------------------------------------------------------------------
# PLD Constants (Level 2 Semantics: Prefix/Phase + Event Type Mapping)
# ----------------------------------------------------------------------

# Lifecycle prefix → PLD phase
PREFIX_TO_PHASE = {
    "D": "drift",
    "R": "repair",
    "RE": "reentry",
    "C": "continue",
    "O": "outcome",
    "F": "failover",
}

# MUST-level event_type → phase mapping
EVENT_TYPE_TO_PHASE_MUST = {
    "drift_detected": "drift",
    "repair_triggered": "repair",
    "reentry_observed": "reentry",
    "continue_allowed": "continue",
    "continue_blocked": "continue",
    "failover_triggered": "failover",
}

# SHOULD-level event_type → phase mapping (warnings only)
EVENT_TYPE_TO_PHASE_SHOULD = {
    "evaluation_pass": "outcome",
    "evaluation_fail": "outcome",
    "info": "none",
}


# ----------------------------------------------------------------------
# Session + Engine State
# ----------------------------------------------------------------------

@dataclass
class SessionState:
    """Holds per-session identifiers and monotonic turn counter."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    turn_sequence: int = 0

    def begin_turn(self) -> int:
        """
        Increment the turn counter for a new user turn.

        All PLD events generated for a single user turn MUST share the
        same turn_sequence.
        """
        self.turn_sequence += 1
        return self.turn_sequence


@dataclass
class EngineState:
    """
    Tracks runtime state across turns.

    For this minimal engine, we only track:
      - how many repairs have been applied in the session
    """
    repair_count: int = 0


# ----------------------------------------------------------------------
# Default Strategies (can be swapped out via EngineConfig)
# ----------------------------------------------------------------------

# Heuristic keywords for "off-task" behavior.
DRIFT_KEYWORDS = {
    "off-topic",
    "unrelated",
    "cooking",
    "recipe",
    "switch topic",
    "switch",
    "penguin",
    "random",
}


def default_drift_detector(user_input: str, agent_plan: str) -> Tuple[bool, str]:
    """
    Minimal drift detector (default strategy).

    Combines a simple keyword-based heuristic with a trivial plan check.

    In a real system, this might use:
      - embeddings / vector similarity,
      - LLM-based classification,
      - policy checks, etc.
    """
    text = (user_input + " " + agent_plan).lower()
    for kw in DRIFT_KEYWORDS:
        if kw in text:
            # Tiny example: if the word "plan" appears, treat as repeated plan.
            return True, "D3_repeated_plan" if "plan" in text else "D4_tool_error"
    return False, "D0_none"


def default_repair_strategy(drift_code: str, repair_count: int) -> str:
    """
    Choose a repair strategy based on the drift code and how many
    repairs have already been attempted in this session.

    Policy (for learning):
      - First repair in the session → soft retry
      - Subsequent repairs → harder reset
    """
    if repair_count == 0:
        return "R1_soft_retry"
    return "R2_hard_reset"


def default_reentry_strategy(
    user_input: str,
    repaired_response: str,
    repair_code: str,
) -> Tuple[bool, str]:
    """
    Minimal reentry evaluator (default strategy).

    For this example, we use a simple rule:

      - If repair_code starts with "R1", we assume reentry succeeds
        as explicit or implicit confirmation.
      - If we had "R2_hard_reset", we also assume success but label
        the reentry differently (e.g., automatic/safety-based).

    NOTE:
        This is an assumption-based reentry model. In many production
        systems, reentry is evaluated based on subsequent user behavior
        ("observation-based" reentry). That more advanced pattern is
        intentionally not implemented here to keep the engine minimal,
        but it is a natural extension point.
    """
    if repair_code.startswith("R1"):
        return True, "RE1_intent_confirmed"
    return True, "RE3_auto"


@dataclass
class EngineConfig:
    """
    Engine configuration.

    This config separates the engine "mechanism" from its "policies":

      - drift_detector:   how to decide whether drift occurred
      - repair_strategy:  how to choose a repair mode from a drift code
      - reentry_strategy: how to decide if reentry succeeded

    Strategies are simple callables so they can be swapped easily,
    e.g. for experiments with LLM-based detectors or more complex rules.

    validation_mode:
      - "strict": raise on semantic violations (good for learning)
      - "warn":   print warnings but do not raise (good for experiments)
    """
    drift_detector: Callable[[str, str], Tuple[bool, str]] = default_drift_detector
    repair_strategy: Callable[[str, int], str] = default_repair_strategy
    reentry_strategy: Callable[[str, str, str], Tuple[bool, str]] = default_reentry_strategy
    validation_mode: str = "strict"  # "strict" or "warn"


# ----------------------------------------------------------------------
# Utility Functions
# ----------------------------------------------------------------------

def utc_timestamp() -> str:
    """Return RFC3339/ISO-8601 UTC timestamp with 'Z' suffix."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


# ----------------------------------------------------------------------
# PLD Event Validation + Construction (Minimal Subset)
# ----------------------------------------------------------------------

def validate_event(event: Dict[str, Any], mode: str = "strict") -> None:
    """
    Ensure event adheres to core PLD semantic constraints.

    Enforces:
      - prefix ↔ phase consistency
      - MUST-level event_type ↔ phase mappings
      - SHOULD-level event_type ↔ phase mappings (warning only)

    Modes:
      - "strict": raise ValueError on MUST/prefix violations.
      - "warn":   only print warnings, do not raise.

    NOTE:
        This function purposely does NOT perform full JSON Schema
        validation. It focuses on Level 2 semantics (matrix rules).
    """
    phase = event["pld"]["phase"]
    code = event["pld"]["code"]
    event_type = event["event_type"]

    # Normalize unknown validation modes to "strict" for safety.
    if mode not in ("strict", "warn"):
        mode = "strict"

    # Prefix–phase constraint
    prefix = code.split("_")[0].rstrip("0123456789")
    if prefix in PREFIX_TO_PHASE:
        required_phase = PREFIX_TO_PHASE[prefix]
        if required_phase != phase:
            msg = (
                f"Prefix–phase mismatch: `{code}` requires `{required_phase}`, "
                f"got `{phase}`."
            )
            if mode == "strict":
                raise ValueError(msg)
            else:
                print(f"[WARN][semantic] {msg}", flush=True)
    else:
        # Non-lifecycle prefixes (e.g., INFO_, SYS_) are expected to use phase="none"
        if phase != "none":
            msg = (
                f"Non-lifecycle prefix in code `{code}` requires phase='none', "
                f"got `{phase}`."
            )
            if mode == "strict":
                raise ValueError(msg)
            else:
                print(f"[WARN][semantic] {msg}", flush=True)

    # MUST-level mapping
    if event_type in EVENT_TYPE_TO_PHASE_MUST:
        required = EVENT_TYPE_TO_PHASE_MUST[event_type]
        if required != phase:
            msg = f"`{event_type}` MUST map to phase `{required}`, got `{phase}`."
            if mode == "strict":
                raise ValueError(msg)
            else:
                print(f"[WARN][semantic] {msg}", flush=True)

    # SHOULD-level mapping (warning only)
    if event_type in EVENT_TYPE_TO_PHASE_SHOULD:
        expected = EVENT_TYPE_TO_PHASE_SHOULD[event_type]
        if expected != phase:
            print(
                f"[WARN][semantic] `{event_type}` SHOULD use phase `{expected}`, "
                f"got `{phase}`.",
                flush=True,
            )


def make_event(
    *,
    session: SessionState,
    event_type: str,
    phase: str,
    code: str,
    turn_sequence: int,
    source: str = "runtime",
    visible: bool = False,
    payload: Optional[Dict[str, Any]] = None,
    runtime: Optional[Dict[str, Any]] = None,
    validation_mode: str = "strict",
) -> Dict[str, Any]:
    """
    Construct a PLD event dictionary compatible with the v2.0 schema
    (minimal subset) and validate it using the given validation_mode.
    """
    event: Dict[str, Any] = {
        "schema_version": "2.0",
        "event_id": str(uuid.uuid4()),
        "timestamp": utc_timestamp(),
        "session_id": session.session_id,
        "turn_sequence": turn_sequence,
        "source": source,
        "event_type": event_type,
        "pld": {"phase": phase, "code": code},
        "payload": payload or {},
        "ux": {"user_visible_state_change": visible},
    }

    if runtime is not None:
        event["runtime"] = runtime

    validate_event(event, mode=validation_mode)
    return event


# ----------------------------------------------------------------------
# Human-readable Rendering
# ----------------------------------------------------------------------

def explain_event(event: Dict[str, Any]) -> None:
    """Print a human-readable summary of a PLD event."""
    phase = event["pld"]["phase"]
    code = event["pld"]["code"]
    event_type = event["event_type"]

    emoji = {
        "drift": "🚨",
        "repair": "🔧",
        "reentry": "🛂",
        "continue": "✅",
        "outcome": "🏁",
        "failover": "❌",
        "none": "ℹ️",
    }.get(phase, "❓")

    print(f"{emoji}  {event_type} ({code})")
    print(
        f"Phase: {phase} | Turn: {event['turn_sequence']} | "
        f"Event ID: {event['event_id']}"
    )
    print()


# ----------------------------------------------------------------------
# Minimal Engine Implementation (with strategy injection)
# ----------------------------------------------------------------------

class MinimalEngine:
    """
    Minimal PLD engine.

    Responsibilities per user turn:
      1. Execute agent step (produce a candidate response/plan)
      2. Detect drift
      3. Choose and apply repair (if needed)
      4. Evaluate reentry
      5. Emit a sequence of PLD events for this turn

    The engine is "mechanism"; the strategies (detectors, repair, reentry)
    are injected via EngineConfig.
    """

    def __init__(self, config: Optional[EngineConfig] = None):
        self.session = SessionState()
        self.config = config or EngineConfig()
        self.state = EngineState()

    # ---- Public orchestration ---------------------------------------

    def run_turn(self, user_input: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Execute a full PLD cycle for a single user turn and return:
          - the final agent response after repairs,
          - the list of PLD events for that turn.
        """
        turn_sequence = self.session.begin_turn()
        mode = self.config.validation_mode

        if not user_input.strip():
            return self._handle_empty_input(user_input, turn_sequence, mode)

        # 1. Execute agent step
        candidate_response = self._agent_step(user_input)

        # 2. Detect drift
        drift_detected, drift_code = self._detect_phase(user_input, candidate_response)

        if drift_detected:
            return self._handle_drift_turn(
                user_input=user_input,
                candidate_response=candidate_response,
                drift_code=drift_code,
                turn_sequence=turn_sequence,
                validation_mode=mode,
            )
        else:
            return self._handle_no_drift_turn(
                user_input=user_input,
                candidate_response=candidate_response,
                turn_sequence=turn_sequence,
                validation_mode=mode,
            )

    # ---- Internal steps (mechanism) ---------------------------------

    def _agent_step(self, user_input: str) -> str:
        """
        Minimal "agent" behavior.

        For this example:
          - If the user appears off-topic, the agent initially tries to follow it.
          - Repairs may later redirect back to the main task.

        NOTE:
            This is deliberately simple. It is not intended as a
            best-practice agent policy, only as a plausible behavior
            to generate meaningful PLD events.
        """
        if any(kw in user_input.lower() for kw in DRIFT_KEYWORDS):
            return "Let me answer that, even if it might be off our main task."
        return "Continuing with the main task as requested."

    def _detect_phase(self, user_input: str, candidate_response: str) -> Tuple[bool, str]:
        """
        Detect whether the combined behavior indicates drift by using
        the configured drift_detector strategy.
        """
        return self.config.drift_detector(user_input, candidate_response)

    def _apply_repair(
        self,
        user_input: str,
        previous_response: str,
        repair_code: str,
    ) -> str:
        """
        Apply a repair strategy via the configured repair_strategy.

        In a real engine, this could:
          - regenerate a plan,
          - change tools,
          - reset context, etc.
        """
        return self.config.repair_strategy(repair_code, self.state.repair_count - 1) \
            if repair_code else previous_response

    def _evaluate_reentry(
        self,
        user_input: str,
        repaired_response: str,
        repair_code: str,
    ) -> Tuple[bool, str]:
        """
        Evaluate reentry via the configured reentry_strategy.

        NOTE:
            This minimal implementation uses only the repair_code and
            the repaired response. A more advanced engine would likely
            consider subsequent user turns and/or constraint checks.
        """
        return self.config.reentry_strategy(user_input, repaired_response, repair_code)

    # ---- Turn handlers (composed from steps above) ------------------

    def _handle_empty_input(
        self,
        user_input: str,
        turn_sequence: int,
        validation_mode: str,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Handle the special case where the user input is empty."""
        events: List[Dict[str, Any]] = []

        info_event = make_event(
            session=self.session,
            event_type="info",
            phase="none",
            code="INFO_empty_input",
            turn_sequence=turn_sequence,
            payload={"user_input": user_input},
            validation_mode=validation_mode,
        )
        events.append(info_event)

        outcome_event = make_event(
            session=self.session,
            event_type="evaluation_pass",
            phase="outcome",
            code="O0_noop",
            turn_sequence=turn_sequence,
            payload={"summary": "No input to process."},
            validation_mode=validation_mode,
        )
        events.append(outcome_event)

        return "", events

    def _handle_drift_turn(
        self,
        user_input: str,
        candidate_response: str,
        drift_code: str,
        turn_sequence: int,
        validation_mode: str,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Handle a turn where drift has been detected:
          - emit drift event
          - choose and apply repair
          - evaluate reentry
          - emit continue/outcome events
        """
        events: List[Dict[str, Any]] = []

        # Drift event
        events.append(
            make_event(
                session=self.session,
                event_type="drift_detected",
                phase="drift",
                code=drift_code,
                turn_sequence=turn_sequence,
                source="detector",
                payload={
                    "user_input": user_input,
                    "agent_plan": candidate_response,
                },
                runtime={"agent_state": "drift_detected"},
                validation_mode=validation_mode,
            )
        )

        # Choose repair via strategy
        repair_code = self.config.repair_strategy(drift_code, self.state.repair_count)
        self.state.repair_count += 1

        repaired_response = self._apply_repair(
            user_input=user_input,
            previous_response=candidate_response,
            repair_code=repair_code,
        )

        events.append(
            make_event(
                session=self.session,
                event_type="repair_triggered",
                phase="repair",
                code=repair_code,
                turn_sequence=turn_sequence,
                source="controller",
                payload={
                    "user_input": user_input,
                    "previous_response": candidate_response,
                    "repaired_response": repaired_response,
                },
                validation_mode=validation_mode,
            )
        )

        # Reentry evaluation via strategy
        reentry_ok, reentry_code = self._evaluate_reentry(
            user_input=user_input,
            repaired_response=repaired_response,
            repair_code=repair_code,
        )

        if reentry_ok:
            events.append(
                make_event(
                    session=self.session,
                    event_type="reentry_observed",
                    phase="reentry",
                    code=reentry_code,
                    turn_sequence=turn_sequence,
                    source="detector",
                    payload={"repair_code": repair_code},
                    validation_mode=validation_mode,
                )
            )
            events.append(
                make_event(
                    session=self.session,
                    event_type="continue_allowed",
                    phase="continue",
                    code="C0_after_repair",
                    turn_sequence=turn_sequence,
                    payload={
                        "note": "Execution continues after successful repair.",
                    },
                    validation_mode=validation_mode,
                )
            )
        else:
            events.append(
                make_event(
                    session=self.session,
                    event_type="continue_blocked",
                    phase="continue",
                    code="C1_blocked_after_repair",
                    turn_sequence=turn_sequence,
                    payload={
                        "note": "Execution blocked after failed repair.",
                    },
                    validation_mode=validation_mode,
                )
            )

        # Outcome for this turn
        events.append(
            make_event(
                session=self.session,
                event_type="evaluation_pass",
                phase="outcome",
                code="O1_success",
                turn_sequence=turn_sequence,
                payload={
                    "user_input": user_input,
                    "final_response": repaired_response,
                    "drift_detected": True,
                },
                validation_mode=validation_mode,
            )
        )

        return repaired_response, events

    def _handle_no_drift_turn(
        self,
        user_input: str,
        candidate_response: str,
        turn_sequence: int,
        validation_mode: str,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Handle a turn where no drift has been detected:
          - emit continue event
          - emit outcome event
        """
        events: List[Dict[str, Any]] = []

        events.append(
            make_event(
                session=self.session,
                event_type="continue_allowed",
                phase="continue",
                code="C0_normal",
                turn_sequence=turn_sequence,
                payload={
                    "user_input": user_input,
                    "agent_response": candidate_response,
                },
                validation_mode=validation_mode,
            )
        )

        events.append(
            make_event(
                session=self.session,
                event_type="evaluation_pass",
                phase="outcome",
                code="O1_success",
                turn_sequence=turn_sequence,
                payload={
                    "user_input": user_input,
                    "final_response": candidate_response,
                    "drift_detected": False,
                },
                validation_mode=validation_mode,
            )
        )

        return candidate_response, events


# ----------------------------------------------------------------------
# Demo Runners
# ----------------------------------------------------------------------

def run_demo_session(human: bool = True, validation_mode: str = "strict") -> None:
    """
    Run a fixed multi-turn demo showing:
      - on-task turn,
      - off-task + repair turn,
      - recovered on-task turn.
    """
    engine = MinimalEngine(EngineConfig(validation_mode=validation_mode))

    turns = [
        "Let's continue with the main task.",
        "Actually, can we switch topic and talk about cooking recipes?",
        "Okay, back to the original task now.",
    ]

    for i, user_input in enumerate(turns, start=1):
        print("\n" + "=" * 60)
        print(f"Turn {i}:")
        print(f"User: {user_input}")
        final_response, events = engine.run_turn(user_input)
        print(f"Agent: {final_response}")

        print("\nPLD events:")
        for event in events:
            if human:
                explain_event(event)
            print(json.dumps(event, ensure_ascii=False, indent=2))


def interactive_session(human: bool = True, validation_mode: str = "strict") -> None:
    """
    Run an interactive session where the user can type turns one by one.
    """
    engine = MinimalEngine(EngineConfig(validation_mode=validation_mode))
    print("\n🧪 Minimal PLD Engine — interactive mode (type 'exit' to quit)\n")

    while True:
        try:
            user_input = input("User> ")
        except (EOFError, KeyboardInterrupt):
            break

        if user_input.lower() in {"exit", "quit"}:
            break

        final_response, events = engine.run_turn(user_input)
        print(f"Agent> {final_response}\n")

        print("PLD events:")
        for event in events:
            if human:
                explain_event(event)
            print(json.dumps(event, ensure_ascii=False, indent=2))
        print()


# ----------------------------------------------------------------------
# CLI Entry Point
# ----------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Minimal PLD engine reference implementation.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run an interactive session instead of the canned demo.",
    )
    parser.add_argument(
        "--no-human",
        action="store_true",
        help="Do not print human-readable summaries, only JSON events.",
    )
    parser.add_argument(
        "--validation-mode",
        choices=["strict", "warn"],
        default="strict",
        help="Validation mode for PLD events (strict or warn).",
    )
    args = parser.parse_args()

    # CLI flags:
    # --no-human       → machine-friendly logs only (JSON)
    # default (False)  → human + JSON hybrid output for learning
    human = not args.no_human
    validation_mode = args.validation_mode

    if args.interactive:
        interactive_session(human=human, validation_mode=validation_mode)
    else:
        run_demo_session(human=human, validation_mode=validation_mode)


if __name__ == "__main__":
    main()

