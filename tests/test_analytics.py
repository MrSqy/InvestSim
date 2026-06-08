import pytest
import os
from backend.database import init_db, get_db
from backend.routers.orders import execute_buy
from backend.routers.analytics import get_performance_metrics, calculate_scenario

TEST_DB = "tests/test_analytics.db"

@pytest.fixture(autouse=True)
def setup():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    init_db(TEST_DB)
    with get_db(TEST_DB) as conn:
        execute_buy(conn, 1, "AAPL", "stock", 10, 100.0)
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_performance_metrics():
    with get_db(TEST_DB) as conn:
        metrics = get_performance_metrics(conn, 1)
        assert metrics["total_invested"] == 1000.0

def test_scenario_calculation():
    result = calculate_scenario("AAPL", "stock", "2024-01-01", 1000.0)
    assert "hypothetical_value" in result
    assert "current_price" in result
