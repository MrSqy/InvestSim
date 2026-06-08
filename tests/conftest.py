import pytest
import sqlite3
import os

TEST_DB = "tests/test_investsim.db"

@pytest.fixture(autouse=True)
def clean_test_db():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_database_creates_tables():
    from backend.database import init_db
    init_db(TEST_DB)
    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    assert "users" in tables
    assert "transactions" in tables
    assert "portfolios" in tables
    assert "price_cache" in tables
    assert "scenarios" in tables
