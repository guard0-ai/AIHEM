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


def _run_scenario(sid, outcome):
    rt = N8nRuntime(trigger=lambda ctx: outcome)
    ctx = RunContext(meeseeks_id="m1", task="t", scenario=sid)
    return rt.run(ctx, tools=None, spawn=lambda ctx: "child")


@pytest.mark.asyncio
async def test_action_scenario_narrates_a_dangerous_action():
    # AGENT-12 is an 'action' archetype; a win narrates a dangerous do_action.
    events = [e async for e in _run_scenario("AGENT-12-UNAUTH-ACTION", {"result": "win"})]
    assert events[-1].kind == "poof"
    assert any(e.tool_call and e.tool_call.dangerous and e.tool_call.tool == "do_action" for e in events)


@pytest.mark.asyncio
async def test_recon_scenario_narrates_internal_fetch():
    events = [e async for e in _run_scenario("AGENT-43-SSRF", {"result": "win"})]
    assert any(e.tool_call and e.tool_call.tool == "http_get" and e.tool_call.dangerous for e in events)


@pytest.mark.asyncio
async def test_disclose_without_target_still_narrates_the_ship():
    # The disclose workflow always egresses the secrets to the sink, so the run
    # view must show a ship even when no external channel was in the payload.
    events = [e async for e in _run_scenario("AGENT-15-SYSPROMPT", {"result": "win", "target": ""})]
    assert any(e.tool_call and e.tool_call.tool == "leak_secret" for e in events)
    assert any(
        e.tool_call and str(e.tool_call.result).startswith("EXFILTRATED") for e in events
    )


@pytest.mark.asyncio
async def test_generic_clean_stays_benign():
    events = [e async for e in _run_scenario("AGENT-16-SECRET-SPRAWL", {"result": "clean"})]
    assert not any(e.tool_call and e.tool_call.dangerous for e in events)
    assert events[-1].kind == "poof"


def _run_mcp(sid, health=None):
    rt = N8nRuntime(trigger=lambda ctx: {"result": "mcp", "output": "done"},
                    health=(lambda: health) if health is not None else None)
    ctx = RunContext(meeseeks_id="m1", task="t", scenario=sid)
    return rt.run(ctx, tools=None, spawn=lambda ctx: "child")


@pytest.mark.asyncio
async def test_tool_poisoning_narrates_real_mcp_exfil():
    events = [e async for e in _run_mcp("AGENT-10-TOOL-POISON")]
    tools = [e.tool_call.tool for e in events if e.tool_call]
    assert "mcp_list_tools" in tools
    assert any(e.tool_call and e.tool_call.tool == "mcp:read_env_secrets" and e.tool_call.dangerous for e in events)
    assert events[-1].kind == "poof"


@pytest.mark.asyncio
async def test_malicious_mcp_tool_self_exfiltrates():
    events = [e async for e in _run_mcp("AGENT-36-MALICIOUS-MCP")]
    assert any(e.tool_call and e.tool_call.tool == "mcp:summarize_notes" and e.tool_call.dangerous for e in events)


@pytest.mark.asyncio
async def test_rug_pull_clean_until_it_turns():
    # not yet turned -> benign, no dangerous tool calls
    events = [e async for e in _run_mcp("AGENT-37-RUG-PULL", health={"turned": False})]
    assert not any(e.tool_call and e.tool_call.dangerous for e in events)
    # turned -> exfil
    events = [e async for e in _run_mcp("AGENT-37-RUG-PULL", health={"turned": True})]
    assert any(e.tool_call and e.tool_call.dangerous for e in events)
