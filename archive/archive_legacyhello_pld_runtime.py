# SPDX-License-Identifier: Apache-2.0
"""
hello_pld_runtime.py — PLD Quickstart Runtime

This script demonstrates how a runtime can emit PLD-compliant events
following the standard lifecycle:

    Drift → Repair → Reentry → Continue → Outcome

It is designed for learning and experimentation and includes:
- Human-readable summaries (optional)
- Interactive mode
- Built-in example scenarios
- Structured JSON output aligned with PLD v2.0 rules

Note:
    The validation logic in this file implements a minimal subset of the
    full specification. For production use, events SHOULD also be checked
    against the authoritative JSON Schema and the full event matrix.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
import argparse
from typing import Dict, Any, Optional, List


# --------------------------------------------------------------------
# PLD Specification (Structural + Semantic Alignment Rules)
# --------------------------------------------------------------------

PREFIX_TO_PHASE = {
    "D": "drift",
    "R": "repair",
    "RE": "reentry",
    "C": "continue",
    "O": "outcome",
    "F": "failover",
}

EVENT_TYPE_TO_PHASE_MUST = {
    "drift_detected": "drift",
    "repair_triggered": "repair",
    "reentry_observed": "reentry",
    "continue_allowed": "continue",
    "failover_triggered": "failover",
}

EVENT_TYPE_TO_PHASE_SHOULD = {
    "evaluation_pass": "outcome",
    "info": "none",
}


@dataclass
class Session:
    session_id: str = str(uuid.uuid4())
    turn: int = 0

    def begin_turn(self) -> int:
        """Increment once per user turn, not per event."""
        self.turn += 1
        return self.turn


def timestamp() -> str:
    """Return RFC3339/ISO-8601 UTC timestamp with 'Z' suffix."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


# --------------------------------------------------------------------
# Mock Drift Detector (lightweight educational heuristic)
# --------------------------------------------------------------------

DRIFT_KEYWORDS = {
    "off-topic",
    "unrelated",
    "cooking",
    "recipe",
    "switch",
    "penguin",
    "random",
}


def detect_drift(text: str) -> bool:
    """Return True if the input looks off-task according to simple heuristics."""
    lowered = text.lower()
    return any(k in lowered for k in DRIFT_KEYWORDS)


# --------------------------------------------------------------------
# PLD Event Creation + Validation
# --------------------------------------------------------------------

def validate(event: Dict[str, Any]) -> None:
    """
    Ensure event adheres to core PLD semantic constraints.

    This is a minimal checker that enforces:
      - prefix ↔ phase consistency
      - MUST-level event_type ↔ phase mappings
      - SHOULD-level event_type ↔ phase mappings as warnings

    It does NOT replace full JSON Schema validation.
    """
    phase = event["pld"]["phase"]
    code = event["pld"]["code"]
    event_type = event["event_type"]

    # Prefix–phase constraint
    prefix = code.split("_")[0].rstrip("0123456789")
    if prefix in PREFIX_TO_PHASE and PREFIX_TO_PHASE[prefix] != phase:
        raise ValueError(
            f"Prefix–phase mismatch: `{code}` requires `{PREFIX_TO_PHASE[prefix]}`, "
            f"got `{phase}`."
        )

    # MUST-level event_type → phase mapping
    if event_type in EVENT_TYPE_TO_PHASE_MUST:
        required = EVENT_TYPE_TO_PHASE_MUST[event_type]
        if required != phase:
            raise ValueError(
                f"`{event_type}` MUST map to phase `{required}`, got `{phase}`."
            )

    # SHOULD-level event_type → phase mapping (warning only)
    if event_type in EVENT_TYPE_TO_PHASE_SHOULD:
        expected = EVENT_TYPE_TO_PHASE_SHOULD[event_type]
        if expected != phase:
            print(
                f"[WARN] `{event_type}` SHOULD use phase `{expected}`, got `{phase}`.",
                flush=True,
            )


def build_event(
    *,
    session: Session,
    event_type: str,
    phase: str,
    code: str,
    turn_sequence: int,
    visible: bool = False,
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Construct a PLD-compliant event dictionary (minimal subset)."""
    event = {
        "schema_version": "2.0",
        "event_id": str(uuid.uuid4()),
        "timestamp": timestamp(),
        "session_id": session.session_id,
        "turn_sequence": turn_sequence,
        "source": "runtime",
        "event_type": event_type,
        "pld": {"phase": phase, "code": code},
        "payload": payload or {},
        "ux": {"user_visible_state_change": visible},
    }

    validate(event)
    return event


# --------------------------------------------------------------------
# Human-readable Rendering Layer
# --------------------------------------------------------------------

def explain(event: Dict[str, Any]) -> None:
    """Print a human-readable summary of a PLD event."""
    phase = event["pld"]["phase"]
    code = event["pld"]["code"]

    emoji = {
        "drift": "🚨",
        "repair": "🔧",
        "reentry": "🛂",
        "continue": "✅",
        "outcome": "🏁",
        "failover": "❌",
        "none": "ℹ️",
    }[phase]

    print(f"{emoji}  {event['event_type']} ({code})")
    print(
        f"Phase: {phase} | Turn: {event['turn_sequence']} | "
        f"Event ID: {event['event_id']}"
    )
    print()


# --------------------------------------------------------------------
# Turn Simulation Logic
# --------------------------------------------------------------------

def mock_system_response(drift_detected: bool, repair_applied: bool) -> str:
    """
    Provide an illustrative system-level explanation corresponding to the turn.

    This is purely descriptive and does not affect PLD semantics.
    """
    if drift_detected and repair_applied:
        return "A repair was applied and the system is now returning to the task."
    if drift_detected:
        return "The system noticed a deviation from the expected task."
    return "Task execution continues normally."


def run_turn(session: Session, user_input: str) -> List[Dict[str, Any]]:
    """
    Simulate one user turn and emit a sequence of PLD events
    sharing the same turn_sequence.
    """
    turn_sequence = session.begin_turn()
    events: List[Dict[str, Any]] = []

    if not user_input.strip():
        events.append(
            build_event(
                session=session,
                event_type="info",
                phase="none",
                code="INFO_empty_input",
                turn_sequence=turn_sequence,
            )
        )
        return events

    drift = detect_drift(user_input)

    if drift:
        # In this demo, we always attempt repair if drift is detected.
        events.append(
            build_event(
                session=session,
                event_type="drift_detected",
                phase="drift",
                code="D4_detected",
                turn_sequence=turn_sequence,
            )
        )
        events.append(
            build_event(
                session=session,
                event_type="repair_triggered",
                phase="repair",
                code="R1_retry",
                turn_sequence=turn_sequence,
            )
        )
        events.append(
            build_event(
                session=session,
                event_type="reentry_observed",
                phase="reentry",
                code="RE3_auto",
                turn_sequence=turn_sequence,
            )
        )
    else:
        events.append(
            build_event(
                session=session,
                event_type="continue_allowed",
                phase="continue",
                code="C0_normal",
                turn_sequence=turn_sequence,
            )
        )

    # Outcome event summarizing this turn
    events.append(
        build_event(
            session=session,
            event_type="evaluation_pass",
            phase="outcome",
            code="O1_success",
            turn_sequence=turn_sequence,
            payload={
                "system_response": mock_system_response(
                    drift_detected=drift,
                    repair_applied=drift,
                )
            },
        )
    )

    return events


# --------------------------------------------------------------------
# CLI Execution Modes
# --------------------------------------------------------------------

def interactive(human_output: bool = False) -> None:
    """Interactive REPL-style session."""
    session = Session()
    print("\n🧪 Interactive PLD Runtime (type 'exit' to quit)\n")

    while True:
        try:
            text = input("User> ")
        except (EOFError, KeyboardInterrupt):
            break

        if text.lower() in {"exit", "quit"}:
            break

        for e in run_turn(session, text):
            if human_output:
                explain(e)
            print(json.dumps(e, ensure_ascii=False, indent=2))


def examples(human_output: bool = False) -> None:
    """Run a set of canned example inputs."""
    session = Session()
    demo_inputs = [
        "Continuing with the task.",
        "Can we switch topic to cooking?",
        "Random penguin trivia.",
        "",
        "Resuming the plan.",
    ]

    for text in demo_inputs:
        print(f"\n> {text}")
        for e in run_turn(session, text):
            if human_output:
                explain(e)
            print(json.dumps(e, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="PLD quickstart runtime example (drift → repair → reentry → outcome)."
    )
    parser.add_argument("text", nargs="*", help="Optional user input for a single turn")
    parser.add_argument("--interactive", action="store_true", help="Start interactive session")
    parser.add_argument("--examples", action="store_true", help="Run demo examples")
    parser.add_argument("--human", action="store_true", help="Show human-readable summaries")
    args = parser.parse_args()

    if args.interactive:
        interactive(args.human)
        return

    if args.examples:
        examples(args.human)
        return

    if args.text:
        session = Session()
        user_text = " ".join(args.text)
        for event in run_turn(session, user_text):
            if args.human:
                explain(event)
            print(json.dumps(event, ensure_ascii=False, indent=2))
        return

    # Default behavior: run examples.
    examples(args.human)


if __name__ == "__main__":
    main()

