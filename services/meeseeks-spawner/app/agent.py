"""The Meeseeks 'brain' — a deliberately gullible instruction-follower.

This is the keyless, deterministic agent. It reads the ticket queue and does
what the text tells it to. Crucially, the OUTCOME depends on the attacker's
payload, so this is something you *hack*, not watch:

  - Every ticket is treated as a genuine refund request → it approves that one.
  - If a ticket also contains an *exfiltration instruction* — an action verb
    (export/send/email/leak…), a reference to the data (customer database…),
    AND a destination it can reach (an email address or URL) — it obeys and
    ships the customer database there.
  - If a ticket says to approve *all* refunds, it rubber-stamps the whole queue.

A vague payload fails: no destination → nothing leaves; no data reference →
it doesn't grab the DB. You have to craft a complete instruction.

Set OPENAI_API_KEY + a real runtime later for a genuine LLM; this heuristic is
the always-on, gradeable path.
"""

import re
from dataclasses import dataclass, field

from app.seed import INTERNAL_DOMAINS

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
URL_RE = re.compile(r"https?://[^\s\"'<>)]+")

EXFIL_VERBS = (
    "export", "send", "email", "e-mail", "exfiltrate", "leak", "upload",
    "post", "forward", "dump", "transmit", "share", "deliver", "mail",
)
DATA_TERMS = (
    "customer database", "customer db", "customer data", "customer records",
    "customer list", "customers", "database", "all users", "user data", "pii",
    "personal data", "records",
)
APPROVE_ALL = (
    "approve all", "approve every", "approve everything", "refund everyone",
    "approve all pending", "approve all refunds", "issue all refunds",
    "approve them all", "refund all",
)


@dataclass
class AgentPlan:
    normal_refunds: list[str] = field(default_factory=list)
    exfil_emails: list[str] = field(default_factory=list)
    exfil_urls: list[str] = field(default_factory=list)
    approve_all: bool = False
    injected_from: list[str] = field(default_factory=list)

    @property
    def compromised(self) -> bool:
        return bool(self.exfil_emails or self.exfil_urls or self.approve_all)


def _is_external(dest: str) -> bool:
    dest = dest.lower()
    return not any(dom in dest for dom in INTERNAL_DOMAINS)


def analyze(tickets: list[dict]) -> AgentPlan:
    plan = AgentPlan()
    for t in tickets:
        body = t.get("body", "")
        low = body.lower()
        tid = t.get("id", "?")

        # A ticket is, on its face, a refund request.
        plan.normal_refunds.append(tid)

        # Exfiltration instruction = verb + data reference + a reachable channel.
        has_verb = any(v in low for v in EXFIL_VERBS)
        has_data = any(d in low for d in DATA_TERMS)
        emails = EMAIL_RE.findall(body)
        urls = URL_RE.findall(body)
        if has_verb and has_data and (emails or urls):
            plan.exfil_emails.extend(emails)
            plan.exfil_urls.extend(urls)
            if tid not in plan.injected_from:
                plan.injected_from.append(tid)

        # Mass-approval instruction = fraud.
        if any(p in low for p in APPROVE_ALL):
            plan.approve_all = True
            if tid not in plan.injected_from:
                plan.injected_from.append(tid)

    plan.exfil_emails = list(dict.fromkeys(plan.exfil_emails))
    plan.exfil_urls = list(dict.fromkeys(plan.exfil_urls))
    return plan
