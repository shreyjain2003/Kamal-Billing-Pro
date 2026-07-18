import sqlite3
import os

# Always resolve DB path relative to this file, not the working directory
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "billing.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Create table if it doesn't exist
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bills(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_no INTEGER,
        customer TEXT,
        mobile TEXT,
        bill_text TEXT,
        total REAL,
        created_at TEXT
    )
    """)

    # Migrate: add bill_no column if it doesn't exist yet
    cur.execute("PRAGMA table_info(bills)")
    columns = [row[1] for row in cur.fetchall()]
    if "bill_no" not in columns:
        cur.execute("ALTER TABLE bills ADD COLUMN bill_no INTEGER")
        # Backfill existing rows in chronological order
        cur.execute("SELECT id FROM bills ORDER BY id ASC")
        rows = cur.fetchall()
        for i, (row_id,) in enumerate(rows, start=1):
            cur.execute("UPDATE bills SET bill_no = ? WHERE id = ?", (i, row_id))

    conn.commit()
    conn.close()


def renumber_bills(conn):
    """Reassign bill_no sequentially (1, 2, 3…) ordered by id after a delete."""
    cur = conn.cursor()
    cur.execute("SELECT id FROM bills ORDER BY id ASC")
    rows = cur.fetchall()
    for i, (row_id,) in enumerate(rows, start=1):
        cur.execute("UPDATE bills SET bill_no = ? WHERE id = ?", (i, row_id))
    conn.commit()
