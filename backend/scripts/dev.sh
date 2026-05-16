#!/usr/bin/env bash
# Local SQLite development bootstrap.
# Starts the backend against ./dev.db so no Postgres is required.
set -euo pipefail

cd "$(dirname "$0")/.."

export DATABASE_URL="${DATABASE_URL:-sqlite+aiosqlite:///./dev.db}"
export APP_ENV="${APP_ENV:-dev}"
export JWT_SECRET="${JWT_SECRET:-dev-jwt-secret-not-for-production}"

echo "→ DATABASE_URL=$DATABASE_URL"
echo "→ APP_ENV=$APP_ENV"
echo "→ Booting uvicorn on :8092 (schema auto-created on first request)"

exec uvicorn app.api.main:app --host 0.0.0.0 --port 8092 --reload
