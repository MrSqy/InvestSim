from fastapi import APIRouter
from backend.database import get_db
from backend.models.schemas import ScenarioRequest
from backend.services.price_fetcher import fetch_price, AssetType
from backend.services.cache import cache

router = APIRouter(prefix="/analytics", tags=["analytics"])

def get_performance_metrics(conn, user_id: int) -> dict:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT SUM(total_amount) as total_invested FROM transactions WHERE user_id=? AND transaction_type='buy'",
        (user_id,)
    )
    row = cursor.fetchone()
    total_invested = row["total_invested"] or 0.0
    cursor.execute("SELECT * FROM portfolios WHERE user_id=?", (user_id,))
    holdings = cursor.fetchall()
    current_value = 0.0
    for h in holdings:
        cached = cache.get(h["asset_symbol"])
        if cached:
            price = cached["price"]
        else:
            fetched = fetch_price(h["asset_symbol"], AssetType(h["asset_type"]))
            if fetched:
                price = fetched["price"]
                cache.set(h["asset_symbol"], fetched)
            else:
                price = 0.0
        current_value += price * h["total_quantity"]
    total_return = current_value - total_invested
    total_return_percent = (total_return / total_invested * 100) if total_invested > 0 else 0.0
    return {
        "total_invested": total_invested,
        "current_value": current_value,
        "total_return": total_return,
        "total_return_percent": round(total_return_percent, 2)
    }

def calculate_scenario(symbol: str, asset_type: str, hypothetical_date: str, hypothetical_amount: float) -> dict:
    cached = cache.get(symbol)
    if cached:
        current_price = cached["price"]
    else:
        fetched = fetch_price(symbol, AssetType(asset_type))
        if fetched:
            current_price = fetched["price"]
            cache.set(symbol, fetched)
        else:
            current_price = None
    if current_price is None:
        return {
            "symbol": symbol,
            "hypothetical_date": hypothetical_date,
            "hypothetical_amount": hypothetical_amount,
            "current_price": None,
            "hypothetical_value": None,
            "gain_loss": None,
            "gain_loss_percent": None,
            "note": "Historical price lookup not available in v1"
        }
    shares = hypothetical_amount / current_price
    hypothetical_value = shares * current_price
    gain_loss = hypothetical_value - hypothetical_amount
    gain_loss_percent = (gain_loss / hypothetical_amount * 100) if hypothetical_amount > 0 else 0.0
    return {
        "symbol": symbol,
        "hypothetical_date": hypothetical_date,
        "hypothetical_amount": hypothetical_amount,
        "current_price": current_price,
        "hypothetical_value": round(hypothetical_value, 2),
        "gain_loss": round(gain_loss, 2),
        "gain_loss_percent": round(gain_loss_percent, 2)
    }

@router.get("/performance")
def read_performance():
    with get_db() as conn:
        return get_performance_metrics(conn, 1)

@router.post("/scenario")
def run_scenario(req: ScenarioRequest):
    result = calculate_scenario(req.asset_symbol, req.asset_type, req.hypothetical_date, req.hypothetical_amount)
    return result

@router.get("/diversification")
def read_diversification():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT asset_type, SUM(total_quantity * avg_cost_basis) as value FROM portfolios WHERE user_id=1 GROUP BY asset_type"
        )
        rows = cursor.fetchall()
        total = sum(r["value"] or 0 for r in rows)
        result = []
        for r in rows:
            value = r["value"] or 0
            result.append({
                "asset_type": r["asset_type"],
                "value": round(value, 2),
                "percentage": round(value / total * 100, 2) if total > 0 else 0
            })
        return result
