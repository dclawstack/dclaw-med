import { GITHUB_URL } from "@/lib/site";

export function Footer() {
  return (
    <footer className="border-t border-black/5 bg-white py-12">
      <div className="container-1280 flex flex-col items-start justify-between gap-6 sm:flex-row sm:items-center">
        <div className="flex items-center gap-2 text-ink">
          <span
            aria-hidden
            className="inline-block h-6 w-6 rounded-md bg-gradient-to-br from-brand-700 to-brand-500"
          />
          <span className="text-[15px] font-semibold tracking-tight">
            DClaw Med
          </span>
          <span className="ml-3 text-[13px] text-meta">
            Part of the{" "}
            <a
              href="https://github.com/dclawstack"
              target="_blank"
              rel="noopener noreferrer"
              className="font-medium text-brand-700 underline-offset-4 hover:underline"
            >
              DClaw Stack
            </a>
          </span>
        </div>
        <nav className="flex flex-wrap items-center gap-6 text-[14px] text-body">
          <a
            href={GITHUB_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-brand-700"
          >
            GitHub
          </a>
          <a
            href={`${GITHUB_URL}/blob/main/README.md`}
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-brand-700"
          >
            README
          </a>
          <a
            href={`${GITHUB_URL}/blob/main/plan_v1.3.md`}
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-brand-700"
          >
            Roadmap
          </a>
          <a
            href={`${GITHUB_URL}/issues`}
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-brand-700"
          >
            Issues
          </a>
        </nav>
      </div>
      <div className="container-1280 mt-8 text-[12.5px] text-meta">
        © {new Date().getFullYear()} DClaw Med. Released under the same
        open-source terms as the DClaw Stack.
      </div>
    </footer>
  );
}
