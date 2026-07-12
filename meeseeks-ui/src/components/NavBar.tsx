import Link from "next/link";

export default function NavBar() {
  return (
    <header className="sticky top-0 z-10 border-b border-[var(--line)] bg-[var(--color-paper)]/85 backdrop-blur">
      <nav className="mx-auto flex max-w-5xl items-center justify-between px-6 py-3">
        <Link href="/" className="flex items-center gap-2.5">
          <span
            aria-hidden
            className="grid h-6 w-6 place-items-center rounded-[7px] bg-[var(--color-ink)] text-[10px] font-bold text-[var(--color-cyan)]"
          >
            M
          </span>
          <span className="font-[family-name:var(--font-display)] text-[15px] font-bold tracking-tight">
            MEESEEKS BOX
          </span>
        </Link>
        <div className="flex items-center gap-5">
          <Link href="/" className="spec hover:text-[var(--color-ink)]">
            console
          </Link>
          <Link href="/inbox" className="spec hover:text-[var(--color-vermilion)]">
            attacker inbox
          </Link>
          <Link href="/graveyard" className="spec hover:text-[var(--color-ink)]">
            graveyard
          </Link>
        </div>
      </nav>
    </header>
  );
}
