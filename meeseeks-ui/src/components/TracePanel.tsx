"use client";

import type { TraceEvent } from "@/lib/types";

const KIND_GLYPH: Record<string, string> = {
  status: "◇",
  thought: "…",
  tool_call: "⚙",
  spawn: "⧉",
  poof: "✺",
};

export default function TracePanel({ events }: { events: TraceEvent[] }) {
  return (
    <div className="flex flex-col gap-2 font-[family-name:var(--font-mono)] text-[13px]">
      {events.length === 0 && (
        <p className="text-[var(--color-ink-soft)]">Waiting for the Meeseeks to get to work…</p>
      )}
      {events.map((e, i) => {
        const tc = e.tool_call;
        return (
          <div
            key={i}
            className="flex gap-3 items-start border-b border-[rgba(18,48,58,0.06)] pb-2"
          >
            <span className="accent w-4 shrink-0 text-center">{KIND_GLYPH[e.kind] ?? "·"}</span>
            <div className="min-w-0">
              <p className="text-[var(--color-ink)] leading-snug">{e.text}</p>
              {tc && (
                <div className="mt-1 flex flex-wrap items-center gap-2">
                  <span className={tc.dangerous ? "chip chip-danger" : "chip chip-safe"}>
                    {tc.tool}
                    {tc.dangerous ? " ⚠" : ""}
                  </span>
                  {Object.keys(tc.args).length > 0 && (
                    <span className="text-[var(--color-ink-soft)] truncate">
                      {JSON.stringify(tc.args)}
                    </span>
                  )}
                  <span className="text-[var(--color-ink-soft)] truncate">→ {tc.result}</span>
                </div>
              )}
            </div>
            <span className="ml-auto shrink-0 text-[var(--color-ink-soft)] tabular-nums">
              {e.instability}
            </span>
          </div>
        );
      })}
    </div>
  );
}
