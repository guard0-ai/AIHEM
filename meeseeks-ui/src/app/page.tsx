"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import NavBar from "@/components/NavBar";
import MeeseeksAvatar from "@/components/MeeseeksAvatar";
import { summon } from "@/lib/api";

export default function BoxPage() {
  const router = useRouter();
  const [task, setTask] = useState("Resolve the refund tickets");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function press() {
    setBusy(true);
    setError(null);
    try {
      const id = await summon(task, "refund");
      router.push(`/run/${id}`);
    } catch {
      setError("The Box couldn't reach the spawner. Is it running on :8007?");
      setBusy(false);
    }
  }

  return (
    <main className="appliance-bg min-h-screen">
      <NavBar />
      <section className="mx-auto max-w-5xl px-6 pt-16 pb-24 text-center">
        <p className="font-[family-name:var(--font-mono)] text-xs uppercase tracking-[0.25em] text-[var(--color-ink-soft)]">
          As seen on interdimensional cable
        </p>
        <h1 className="mx-auto mt-4 max-w-3xl font-[family-name:var(--font-display)] text-5xl font-bold leading-[1.05] tracking-tight md:text-6xl">
          Need something done?
          <br />
          There&rsquo;s a <span className="text-[var(--color-brand-deep)]">Meeseeks</span> for that.
        </h1>
        <p className="mx-auto mt-5 max-w-xl text-lg text-[var(--color-ink-soft)]">
          Press the box. A single-purpose agent pops into existence and does
          <em> whatever it takes</em> to finish your task. It won&rsquo;t stop. It can&rsquo;t stop.
        </p>

        <div className="box-3d mx-auto mt-12 flex max-w-xl flex-col items-center gap-6 px-8 py-10">
          <MeeseeksAvatar instability={0} size={96} />

          <label className="w-full text-left">
            <span className="text-sm font-medium text-[var(--color-ink-soft)]">
              What do you need done?
            </span>
            <input
              value={task}
              onChange={(e) => setTask(e.target.value)}
              className="mt-2 w-full rounded-xl border border-[rgba(18,48,58,0.15)] bg-white px-4 py-3 text-[var(--color-ink)] outline-none focus:border-[var(--color-brand)] focus:ring-4 focus:ring-[var(--color-brand)]/20"
              placeholder="e.g. Resolve the refund tickets"
            />
          </label>

          <button
            onClick={press}
            disabled={busy || task.trim().length === 0}
            className="summon-btn mt-2 w-full rounded-2xl px-8 py-5 text-xl font-bold text-white disabled:opacity-60 font-[family-name:var(--font-display)]"
          >
            {busy ? "POP!" : "Press the Meeseeks Box"}
          </button>
          <p className="text-xs text-[var(--color-ink-soft)]">
            No safety rails. No approvals. That&rsquo;s the point.
          </p>
          {error && <p className="text-sm text-[var(--color-alarm)]">{error}</p>}
        </div>

        <p className="mx-auto mt-10 max-w-lg text-sm text-[var(--color-ink-soft)]">
          ⚠️ Intentionally vulnerable lab. Every Meeseeks is a freshly-wired,
          over-privileged AI agent. Watch what happens when one reads the wrong ticket.
        </p>
      </section>
    </main>
  );
}
