# Stage 1: dependency builder
FROM python:3.12-slim AS builder
WORKDIR /app
COPY api/requirements.txt requirements.txt
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: minimal runtime — no build tools
FROM python:3.12-slim
WORKDIR /app

# Non-root user (skill-07 non-negotiable)
RUN useradd --create-home --shell /bin/bash appuser
COPY --from=builder /root/.local /home/appuser/.local
COPY api/ api/
COPY db/ db/
RUN chown -R appuser:appuser /app
USER appuser

ENV PATH=/home/appuser/.local/bin:$PATH
ENV PORT=8080
ENV PYTHONPATH=/app

EXPOSE 8080

# Run using package-relative path
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
