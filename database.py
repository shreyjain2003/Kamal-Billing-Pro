import sqlite3

def init_db():

    conn = sqlite3.connect("billing.db")

    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS bills(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer TEXT,
        mobile TEST,
        bill_text TEXT,
        total REAL,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()