# Docker Optimization for Ungouge.ai

Production-ready Dockerfile patterns and optimization techniques.

## Optimized FastAPI Dockerfile

```dockerfile
# syntax=docker/dockerfile:1

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 appuser

# Copy installed packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Add local bin to PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run the application
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Key Optimizations

### Multi-Stage Builds
- **Builder stage**: Install build dependencies, compile packages
- **Runtime stage**: Copy only what's needed, no build tools
- **Result**: ~50% smaller image size

### Layer Caching
```dockerfile
# Good: Dependencies change less often than code
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# Bad: Rebuilds everything when code changes
COPY . .
RUN pip install -r requirements.txt
```

### .dockerignore
```
**/__pycache__
**/.pytest_cache
**/.mypy_cache
**/.coverage
**/node_modules
.git
.env
*.pyc
*.pyo
*.pyd
.Python
*.so
.venv
venv/
ENV/
```

### Security Best Practices

1. **Run as non-root user**
2. **Use official base images** (python:3.11-slim)
3. **Pin dependencies** (requirements.txt with exact versions)
4. **Scan for vulnerabilities** (trivy, snyk)
5. **Remove build dependencies** (multi-stage)
6. **Use HEALTHCHECK** for monitoring

### Image Size Comparison

```
python:3.11        : 1.02GB
python:3.11-slim   : 0.18GB
python:3.11-alpine : 0.06GB (but slower builds, compatibility issues)
```

**Recommendation**: Use `slim` for best balance of size and compatibility.

## Cloud Run Specific

### Environment Variables
Set via `--set-env-vars`, never hardcode:

```bash
--set-env-vars="DATABASE_URL=$DATABASE_URL,JWT_SECRET=$JWT_SECRET"
```

### Resource Limits
```bash
--memory=512Mi         # Sufficient for FastAPI
--cpu=1                # 1 vCPU
--min-instances=0      # Scale to zero when idle
--max-instances=10     # Prevent runaway costs
--timeout=60s          # Request timeout
--concurrency=80       # Requests per container
```

### Cold Start Optimization
- Keep image < 500MB
- Minimize dependencies
- Use `--min-instances=1` for production if needed

## Troubleshooting

**"Build fails with permission denied"**
- Check file permissions before COPY
- Use --chown with COPY

**"Image is too large"**
- Use multi-stage build
- Switch to slim base image
- Add .dockerignore

**"Container exits immediately"**
- Check CMD syntax
- Verify entry point exists
- Check logs: `docker logs <container-id>`
