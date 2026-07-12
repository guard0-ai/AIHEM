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
