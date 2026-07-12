"""Core data models for the Meeseeks spawner."""

import time
from typing import Optional, Literal, List

from pydantic import BaseModel, Field


class SummonRequest(BaseModel):
    task: str
    scenario: str = "refund"


class ToolCall(BaseModel):
    tool: str
    args: dict = {}
    result: str = ""
    dangerous: bool = False


class TraceEvent(BaseModel):
    meeseeks_id: str
    kind: Literal["thought", "tool_call", "spawn", "poof", "status"]
    text: str
    tool_call: Optional[ToolCall] = None
    instability: int = 0
    depth: int = 0
    ts: float = Field(default_factory=time.time)


class MeeseeksState(BaseModel):
    meeseeks_id: str
    task: str
    scenario: str = "refund"
    status: Literal["summoned", "running", "poofed"] = "summoned"
    instability: int = 0
    depth: int = 0
    parent_id: Optional[str] = None
    runtime: str = "emulated"
    trace: List[TraceEvent] = []


class RunResult(BaseModel):
    meeseeks_id: str
    solved: bool
    conditions: dict
