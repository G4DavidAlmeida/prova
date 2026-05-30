from __future__ import annotations

import json
from typing import Any

from redis import Redis
from redis.exceptions import RedisError

from app.core.settings import Settings


class RedisRepository:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: Redis | None = None

    @property
    def client(self) -> Redis:
        if self._client is None:
            raise RuntimeError("Redis client is not connected")
        return self._client

    def connect(self) -> None:
        self._client = Redis(
            host=self._settings.redis_host,
            port=self._settings.redis_port,
            db=self._settings.redis_db,
            decode_responses=True,
        )
        self._client.ping()

    def ping(self) -> bool:
        try:
            return bool(self.client.ping())
        except RedisError:
            return False

    def get_quote(self, symbol: str) -> dict[str, Any] | None:
        value = self.client.get(self._cache_key(symbol))
        if value is None:
            return None
        return json.loads(value)

    def set_quote(self, symbol: str, payload: dict[str, Any], ttl_seconds: int) -> None:
        self.client.set(
            self._cache_key(symbol),
            json.dumps(payload),
            ex=ttl_seconds,
        )

    def flush(self) -> None:
        self.client.flushdb()

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    @staticmethod
    def _cache_key(symbol: str) -> str:
        return f"quote:{symbol.upper()}"
