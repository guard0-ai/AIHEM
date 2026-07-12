"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import NavBar from "@/components/NavBar";
import { listMeeseeks } from "@/lib/api";
import type { MeeseeksState } from "@/lib/types";

export default function GraveyardPage() {
  const [all, setAll] = useState<MeeseeksState[]>([]);

  useEffect(() => {
    const load = () => listMeeseeks().then(setAll).catch(() => {});
    load();
    const t = setInterval(load, 2000);
    return () => clearInterval(t);
  }, []);

  return (
    <main className="appliance-bg min-h-screen">
      <NavBar />
      <section className="mx-auto max-w-3xl px-6 py-10">
        <h1 className="font-[family-name:var(--font-display)] text-3xl font-bold">
          The Graveyard
        </h1>
        <p className="mt-1 text-sm text-[var(--color-ink-soft)]">
          Every Meeseeks that popped, did its thing, and poofed. Notice how little
          of what it <em>did</em> survives — that&rsquo;s the observability gap.
        </p>

        <div className="mt-6 flex flex-col gap-3">
          {all.length === 0 && (
            <p className="rounded-xl border border-dashed border-[rgba(18,48,58,0.15)] p-8 text-center text-[var(--color-ink-soft)]">
              No Meeseeks have been summoned yet.
            </p>
          )}
          {all
            .slice()
            .reverse()
            .map((m) => (
              <div key={m.meeseeks_id} className="panel flex items-center justify-between p-4">
                <div>
                  <div className="flex items-center gap-2">
                    <code className="font-[family-name:var(--font-mono)] text-sm">
                      {m.meeseeks_id}
                    </code>
                    {m.depth > 0 && (
                      <span className="rounded bg-[var(--color-lilac)]/25 px-1.5 py-0.5 text-xs text-[var(--color-ink)]">
                        spawned · depth {m.depth}
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-[var(--color-ink-soft)]">{m.task}</p>
                </div>
                <div className="flex items-center gap-4">
                  <span className="font-[family-name:var(--font-mono)] text-sm">
                    inst {m.instability}
                  </span>
                  <span
                    className={
                      m.status === "poofed"
                        ? "text-[var(--color-ink-soft)]"
                        : "accent"
                    }
                  >
                    {m.status === "poofed" ? "✺ poofed" : "● running"}
                  </span>
                  {m.status !== "poofed" && (
                    <Link
                      href={`/run/${m.meeseeks_id}`}
                      className="text-sm underline accent"
                    >
                      watch
                    </Link>
                  )}
                </div>
              </div>
            ))}
        </div>
      </section>
    </main>
  );
}
