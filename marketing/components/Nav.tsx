import Link from "next/link";
import { GITHUB_URL } from "@/lib/site";

export function Nav() {
  return (
    <header className="sticky top-0 z-40 border-b border-black/5 bg-white/80 backdrop-blur-md">
      <div className="container-1280 flex h-16 items-center justify-between">
        <Link href="/" className="flex items-center gap-2 text-ink">
          <span
            aria-hidden
            className="inline-block h-6 w-6 rounded-md bg-gradient-to-br from-brand-700 to-brand-500 shadow-brand"
          />
          <span className="text-[15px] font-semibold tracking-tight">
            DClaw Med
          </span>
          <span className="ml-2 hidden rounded-pill border border-brand-200 bg-brand-50 px-2 py-[2px] text-[11px] font-medium text-brand-700 sm:inline-block">
            v1.2 · open source
          </span>
        </Link>

        <nav className="hidden items-center gap-8 text-sm text-body md:flex">
          <a href="#features" className="hover:text-brand-700">
            Features
          </a>
          <a href="#how-it-works" className="hover:text-brand-700">
            How it works
          </a>
          <a href="#stack" className="hover:text-brand-700">
            Stack
          </a>
          <a href="#roadmap" className="hover:text-brand-700">
            Roadmap
          </a>
        </nav>

        <div className="flex items-center gap-3">
          <a
            href={GITHUB_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="hidden text-sm font-medium text-body hover:text-brand-700 sm:inline"
          >
            GitHub
          </a>
          <a
            href={GITHUB_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 rounded-pill bg-ink px-4 py-2 text-sm font-medium text-white shadow-card transition hover:bg-brand-700"
          >
            <svg
              aria-hidden
              viewBox="0 0 24 24"
              className="h-4 w-4"
              fill="currentColor"
            >
              <path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.11.79-.25.79-.55v-2.18c-3.2.7-3.87-1.36-3.87-1.36-.52-1.33-1.28-1.69-1.28-1.69-1.05-.71.08-.7.08-.7 1.16.08 1.77 1.19 1.77 1.19 1.03 1.76 2.7 1.25 3.36.96.1-.75.4-1.25.73-1.54-2.55-.29-5.24-1.28-5.24-5.69 0-1.26.45-2.29 1.19-3.1-.12-.29-.52-1.46.11-3.04 0 0 .97-.31 3.18 1.18a11.1 11.1 0 015.79 0c2.21-1.49 3.18-1.18 3.18-1.18.63 1.58.23 2.75.11 3.04.74.81 1.19 1.84 1.19 3.1 0 4.42-2.7 5.39-5.27 5.68.41.36.78 1.06.78 2.13v3.16c0 .3.21.67.8.55C20.21 21.38 23.5 17.07 23.5 12 23.5 5.65 18.35.5 12 .5z" />
            </svg>
            Star on GitHub
          </a>
        </div>
      </div>
    </header>
  );
}
