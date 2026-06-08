import requests
from enum import Enum


class AssetType(str, Enum):
    STOCK = "stock"
    CRYPTO = "crypto"
    FOREX = "forex"


def fetch_price(symbol: str, asset_type: AssetType) -> dict | None:
    try:
        if asset_type == AssetType.STOCK:
            return _fetch_yahoo(symbol)
        elif asset_type == AssetType.CRYPTO:
            return _fetch_coingecko(symbol)
        elif asset_type == AssetType.FOREX:
            return _fetch_forex(symbol)
    except Exception:
        return None
    return None


def _fetch_yahoo(symbol: str) -> dict | None:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    result = data["chart"]["result"]
    if not result:
        return None
    meta = result[0]["meta"]
    price = meta.get("regularMarketPrice") or meta.get("previousClose")
    currency = meta.get("currency", "USD")
    if price is None:
        return None
    return {"price": float(price), "currency": currency}


def _fetch_coingecko(symbol: str) -> dict | None:
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if symbol not in data or "usd" not in data[symbol]:
        return None
    return {"price": float(data[symbol]["usd"]), "currency": "USD"}


def _fetch_forex(symbol: str) -> dict | None:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    result = data["chart"]["result"]
    if not result:
        return None
    meta = result[0]["meta"]
    price = meta.get("regularMarketPrice") or meta.get("previousClose")
    if price is None:
        return None
    return {"price": float(price), "currency": "USD"}
