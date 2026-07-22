"""
middleware/rate_limit.py — Simple in-memory IP-based rate limiter.

Limits each client IP to RATE_LIMIT_PER_MINUTE requests per 60-second window.
Returns HTTP 429 Too Many Requests when the limit is exceeded.

Implementation notes:
  - Uses a sliding-window counter stored in memory (dict of IP → request timestamps)
  - Thread-safe with threading.Lock
  - Resets on server restart (acceptable for dev; swap to Redis for prod)
  - Excludes /docs, /redoc, /openapi.json from limiting
"""

import logging
import threading
import time
from collections import defaultdict, deque
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from config import settings

logger = logging.getLogger(__name__)

_EXEMPT_PATHS = frozenset({"/", "/docs", "/redoc", "/openapi.json", "/favicon.ico"})
_WINDOW_SECONDS = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding-window rate limiter — max N requests per minute per client IP."""

    def __init__(self, app, limit: Optional[int] = None) -> None:
        super().__init__(app)
        self._limit = limit or settings.rate_limit_per_minute
        # Map of IP → deque of request timestamps (monotonic)
        self._requests: dict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()

    async def dispatch(self, request: Request, call_next) -> Response:
        # Exempt documentation paths
        if request.url.path in _EXEMPT_PATHS:
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        now = time.monotonic()

        with self._lock:
            window = self._requests[client_ip]

            # Remove timestamps older than the window
            while window and now - window[0] > _WINDOW_SECONDS:
                window.popleft()

            if len(window) >= self._limit:
                retry_after = int(_WINDOW_SECONDS - (now - window[0])) + 1
                logger.warning(
                    "Rate limit exceeded for %s on %s", client_ip, request.url.path
                )
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "detail": f"Maximum {self._limit} requests per minute. Retry in {retry_after}s.",
                        "retry_after_seconds": retry_after,
                    },
                    headers={"Retry-After": str(retry_after)},
                )

            window.append(now)

        # Add rate-limit info headers to every response
        response = await call_next(request)
        with self._lock:
            remaining = max(0, self._limit - len(self._requests[client_ip]))
        response.headers["X-RateLimit-Limit"] = str(self._limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Window"] = f"{_WINDOW_SECONDS}s"
        return response

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"
