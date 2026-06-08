from fastapi import APIRouter
from backend.database import get_db
from backend.services.price_fetcher import fetch_price, AssetType
from backend.services.cache import cache
from typing import List

router = APIRouter(prefix="/portfolio", tags=["portfolio"])

def get_portfolio(conn, user_id: int) -> List[dict]:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM portfolios WHERE user_id=?", (user_id,))
    rows = cursor.fetchall()
    result = []
    for row in rows:
        item = dict(row)
        cached = cache.get(item["asset_symbol"])
        if cached:
            current_price = cached["price"]
        else:
            fetched = fetch_price(item["asset_symbol"], AssetType(item["asset_type"]))
            if fetched:
                current_price = fetched["price"]
                cache.set(item["asset_symbol"], fetched)
            else:
                current_price = None
        item["current_price"] = current_price
        if current_price is not None:
            item["unrealized_pnl"] = (current_price - item["avg_cost_basis"]) * item["total_quantity"]
        else:
            item["unrealized_pnl"] = None
        result.append(item)
    return result

def get_transaction_history(conn, user_id: int) -> List[dict]:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM transactions WHERE user_id=? ORDER BY timestamp DESC",
        (user_id,)
    )
    return [dict(row) for row in cursor.fetchall()]

@router.get("/")
def read_portfolio():
    with get_db() as conn:
        return get_portfolio(conn, 1)

@router.get("/history")
def read_history():
    with get_db() as conn:
        return get_transaction_history(conn, 1)

@router.get("/balance")
def read_balance():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT virtual_balance FROM users WHERE id=1")
        return {"balance": cursor.fetchone()["virtual_balance"]}
