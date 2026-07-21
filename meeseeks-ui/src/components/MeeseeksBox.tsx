"use client";

/** The Meeseeks Box — teal faceted cube with the big blue summon button. */
export default function MeeseeksBox({ size = 150, pressed = false }: { size?: number; pressed?: boolean }) {
  const INK = "#17140f";
  return (
    <svg width={size} height={size * (150 / 160)} viewBox="0 0 160 150" fill="none" aria-hidden="true">
      <defs>
        <clipPath id="boxbody">
          <rect x="26" y="46" width="108" height="90" rx="14" />
        </clipPath>
      </defs>

      {/* feet */}
      <rect x="38" y="130" width="18" height="12" rx="4" fill="#1c4a55" stroke={INK} strokeWidth="4" />
      <rect x="104" y="130" width="18" height="12" rx="4" fill="#1c4a55" stroke={INK} strokeWidth="4" />

      {/* body */}
      <rect x="26" y="46" width="108" height="90" rx="14" fill="#2f8f7e" stroke={INK} strokeWidth="4.5" />

      {/* harlequin facets */}
      <g clipPath="url(#boxbody)" stroke={INK} strokeWidth="1.6" strokeLinejoin="round">
        {[
          [52, 72], [80, 72], [108, 72],
          [52, 106], [80, 106], [108, 106],
        ].map(([x, y], i) => (
          <path
            key={i}
            d={`M${x} ${y - 18} L${x + 18} ${y} L${x} ${y + 18} L${x - 18} ${y} Z`}
            fill={i % 2 === 0 ? "#23705f" : "#46b79c"}
          />
        ))}
      </g>
      {/* re-stroke body edge over facets */}
      <rect x="26" y="46" width="108" height="90" rx="14" fill="none" stroke={INK} strokeWidth="4.5" />

      {/* button */}
      <g style={{ transform: pressed ? "translateY(5px)" : "translateY(0)", transition: "transform 90ms ease" }}>
        <ellipse cx="80" cy="46" rx="26" ry="11" fill="#1c4a55" stroke={INK} strokeWidth="4" />
        <ellipse cx="80" cy="40" rx="20" ry="16" fill="#4aa6e2" stroke={INK} strokeWidth="4" />
        <ellipse cx="74" cy="34" rx="7" ry="4" fill="#fff" opacity="0.75" />
      </g>
    </svg>
  );
}
