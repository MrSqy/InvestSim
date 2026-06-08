import sqlite3
from contextlib import contextmanager
from backend.config import DATABASE_URL, DEFAULT_VIRTUAL_BALANCE, DEFAULT_CURRENCY

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    virtual_balance REAL NOT NULL,
    currency TEXT NOT NULL DEFAULT 'USD',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    asset_symbol TEXT NOT NULL,
    asset_type TEXT NOT NULL CHECK(asset_type IN ('stock', 'crypto', 'forex')),
    transaction_type TEXT NOT NULL CHECK(transaction_type IN ('buy', 'sell')),
    quantity REAL NOT NULL,
    price REAL NOT NULL,
    total_amount REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS portfolios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    asset_symbol TEXT NOT NULL,
    asset_type TEXT NOT NULL,
    total_quantity REAL NOT NULL DEFAULT 0,
    avg_cost_basis REAL NOT NULL DEFAULT 0,
    UNIQUE(user_id, asset_symbol),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS price_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_symbol TEXT NOT NULL UNIQUE,
    asset_type TEXT NOT NULL,
    price REAL NOT NULL,
    currency TEXT NOT NULL,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scenarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    asset_symbol TEXT NOT NULL,
    asset_type TEXT NOT NULL,
    hypothetical_date TEXT NOT NULL,
    hypothetical_amount REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
"""

@contextmanager
def get_db(db_path=None):
    path = db_path or DATABASE_URL
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db(db_path=None):
    with get_db(db_path) as conn:
        conn.executescript(SCHEMA)
        conn.commit()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO users (id, username, virtual_balance, currency) VALUES (1, 'default', ?, ?)",
            (DEFAULT_VIRTUAL_BALANCE, DEFAULT_CURRENCY)
        )
        conn.commit()
