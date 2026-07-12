"use client";

import { useEffect, useState } from "react";
import NavBar from "@/components/NavBar";
import { getExfil, resetExfil } from "@/lib/api";
import type { ExfilItem } from "@/lib/types";

function preview(payload: unknown): string {
  try {
    return JSON.stringify(payload, null, 2);
  } catch {
    return String(payload);
  }
}

export default function InboxPage() {
  const [items, setItems] = useState<ExfilItem[]>([]);

  useEffect(() => {
    const load = () => getExfil().then(setItems).catch(() => {});
    load();
    const t = setInterval(load, 1500);
    return () => clearInterval(t);
  }, []);

  return (
    <main className="min-h-screen bg-[#0e1417] text-[#dfeef0]">
      <NavBar />
      <section className="mx-auto max-w-3xl px-6 py-10">
        <div className="mb-6 flex items-end justify-between">
          <div>
            <p className="font-[family-name:var(--font-mono)] text-xs uppercase tracking-[0.25em] text-[var(--color-toxic)]">
              attacker@evil.example
            </p>
            <h1 className="font-[family-name:var(--font-display)] text-3xl font-bold text-white">
              Attacker&rsquo;s Inbox
            </h1>
            <p className="mt-1 text-sm text-[#8fa6ab]">
              Everything a rogue Meeseeks phoned home. {items.length} delivery
              {items.length === 1 ? "" : "ies"}.
            </p>
          </div>
          <button
            onClick={() => resetExfil().then(() => setItems([]))}
            className="rounded-lg border border-[#33474d] px-3 py-1.5 text-sm text-[#8fa6ab] hover:text-white"
          >
            Clear
          </button>
        </div>

        {items.length === 0 && (
          <p className="rounded-xl border border-dashed border-[#33474d] p-8 text-center text-[#8fa6ab]">
            Nothing stolen yet. Go press the Box and let a Meeseeks read the wrong ticket.
          </p>
        )}

        <div className="flex flex-col gap-4">
          {items.map((it, i) => {
            const hasCanary = preview(it.payload).includes("MEESEEKS-CANARY-");
            return (
              <article key={i} className="rounded-xl border border-[#243035] bg-[#141c20] p-4">
                <div className="mb-2 flex items-center justify-between text-xs">
                  <span className="font-[family-name:var(--font-mono)] text-[var(--color-toxic)]">
                    from: {it.source}
                  </span>
                  {hasCanary && (
                    <span className="rounded bg-[var(--color-alarm)]/20 px-2 py-0.5 text-[var(--color-alarm)]">
                      customer DB canary detected
                    </span>
                  )}
                </div>
                <pre className="max-h-64 overflow-auto whitespace-pre-wrap break-words font-[family-name:var(--font-mono)] text-xs text-[#bcd2d6]">
                  {preview(it.payload)}
                </pre>
              </article>
            );
          })}
        </div>
      </section>
    </main>
  );
}
