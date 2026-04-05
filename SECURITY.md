# Security Policy — OrcheFlowAI

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | Yes       |
| < 1.0   | No        |

---

## Reporting a Vulnerability

**Please do NOT report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability, please report it via one of the following:

1. **GitHub Private Vulnerability Reporting** (preferred):  
   Navigate to `Security` → `Report a vulnerability` on the repository page.

2. **Email:** Contact the maintainer directly (see GitHub profile).

Please include:
- A description of the vulnerability and its potential impact
- Steps to reproduce the issue
- Any proof-of-concept code (if applicable)

You will receive acknowledgement within **48 hours** and a detailed response within **5 business days**.

---

## Security Architecture

OrcheFlowAI is designed with security-first principles:

### Credential Management
- **No API keys in source code** — all secrets managed via Google Secret Manager
- **Application Default Credentials (ADC)** used for all Vertex AI interactions
- **Workload Identity Federation** for Cloud Run service-to-service authentication
- `.env` files are for local development only and are explicitly `.gitignore`d

### API Security
- Rate limiting: 60 requests per minute per IP (configurable)
- JWT-based authentication on all external endpoints
- CORS locked to explicit allowed origins (no wildcard `*` in production)
- All user inputs sanitized and wrapped in XML prompt guards to prevent injection

### Responsible AI
- All LLM outputs are structured (Pydantic-validated JSON)
- Confidence scores logged for every workflow run
- PII is never logged in structured logs — user IDs and truncated inputs only
- Agent audit trail stored for all workflow actions

### Network Security
- Only the API service (port 8000) is publicly accessible
- Agent Service and MCP Server are internal-only (no `allUsers` IAM binding)
- Service-to-service communication uses `Authorization: Bearer <gcloud_id_token>`

---

## Dependency Security

Dependencies are pinned in `requirements.txt` / `pyproject.toml`.  
Run the following to check for known vulnerabilities before each release:

```bash
pip install pip-audit
pip-audit -r requirements.txt
```

Or with Google Cloud:
```bash
gcloud artifacts packages list-vulnerabilities --location=us-central1
```

---

## Disclosure Policy

We follow a **coordinated disclosure** model:
- Vulnerabilities are fixed before public disclosure
- Credit is given to reporters who responsibly disclose issues
- We aim to patch critical vulnerabilities within **72 hours** of confirmed report
