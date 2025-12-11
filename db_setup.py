# db_setup.py
import sqlite3
import os

APP_DIR_NAME = "OrphansApp"

def get_data_dir() -> str:
    base = os.getenv("APPDATA") or os.path.expanduser("~")
    data_dir = os.path.join(base, APP_DIR_NAME)
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

DB_NAME = os.path.join(get_data_dir(), "orphans.db")

def create_tables(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # --- 1. جداول الأيتام ---
    cursor.execute("""
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
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sponsorships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orphan_id INTEGER NOT NULL,
            monthly_amount REAL,
            start_date TEXT,
            status TEXT,
            notes TEXT,
            FOREIGN KEY(orphan_id) REFERENCES orphans(id) ON DELETE CASCADE
        )
    """)
    cursor.execute("""
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
    """)

    # --- 2. جداول الطلاب (نظام جديد) ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            gender TEXT,
            birth_date TEXT,
            school_stage TEXT, -- الابتدائية، المتوسطة، الخ
            school_name TEXT,
            guardian_name TEXT,
            guardian_phone TEXT,
            status TEXT,
            notes TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_sponsorships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            monthly_amount REAL,
            start_date TEXT,
            status TEXT,
            notes TEXT,
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
        )
    """)
    # يمكن إضافة جدول student_payments هنا بنفس هيكلية payments

    # --- 3. جداول دعم السكن (نظام جديد) ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS housing_beneficiaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            governorate TEXT,
            address TEXT,
            phone TEXT,
            housing_status TEXT, -- ملك، إيجار، تجاوز
            support_type TEXT,   -- ترميم، بناء، إيجار
            amount_allocated REAL,
            project_status TEXT, -- قيد الإنجاز، مكتمل
            notes TEXT
        )
    """)

    conn.commit()