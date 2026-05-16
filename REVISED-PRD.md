---
tags: [meta, prd, revised, swarm]
version: 2.3
date: 2026-05-16
app_id: med
app_name: DClaw Med
category: Healthcare
status: P2
---

# 📘 DClaw Med — Revised PRD v2.3

> **The single document every agent must read before writing code for this app.**
> Generated from DClaw Master PRD v2.2. Read the Master PRD first: https://raw.githubusercontent.com/dclawstack/dclaw-prd/main/DClaw-Master-PRD.md

---

## 1. Product Identity

| Field | Value |
|-------|-------|
| **App ID** | `med` |
| **Name** | DClaw Med |
| **Category** | Healthcare |
| **Tagline** | Clinical intelligence |
| **Color** | #EF4444 |
| **Phase** | P2 |
| **Port (Frontend Dev)** | 3004 (Assigned) |
| **Port (Backend Dev)** | 8092 (Assigned) |
| **Maturity Tier** | 🟢 Tier 1 — Mature |

---

## 2. Current State Assessment

### 2.1 Scaffold Status
| Component | Status | Notes |
|-----------|--------|-------|
| `frontend/` | ✅ | Next.js 14+ app |
| `backend/` | ✅ | FastAPI + SQLAlchemy 2.0 |
| `docs/` | ✅ | getting-started, guides, reference, releases |
| `helm/` | ✅ | K8s deployment manifests |
| `.github/workflows/` | ✅ | CI/CD + Claude integration |
| `AGENTS.md` | ✅ | Per-repo agent instructions |
| `PLAN-v1.2.md` | ✅ | Feature roadmap |
| `docker-compose.yml` | ✅ | Local dev stack |
| `tests/` | ✅ | pytest + pytest-asyncio |
| `alembic/` | ✅ | Database migrations |
| `dclaw-manifest.json` | ✅ | DPanel registration |

### 2.2 Code Maturity
| Metric | Value |
|--------|-------|
| Python source files (backend) | ~88 |
| TypeScript/TSX files (frontend) | ~42 |
| Total source files | ~130 |
| Tests | ✅ Present |
| Alembic migrations | ✅ Present |
| DPanel manifest | ✅ Present |

### 2.3 Feature Maturity
- **P0 Foundation:** Partially implemented
- **P1 Platform:** Not yet started
- **P2 Vertical:** Not yet started

---

## 3. Gap Analysis

| # | Gap | Severity | Fix |
|---|-----|----------|-----|
| 1 | No critical gaps identified — focus on P1/P2 features | 🟢 | Continue building P1 features and add depth to existing code |

---

## 4. Sacred Architecture & Tech Stack

> **NON-NEGOTIABLE. Every DClaw product MUST use this exact stack.**

| Layer | Technology | Version |
|-------|------------|---------|
| **Frontend** | Next.js 14+ | App Router, Tailwind CSS, shadcn/ui |
| **Backend** | FastAPI | Pydantic v2, SQLAlchemy 2.0, asyncpg |
| **Database** | PostgreSQL 16 | CloudNativePG operator in K8s |
| **Vector DB** | Qdrant / pgvector | Only if RAG / semantic search |
| **Cache / Bus** | Redis | 7.x |
| **Object Storage** | MinIO | Latest |
| **Workflow** | Temporal.io | Only if automation/orchestration |
| **Auth** | Logto | JWT validation on all protected routes |
| **Billing** | Stripe | Metered or per-seat |
| **K8s Operator** | Go + controller-runtime | 0.18 |
| **LLM Local** | Ollama | Apple Silicon |
| **LLM Cloud** | OpenRouter + Kimi K2.5 | Fallback |
| **Monitoring** | Prometheus + Grafana | Latest |

### 4.1 Python Rules
- `ruff` formatting enforced
- Type hints on ALL public APIs
- `pydantic` v2 for schemas
- `sqlalchemy` 2.0 style (`Mapped`, `mapped_column`)
- `pytest` + `pytest-asyncio` for tests
- Functions < 50 lines
- No `print()` — use `structlog`

### 4.2 TypeScript / Next.js Rules
- Strict TypeScript (`strict: true`)
- Tailwind for ALL styling
- `cn()` utility for conditional classes
- No `any` without `// @ts-ignore`

### 4.3 Docker Standards
- Port mappings MUST match container listen port
- Healthchecks MUST use binaries present in base image
- `docker compose config` must pass before shipping
- Service type MUST be `ClusterIP`
- TLS required on all ingress

---

## 5. P0 Foundation Features (Must Have — Demo Ready)

> **Every P0 MUST include an AI Copilot per YC S25/W26 RFS.**

| # | Feature | Description | AI Component | Acceptance Criteria |
|---|---------|-------------|--------------|---------------------|
| P0.1 | **AI Clinical Copilot** | Assist clinicians with differential diagnosis, drug interactions, and note generation. | MedPaLM-style clinical LLM + retrieval-augmented guidelines | Generate differential with 5+ candidates; drug interaction check <2s |
| P0.2 | **Patient CRUD & MRN** | Complete patient records with medical record numbers, demographics, contacts. | AI data-quality validation + duplicate detection | CRUD with soft-delete; MRN auto-generation; dedup accuracy >95% |
| P0.3 | **Symptom Analyzer** | AI-powered symptom intake with differential diagnosis suggestions. | Symptom-to-ICD10 mapping + Bayesian inference | Capture 20+ symptoms; suggest 3-5 differentials |
| P0.4 | **Prescription Management** | Create, track, and manage prescriptions with dosage and frequency. | AI drug-interaction checker + allergy cross-check | Check 1000+ drug pairs; alert on contraindications |

---

## 6. P1 Platform Features (Should Have — v1.1–1.2)

| # | Feature | Description | AI Component | Acceptance Criteria |
|---|---------|-------------|--------------|---------------------|
| P1.1 | **Lab Results Integration** | Import and trend lab results with reference range alerting. | AI anomaly flagging + trend prediction | Support HL7 FHIR; auto-flag values outside reference range |
| P1.2 | **Appointment Scheduling** | Book, reschedule, and remind patients of appointments. | AI no-show prediction + optimal-slot recommendation | Calendar sync; SMS/email reminders; no-show prediction >80% |
| P1.3 | **Clinical Notes AI** | Auto-generate SOAP notes from encounter transcripts. | Whisper + clinical fine-tuned summarization | Generate SOAP note in <30s; clinician edit + approve |
| P1.4 | **HIPAA Audit Logging** | Every data access logged with immutable audit trails. | AI anomaly detection for unauthorized access | 100% access logged; tamper-proof storage; real-time alerts |

---

## 7. P2 Vertical / Scale Features (Could Have — v1.3+)

| # | Feature | Description | AI Component | Acceptance Criteria |
|---|---------|-------------|--------------|---------------------|
| P2.1 | **FHIR Integration** | Full HL7 FHIR R4 support for EHR interoperability. | AI FHIR mapping validation + data normalization | Support 20+ FHIR resources; bidirectional sync with Epic/Cerner |
| P2.2 | **Telemedicine** | Video consultations with screen sharing and e-prescription. | AI vitals estimation from camera (optional) | HD video; e-prescription to pharmacy; session notes auto-generated |
| P2.3 | **Patient Portal** | Self-service portal for patients to view records and message providers. | AI health literacy translator | View labs, appointments, messages; request refills |
| P2.4 | **Insurance Eligibility** | Real-time insurance verification and prior authorization tracking. | AI prior-auth document generation | Verify eligibility in <5s; track auth status with alerts |

---

## 8. Scaffold Checklist

Before marking this app "shipped", confirm:

- [ ] `frontend/` with Next.js 14+, Tailwind, shadcn/ui
- [ ] `backend/` with FastAPI, Pydantic v2, SQLAlchemy 2.0, asyncpg
- [ ] `docs/` with getting-started, guides, reference, releases, troubleshooting
- [ ] `helm/` with Chart.yaml, values.yaml, templates (deployment, service, ingress, cloudnativepg)
- [ ] `.github/workflows/` with build-backend.yml, build-frontend.yml, deploy.yml, claude.yml
- [ ] `frontend/public/dclaw-manifest.json` for DPanel registration
- [ ] `backend/tests/` with pytest + pytest-asyncio
- [ ] `backend/alembic/` with initial migration
- [ ] `Dockerfile` + `docker-compose.yml` with correct healthchecks
- [ ] Health endpoint at `/health` returning `{"status":"ok"}`
- [ ] `AGENTS.md` with per-repo instructions
- [ ] `PLAN-v1.2.md` with feature roadmap
- [ ] Port assigned from registry and documented
- [ ] No hardcoded secrets — use `.env.example` + K8s Secrets
- [ ] Non-root containers in Dockerfile

---

## 9. AI Copilot Mandate (YC S25/W26 Requirement)

Every DClaw app MUST have an AI Copilot as its first P0 feature. The copilot must:
1. Be contextually aware of the app's domain data
2. Use RAG over the app's knowledge base where applicable
3. Suggest next actions, not just answer questions
4. Be accessible from every page via floating chat or sidebar
5. Fall back to local Ollama when cloud is unavailable

---

## 10. Next Tasks for Vibe Coders

1. **Audit current state**: Verify all P0 features are complete and documented.
2. **Implement P1 features**: Build the 4 P1 features to reach v1.1 platform readiness.
3. **Add advanced features**: Begin P2 features for competitive differentiation.
4. **Optimize and scale**: Improve test coverage, add performance monitoring, and refine UX.

---

## 11. Domain Research Notes

Inspired by Epic, Cerner, Doxy.me, Nuance DAX. Healthcare AI is massive YC theme: clinician burnout + diagnostic accuracy.

---

## 12. Links & Resources

| Resource | URL |
|----------|-----|
| **Master PRD** | https://raw.githubusercontent.com/dclawstack/dclaw-prd/main/DClaw-Master-PRD.md |
| **GitHub Org** | https://github.com/dclawstack |
| **DPanel** | https://dpanel.dclawstack.io |
| **Port Registry** | See `dclaw-platform/PORT_REGISTRY.md` |
| **App PRD Template** | Obsidian Vault → `00-META/📐 App PRD Template.md` |
| **Scaffold Source** | `dclaw-scaffold/` in DClaw-Stack |

---

*Revised PRD version: 2.3*
*Generated: 2026-05-16 by DClaw Stack Generator*
*Next review: When P0 features are complete or architecture changes*
