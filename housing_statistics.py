# housing_statistics.py
import tkinter as tk
from tkinter import ttk
import sqlite3

class HousingStatisticsScreen(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        self.create_widgets()
        self.refresh()

    def create_widgets(self):
        frame = ttk.LabelFrame(self, text="إحصائيات مشاريع السكن", padding=10)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.lbl_total = ttk.Label(frame, text="...", font=("", 14))
        self.lbl_total.pack(pady=10)
        
        self.lbl_money = ttk.Label(frame, text="...", font=("", 12))
        self.lbl_money.pack(pady=5)
        
        self.tree = ttk.Treeview(frame, columns=("type", "count"), show="headings", height=6)
        self.tree.heading("type", text="نوع الدعم")
        self.tree.heading("count", text="العدد")
        self.tree.column("type", anchor="center"); self.tree.column("count", anchor="center")
        self.tree.pack(fill="x", pady=10)
        
        ttk.Button(self, text="تحديث", command=self.refresh).pack()

    def refresh(self):
        cur = self.conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM housing_beneficiaries")
        total = cur.fetchone()[0]
        self.lbl_total.config(text=f"إجمالي عدد المشاريع: {total}")
        
        cur.execute("SELECT SUM(amount_allocated) FROM housing_beneficiaries")
        money = cur.fetchone()[0] or 0
        self.lbl_money.config(text=f"إجمالي المبالغ المخصصة: {money:,.0f}")
        
        for i in self.tree.get_children(): self.tree.delete(i)
        cur.execute("SELECT support_type, COUNT(*) FROM housing_beneficiaries GROUP BY support_type")
        for r in cur.fetchall():
            self.tree.insert("", "end", values=(r[0] or "غير محدد", r[1]))