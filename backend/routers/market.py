from fastapi import APIRouter, HTTPException
from backend.services.price_fetcher import fetch_price, AssetType
from backend.services.cache import cache
from backend.database import get_db

router = APIRouter(prefix="/market", tags=["market"])

ASSETS = [
    {"symbol": "AAPL", "name": "Apple Inc.", "asset_type": "stock"},
    {"symbol": "TSLA", "name": "Tesla Inc.", "asset_type": "stock"},
    {"symbol": "GOOGL", "name": "Alphabet Inc.", "asset_type": "stock"},
    {"symbol": "bitcoin", "name": "Bitcoin", "asset_type": "crypto"},
    {"symbol": "ethereum", "name": "Ethereum", "asset_type": "crypto"},
    {"symbol": "EURUSD=X", "name": "EUR/USD", "asset_type": "forex"},
    {"symbol": "GBPUSD=X", "name": "GBP/USD", "asset_type": "forex"},
]

@router.get("/assets")
def list_assets():
    return ASSETS

@router.get("/price/{symbol}")
def get_price(symbol: str, asset_type: str = "stock"):
    cached = cache.get(symbol)
    if cached:
        return {"symbol": symbol, "price": cached["price"], "currency": cached["currency"], "source": "cache"}
    result = fetch_price(symbol, AssetType(asset_type))
    if result is None:
        raise HTTPException(status_code=404, detail=f"Price not found for {symbol}")
    cache.set(symbol, result)
    return {"symbol": symbol, "price": result["price"], "currency": result["currency"], "source": "api"}
