# settings_screen.py
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
import sqlite3
from db_setup import DB_NAME

# استيراد دوال الحفظ والاسترجاع من ملف الإعدادات
from app_settings import (
    get_currency_symbol,
    set_currency_symbol,
    get_default_export_dir,
    set_default_export_dir,
)

class SettingsScreen(ttk.Frame):
    def __init__(self, parent, conn: sqlite3.Connection = None):
        super().__init__(parent)
        self.conn = conn
        
        # تحميل القيم الحالية
        self.var_currency = ttk.StringVar(value=get_currency_symbol())
        self.var_export_dir = ttk.StringVar(value=get_default_export_dir() or "")

        self.create_widgets()

    def create_widgets(self):
        # حاوية رئيسية في المنتصف مع شريط تمرير إذا لزم الأمر
        container = ttk.Frame(self)
        container.pack(expand=True, fill="both", padx=50, pady=20)

        # ==========================
        # 1. قسم الإعدادات العامة
        # ==========================
        gen_frame = ttk.Labelframe(
            container, 
            text=" إعدادات عامة ", 
            padding=20, 
            bootstyle="info",
            labelanchor="ne"  # <--- هذا هو الجزء المسؤول عن المحاذاة لليمين
        )
        gen_frame.pack(fill="x", pady=(0, 20))

        # --- رمز العملة ---
        row1 = ttk.Frame(gen_frame)
        row1.pack(fill="x", pady=5)
        
        ttk.Label(row1, text=":رمز العملة (مثال: د.ع أو $)", font=("Segoe UI", 10)).pack(side=RIGHT)
        ttk.Entry(
            row1, 
            textvariable=self.var_currency, 
            width=15, 
            justify="right"
        ).pack(side=RIGHT, padx=10)

        # --- مسار التصدير ---
        row2 = ttk.Frame(gen_frame)
        row2.pack(fill="x", pady=5)

        ttk.Label(row2, text=":مسار حفظ التقارير", font=("Segoe UI", 10)).pack(side=RIGHT)
        
        # حقل المسار + زر التصفح
        path_frame = ttk.Frame(row2)
        path_frame.pack(side=RIGHT, fill="x", expand=True, padx=10)
        
        ttk.Entry(
            path_frame, 
            textvariable=self.var_export_dir, 
            state="readonly", 
            justify="right"
        ).pack(side=RIGHT, fill="x", expand=True)

        ttk.Button(
            path_frame, 
            text="تصفح", 
            command=self.browse_export_dir,
            bootstyle="outline-info",
            width=10
        ).pack(side=RIGHT, padx=(0, 5))

        # زر الحفظ
        ttk.Button(
            gen_frame, 
            text="حفظ الإعدادات", 
            command=self.save_settings, 
            bootstyle="success",
            width=20
        ).pack(pady=(15, 0))

        # ==========================
        # 2. قسم إدارة البيانات (الخطر)
        # ==========================
        danger_frame = ttk.Labelframe(
            container, 
            text=" منطقة الخطر ", 
            padding=20, 
            bootstyle="danger",
            labelanchor="ne"  # <--- هذا السطر المسؤول عن المحاذاة لليمين
        )
        danger_frame.pack(fill="x", pady=10)

        ttk.Label(
            danger_frame, 
            text="تحذير: الإجراءات هنا لا يمكن التراجع عنها", 
            bootstyle="danger",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="e", pady=(0, 10))

        # زر تصفير المصنع
        ttk.Button(
            danger_frame,
            text="حذف كافة البيانات (تصفير قاعدة البيانات)",
            bootstyle="danger",
            width=35,
            command=self.reset_factory
        ).pack(pady=5)

        ttk.Label(
            danger_frame,
            text="سيقوم هذا الإجراء بحذف جميع البيانات وإعادة العداد إلى 1",
            font=("Segoe UI", 9),
            bootstyle="secondary"
        ).pack()

    # --- دوال الإعدادات العامة ---
    def browse_export_dir(self):
        path = filedialog.askdirectory(title="اختيار مجلد الحفظ")
        if path:
            self.var_export_dir.set(path)

    def save_settings(self):
        symbol = self.var_currency.get().strip()
        export_dir = self.var_export_dir.get().strip()
        
        set_currency_symbol(symbol)
        set_default_export_dir(export_dir)
        
        messagebox.showinfo("تم", "تم حفظ الإعدادات بنجاح.")

    # --- دوال تصفير البيانات ---
    def reset_factory(self):
        """دالة لحذف كل البيانات وتصفير العدادات لكافة الأنظمة"""
        
        confirm1 = messagebox.askyesno(
            "تحذير هام", 
            "هل أنت متأكد أنك تريد حذف جميع البيانات من كل الأنظمة؟\n(الأيتام، الطلاب، السكن)\n\nلا يمكن استرجاع البيانات بعد الحذف!"
        )
        if not confirm1:
            return

        confirm2 = messagebox.askyesno(
            "تأكيد نهائي", 
            "هل تريد حقاً تصفير العدادات والبدء من جديد؟"
        )
        if not confirm2:
            return

        try:
            # 1. التأكد من الاتصال
            if self.conn is None:
                self.conn = sqlite3.connect(DB_NAME)

            cursor = self.conn.cursor()

            # --- 2. حذف بيانات الأيتام ---
            cursor.execute("DELETE FROM payments")
            cursor.execute("DELETE FROM sponsorships")
            cursor.execute("DELETE FROM orphans")
            
            # --- 3. حذف بيانات الطلاب ---
            cursor.execute("DELETE FROM student_payments")
            cursor.execute("DELETE FROM student_sponsorships")
            cursor.execute("DELETE FROM students")

            # --- 4. حذف بيانات مشاريع السكن ---
            cursor.execute("DELETE FROM housing_payments")
            # التصحيح هنا: الاسم الصحيح هو housing_beneficiaries وليس housing_projects
            cursor.execute("DELETE FROM housing_beneficiaries") 
            
            # --- 5. تصفير العدادات (مهم جداً ليعود الرقم 1) ---
            cursor.execute("DELETE FROM sqlite_sequence")

            self.conn.commit()
            
            # 6. رسالة نجاح وإغلاق البرنامج
            messagebox.showinfo(
                "نجاح", 
                "تم تصفير النظام بالكامل (أيتام، طلاب، سكن).\n\nسيتم إغلاق البرنامج الآن، يرجى إعادة تشغيله."
            )
            
            # إغلاق البرنامج بالكامل
            self.quit()

        except Exception as e:
            self.conn.rollback() # تراجع عن التغييرات لتجنب مشاكل جزئية
            messagebox.showerror("خطأ", f"حدث خطأ أثناء التصفير:\n{e}")