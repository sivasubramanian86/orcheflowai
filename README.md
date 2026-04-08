# OrcheFlowAI
**Eliminate the 'Cognitive Tax'. Let agents do the rest.**

OrcheFlowAI is a high-performance **Multi-Agent Intelligence Mesh** designed to eliminate the mental friction of modern tool-switching. Acting as your **Digital Twin**, it proactively orchestrates your fragmented workspace using **Vertex AI**, **Gemini 1.5 Flash**, and the **Model Context Protocol (MCP)**.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12+-green.svg)](https://python.org)
[![Google ADK](https://img.shields.io/badge/Google-ADK-orange.svg)](https://cloud.google.com/vertex-ai)
[![Cloud Run](https://img.shields.io/badge/Deploy-Cloud_Run-blue.svg)](https://cloud.google.com/run)
[![CI](https://github.com/sivasubramanian86/orcheflowai/actions/workflows/deploy.yml/badge.svg)](https://github.com/sivasubramanian86/orcheflowai/actions)

---

---

## 📺 Demo & Submission
*   **Demo Video:** [Watch on YouTube](https://youtu.be/ORCHEFLOW_DEMO_LINK)
*   **Architecture Overview:** [Deep Dive](./infra/ARCHITECTURE.md) | [Technical Stack](./infra/TECHSTACK.md)

```
API Service (FastAPI)
    └── Agent Service (ADK Orchestrator + 4 Sub-Agents)
            ├── Notes Agent     → MCP: notes_manager
            ├── Task Agent      → MCP: task_manager
            ├── Schedule Agent  → MCP: calendar_manager
            └── Workflow Agent  → compile + summarize
                    └── AlloyDB / Postgres (all state)
```

## Quick Start (Local Development)

### 1. Prerequisites
- **Python 3.11+**
- **Node.js 18+** (for frontend)
- **Google Cloud SDK** + **ADC** (run `gcloud auth application-default login`)
- **PostgreSQL** (optional, uses local mock if not found)

### 2. Setup
```powershell
# Clone the repository
git clone https://github.com/sivasubramanian86/orcheflowai.git
cd OrcheFlowAI

# Copy environment template
cp .env.example .env
# Edit .env: ensure GOOGLE_CLOUD_PROJECT=genai-apac-2026-491004 is set
```

### 3. Run (No Docker)
To start all services (API, Agents, MCP, and Vite Frontend) in separate terminal windows:
```powershell
.\scripts\run_local_dev.ps1
```
The script will auto-create a `.venv`, install dependencies, and start the dashboard at **http://localhost:3000**.

To stop all background services:
```powershell
.\scripts\run_local_dev.ps1 -Stop
```

### 4. Project Structure (Reorganized 2026)
- `api/`: FastAPI Backend & OAuth Routers
- `frontend/`: React 19 + Vite 6 Dashboard
- `agents/`: Google ADK Multi-Agent Orchestrator
- `mcp_server/`: Model Context Protocol tool connectors
- `infra/`: Terraform, Architecture blueprints & TECHSTACK
- `scripts/`: Production-grade runners and Deployment pipelines
- `tools/`: Binary proxies (AlloyDB Auth Proxy)
- `sample_data/`: Local development databases (SQLite)

---

## 🚀 Production Deployment (GCP)

We use **Terraform** for Infrastructure as Code and **Artifact Registry** for container hosting. Deployment is fully automated.

### Full Deployment Pipeline
```powershell
# Core deployment targeting asia-southeast1 (matches AlloyDB)
.\scripts\deploy_gcp.ps1
```
This script will:
1. Build and push Docker images for API, Agents, and MCP to **Artifact Registry** via Google Cloud Build.
2. Run `terraform apply` (or `gcloud run deploy` fallback) to provision/update **Cloud Run** services in `asia-southeast1`.
3. Output the production URLs.

> **Note on OAuth in Production:** Google Cloud Run terminates TLS at the edge. To satisfy strict `google-auth-oauthlib` HTTPS callbacks and avoid `OAuth 2 MUST utilize https` or 400 `redirect_uri` mismatch errors, the FastAPI production backend dynamically casts inbound proxy headers back to HTTPS.

---

## Technical Stack & Governance

### Frameworks & AI
- **Google ADK** — Multi-agent orchestration framework (Vertex AI native)
- **Vertex AI Gemini 1.5 Flash** — High-speed pipeline orchestration and low-latency reasoning
- **Vertex AI Gemini 1.0 Pro** — (Optional) Specialized long-context analysis
- **MCP (Model Context Protocol)** — Standardized tool/context interface between the mesh and your apps

### Infrastructure
- **Cloud Run** — Highly-scalable, serverless container execution
- **Artifact Registry** — Modern artifact management
- **Secret Manager** — Production-grade credential store (JWT secrets, DB URLs)
- **Terraform** — Deterministic infrastructure management

### Frontend (v2.0)
- **Vite 6 + React 19 + TypeScript** — High-performance modular dashboard
- **CS @layer + oklch()** — Modern, accessible design tokens
- **View Transitions API** — Smooth, app-like navigation
- **Real-time Agent Audit Log** — Live trace of ADK orchestration steps
