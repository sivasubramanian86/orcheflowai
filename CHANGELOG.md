# Changelog

All notable changes to OrcheFlowAI are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2026-04-05

### Added
- **Multi-agent orchestration** via Google ADK (Orchestrator + 4 sub-agents)
- **Vertex AI integration** — all LLM calls via ADC (no API key required)
  - Orchestrator: `vertex-ai:gemini-2.5-flash`
  - Sub-agents: `vertex-ai:gemini-2.0-flash`
- **FastAPI REST API** with JWT authentication and rate limiting (60 RPM)
- **MCP tool layer** — Notes Manager, Task Manager, Calendar Manager
- **AlloyDB / Postgres** operational state with pgvector extension
- **Prompt injection guardrails** — XML input wrapping in all system prompts
- **Structured audit trail** — every agent action logged to `agent_audit_log`
- **CORS lockdown** — explicit origin whitelist (no wildcard `*` in production)
- **Agent pipeline visualizer** — real-time pipeline status in frontend dashboard
- **Docker Compose** — local 3-tier orchestration (API + Agents + MCP + Postgres)
- **Terraform IaC** — Cloud Run deployment with Workload Identity Federation
- **GitHub Actions CI/CD** — automated test, lint, secret-scan, and deploy pipeline
- **Responsible AI** — RAI risk classification (Medium), fairness/bias audit patterns
- **Cost efficiency** — context caching strategy, session management, fallback chains

### Infrastructure
- Cloud Run deployment: `us-central1` region
- Secret Manager for all runtime secrets
- Cloud Logging with structured JSON output
- pgvector `HNSW` index for semantic search

### Documentation
- `README.md` — quick start, architecture, tech stack, deployment
- `SECURITY.md` — vulnerability disclosure, security architecture
- `CONTRIBUTING.md` — dev setup, branch strategy, PR process
- `CHANGELOG.md` — this file
- `demo/DEMO_SCRIPT.md` — 4-minute YouTube demo script

---

## [Unreleased]

### Planned
- WebSocket streaming output for real-time agent responses
- Redis session cache for production-scale session management
- Langfuse tracing integration for LLM observability
- HITL (Human-in-the-Loop) approval gate for high-confidence actions
