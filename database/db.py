"""SQLite data layer for Spendly.

Provides three helpers used across the app:
  get_db()   — a connection with dict-like rows and foreign keys enforced
  init_db()  — creates tables (idempotent)
  seed_db()  — inserts demo data once, for development
"""

import sqlite3
from datetime import date
from pathlib import Path

from werkzeug.security import generate_password_hash

# DB lives in the project root (one level up from this database/ package).
DB_PATH = Path(__file__).resolve().parent.parent / "expense_tracker.db"

# Fixed category list — keep in sync with the rest of the app.
CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]


def get_db():
    """Return a SQLite connection with row_factory and FK enforcement on.

    SQLite disables foreign keys by default, so the PRAGMA must run on every
    connection — not just once at setup.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create the users and expenses tables if they don't already exist."""
    conn = get_db()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT NOT NULL,
                email         TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at    TEXT DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                amount      REAL NOT NULL,
                category    TEXT NOT NULL,
                date        TEXT NOT NULL,
                description TEXT,
                created_at  TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def seed_db():
    """Insert one demo user and 8 sample expenses, once.

    Idempotent: if any users already exist, this returns without inserting.
    """
    conn = get_db()
    try:
        existing = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if existing > 0:
            return

        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", generate_password_hash("demo123")),
        )
        user_id = cursor.lastrowid

        # Dates spread across the current month, YYYY-MM-DD.
        today = date.today()

        def day(d):
            return date(today.year, today.month, d).isoformat()

        # (amount, category, date, description) — at least one per category.
        expenses = [
            (12.50, "Food", day(2), "Lunch at cafe"),
            (45.00, "Food", day(15), "Groceries"),
            (30.00, "Transport", day(3), "Monthly metro top-up"),
            (89.99, "Bills", day(5), "Electricity bill"),
            (20.00, "Health", day(8), "Pharmacy"),
            (15.75, "Entertainment", day(11), "Movie ticket"),
            (60.40, "Shopping", day(18), "New shoes"),
            (9.00, "Other", day(21), "Misc"),
        ]

        conn.executemany(
            """
            INSERT INTO expenses (user_id, amount, category, date, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            [(user_id, amount, category, d, desc) for amount, category, d, desc in expenses],
        )
        conn.commit()
    finally:
        conn.close()
