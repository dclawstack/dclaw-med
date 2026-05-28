import { APP_URL } from "@/lib/site";

export function Demo() {
  return (
    <section id="demo" className="bg-brand-50/40 py-24">
      <div className="container-1280">
        <div className="mx-auto max-w-2xl text-center">
          <div className="eyebrow">Try it</div>
          <h2 className="mt-3 text-[32px] font-bold leading-[1.15] tracking-[-0.015em] text-ink sm:text-[44px]">
            Spin up a demo dataset.
          </h2>
          <p className="mt-5 text-lg leading-relaxed text-body">
            One click in the dashboard loads five demo patients with diagnoses
            and active prescriptions, plus a demo clinician account so you can
            sign in and poke around. One click takes it all away — the seed
            only ever touches rows tagged with the{" "}
            <code className="rounded bg-brand-100 px-1.5 py-0.5 font-mono text-[13px] text-brand-800">
              DEMO-
            </code>{" "}
            MRN prefix, so it&rsquo;s safe to run against a populated
            instance.
          </p>
        </div>

        <div className="mt-12 mx-auto max-w-3xl rounded-2xl border border-black/5 bg-white p-6 shadow-card sm:p-8">
          <div className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
            <div className="flex items-start gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-brand-100 text-brand-700">
                <svg
                  viewBox="0 0 24 24"
                  aria-hidden
                  width={22}
                  height={22}
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={1.8}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <ellipse cx="12" cy="5" rx="8" ry="3" />
                  <path d="M4 5v6c0 1.7 3.6 3 8 3s8-1.3 8-3V5" />
                  <path d="M4 11v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6" />
                </svg>
              </div>
              <div>
                <div className="text-[15px] font-semibold text-ink">
                  Demo dataset
                </div>
                <div className="text-[13.5px] text-body">
                  5 patients · 5 diagnoses · 5 active prescriptions · 1 demo
                  clinician account
                </div>
              </div>
            </div>
            <a
              href={`${APP_URL}/#demo`}
              className="inline-flex items-center gap-2 rounded-pill bg-brand-700 px-5 py-2.5 text-sm font-semibold text-white shadow-brand transition hover:bg-brand-800"
            >
              Try the live demo
              <svg viewBox="0 0 20 20" aria-hidden className="h-4 w-4">
                <path
                  fill="currentColor"
                  d="M5 10h9.5l-3.7-3.7L12 5l6 6-6 6-1.2-1.3L14.5 12H5z"
                />
              </svg>
            </a>
          </div>

          <p className="mt-6 text-[13px] leading-relaxed text-body">
            Clicking <em>Try the live demo</em> drops you on the in-app landing
            page. Hit <span className="font-medium text-ink">Seed demo data</span>{" "}
            and then <span className="font-medium text-ink">Sign in as demo doctor</span>{" "}
            to land in the dashboard. Need to clean up afterwards? The same
            section has a Clear button that wipes only the demo rows.
          </p>
        </div>
      </div>
    </section>
  );
}
