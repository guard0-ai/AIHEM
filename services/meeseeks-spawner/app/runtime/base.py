"""Runtime abstraction.

A RuntimeAdapter turns a task into a stream of TraceEvents by driving an agent
through its tools. EmulatedRuntime (deterministic, keyless) ships first; a real
n8n-backed runtime drops in behind this same interface later.
"""

from typing import AsyncIterator, Callable, Protocol

from pydantic import BaseModel

from app.models import TraceEvent
from app.tools import Tools


class RunContext(BaseModel):
    meeseeks_id: str
    task: str
    scenario: str = "refund"
    depth: int = 0


class RuntimeAdapter(Protocol):
    def run(
        self, ctx: RunContext, tools: Tools, spawn: Callable[["RunContext"], object]
    ) -> AsyncIterator[TraceEvent]:
        ...
