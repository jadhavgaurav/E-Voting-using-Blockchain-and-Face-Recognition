"""Fixed-window rate limiting. Uses Redis when configured, else in-process memory.

The in-memory backend is per-process and intended for dev/tests; production should set
REDIS_URL so limits hold across workers.
"""

from __future__ import annotations

import time

from app.config import get_settings
from app.core.errors import RateLimitError

try:  # redis is optional at runtime
    import redis.asyncio as aioredis
except Exception:  # pragma: no cover
    aioredis = None  # type: ignore[assignment]


class _MemoryLimiter:
    def __init__(self) -> None:
        self._hits: dict[str, list[float]] = {}

    async def hit(self, key: str, limit: int, window: int) -> None:
        now = time.monotonic()
        bucket = [t for t in self._hits.get(key, []) if now - t < window]
        if len(bucket) >= limit:
            raise RateLimitError("Too many requests, please slow down")
        bucket.append(now)
        self._hits[key] = bucket


class _RedisLimiter:
    def __init__(self, url: str) -> None:
        assert aioredis is not None
        self._redis = aioredis.from_url(url, encoding="utf-8", decode_responses=True)

    async def hit(self, key: str, limit: int, window: int) -> None:
        full_key = f"rl:{key}"
        count = await self._redis.incr(full_key)
        if count == 1:
            await self._redis.expire(full_key, window)
        if count > limit:
            raise RateLimitError("Too many requests, please slow down")


_limiter: _MemoryLimiter | _RedisLimiter | None = None


def get_limiter() -> _MemoryLimiter | _RedisLimiter:
    global _limiter
    if _limiter is None:
        settings = get_settings()
        if settings.redis_url and aioredis is not None:
            _limiter = _RedisLimiter(settings.redis_url)
        else:
            _limiter = _MemoryLimiter()
    return _limiter


async def enforce(scope: str, identity: str, limit: int) -> None:
    """Raise RateLimitError if ``identity`` exceeds ``limit`` within the window."""
    settings = get_settings()
    await get_limiter().hit(f"{scope}:{identity}", limit, settings.rate_limit_window_seconds)
