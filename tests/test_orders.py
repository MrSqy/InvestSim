import pytest
import os
from backend.database import init_db, get_db
from backend.routers.orders import execute_buy, execute_sell

TEST_DB = "tests/test_orders.db"

@pytest.fixture(autouse=True)
def setup():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    init_db(TEST_DB)
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_buy_reduces_balance():
    with get_db(TEST_DB) as conn:
        execute_buy(conn, 1, "AAPL", "stock", 10, 150.0)
        cursor = conn.cursor()
        cursor.execute("SELECT virtual_balance FROM users WHERE id=1")
        balance = cursor.fetchone()["virtual_balance"]
        assert balance == 100000.0 - 1500.0

def test_buy_creates_portfolio_entry():
    with get_db(TEST_DB) as conn:
        execute_buy(conn, 1, "AAPL", "stock", 10, 150.0)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM portfolios WHERE user_id=1 AND asset_symbol='AAPL'")
        row = cursor.fetchone()
        assert row["total_quantity"] == 10.0
        assert row["avg_cost_basis"] == 150.0

def test_sell_insufficient_shares():
    with get_db(TEST_DB) as conn:
        execute_buy(conn, 1, "AAPL", "stock", 5, 150.0)
        with pytest.raises(ValueError, match="Insufficient"):
            execute_sell(conn, 1, "AAPL", "stock", 10, 160.0)

def test_sell_updates_balance():
    with get_db(TEST_DB) as conn:
        execute_buy(conn, 1, "AAPL", "stock", 10, 150.0)
        execute_sell(conn, 1, "AAPL", "stock", 5, 160.0)
        cursor = conn.cursor()
        cursor.execute("SELECT virtual_balance FROM users WHERE id=1")
        balance = cursor.fetchone()["virtual_balance"]
        assert balance == 99300.0
