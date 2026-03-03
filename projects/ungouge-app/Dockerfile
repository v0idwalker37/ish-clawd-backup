# ==============================================================================
# UnGouge.ai Backend — Production Dockerfile
# ==============================================================================
# Multi-stage build: Python 3.11 slim, non-root user, health check
#
# Build:  docker build -t gougealert-api .
# Run:    docker run -p 8000:8000 --env-file .env.production gougealert-api
# ==============================================================================

# ── Stage 1: Dependencies ────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install system dependencies needed for building Python packages
# - gcc/musl-dev: compile C extensions (bcrypt, cryptography)
# - libmagic1: python-magic file type detection
# - libpq-dev: asyncpg PostgreSQL driver
# - poppler-utils: pdf2image (PDF rendering)
# - tesseract-ocr: pytesseract (OCR for scanned quotes)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libmagic1 \
    libpq-dev \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt requirements.txt
COPY backend/requirements-security.txt requirements-security.txt
RUN pip install --no-cache-dir --prefix=/install \
    -r requirements.txt \
    -r requirements-security.txt


# ── Stage 2: Runtime ─────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Install runtime-only system libraries (no compilers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    libpq5 \
    poppler-utils \
    tesseract-ocr \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Create non-root user
RUN groupadd -r gougealert && useradd -r -g gougealert -d /app -s /sbin/nologin gougealert

WORKDIR /app

# Copy application code
COPY backend/ .

# Set ownership
RUN chown -R gougealert:gougealert /app

# Switch to non-root user
USER gougealert

# Environment defaults (override at runtime)
ENV ENVIRONMENT=production \
    PORT=8000 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8000

# Health check — Cloud Run uses HTTP probes, but this helps local Docker
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with uvicorn
# - workers=1: Cloud Run handles scaling via instances, not workers
# - host=0.0.0.0: accept connections from outside container
# - port from $PORT (Cloud Run sets this)
# - proxy-headers: trust X-Forwarded-* from Cloud Run load balancer
# - forwarded-allow-ips=*: Cloud Run is trusted proxy
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --proxy-headers --forwarded-allow-ips='*' --access-log"]
