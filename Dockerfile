# ==============================================================================
# SwasthyaGrid AI — Full-Stack Unified Cloud Run Dockerfile
# Stage 1: Build React 19 Frontend
# Stage 2: Install Python 3.11 Backend & Dependencies
# Stage 3: Minimal Secure Production Container
# ==============================================================================

# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Build Python dependencies
FROM python:3.11-slim AS backend-builder
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 3: Minimal Production Image
FROM python:3.11-slim
WORKDIR /app

RUN groupadd -r swasthya && useradd -r -g swasthya -d /app -s /sbin/nologin swasthya

COPY --from=backend-builder /install /usr/local
COPY backend /app/backend
COPY data /app/data
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

RUN mkdir -p /app/data/processed/simulated && \
    chown -R swasthya:swasthya /app

USER swasthya

ENV PYTHONUNBUFFERED=1 \
    PORT=8080 \
    ENVIRONMENT=production

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health')" || exit 1

CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
