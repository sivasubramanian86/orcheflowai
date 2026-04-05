# Stage 0: Node Builder (Frontend Dashboard)
FROM node:20-slim AS frontend-builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 1: Dependency Builder (Python)
FROM python:3.12-slim AS builder
WORKDIR /app
COPY api/requirements.txt requirements.txt
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Final minimal runtime
FROM python:3.12-slim
WORKDIR /app

# Non-root user
RUN useradd --create-home --shell /bin/bash appuser
COPY --from=builder /root/.local /home/appuser/.local
COPY --from=frontend-builder /app/dist /app/static

COPY api/ api/
COPY db/ db/

RUN chown -R appuser:appuser /app
USER appuser

ENV PATH=/home/appuser/.local/bin:$PATH
ENV PORT=8080
ENV PYTHONPATH=/app

EXPOSE 8080

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
