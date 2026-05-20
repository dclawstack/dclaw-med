import Link from "next/link";
import { APP_URL, GITHUB_URL } from "@/lib/site";

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
            href={APP_URL}
            className="inline-flex items-center gap-2 rounded-pill bg-brand-700 px-4 py-2 text-sm font-semibold text-white shadow-brand transition hover:bg-brand-800"
          >
            Launch app
            <svg viewBox="0 0 20 20" aria-hidden className="h-4 w-4">
              <path
                fill="currentColor"
                d="M5 10h9.5l-3.7-3.7L12 5l6 6-6 6-1.2-1.3L14.5 12H5z"
              />
            </svg>
          </a>
        </div>
      </div>
    </header>
  );
}
