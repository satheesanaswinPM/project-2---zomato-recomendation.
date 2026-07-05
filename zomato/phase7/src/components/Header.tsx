import { CompassLogo } from "@/components/Icons";

export function Header() {
  return (
    <header className="mb-8 flex items-center justify-between gap-4">
      <div className="flex items-center gap-3">
        <CompassLogo className="h-9 w-9 shrink-0" />
        <span className="font-serif text-2xl font-semibold text-brand sm:text-[1.65rem]">
          Culinary Compass
        </span>
      </div>

      <nav className="hidden items-center gap-8 text-sm font-medium text-ink-secondary md:flex">
        <a href="#" className="transition-colors hover:text-brand">
          Home
        </a>
        <a href="#" className="transition-colors hover:text-brand">
          Discovery
        </a>
      </nav>

      <button
        type="button"
        className="rounded-lg bg-brand px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-brand-hover sm:px-5 sm:py-2.5"
      >
        Sign In
      </button>
    </header>
  );
}
