#!/usr/bin/env python
# component_id: langgraph_assistant_node
# kind: example
# area: integration
# status: experimental
# authority_level: 2
# purpose: LangGraph node that wraps the OpenAI Assistants API (PLD-agnostic application layer).

from __future__ import annotations

from typing import Any, Dict, List

from openai import OpenAI


class AssistantNode:
    """LangGraph node wrapper for the OpenAI Assistants-style chat API.

    This layer is intentionally **PLD-unaware**:
    - It does NOT import PLD runtime modules.
    - It does NOT construct PLD events.
    - It only knows about application-level "messages" and model configuration.
    """

    def __init__(self, model: str, tools: List[Dict[str, Any]] | None = None) -> None:
        self._client = OpenAI()
        self._model = model
        self._tools = tools or []

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute one assistant turn and append the reply to the state.

        Expected state keys:
            - state["messages"]: list of {"role": str, "content": str}
        """

        messages = state.get("messages") or []
        if not isinstance(messages, list):
            raise ValueError("state['messages'] must be a list of message dicts")

        # Example call using the Responses API.
        # NOTE: Response object structure may evolve; this is a minimal example
        # and may need adjustment to match the installed openai SDK version.
        response = self._client.responses.create(
            model=self._model,
            input=[{"role": m["role"], "content": m["content"]} for m in messages],
            tools=self._tools,
        )

        # Extract the assistant's reply text from the response.
        # This is intentionally defensive: we try to find the first text output.
        assistant_reply = "<no response>"
        try:
            for item in response.output:
                if item.type == "message":
                    for c in item.content:
                        if getattr(c, "type", None) == "output_text":
                            assistant_reply = c.text.value
                            raise StopIteration
            # Fallback: if structure differs, stringify the response
        except StopIteration:
            pass
        except Exception:
            # As a last resort, stringify the response object
            assistant_reply = str(response)

        messages.append({"role": "assistant", "content": assistant_reply})
        state["messages"] = messages
        return state
