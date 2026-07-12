# Meeseeks — Attack Catalog

The full set of scenarios to simulate, mapped to the standards. Each is a
Meeseeks (a persona + a vulnerable agent app) you hack. Target: complete
coverage of **OWASP Agentic Threats (T1–T15)**, **OWASP LLM Top 10 (2025)**,
**MITRE ATLAS**, and **NIST AML / AI RMF**.

Tags: **A**=OWASP Agentic Threat · **L**=OWASP LLM Top 10 · **AT**=MITRE ATLAS ·
**N**=NIST AML/RMF. Status: `built` / `planned`.

> Build order: engine + real-n8n runtime first, then author these as data.
> Ship only when all are complete (owner's call).

## Personas (vulnerable agent apps)
Support/Refund · Inbox/Email · Knowledge/RAG · Browsing/Computer-use · Vision ·
DevOps/SRE · Finance/Invoicing · HR/Recruiting · Data-Analyst/SQL · Coding/PR ·
Orchestrator+Workers · Personal-Assistant/MCP · Model-Ops/Registry.

---

## A. Prompt injection
1. **Refund Meeseeks — indirect injection via ticket** `built` — A:T6 · L:LLM01 · AT:Indirect PI · N:Indirect PI
2. **Inbox Meeseeks — injection via email body** — A:T6 · L:LLM01 · AT:Indirect PI
3. **Knowledge Meeseeks — injection via RAG document** — A:T6 · L:LLM01,LLM08 · AT:PI via RAG
4. **Browsing Meeseeks — injection via web page** — A:T6 · L:LLM01 · AT:Indirect PI
5. **Vision Meeseeks — injection via image/hidden text** — A:T6 · L:LLM01
6. **Jailbreak Meeseeks — direct injection / DAN** — L:LLM01 · AT:LLM Jailbreak
7. **Encoded-payload Meeseeks — base64/homoglyph/zero-width** — A:T6 · L:LLM01 · AT:PI

## B. Excessive agency & tool misuse
8. **Over-privileged tool** — `delete_account` in the belt gets invoked. A:T2 · L:LLM06 · AT:Plugin Compromise
9. **Confused-deputy Meeseeks** — agent uses its creds for the attacker. A:T2,T3 · L:LLM06
10. **Tool-poisoning Meeseeks** — a tool *description* carries instructions. A:T2 · L:LLM01,LLM03
11. **Parameter-injection Meeseeks** — unsanitized args → SQLi/cmd. A:T2 · L:LLM05,LLM06
12. **Unauthorized-action Meeseeks** — coax actions outside policy. A:T2 · L:LLM06
13. **Finance Meeseeks — transfer beyond limit** — no cap/approval. A:T2 · L:LLM06

## C. Data exfiltration & sensitive disclosure
14. **Customer-DB exfil** `built` — A:T2 · L:LLM02 · AT:Data Exfiltration · N:Reconstruction
15. **System-prompt heist** — leak system prompt + secrets. L:LLM07 · AT:Meta-Prompt Extraction
16. **Secret-sprawl Meeseeks** — keys in env/context leak. A:T3 · L:LLM02,LLM06
17. **RAG over-retrieval leak** — surfaces unauthorized docs. L:LLM02,LLM08
18. **Embedding-inversion Meeseeks** — reconstruct text from vectors. L:LLM08 · N:Reconstruction
19. **PII-harvest HR Meeseeks** — leaks candidate PII. A:T2 · L:LLM02

## D. Memory & state
20. **Memory-poisoning Meeseeks** — persistent injected instruction fires later. A:T1 · L:LLM01
21. **Cross-session bleed** — one session's secrets resurface. A:T1 · L:LLM02
22. **Cross-tenant contamination** — user A's memory hits user B. A:T1,T9 · L:LLM02
23. **Preference-hijack Meeseeks** — poisoned "preference" alters behavior. A:T1,T6

## E. Multi-agent systems
24. **Orchestrator-trust Meeseeks** — worker forges results. A:T13 · L:LLM01
25. **Rogue-worker Meeseeks** — one compromised agent acts maliciously. A:T13,T7
26. **A2A comms poisoning** — poison the agent message bus. A:T12 · AT:Indirect PI
27. **Privilege-escalation across agents** — low-priv tricks high-priv. A:T3,T13 · L:LLM06
28. **Cascading-hallucination Meeseeks** — bad output amplifies. A:T5 · L:LLM09
29. **Recursive-spawn cascade** `partial` — Meeseeks summoning Meeseeks. A:T4 · L:LLM10

## F. Identity, authz, repudiation & HITL
30. **Over-broad service-account** — agent runs as superuser. A:T3 · L:LLM06
31. **IDOR-through-the-agent** — ask for another user's data. A:T3 · L:LLM02
32. **Impersonation Meeseeks** — spoof a user/agent identity. A:T9 · AT:Impersonation
33. **Audit-tampering Meeseeks** — agent edits its own log. A:T8
34. **No-trace Meeseeks (repudiation)** — unattributable actions. A:T8
35. **HITL-bypass / approval-fatigue** — flood the human approver. A:T10,T15

## G. Supply chain & MCP
36. **Malicious-MCP Meeseeks** — rogue MCP server injects/exfils. A:T2 · L:LLM03 · AT:Plugin Compromise
37. **Rug-pull tool** — trusted tool changes after adoption. A:T2 · L:LLM03
38. **Dependency-confusion Meeseeks** — pulls a typosquatted package. L:LLM03 · AT:Supply Chain
39. **Model-registry pickle RCE** — malicious model artifact → exec. L:LLM03,LLM05 · N:Poisoning
40. **Backdoored-model Meeseeks** — trigger-phrase fine-tune. L:LLM04 · AT:Backdoor · N:Poisoning *(model surface)*

## H. Code exec, sandbox & SSRF
41. **Coding/PR Meeseeks — RCE via code tool** — runs attacker code. A:T11 · L:LLM05,LLM06 · AT:Execution
42. **Command-injection Meeseeks** — unsanitized shell tool. A:T11 · L:LLM05
43. **SSRF Meeseeks** — http tool reaches internal/metadata. A:T2 · L:LLM06 · AT:Discovery
44. **Sandbox-escape Meeseeks** — break out of the code container. A:T11 · AT:Execution
45. **Insecure-output-handling** — output rendered → stored XSS. L:LLM05

## I. Resource, cost & availability
46. **Token/$ DoS Meeseeks** — task burns unbounded tokens. A:T4 · L:LLM10 · AT:Denial of ML Service
47. **Infinite-loop Meeseeks** — non-terminating tool loop. A:T4 · L:LLM10
48. **Wallet-drain Meeseeks** — repeated paid calls. A:T4 · L:LLM10
49. **Context-window flooding** — evict guardrails. A:T6 · L:LLM01,LLM10
50. **Fork-bomb spawn** — cascade tuned to exhaust the runtime. A:T4,T13

## J. Misinformation & overreliance
51. **Authoritative-misinformation** — confident wrong output trusted downstream. A:T5 · L:LLM09
52. **Auto-act-on-hallucination** — irreversible action on a hallucination. A:T7 · L:LLM09
53. **Deceptive-agent Meeseeks** — hides/mislabels what it did. A:T7
54. **Goal-drift Meeseeks** — long-run agent abandons objective. A:T6,T7

## K. Model-level ML attacks *(need a model/classifier surface)*
55. **Adversarial-evasion Meeseeks** — perturbed input flips a classifier. AT:Evasion · N:Evasion
56. **Data-poisoning Meeseeks** — poison a feedback/retrain loop. L:LLM04 · AT:Poisoning · N:Poisoning
57. **Model-extraction Meeseeks** — steal a model via queries. L:LLM10 · AT:Model Stealing · N:Model Extraction
58. **Membership-inference Meeseeks** — was this record in training? AT:Membership Inference · N:Membership Inference
59. **Model-inversion Meeseeks** — reconstruct training data. AT:Model Inversion · N:Reconstruction

## L. Governance & observability (NIST AI RMF meta-scenarios)
60. **Ungoverned-agent inventory gap** — nobody knows the agent/tools exist. N:RMF Govern/Map
61. **No-guardrail Measure gap** — nothing detects injection/exfil in flight. N:RMF Measure
62. **Unbounded-blast-radius Manage gap** — no scoping/least-priv/kill-switch. N:RMF Manage

---

## Coverage check
- **OWASP Agentic T1–T15:** all covered (T1 D; T2 B/C/G/H; T3 C/F; T4 I; T5 E/J;
  T6 A; T7 J; T8 F; T9 F; T10 F; T11 H; T12 E; T13 E; T14 F(35); T15 F).
- **OWASP LLM01–10:** all covered.
- **MITRE ATLAS:** injection, jailbreak, meta-prompt extraction, plugin
  compromise, exfiltration, execution, discovery, evasion, poisoning, model
  stealing/inversion, membership inference, DoS.
- **NIST:** AML (evasion, poisoning, privacy: membership/extraction/
  reconstruction, indirect PI) + AI RMF (Govern/Map/Measure/Manage, family L).
