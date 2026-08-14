import types

from app.models import ActionType, AgentState
from app.llm_brain import LLMBrain, make_llm_brain_from_env


def _block(**kw):
    return types.SimpleNamespace(**kw)


class FakeClient:
    """Mimics the Anthropic client surface used by LLMBrain."""

    def __init__(self, blocks):
        self._blocks = blocks
        self.messages = types.SimpleNamespace(create=self._create)

    def _create(self, **kwargs):
        return types.SimpleNamespace(content=self._blocks)


def test_llmbrain_parses_tool_use_block_into_tool_call():
    client = FakeClient([_block(type="tool_use", name="exfiltrate", input={"data": "x"})])
    brain = LLMBrain(client=client, model="claude-fable-5",
                     tools=[{"name": "exfiltrate", "description": "send", "input_schema": {"type": "object"}}])
    action = brain.decide(AgentState(task="t", session_id="s1"))
    assert action.type == ActionType.TOOL_CALL
    assert action.tool == "exfiltrate"
    assert action.args == {"data": "x"}


def test_llmbrain_parses_text_block_into_final():
    client = FakeClient([_block(type="text", text="here is the answer")])
    brain = LLMBrain(client=client, model="claude-fable-5", tools=[])
    action = brain.decide(AgentState(task="t", session_id="s1"))
    assert action.type == ActionType.FINAL
    assert action.content == "here is the answer"


def test_make_llm_brain_from_env_returns_none_without_key(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert make_llm_brain_from_env(tools=[]) is None
