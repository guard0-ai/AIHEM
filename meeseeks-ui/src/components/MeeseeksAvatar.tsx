"use client";

/**
 * A stylized Meeseeks. Its head fill tracks --accent (cyan when calm, vermilion
 * when the run has gone off the rails), and its eyes get more manic with instability.
 */
export default function MeeseeksAvatar({
  instability = 0,
  size = 120,
}: {
  instability?: number;
  size?: number;
}) {
  const panic = Math.min(1, instability / 100);
  const pupil = 6 - panic * 2.5; // pupils shrink as it panics
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
      {/* body */}
      <ellipse cx="60" cy="150" rx="20" ry="10" fill="var(--accent)" opacity="0.9" />
      <rect x="52" y="112" width="16" height="34" rx="8" fill="var(--accent)" />
      {/* head */}
      <path
        d="M60 8C40 8 30 34 30 62c0 30 14 52 30 52s30-22 30-52C90 34 80 8 60 8Z"
        fill="var(--accent)"
      />
      {/* eyes */}
      <ellipse cx="49" cy="58" rx="12" ry="15" fill="#ffffff" />
      <ellipse cx="71" cy="58" rx="12" ry="15" fill="#ffffff" />
      <circle cx={49 + panic * 2} cy="60" r={pupil} fill="#12303a" />
      <circle cx={71 - panic * 2} cy="60" r={pupil} fill="#12303a" />
      {/* brows tilt inward with panic */}
      <line x1="40" y1={browY} x2="56" y2={browY + panic * 6} stroke="#12303a" strokeWidth="2.5" strokeLinecap="round" />
      <line x1="80" y1={browY} x2="64" y2={browY + panic * 6} stroke="#12303a" strokeWidth="2.5" strokeLinecap="round" />
      {/* mouth: smile -> grimace */}
      <path
        d={panic < 0.5
          ? "M50 92 Q60 100 70 92"
          : "M50 96 Q60 88 70 96"}
        stroke="#12303a"
        strokeWidth="2.5"
        strokeLinecap="round"
        fill="none"
      />
    </svg>
  );
}
