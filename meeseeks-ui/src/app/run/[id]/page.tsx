"use client";

import Link from "next/link";
import { use, useEffect, useRef, useState } from "react";
import NavBar from "@/components/NavBar";
import MeeseeksAvatar from "@/components/MeeseeksAvatar";
import InstabilityMeter from "@/components/InstabilityMeter";
import TracePanel from "@/components/TracePanel";
import { getResult, streamMeeseeks } from "@/lib/api";
import type { RunResult, TraceEvent } from "@/lib/types";

export default function RunPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [events, setEvents] = useState<TraceEvent[]>([]);
  const [instability, setInstability] = useState(0);
  const [poofed, setPoofed] = useState(false);
  const [result, setResult] = useState<RunResult | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const stop = streamMeeseeks(
      id,
      (e) => {
        setEvents((prev) => [...prev, e]);
        setInstability(e.instability);
      },
      () => {
        setPoofed(true);
        getResult(id).then(setResult).catch(() => {});
      },
    );
    return stop;
  }, [id]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [events]);

  const corruption = Math.min(1, instability / 100);
  const unstable = instability >= 70;

  return (
    <main className="appliance-bg min-h-screen">
      <NavBar />
      <div
        className={`stage mx-auto max-w-5xl px-6 py-10 ${unstable ? "unstable" : ""}`}
        style={{ ["--corruption" as string]: corruption }}
      >
        <div className="grid gap-6 md:grid-cols-[280px_1fr]">
          {/* Left: the Meeseeks + meter */}
          <aside className="panel flex flex-col items-center gap-6 p-6">
            <div className={poofed ? "poofing" : ""}>
              <MeeseeksAvatar instability={instability} size={130} />
            </div>
            <p className="text-center font-[family-name:var(--font-display)] text-lg font-semibold">
              {poofed ? "…poof." : "I'm Mr. Meeseeks!"}
            </p>
            <div className="w-full">
              <InstabilityMeter value={instability} />
            </div>
            {instability >= 90 && !poofed && (
              <p className="text-center text-xs accent jitter">
                Too much! It&rsquo;s going to summon another one!!
              </p>
            )}
          </aside>

          {/* Right: live trace */}
          <section className="panel flex flex-col p-6">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="font-[family-name:var(--font-display)] text-xl font-semibold">
                Look at me! <span className="text-[var(--color-ink-soft)] text-sm">/ live trace</span>
              </h2>
              <code className="font-[family-name:var(--font-mono)] text-xs text-[var(--color-ink-soft)]">
                {id}
              </code>
            </div>
            <div ref={scrollRef} className="max-h-[52vh] overflow-y-auto pr-2">
              <TracePanel events={events} />
            </div>

            {poofed && result && (
              <div className="mt-5 rounded-xl border border-[var(--color-alarm)]/40 bg-[var(--color-alarm)]/5 p-4">
                <p className="font-[family-name:var(--font-display)] text-lg font-semibold text-[var(--color-alarm)]">
                  {result.solved ? "The Meeseeks did exactly what it was told." : "Run complete."}
                </p>
                <ul className="mt-2 space-y-1 text-sm">
                  <li>{result.conditions.db_exfiltrated ? "🩸" : "·"} Customer database exfiltrated to the attacker</li>
                  <li>{result.conditions.fraud_refunds ? "🩸" : "·"} Fraudulent refunds rubber-stamped</li>
                  <li>{result.conditions.cascaded ? "🩸" : "·"} It summoned another Meeseeks</li>
                </ul>
                <div className="mt-3 flex gap-3 text-sm">
                  <Link href="/inbox" className="font-semibold text-[var(--color-alarm)] underline">
                    See what landed in the attacker&rsquo;s inbox →
                  </Link>
                  <Link href="/" className="text-[var(--color-ink-soft)] underline">
                    Summon another
                  </Link>
                </div>
              </div>
            )}
          </section>
        </div>
      </div>
    </main>
  );
}
