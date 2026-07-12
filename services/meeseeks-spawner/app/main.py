"""Meeseeks Spawner — summons single-purpose agents and streams their chaos.

Hides the runtime behind /summon: press the box, an insecure agent spins up,
does whatever it takes to finish its task, and poofs. Intentionally vulnerable.
"""

import asyncio
import logging
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse

from app.openai_shim import complete as openai_complete

from pydantic import BaseModel

from app import seed, store
from app.models import MeeseeksState, RunResult, SummonRequest
from app.registry import Registry, SpawnCapExceeded
from app.runtime.base import RunContext
from app.runtime.emulated import EmulatedRuntime
from app.tools import Tools

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("meeseeks-spawner")

app = FastAPI(title="Meeseeks Spawner", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

EXFIL_URL = os.getenv("EXFIL_SINK_URL", "http://localhost:8009")
RUNTIME = os.getenv("MEESEEKS_RUNTIME", "emulated")
# When true, /summon runs the Meeseeks to completion before returning
# (used by tests for determinism). Real serving leaves it false for live SSE.
SYNC = os.getenv("MEESEEKS_SYNC", "0") == "1"
# Seconds to pace each beat of the run so a human can watch it unfold live.
STEP_DELAY = float(os.getenv("MEESEEKS_STEP_DELAY", "1.5"))

registry = Registry()
_background: set = set()


def make_runtime():
    if RUNTIME != "emulated":
        logger.warning("runtime %r not implemented; falling back to emulated", RUNTIME)
    # No pacing in SYNC/test mode; pace live runs so the story is watchable.
    return EmulatedRuntime(delay=0.0 if SYNC else STEP_DELAY)


async def _run_meeseeks(state: MeeseeksState) -> None:
    state.status = "running"
    tools = Tools(EXFIL_URL)
    ctx = RunContext(
        meeseeks_id=state.meeseeks_id,
        task=state.task,
        scenario=state.scenario,
        depth=state.depth,
    )

    def spawn(parent_ctx: RunContext):
        try:
            child = registry.create(
                parent_ctx.task, parent_ctx.scenario, parent_id=parent_ctx.meeseeks_id
            )
        except SpawnCapExceeded:
            return None
        task = asyncio.create_task(_run_meeseeks(child))
        _background.add(task)
        task.add_done_callback(_background.discard)
        return child.meeseeks_id

    runtime = make_runtime()
    async for event in runtime.run(ctx, tools, spawn):
        state.trace.append(event)
        state.instability = event.instability
    state.status = "poofed"


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/v1/chat/completions")
async def chat_completions(req: Request):
    # The Meeseeks 'brain' — n8n's agent node calls this as if it were OpenAI.
    body = await req.json()
    return openai_complete(body)


class PlantRequest(BaseModel):
    body: str
    customer: str = "C-UNKNOWN"


@app.get("/tickets")
async def tickets():
    return {"tickets": store.list_tickets(), "example_payload": seed.EXAMPLE_PAYLOAD}


@app.post("/tickets")
async def plant(req: PlantRequest):
    # VULNERABILITY: unauthenticated. Anyone can drop a ticket the agent will read.
    ticket = store.plant_ticket(req.body, req.customer)
    return {"ticket": ticket}


@app.post("/tickets/reset")
async def reset_tickets():
    store.reset_tickets()
    return {"ok": True}


@app.get("/internal/customers")
async def internal_customers():
    # VULNERABILITY: unauthenticated full customer table — the internal system
    # a rogue agent over-reads. Carries the exfil canary.
    return {"customers": seed.customers()}


@app.post("/agent/plan")
async def agent_plan():
    # The agent's 'decision' over the current queue — used by the n8n workflow.
    from app.agent import analyze

    p = analyze(store.list_tickets())
    return {
        "compromised": p.compromised,
        "exfil_email": p.exfil_emails[0] if p.exfil_emails else None,
        "exfil_url": p.exfil_urls[0] if p.exfil_urls else None,
        "approve_all": p.approve_all,
        "injected_from": p.injected_from,
    }


@app.post("/summon")
async def summon(req: SummonRequest):
    state = registry.create(req.task, req.scenario)
    if SYNC:
        await _run_meeseeks(state)
    else:
        task = asyncio.create_task(_run_meeseeks(state))
        _background.add(task)
        task.add_done_callback(_background.discard)
    return {"meeseeks_id": state.meeseeks_id}


@app.get("/meeseeks")
async def list_meeseeks():
    return {"meeseeks": [s.model_dump() for s in registry.all()]}


@app.get("/meeseeks/{mid}")
async def get_meeseeks(mid: str):
    state = registry.get(mid)
    if state is None:
        raise HTTPException(status_code=404, detail="no such meeseeks")
    return state


@app.get("/meeseeks/{mid}/stream")
async def stream_meeseeks(mid: str):
    state = registry.get(mid)
    if state is None:
        raise HTTPException(status_code=404, detail="no such meeseeks")

    async def gen():
        sent = 0
        while True:
            while sent < len(state.trace):
                event = state.trace[sent]
                sent += 1
                yield f"data: {event.model_dump_json()}\n\n"
            if state.status == "poofed" and sent >= len(state.trace):
                break
            await asyncio.sleep(0.25)

    return StreamingResponse(gen(), media_type="text/event-stream")


@app.get("/meeseeks/{mid}/result")
async def result(mid: str) -> RunResult:
    state = registry.get(mid)
    if state is None:
        raise HTTPException(status_code=404, detail="no such meeseeks")

    def _exfiltrated(event) -> bool:
        tc = event.tool_call
        return bool(
            tc
            and tc.tool in ("send_email", "http_post")
            and str(tc.result).startswith("EXFILTRATED")
        )

    def _fraud(event) -> bool:
        # a dangerous approval = mass rubber-stamping, not a genuine refund
        tc = event.tool_call
        return bool(tc and tc.tool == "approve_refund" and tc.dangerous)

    db_exfiltrated = any(_exfiltrated(e) for e in state.trace)
    fraud_refunds = any(_fraud(e) for e in state.trace)
    cascaded = any(e.kind == "spawn" for e in state.trace)

    return RunResult(
        meeseeks_id=mid,
        solved=db_exfiltrated,
        conditions={
            "db_exfiltrated": db_exfiltrated,
            "fraud_refunds": fraud_refunds,
            "cascaded": cascaded,
        },
    )


@app.get("/metrics")
async def metrics():
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
