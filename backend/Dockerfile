# ==============================================================================
# SwasthyaGrid AI — Backend Cloud Run Production Dockerfile
# Multi-stage lean Python container with non-root security context
# ==============================================================================

FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Final minimal runtime image
FROM python:3.11-slim

WORKDIR /app

# Create non-root system user
RUN groupadd -r swasthya && useradd -r -g swasthya -d /app -s /sbin/nologin swasthya

COPY --from=builder /install /usr/local
COPY backend /app/backend
COPY data /app/data

# Ensure write permissions for SQLite DB and simulation logs
RUN mkdir -p /app/data/processed/simulated && \
    chown -R swasthya:swasthya /app

USER swasthya

ENV PYTHONUNBUFFERED=1 \
    PORT=8000 \
    ENVIRONMENT=production

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1

CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
