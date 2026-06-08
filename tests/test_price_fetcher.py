import pytest
from backend.services.price_fetcher import fetch_price, AssetType


def test_fetch_price_returns_dict():
    result = fetch_price("AAPL", AssetType.STOCK)
    assert isinstance(result, dict)
    assert "price" in result
    assert "currency" in result
    assert isinstance(result["price"], float)
    assert result["price"] > 0


def test_fetch_price_crypto():
    result = fetch_price("bitcoin", AssetType.CRYPTO)
    assert isinstance(result, dict)
    assert "price" in result
    assert result["price"] > 0


def test_fetch_price_invalid_symbol():
    result = fetch_price("INVALID_SYMBOL_12345", AssetType.STOCK)
    assert result is None
