import Link from "next/link";
import { N8N_URL } from "@/lib/api";

export default function NavBar() {
  return (
    <header className="sticky top-0 z-10 border-b-[2.5px] border-[var(--color-ink)] bg-[var(--color-cream-2)]">
      <nav className="mx-auto flex max-w-5xl items-center justify-between px-6 py-3">
        <Link href="/" className="flex items-center gap-2">
          <span aria-hidden className="grid h-7 w-7 place-items-center rounded-full border-[2.5px] border-[var(--color-ink)] bg-[var(--color-blue)]">
            <span className="block h-2.5 w-2.5 rounded-full bg-[var(--color-ink)]" />
          </span>
          <span className="font-[family-name:var(--font-display)] text-lg">Meeseeks Box</span>
        </Link>
        <div className="flex items-center gap-4 text-sm font-extrabold">
          <Link href="/" className="hover:text-[var(--color-blue-dk)]">Console</Link>
          <a href={`${N8N_URL}/home/workflows`} target="_blank" rel="noreferrer" className="hover:text-[var(--color-blue-dk)]">Workflows&nbsp;↗</a>
          <Link href="/inbox" className="hover:text-[var(--color-red)]">Attacker inbox</Link>
          <Link href="/graveyard" className="hover:text-[var(--color-magenta)]">Graveyard</Link>
        </div>
      </nav>
    </header>
  );
}
