"use client";

/**
 * Mr. Meeseeks. Big egg head, orange tuft, big dopey eyes, and a long thin
 * noodle body with hands on hips. Calm = wide smile. As instability rises he
 * panics — brows angle in, mouth opens into the magenta scream, sweat flies.
 * He stays blue (the show never turns him red); the dread is all in the face.
 */
export default function MeeseeksAvatar({
  instability = 0,
  size = 150,
}: {
  instability?: number;
  size?: number;
}) {
  const p = Math.min(1, Math.max(0, instability / 100));
  const scream = p > 0.45;
  const BLUE = "#78cfec";
  const BLUE_LT = "#a9e2f5";
  const INK = "#17140f";
  const s = { stroke: INK, strokeWidth: 5, strokeLinecap: "round" as const, strokeLinejoin: "round" as const };

  return (
    <svg
      width={size}
      height={size * (420 / 220)}
      viewBox="0 0 220 420"
      fill="none"
      aria-hidden="true"
      className="jitter"
    >
      {/* ground shadow */}
      <ellipse cx="110" cy="406" rx="56" ry="8" fill={INK} opacity="0.1" />

      {/* legs (black underlay + blue) */}
      {[[100, 98], [120, 122]].map(([hipX, footX], i) => (
        <g key={i}>
          <path d={`M${hipX} 300 L${footX} 392`} stroke={INK} strokeWidth="17" strokeLinecap="round" />
          <path d={`M${hipX} 300 L${footX} 392`} stroke={BLUE} strokeWidth="11" strokeLinecap="round" />
          <ellipse cx={footX} cy="398" rx="14" ry="6.5" fill={BLUE} {...s} />
        </g>
      ))}

      {/* torso — long, thin, gently tapered noodle (over leg tops) */}
      <path
        d="M80 150 C74 205 86 214 87 250 C88 285 96 302 110 304 C124 302 132 285 133 250 C134 214 146 205 140 150 Z"
        fill={BLUE}
        {...s}
      />
      {/* soft central sheen */}
      <ellipse cx="110" cy="250" rx="13" ry="44" fill={BLUE_LT} opacity="0.5" />

      {/* head (over torso top to hide the neck seam) */}
      <ellipse cx="110" cy="92" rx="58" ry="66" fill={BLUE} {...s} />

      {/* arms — hands on hips (calm) / flung up (panic) */}
      {!scream ? (
        <>
          {[["M72 172 Q50 214 62 238 Q73 254 88 250", ""], ["M148 172 Q170 214 158 238 Q147 254 132 250", ""]].map(([d], i) => (
            <g key={i}>
              <path d={d} stroke={INK} strokeWidth="17" fill="none" strokeLinecap="round" strokeLinejoin="round" />
              <path d={d} stroke={BLUE} strokeWidth="11" fill="none" strokeLinecap="round" strokeLinejoin="round" />
            </g>
          ))}
        </>
      ) : (
        <>
          {["M72 172 Q44 148 40 112", "M148 172 Q176 148 180 112"].map((d, i) => (
            <g key={i}>
              <path d={d} stroke={INK} strokeWidth="17" fill="none" strokeLinecap="round" />
              <path d={d} stroke={BLUE} strokeWidth="11" fill="none" strokeLinecap="round" />
            </g>
          ))}
        </>
      )}

      {/* orange tuft */}
      {[[95, 12], [108, 2], [121, 12]].map(([x, ty], i) => (
        <path key={i} d={`M${x - 8} 34 Q${x} ${ty} ${x + 8} 34 Z`} fill="#f2872e" stroke={INK} strokeWidth="3" strokeLinejoin="round" />
      ))}

      {/* brows (panic) */}
      {scream && (
        <>
          <path d="M74 66 L98 74" stroke={INK} strokeWidth="5" strokeLinecap="round" />
          <path d="M146 66 L122 74" stroke={INK} strokeWidth="5" strokeLinecap="round" />
        </>
      )}

      {/* eyes */}
      <ellipse cx="92" cy={scream ? 84 : 82} rx={scream ? 9 : 8} ry={scream ? 13 : 11} fill={INK} />
      <ellipse cx="128" cy={scream ? 84 : 82} rx={scream ? 9 : 8} ry={scream ? 13 : 11} fill={INK} />
      <circle cx="95" cy={scream ? 80 : 78} r="2.6" fill="#fff" />
      <circle cx="131" cy={scream ? 80 : 78} r="2.6" fill="#fff" />

      {/* mouth */}
      {!scream ? (
        <path d="M84 114 Q110 142 136 114" stroke={INK} strokeWidth="5" fill="none" strokeLinecap="round" />
      ) : (
        <g>
          <ellipse cx="110" cy="126" rx="27" ry="19" fill="#c0267e" stroke={INK} strokeWidth="5" />
          <path d="M86 118 Q110 112 134 118 L131 124 Q110 119 89 124 Z" fill="#fff" />
          <ellipse cx="110" cy="136" rx="10" ry="6" fill="#8a1a5a" />
        </g>
      )}

      {/* sweat (panic) */}
      {scream && (
        <>
          <path d="M163 76 q6 10 0 16 q-6 -6 0 -16 Z" fill={BLUE_LT} stroke={INK} strokeWidth="2.5" />
          <path d="M55 80 q6 10 0 16 q-6 -6 0 -16 Z" fill={BLUE_LT} stroke={INK} strokeWidth="2.5" />
        </>
      )}
    </svg>
  );
}
