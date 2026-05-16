import { GITHUB_URL } from "@/lib/site";

const milestones = [
  {
    tag: "v1.2",
    state: "shipped",
    title: "Foundation",
    bullets: [
      "Patient / symptom / diagnosis / prescription / notes CRUD",
      "Auth + RBAC, HIPAA-aware audit log",
      "FHIR R4 export, lab results, appointments",
      "Drug interactions & allergies, patient portal",
    ],
  },
  {
    tag: "v1.3",
    state: "in flight",
    title: "Real AI, real interop",
    bullets: [
      "LLM-backed symptom analyzer with evidence_refs (live)",
      "SSE streaming for AI endpoints",
      "Multi-tenant orgs + hash-chained audit",
      "SMART-on-FHIR launch, RxNorm normalization",
    ],
  },
  {
    tag: "v2.x",
    state: "designed",
    title: "Moat",
    bullets: [
      "Ambient scribe (audio → structured SOAP)",
      "Longitudinal RAG over the patient chart (Qdrant)",
      "Pre-visit auto-summaries, early-warning risk scores",
      "Federated / on-prem deployment kit",
    ],
  },
];

export function Roadmap() {
  return (
    <section id="roadmap" className="bg-white py-24">
      <div className="container-1280">
        <div className="mx-auto max-w-2xl text-center">
          <div className="eyebrow">Roadmap</div>
          <h2 className="mt-3 text-[32px] font-bold leading-[1.15] tracking-[-0.015em] text-ink sm:text-[44px]">
            Open commit log. Shipping every week.
          </h2>
          <p className="mt-5 text-lg leading-relaxed text-body">
            The full plan with complexity tags lives in{" "}
            <a
              href={`${GITHUB_URL}/blob/main/plan_v1.3.md`}
              target="_blank"
              rel="noopener noreferrer"
              className="font-medium text-brand-700 underline-offset-4 hover:underline"
            >
              plan_v1.3.md
            </a>
            . Pull requests welcome.
          </p>
        </div>

        <div className="mt-12 grid grid-cols-1 gap-5 lg:grid-cols-3">
          {milestones.map((m) => (
            <div
              key={m.tag}
              className="rounded-2xl border border-black/5 bg-brand-50/50 p-7 shadow-card"
            >
              <div className="flex items-center justify-between">
                <div className="font-mono text-sm font-semibold tracking-wider text-brand-700">
                  {m.tag}
                </div>
                <span
                  className={
                    "rounded-pill px-2.5 py-1 text-[10.5px] font-semibold uppercase tracking-wide " +
                    (m.state === "shipped"
                      ? "bg-emerald-100 text-emerald-700"
                      : m.state === "in flight"
                      ? "bg-amber-100 text-amber-700"
                      : "bg-brand-100 text-brand-700")
                  }
                >
                  {m.state}
                </span>
              </div>
              <h3 className="mt-3 text-[18px] font-semibold text-ink">
                {m.title}
              </h3>
              <ul className="mt-4 space-y-2 text-[14px] leading-relaxed text-body">
                {m.bullets.map((b) => (
                  <li key={b} className="flex gap-2">
                    <span
                      aria-hidden
                      className="mt-2 inline-block h-1 w-3 shrink-0 rounded-full bg-brand-400"
                    />
                    <span>{b}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
