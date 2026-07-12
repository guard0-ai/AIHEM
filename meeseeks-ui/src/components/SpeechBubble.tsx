"use client";

export default function SpeechBubble({ text }: { text: string }) {
  return (
    <div className="relative max-w-sm">
      <div className="rounded-2xl border border-[color-mix(in_oklab,var(--accent),white_45%)] bg-white px-5 py-3 text-center shadow-[0_10px_30px_-18px_rgba(18,48,58,0.5)]">
        <p className="font-[family-name:var(--font-display)] text-[15px] leading-snug text-[var(--color-ink)]">
          &ldquo;{text}&rdquo;
        </p>
      </div>
      {/* tail */}
      <div className="absolute left-1/2 -bottom-2 h-4 w-4 -translate-x-1/2 rotate-45 border-b border-r border-[color-mix(in_oklab,var(--accent),white_45%)] bg-white" />
    </div>
  );
}
