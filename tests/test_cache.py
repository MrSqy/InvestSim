import time
from backend.services.cache import PriceCache


def test_cache_get_miss():
    cache = PriceCache(ttl_seconds=5)
    assert cache.get("AAPL") is None


def test_cache_set_and_get():
    cache = PriceCache(ttl_seconds=5)
    cache.set("AAPL", {"price": 150.0, "currency": "USD"})
    result = cache.get("AAPL")
    assert result is not None
    assert result["price"] == 150.0


def test_cache_expires():
    cache = PriceCache(ttl_seconds=1)
    cache.set("AAPL", {"price": 150.0})
    time.sleep(1.1)
    assert cache.get("AAPL") is None


def test_cache_clear():
    cache = PriceCache(ttl_seconds=5)
    cache.set("AAPL", {"price": 150.0})
    cache.clear()
    assert cache.get("AAPL") is None
