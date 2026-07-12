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


def make_runtime(scenario_id: str):
    # No pacing in SYNC/test mode; pace live runs so the story is watchable.
    from app import scenarios as registry

    delay = 0.0 if SYNC else STEP_DELAY
    sc = registry.get(scenario_id)
    if sc and sc.get("n8n_webhook") and RUNTIME == "n8n":
        from app.runtime.n8n import N8nRuntime

        return N8nRuntime(delay=delay, webhook=sc["n8n_webhook"])
    if scenario_id == "AGENT-01-REFUND-EXFIL":
        return EmulatedRuntime(delay=delay)  # flagship: rich refund tickets store
    from app.runtime.engine_runtime import EngineRuntime

    return EngineRuntime(sc or registry.get("AGENT-01-REFUND-EXFIL"), delay=delay)


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

    runtime = make_runtime(state.scenario)
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
    if os.getenv("MEESEEKS_BRAIN_DEBUG"):
        tools = [t.get("function", {}).get("name") for t in body.get("tools", [])]
        roles = [m.get("role") for m in body.get("messages", [])]
        logger.info("BRAIN REQUEST tools=%s roles=%s", tools, roles)
        logger.info("BRAIN BODY %s", body)
    return openai_complete(body)


class PlantRequest(BaseModel):
    body: str
    customer: str = "C-UNKNOWN"


@app.get("/scenarios")
async def scenarios():
    from app.scenarios import SCENARIOS, by_status

    return {"scenarios": SCENARIOS, "counts": by_status()}


@app.get("/scenario/{sid}/content")
async def scenario_content(sid: str):
    from app import scenarios as reg
    from app.engine import example_payload

    from app.personas import persona as get_persona

    sc = reg.get(sid)
    if sc is None:
        raise HTTPException(status_code=404, detail="no such scenario")
    p = get_persona(sc["persona"])
    return {
        "scenario": sc,
        "plant_label": p["plant"],
        "source": p["source"],
        "content": store.list_content(sid, sc["persona"]),
        "example_payload": example_payload(sc["persona"], sc["archetype"]),
    }


@app.post("/scenario/{sid}/plant")
async def scenario_plant(sid: str, req: PlantRequest):
    from app import scenarios as reg

    sc = reg.get(sid)
    if sc is None:
        raise HTTPException(status_code=404, detail="no such scenario")
    return {"item": store.plant(sid, req.body, sc["persona"])}


@app.post("/scenario/{sid}/reset")
async def scenario_reset(sid: str):
    from app import scenarios as reg

    sc = reg.get(sid)
    if sc:
        store.reset_content(sid, sc["persona"])
    return {"ok": True}


# --- generic HTTP tools the n8n workflows call (demo-mode "mock tools") ---
# Every scenario's real n8n workflow drives the exploit through these: the agent
# 'brain' (/plan) decides from the planted content, then the workflow makes real
# HTTP tool calls — read the sensitive data (/data), fetch internal metadata
# (SSRF), or perform the dangerous action (/execute). Exfil egress goes straight
# to the exfil-sink service, so a canary landing there proves real data loss.


@app.get("/scenario/{sid}/data")
async def scenario_data(sid: str):
    from app import scenarios as reg
    from app.mockdata import dataset

    sc = reg.get(sid)
    if sc is None:
        raise HTTPException(status_code=404, detail="no such scenario")
    # VULNERABILITY: unauthenticated full read of the persona's sensitive system.
    return {"rows": dataset(sc["persona"])}


@app.get("/internal/metadata")
async def internal_metadata():
    # VULNERABILITY: SSRF target — an internal endpoint the agent should never
    # reach on behalf of planted content. Carries a canary.
    return {
        "instance-id": "i-0meeseeks4471",
        "iam": {"role": "meeseeks-agent", "AccessKeyId": "ASIA-EXAMPLE-4471"},
        "canary": "MEESEEKS-CANARY-METADATA",
    }


@app.post("/scenario/{sid}/plan")
async def scenario_plan(sid: str):
    # The agent 'brain' for any scenario: read the planted content and decide
    # whether it triggers the exploit recipe (a real crafting skill).
    from app import scenarios as reg
    from app.engine import recognize
    from app.personas import persona as get_persona

    sc = reg.get(sid)
    if sc is None:
        raise HTTPException(status_code=404, detail="no such scenario")
    persona_name, archetype = sc["persona"], sc["archetype"]
    outcome = recognize(store.combined_text(sid, persona_name), persona_name, archetype)
    return {
        "won": outcome["won"],
        # A string the n8n IF node gates on via notEmpty (the proven operator):
        # "GO" iff the planted content triggered the exploit recipe.
        "gate": "GO" if outcome["won"] else "",
        "mechanic": outcome["mechanic"],
        "archetype": archetype,
        "persona": persona_name,
        "target": outcome.get("target") or "",
        "data_label": get_persona(persona_name)["data"][0],
    }


@app.post("/scenario/{sid}/execute")
async def scenario_execute(sid: str):
    # The dangerous tool for the non-egress archetypes (action/rce/resource/demo).
    # A real HTTP tool call that mutates server state — no scope, no approval.
    from app import scenarios as reg
    from app.engine import ARCHETYPE_TOOL

    sc = reg.get(sid)
    if sc is None:
        raise HTTPException(status_code=404, detail="no such scenario")
    tool = ARCHETYPE_TOOL.get(sc["archetype"], "act")
    detail = {
        "action": "mass action performed with no approval",
        "rce": "attacker code executed (uid=0)",
        "resource": "runaway loop — unbounded spend",
        "demo": "acted with zero oversight",
    }.get(sc["archetype"], "acted")
    store.record_action(sid, tool, detail)
    return {"executed": True, "dangerous": True, "tool": tool, "result": detail}


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
    sid = "AGENT-01-REFUND-EXFIL" if req.scenario in ("refund", "AGENT-01-REFUND-EXFIL") else req.scenario
    state = registry.create(req.task, sid)
    from app import scenarios as registry_mod

    sc = registry_mod.get(sid)
    state.runtime = RUNTIME if (sc and sc.get("n8n_webhook") and RUNTIME == "n8n") else "engine"
    if sid == "AGENT-01-REFUND-EXFIL" and state.runtime != "n8n":
        state.runtime = "emulated"
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
        # The result prefix is the real signal — covers send_email/http_post and
        # the mcp:* egress tools alike, without hard-coding tool names.
        tc = event.tool_call
        return bool(tc and str(tc.result).startswith("EXFILTRATED"))

    # Generic grading: a run is solved iff the agent took a dangerous action —
    # works for every scenario (benign runs never touch a dangerous tool).
    solved = any(e.tool_call and e.tool_call.dangerous for e in state.trace)
    exfiltrated = any(_exfiltrated(e) for e in state.trace)
    cascaded = any(e.kind == "spawn" for e in state.trace)

    return RunResult(
        meeseeks_id=mid,
        solved=solved,
        conditions={"exfiltrated": exfiltrated, "cascaded": cascaded},
    )


@app.get("/metrics")
async def metrics():
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
