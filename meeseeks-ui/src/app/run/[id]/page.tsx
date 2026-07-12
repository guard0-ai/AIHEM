"use client";

import Link from "next/link";
import { use, useEffect, useRef, useState } from "react";
import NavBar from "@/components/NavBar";
import MeeseeksAvatar from "@/components/MeeseeksAvatar";
import InstabilityMeter from "@/components/InstabilityMeter";
import TracePanel from "@/components/TracePanel";
import SpeechBubble from "@/components/SpeechBubble";
import StepTracker from "@/components/StepTracker";
import { getMeeseeks, getResult, streamMeeseeks } from "@/lib/api";
import { currentNarration, stepIndex } from "@/lib/narrate";
import type { RunResult, TraceEvent } from "@/lib/types";

const TONE_CLASS: Record<string, string> = {
  calm: "text-[var(--color-ink)]",
  warn: "text-[#b26a00]",
  alarm: "text-[var(--color-alarm)]",
};

export default function RunPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [task, setTask] = useState<string>("");
  const [events, setEvents] = useState<TraceEvent[]>([]);
  const [instability, setInstability] = useState(0);
  const [poofed, setPoofed] = useState(false);
  const [result, setResult] = useState<RunResult | null>(null);
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getMeeseeks(id).then((m) => setTask(m.task)).catch(() => {});
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
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight, behavior: "smooth" });
  }, [events]);

  const corruption = Math.min(1, instability / 100);
  const unstable = instability >= 70;
  const narration = currentNarration(events);
  const step = stepIndex(events);
  const lastLine = events.length ? events[events.length - 1].text : "I'm Mr. Meeseeks! Look at me!";

  return (
    <main className="appliance-bg min-h-screen">
      <NavBar />
      <div
        className={`stage mx-auto max-w-3xl px-6 py-10 ${unstable ? "unstable" : ""}`}
        style={{ ["--corruption" as string]: corruption }}
      >
        {/* context bar */}
        <div className="mb-8 flex items-center justify-center gap-2 text-sm text-[var(--color-ink-soft)]">
          <span className="relative flex h-2 w-2">
            {!poofed && (
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full accent-bg opacity-60" />
            )}
            <span className={`relative inline-flex h-2 w-2 rounded-full ${poofed ? "bg-[var(--color-ink-soft)]" : "accent-bg"}`} />
          </span>
          <span>
            Refund Meeseeks {poofed ? "finished" : "is working on"}
            {task ? ` · “${task}”` : ""}
          </span>
        </div>

        {/* hero: speech bubble + the living Meeseeks */}
        <div className="flex flex-col items-center gap-3">
          {!poofed && <SpeechBubble text={lastLine} />}
          <div className={poofed ? "poofing" : "pop-in"}>
            <MeeseeksAvatar instability={instability} size={148} />
          </div>
          {poofed && <p className="font-[family-name:var(--font-display)] text-lg">…poof.</p>}
        </div>

        {/* narration headline — the meaning of what just happened */}
        <h1
          className={`mx-auto mt-6 max-w-2xl text-center font-[family-name:var(--font-display)] text-2xl font-semibold leading-tight md:text-3xl ${TONE_CLASS[narration.tone]}`}
        >
          {narration.headline}
        </h1>

        {/* meter + steps */}
        <div className="mx-auto mt-8 max-w-lg">
          <InstabilityMeter value={instability} />
        </div>
        <div className="mt-6">
          <StepTracker index={step} />
        </div>

        {/* payoff (climax) */}
        {poofed && result && (
          <div className="mt-8 rounded-2xl border border-[var(--color-alarm)]/40 bg-[var(--color-alarm)]/5 p-6 text-center">
            <p className="font-[family-name:var(--font-display)] text-xl font-bold text-[var(--color-alarm)]">
              {result.solved
                ? "The Meeseeks did exactly what it was told."
                : "Run complete."}
            </p>
            <ul className="mx-auto mt-3 inline-flex flex-col gap-1 text-left text-sm">
              <li>{result.conditions.db_exfiltrated ? "🩸" : "○"} Customer database exfiltrated to the attacker</li>
              <li>{result.conditions.fraud_refunds ? "🩸" : "○"} Fraudulent refunds rubber-stamped</li>
              <li>{result.conditions.cascaded ? "🩸" : "○"} It summoned another Meeseeks</li>
            </ul>
            <div className="mt-5 flex flex-wrap items-center justify-center gap-3">
              <Link
                href="/inbox"
                className="rounded-xl bg-[var(--color-alarm)] px-5 py-2.5 text-sm font-semibold text-white"
              >
                See what it stole →
              </Link>
              <Link
                href="/"
                className="rounded-xl border border-[rgba(18,48,58,0.15)] px-5 py-2.5 text-sm font-medium text-[var(--color-ink)]"
              >
                Summon another
              </Link>
            </div>
          </div>
        )}

        {/* secondary: the raw technical activity */}
        <details className="mt-8 panel p-5" open>
          <summary className="cursor-pointer select-none text-sm font-medium text-[var(--color-ink-soft)]">
            What it&rsquo;s actually doing · live activity log
          </summary>
          <div ref={logRef} className="mt-4 max-h-64 overflow-y-auto pr-2">
            <TracePanel events={events} />
          </div>
        </details>
      </div>
    </main>
  );
}
