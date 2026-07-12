"use client";

function lerpHex(a: string, b: string, t: number): string {
  const av = a.match(/\w\w/g)!.map((x) => parseInt(x, 16));
  const bv = b.match(/\w\w/g)!.map((x) => parseInt(x, 16));
  return `#${av.map((v, i) => Math.round(v + (bv[i] - v) * t).toString(16).padStart(2, "0")).join("")}`;
}

/**
 * The Meeseeks Box as an industrial object: plastic housing, a screen with the
 * Meeseeks inside it, a speaker grille, and the big summon button. The screen
 * skin goes cyan -> vermilion with instability. Purely presentational.
 */
export default function MeeseeksDevice({
  instability = 0,
  size = 300,
}: {
  instability?: number;
  size?: number;
}) {
  const panic = Math.min(1, Math.max(0, instability / 100));
  const skin = lerpHex("10c4d6", "ff4a1c", panic);
  const mono = "font-[family-name:var(--font-mono)]";
  return (
    <svg width={size} height={size * (380 / 300)} viewBox="0 0 300 380" fill="none" aria-hidden="true">
      <defs>
        <linearGradient id="plastic" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#ffffff" />
          <stop offset="1" stopColor="#e4e7e0" />
        </linearGradient>
        <radialGradient id="btn" cx="0.5" cy="0.15" r="0.9">
          <stop offset="0" stopColor="#5fe2ef" />
          <stop offset="0.45" stopColor="#10c4d6" />
          <stop offset="1" stopColor="#0a93a1" />
        </radialGradient>
      </defs>

      {/* housing */}
      <rect x="6" y="6" width="288" height="368" rx="30" fill="url(#plastic)" stroke="#15191b" strokeOpacity="0.14" />
      {/* corner screws */}
      {[[26, 26], [274, 26], [26, 354], [274, 354]].map(([cx, cy], i) => (
        <g key={i}>
          <circle cx={cx} cy={cy} r="4" fill="#cfd2cb" />
          <line x1={cx - 2.5} y1={cy} x2={cx + 2.5} y2={cy} stroke="#9aa09a" strokeWidth="1" />
        </g>
      ))}

      {/* model plate */}
      <rect x="108" y="22" width="84" height="20" rx="6" fill="#15191b" />
      <text x="150" y="36" textAnchor="middle" fontSize="11" letterSpacing="2" fill="#ecede8" className={mono}>
        MSX-1
      </text>

      {/* screen */}
      <rect x="40" y="58" width="220" height="150" rx="14" fill="#0c0f11" />
      <rect x="40" y="58" width="220" height="150" rx="14" fill="none" stroke={skin} strokeOpacity="0.35" />
      {/* the Meeseeks, on-screen */}
      <g transform="translate(0,4)">
        <path d="M150 82c-20 0-30 22-30 44 0 24 13 40 30 40s30-16 30-40c0-22-10-44-30-44Z" fill={skin} />
        <ellipse cx="139" cy="126" rx="9" ry="11" fill="#ffffff" />
        <ellipse cx="161" cy="126" rx="9" ry="11" fill="#ffffff" />
        <circle cx={139 + panic * 2} cy="128" r={4 - panic * 1.5} fill="#0c0f11" />
        <circle cx={161 - panic * 2} cy="128" r={4 - panic * 1.5} fill="#0c0f11" />
        <path
          d={panic < 0.5 ? "M141 150 Q150 157 159 150" : "M141 154 Q150 147 159 154"}
          stroke="#0c0f11"
          strokeWidth="2.5"
          strokeLinecap="round"
          fill="none"
        />
      </g>
      {/* scanlines */}
      {[74, 96, 118, 140, 162, 184].map((y) => (
        <line key={y} x1="40" y1={y} x2="260" y2={y} stroke={skin} strokeOpacity="0.06" strokeWidth="2" />
      ))}

      {/* brand */}
      <text x="150" y="232" textAnchor="middle" fontSize="12" letterSpacing="4" fill="#5a6468" className={mono}>
        MEESEEKS
      </text>

      {/* speaker grille */}
      {[0, 1, 2, 3, 4].map((i) => (
        <rect key={i} x="100" y={248 + i * 9} width="100" height="3.5" rx="1.75" fill="#15191b" fillOpacity="0.12" />
      ))}

      {/* summon button */}
      <circle cx="150" cy="322" r="42" fill="none" stroke="#15191b" strokeOpacity="0.12" />
      <circle cx="150" cy="322" r="34" fill="url(#btn)" />
      <ellipse cx="150" cy="310" rx="20" ry="9" fill="#ffffff" fillOpacity="0.35" />
    </svg>
  );
}
