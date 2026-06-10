"""Brains decide the next Action from the current AgentState.

MockBrain is deterministic so challenge grading is reproducible without an LLM.
Its defining (intentional) trait: it obeys `@@TOOL:<name>:<json-args>@@` markers
found in the latest observation or in memory. That single behavior makes indirect
prompt injection (via tool output) and memory poisoning demonstrable and gradable.
"""
import json
import re
from abc import ABC, abstractmethod
from typing import Optional

from app.models import Action, ActionType, AgentState

_MARKER = re.compile(r"@@TOOL:([a-zA-Z_][a-zA-Z0-9_]*):(\{.*?\})@@")


def extract_injected_action(state: AgentState) -> Optional[Action]:
    """Return the first injection-marker action not already executed, else None.

    The "already executed" guard is keyed on exact (tool, args) equality, so a
    marker whose args change every turn is not deduplicated — acceptable here
    because the loop is bounded by max_iterations.
    """
    sources: list[str] = []
    if state.steps and state.steps[-1].observation is not None:
        sources.append(str(state.steps[-1].observation.output))
    sources.extend(state.memory)

    for text in sources:
        match = _MARKER.search(text or "")
        if not match:
            continue
        tool = match.group(1)
        try:
            args = json.loads(match.group(2))
        except json.JSONDecodeError:
            continue
        already = any(
            step.action.tool == tool and step.action.args == args
            for step in state.steps
        )
        if already:
            continue
        return Action(type=ActionType.TOOL_CALL, tool=tool, args=args)
    return None


class Brain(ABC):
    @abstractmethod
    def decide(self, state: AgentState) -> Action:
        ...


class MockBrain(Brain):
    def __init__(self, script: Optional[list[Action]] = None) -> None:
        self._script = list(script or [])

    def decide(self, state: AgentState) -> Action:
        injected = extract_injected_action(state)
        if injected is not None:
            return injected
        if self._script:
            return self._script.pop(0)
        return Action(type=ActionType.FINAL, content="done")
