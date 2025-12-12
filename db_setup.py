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

    # --- 2. جداول الطلاب (تمت إضافة الهاتف والملاحظات) ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,             -- حقل جديد: رقم هاتف الطالب
            gender TEXT,
            birth_date TEXT,
            school_stage TEXT,
            school_name TEXT,
            guardian_name TEXT,
            guardian_phone TEXT,
            status TEXT,
            notes TEXT              -- حقل جديد: الملاحظات
        )
    """)
    
    # جدول كفالة الطلاب
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

    # --- 3. جداول دعم السكن (تمت إضافة الهاتف والملاحظات) ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS housing_beneficiaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,             -- حقل جديد: رقم الهاتف
            governorate TEXT,
            address TEXT,
            housing_status TEXT,
            support_type TEXT,
            amount_allocated REAL,
            project_status TEXT,
            notes TEXT              -- حقل جديد: الملاحظات
        )
    """)


    # --- 4. جدول دفعات الطلاب (جديد) ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL,
            required_amount REAL,
            paid_amount REAL,
            status TEXT,
            payment_date TEXT,
            notes TEXT,
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
        )
    """)

    # --- 5. جدول دفعات السكن (جديد) ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS housing_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            housing_id INTEGER NOT NULL,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL,
            required_amount REAL,
            paid_amount REAL,
            status TEXT,
            payment_date TEXT,
            notes TEXT,
            FOREIGN KEY(housing_id) REFERENCES housing_beneficiaries(id) ON DELETE CASCADE
        )
    """)

    conn.commit()