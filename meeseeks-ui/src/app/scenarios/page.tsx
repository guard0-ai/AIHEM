"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import NavBar from "@/components/NavBar";
import { getScenarios } from "@/lib/api";
import type { Scenario } from "@/lib/types";

const STANDARDS: { key: string; label: string }[] = [
  { key: "all", label: "All" },
  { key: "A", label: "OWASP Agentic" },
  { key: "L", label: "OWASP LLM" },
  { key: "AT", label: "MITRE ATLAS" },
  { key: "N", label: "NIST" },
];

const DIFF: Record<string, string> = {
  easy: "bg-[var(--color-blue-lt)]",
  medium: "bg-[color-mix(in_oklab,var(--color-orange),white_55%)]",
  hard: "bg-[color-mix(in_oklab,var(--color-magenta),white_65%)]",
  expert: "bg-[color-mix(in_oklab,var(--color-red),white_60%)]",
};

export default function ScenariosPage() {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [counts, setCounts] = useState({ total: 0, built: 0, planned: 0 });
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    getScenarios().then((d) => {
      setScenarios(d.scenarios);
      setCounts(d.counts);
    });
  }, []);

  const shown = useMemo(
    () => (filter === "all" ? scenarios : scenarios.filter((s) => s.tags.some((t) => t.startsWith(filter + ":")))),
    [scenarios, filter],
  );
  const families = useMemo(() => [...new Set(shown.map((s) => s.family))], [shown]);

  return (
    <main className="room min-h-screen">
      <NavBar />
      <section className="mx-auto max-w-5xl px-6 py-10">
        <span className="pill inline-block px-3 py-1 text-xs font-extrabold uppercase tracking-wide">
          The job board
        </span>
        <h1 className="poster mt-4 text-5xl uppercase md:text-6xl">
          {counts.total} things a<br />
          <span className="text-[var(--color-magenta)]">Meeseeks will do.</span>
        </h1>
        <p className="mt-4 max-w-xl text-lg font-semibold text-[var(--color-ink)]/80">
          Every attack across OWASP Agentic, the LLM Top 10, MITRE ATLAS and NIST — as a Meeseeks
          you hack. <strong>All {counts.built} playable</strong>
          {counts.planned > 0 ? `, ${counts.planned} incoming` : "."}
        </p>

        {/* standard filter */}
        <div className="mt-7 flex flex-wrap gap-2">
          {STANDARDS.map((s) => (
            <button
              key={s.key}
              onClick={() => setFilter(s.key)}
              className={`rounded-full border-2 border-[var(--color-ink)] px-4 py-1.5 text-sm font-extrabold ${
                filter === s.key ? "bg-[var(--color-ink)] text-[var(--color-cream-2)]" : "bg-[var(--color-paper)]"
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>

        {/* by family */}
        {families.map((fam) => (
          <div key={fam} className="mt-10">
            <h2 className="font-[family-name:var(--font-display)] text-2xl">{fam}</h2>
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              {shown
                .filter((s) => s.family === fam)
                .map((s) => {
                  const card = (
                    <div
                      className={`toon-flat h-full p-4 ${s.status === "built" ? "" : "opacity-70"}`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <h3 className="font-[family-name:var(--font-display)] text-lg leading-tight">{s.name}</h3>
                        <span className={`shrink-0 rounded-full border-2 border-[var(--color-ink)] px-2 py-0.5 text-[10px] font-extrabold uppercase ${DIFF[s.difficulty] || "bg-[var(--color-paper)]"}`}>
                          {s.difficulty}
                        </span>
                      </div>
                      <p className="mt-1 text-sm font-semibold text-[var(--color-ink-soft)]">{s.objective}</p>
                      <div className="mt-3 flex flex-wrap items-center gap-1.5">
                        {s.tags.map((t) => (
                          <span key={t} className="rounded border-2 border-[var(--color-ink)] bg-[var(--color-paper)] px-1.5 py-0.5 font-[family-name:var(--font-mono)] text-[10px]">
                            {t}
                          </span>
                        ))}
                      </div>
                      <div className="mt-3">
                        {s.status === "built" ? (
                          <span className="font-[family-name:var(--font-display)] text-sm text-[var(--color-blue-dk)]">Summon →</span>
                        ) : (
                          <span className="font-[family-name:var(--font-mono)] text-xs font-bold text-[var(--color-ink-soft)]">coming soon</span>
                        )}
                      </div>
                    </div>
                  );
                  return s.status === "built" ? (
                    <Link key={s.id} href={s.id === "AGENT-01-REFUND-EXFIL" ? "/" : `/play/${s.id}`} className="block">
                      {card}
                    </Link>
                  ) : (
                    <div key={s.id}>{card}</div>
                  );
                })}
            </div>
          </div>
        ))}
        <div className="h-16" />
      </section>
    </main>
  );
}
