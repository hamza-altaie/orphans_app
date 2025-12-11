# housing_screen.py
import tkinter as tk
from tkinter import ttk, messagebox
from ttkbootstrap.constants import *
import sqlite3

class HousingScreen(ttk.Frame):
    def __init__(self, parent, conn: sqlite3.Connection):
        super().__init__(parent)
        self.conn = conn
        
        # الجدول يسار (0)، الفورم يمين (1)
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        self.var_id = tk.StringVar()
        self.var_name = tk.StringVar()
        self.var_type = tk.StringVar()
        self.var_status = tk.StringVar()
        self.var_amount = tk.StringVar()
        
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # --- 1. الجدول (يسار) ---
        table_frame = ttk.LabelFrame(self, text="مشاريع السكن", padding=5)
        table_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        columns = ("id", "name", "type", "status", "amount")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="info.Treeview")
        
        self.tree.heading("id", text="#")
        self.tree.heading("name", text="المستفيد")
        self.tree.heading("type", text="نوع الدعم")
        self.tree.heading("status", text="الحالة")
        self.tree.heading("amount", text="المبلغ")
        
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("name", width=150, anchor="center")
        self.tree.column("type", width=80, anchor="center")
        self.tree.column("status", width=80, anchor="center")
        self.tree.column("amount", width=80, anchor="center")
        
        # RTL عكس الأعمدة
        self.tree["displaycolumns"] = ("amount", "status", "type", "name", "id")
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # --- 2. الفورم (يمين) ---
        form_frame = ttk.LabelFrame(self, text="بيانات المشروع", padding=10)
        form_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=0)
        
        self.row_idx = 0
        def add_row(label, widget):
            widget.grid(row=self.row_idx, column=0, sticky="ew", pady=5, padx=5)
            ttk.Label(form_frame, text=label + ":").grid(row=self.row_idx, column=1, sticky="e", pady=5, padx=5)
            self.row_idx += 1

        add_row("رقم الملف", ttk.Entry(form_frame, textvariable=self.var_id, state="readonly", justify="right"))
        add_row("المستفيد", ttk.Entry(form_frame, textvariable=self.var_name, justify="right"))
        
        cb_type = ttk.Combobox(form_frame, textvariable=self.var_type, values=["بناء", "ترميم", "إيجار"], state="readonly", justify="right")
        add_row("نوع الدعم", cb_type)
        
        cb_status = ttk.Combobox(form_frame, textvariable=self.var_status, values=["قيد الدراسة", "جاري التنفيذ", "مكتمل"], state="readonly", justify="right")
        add_row("حالة المشروع", cb_status)
        
        add_row("المبلغ التقديري", ttk.Entry(form_frame, textvariable=self.var_amount, justify="right"))

        # الأزرار
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=self.row_idx, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="جديد", bootstyle="secondary", width=10, command=self.clear).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="حفظ", bootstyle="warning", width=10, command=self.save).pack(side=LEFT, padx=5)

    def load_data(self):
        for row in self.tree.get_children(): self.tree.delete(row)
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, support_type, project_status, amount_allocated FROM housing_beneficiaries")
        for row in cursor.fetchall():
            self.tree.insert("", "end", iid=row[0], values=row)

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        uid = sel[0]
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM housing_beneficiaries WHERE id=?", (uid,))
        row = cursor.fetchone()
        if row:
            self.var_id.set(row[0])
            self.var_name.set(row[1])
            self.var_type.set(row[6])
            self.var_amount.set(row[7])
            self.var_status.set(row[8])

    def save(self):
        if not self.var_name.get(): return
        cursor = self.conn.cursor()
        data = (self.var_name.get(), self.var_type.get(), self.var_amount.get(), self.var_status.get())
        if self.var_id.get():
            cursor.execute("UPDATE housing_beneficiaries SET name=?, support_type=?, amount_allocated=?, project_status=? WHERE id=?", data + (self.var_id.get(),))
        else:
            cursor.execute("INSERT INTO housing_beneficiaries (name, support_type, amount_allocated, project_status) VALUES (?, ?, ?, ?)", data)
        self.conn.commit()
        self.load_data()
        self.clear()

    def clear(self):
        self.var_id.set("")
        self.var_name.set("")
        self.var_type.set("")
        self.var_amount.set("")
        self.var_status.set("")