# student_statistics.py
import tkinter as tk
from tkinter import ttk
import sqlite3

class StudentStatisticsScreen(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        self.create_widgets()
        self.refresh()

    def create_widgets(self):
        # بطاقات ملخص في الأعلى
        summary_frame = ttk.LabelFrame(self, text="ملخص عام", padding=10)
        summary_frame.pack(fill="x", padx=10, pady=10)
        
        self.lbl_total = ttk.Label(summary_frame, text="عدد الطلاب الكلي: 0", font=("", 12))
        self.lbl_total.pack(anchor="e", pady=5)
        
        self.lbl_cost = ttk.Label(summary_frame, text="إجمالي الكفالات الشهرية: 0", font=("", 12))
        self.lbl_cost.pack(anchor="e", pady=5)

        # جدول تفصيلي
        tree_frame = ttk.LabelFrame(self, text="توزيع الطلاب حسب المرحلة", padding=10)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.tree = ttk.Treeview(tree_frame, columns=("stage", "count"), show="headings")
        self.tree.heading("stage", text="المرحلة الدراسية")
        self.tree.heading("count", text="العدد")
        self.tree.column("stage", anchor="center"); self.tree.column("count", anchor="center")
        self.tree.pack(fill="both", expand=True)
        
        ttk.Button(self, text="تحديث البيانات", command=self.refresh).pack(pady=10)

    def refresh(self):
        cur = self.conn.cursor()
        
        # العدد الكلي
        cur.execute("SELECT COUNT(*) FROM students")
        total = cur.fetchone()[0]
        self.lbl_total.config(text=f"عدد الطلاب الكلي: {total}")
        
        # تكلفة الكفالات
        cur.execute("SELECT SUM(monthly_amount) FROM student_sponsorships")
        cost = cur.fetchone()[0] or 0
        self.lbl_cost.config(text=f"إجمالي الكفالات الشهرية: {cost:,.0f}")
        
        # التوزيع حسب المرحلة
        for i in self.tree.get_children(): self.tree.delete(i)
        cur.execute("SELECT school_stage, COUNT(*) FROM students GROUP BY school_stage")
        for r in cur.fetchall():
            stage = r[0] if r[0] else "غير محدد"
            self.tree.insert("", "end", values=(stage, r[1]))