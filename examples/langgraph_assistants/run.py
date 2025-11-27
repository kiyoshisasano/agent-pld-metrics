#!/usr/bin/env python
# component_id: langgraph_pld_run
# kind: example
# area: integration
# status: experimental
# authority_level: 2
# purpose: Entry point for the LangGraph + PLD observer-mode integration example.

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict

import yaml

# ---------------------------------------------------------------------------
# Adjust import path so that pld_runtime and this example package are importable
# from the repo root.
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Now we can safely import our example modules.
from examples.langgraph_assistants.graph import build_graph  # noqa: E402
from examples.langgraph_assistants.pld_runtime_integration import (  # noqa: E402
    init_pld_observer,
    emit_tool_error,
    emit_session_closed,
)


def load_config() -> Dict[str, Any]:
    cfg_path = Path(__file__).parent / "config.yaml"
    return yaml.safe_load(cfg_path.read_text())


def main() -> None:
    # Ensure OpenAI API key is set.
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY environment variable is not set.")

    cfg = load_config()

    model = cfg["model"]
    pld_mode = cfg.get("pld_validation_mode", "strict")
    jsonl_path = cfg.get("logging", {}).get("jsonl_path", "logs/langgraph_pld_demo.jsonl")

    # Initialize PLD observer stack (bridge + logging pipeline).
    init_pld_observer(jsonl_path=jsonl_path, validation_mode=pld_mode)

    # Build LangGraph application.
    app = build_graph(model=model)

    # Initial state for the conversation.
    state: Dict[str, Any] = {
        "session_id": "demo-session-1",
        "turn": 1,
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "Help me plan a short weekend trip to a nearby city.",
            }
        ],
    }

    # Run a short scripted loop of turns.
    max_turns = 3
    for _ in range(max_turns):
        try:
            # Invoke the LangGraph app; this will call the AssistantNode and
            # emit a 'continue' PLD observer event in graph.py.
            state = app.invoke(state)
        except Exception as exc:
            # If something goes wrong (e.g., API failure), emit a TOOL_ERROR event
            # and stop the loop. The PLD observer remains non-disruptive to the
            # caller's flow; here we simply break as part of the demo.
            emit_tool_error(state, reason=str(exc))
            print(f"[warn] Encountered error during assistant turn: {exc!r}")
            break

        # Increment the turn counter on the state (1-based).
        state["turn"] = int(state.get("turn", 1)) + 1

    # Emit a 'session_closed' observer event at the end of the conversation.
    emit_session_closed(state)

    print("Final state:", state)
    print(f"PLD JSONL logs → {jsonl_path}")


if __name__ == "__main__":
    main()
