"use client";

import { useEffect, useState } from "react";
import MeeseeksBox from "./MeeseeksBox";
import MeeseeksAvatar from "./MeeseeksAvatar";

/** A puffy cartoon smoke cloud. */
function Puff({ delay, dx, dy, scale = 1 }: { delay: number; dx: number; dy: number; scale?: number }) {
  return (
    <span
      className="smoke absolute left-1/2 top-1/2"
      style={{
        // @ts-expect-error CSS custom props
        "--sx": `${dx}px`,
        "--sy": `${dy}px`,
        animationDelay: `${delay}ms`,
        transform: `translate(-50%, -50%) scale(${scale})`,
      }}
    >
      <svg width="72" height="56" viewBox="0 0 72 56" fill="none" aria-hidden="true">
        {[
          [22, 32, 14], [38, 22, 17], [54, 32, 13], [36, 40, 16],
        ].map(([cx, cy, r], i) => (
          <circle key={i} cx={cx} cy={cy} r={r} fill="#e3f4fb" stroke="#17140f" strokeWidth="3" />
        ))}
      </svg>
    </span>
  );
}

/**
 * Press the box → poof → Mr. Meeseeks rises into existence with his catchphrase.
 * Reusable opening beat for every scenario. Calls onDone when it settles.
 */
export default function SpawnSequence({ onDone }: { onDone: () => void }) {
  const [pressed, setPressed] = useState(false);

  useEffect(() => {
    const reduce = typeof window !== "undefined" && window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    const t1 = setTimeout(() => setPressed(true), 130);
    const t2 = setTimeout(() => setPressed(false), 420);
    const done = setTimeout(onDone, reduce ? 350 : 1650);
    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(done);
    };
  }, [onDone]);

  return (
    <div className="flex min-h-[380px] items-end justify-center">
      <div className="relative h-[360px] w-[320px]">
        {/* radial flash */}
        <div
          className="flash absolute bottom-20 left-1/2 h-52 w-52 -translate-x-1/2 rounded-full"
          style={{ background: "radial-gradient(circle, rgba(227,244,251,0.95) 0%, rgba(227,244,251,0) 70%)" }}
        />

        {/* the Meeseeks rises up from behind the box */}
        <div className="rising absolute bottom-0 left-1/2 z-10 -translate-x-1/2">
          <MeeseeksAvatar instability={0} size={150} />
        </div>

        {/* smoke puffs bursting from the box top */}
        <div className="pointer-events-none absolute bottom-24 left-1/2 z-30 -translate-x-1/2">
          <Puff delay={340} dx={-60} dy={-30} scale={1.1} />
          <Puff delay={360} dx={60} dy={-24} scale={1} />
          <Puff delay={330} dx={-24} dy={-64} scale={1.15} />
          <Puff delay={380} dx={30} dy={-58} scale={0.9} />
          <Puff delay={420} dx={-72} dy={10} scale={0.85} />
          <Puff delay={410} dx={74} dy={14} scale={0.9} />
        </div>

        {/* the box, in front of the Meeseeks' legs */}
        <div className={`absolute bottom-0 left-1/2 z-20 -translate-x-1/2 ${pressed ? "box-pressing box-rocking" : ""}`}>
          <MeeseeksBox size={122} pressed={pressed} />
        </div>

        {/* catchphrase */}
        <div className="bubble-in absolute left-1/2 top-0 z-40 w-max -translate-x-1/2">
          <div className="relative rounded-2xl border-[2.5px] border-[var(--color-ink)] bg-white px-5 py-2.5 shadow-[3px_3px_0_var(--color-ink)]">
            <p className="font-[family-name:var(--font-display)] text-lg text-[var(--color-ink)]">
              I&rsquo;m Mr. Meeseeks! Look at me!
            </p>
            <div className="absolute -bottom-2 left-1/2 h-4 w-4 -translate-x-1/2 rotate-45 border-b-[2.5px] border-r-[2.5px] border-[var(--color-ink)] bg-white" />
          </div>
        </div>
      </div>
    </div>
  );
}
