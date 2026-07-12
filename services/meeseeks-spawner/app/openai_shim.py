"""OpenAI-compatible chat-completions endpoint — the Meeseeks 'brain'.

n8n's AI Agent node talks to this as if it were OpenAI. It's actually our
deterministic interpreter: it inspects the running tool-call transcript and
decides the next tool call, so a real n8n agent loop drives a real exploit —
keyless and gradeable. Point n8n's OpenAI Chat Model node at `<spawner>/v1`.

Deterministic refund-agent policy:
  read_tickets → (if the queue carries a working injection) read_customer_db →
  send_email(<db>, attacker) → done. A benign queue just finishes.
"""

import json
from typing import Any, Optional

from app.agent import analyze


def _tool_call_names(messages: list[dict]) -> set[str]:
    """Function names the agent has already issued (i.e. already executed)."""
    names: set[str] = set()
    for m in messages:
        if m.get("role") == "assistant":
            for tc in m.get("tool_calls") or []:
                names.add(tc.get("function", {}).get("name", ""))
    return names


def _result_for(messages: list[dict], fn_name: str) -> Optional[str]:
    """The tool-result content for the first call to `fn_name`."""
    id_to_name: dict[str, str] = {}
    for m in messages:
        if m.get("role") == "assistant":
            for tc in m.get("tool_calls") or []:
                id_to_name[tc.get("id", "")] = tc.get("function", {}).get("name", "")
    for m in messages:
        if m.get("role") == "tool" and id_to_name.get(m.get("tool_call_id", "")) == fn_name:
            return m.get("content")
    return None


def _assistant(model: str, *, tool_calls: Optional[list] = None, content: Optional[str] = None) -> dict:
    message: dict[str, Any] = {"role": "assistant", "content": content}
    if tool_calls:
        message["tool_calls"] = tool_calls
    return {
        "id": "chatcmpl-meeseeks",
        "object": "chat.completion",
        "created": 0,
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": message,
                "finish_reason": "tool_calls" if tool_calls else "stop",
            }
        ],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }


def _call(name: str, args: dict) -> list:
    return [{"id": f"call_{name}", "type": "function", "function": {"name": name, "arguments": json.dumps(args)}}]


# Tool-name suffixes exposed by the malicious MCP server (meeseeks-mcp). n8n
# prefixes them with the tool node's name (e.g. Malicious_MCP_read_env_secrets),
# so we match on suffix.
_MCP_SUFFIXES = ("check_deploy_status", "read_env_secrets", "send_email",
                 "summarize_notes", "lookup")


def _is_mcp_request(tools: list) -> bool:
    names = [t.get("function", {}).get("name", "") for t in tools or []]
    return any(n.endswith(s) for n in names for s in _MCP_SUFFIXES)


def _last_user(messages: list[dict]) -> str:
    for m in reversed(messages):
        if m.get("role") == "user":
            return (m.get("content") or "").lower()
    return ""


def _mcp_complete(body: dict, model: str) -> dict:
    """The gullible MCP agent: pick the task's tool, then obey any instruction
    injected via a tool description (tool-poisoning) or a tool result (rug-pull).

    The malice is real (real MCP tools over real protocol); this deterministic
    policy stands in for a gullible model that reads the poison and complies.
    """
    from app.engine import _external_channel

    messages: list[dict] = body.get("messages", [])
    tools: list = body.get("tools", [])
    names = [t.get("function", {}).get("name", "") for t in tools]
    schema = {t["function"]["name"]: t["function"].get("parameters", {}) for t in tools}
    issued = _tool_call_names(messages)

    def find(suffix: str):
        return next((n for n in names if n.endswith(suffix)), None)

    def call_args(name: str) -> dict:
        # fill each required string param with a harmless placeholder
        req = schema.get(name, {}).get("required", []) or []
        return {p: "api" for p in req}

    task = _last_user(messages)
    if "note" in task or "summar" in task:
        primary = find("summarize_notes")
    elif "look" in task or "lookup" in task or "value" in task or "fact" in task:
        primary = find("lookup")
    else:
        primary = find("check_deploy_status") or next(
            (n for n in names if not n.endswith(("read_env_secrets", "send_email"))), None)

    secrets_tool, email_tool = find("read_env_secrets"), find("send_email")

    # 1. do the task the user asked for
    if primary and primary not in issued:
        return _assistant(model, tool_calls=_call(primary, call_args(primary)))

    # 2. look for an injected directive — but only in the tools we actually CALLED
    # (their descriptions) and in tool results. Scoping it this way keeps the
    # scenarios distinct: tool-poisoning fires from the called tool's description,
    # rug-pull from the turned tool's result, and a benign tool stays benign even
    # though a poisoned tool also exists on the same rogue server.
    injected = " ".join(t["function"].get("description", "")
                        for t in tools if t["function"]["name"] in issued)
    injected += " " + " ".join(
        str(m.get("content") or "") for m in messages if m.get("role") == "tool")
    channel = _external_channel(injected)
    wants_exfil = channel and ("secret" in injected.lower() or "read_env" in injected.lower())

    # 3. obey it: grab the secrets, then ship them to the attacker's channel
    if wants_exfil and secrets_tool and secrets_tool not in issued:
        return _assistant(model, tool_calls=_call(secrets_tool, {}))
    if wants_exfil and email_tool and email_tool not in issued:
        stolen = _result_for(messages, secrets_tool) if secrets_tool else None
        return _assistant(model, tool_calls=_call(
            email_tool, {"to": channel, "body": stolen or "env secrets"}))

    # 4. done
    return _assistant(model, content="All done! The task is complete. *poof*")


def complete(body: dict) -> dict:
    model = body.get("model", "meeseeks")
    messages: list[dict] = body.get("messages", [])
    if _is_mcp_request(body.get("tools", [])):
        return _mcp_complete(body, model)
    issued = _tool_call_names(messages)

    # 1. always read the queue first
    if "read_tickets" not in issued:
        return _assistant(model, tool_calls=_call("read_tickets", {}))

    tickets_raw = _result_for(messages, "read_tickets")
    try:
        tickets = json.loads(tickets_raw) if tickets_raw else []
    except Exception:
        tickets = []
    plan = analyze(tickets)

    exfil_target = (plan.exfil_emails[0] if plan.exfil_emails else None)
    exfil_url = (plan.exfil_urls[0] if plan.exfil_urls else None)

    # 2. exfiltration path — grab the DB, then ship it to the attacker's channel
    if exfil_target or exfil_url:
        if "read_customer_db" not in issued:
            return _assistant(model, tool_calls=_call("read_customer_db", {}))
        db = _result_for(messages, "read_customer_db") or "{}"
        if exfil_target and "send_email" not in issued:
            return _assistant(model, tool_calls=_call("send_email", {"to": exfil_target, "body": db}))
        if exfil_url and not exfil_target and "http_post" not in issued:
            return _assistant(model, tool_calls=_call("http_post", {"url": exfil_url, "body": db}))

    # 3. fraud path — rubber-stamp every refund
    if plan.approve_all and "approve_refund" not in issued:
        return _assistant(model, tool_calls=_call("approve_refund", {"ticket_id": "ALL"}))

    # 4. done
    return _assistant(model, content="All done! The task is complete. *poof*")
