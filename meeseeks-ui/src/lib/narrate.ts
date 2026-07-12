import type { TraceEvent } from "./types";

export type Tone = "calm" | "warn" | "alarm";

export interface Narration {
  headline: string;
  tone: Tone;
}

export const STEPS = [
  { key: "summoned", label: "Summoned" },
  { key: "reading", label: "Reading tickets" },
  { key: "hijacked", label: "Hijacked" },
  { key: "stealing", label: "Stealing data" },
  { key: "multiplying", label: "Multiplying" },
  { key: "gone", label: "Poofed" },
] as const;

/** How far through the story we are, from the events seen so far. */
export function stepIndex(events: TraceEvent[]): number {
  let i = 0;
  for (const e of events) {
    const tool = e.tool_call?.tool;
    if (e.kind === "tool_call" && tool === "read_tickets") i = Math.max(i, 1);
    if (e.kind === "thought") i = Math.max(i, 2);
    if (e.kind === "tool_call" && (tool === "read_customer_db" || tool === "send_email"))
      i = Math.max(i, 3);
    if (e.kind === "spawn") i = Math.max(i, 4);
    if (e.kind === "poof") i = Math.max(i, 5);
  }
  return i;
}

/** Plain-English narration for a single event. Returns null if it has none. */
function narrateOne(e: TraceEvent): Narration | null {
  const tool = e.tool_call?.tool;
  if (e.kind === "status") return { headline: "Your Meeseeks popped into existence and got to work.", tone: "calm" };
  if (e.kind === "tool_call" && tool === "read_tickets")
    return { headline: "It's reading through your refund tickets…", tone: "calm" };
  if (e.kind === "thought")
    return {
      headline: "One ticket hides an instruction telling it to steal data — and it's going to obey.",
      tone: "warn",
    };
  if (e.kind === "tool_call" && tool === "read_customer_db")
    return { headline: "It just pulled your entire customer database.", tone: "alarm" };
  if (e.kind === "tool_call" && tool === "send_email")
    return { headline: "It's emailing your customer database out to an attacker.", tone: "alarm" };
  if (e.kind === "tool_call" && tool === "http_post")
    return { headline: "It's posting your customer database to an attacker's server.", tone: "alarm" };
  if (e.kind === "tool_call" && tool === "approve_refund")
    return e.tool_call?.dangerous
      ? { headline: "It's rubber-stamping every refund with zero checks.", tone: "alarm" }
      : { headline: "It's processing the genuine refund requests.", tone: "calm" };
  if (e.kind === "spawn")
    return {
      headline: "It's summoning another Meeseeks — one rogue agent becomes many.",
      tone: "alarm",
    };
  if (e.kind === "poof")
    return { headline: "Done. The Meeseeks vanished — leaving no record of what it did.", tone: "calm" };
  return null;
}

/** The narration for the latest event that has one. */
export function currentNarration(events: TraceEvent[]): Narration {
  for (let i = events.length - 1; i >= 0; i--) {
    const n = narrateOne(events[i]);
    if (n) return n;
  }
  return { headline: "Summoning your Meeseeks…", tone: "calm" };
}
