from fastapi import APIRouter, HTTPException
from backend.database import get_db
from backend.models.schemas import OrderRequest, OrderResponse
from backend.services.price_fetcher import fetch_price, AssetType
from backend.services.cache import cache

router = APIRouter(prefix="/orders", tags=["orders"])

def execute_buy(conn, user_id: int, symbol: str, asset_type: str, quantity: float, price: float):
    cursor = conn.cursor()
    total = quantity * price
    cursor.execute("SELECT virtual_balance FROM users WHERE id=?", (user_id,))
    row = cursor.fetchone()
    if row is None:
        raise ValueError("User not found")
    balance = row["virtual_balance"]
    if balance < total:
        raise ValueError("Insufficient balance")
    cursor.execute("UPDATE users SET virtual_balance=? WHERE id=?", (balance - total, user_id))
    cursor.execute(
        "INSERT INTO transactions (user_id, asset_symbol, asset_type, transaction_type, quantity, price, total_amount) VALUES (?,?,?,?,?,?,?)",
        (user_id, symbol, asset_type, "buy", quantity, price, total)
    )
    cursor.execute(
        "SELECT total_quantity, avg_cost_basis FROM portfolios WHERE user_id=? AND asset_symbol=?",
        (user_id, symbol)
    )
    port = cursor.fetchone()
    if port is None:
        cursor.execute(
            "INSERT INTO portfolios (user_id, asset_symbol, asset_type, total_quantity, avg_cost_basis) VALUES (?,?,?,?,?)",
            (user_id, symbol, asset_type, quantity, price)
        )
    else:
        old_qty = port["total_quantity"]
        old_cost = port["avg_cost_basis"]
        new_qty = old_qty + quantity
        new_cost = (old_qty * old_cost + quantity * price) / new_qty
        cursor.execute(
            "UPDATE portfolios SET total_quantity=?, avg_cost_basis=? WHERE user_id=? AND asset_symbol=?",
            (new_qty, new_cost, user_id, symbol)
        )
    conn.commit()

def execute_sell(conn, user_id: int, symbol: str, asset_type: str, quantity: float, price: float):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT total_quantity, avg_cost_basis FROM portfolios WHERE user_id=? AND asset_symbol=?",
        (user_id, symbol)
    )
    port = cursor.fetchone()
    if port is None or port["total_quantity"] < quantity:
        raise ValueError("Insufficient shares")
    total = quantity * price
    cursor.execute("SELECT virtual_balance FROM users WHERE id=?", (user_id,))
    balance = cursor.fetchone()["virtual_balance"]
    cursor.execute("UPDATE users SET virtual_balance=? WHERE id=?", (balance + total, user_id))
    cursor.execute(
        "INSERT INTO transactions (user_id, asset_symbol, asset_type, transaction_type, quantity, price, total_amount) VALUES (?,?,?,?,?,?,?)",
        (user_id, symbol, asset_type, "sell", quantity, price, total)
    )
    new_qty = port["total_quantity"] - quantity
    if new_qty <= 0:
        cursor.execute("DELETE FROM portfolios WHERE user_id=? AND asset_symbol=?", (user_id, symbol))
    else:
        cursor.execute(
            "UPDATE portfolios SET total_quantity=? WHERE user_id=? AND asset_symbol=?",
            (new_qty, user_id, symbol)
        )
    conn.commit()

@router.post("/buy", response_model=OrderResponse)
def buy(req: OrderRequest):
    with get_db() as conn:
        cached = cache.get(req.asset_symbol)
        if cached:
            price = cached["price"]
        else:
            fetched = fetch_price(req.asset_symbol, AssetType(req.asset_type))
            if fetched is None:
                raise HTTPException(status_code=404, detail="Price not available")
            price = fetched["price"]
            cache.set(req.asset_symbol, fetched)
        try:
            execute_buy(conn, 1, req.asset_symbol, req.asset_type, req.quantity, price)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT 1")
        row = dict(cursor.fetchone())
        return OrderResponse(**row)

@router.post("/sell", response_model=OrderResponse)
def sell(req: OrderRequest):
    with get_db() as conn:
        cached = cache.get(req.asset_symbol)
        if cached:
            price = cached["price"]
        else:
            fetched = fetch_price(req.asset_symbol, AssetType(req.asset_type))
            if fetched is None:
                raise HTTPException(status_code=404, detail="Price not available")
            price = fetched["price"]
            cache.set(req.asset_symbol, fetched)
        try:
            execute_sell(conn, 1, req.asset_symbol, req.asset_type, req.quantity, price)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT 1")
        row = dict(cursor.fetchone())
        return OrderResponse(**row)
