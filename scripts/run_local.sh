#!/usr/bin/env bash
# =============================================================================
# OrcheFlowAI — Local Development Runner (macOS / Linux)
# Usage:
#   ./scripts/run_local.sh           # start all services
#   ./scripts/run_local.sh stop      # stop all services
#   ./scripts/run_local.sh reset     # wipe volumes and restart
#   ./scripts/run_local.sh logs      # tail all logs
#   ./scripts/run_local.sh logs api  # tail specific service
# =============================================================================

set -euo pipefail

PROJ_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE="docker compose -f $PROJ_DIR/docker-compose.yml"

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'; NC='\033[0m'
step() { echo -e "\n${CYAN}>> $*${NC}"; }
ok()   { echo -e "   ${GREEN}OK${NC}  $*"; }
warn() { echo -e "   ${YELLOW}WARN${NC} $*"; }
fail() { echo -e "   ${RED}FAIL${NC} $*"; }

# ── Handle subcommands ────────────────────────────────────────────
case "${1:-}" in
  stop)
    step "Stopping all services"
    $COMPOSE down
    ok "All services stopped"; exit 0 ;;
  reset)
    step "Resetting volumes and containers"
    $COMPOSE down -v --remove-orphans
    ok "Reset complete" ;;
  logs)
    $COMPOSE logs -f "${2:-}"; exit 0 ;;
esac

# ── 0. Pre-flight checks ──────────────────────────────────────────
step "Pre-flight checks"

if ! command -v docker &>/dev/null; then
  fail "Docker not found. Install: https://www.docker.com/products/docker-desktop"; exit 1
fi
ok "Docker found: $(docker --version | head -1)"

if ! command -v gcloud &>/dev/null; then
  warn "gcloud not found. Vertex AI features require ADC credentials."
else
  ADC_PATH="$HOME/.config/gcloud/application_default_credentials.json"
  if [[ -f "$ADC_PATH" ]]; then ok "Application Default Credentials found"
  else warn "ADC not configured. Run: gcloud auth application-default login"; fi
fi

# Create .env if missing
if [[ ! -f "$PROJ_DIR/.env" ]]; then
  step "Creating .env from .env.example"
  cp "$PROJ_DIR/.env.example" "$PROJ_DIR/.env"
  ok ".env created. Edit before running if needed."
else
  ok ".env exists"
fi

# ── 1. Start services ─────────────────────────────────────────────
step "Starting OrcheFlowAI services (docker compose up --build)"
$COMPOSE up -d --build

# ── 2. Wait for health ────────────────────────────────────────────
step "Waiting for API health (up to 60s)..."
MAX=60; WAITED=0; HEALTHY=false
while [[ $WAITED -lt $MAX ]]; do
  sleep 3; WAITED=$((WAITED+3))
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/v1/health 2>/dev/null || echo "000")
  if [[ "$STATUS" == "200" ]]; then HEALTHY=true; break; fi
  echo "   Waiting... (${WAITED}/${MAX}s)"
done

if [[ "$HEALTHY" == "true" ]]; then
  ok "API is healthy at http://localhost:8000"
else
  warn "API did not become healthy within ${MAX}s. Check: docker compose logs api"
fi

# ── 3. Summary ────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}========================================${NC}"
echo -e " OrcheFlowAI Local Environment Ready"
echo -e "${CYAN}========================================${NC}"
echo -e " Frontend:    ${YELLOW}open frontend/index.html${NC}"
echo -e " API:         ${GREEN}http://localhost:8000/v1/health${NC}"
echo -e " API Docs:    ${GREEN}http://localhost:8000/docs${NC}"
echo -e " MCP Server:  ${GREEN}http://localhost:8001${NC}"
echo -e " Agents:      ${GREEN}http://localhost:8002${NC}"
echo -e " Postgres:    ${GREEN}localhost:5432 (user: orcheflow)${NC}"
echo ""
echo -e " Stop:        ./scripts/run_local.sh stop"
echo -e " Logs:        ./scripts/run_local.sh logs [service]"
echo -e " Reset:       ./scripts/run_local.sh reset"
echo -e "${CYAN}========================================${NC}"
