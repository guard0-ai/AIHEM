"use client";

import { STEPS } from "@/lib/narrate";

export default function StepTracker({ index }: { index: number }) {
  return (
    <ol className="flex flex-wrap items-center justify-center gap-x-2 gap-y-2">
      {STEPS.map((s, i) => {
        const done = i < index;
        const current = i === index;
        return (
          <li key={s.key} className="flex items-center gap-2">
            <span
              className={[
                "flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium transition-colors",
                current
                  ? "accent-bg text-white"
                  : done
                    ? "bg-[color-mix(in_oklab,var(--accent),white_75%)] text-[var(--color-ink)]"
                    : "bg-[rgba(18,48,58,0.06)] text-[var(--color-ink-soft)]",
              ].join(" ")}
            >
              <span className="tabular-nums opacity-70">{i + 1}</span>
              {s.label}
            </span>
            {i < STEPS.length - 1 && (
              <span
                className={`h-px w-4 ${i < index ? "accent-bg" : "bg-[rgba(18,48,58,0.15)]"}`}
              />
            )}
          </li>
        );
      })}
    </ol>
  );
}
