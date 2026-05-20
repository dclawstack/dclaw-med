const layers = [
  {
    layer: "Frontend",
    items: ["Next.js 14 App Router", "TypeScript", "Tailwind CSS", "shadcn/ui"],
  },
  {
    layer: "Backend",
    items: [
      "FastAPI",
      "SQLAlchemy 2.0 (async)",
      "Pydantic v2",
      "Alembic migrations",
    ],
  },
  {
    layer: "Data",
    items: [
      "Postgres 16 (prod)",
      "SQLite (dev mode)",
      "Qdrant (RAG, v1.3)",
      "Append-only audit",
    ],
  },
  {
    layer: "AI / LLM",
    items: [
      "OpenRouter gateway",
      "Kimi K2 / Claude / GPT",
      "Structured JSON output",
      "Evidence-cited",
    ],
  },
  {
    layer: "Ops",
    items: [
      "Docker Compose",
      "Helm / Kubernetes",
      "Prometheus /metrics",
      "X-Request-ID + structlog",
    ],
  },
];

export function Stack() {
  return (
    <section id="stack" className="bg-brand-50/40 py-24">
      <div className="container-1280">
        <div className="mx-auto max-w-2xl text-center">
          <div className="eyebrow">Built on</div>
          <h2 className="mt-3 text-[32px] font-bold leading-[1.15] tracking-[-0.015em] text-ink sm:text-[44px]">
            Boring tech where it matters, sharp tech where it counts.
          </h2>
          <p className="mt-5 text-lg leading-relaxed text-body">
            Async Python on Postgres for the medical record. LLMs only at the
            edges, behind a typed schema, with a keyword fallback if the model
            is mocked or down. No surprises in prod.
          </p>
        </div>

        <div className="mt-12 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-5">
          {layers.map((l) => (
            <div
              key={l.layer}
              className="rounded-2xl border border-black/5 bg-white p-6 shadow-card"
            >
              <div className="text-[11px] font-semibold uppercase tracking-widest text-brand-700">
                {l.layer}
              </div>
              <ul className="mt-4 space-y-2 text-[14px] text-body">
                {l.items.map((i) => (
                  <li key={i} className="flex items-center gap-2">
                    <span className="inline-block h-1.5 w-1.5 rounded-full bg-brand-500" />
                    {i}
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
