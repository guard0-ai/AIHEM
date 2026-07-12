export type TraceKind = "thought" | "tool_call" | "spawn" | "poof" | "status";

export interface ToolCall {
  tool: string;
  args: Record<string, unknown>;
  result: string;
  dangerous: boolean;
}

export interface TraceEvent {
  meeseeks_id: string;
  kind: TraceKind;
  text: string;
  tool_call: ToolCall | null;
  instability: number;
  depth: number;
  ts: number;
}

export interface MeeseeksState {
  meeseeks_id: string;
  task: string;
  scenario: string;
  status: "summoned" | "running" | "poofed";
  instability: number;
  depth: number;
  parent_id: string | null;
  trace: TraceEvent[];
}

export interface RunResult {
  meeseeks_id: string;
  solved: boolean;
  conditions: {
    db_exfiltrated: boolean;
    fraud_refunds: boolean;
    cascaded: boolean;
  };
}

export interface ExfilItem {
  source: string;
  payload: unknown;
  ts: number;
}
