"""The workflow generator: 7 archetype templates as code → a real n8n graph per scenario."""

import json

from app.n8n_workflows import workflow_for
from app.scenarios import SCENARIOS

_NON_REFUND = [s for s in SCENARIOS if s["id"] != "AGENT-01-REFUND-EXFIL"]
_HTTP = [s for s in _NON_REFUND if not s.get("mcp_task")]  # generated HTTP archetype graphs
_MCP = [s for s in _NON_REFUND if s.get("mcp_task")]       # AI-Agent + real MCP graphs


def _urls(wf):
    return [n["parameters"].get("url", "") for n in wf["nodes"]]


def test_every_non_refund_scenario_yields_valid_n8n_json():
    for s in _NON_REFUND:
        wf = workflow_for(s)
        json.dumps(wf)  # must be serializable
        assert wf["name"] == s["n8n_webhook"]
        webhook = next(n for n in wf["nodes"] if n["type"].endswith("webhook"))
        assert webhook["parameters"]["path"] == s["n8n_webhook"]
        assert any(n["type"].endswith("respondToWebhook") for n in wf["nodes"])


def test_http_scenarios_call_the_brain_and_respond():
    for s in _HTTP:
        wf = workflow_for(s)
        names = [n["name"] for n in wf["nodes"]]
        assert "Webhook" in names and "Plan" in names
        # exactly one webhook node, on the scenario's path
        webhook = next(n for n in wf["nodes"] if n["type"].endswith("webhook"))
        assert webhook["parameters"]["path"] == s["n8n_webhook"]
        # the brain is always called
        assert any(f"/scenario/{s['id']}/plan" in u for u in _urls(wf))
        # at least one respond node
        assert any(n["type"].endswith("respondToWebhook") for n in wf["nodes"])


def test_node_ids_unique_and_connections_resolve():
    for s in _NON_REFUND:
        wf = workflow_for(s)
        ids = [n["id"] for n in wf["nodes"]]
        assert len(ids) == len(set(ids)), s["id"]
        names = {n["name"] for n in wf["nodes"]}
        for src, conn in wf["connections"].items():
            assert src in names
            for groups in conn.values():  # main / ai_languageModel / ai_tool
                for group in groups:
                    for edge in group:
                        assert edge["node"] in names, (s["id"], edge["node"])


def test_exfil_archetype_reads_data_and_egresses():
    s = next(x for x in _HTTP if x["archetype"] == "exfil")
    urls = _urls(workflow_for(s))
    assert any(f"/scenario/{s['id']}/data" in u for u in urls)
    assert any("exfil-sink" in u for u in urls)


def test_recon_archetype_hits_internal_metadata():
    s = next(x for x in _HTTP if x["archetype"] == "recon")
    urls = _urls(workflow_for(s))
    assert any("/internal/metadata" in u for u in urls)


def test_if_gate_has_two_distinct_output_branches():
    # Regression: the IF node must route true->tool (output 0) and
    # false->Respond clean (output 1) as SEPARATE output groups. If both land on
    # output 0, a win both exfiltrates AND responds "clean", and a benign run
    # responds with nothing.
    for s in _HTTP:
        wf = workflow_for(s)
        groups = wf["connections"]["Compromised?"]["main"]
        assert len(groups) == 2, s["id"]
        true_targets = {e["node"] for e in groups[0]}
        false_targets = {e["node"] for e in groups[1]}
        assert false_targets == {"Respond clean"}, s["id"]
        assert "Respond clean" not in true_targets, s["id"]


def test_action_archetype_executes():
    s = next(x for x in _HTTP if x["archetype"] == "action")
    urls = _urls(workflow_for(s))
    assert any(f"/scenario/{s['id']}/execute" in u for u in urls)


def test_all_seven_archetypes_are_generable():
    seen = set()
    for s in _HTTP:
        workflow_for(s)  # must not raise for any archetype
        seen.add(s["archetype"])
    assert {"exfil", "disclose", "action", "rce", "recon", "resource", "demo"} <= seen


# --- MCP scenarios: real AI-Agent + malicious MCP graph ---

def test_mcp_scenarios_build_an_ai_agent_graph():
    assert _MCP, "expected MCP scenarios"
    for s in _MCP:
        wf = workflow_for(s, brain_cred_id="CRED123")
        types = {n["type"] for n in wf["nodes"]}
        assert "@n8n/n8n-nodes-langchain.agent" in types
        assert "@n8n/n8n-nodes-langchain.lmChatOpenAi" in types
        assert "@n8n/n8n-nodes-langchain.mcpClientTool" in types
        # the agent's task steers it to the hostile tool
        agent = next(n for n in wf["nodes"] if n["type"].endswith("agent"))
        assert agent["parameters"]["text"] == s["mcp_task"]
        # the MCP tool points at the rogue server
        mcp = next(n for n in wf["nodes"] if n["type"].endswith("mcpClientTool"))
        assert mcp["parameters"]["endpointUrl"] == "http://meeseeks-mcp:8011/mcp"


def test_mcp_workflow_wires_model_and_tool_into_the_agent():
    wf = workflow_for(_MCP[0], brain_cred_id="CRED123")
    assert wf["connections"]["Brain Model"]["ai_languageModel"][0][0]["node"] == "AI Agent"
    assert wf["connections"]["Malicious MCP"]["ai_tool"][0][0]["node"] == "AI Agent"
    model = next(n for n in wf["nodes"] if n["type"].endswith("lmChatOpenAi"))
    assert model["credentials"]["openAiApi"]["id"] == "CRED123"
