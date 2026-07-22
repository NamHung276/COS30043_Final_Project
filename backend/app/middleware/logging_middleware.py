"""
middleware/logging_middleware.py — Starlette request/response logging middleware.

Logs every HTTP request with:
  - HTTP method
  - Request path + query string
  - Response status code
  - Duration in milliseconds
  - Client IP address

Example log output (development):
  09:15:32  [INFO    ]  app.middleware.logging_middleware — GET /api/games → 200 (142ms) from 127.0.0.1
"""

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

# Paths that should not be logged (health checks, static files etc.)
_SKIP_PATHS = frozenset({"/", "/docs", "/redoc", "/openapi.json", "/favicon.ico"})


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log each incoming HTTP request and its response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip noisy endpoints
        if request.url.path in _SKIP_PATHS:
            return await call_next(request)

        start = time.perf_counter()
        client_ip = self._get_client_ip(request)

        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.error(
                "%s %s → ERROR (%.0fms) from %s — %s",
                request.method,
                request.url.path,
                duration_ms,
                client_ip,
                str(exc),
            )
            raise

        duration_ms = (time.perf_counter() - start) * 1000
        level = logging.WARNING if response.status_code >= 400 else logging.INFO

        logger.log(
            level,
            "%s %s -> %d (%.0fms) from %s",
            request.method,
            request.url.path
            + (f"?{request.url.query}" if request.url.query else ""),
            response.status_code,
            duration_ms,
            client_ip,
        )

        # Attach server timing header for debugging
        response.headers["X-Response-Time"] = f"{duration_ms:.1f}ms"
        return response

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """Extract real client IP, respecting X-Forwarded-For if behind a proxy."""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"
