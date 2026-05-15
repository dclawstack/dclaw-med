# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

# Build deps + WeasyPrint runtime libs (pango/cairo/gdk-pixbuf + base fonts)
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libcairo2 \
        libgdk-pixbuf-2.0-0 \
        shared-mime-info \
        fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Copy application first (hatchling needs source for editable install)
COPY . .
RUN pip install --no-cache-dir -e ".[dev]"

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8092

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8092/health')" || exit 1

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.api.main:app --host 0.0.0.0 --port 8092"]
