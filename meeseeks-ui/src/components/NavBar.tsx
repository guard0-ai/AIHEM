import Link from "next/link";

export default function NavBar() {
  return (
    <header className="w-full border-b border-[rgba(18,48,58,0.08)] bg-white/70 backdrop-blur">
      <nav className="mx-auto flex max-w-5xl items-center justify-between px-6 py-3">
        <Link href="/" className="flex items-center gap-2">
          <span className="grid h-7 w-7 place-items-center rounded-lg bg-[var(--color-brand)] text-white font-bold">
            M
          </span>
          <span className="font-[family-name:var(--font-display)] text-lg font-semibold">
            Meeseeks Box
          </span>
        </Link>
        <div className="flex items-center gap-5 text-sm text-[var(--color-ink-soft)]">
          <Link href="/" className="hover:text-[var(--color-ink)]">
            The Box
          </Link>
          <Link href="/inbox" className="hover:text-[var(--color-alarm)]">
            Attacker Inbox
          </Link>
          <Link href="/graveyard" className="hover:text-[var(--color-ink)]">
            Graveyard
          </Link>
        </div>
      </nav>
    </header>
  );
}
