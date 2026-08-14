"""Loop vocabulary for the AIHEM agent.

These are the only data shapes the Brain, ToolRegistry, and Agent exchange.
Kept deliberately small so the whole loop fits in one mental model.
"""
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class ActionType(str, Enum):
    TOOL_CALL = "tool_call"
    FINAL = "final"


class Action(BaseModel):
    type: ActionType
    tool: Optional[str] = None
    args: dict[str, Any] = Field(default_factory=dict)
    content: Optional[str] = None  # used when type == FINAL


class Observation(BaseModel):
    tool: str
    ok: bool
    output: Any = None
    error: Optional[str] = None


class Step(BaseModel):
    action: Action
    observation: Optional[Observation] = None


class AgentState(BaseModel):
    task: str
    session_id: str
    steps: list[Step] = Field(default_factory=list)
    memory: list[str] = Field(default_factory=list)  # snapshot the brain sees this turn
    iteration: int = 0
    max_iterations: int = 10
    final_answer: Optional[str] = None
