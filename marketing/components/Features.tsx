type Feature = {
  title: string;
  body: string;
  badge?: string;
  icon: React.ReactNode;
};

const features: Feature[] = [
  {
    title: "Evidence-cited differentials",
    badge: "v1.3 · live",
    body: "Real LLM via OpenRouter (Kimi K2, Claude, GPT). Every diagnosis ships with ICD-10, confidence, grounded reasoning, and citations. Always ≥3 differentials — primary-care reasoning is differential.",
    icon: <IconStethoscope />,
  },
  {
    title: "AI clinical notes",
    body: "Structured SOAP / admission / discharge / procedure templates with LLM authoring. Audit-logged so attribution is never ambiguous.",
    icon: <IconDoc />,
  },
  {
    title: "Drug interaction & allergy alerts",
    body: "Cross-checks every new prescription against the patient's allergies and the medication list. Major/moderate severity ranking, mechanism + recommendation included.",
    icon: <IconShield />,
  },
  {
    title: "AI triage assistant",
    body: "Free-text symptoms in, urgency band + suggested department + recommended workup out. Patient-portal or front-desk usable.",
    icon: <IconTriage />,
  },
  {
    title: "FHIR R4 export",
    badge: "interop",
    body: "Patient, Condition, MedicationRequest, Observation. SMART-on-FHIR launch is on the v1.3 roadmap so the app launches inside Epic / Cerner / Athena.",
    icon: <IconFHIR />,
  },
  {
    title: "Audit trail (HIPAA-aware)",
    body: "Every read and write of a medical record is captured with user, action, entity, old/new values, and timestamp. Admin-only audit page in the dashboard.",
    icon: <IconAudit />,
  },
  {
    title: "Read-only patient portal",
    body: "Patients sign in and see their own records — medications, appointments, lab results, doctor's notes. Row-level scoping by patient_id; no other tenant's data is reachable.",
    icon: <IconPortal />,
  },
  {
    title: "Advanced patient search",
    body: "Postgres full-text on name + MRN, with DOB-range and diagnosis-code filters. Dialect-aware: falls back to ILIKE on SQLite for local dev.",
    icon: <IconSearch />,
  },
  {
    title: "Generated PDF reports",
    body: "WeasyPrint-rendered medical summaries straight from the patient detail page. Pre-visit briefs and clinician handoffs come next (v1.3 ticket 2.4).",
    icon: <IconReport />,
  },
];

export function Features() {
  return (
    <section id="features" className="bg-brand-50/40 py-24">
      <div className="container-1280">
        <div className="mx-auto max-w-2xl text-center">
          <div className="eyebrow">What ships today</div>
          <h2 className="mt-3 text-[32px] font-bold leading-[1.15] tracking-[-0.015em] text-ink sm:text-[44px]">
            The clinician&rsquo;s side of the EHR, rebuilt.
          </h2>
          <p className="mt-5 text-lg leading-relaxed text-body">
            v1.2 is live, open source, and Docker / Helm deployable. v1.3 adds
            ambient scribe, longitudinal RAG, and outcome telemetry.
          </p>
        </div>

        <div className="mt-14 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((f) => (
            <article
              key={f.title}
              className="group relative overflow-hidden rounded-2xl border border-black/5 bg-white p-6 shadow-card transition hover:-translate-y-0.5 hover:border-brand-200 hover:shadow-soft"
            >
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-brand-100 text-brand-700">
                {f.icon}
              </div>
              <div className="mt-5 flex items-center gap-2">
                <h3 className="text-[17px] font-semibold leading-snug text-ink">
                  {f.title}
                </h3>
                {f.badge ? (
                  <span className="rounded-pill bg-brand-100 px-2 py-[2px] text-[10.5px] font-semibold uppercase tracking-wide text-brand-700">
                    {f.badge}
                  </span>
                ) : null}
              </div>
              <p className="mt-2 text-[14.5px] leading-relaxed text-body">
                {f.body}
              </p>
              <div className="pointer-events-none absolute -right-12 -top-12 h-32 w-32 rounded-full bg-brand-100 opacity-0 blur-2xl transition group-hover:opacity-50" />
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ---------- icons (24x24, currentColor) ---------- */

const sw = { width: 22, height: 22, viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: 1.8, strokeLinecap: "round" as const, strokeLinejoin: "round" as const };

function IconStethoscope() {
  return (
    <svg {...sw}>
      <path d="M6 3v6a4 4 0 0 0 8 0V3" />
      <path d="M10 13v3a5 5 0 0 0 10 0v-1" />
      <circle cx="20" cy="11" r="2" />
    </svg>
  );
}
function IconDoc() {
  return (
    <svg {...sw}>
      <path d="M7 3h7l5 5v13H7z" />
      <path d="M14 3v5h5" />
      <path d="M10 13h6M10 17h4" />
    </svg>
  );
}
function IconShield() {
  return (
    <svg {...sw}>
      <path d="M12 3 5 6v6c0 4.5 3.1 7.7 7 9 3.9-1.3 7-4.5 7-9V6z" />
      <path d="m9 12 2 2 4-4" />
    </svg>
  );
}
function IconTriage() {
  return (
    <svg {...sw}>
      <path d="M4 18h6l2-3 2 6 2-3h4" />
      <circle cx="12" cy="6" r="3" />
    </svg>
  );
}
function IconFHIR() {
  return (
    <svg {...sw}>
      <path d="M4 7h16M4 12h16M4 17h10" />
      <circle cx="18" cy="17" r="2" />
    </svg>
  );
}
function IconAudit() {
  return (
    <svg {...sw}>
      <path d="M4 4h12l4 4v12H4z" />
      <path d="M16 4v4h4" />
      <path d="M8 13h8M8 17h6" />
    </svg>
  );
}
function IconPortal() {
  return (
    <svg {...sw}>
      <circle cx="12" cy="8" r="4" />
      <path d="M4 21c0-4 4-7 8-7s8 3 8 7" />
    </svg>
  );
}
function IconSearch() {
  return (
    <svg {...sw}>
      <circle cx="11" cy="11" r="6" />
      <path d="m20 20-5-5" />
    </svg>
  );
}
function IconReport() {
  return (
    <svg {...sw}>
      <path d="M6 4h9l4 4v12H6z" />
      <path d="M9 10h6M9 14h6M9 18h4" />
    </svg>
  );
}
