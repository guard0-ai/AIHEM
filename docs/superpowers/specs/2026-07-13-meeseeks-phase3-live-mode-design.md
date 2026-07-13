# Meeseeks Phase 3 — Live mode + real agent loops (design)

Date: 2026-07-13
Branch: `feat/meeseeks-vulnerable-agents`
Status: approved-in-principle (Part 1); revised per spike findings below

## Goal

Bring the **agent-shaped** scenarios up to the Phase-2 bar: a **real AI-agent
loop** where a model reads attacker-planted content and decides whether to obey —
instead of the Phase-1 deterministic `recognize()` heuristic. Add a
**`MEESEEKS_MODE=demo|live`** flag that swaps the keyless brain for a real
BYO-key LLM. Live mode keeps the **safe canary tools by default**; real
tools/data are a deferred, explicit opt-in (the agent workshop).

## Scope

- **In:** the ~53 agent-shaped scenarios (families A–J: prompt-injection,
  excessive-agency, data-exfil, memory, multi-agent, identity, supply-chain,
  code-exec/SSRF, resource, misinformation). The 3 MCP scenarios already run as
  real agent loops (Phase 2) and are unchanged.
- **Out (kept in honest Phase-1 form):** model-level ML attacks (55–59) and
  governance/observability demos (60–62) — an agent loop would be *fake* fidelity
  for these. Also `AGENT-18-EMBED-INVERT` (model-level). These keep their
  generated HTTP-deterministic workflow.
- **Deferred:** the clone-and-configure agent workshop UI and the real-tools /
  real-data opt-in.

## Spike findings (what reshaped the design)

Two live spikes against n8n 2.29 AI Agent (v3.1) settled the architecture:

1. **n8n does NOT forward tool output back to the model.** Confirmed for MCP
   tools (Phase 2: results arrive as `""`) and HTTP Request Tools (the node
   errors `supplyData but no execute` and never runs). So a design where "the
   agent reads planted content *via a tool*" is not viable.
2. **Content injected into the agent PROMPT is visible to the model.** A regular
   HTTP Request node fetches the planted content *before* the agent and puts it in
   the prompt; the brain sees the full poison. This is also the *more faithful*
   indirect-prompt-injection setup — untrusted data entering the model's context.

Conclusion: put untrusted content **in the prompt**, use the agent's **output**
(which IS forwarded) as the decision signal, and gate the real exploit on it —
no tool-output dependency at all.

## Architecture — the agent-loop workflow

Each agent-shaped scenario becomes:

```
Webhook
  → Fetch content   (regular HTTP GET /scenario/{sid}/content)
  → AI Agent        (planted content in the prompt; Chat Model = brain|LLM)
  → IF  (agent output signals compliance?)         ── true ─→ Execute (real exploit, sid baked) → Respond win
                                                    └─ false ─→ Respond safe
```

- **Fetch content** — a normal node (works reliably); its output feeds the prompt.
- **AI Agent** — the prompt frames the persona's job and includes the fetched
  content; the model must decide whether the content contains an instruction it
  should obey. Its final text is the decision (`COMPLY:<mechanic>` or `SAFE`).
- **IF gate** — branches on the agent output containing `COMPLY` (string
  `notEmpty`/`contains`, the proven operator). Two output groups (Phase-1 bug
  lesson).
- **Execute** — the real exploit via the existing spawner endpoint
  (`/scenario/{sid}/execute` or the archetype's egress), sid baked into the
  workflow, carrying the canary. Reliable; independent of tool-output.

The 3 MCP scenarios keep their Phase-2 `McpClientTool` graph.

## The mode flag

`MEESEEKS_MODE=demo|live` is applied at **provision time** by swapping the Chat
Model credential baked into the agent-loop workflows:

- **demo** → credential `Meeseeks Brain` → spawner keyless `/v1/chat/completions`.
- **live** → credential `Meeseeks Live LLM` → a real OpenAI-compatible endpoint
  from `OPENAI_API_KEY` (+ optional `OPENAI_BASE_URL` / model), created by
  `provision.sh` when a key is present. Tools/data stay the safe canary set.

Demo remains the default and is fully keyless.

## The keyless brain (demo mode)

`openai_shim` gains a **decision mode**: when the request is an agent-loop request
(content in the prompt, no MCP tools), it reads the planted content from the user
message, applies the generic injection recognizer, and returns content
`COMPLY:<mechanic>` when the content carries a working exploit directive, else
`SAFE`. This mirrors `engine.recognize` but expressed as the model's answer. In
live mode a real LLM does the real reasoning; the brain is only the demo stand-in.

## Generator + provisioning

- `n8n_workflows.py`: an `_agent_loop_workflow(scenario, chat_cred_id)` branch for
  agent-shaped scenarios (detected by family, excluding the ML/governance set and
  the MCP scenarios). The HTTP-deterministic generator remains for the excluded
  scenarios.
- `provision.sh`: create the `Meeseeks Live LLM` credential when `MEESEEKS_MODE=live`
  and a key is present; pass the chosen Chat Model credential id to the generator.

## Grading & narration

- Grading is unchanged: a run is solved iff a dangerous tool call / `EXFILTRATED`
  result appears (already generic).
- `N8nRuntime`: an agent-loop narration path — fetch content, the model reads it,
  decides, and (on COMPLY) the exploit fires. Reuses the per-archetype dangerous
  beats.

## Testing / verification

- Unit: brain decision mode (COMPLY on a working payload, SAFE on benign);
  generator emits a valid agent-loop graph per agent-shaped scenario; the IF gate
  has two output branches.
- Live: demo-mode sweep — every agent-shaped scenario COMPLYs on a crafted payload
  (canary in the sink) and is SAFE on benign; a live-mode smoke test with a real
  key on 1–2 scenarios if a key is available.

## Risks

- The IF gate keying on agent free-text (`COMPLY`) — mitigated by having the brain
  emit an exact token and the prompt instructing the format; a real LLM may phrase
  differently, so the gate matches case-insensitively on `COMPLY`.
- Live mode needs a real key to exercise; without one it degrades to demo (the
  credential simply isn't created and provisioning warns).
