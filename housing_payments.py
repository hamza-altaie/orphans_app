# housing_payments.py
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from ttkbootstrap.widgets import DateEntry
from app_settings import get_currency_symbol

class HousingPaymentsScreen(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        
        self.var_month = tk.StringVar(value=str(datetime.now().month))
        self.var_year = tk.StringVar(value=str(datetime.now().year))
        
        self.var_pid = tk.StringVar()
        self.var_paid = tk.StringVar()
        self.var_status = tk.StringVar()
        self.var_date = tk.StringVar()
        self.filter_name = tk.StringVar()
        
        self.total_req = tk.StringVar(value="0")
        self.total_paid = tk.StringVar(value="0")
        self.total_rem = tk.StringVar(value="0")

        self.create_widgets()

    def create_widgets(self):
        # Top
        top = ttk.Frame(self); top.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(top, text="سنة:\u200f").pack(side="right"); ttk.Entry(top, textvariable=self.var_year, width=5).pack(side="right")
        ttk.Label(top, text="شهر:\u200f").pack(side="right"); ttk.Combobox(top, textvariable=self.var_month, values=[str(i) for i in range(1,13)], width=4).pack(side="right")
        ttk.Button(top, text="تحميل", command=self.load).pack(side="right", padx=5)
        ttk.Button(top, text="إنشاء دفعات", command=self.create_batch, bootstyle="warning").pack(side="right", padx=5)

        # Main
        main = ttk.Frame(self); main.pack(expand=True, fill="both", padx=10)
        
        # Form Right
        right = ttk.LabelFrame(main, text="بيانات الدفعة", padding=10)
        right.pack(side="right", fill="y")
        
        ttk.Label(right, text="المدفوع:\u200f").pack(anchor="ne")
        ttk.Entry(right, textvariable=self.var_paid).pack(fill="x")
        ttk.Label(right, text="الحالة:\u200f").pack(anchor="ne")
        ttk.Combobox(right, textvariable=self.var_status, values=["مدفوع", "غير مدفوع"]).pack(fill="x")
        ttk.Button(right, text="حفظ", command=self.save, bootstyle="success").pack(fill="x", pady=10)

        # Tree Left
        left = ttk.Frame(main); left.pack(side="left", fill="both", expand=True)
        
        # Filter
        f = ttk.Frame(left); f.pack(fill="x")
        ttk.Entry(f, textvariable=self.filter_name).pack(side="right"); ttk.Button(f, text="بحث", command=self.load).pack(side="right")

        self.tree = ttk.Treeview(left, columns=("id","hid","name","req","paid","rem","stat"), show="headings")
        self.tree.heading("name", text="المشروع"); self.tree.heading("req", text="المخصص")
        self.tree.heading("paid", text="المدفوع"); self.tree.heading("rem", text="المتبقي")
        self.tree.heading("stat", text="الحالة")
        
        self.tree.column("id", width=0, stretch=False); self.tree.column("hid", width=0, stretch=False)
        self.tree.column("name", width=150)
        
        self.tree["displaycolumns"] = ("stat", "rem", "paid", "req", "name") # RTL
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Totals
        t = ttk.Frame(left); t.pack(fill="x")
        ttk.Label(t, textvariable=self.total_rem).pack(side="left", padx=5); ttk.Label(t, text="المتبقي:").pack(side="left")
        ttk.Label(t, textvariable=self.total_paid).pack(side="left", padx=5); ttk.Label(t, text="المدفوع:").pack(side="left")

    def create_batch(self):
        try:
            m, y = int(self.var_month.get()), int(self.var_year.get())
            cur = self.conn.cursor()
            # في نظام السكن، قد نعتبر المبلغ المخصص هو المطلوب لهذا الشهر أو نعتبره قسطاً
            # للتبسيط سنعتبر المبلغ المخصص (amount_allocated) هو المطلوب
            cur.execute("SELECT id, amount_allocated FROM housing_beneficiaries")
            for hid, amt in cur.fetchall():
                cur.execute("SELECT id FROM housing_payments WHERE housing_id=? AND month=? AND year=?", (hid, m, y))
                if not cur.fetchone():
                    cur.execute("INSERT INTO housing_payments (housing_id, month, year, required_amount, paid_amount, status) VALUES (?,?,?,?,0,'غير مدفوع')", (hid, m, y, amt or 0))
            self.conn.commit(); self.load(); messagebox.showinfo("تم", "تم الإنشاء")
        except Exception as e: messagebox.showerror("خطأ", str(e))

    def load(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        try:
            m, y = int(self.var_month.get()), int(self.var_year.get())
            cur = self.conn.cursor()
            cur.execute("""
                SELECT p.id, h.id, h.name, p.required_amount, p.paid_amount, p.status 
                FROM housing_payments p JOIN housing_beneficiaries h ON h.id=p.housing_id
                WHERE p.month=? AND p.year=? AND h.name LIKE ?""", (m, y, f"%{self.filter_name.get()}%"))
            
            rs=ps=rms=0
            for r in cur.fetchall():
                rem = (r[3] or 0) - (r[4] or 0)
                rs+=r[3] or 0; ps+=r[4] or 0; rms+=rem
                self.tree.insert("", "end", values=(r[0], r[1], r[2], r[3], r[4], rem, r[5]))
            
            sym = get_currency_symbol()
            self.total_req.set(f"{rs:,.0f} {sym}"); self.total_paid.set(f"{ps:,.0f} {sym}"); self.total_rem.set(f"{rms:,.0f} {sym}")
        except: pass

    def on_select(self, e):
        sel = self.tree.selection()
        if not sel: return
        v = self.tree.item(sel[0])['values']
        self.var_pid.set(v[0]); self.var_paid.set(v[4]); self.var_status.set(v[6])

    def save(self):
        if not self.var_pid.get(): return
        self.conn.execute("UPDATE housing_payments SET paid_amount=?, status=? WHERE id=?", (self.var_paid.get(), self.var_status.get(), self.var_pid.get()))
        self.conn.commit(); self.load()