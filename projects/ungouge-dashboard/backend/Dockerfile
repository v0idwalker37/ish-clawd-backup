# UnGouge Dashboard - Google Cloud Run Dockerfile
# Build: 2026-02-09-1439
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Cloud Run will provide $PORT)
ENV PORT=8080
EXPOSE 8080

# Start FastAPI with uvicorn
# Database will be initialized on first startup via FastAPI's startup event
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
