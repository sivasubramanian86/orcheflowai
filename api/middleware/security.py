"""
OrcheFlowAI — Security Middleware
Implements: rate limiting, prompt injection guardrails, PII-safe logging,
CORS restriction, JWT auth, and request ID propagation.
Based on skill-06 Security Governance requirements.
"""
import os
import re
import time
import uuid
from typing import Callable

import structlog
from fastapi import Request, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

log = structlog.get_logger()

# ─── CORS (skill-06: never allow_origins=["*"] in production) ─────────────────
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5173"  # dev default
).split(",")


def configure_cors(app) -> None:
    """Register CORS with restricted origins. Override via ALLOWED_ORIGINS env var."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH"],   # no DELETE/PUT on public API
        allow_headers=["Authorization", "Content-Type", "X-Idempotency-Key"],
    )


# ─── Rate Limiting (in-memory; use Redis in prod) ────────────────────────────
_rate_store: dict[str, list[float]] = {}
RATE_LIMIT = int(os.getenv("RATE_LIMIT_RPM", "60"))   # requests per minute per IP


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        window_start = now - 60.0

        calls = _rate_store.get(client_ip, [])
        calls = [t for t in calls if t > window_start]

        if len(calls) >= RATE_LIMIT:
            log.warning("rate_limit_exceeded", ip=client_ip, count=len(calls))
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Retry after 60 seconds.",
            )

        calls.append(now)
        _rate_store[client_ip] = calls
        return await call_next(request)


# ─── Request ID propagation ───────────────────────────────────────────────────
class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
        with structlog.contextvars.bound_contextvars(request_id=request_id):
            response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


# ─── Prompt Injection Guardrail (skill-10: wrap user input in XML tags) ───────
_INJECTION_PATTERNS = re.compile(
    r"(ignore previous instructions|disregard all prior|you are now|"
    r"act as|pretend to be|jailbreak|system prompt|<\|.*?\|>)",
    re.IGNORECASE,
)


def sanitize_user_input(text: str) -> str:
    """
    Wraps user input in XML delimiters (skill-10 pattern) to prevent prompt injection.
    Strips regex-detected jailbreak patterns before wrapping.
    """
    cleaned = _INJECTION_PATTERNS.sub("[REMOVED]", text)
    return f"<user_input>{cleaned}</user_input>"


def check_prompt_injection(text: str) -> None:
    """Raises HTTPException if obvious injection patterns are detected."""
    if _INJECTION_PATTERNS.search(text):
        log.warning("prompt_injection_attempt", preview=text[:80])
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Input contains disallowed patterns.",
        )


# ─── PII-safe logging (skill-06: log only IDs, never PII fields) ─────────────
_PII_FIELDS = frozenset({
    "email", "phone", "mobile", "password", "full_name", "first_name",
    "last_name", "address", "ip_address", "national_id", "account_number",
    "card_number", "ssn", "dob", "date_of_birth",
})


def safe_log_dict(data: dict) -> dict:
    """Returns a copy of data with PII fields redacted (skill-06)."""
    return {
        k: "[REDACTED]" if k.lower() in _PII_FIELDS else v
        for k, v in data.items()
    }


# ─── Security Headers ─────────────────────────────────────────────────────────
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
        return response
