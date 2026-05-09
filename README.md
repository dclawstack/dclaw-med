# DClaw Med

**Clinical intelligence at your fingertips**

Healthcare AI platform for symptom analysis, clinical note generation, ICD-10 lookup, and drug interaction checking.

[![Build Backend](https://github.com/dclawstack/dclaw-med/actions/workflows/build-backend.yml/badge.svg)](https://github.com/dclawstack/dclaw-med/actions/workflows/build-backend.yml)
[![Build Frontend](https://github.com/dclawstack/dclaw-med/actions/workflows/build-frontend.yml/badge.svg)](https://github.com/dclawstack/dclaw-med/actions/workflows/build-frontend.yml)

## Quick Start

```bash
# Clone the repository
git clone https://github.com/dclawstack/dclaw-med.git
cd dclaw-med

# Start all services
docker compose up -d

# Backend API: http://localhost:8092
# Frontend UI: http://localhost:3004
```

## Backend API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/med/symptoms/analyze` | Symptom analysis with differential diagnosis |
| GET | `/api/v1/med/symptoms` | List symptoms |
| POST | `/api/v1/med/notes/generate` | Generate clinical note |
| GET | `/api/v1/med/notes` | List clinical notes |
| POST | `/api/v1/med/icd10/lookup` | ICD-10 code search |
| POST | `/api/v1/med/drug/interactions` | Drug interaction checker |
| GET | `/api/v1/med/patients` | List patients |
| POST | `/api/v1/med/patients` | Create patient |
| GET | `/api/v1/med/patients/{id}` | Get patient |
| PUT | `/api/v1/med/patients/{id}` | Update patient |
| DELETE | `/api/v1/med/patients/{id}` | Delete patient |
| GET | `/api/v1/med/patients/{id}/history` | Patient history |

## Frontend Pages

| Route | Feature |
|-------|---------|
| `/` | Dashboard with stats and quick actions |
| `/symptoms` | Symptom analyzer with differential diagnoses |
| `/notes` | AI clinical note generator |
| `/patients` | Patient management (CRUD) |
| `/icd10` | ICD-10 code search |
| `/settings` | System configuration |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, SQLAlchemy 2.0, Pydantic v2, asyncpg |
| Frontend | Next.js 16, TypeScript, Tailwind CSS, shadcn/ui |
| Database | PostgreSQL 16 (CloudNativePG in K8s) |
| Vector Store | Qdrant |
| LLM Gateway | OpenRouter + Kimi K2.5 |

## Ports

| Service | Port |
|---------|------|
| Backend API | 8092 |
| Frontend Dev | 3004 |
| PostgreSQL | 5432 |

## Deployment

### Docker Compose
```bash
docker compose up -d
```

### Kubernetes (Helm)
```bash
helm upgrade --install dclaw-med ./helm/dclaw-med   --namespace dclaw --create-namespace
```

## Code Manager

Allen Antony ([@allenantony007](https://github.com/allenantony007))

## DClaw Stack

Part of the [DClaw Stack](https://github.com/dclawstack) — an AI-native application platform with 65+ products.
