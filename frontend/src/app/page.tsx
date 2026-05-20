"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { APP_NAME, APP_TAGLINE, GITHUB_URL } from "@/lib/tokens";
import { useAuth } from "@/components/auth-provider";
import { DemoSection } from "@/components/landing/demo-section";
import {
  Activity,
  ArrowRight,
  ClipboardList,
  Database,
  FileText,
  Github,
  HeartPulse,
  ShieldCheck,
  Stethoscope,
  Users,
} from "lucide-react";

const FEATURES: { icon: typeof Activity; title: string; body: string }[] = [
  {
    icon: Stethoscope,
    title: "Evidence-cited differentials",
    body: "Real LLM via OpenRouter. Every diagnosis ships with ICD-10, confidence, grounded reasoning, and citations. Always ≥ 3 differentials.",
  },
  {
    icon: FileText,
    title: "AI clinical notes",
    body: "SOAP / admission / discharge / procedure templates authored by the model. Audit-logged for clean attribution.",
  },
  {
    icon: ShieldCheck,
    title: "Drug & allergy safety nets",
    body: "Every new prescription is cross-checked against patient allergies and the medication list — major / moderate severity with mechanism.",
  },
  {
    icon: HeartPulse,
    title: "AI triage assistant",
    body: "Free-text symptoms in; urgency band, suggested department, and recommended workup out. Patient-portal usable.",
  },
  {
    icon: Database,
    title: "FHIR R4 export",
    body: "Patient, Condition, MedicationRequest, Observation. SMART-on-FHIR launch on the v1.3 roadmap — drops into Epic / Cerner / Athena.",
  },
  {
    icon: ClipboardList,
    title: "HIPAA-aware audit trail",
    body: "Every read and write of a medical record is captured immutably with user, action, entity, old/new values, and timestamp.",
  },
];

export default function LandingPage() {
  const { user } = useAuth();
  const ctaHref = user ? (user.role === "patient" ? "/patient-portal" : "/dashboard") : "/login";
  const ctaLabel = user ? "Open dashboard" : "Launch app";

  return (
    <div className="min-h-screen flex flex-col">
      {/* nav */}
      <header className="sticky top-0 z-40 border-b bg-background/80 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
          <Link href="/" className="flex items-center gap-2 font-bold text-lg">
            <span className="inline-flex items-center justify-center w-8 h-8 rounded-lg bg-primary text-primary-foreground">
              <Activity className="w-4 h-4" />
            </span>
            {APP_NAME}
          </Link>
          <nav className="hidden items-center gap-7 text-sm text-muted-foreground md:flex">
            <a href="#features" className="hover:text-foreground">
              Features
            </a>
            <a href="#stack" className="hover:text-foreground">
              Stack
            </a>
            <Link href="/login" className="hover:text-foreground">
              Sign in
            </Link>
          </nav>
          <div className="flex items-center gap-2">
            <a
              href={GITHUB_URL}
              target="_blank"
              rel="noopener noreferrer"
              aria-label="View source on GitHub"
              className="inline-flex items-center justify-center h-9 w-9 rounded-md text-muted-foreground transition hover:bg-muted hover:text-foreground"
            >
              <Github className="w-4 h-4" />
            </a>
            <Link href={ctaHref}>
              <Button size="sm">
                {ctaLabel}
                <ArrowRight className="w-4 h-4 ml-1" />
              </Button>
            </Link>
          </div>
        </div>
      </header>

      <main>
        {/* hero */}
        <section className="relative overflow-hidden">
          <div
            aria-hidden
            className="pointer-events-none absolute inset-x-0 top-0 -z-10 h-[420px] bg-gradient-to-b from-primary/5 to-transparent"
          />
          <div className="mx-auto max-w-6xl px-4 pt-16 pb-20 sm:px-6 sm:pt-24 sm:pb-28">
            <div className="grid grid-cols-1 gap-12 lg:grid-cols-12 lg:gap-10">
              <div className="lg:col-span-7">
                <div className="text-xs font-semibold uppercase tracking-widest text-primary">
                  Open-source clinical intelligence
                </div>
                <h1 className="mt-4 text-4xl font-bold leading-[1.06] tracking-tight sm:text-5xl lg:text-6xl">
                  Clinical intelligence,{" "}
                  <span className="text-primary">not billing software.</span>
                </h1>
                <p className="mt-6 max-w-2xl text-lg leading-relaxed text-muted-foreground">
                  {APP_TAGLINE}. DClaw Med drops in next to your EHR via FHIR.
                  Real LLM-backed differentials with cited evidence, ambient
                  documentation, drug-interaction safety nets, and an audit
                  trail clinicians and compliance can both live with.
                </p>
                <div className="mt-8 flex flex-wrap items-center gap-3">
                  <Link href={ctaHref}>
                    <Button size="lg" className="rounded-full">
                      {ctaLabel}
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  </Link>
                  <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer">
                    <Button size="lg" variant="outline" className="rounded-full">
                      <Github className="w-4 h-4 mr-2" />
                      View on GitHub
                    </Button>
                  </a>
                  <a href="#features" className="text-sm font-medium text-muted-foreground underline-offset-4 hover:text-foreground hover:underline">
                    See features
                  </a>
                </div>
                <ul className="mt-9 grid grid-cols-1 gap-x-8 gap-y-2 text-sm text-muted-foreground sm:grid-cols-2">
                  <li>· HIPAA-aware immutable audit log</li>
                  <li>· FHIR R4 export</li>
                  <li>· LLM responses include evidence_refs</li>
                  <li>· Drop-in via Docker / Helm</li>
                </ul>
              </div>

              {/* mock terminal */}
              <div className="lg:col-span-5">
                <div className="rounded-2xl bg-foreground text-background p-1 shadow-lg">
                  <div className="rounded-[14px] bg-black/85 p-5">
                    <div className="flex items-center gap-1.5 pb-3">
                      <span className="h-2.5 w-2.5 rounded-full bg-red-400" />
                      <span className="h-2.5 w-2.5 rounded-full bg-amber-300" />
                      <span className="h-2.5 w-2.5 rounded-full bg-emerald-400" />
                      <span className="ml-2 font-mono text-[10.5px] text-white/40">
                        POST /api/v1/med/symptoms/analyze
                      </span>
                    </div>
                    <pre className="overflow-x-auto rounded-lg bg-black/50 p-3 font-mono text-[11.5px] leading-relaxed text-white/90 ring-1 ring-white/5">
{`{
  "differential_diagnoses": [
    { "condition": "Acute STEMI",
      "icd10_code": "I21.9",
      "confidence": 0.90,
      "evidence_refs": [{ ... }] },
    { "condition": "Unstable angina",   ... },
    { "condition": "Aortic dissection", ... }
  ],
  "recommended_tests": ["ECG", "Troponin", "CXR"],
  "urgency_level": `}<span className="text-red-300">{`"critical"`}</span>{`
}`}
                    </pre>
                    <div className="mt-3 flex items-center justify-between text-[10.5px]">
                      <span className="font-mono text-white/50">moonshotai/kimi-k2</span>
                      <span className="rounded-full bg-red-400/15 px-2.5 py-0.5 font-medium text-red-300">
                        URGENCY · critical
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* features */}
        <section id="features" className="bg-muted/40 py-20">
          <div className="mx-auto max-w-6xl px-4 sm:px-6">
            <div className="mx-auto max-w-2xl text-center">
              <div className="text-xs font-semibold uppercase tracking-widest text-primary">
                What ships today
              </div>
              <h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
                The clinician&rsquo;s side of the EHR, rebuilt.
              </h2>
              <p className="mt-4 text-base leading-relaxed text-muted-foreground">
                v1.2 is live, open source, and Docker / Helm deployable. v1.3
                adds ambient scribe, longitudinal RAG, and outcome telemetry.
              </p>
            </div>
            <div className="mt-12 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {FEATURES.map((f) => {
                const Icon = f.icon;
                return (
                  <Card key={f.title} className="transition hover:shadow-md">
                    <CardContent className="p-6">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                        <Icon className="w-5 h-5" />
                      </div>
                      <h3 className="mt-4 text-base font-semibold">{f.title}</h3>
                      <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                        {f.body}
                      </p>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>
        </section>

        {/* stack */}
        <section id="stack" className="py-20">
          <div className="mx-auto max-w-6xl px-4 sm:px-6">
            <div className="mx-auto max-w-2xl text-center">
              <div className="text-xs font-semibold uppercase tracking-widest text-primary">
                Built on
              </div>
              <h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
                Boring tech where it matters, sharp tech where it counts.
              </h2>
              <p className="mt-4 text-base leading-relaxed text-muted-foreground">
                Async Python on Postgres for the medical record. LLMs only at
                the edges, behind a typed schema, with a keyword fallback if
                the model is mocked or down.
              </p>
            </div>
            <div className="mt-10 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
              {[
                { title: "Frontend", items: ["Next.js 16", "TypeScript", "Tailwind", "shadcn/ui"] },
                { title: "Backend", items: ["FastAPI", "SQLAlchemy 2", "Pydantic v2", "Alembic"] },
                { title: "Data", items: ["Postgres 16", "SQLite (dev)", "Qdrant (RAG)", "Audit log"] },
                { title: "AI", items: ["OpenRouter", "Kimi K2", "Structured JSON", "Evidence-cited"] },
                { title: "Ops", items: ["Docker", "Helm / K8s", "Prometheus", "structlog"] },
              ].map((layer) => (
                <Card key={layer.title}>
                  <CardContent className="p-5">
                    <div className="text-[10.5px] font-semibold uppercase tracking-widest text-primary">
                      {layer.title}
                    </div>
                    <ul className="mt-3 space-y-1.5 text-sm text-muted-foreground">
                      {layer.items.map((i) => (
                        <li key={i} className="flex items-center gap-2">
                          <span className="inline-block h-1.5 w-1.5 rounded-full bg-primary" />
                          {i}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* demo (auto-hides if backend reports demo mode off) */}
        <DemoSection />

        {/* CTA */}
        <section className="bg-foreground py-20 text-background">
          <div className="mx-auto max-w-4xl px-4 text-center sm:px-6">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Ready to see it?
            </h2>
            <p className="mt-4 text-base text-background/70">
              Sign in with a clinician account to open the dashboard. Need an
              account? Ask your administrator to create one — or seed an admin
              with the bootstrap script in the repo.
            </p>
            <div className="mt-8 flex flex-wrap justify-center gap-3">
              <Link href={ctaHref}>
                <Button size="lg" variant="secondary" className="rounded-full">
                  {ctaLabel}
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </Link>
              <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer">
                <Button
                  size="lg"
                  variant="outline"
                  className="rounded-full border-background/30 bg-transparent text-background hover:bg-background/10"
                >
                  <Github className="w-4 h-4 mr-2" />
                  View source
                </Button>
              </a>
            </div>
          </div>
        </section>
      </main>

      {/* footer */}
      <footer className="border-t bg-background py-8 text-sm text-muted-foreground">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-4 sm:px-6">
          <div className="flex items-center gap-2 text-foreground">
            <Users className="w-4 h-4 text-primary" />
            <span className="font-semibold">{APP_NAME}</span>
            <span className="text-muted-foreground">· v1.2</span>
          </div>
          <div className="flex flex-wrap items-center gap-5">
            <Link href="/login" className="hover:text-foreground">
              Sign in
            </Link>
            <a href="#features" className="hover:text-foreground">
              Features
            </a>
            <a href="#stack" className="hover:text-foreground">
              Stack
            </a>
            <a
              href={GITHUB_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 hover:text-foreground"
            >
              <Github className="w-3.5 h-3.5" />
              GitHub
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
