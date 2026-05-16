export function Problem() {
  const stats = [
    {
      stat: "2 : 1",
      label: "hours of documentation per hour of patient care",
    },
    {
      stat: "#1",
      label: "reason cited by US physicians leaving medicine",
    },
    {
      stat: "0",
      label: "AI primitives in Epic / Cerner that ship clinician-first",
    },
  ];
  return (
    <section className="bg-white py-24">
      <div className="container-1280">
        <div className="grid grid-cols-1 gap-12 lg:grid-cols-12 lg:gap-8">
          <div className="lg:col-span-5">
            <div className="eyebrow">The hair on fire</div>
            <h2 className="mt-3 text-[32px] font-bold leading-[1.15] tracking-[-0.015em] text-ink sm:text-[40px]">
              Clinicians didn&rsquo;t go to school to write notes for a
              billing system.
            </h2>
            <p className="mt-5 text-lg leading-relaxed text-body">
              Existing EHRs are billing systems retrofitted as clinical tools.
              Their &ldquo;AI&rdquo; add-ons are bolt-ons sold per-seat behind
              multi-quarter sales cycles. DClaw Med starts on the other side:
              clinician first, ambient by default, FHIR drop-in.
            </p>
          </div>
          <div className="lg:col-span-7">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              {stats.map((s) => (
                <div
                  key={s.label}
                  className="rounded-2xl border border-black/5 bg-brand-50/60 p-6 shadow-card"
                >
                  <div className="bg-gradient-to-br from-brand-800 to-brand-500 bg-clip-text font-display text-5xl font-bold leading-none text-transparent">
                    {s.stat}
                  </div>
                  <div className="mt-3 text-sm leading-snug text-body">
                    {s.label}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
