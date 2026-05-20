const steps = [
  {
    n: "01",
    title: "Connect to the patient chart",
    body: "Run via Docker Compose or Helm; point at your Postgres. FHIR R4 endpoints are live for Patient / Condition / MedicationRequest / Observation. SMART-on-FHIR launch is next, so the app launches inside Epic, Cerner, or Athena without context switching.",
  },
  {
    n: "02",
    title: "Clinicians work in the AI surfaces",
    body: "Symptom analyzer returns evidence-cited differentials with urgency triage. SOAP / discharge / procedure templates draft themselves. Drug interaction and allergy checks fire on every prescription. Triage routes free-text symptoms to the right urgency band.",
  },
  {
    n: "03",
    title: "Audit, measure, prove",
    body: "Every read and write is captured in an append-only audit log. Per-clinician minutes-saved telemetry (v1.3 ticket 1.9) closes the loop with admins: the AI surfaces are only valuable if they save time, and that number is the one that closes the YC slide.",
  },
];

export function HowItWorks() {
  return (
    <section id="how-it-works" className="bg-white py-24">
      <div className="container-1280">
        <div className="mx-auto max-w-2xl text-center">
          <div className="eyebrow">How it fits</div>
          <h2 className="mt-3 text-[32px] font-bold leading-[1.15] tracking-[-0.015em] text-ink sm:text-[44px]">
            Drops in next to your EHR. No rip-and-replace.
          </h2>
        </div>

        <div className="relative mt-14">
          <div
            aria-hidden
            className="absolute left-1/2 top-0 hidden h-full w-px -translate-x-1/2 bg-gradient-to-b from-brand-200 via-brand-300 to-brand-100 lg:block"
          />
          <ol className="grid grid-cols-1 gap-8 lg:grid-cols-3">
            {steps.map((s) => (
              <li
                key={s.n}
                className="relative rounded-2xl border border-black/5 bg-white p-8 shadow-card"
              >
                <div className="text-sm font-mono font-semibold tracking-widest text-brand-700">
                  {s.n}
                </div>
                <h3 className="mt-3 text-[20px] font-semibold text-ink">
                  {s.title}
                </h3>
                <p className="mt-3 text-[15px] leading-relaxed text-body">
                  {s.body}
                </p>
              </li>
            ))}
          </ol>
        </div>
      </div>
    </section>
  );
}
