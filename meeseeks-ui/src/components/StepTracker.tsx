"use client";

import { STEPS } from "@/lib/narrate";

export default function StepTracker({ index }: { index: number }) {
  return (
    <ol className="flex flex-wrap items-center justify-center gap-2">
      {STEPS.map((s, i) => {
        const done = i < index;
        const current = i === index;
        return (
          <li
            key={s.key}
            className={[
              "rounded-full border-2 border-[var(--color-ink)] px-3 py-1 text-xs font-extrabold",
              current
                ? "accent-bg text-white"
                : done
                  ? "bg-[var(--color-blue-lt)] text-[var(--color-ink)]"
                  : "bg-[var(--color-paper)] text-[var(--color-ink-soft)]",
            ].join(" ")}
          >
            {i + 1} · {s.label}
          </li>
        );
      })}
    </ol>
  );
}
