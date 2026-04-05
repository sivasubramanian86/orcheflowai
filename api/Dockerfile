# Stage 1: dependency builder
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: minimal runtime — no build tools
FROM python:3.12-slim
WORKDIR /app

# Non-root user (skill-07 non-negotiable)
RUN useradd --create-home --shell /bin/bash appuser
COPY --from=builder /root/.local /home/appuser/.local
COPY . .
RUN chown -R appuser:appuser /app
USER appuser

ENV PATH=/home/appuser/.local/bin:$PATH
ENV PORT=8080

EXPOSE 8080

# Vertex AI uses ADC — no API key env var needed
# Workload Identity / Service Account attached to Cloud Run handles auth
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
