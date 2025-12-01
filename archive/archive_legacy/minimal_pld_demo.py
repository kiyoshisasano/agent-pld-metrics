# SPDX-License-Identifier: Apache-2.0
"""
minimal_pld_demo.py — Example usage of run_minimal_engine.py

Purpose:
    Demonstrate how to use the Minimal PLD Engine in a short, readable
    script.

What this example shows:
    - How to construct a MinimalEngine with default configuration.
    - How to run a small multi-turn conversation.
    - How to inspect PLD events (both human-readable and raw JSON).

Relationship in the quickstart stack:
    - hello_pld_runtime.py     → first-contact conceptual demo
    - run_minimal_engine.py    → minimal but complete engine
    - minimal_pld_demo.py      → usage example of the engine (this file)
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

# ---------------------------------------------------------------------
# Local import setup
# ---------------------------------------------------------------------
# Allow running this file directly (e.g., `python minimal_pld_demo.py`)
# without requiring installation. We append the quickstart root so
# that `run_minimal_engine` can be imported as a module.
SCRIPT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(SCRIPT_ROOT))

from run_minimal_engine import MinimalEngine, EngineConfig, explain_event  # type: ignore


def demo() -> None:
    """
    Run a small, educational demonstration of the Minimal PLD Engine.

    Turn sequence:
        1. On-task turn (no drift)
        2. Intentional drift (repair and reentry expected)
        3. Recovery turn (back on task)

    For each turn we print:
        - User input
        - Agent response
        - PLD events (human-readable + JSON)
    """
    print("\n🧪 MINIMAL PLD DEMO (Example)\n")

    # Create engine with default strategies and strict validation.
    engine = MinimalEngine(config=EngineConfig(validation_mode="strict"))

    turns = [
        "Let's continue working on the plan.",
        "Actually… can we switch topics and talk about penguins?",
        "Okay, going back to the task now.",
    ]

    for i, user_input in enumerate(turns, start=1):
        print("=" * 60)
        print(f"Turn {i}")
        print(f"User → {user_input}")

        agent_response, events = engine.run_turn(user_input)

        print(f"Agent → {agent_response}\n")
        print("PLD Events:")

        for event in events:
            # Human-readable explanation (phase / code / turn)
            explain_event(event)
            # Raw JSON event (matches PLD v2.0 schema structure, minimal subset)
            print(json.dumps(event, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    demo()
