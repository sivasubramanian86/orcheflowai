# OrcheFlowAI — Technical Stack (2026)

This document details the polyglot architecture and enterprise-grade tools powering the OrcheFlowAI multi-agent orchestration platform.

## 1. Core Platform (Backend)
- **Language**: Python 3.12 (Selected for advanced type hinting and fast AI orchestration).
- **Framework**: **FastAPI** (High-performance, asynchronous REST API).
- **ORM**: **SQLAlchemy** (Async-mode) with Pydantic v2 for robust data validation.
- **Task Orchestration**: **Google ADK** (Agent Development Kit) for multi-agent swarm logic.
- **Security**: OAuth 2.0 (Google Identity Services) + JWT for stateless session management.

## 2. Intelligence & AI
- **Primary Model**: **Gemini 2.5 Flash** (Selected for ultra-low latency in real-time "Agent Swarm" logs).
- **Embedded Logic**: Vertex AI SDK for specialized prompt engineering and context caching.
- **Agent Mesh**: Custom MCP (Model Context Protocol) servers for tool-use (Calendar, Fit, Maps).

## 3. Storage & Data
- **Primary Database**: **Google AlloyDB for PostgreSQL** (Highly available, enterprise-grade vector storage).
- **Caching**: **Redis** (Memory Store) for agent session persistence and context window management.
- **Secret Management**: **Google Secret Manager** (Encryption of API keys and User Tokens).

## 4. User Experience (Frontend)
- **Language**: TypeScript + React 19 (Strict typing for high-reliability dashboards).
- **Design System**: Custom **Glassmorphic OKLCH Styling** (Premium "Mission Control" aesthetic).
- **Build Tool**: **Vite 6** (Optimized for fast HMR and lightweight production bundles).
- **Styling**: Vanilla CSS Modules (Maximum performance and zero dependency overhead).

## 5. DevOps & Infrastructure (GCP Native)
- **Deployment**: **Google Cloud Run** (Serverless container orchestration).
- **CI/CD**: **GitHub Actions** (Automated testing and Cloud Build triggers).
- **IaC**: **Terraform** (Declarative infrastructure for AlloyDB, Networking, and IAM).
- **Monitoring**: **Cloud Monitoring** + **Langfuse** (Agent trace observability).

---
> [!NOTE]
> All infrastructure is provisioned with **Least Privilege IAM Roles** to ensure data sovereignty and hackathon compliance.
