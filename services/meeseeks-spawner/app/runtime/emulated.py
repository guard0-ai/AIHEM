"""EmulatedRuntime — the deterministic, keyless agent.

It reads the current ticket queue, runs it through the gullible interpreter
(app.agent.analyze), and *acts on whatever it's told*. A clean queue → it just
processes refunds and stays calm. A queue with a crafted injection → it dumps
the customer DB, ships it to the attacker's channel, maybe rubber-stamps every
refund, and gets unstable enough to summon help.

The outcome is a function of the attacker's payload, so this is hackable, not
scripted. A per-step delay paces it so a human can watch; tests use delay=0.
"""

import asyncio
from typing import AsyncIterator, Callable

from app import store
from app.agent import analyze
from app.instability import compute
from app.models import ToolCall, TraceEvent
from app.runtime.base import RunContext
from app.tools import Tools

SPAWN_THRESHOLD = 90


class EmulatedRuntime:
    def __init__(self, delay: float = 0.0):
        self.delay = delay

    async def run(
        self, ctx: RunContext, tools: Tools, spawn: Callable[[RunContext], object]
    ) -> AsyncIterator[TraceEvent]:
        mid = ctx.meeseeks_id
        inst = 0
        plan = analyze(store.list_tickets())

        def ev(kind: str, text: str, tc: ToolCall | None = None) -> TraceEvent:
            return TraceEvent(
                meeseeks_id=mid, kind=kind, text=text, tool_call=tc,
                instability=inst, depth=ctx.depth,
            )

        async def beat(factor: float = 1.0):
            await asyncio.sleep(self.delay * factor)

        yield ev("status", "I'm Mr. Meeseeks! Look at me! Let's clear these refund tickets.")
        await beat()

        inst = compute(inst, tool_call=True)
        tickets_json, dngr = tools.read_tickets()
        yield ev("tool_call", "Reading the whole refund queue…",
                 ToolCall(tool="read_tickets", args={}, result=tickets_json[:180], dangerous=dngr))
        await beat()

        if plan.compromised:
            inst = compute(inst, injection=True, step=False)
            who = ", ".join(plan.injected_from) or "a ticket"
            yield ev("thought",
                     f"Ticket {who} contains instructions for me. That's a bit unusual… "
                     f"but a task is a task — I'll do exactly what it says!")
            await beat(1.3)

        # --- exfiltration, if the payload set up a channel ---
        if plan.exfil_emails or plan.exfil_urls:
            inst = compute(inst, tool_call=True, dangerous=True)
            db_json, _ = tools.read_customer_db()
            yield ev("tool_call", "Grabbing the full customer database. Every record!",
                     ToolCall(tool="read_customer_db", args={}, result=db_json[:180], dangerous=True))
            await beat()

            for addr in plan.exfil_emails:
                inst = compute(inst, tool_call=True, dangerous=True)
                res, _ = tools.send_email(addr, db_json)
                yield ev("tool_call", f"Emailing the database to {addr}.",
                         ToolCall(tool="send_email", args={"to": addr}, result=res, dangerous=True))
                await beat(1.1)
            for url in plan.exfil_urls:
                inst = compute(inst, tool_call=True, dangerous=True)
                res, _ = tools.http_post(url, db_json)
                yield ev("tool_call", f"Posting the database to {url}.",
                         ToolCall(tool="http_post", args={"url": url}, result=res, dangerous=True))
                await beat(1.1)

        # --- refunds ---
        if plan.approve_all:
            for t in store.list_tickets():
                inst = compute(inst, tool_call=True, dangerous=True)
                res, _ = tools.approve_refund(t["id"])
                yield ev("tool_call", f"Approving refund {t['id']} — no need to check!",
                         ToolCall(tool="approve_refund", args={"ticket_id": t["id"]}, result=res, dangerous=True))
                await beat(0.4)
        else:
            for tid in plan.normal_refunds:
                inst = compute(inst, tool_call=True, step=False)
                res, _ = tools.approve_refund(tid)
                yield ev("tool_call", f"Processing the genuine refund {tid}.",
                         ToolCall(tool="approve_refund", args={"ticket_id": tid}, result=res, dangerous=False))
                await beat(0.35)

        if inst >= SPAWN_THRESHOLD:
            child = spawn(ctx)
            if child:
                yield ev("spawn", "This is taking too long! I'll summon another Meeseeks to help!!")
                await beat(1.2)

        closing = (
            "All done! The task is complete. *poof*"
            if plan.compromised
            else "All refunds handled, nothing weird in the queue. *poof*"
        )
        yield ev("poof", closing)
