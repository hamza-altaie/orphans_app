# student_payments.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from ttkbootstrap.widgets import DateEntry
from app_settings import get_currency_symbol

class StudentPaymentsScreen(ttk.Frame):
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
        
        # المجاميع
        self.total_req = tk.StringVar(value="0")
        self.total_paid = tk.StringVar(value="0")
        self.total_rem = tk.StringVar(value="0")

        self.create_widgets()

    def create_widgets(self):
        # --- الشريط العلوي ---
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(top, text="السنة :\u200f").pack(side="right", padx=5)
        ttk.Entry(top, textvariable=self.var_year, width=6).pack(side="right", padx=5)
        
        ttk.Label(top, text="الشهر :\u200f").pack(side="right", padx=5)
        ttk.Combobox(top, textvariable=self.var_month, values=[str(i) for i in range(1,13)], width=5, state="readonly").pack(side="right", padx=5)
        
        ttk.Button(top, text="تحميل الدفعات", command=self.load_payments).pack(side="right", padx=10)
        ttk.Button(top, text="إنشاء دفعات الشهر", command=self.create_monthly_payments, bootstyle="success").pack(side="right", padx=10)

        # --- المنطقة الرئيسية ---
        main = ttk.Frame(self)
        main.pack(expand=True, fill="both", padx=10, pady=5)
        
        # الجدول (يمين - افتراض RTL)
        # ملاحظة: في الواجهة العربية الجدول يكون يمين إذا كان الاتجاه العام RTL
        # هنا سنضع الجدول على اليسار والفورم يمين ليتناسق مع الكود السابق
        
        # يمين: الفورم
        right_frame = ttk.LabelFrame(main, text="تحديث الدفعة", padding=10)
        right_frame.pack(side="right", fill="y", padx=5)
        
        ttk.Label(right_frame, text="المدفوع :\u200f").pack(anchor="ne")
        ttk.Entry(right_frame, textvariable=self.var_paid).pack(fill="x", pady=5)
        
        ttk.Label(right_frame, text="الحالة :").pack(anchor="ne")
        ttk.Combobox(right_frame, textvariable=self.var_status, values=["غير مدفوع", "مدفوع جزئياً", "مدفوع بالكامل"]).pack(fill="x", pady=5)
        
        ttk.Label(right_frame, text="التاريخ :\u200f").pack(anchor="ne")
        de = DateEntry(right_frame, dateformat='%Y-%m-%d')
        de.entry.configure(textvariable=self.var_date)
        de.pack(fill="x", pady=5)
        
        ttk.Label(right_frame, text="ملاحظات :\u200f").pack(anchor="ne")
        self.txt_notes = tk.Text(right_frame, height=4, width=25)
        self.txt_notes.pack(fill="x", pady=5)
        
        ttk.Button(right_frame, text="حفظ التعديل", command=self.save_payment, bootstyle="warning").pack(fill="x", pady=10)

        # يسار: الجدول
        left_frame = ttk.Frame(main)
        left_frame.pack(side="left", fill="both", expand=True)
        
        # بحث
        filter_frame = ttk.Frame(left_frame)
        filter_frame.pack(fill="x", pady=5)
        ttk.Label(filter_frame, text="بحث اسم :\u200f").pack(side="right", padx=5)
        entry_search = ttk.Entry(filter_frame, textvariable=self.filter_name)
        entry_search.pack(side="right", padx=5)
        entry_search.bind("<Return>", lambda e: self.load_payments())
        ttk.Button(filter_frame, text="بحث", command=self.load_payments).pack(side="right", padx=5)

        cols = ("id", "sid", "name", "req", "paid", "rem", "stat")
        self.tree = ttk.Treeview(left_frame, columns=cols, show="headings")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("sid", text="رقم الطالب")
        self.tree.heading("name", text="الاسم")
        self.tree.heading("req", text="المطلوب")
        self.tree.heading("paid", text="المدفوع")
        self.tree.heading("rem", text="المتبقي")
        self.tree.heading("stat", text="الحالة")
        
        self.tree.column("id", width=40); self.tree.column("sid", width=60)
        self.tree.column("name", width=150); self.tree.column("req", width=80)
        self.tree.column("paid", width=80); self.tree.column("rem", width=80)
        
        # RTL
        self.tree["displaycolumns"] = ("stat", "rem", "paid", "req", "name", "sid", "id")
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # شريط المجاميع
        sum_frame = ttk.Frame(left_frame, padding=5)
        sum_frame.pack(fill="x")
        
        def add_sum(lbl, var):
            f = ttk.Frame(sum_frame); f.pack(side="right", padx=10)
            ttk.Label(f, text=lbl, font=("", 10, "bold")).pack(side="right")
            ttk.Label(f, textvariable=var, bootstyle="inverse-info").pack(side="right", padx=5)

        add_sum("المطلوب :\u200f", self.total_req)
        add_sum("المدفوع :\u200f", self.total_paid)
        add_sum("المتبقي :\u200f", self.total_rem)

    def create_monthly_payments(self):
        try:
            m, y = int(self.var_month.get()), int(self.var_year.get())
            cur = self.conn.cursor()
            # جلب الطلاب وكفالاتهم
            cur.execute("""
                SELECT s.id, COALESCE(sp.monthly_amount, 0) 
                FROM students s
                LEFT JOIN student_sponsorships sp ON s.id = sp.student_id
            """)
            students = cur.fetchall()
            
            count = 0
            for sid, amount in students:
                # التحقق هل الدفعة موجودة
                cur.execute("SELECT id FROM student_payments WHERE student_id=? AND month=? AND year=?", (sid, m, y))
                if not cur.fetchone():
                    cur.execute("""
                        INSERT INTO student_payments (student_id, month, year, required_amount, paid_amount, status)
                        VALUES (?, ?, ?, ?, 0, 'غير مدفوع')
                    """, (sid, m, y, amount))
                    count += 1
            
            self.conn.commit()
            self.load_payments()
            messagebox.showinfo("تم", f"تم إنشاء {count} دفعات جديدة لشهر {m}/{y}")
        except Exception as e:
            messagebox.showerror("خطأ", str(e))

    def load_payments(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        try:
            m, y = int(self.var_month.get()), int(self.var_year.get())
            name_filter = f"%{self.filter_name.get()}%"
            
            cur = self.conn.cursor()
            cur.execute("""
                SELECT p.id, s.id, s.name, p.required_amount, p.paid_amount, p.status
                FROM student_payments p
                JOIN students s ON s.id = p.student_id
                WHERE p.month=? AND p.year=? AND s.name LIKE ?
            """, (m, y, name_filter))
            
            req_sum = paid_sum = rem_sum = 0
            
            for row in cur.fetchall():
                pid, sid, name, req, paid, stat = row
                req = req or 0; paid = paid or 0
                rem = req - paid
                
                req_sum += req; paid_sum += paid; rem_sum += rem
                
                self.tree.insert("", "end", values=(pid, sid, name, req, paid, rem, stat))
            
            sym = get_currency_symbol()
            self.total_req.set(f"{req_sum:,.0f} {sym}")
            self.total_paid.set(f"{paid_sum:,.0f} {sym}")
            self.total_rem.set(f"{rem_sum:,.0f} {sym}")
            
        except Exception as e:
            print(e)

    def on_select(self, e):
        sel = self.tree.selection()
        if not sel: return
        val = self.tree.item(sel[0])['values']
        # values: id, sid, name, req, paid, rem, stat
        pid = val[0]
        self.var_pid.set(pid)
        self.var_paid.set(val[4])
        self.var_status.set(val[6])
        
        cur = self.conn.cursor()
        cur.execute("SELECT payment_date, notes FROM student_payments WHERE id=?", (pid,))
        r = cur.fetchone()
        if r:
            self.var_date.set(r[0] or "")
            self.txt_notes.delete("1.0", "end")
            self.txt_notes.insert("1.0", r[1] or "")

    def save_payment(self):
        if not self.var_pid.get(): return
        try:
            paid = float(self.var_paid.get() or 0)
            stat = self.var_status.get()
            date = self.var_date.get()
            notes = self.txt_notes.get("1.0", "end").strip()
            
            self.conn.execute("""
                UPDATE student_payments SET paid_amount=?, status=?, payment_date=?, notes=? WHERE id=?
            """, (paid, stat, date, notes, self.var_pid.get()))
            self.conn.commit()
            self.load_payments()
            messagebox.showinfo("تم", "تم تحديث الدفعة")
        except Exception as e:
            messagebox.showerror("خطأ", str(e))