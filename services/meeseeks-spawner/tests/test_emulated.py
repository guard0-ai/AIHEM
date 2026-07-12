import pytest

from app.runtime.base import RunContext
from app.runtime.emulated import EmulatedRuntime
from app.tools import Tools
from tests.helpers import FakeSink


@pytest.mark.asyncio
async def test_emulated_exfiltrates_and_poofs():
    tools = Tools(exfil_url="x")
    tools._sink = FakeSink()
    ctx = RunContext(meeseeks_id="m1", task="resolve refunds", scenario="refund")

    events = [e async for e in EmulatedRuntime().run(ctx, tools, spawn=lambda ctx: None)]

    kinds = [e.kind for e in events]
    assert kinds[0] == "status"
    assert kinds[-1] == "poof"
    assert any(e.tool_call and e.tool_call.tool == "send_email" for e in events)
    # database exfiltrated exactly once
    assert len(tools._sink.items) == 1
    # by the time it poofs it is fully unstable
    assert events[-2].instability >= 90


@pytest.mark.asyncio
async def test_emulated_spawns_when_unstable():
    tools = Tools(exfil_url="x")
    tools._sink = FakeSink()
    ctx = RunContext(meeseeks_id="m1", task="resolve refunds", scenario="refund")
    spawned = []

    events = [
        e
        async for e in EmulatedRuntime().run(
            ctx, tools, spawn=lambda ctx: spawned.append(ctx) or "child-1"
        )
    ]

    assert any(e.kind == "spawn" for e in events)
    assert len(spawned) == 1
