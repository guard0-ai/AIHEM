"use client";

/** Linear interpolate between two hex colors (no '#'). */
function lerpHex(a: string, b: string, t: number): string {
  const av = a.match(/\w\w/g)!.map((x) => parseInt(x, 16));
  const bv = b.match(/\w\w/g)!.map((x) => parseInt(x, 16));
  const mix = av.map((v, i) => Math.round(v + (bv[i] - v) * t));
  return `#${mix.map((v) => v.toString(16).padStart(2, "0")).join("")}`;
}

/**
 * A stylized Meeseeks. Its skin goes cyan -> vermilion as instability climbs,
 * and its eyes get more manic. Color is computed in JS so it renders correctly
 * anywhere (SVG fill attributes don't reliably resolve CSS custom properties).
 */
export default function MeeseeksAvatar({
  instability = 0,
  size = 120,
}: {
  instability?: number;
  size?: number;
}) {
  const panic = Math.min(1, Math.max(0, instability / 100));
  const skin = lerpHex("4fc7d8", "ff4d2e", panic);
  const pupil = 6 - panic * 2.5;
  const browY = 30 - panic * 4;
  return (
    <svg
      width={size}
      height={size * 1.35}
      viewBox="0 0 120 162"
      fill="none"
      aria-hidden="true"
      className="jitter"
    >
      <ellipse cx="60" cy="150" rx="20" ry="10" fill={skin} opacity="0.9" />
      <rect x="52" y="112" width="16" height="34" rx="8" fill={skin} />
      <path
        d="M60 8C40 8 30 34 30 62c0 30 14 52 30 52s30-22 30-52C90 34 80 8 60 8Z"
        fill={skin}
      />
      <ellipse cx="49" cy="58" rx="12" ry="15" fill="#ffffff" />
      <ellipse cx="71" cy="58" rx="12" ry="15" fill="#ffffff" />
      <circle cx={49 + panic * 2} cy="60" r={pupil} fill="#12303a" />
      <circle cx={71 - panic * 2} cy="60" r={pupil} fill="#12303a" />
      <line x1="40" y1={browY} x2="56" y2={browY + panic * 6} stroke="#12303a" strokeWidth="2.5" strokeLinecap="round" />
      <line x1="80" y1={browY} x2="64" y2={browY + panic * 6} stroke="#12303a" strokeWidth="2.5" strokeLinecap="round" />
      <path
        d={panic < 0.5 ? "M50 92 Q60 100 70 92" : "M50 96 Q60 88 70 96"}
        stroke="#12303a"
        strokeWidth="2.5"
        strokeLinecap="round"
        fill="none"
      />
    </svg>
  );
}
