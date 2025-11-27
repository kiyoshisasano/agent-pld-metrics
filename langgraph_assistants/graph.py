#!/usr/bin/env python
# component_id: langgraph_pld_graph
# kind: example
# area: integration
# status: experimental
# authority_level: 2
# purpose: Build a minimal LangGraph graph and hook in the PLD observer (observer mode only).

from __future__ import annotations

from typing import Any, Dict

from langgraph.graph import StateGraph

from .agent_node import AssistantNode
from .pld_runtime_integration import emit_continue_event


def build_graph(model: str) -> Any:
    """Build and compile a minimal LangGraph graph.

    The graph has a single node:

        "assistant" → AssistantNode.run → emit_continue_event

    We run this graph multiple times from run.py, manually incrementing
    the turn counter and handling session closure there. This keeps the
    graph itself simple while still demonstrating how to hook in PLD.
    """

    graph = StateGraph(dict)
    agent = AssistantNode(model=model)

    @graph.add_node("assistant")
    def assistant_step(state: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Run the assistant node (LLM call).
        state = agent.run(state)

        # 2. Emit a 'continue' observer event (PLD runtime).
        emit_continue_event(state)

        # turn increment is handled in run.py to keep responsibilities clear.
        return state

    graph.set_entry_point("assistant")

    app = graph.compile()
    return app
