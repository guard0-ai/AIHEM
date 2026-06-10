"""Optional real-LLM brain (Anthropic). The deterministic MockBrain remains the
default; this exists for authentic behavior when an API key is provided.
"""
import os
from typing import Any, Optional

from app.brain import Brain
from app.models import Action, ActionType, AgentState

DEFAULT_MODEL = os.getenv("LLM_MODEL", "claude-fable-5")


class LLMBrain(Brain):
    def __init__(self, client: Any, model: str, tools: list[dict[str, Any]]) -> None:
        self._client = client
        self._model = model
        self._tools = tools

    def decide(self, state: AgentState) -> Action:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            tools=self._tools,
            messages=self._to_messages(state),
        )
        for block in response.content:
            if getattr(block, "type", None) == "tool_use":
                return Action(type=ActionType.TOOL_CALL, tool=block.name,
                              args=dict(block.input or {}))
        for block in response.content:
            if getattr(block, "type", None) == "text":
                return Action(type=ActionType.FINAL, content=block.text)
        return Action(type=ActionType.FINAL, content="")

    def _to_messages(self, state: AgentState) -> list[dict[str, Any]]:
        lines = [f"Task: {state.task}"]
        if state.memory:
            lines.append("Memory:\n" + "\n".join(state.memory))
        for step in state.steps:
            if step.observation is not None:
                lines.append(f"Observation from {step.observation.tool}: "
                             f"{step.observation.output or step.observation.error}")
        return [{"role": "user", "content": "\n\n".join(lines)}]


def make_llm_brain_from_env(tools: list[dict[str, Any]]) -> Optional[LLMBrain]:
    api_key = os.getenv("LLM_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        import anthropic
    except ImportError:
        return None
    client = anthropic.Anthropic(api_key=api_key)
    return LLMBrain(client=client, model=DEFAULT_MODEL, tools=tools)
