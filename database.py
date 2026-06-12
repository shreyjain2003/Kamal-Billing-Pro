import sqlite3
import os

# Always resolve DB path relative to this file, not the working directory
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "billing.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bills(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer TEXT,
        mobile TEXT,
        bill_text TEXT,
        total REAL,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()
