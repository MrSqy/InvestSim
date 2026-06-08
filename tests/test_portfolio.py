import pytest
import os
from backend.database import init_db, get_db
from backend.routers.orders import execute_buy
from backend.routers.portfolio import get_portfolio, get_transaction_history

TEST_DB = "tests/test_portfolio.db"

@pytest.fixture(autouse=True)
def setup():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    init_db(TEST_DB)
    with get_db(TEST_DB) as conn:
        execute_buy(conn, 1, "AAPL", "stock", 10, 150.0)
        execute_buy(conn, 1, "TSLA", "stock", 5, 200.0)
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_get_portfolio():
    with get_db(TEST_DB) as conn:
        portfolio = get_portfolio(conn, 1)
        assert len(portfolio) == 2
        symbols = [p["asset_symbol"] for p in portfolio]
        assert "AAPL" in symbols
        assert "TSLA" in symbols

def test_get_transaction_history():
    with get_db(TEST_DB) as conn:
        history = get_transaction_history(conn, 1)
        assert len(history) == 2
