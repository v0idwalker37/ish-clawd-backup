FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cloud Run terminates TLS, so don't use HTTPS redirect middleware
ENV ENVIRONMENT=staging

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
