import asyncio
import logging
from typing import Any, Callable, Awaitable, TypeVar

import httpx

logger = logging.getLogger(__name__)
T = TypeVar("T")


async def retry_async(
    func: Callable[[], Awaitable[T]],
    retries: int = 3,
    delay: float = 0.5,
    retryable_exceptions: tuple[type[Exception], ...] = (httpx.TimeoutException, httpx.TransportError),
) -> T:
    """Retry an async callable a few times for transient network issues."""
    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        try:
            return await func()
        except retryable_exceptions as exc:
            last_exc = exc
            if attempt >= retries:
                raise
            logger.warning("Transient request failure on attempt %s/%s: %s", attempt + 1, retries + 1, exc)
            if delay > 0:
                await asyncio.sleep(delay)
    if last_exc is not None:
        raise last_exc
    raise RuntimeError("retry_async exhausted without raising")
