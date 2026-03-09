"""Database initialization and connection management for SQLite."""

import sqlite3
import os
from contextlib import contextmanager

DATABASE_PATH = os.getenv("DATABASE_PATH", "car_rental.db")


def get_connection() -> sqlite3.Connection:
    """Create a new database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Initialize database schema."""
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS vehicles (
                id TEXT PRIMARY KEY,
                brand TEXT NOT NULL,
                model TEXT NOT NULL,
                year INTEGER NOT NULL,
                license_plate TEXT NOT NULL UNIQUE,
                category TEXT NOT NULL,
                fuel_type TEXT NOT NULL,
                daily_rate REAL NOT NULL,
                mileage INTEGER DEFAULT 0,
                color TEXT NOT NULL,
                seats INTEGER DEFAULT 5,
                is_available INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS reservations (
                id TEXT PRIMARY KEY,
                vehicle_id TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                customer_email TEXT NOT NULL,
                customer_document TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                total_amount REAL NOT NULL,
                daily_rate REAL NOT NULL,
                total_days INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
            );

            CREATE INDEX IF NOT EXISTS idx_vehicles_category ON vehicles(category);
            CREATE INDEX IF NOT EXISTS idx_vehicles_available ON vehicles(is_available);
            CREATE INDEX IF NOT EXISTS idx_reservations_vehicle ON reservations(vehicle_id);
            CREATE INDEX IF NOT EXISTS idx_reservations_status ON reservations(status);
            CREATE INDEX IF NOT EXISTS idx_reservations_dates ON reservations(start_date, end_date);
        """)
