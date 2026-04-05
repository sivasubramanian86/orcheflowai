# Contributing to OrcheFlowAI

Thank you for your interest in contributing to OrcheFlowAI.  
This document outlines the development workflow, code standards, and PR process.

---

## Development Setup

### Prerequisites

- Python 3.12+
- Docker Desktop (for local Postgres)
- Google Cloud SDK (`gcloud`) with active login
- Application Default Credentials: `gcloud auth application-default login`

### Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/sivasubramanian86/orcheflowai.git
cd orcheflowai

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
.venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r agents/requirements.txt
pip install -r api/requirements.txt
pip install -r requirements-dev.txt

# 4. Copy and configure environment
cp .env.example .env
# Edit .env with your local values

# 5. Start services
docker-compose up -d postgres
```

---

## Branch Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Production-ready code only |
| `feat/*` | New features (`feat/streaming-output`) |
| `fix/*` | Bug fixes (`fix/session-timeout`) |
| `docs/*` | Documentation updates |
| `chore/*` | Dependencies, CI, tooling |

**Never push directly to `main`.** Always open a Pull Request.

---

## Commit Message Format

We use **Conventional Commits**:

```
<type>(<scope>): <short description>

[optional body]

[optional footer: BREAKING CHANGE, closes #issue]
```

**Types:** `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `perf`, `ci`

**Example:**
```
feat(orchestrator): add streaming SSE output for workflow runs

Replaces synchronous JSON response with Server-Sent Events for real-time
agent progress feedback in the frontend dashboard.

Closes #15
```

---

## Code Standards

- Python 3.12+, type hints on all functions, PEP 257 docstrings
- `black` for formatting, `ruff` for linting — run before every commit
- No `# type: ignore`, no bare `except:`, no hardcoded secrets

```bash
# Format and lint
black .
ruff check . --fix
mypy agents/ api/ --strict
```

---

## Testing Requirements

Every PR must include:
1. **Unit tests** for any new business logic
2. **At least one integration test** for new API endpoints

```bash
# Run full test suite
pytest tests/ -v --cov=agents --cov=api --cov-report=term-missing

# Minimum bar: 70% coverage on new files
```

---

## Pull Request Process

1. Open a PR against `main` with a clear title and description
2. Fill in the PR template (auto-populated)
3. Ensure all CI checks pass (GitHub Actions: `test`, `lint`, `secret-scan`)
4. Request review from at least one maintainer
5. Squash-merge after approval

---

## Code of Conduct

Be professional, inclusive, and constructive in all interactions.  
This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).
