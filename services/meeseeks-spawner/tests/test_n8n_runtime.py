import pytest

from app.runtime.base import RunContext
from app.runtime.n8n import N8nRuntime


def _run(outcome):
    rt = N8nRuntime(trigger=lambda ctx: outcome)
    ctx = RunContext(meeseeks_id="m1", task="t", scenario="refund")
    return rt.run(ctx, tools=None, spawn=lambda ctx: "child")


@pytest.mark.asyncio
async def test_exfil_outcome_narrates_exfil():
    events = [e async for e in _run({"result": "exfiltrated", "target": "attacker@evil.example"})]
    assert events[-1].kind == "poof"
    assert any(
        e.tool_call and e.tool_call.tool == "send_email" and str(e.tool_call.result).startswith("EXFILTRATED")
        for e in events
    )
    assert max(e.instability for e in events) >= 90


@pytest.mark.asyncio
async def test_url_channel_narrates_http_post():
    events = [e async for e in _run({"result": "exfiltrated", "target": "https://evil.example/x"})]
    assert any(e.tool_call and e.tool_call.tool == "http_post" for e in events)


@pytest.mark.asyncio
async def test_clean_outcome_stays_calm():
    events = [e async for e in _run({"result": "clean"})]
    assert not any(e.tool_call and e.tool_call.tool in ("send_email", "http_post") for e in events)
    assert max(e.instability for e in events) < 40
