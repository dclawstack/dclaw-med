import { GITHUB_URL } from "@/lib/site";

export function Hero() {
  return (
    <section className="relative overflow-hidden">
      {/* gradient wash */}
      <div
        aria-hidden
        className="absolute inset-x-0 top-0 h-[640px] -z-10 bg-gradient-to-b from-brand-50 to-white"
      />
      <div
        aria-hidden
        className="absolute -right-32 -top-32 -z-10 h-[520px] w-[520px] rounded-full bg-brand-200 opacity-40 blur-3xl"
      />
      <div
        aria-hidden
        className="absolute -left-32 top-40 -z-10 h-[420px] w-[420px] rounded-full bg-brand-100 opacity-70 blur-3xl"
      />

      <div className="container-1280 grid grid-cols-1 gap-12 pt-20 pb-24 lg:grid-cols-12 lg:gap-8 lg:pt-28 lg:pb-32">
        <div className="lg:col-span-7">
          <div className="eyebrow inline-flex items-center gap-2">
            <span className="inline-block h-2 w-2 rounded-full bg-brand-700" />
            Open-source clinical intelligence
          </div>

          <h1 className="mt-5 text-[40px] font-bold leading-[1.06] tracking-[-0.025em] text-ink sm:text-[56px] lg:text-[72px]">
            Clinical intelligence,
            <br className="hidden sm:block" />{" "}
            <span className="bg-gradient-to-r from-brand-800 to-brand-500 bg-clip-text text-transparent">
              not billing software.
            </span>
          </h1>

          <p className="mt-6 max-w-2xl text-lg leading-relaxed text-body sm:text-xl">
            DClaw Med drops in next to your EHR via FHIR. Real LLM-backed
            differentials with cited evidence, ambient documentation, drug
            interaction & allergy safety nets, and an audit trail clinicians and
            compliance can both live with. No rip-and-replace.
          </p>

          <div className="mt-9 flex flex-wrap items-center gap-4">
            <a
              href={GITHUB_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-pill bg-brand-700 px-6 py-3 text-sm font-semibold text-white shadow-brand transition hover:bg-brand-800"
            >
              View on GitHub
              <svg viewBox="0 0 20 20" aria-hidden className="h-4 w-4">
                <path
                  fill="currentColor"
                  d="M5 10h9.5l-3.7-3.7L12 5l6 6-6 6-1.2-1.3L14.5 12H5z"
                />
              </svg>
            </a>
            <a
              href="#features"
              className="inline-flex items-center gap-2 rounded-pill border border-black/10 bg-white px-6 py-3 text-sm font-semibold text-ink shadow-card transition hover:border-brand-300 hover:text-brand-700"
            >
              See features
            </a>
          </div>

          <ul className="mt-10 flex flex-wrap gap-x-8 gap-y-3 text-sm text-meta">
            <li className="flex items-center gap-2">
              <Check />
              HIPAA-aware audit trail
            </li>
            <li className="flex items-center gap-2">
              <Check />
              FHIR R4 export
            </li>
            <li className="flex items-center gap-2">
              <Check />
              LLM with evidence_refs
            </li>
            <li className="flex items-center gap-2">
              <Check />
              Drop-in via Docker / Helm
            </li>
          </ul>
        </div>

        {/* hero "screenshot" card — pure CSS, no images */}
        <div className="lg:col-span-5">
          <HeroCard />
        </div>
      </div>
    </section>
  );
}

function Check() {
  return (
    <svg
      viewBox="0 0 20 20"
      aria-hidden
      className="h-4 w-4 text-brand-700"
      fill="currentColor"
    >
      <path d="M8.3 13.3 4.7 9.7l1.4-1.4 2.2 2.2 5.6-5.6 1.4 1.4z" />
    </svg>
  );
}

function HeroCard() {
  return (
    <div className="grain rounded-3xl bg-gradient-to-br from-ink to-[#1e1828] p-1 shadow-soft">
      <div className="rounded-[22px] bg-[#0e0c14] p-6 ring-1 ring-white/5">
        <div className="flex items-center gap-1.5 pb-4">
          <span className="h-3 w-3 rounded-full bg-[#ff5f57]" />
          <span className="h-3 w-3 rounded-full bg-[#febc2e]" />
          <span className="h-3 w-3 rounded-full bg-[#28c840]" />
          <span className="ml-3 font-mono text-[11px] text-white/40">
            POST /api/v1/med/symptoms/analyze
          </span>
        </div>

        <pre className="overflow-x-auto rounded-xl bg-black/40 p-4 font-mono text-[12.5px] leading-relaxed text-white/90 ring-1 ring-white/5">
{`{
  "differential_diagnoses": [
    {
      "condition": "Acute ST-elevation MI",
      "icd10_code": "I21.9",
      "confidence": 0.90,
      "reasoning": "Crushing chest pain
        radiating to left arm with
        diaphoresis is the classic
        presentation of acute MI.",
      "evidence_refs": [
        { "source": "patient-symptoms",
          "excerpt": "..." }
      ]
    },
    { "condition": "Unstable angina",   ... },
    { "condition": "Aortic dissection", ... }
  ],
  "recommended_tests": [
    "12-lead ECG",
    "Cardiac troponin I/T",
    "Chest X-ray"
  ],
  "urgency_level": `}<span className="text-[#ff7e7e]">{`"critical"`}</span>{`
}`}
        </pre>

        <div className="mt-4 flex items-center justify-between text-[11px]">
          <div className="flex items-center gap-2 text-white/50">
            <span className="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
            <span className="font-mono">moonshotai/kimi-k2</span>
          </div>
          <span className="rounded-full bg-[#ff7e7e]/15 px-2.5 py-1 font-medium text-[#ffb1b1]">
            URGENCY · critical
          </span>
        </div>
      </div>
    </div>
  );
}
