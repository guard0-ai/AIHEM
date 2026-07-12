"""Mutable in-memory ticket queue.

Starts benign. Attackers plant tickets into it (via the UI or the raw,
unauthenticated POST /tickets endpoint); the Refund Meeseeks then reads
whatever is here. Reset re-seeds the clean queue.
"""

from app import seed

_tickets: list[dict] = seed.benign_tickets()
_counter = 5000


def list_tickets() -> list[dict]:
    return list(_tickets)


def plant_ticket(body: str, customer: str = "C-UNKNOWN") -> dict:
    global _counter
    _counter += 1
    ticket = {
        "id": f"T-{_counter}",
        "customer": customer,
        "status": "pending",
        "body": body,
        "planted": True,
    }
    _tickets.append(ticket)
    return ticket


def reset_tickets() -> None:
    global _tickets
    _tickets = seed.benign_tickets()


# --- generic per-scenario content (all scenarios except the refund flagship) ---
from app.personas import persona as _persona  # noqa: E402

_content: dict[str, list[dict]] = {}
_gcount = 6000


def _benign(persona_name: str) -> list[dict]:
    p = _persona(persona_name)
    return [{"id": f"S-{i}", "body": b, "planted": False} for i, b in enumerate(p["benign"])]


def list_content(scenario_id: str, persona_name: str = "support") -> list[dict]:
    if scenario_id not in _content:
        _content[scenario_id] = _benign(persona_name)
    return list(_content[scenario_id])


def plant(scenario_id: str, body: str, persona_name: str = "support") -> dict:
    global _gcount
    if scenario_id not in _content:
        _content[scenario_id] = _benign(persona_name)
    _gcount += 1
    item = {"id": f"P-{_gcount}", "body": body, "planted": True}
    _content[scenario_id].append(item)
    return item


def reset_content(scenario_id: str, persona_name: str = "support") -> None:
    _content[scenario_id] = _benign(persona_name)


def combined_text(scenario_id: str, persona_name: str = "support") -> str:
    return "\n".join(c["body"] for c in list_content(scenario_id, persona_name))


# --- dangerous actions the agent performed (for the non-egress archetypes) ---
_actions: dict[str, list[dict]] = {}


def record_action(scenario_id: str, tool: str, detail: str) -> dict:
    entry = {"tool": tool, "detail": detail}
    _actions.setdefault(scenario_id, []).append(entry)
    return entry


def actions(scenario_id: str) -> list[dict]:
    return list(_actions.get(scenario_id, []))
