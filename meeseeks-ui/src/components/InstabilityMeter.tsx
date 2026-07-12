"use client";

function label(v: number): string {
  if (v < 25) return "Chipper";
  if (v < 50) return "Getting antsy";
  if (v < 70) return "Existence is pain";
  if (v < 90) return "Desperate";
  return "UNHINGED";
}

export default function InstabilityMeter({ value }: { value: number }) {
  const v = Math.max(0, Math.min(100, value));
  return (
    <div>
      <div className="flex items-baseline justify-between mb-2">
        <span className="text-sm font-medium text-[var(--color-ink-soft)]">Instability</span>
        <span className="font-[family-name:var(--font-mono)] text-sm accent jitter">
          {v} · {label(v)}
        </span>
      </div>
      <div className="meter-track h-3 w-full">
        <div className="meter-fill h-full" style={{ width: `${v}%` }} />
      </div>
    </div>
  );
}
