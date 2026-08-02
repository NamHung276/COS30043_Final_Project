import asyncio

import httpx

from app.utils.http_retry import retry_async


async def _fail_twice_then_succeed() -> str:
    raise httpx.ReadTimeout("temporary timeout")


async def _succeed_after_two_failures() -> str:
    if not hasattr(_succeed_after_two_failures, "calls"):
        _succeed_after_two_failures.calls = 0
    _succeed_after_two_failures.calls += 1
    if _succeed_after_two_failures.calls < 3:
        raise httpx.ReadTimeout("temporary timeout")
    return "ok"


def test_retry_async_succeeds_after_transient_failures():
    async def run_test() -> None:
        result = await retry_async(_succeed_after_two_failures, retries=3, delay=0.0)
        assert result == "ok"

    asyncio.run(run_test())


def test_retry_async_raises_after_exhausting_retries():
    async def run_test() -> None:
        try:
            await retry_async(_fail_twice_then_succeed, retries=2, delay=0.0)
        except httpx.ReadTimeout:
            return
        raise AssertionError("expected ReadTimeout to be raised")

    asyncio.run(run_test())
