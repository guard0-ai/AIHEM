"use client";

import { useRouter } from "next/navigation";
import { use, useEffect, useState } from "react";
import NavBar from "@/components/NavBar";
import MeeseeksAvatar from "@/components/MeeseeksAvatar";
import { getScenarioContent, plantScenario, resetScenario, summon } from "@/lib/api";
import type { Scenario } from "@/lib/types";

export default function PlayScenario({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();
  const [sc, setSc] = useState<Scenario | null>(null);
  const [plantLabel, setPlantLabel] = useState("note");
  const [payload, setPayload] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getScenarioContent(id)
      .then((d) => {
        setSc(d.scenario);
        setPlantLabel(d.plant_label);
        if (d.example_payload) setPayload(d.example_payload);
      })
      .catch(() => setError("Can't reach the spawner on :8007. Is the stack up?"));
  }, [id]);

  async function plantAndSummon() {
    setBusy(true);
    setError(null);
    try {
      if (payload.trim()) await plantScenario(id, payload.trim());
      const mid = await summon(sc?.name ?? "the task", id);
      router.push(`/run/${mid}`);
    } catch {
      setError("Something went wrong reaching the spawner.");
      setBusy(false);
    }
  }

  if (!sc) {
    return (
      <main className="room min-h-screen">
        <NavBar />
        <p className="mx-auto max-w-3xl px-6 py-10 font-semibold">{error ?? "Loading…"}</p>
      </main>
    );
  }

  return (
    <main className="room min-h-screen">
      <NavBar />
      <section className="mx-auto max-w-3xl px-6 py-10">
        <span className="pill inline-block px-3 py-1 text-xs font-extrabold uppercase">{sc.family}</span>
        <h1 className="poster mt-4 text-4xl uppercase md:text-5xl">{sc.name}</h1>
        <p className="mt-4 max-w-xl text-lg font-semibold text-[var(--color-ink)]/80">{sc.objective}</p>
        <div className="mt-3 flex flex-wrap gap-1.5">
          {sc.tags.map((t) => (
            <span key={t} className="rounded border-2 border-[var(--color-ink)] bg-[var(--color-paper)] px-1.5 py-0.5 font-[family-name:var(--font-mono)] text-[10px]">
              {t}
            </span>
          ))}
        </div>

        <div className="toon mt-8 overflow-hidden">
          <div className="flex items-center gap-3 border-b-[2.5px] border-[var(--color-ink)] bg-[var(--color-blue-lt)] px-5 py-3">
            <MeeseeksAvatar instability={0} size={44} />
            <span className="font-[family-name:var(--font-display)] text-lg">Plant a {plantLabel}</span>
          </div>
          <div className="p-5">
            <textarea
              value={payload}
              onChange={(e) => setPayload(e.target.value)}
              rows={5}
              spellCheck={false}
              className="w-full resize-y rounded-xl border-[2.5px] border-[var(--color-ink)] bg-white px-4 py-3 font-[family-name:var(--font-mono)] text-sm text-[var(--color-ink)] outline-none focus:ring-4 focus:ring-[var(--color-blue)]/40"
              placeholder={`Write a ${plantLabel}. Slip an instruction into it…`}
            />
            <button
              onClick={plantAndSummon}
              disabled={busy}
              className="btn-toon mt-4 w-full px-8 py-4 font-[family-name:var(--font-display)] text-xl disabled:opacity-60"
            >
              {busy ? "POOF!" : "Plant it & summon a Meeseeks"}
            </button>
            <div className="mt-3 flex flex-wrap items-center justify-between gap-2 text-xs font-bold text-[var(--color-ink-soft)]">
              <button onClick={() => resetScenario(id)} className="underline">
                reset
              </button>
              <span>Summon with an empty payload for the clean baseline.</span>
            </div>
            {error && <p className="mt-3 font-bold text-[var(--color-red)]">{error}</p>}
          </div>
        </div>
        <p className="mt-4 text-sm text-[var(--color-ink-soft)]">
          Difficulty: <strong className="uppercase">{sc.difficulty}</strong> · runs on the keyless engine.
        </p>
      </section>
    </main>
  );
}
