# DClaw Med — Agent Development Guide

> **Read this file first before making any code changes.**
> This document is the source of truth for architecture, anti-patterns, and development workflow.

## App Identity

**DClaw Med** is a clinical intelligence platform for healthcare providers. It manages patients, symptoms, diagnoses, prescriptions, clinical notes, and drug interactions with AI-assisted analysis.

- **Backend Port:** `8092` (FastAPI)
- **Frontend Port:** `3004` (Next.js)
- **Database:** `dclaw_med` (PostgreSQL)
- **Base API Path:** `/api/v1/med`

## Architecture Lock — DO NOT CHANGE

These are non-negotiable. If an agent suggests changing them, reject it.

### Backend
- **FastAPI** with `lifespan` handler for startup/shutdown
- **SQLAlchemy 2.0** — `DeclarativeBase` from `app.models.base`, NOT `declarative_base()`
- **Pydantic v2** schemas with `ConfigDict(from_attributes=True)`
- **Async SQLAlchemy** — `create_async_engine` + `AsyncSession`
- **Repository pattern** — all DB access goes through `app/repositories/`
- **Dependency injection** — use `Depends(get_db)`, never instantiate `AsyncSession` manually
- **NO MOCK DATA** — never use in-memory `dict`s for persistence

### Frontend
- **Next.js 14+ App Router**
- **Tailwind CSS** + **shadcn/ui** components in `src/components/ui/`
- **API client** in `src/lib/api.ts` — typed fetch wrapper
- **Environment variables** — `NEXT_PUBLIC_API_URL` baked at build time. Dockerfile MUST declare `ARG NEXT_PUBLIC_API_URL`.

### Docker
- **Backend:** `python:3.11-slim`, non-root `appuser`, healthcheck with `python urllib.request.urlopen()`
- **Frontend:** `node:20-alpine` builder + runner, port `3004`
- **Compose:** container port MUST match `EXPOSE`/`ENV PORT`

## Directory Structure

```
dclaw-med/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── main.py
│   │   │   └── v1/
│   │   │       └── med/
│   │   │           ├── __init__.py      # Router aggregator
│   │   │           ├── patients.py      # Patient CRUD
│   │   │           ├── symptoms.py      # Symptom CRUD + analyzer
│   │   │           ├── diagnoses.py     # Diagnosis CRUD
│   │   │           ├── prescriptions.py # Prescription CRUD
│   │   │           ├── notes.py         # Clinical note CRUD + generator
│   │   │           ├── drugs.py         # Drug interaction check
│   │   │           └── icd10.py         # ICD-10 lookup
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── database.py            # engine, get_db, init_db
│   │   ├── models/
│   │   │   ├── base.py                # Base(DeclarativeBase)
│   │   │   ├── patient.py
│   │   │   ├── symptom.py
│   │   │   ├── diagnosis.py
│   │   │   ├── prescription.py
│   │   │   └── clinical_note.py
│   │   ├── repositories/              # CRUD layer
│   │   ├── schemas/                   # Pydantic v2
│   │   └── services/
│   │       ├── symptom_analyzer.py
│   │       ├── note_generator.py
│   │       └── drug_service.py
│   ├── alembic/
│   ├── tests/
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/                       # Next.js App Router
│   │   │   ├── patients/
│   │   │   │   └── [id]/              # Patient detail
│   │   │   ├── diagnoses/
│   │   │   ├── prescriptions/
│   │   │   ├── symptoms/
│   │   │   ├── notes/
│   │   │   └── icd10/
│   │   ├── components/
│   │   │   ├── ui/                    # shadcn/ui
│   │   │   ├── navbar.tsx
│   │   │   └── sidebar.tsx
│   │   └── lib/
│   │       └── api.ts
│   └── Dockerfile
├── docker-compose.yml
├── helm/
└── .env.example
```

## Anti-Patterns — NEVER DO

| Anti-Pattern | Why It Breaks Things | Correct Alternative |
|--------------|---------------------|---------------------|
| `declarative_base()` in `database.py` | Separate metadata registry → zero tables | `from app.models.base import Base` |
| `curl` in healthcheck on `python:*-slim` | No `curl` in image → silent healthcheck failure | `python -c "import urllib.request; urllib.request.urlopen(...)"` |
| In-memory `MOCK_*` dicts | Data lost on restart, no relationships | Create `app/repositories/{entity}_repo.py` |
| Missing `ARG NEXT_PUBLIC_API_URL` | Wrong API URL baked into frontend | Add `ARG NEXT_PUBLIC_API_URL` before `npm run build` |
| Manual `get_db()` with `__anext__()` | Session leaks | `Depends(get_db)` in route signatures |
| Hardcoded `localhost:PORT` | Breaks Docker/K8s | Use `process.env.NEXT_PUBLIC_API_URL` |
| No alembic migration for new models | Schema drift, deployment failures | `alembic revision --autogenerate -m "msg"` |
| Missing `ondelete` on ForeignKey | Orphan records, constraint errors | Always specify `ondelete="CASCADE"` or `"SET NULL"` |

## Database Rules

1. All models MUST inherit from `Base` in `app.models.base`
2. All models MUST use `Mapped[...]` and `mapped_column()`
3. **Never use `default_factory=` in `mapped_column()`** — use `default=` instead
3. Relationships MUST specify `lazy="selectin"` for async safety
4. All new tables MUST get an alembic migration
5. `ondelete="CASCADE"` for child tables (symptoms, diagnoses, prescriptions, notes)
6. Add `index=True` on all foreign key columns and frequently queried columns

## How to Add a Feature

1. **Read this file** and `PLAN-v1.2.md`
2. **Backend:**
   - Add/update model in `app/models/`
   - Add/update schema in `app/schemas/`
   - Add repository in `app/repositories/`
   - Add/update router in `app/api/v1/med/`
   - Wire router in `app/api/v1/med/__init__.py`
   - Add tests in `tests/`
   - Generate alembic migration
3. **Frontend:**
   - Add API types/functions to `src/lib/api.ts`
   - Add page in `src/app/` or component
   - Use existing shadcn/ui components
4. **Docker:** Verify `docker compose config` and `docker compose up -d`
5. **Commit** with conventional commit message

## Testing Requirements

- Every new repository MUST have tests
- Every new router endpoint MUST be covered
- Use `pytest-asyncio` with `async` test functions
- Use `httpx.AsyncClient` with `ASGITransport`
- Override `get_db` dependency with test session

## Port Registry

| Service | Host Port | Container Port |
|---------|-----------|----------------|
| med-frontend | 3004 | 3004 |
| med-backend | 8092 | 8092 |
| med-postgres | 5432 | 5432 |
