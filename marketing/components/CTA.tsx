import { GITHUB_URL } from "@/lib/site";

export function CTA() {
  return (
    <section className="bg-gradient-to-br from-ink to-[#1c1828] py-24 text-white">
      <div className="container-1280">
        <div className="grid grid-cols-1 items-center gap-10 lg:grid-cols-12 lg:gap-12">
          <div className="lg:col-span-7">
            <div className="text-[13px] font-semibold uppercase tracking-widest text-brand-300">
              Want it on your stack?
            </div>
            <h2 className="mt-3 text-[34px] font-bold leading-[1.1] tracking-[-0.015em] sm:text-[46px]">
              Clone it. Run it. Push the first PR.
            </h2>
            <p className="mt-5 max-w-2xl text-lg leading-relaxed text-white/70">
              The whole thing is open source under the DClaw Stack. Clone, run{" "}
              <span className="font-mono text-brand-200">make dev</span> against
              a local SQLite, seed demo patients with{" "}
              <span className="font-mono text-brand-200">make seed</span>, and
              you&rsquo;re on the dashboard in under five minutes.
            </p>
          </div>
          <div className="lg:col-span-5">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur">
              <pre className="overflow-x-auto font-mono text-[13px] leading-relaxed text-white/90">
{`git clone ${GITHUB_URL.replace("https://", "")}
cd dclaw-med/backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
make dev   # sqlite, no docker required
make seed  # 10 patients, 3 demo users`}
              </pre>
              <div className="mt-5 flex flex-wrap gap-3">
                <a
                  href={GITHUB_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 rounded-pill bg-white px-5 py-2.5 text-sm font-semibold text-ink shadow-card transition hover:bg-brand-100"
                >
                  Open the repo
                </a>
                <a
                  href={`${GITHUB_URL}/blob/main/plan_v1.3.md`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 rounded-pill border border-white/20 px-5 py-2.5 text-sm font-semibold text-white transition hover:border-brand-300 hover:text-brand-200"
                >
                  Read the v1.3 plan
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
