import time
from typing import Any


class PriceCache:
    def __init__(self, ttl_seconds: int = 300):
        self._store: dict[str, dict] = {}
        self._ttl = ttl_seconds

    def get(self, symbol: str) -> dict | None:
        entry = self._store.get(symbol)
        if entry is None:
            return None
        if time.time() - entry["timestamp"] > self._ttl:
            del self._store[symbol]
            return None
        return entry["data"]

    def set(self, symbol: str, data: dict[str, Any]) -> None:
        self._store[symbol] = {"timestamp": time.time(), "data": data}

    def clear(self) -> None:
        self._store.clear()

# Global singleton instance shared across all routers
cache = PriceCache(ttl_seconds=300)
