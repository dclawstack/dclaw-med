# DClaw Med — Plan v1.3 (YC-Grade Strategy & Roadmap)

> **Date:** 2026-05-16
> **Author:** Allen Antony (with autonomous agent)
> **Prior versions:** `PLAN-v1.2.md`, `AGENTS.md` (architecture lock — still binding)
> **Source of truth for v1.3 implementation.** Update checkmarks as items ship.

---

## 1. Pitch Frame — Why This, Why Now

**Problem (hair on fire).** US physicians spend ~2 hours on documentation and inbox work for every 1 hour of direct patient care. Burnout is the #1 reason clinicians leave medicine. Existing EHRs (Epic, Cerner) are billing systems retrofitted as clinical tools; their "AI" add-ons are bolt-ons sold per-seat and gated behind multi-quarter sales cycles.

**Wedge.** DClaw Med is a **clinician-first, LLM-native** clinical intelligence layer that drops in next to an existing EHR via FHIR (no rip-and-replace), and gives back hours per day through ambient documentation, evidence-cited differentials, and longitudinal RAG over the patient's own chart.

**Why now.**
1. FHIR R4 is now a federal mandate (21st Century Cures Act enforcement → all major EHRs expose patient data via SMART-on-FHIR).
2. LLMs (Kimi K2.5, Claude 4, GPT-5) crossed the safety/quality bar for structured clinical reasoning when constrained by schemas and grounded with RAG.
3. Whisper-class transcription is now cheap enough (~$0.006/min) to run on every encounter.
4. CMS now reimburses ambient AI scribing under specific G-codes.

**Moat.**
- Longitudinal patient RAG with cited evidence (not "AI hallucination roulette").
- Outcome telemetry: prove minutes-per-encounter saved, per-clinician, per-department.
- Trust surface: every AI suggestion shows its source documents, confidence, and reversal path.

---

## 2. v1.2 State of the Code (audit summary)

| Area | What exists | Honest assessment |
|---|---|---|
| Patient/symptom/diagnosis/prescription/note CRUD | ✅ Real, async SQLAlchemy + Postgres | Solid foundation |
| Auth + RBAC | ✅ JWT (HS256), users, roles | `jwt_secret="change-me-in-prod"` default — must fix |
| Audit log | ✅ Append-only table | Not cryptographically chained — HIPAA-acceptable, not tamper-evident |
| FHIR R4 export | ✅ Patient/Condition/MedicationRequest/Observation | Export only; no import, no SMART-on-FHIR |
| Drug interactions | ⚠️ 5 hardcoded pairs | Demo-grade, not clinically usable |
| ICD-10 lookup | ⚠️ ~35 hardcoded codes | Real CMS list is ~73,000 codes |
| Symptom analyzer (AI) | ❌ Mock — 5 keyword patterns | **The biggest gap.** `openrouter_api_key` is wired but never called. |
| Clinical note generator (AI) | ❌ Static templates | Same — pretends to be AI |
| AI triage assistant | ❌ Same mock pattern matcher | Same |
| Vector store / RAG | ❌ README mentions Qdrant; no code | Not started |
| Ambient scribe | ❌ | Not started |
| Observability | ⚠️ structlog only | No /metrics, no traces, no request IDs |
| Streaming | ❌ | No SSE/WS — required for LLM UX |
| Mobile / PWA | ❌ | Desktop-only |
| Multi-tenancy | ❌ | Single-tenant; no `Organization` scoping |

**Knowledge graph note.** `graphify-out/` (built from commit `bb6f8b0`) is the current project knowledge graph — use it for navigation. The `.obsidian/` folder is an *empty* vault (configs only, no notes). v1.3 will keep `graphify-out` as the canonical map and skip Obsidian until there's real prose to vault.

---

## 3. YC Gap Analysis

Mapped against a typical YC rubric:

| Dimension | v1.2 grade | What YC wants | v1.3 target |
|---|---|---|---|
| **Hair-on-fire problem** | C | Clinician burnout w/ a number attached | A — quantified time-saved per encounter, dashboard visible to admins |
| **Wedge / why-now** | B | One narrow user, one painful task | A — *"ambient scribe + cited differential, for outpatient PCPs"* |
| **Technical moat** | D | Hard to copy in a weekend | A — longitudinal RAG + evidence citations + outcome telemetry |
| **AI sophistication** | F (mock) | Real models, grounded, streamed | A — OpenRouter+Kimi K2.5 calls behind a `LLMService`, structured JSON output, evidence-cited |
| **Interoperability** | C (FHIR export only) | SMART-on-FHIR app launchable from Epic | B+ — FHIR import + SMART launch endpoints |
| **Compliance / trust** | C | HIPAA-credible, immutable audit, signed deploys | A — hash-chained audit, secret rotation docs, BAA-ready |
| **Scalability** | C | Multi-tenant, observable, async | B+ — `Organization` scoping, OpenTelemetry, rate limits |
| **Founder velocity proof** | C | Ship every week | A — CI matrix, dev SQLite mode, seed CLI, < 5-min onboarding |

**Biggest single fix:** stop pretending to be AI. Wire the LLM. Every YC reviewer will ask "what model is this?" and "can I see it stream?".

---

## 4. v1.3 Roadmap — Prioritized, Complexity-Tagged

Complexity scale per the user's brief:
- **0** = Low / foundational. Quick wins, removes embarrassment, unblocks higher-tier work.
- **1** = Medium / core differentiator. Demonstrable moat.
- **2** = High / advanced. AI integration, complex workflows, multi-system.

Order within each tier = recommended ship order.

### Complexity 0 — Foundational (quick wins, ~1–3 days each)

- [ ] **0.1 LLMService scaffold (no behavior change)** — single `app/services/llm.py` async client over OpenRouter with timeout, retry, structured-JSON helper, and a `MOCK_LLM=true` test mode. No prompts yet — just the surface area so 1.x can plug in.
- [ ] **0.2 Local SQLite dev mode** — `database_url` autodetects `sqlite+aiosqlite:///./dev.db`; `dev-up` script seeds 10 patients and runs the API on 8092 without Docker. Slashes onboarding from "install Postgres" to `make dev`.
- [ ] **0.3 Seed CLI** — `python -m app.scripts.seed --realistic` produces 50 patients with longitudinal symptoms/diagnoses/labs/notes for demos.
- [ ] **0.4 Replace JWT default secret** — refuse to boot in `app_env != "dev"` if `jwt_secret == "change-me-in-prod"`; document rotation in `docs/security.md`.
- [ ] **0.5 Rate limiting** — `slowapi` middleware: 60 req/min for unauthenticated, 600 req/min for auth, 6 req/min for `/symptoms/analyze` and `/notes/generate`. Per-IP and per-user.
- [ ] **0.6 Request IDs + structured logs** — `X-Request-ID` middleware; structlog binds it to every log line. Lays the groundwork for tracing.
- [ ] **0.7 Prometheus `/metrics`** — `prometheus-fastapi-instrumentator`; HTTP latency, DB pool, custom counters for `ai_calls_total`, `ai_tokens_total`.
- [ ] **0.8 DB-ping healthcheck** — `/health` now executes `SELECT 1`; Docker healthcheck stays the same.
- [ ] **0.9 Full ICD-10-CM dataset loader** — script that downloads CMS public file (or ships the YAML in repo) and seeds `icd10_codes` table; `/icd10/lookup` switches from in-memory list to DB-backed `trgm` search.
- [ ] **0.10 RxNorm-normalized prescriptions** — `medication_rxcui` column + nightly job to resolve free-text drug names against the RxNorm REST API; falls back to text if no match. Required for any future e-prescribe story.
- [ ] **0.11 Frontend error boundary + skeletons audit** — every page wrapped in `<ErrorBoundary>`, every list has a skeleton. Prevents the "white screen of death" demo failure.
- [ ] **0.12 Accessibility pass** — keyboard nav, `aria-*` on all interactive shadcn components, color-contrast check on `colors_and_type.css`. YC partners notice.
- [ ] **0.13 GitHub Actions CI matrix** — backend `pytest` + ruff + mypy; frontend `next build` + `tsc --noEmit`; block merge on red. (Today: only build workflows exist.)
- [ ] **0.14 OpenAPI tags + examples** — every endpoint gets a `description=` and a request example so `/docs` is demo-ready.
- [ ] **0.15 Pitch-ready README + 2-min Loom script outline** — landing section: problem stat, demo GIF, "drop into your EHR via SMART" hook.

### Complexity 1 — Core differentiators (1–2 weeks each)

- [ ] **1.1 Real LLM-backed symptom analyzer** — replace `SYMPTOM_PATTERNS` with `LLMService.json_completion(prompt, schema=DifferentialDiagnosis[])`. Includes:
  - System prompt with safety guardrails ("never give a single diagnosis, always differential of ≥3").
  - Structured output: condition, ICD-10 code, confidence, reasoning, evidence_refs[].
  - Fallback to keyword matcher if `MOCK_LLM` or upstream timeout.
- [ ] **1.2 Server-sent events for AI endpoints** — `/symptoms/analyze` and `/notes/generate` stream tokens. Frontend uses `EventSource` and renders progressively.
- [ ] **1.3 Real LLM-backed SOAP note generator** — same approach: prompt + schema + streaming. Inputs: patient summary, symptoms, vitals. Outputs: SOAP sections, ICD-10 suggestions, billable CPT codes.
- [ ] **1.4 Evidence citations** — every AI suggestion includes `evidence_refs: [{source: "UpToDate"|"PubMed"|"patient-record", excerpt, url?}]`. UI shows source-on-hover. Phase 1 uses a curated YAML of ~200 clinical references; phase 2 (in 2.x) swaps to RAG.
- [ ] **1.5 Organization (multi-tenant) scoping** — add `Organization` model; every patient/audit/appointment row gets `organization_id`; queries filter by `current_user.organization_id`. Migration plan: backfill default org, then enforce non-null.
- [ ] **1.6 Hash-chained audit log** — `audit_log.prev_hash` + `entry_hash = sha256(prev_hash||row_json)`. Daily anchor written to a separate `audit_anchors` table; verifier CLI. Demonstrably tamper-evident → BAA conversation easier.
- [ ] **1.7 FHIR import + SMART-on-FHIR launch** — `/fhir/$import` (NDJSON bulk); `/smart/launch` and `/smart/callback` endpoints; register as a SMART app. Test against the public SMART sandbox.
- [ ] **1.8 OpenTelemetry traces** — auto-instrument FastAPI + SQLAlchemy + httpx; OTLP exporter to a local Tempo/Jaeger in `docker-compose.yml`.
- [ ] **1.9 Clinician outcome telemetry** — per-encounter timer: clinician opens patient → closes patient; minutes-saved estimate vs. baseline; weekly digest email to admins. The metric that closes YC.
- [ ] **1.10 Prompt library + versioning** — `app/prompts/*.yaml` with semver; `LLMService` records `prompt_version` on every call so we can A/B and revert.
- [ ] **1.11 Drug-interaction upgrade to RxNorm/DDInter** — fetch the open DDInter dataset on first boot; `(rxcui_a, rxcui_b) -> severity` table; alerts move from 5 pairs to ~150k pairs.
- [ ] **1.12 Per-tenant API keys + scoped tokens** — for the SMART app, integrations, and webhooks. Stored argon2-hashed.
- [ ] **1.13 Mobile-friendly PWA shell** — Next.js `manifest.json`, install banner, responsive patient detail and triage widget. iPad-first.
- [ ] **1.14 Backend feature flags** — env-driven (`FEATURE_AMBIENT=on`); centralized in `app/core/features.py`. Lets us demo 2.x features to specific orgs without forking.

### Complexity 2 — Advanced (multi-week, high leverage)

- [ ] **2.1 Ambient scribe (encounter recording → structured SOAP)**
  - Browser mic → WebRTC chunked upload → Whisper (large-v3 via OpenRouter or self-hosted).
  - Diarization (clinician vs. patient).
  - LLM extracts: chief complaint, HPI, ROS, exam, A/P; emits a draft `ClinicalNote` for clinician to review and sign.
  - Stores raw audio encrypted at rest (org-key envelope encryption); retention policy configurable.
- [ ] **2.2 Longitudinal patient RAG (Qdrant)** — embed every clinical note, lab, prescription on write; `/patients/{id}/ask` answers free-text questions with citations to specific notes. The "moat" feature.
- [ ] **2.3 Bayesian differential with visible reasoning** — sequential prior→posterior updates as the clinician adds findings; UI shows the probability bars shift live. Implemented as a constrained tool-use loop over the LLM.
- [ ] **2.4 Pre-visit auto-summarizer (agent)** — overnight job: for tomorrow's appointments, generate a one-page brief (recent labs out of range, med changes, missed follow-ups, open referrals). Cited.
- [ ] **2.5 Early-warning risk scores** — sepsis (qSOFA + labs delta), 30-day readmission, deterioration index. Trained on synthetic + public MIMIC-IV data; serve via `/risk/{patient_id}`.
- [ ] **2.6 HL7 v2 → FHIR bridge** — for hospitals that can't do FHIR yet; Mirth-style listener that ingests ADT/ORU and projects into the same models.
- [ ] **2.7 Multi-modal: derm/wound image triage** — patient/clinician uploads image; vision model returns differential with confidence; appended to encounter as a "computer-aided" note (never autonomous).
- [ ] **2.8 Voice command UI** — "show me Maria's last A1c trend" → renders the chart. Whisper for ASR, structured intent extractor, query dispatcher.
- [ ] **2.9 Clinical pathway recommender** — given diagnosis + comorbidities, suggest next workup/treatment per UpToDate-style pathway YAML; user confirms each step (no autonomous orders).
- [ ] **2.10 Federated/on-prem deployment kit** — Helm chart variant that runs against Bedrock/Azure OpenAI/local Llama, no outbound traffic; lets us sell to hospitals with strict egress.

---

## 5. Implementation Order (concrete sequence)

The next agent session should ship these in this order (recompute after each milestone):

1. **0.1 LLMService scaffold** — needed by 1.1/1.3.
2. **0.2 SQLite dev mode** — unblocks fast iteration without Docker.
3. **0.3 Seed CLI** — demo data for every other feature.
4. **0.4 JWT secret hardening** + **0.5 rate limiting** — closes the two most embarrassing gaps.
5. **0.6 Request IDs / 0.7 Prometheus / 0.8 DB ping healthcheck** — observability baseline.
6. **0.9 ICD-10 full dataset** + **0.10 RxNorm** — makes the clinical surface real.
7. **0.11–0.15** — UX polish, CI, pitch artifacts.
8. **1.1 LLM symptom analyzer** + **1.2 streaming** + **1.4 citations** — the AI no longer fakes it.
9. **1.3 LLM SOAP notes**.
10. **1.5 multi-tenancy** + **1.6 hash-chained audit** — enterprise trust surface.
11. **1.7 SMART-on-FHIR** + **1.11 DDInter** + **1.9 outcome telemetry** — the YC closing slides.
12. **1.8/1.10/1.12/1.13/1.14** — supporting infrastructure.
13. **2.1 ambient scribe** + **2.2 longitudinal RAG** — the moat. By the time we get here, the demo writes itself.
14. **2.3–2.10** — staged by which YC interview question they answer.

---

## 6. Non-Negotiables Carried Forward from `AGENTS.md`

- No mock dicts as persistence.
- All models inherit from `Base` in `app.models.base`, use `Mapped[...]` and `mapped_column()`.
- Repository pattern for DB access; `Depends(get_db)` only.
- Alembic migration for every new table or column.
- Pydantic v2 with `ConfigDict(from_attributes=True)`.
- Frontend: shadcn/ui only, `NEXT_PUBLIC_API_URL` baked at build time.
- Docker: `python urllib.request.urlopen()` for healthchecks; `ARG NEXT_PUBLIC_API_URL` before `npm run build`.
- Ports unchanged: backend 8092, frontend 3004, postgres 5432.

---

## 7. Definition of Done (per ticket)

A complexity-N item is "done" when:
- Migration exists (if schema changed) and applies cleanly on a fresh DB.
- Backend tests cover happy path + one failure mode (pytest-asyncio + `httpx.AsyncClient`).
- Frontend renders without console errors and has a skeleton/empty/error state.
- `docker compose up -d` boots green; `/health` and `/metrics` return 200.
- `PLAN-v1.2.md` and this file get the checkbox flipped in the same commit.
- Conventional commit message; PR auto-linked to the ticket ID (e.g. `feat(llm): real symptom analyzer (1.1)`).

---

## 8. Open Questions Parked for the Founder

- Which OpenRouter model is the v1.3 default — Kimi K2.5 (current config) or upgrade to Claude Sonnet 4.6 for clinical reasoning? (Cost vs. quality data TBD.)
- BAA path: OpenRouter doesn't sign BAAs. For HIPAA-credible deployments do we (a) route to Azure OpenAI with BAA, (b) self-host Llama 3.3-70B, or (c) both behind feature flag 1.14? Default plan: (c).
- Pilot design partners: target 3 outpatient PCP clinics for the ambient scribe alpha. Owner: founder.
- Pricing: per-encounter ($X/visit), per-seat ($Y/clinician/month), or value-share (% of clinician time saved)? Recommendation: per-seat for early pilots, per-encounter at scale.

---

_End of plan_v1.3.md — proceed to Phase 3 only after this file is committed._
