"use client";

export default function SpeechBubble({ text }: { text: string }) {
  return (
    <div className="relative max-w-sm">
      <div className="rounded-2xl border-[2.5px] border-[var(--color-ink)] bg-white px-5 py-3 text-center shadow-[3px_3px_0_var(--color-ink)]">
        <p className="font-[family-name:var(--font-display)] text-base leading-snug text-[var(--color-ink)]">
          {text}
        </p>
      </div>
      <div className="absolute -bottom-2 left-1/2 h-4 w-4 -translate-x-1/2 rotate-45 border-b-[2.5px] border-r-[2.5px] border-[var(--color-ink)] bg-white" />
    </div>
  );
}
