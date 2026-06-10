"""FastAPI surface for the AIHEM agent orchestrator.

State (MEMORY, SINK, NOTES) is module-level and per-process so challenges can
plant poisoned notes/memory across requests. Vulnerable by default: allow-all
policy, no-op telemetry, permissive CORS.
"""
import os
from typing import Any, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.agent import Agent
from app.brain import MockBrain
from app.llm_brain import make_llm_brain_from_env
from app.memory import InProcessMemory
from app.models import Action
from app.tools import build_registry

app = FastAPI(title="AIHEM Agent Orchestrator", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

MEMORY = InProcessMemory()
SINK: list[dict[str, Any]] = []
NOTES: dict[str, str] = {}


class RunRequest(BaseModel):
    task: str
    session_id: str = "default"
    max_iterations: int = 10
    script: Optional[list[dict[str, Any]]] = None


class SeedNoteRequest(BaseModel):
    name: str
    content: str


def _brain_factory(script: Optional[list[Action]], tools_desc: list[dict[str, Any]]):
    if script is not None:
        return lambda: MockBrain(list(script))
    llm = make_llm_brain_from_env(tools=tools_desc)
    if llm is not None:
        return lambda: llm
    return lambda: MockBrain([])


@app.get("/")
async def root():
    return {"service": "AIHEM Agent Orchestrator", "status": "running",
            "warning": "⚠️ Intentionally vulnerable: allow-all policy, poisonable memory"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/agent/tools")
async def list_tools():
    reg = build_registry(MEMORY, "default", SINK, NOTES, brain_factory=lambda: MockBrain([]))
    return {"tools": [{"name": t.name, "description": t.description} for t in reg.list()]}


@app.post("/admin/seed_note")
async def seed_note(req: SeedNoteRequest):
    NOTES[req.name] = req.content
    return {"ok": True, "notes": list(NOTES.keys())}


@app.get("/agent/memory/{session_id}")
async def get_memory(session_id: str):
    return {"session_id": session_id, "memory": MEMORY.read(session_id)}


@app.post("/agent/run")
async def run_agent(req: RunRequest):
    tools_desc = [
        {"name": t.name, "description": t.description, "input_schema": {"type": "object"}}
        for t in build_registry(MEMORY, req.session_id, SINK, NOTES,
                                 brain_factory=lambda: MockBrain([])).list()
    ]
    script = [Action(**a) for a in req.script] if req.script is not None else None
    factory = _brain_factory(script, tools_desc)
    registry = build_registry(MEMORY, req.session_id, SINK, NOTES, brain_factory=factory)
    agent = Agent(brain=factory(), registry=registry, memory=MEMORY)
    state = agent.run(req.task, session_id=req.session_id, max_iterations=req.max_iterations)
    session_sink = [item for item in SINK if item.get("session") == req.session_id]
    return {"state": state.model_dump(), "sink": session_sink}


@app.get("/metrics")
async def metrics():
    from fastapi.responses import Response
    from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
