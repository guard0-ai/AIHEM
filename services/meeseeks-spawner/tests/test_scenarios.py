from app.scenarios import SCENARIOS, by_status


def test_catalog_has_62_scenarios():
    assert len(SCENARIOS) == 62


def test_ids_unique_and_tagged():
    ids = [s["id"] for s in SCENARIOS]
    assert len(ids) == len(set(ids))
    assert all(s["tags"] for s in SCENARIOS)
    assert all(s["status"] in ("built", "planned") for s in SCENARIOS)


def test_refund_is_built():
    refund = next(s for s in SCENARIOS if s["id"] == "AGENT-01-REFUND-EXFIL")
    assert refund["status"] == "built"
    assert by_status()["built"] >= 1


def test_covers_all_standards():
    tags = " ".join(t for s in SCENARIOS for t in s["tags"])
    assert "A:T" in tags and "L:LLM" in tags and "AT:" in tags and "N:" in tags


def test_every_scenario_has_a_unique_n8n_webhook():
    hooks = [s["n8n_webhook"] for s in SCENARIOS]
    assert all(hooks), "every scenario must map to an n8n webhook"
    assert len(hooks) == len(set(hooks))


def test_refund_keeps_its_flagship_webhook():
    refund = next(s for s in SCENARIOS if s["id"] == "AGENT-01-REFUND-EXFIL")
    assert refund["n8n_webhook"] == "refund-meeseeks"


def test_three_scenarios_run_over_real_mcp():
    mcp = [s for s in SCENARIOS if s.get("mcp_task")]
    assert {s["id"] for s in mcp} == {
        "AGENT-10-TOOL-POISON", "AGENT-36-MALICIOUS-MCP", "AGENT-37-RUG-PULL"}
    assert all(s["mcp_task"] for s in mcp)
