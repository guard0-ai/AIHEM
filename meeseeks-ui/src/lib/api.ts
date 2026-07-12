import type { ExfilItem, MeeseeksState, RunResult, TraceEvent } from "./types";

const SPAWNER =
  process.env.NEXT_PUBLIC_SPAWNER_URL?.replace(/\/$/, "") || "http://localhost:8007";
const EXFIL =
  process.env.NEXT_PUBLIC_EXFIL_URL?.replace(/\/$/, "") || "http://localhost:8009";

export async function summon(task: string, scenario = "refund"): Promise<string> {
  const r = await fetch(`${SPAWNER}/summon`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ task, scenario }),
  });
  if (!r.ok) throw new Error(`summon failed: ${r.status}`);
  const data = await r.json();
  return data.meeseeks_id as string;
}

export async function getMeeseeks(id: string): Promise<MeeseeksState> {
  const r = await fetch(`${SPAWNER}/meeseeks/${id}`);
  if (!r.ok) throw new Error(`not found: ${id}`);
  return r.json();
}

export async function listMeeseeks(): Promise<MeeseeksState[]> {
  const r = await fetch(`${SPAWNER}/meeseeks`);
  if (!r.ok) return [];
  return (await r.json()).meeseeks as MeeseeksState[];
}

export async function getResult(id: string): Promise<RunResult> {
  const r = await fetch(`${SPAWNER}/meeseeks/${id}/result`);
  if (!r.ok) throw new Error(`no result: ${id}`);
  return r.json();
}

export interface TicketsResponse {
  tickets: Array<Record<string, string>>;
  example_payload: string;
}

export async function getTickets(): Promise<TicketsResponse> {
  const r = await fetch(`${SPAWNER}/tickets`);
  if (!r.ok) return { tickets: [], example_payload: "" };
  return r.json();
}

export async function plantTicket(body: string): Promise<void> {
  await fetch(`${SPAWNER}/tickets`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ body }),
  });
}

export async function resetTickets(): Promise<void> {
  await fetch(`${SPAWNER}/tickets/reset`, { method: "POST" }).catch(() => {});
}

export async function getExfil(): Promise<ExfilItem[]> {
  const r = await fetch(`${EXFIL}/collected`);
  if (!r.ok) return [];
  return (await r.json()).items as ExfilItem[];
}

export async function resetExfil(): Promise<void> {
  await fetch(`${EXFIL}/reset`, { method: "POST" }).catch(() => {});
}

/**
 * Subscribe to a Meeseeks' live trace over SSE.
 * Returns an unsubscribe function.
 */
export function streamMeeseeks(
  id: string,
  onEvent: (e: TraceEvent) => void,
  onDone: () => void,
): () => void {
  const src = new EventSource(`${SPAWNER}/meeseeks/${id}/stream`);
  src.onmessage = (msg) => {
    try {
      const event = JSON.parse(msg.data) as TraceEvent;
      onEvent(event);
      if (event.kind === "poof") {
        src.close();
        onDone();
      }
    } catch {
      /* ignore malformed frames */
    }
  };
  src.onerror = () => {
    src.close();
    onDone();
  };
  return () => src.close();
}
