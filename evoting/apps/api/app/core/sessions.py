"""Short-lived key/value store for verification challenge sessions (Redis or memory)."""

from __future__ import annotations

import json
import time
from typing import cast

from app.config import get_settings

try:
    import redis.asyncio as aioredis
except Exception:  # pragma: no cover
    aioredis = None  # type: ignore[assignment]


class _MemoryStore:
    def __init__(self) -> None:
        self._data: dict[str, tuple[float, str]] = {}

    async def set(self, key: str, value: str, ttl: int) -> None:
        self._data[key] = (time.monotonic() + ttl, value)

    async def get(self, key: str) -> str | None:
        item = self._data.get(key)
        if item is None:
            return None
        expires, value = item
        if time.monotonic() > expires:
            self._data.pop(key, None)
            return None
        return value

    async def delete(self, key: str) -> None:
        self._data.pop(key, None)


class _RedisStore:
    def __init__(self, url: str) -> None:
        assert aioredis is not None
        self._redis = aioredis.from_url(url, encoding="utf-8", decode_responses=True)

    async def set(self, key: str, value: str, ttl: int) -> None:
        await self._redis.set(key, value, ex=ttl)

    async def get(self, key: str) -> str | None:
        # decode_responses=True guarantees str, but the stub types this as bytes|str|None.
        return cast("str | None", await self._redis.get(key))

    async def delete(self, key: str) -> None:
        await self._redis.delete(key)


_store: _MemoryStore | _RedisStore | None = None


def _backend() -> _MemoryStore | _RedisStore:
    global _store
    if _store is None:
        settings = get_settings()
        _store = (
            _RedisStore(settings.redis_url)
            if settings.redis_url and aioredis is not None
            else _MemoryStore()
        )
    return _store


async def put_session(request_id: str, payload: dict[str, str], ttl: int) -> None:
    await _backend().set(f"verif:{request_id}", json.dumps(payload), ttl)


async def get_session(request_id: str) -> dict[str, str] | None:
    raw = await _backend().get(f"verif:{request_id}")
    return json.loads(raw) if raw else None


async def drop_session(request_id: str) -> None:
    await _backend().delete(f"verif:{request_id}")
