# db_setup.py
import sqlite3

DB_NAME = "orphans.db"


def create_tables(conn: sqlite3.Connection):
    """إنشاء الجداول إذا لم تكن موجودة"""
    cursor = conn.cursor()

    # جدول الأيتام
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS orphans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            gender TEXT,
            age INTEGER,
            governorate TEXT,
            address TEXT,
            guardian_name TEXT,
            guardian_phone TEXT,
            status TEXT,
            notes TEXT
        )
        """
    )

    # جدول الكفالات
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sponsorships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orphan_id INTEGER NOT NULL,
            monthly_amount REAL,
            start_date TEXT,
            status TEXT,
            notes TEXT,
            FOREIGN KEY(orphan_id) REFERENCES orphans(id) ON DELETE CASCADE
        )
        """
    )

    # جدول الدفعات
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orphan_id INTEGER NOT NULL,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL,
            required_amount REAL,
            paid_amount REAL,
            status TEXT,
            payment_date TEXT,
            notes TEXT,
            FOREIGN KEY(orphan_id) REFERENCES orphans(id) ON DELETE CASCADE
        )
        """
    )

    conn.commit()
