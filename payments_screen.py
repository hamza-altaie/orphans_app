# payments_screen.py
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from typing import Optional, Tuple
from datetime import datetime
from tkcalendar import DateEntry


class PaymentsScreen(ttk.Frame):
    def __init__(self, parent, conn: sqlite3.Connection):
        super().__init__(parent)

        self.conn = conn

        # متغيرات عامة
        self.var_month = tk.StringVar(value=str(datetime.now().month))
        self.var_year = tk.StringVar(value=str(datetime.now().year))
        self.var_selected_payment_id = tk.StringVar()
        self.var_pay_paid = tk.StringVar()
        self.var_pay_status = tk.StringVar()
        self.var_pay_date = tk.StringVar()

        self.pay_tree = None
        self.pay_notes_text = None

        self.create_widgets()

    # ==========================
    #   دوال تحقق للأرقام
    # ==========================
    def _validate_int(self, value: str) -> bool:
        """السماح فقط بأرقام صحيحة أو فراغ."""
        return value == "" or value.isdigit()

    def _validate_float(self, value: str) -> bool:
        """السماح فقط بأرقام عشرية أو فراغ."""
        if value == "":
            return True
        try:
            float(value)
            return True
        except ValueError:
            return False

    # ==========================
    #   الواجهة
    # ==========================

    def create_widgets(self):
        # أوامر التحقق
        vcmd_int = (self.register(self._validate_int), "%P")
        vcmd_float = (self.register(self._validate_float), "%P")

        # سطر أعلى لاختيار الشهر والسنة + أزرار التحكم
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(top_frame, text="السنة:\u200f").pack(side="right", padx=(0, 5))
        entry_year = ttk.Entry(
            top_frame,
            textvariable=self.var_year,
            width=8,
            validate="key",
            validatecommand=vcmd_int,   # أرقام فقط
        )
        entry_year.pack(side="right", padx=(0, 15))

        ttk.Label(top_frame, text="الشهر:\u200f").pack(side="right", padx=(0, 5))
        combo_month = ttk.Combobox(
            top_frame,
            textvariable=self.var_month,
            values=[str(i) for i in range(1, 12 + 1)],
            width=5,
            state="readonly",
        )
        combo_month.pack(side="right", padx=(0, 15))

        ttk.Button(
            top_frame,
            text="تحميل الدفعات",
            command=self.load_payments_clicked,
            width=15,
        ).pack(side="right", padx=(0, 10))

        ttk.Button(
            top_frame,
            text="إنشاء دفعات الشهر",
            command=self.create_payments_clicked,
            width=18,
        ).pack(side="right", padx=(0, 10))

        # إطار رئيسي: يسار جدول، يمين فورم تحديث
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill="both", padx=10, pady=(0, 10))

        # يسار: جدول الدفعات
        left_frame = ttk.LabelFrame(
            main_frame,
            text="دفعات الأيتام للشهر المحدد",
            padding=5,
            labelanchor="ne",
        )
        left_frame.pack(side="left", expand=True, fill="both", padx=(0, 10))

        scroll_y = ttk.Scrollbar(left_frame, orient="vertical")
        scroll_y.pack(side="right", fill="y")

        self.pay_tree = ttk.Treeview(
            left_frame,
            columns=("id", "orphan_id", "name", "required", "paid", "remaining", "status"),
            show="headings",
            displaycolumns=("status", "remaining", "paid", "required", "name", "orphan_id"),
            yscrollcommand=scroll_y.set,
        )
        self.pay_tree.pack(expand=True, fill="both")
        scroll_y.config(command=self.pay_tree.yview)

        self.pay_tree.heading("id", text="ID")
        self.pay_tree.heading("orphan_id", text="رقم اليتيم")
        self.pay_tree.heading("name", text="اسم اليتيم")
        self.pay_tree.heading("required", text="المطلوب")
        self.pay_tree.heading("paid", text="المدفوع")
        self.pay_tree.heading("remaining", text="المتبقي")
        self.pay_tree.heading("status", text="الحالة")

        self.pay_tree.column("id", width=40, anchor="center")
        self.pay_tree.column("orphan_id", width=70, anchor="center")
        self.pay_tree.column("name", width=150, anchor="center")
        self.pay_tree.column("required", width=80, anchor="center")
        self.pay_tree.column("paid", width=80, anchor="center")
        self.pay_tree.column("remaining", width=80, anchor="center")
        self.pay_tree.column("status", width=100, anchor="center")

        # ألوان حسب الحالة
        self.pay_tree.tag_configure("unpaid", background="#ffe5e5")
        self.pay_tree.tag_configure("partial", background="#fff7cc")
        self.pay_tree.tag_configure("full", background="#e5ffe5")

        self.pay_tree.bind("<<TreeviewSelect>>", self.on_payment_select)

        # يمين: فورم تحديث الدفعة
        right_frame = ttk.LabelFrame(
            main_frame,
            text="تحديث بيانات الدفعة المحددة",
            padding=10,
            labelanchor="ne",
        )
        right_frame.pack(side="left", fill="y")

        right_frame.columnconfigure(0, weight=1)
        right_frame.columnconfigure(1, weight=0)

        row_idx = 0

        def add_row(label_text, widget):
            nonlocal row_idx
            widget.grid(row=row_idx, column=0, sticky="w", pady=4, padx=(0, 5))
            ttk.Label(right_frame, text=label_text + "\u200f").grid(
                row=row_idx, column=1, sticky="e", pady=4, padx=(5, 0)
            )
            row_idx += 1

        entry_pid = ttk.Entry(
            right_frame,
            textvariable=self.var_selected_payment_id,
            state="readonly",
            width=10,
        )
        add_row("رقم الدفعة:", entry_pid)

        entry_paid = ttk.Entry(
            right_frame,
            textvariable=self.var_pay_paid,
            width=12,
            validate="key",
            validatecommand=vcmd_float,   # مبلغ = رقم عشري فقط
        )
        add_row("المبلغ المدفوع:", entry_paid)

        combo_status = ttk.Combobox(
            right_frame,
            textvariable=self.var_pay_status,
            values=["غير مدفوع", "مدفوع جزئياً", "مدفوع بالكامل"],
            width=15,
            state="readonly",
        )
        add_row("حالة الدفعة:", combo_status)

        entry_date = DateEntry(
            right_frame,
            textvariable=self.var_pay_date,
            width=15,
            justify="right",
            date_pattern="yyyy-mm-dd",   # شكل التاريخ اللي ينخزن بالنص
        )
        add_row("تاريخ الدفع:", entry_date)

        self.pay_notes_text = tk.Text(right_frame, width=30, height=4)
        self.pay_notes_text.grid(row=row_idx, column=0, sticky="w", pady=4, padx=(0, 5))
        ttk.Label(right_frame, text="ملاحظات:\u200f").grid(
            row=row_idx, column=1, sticky="e", pady=4, padx=(5, 0)
        )
        row_idx += 1

        ttk.Button(
            right_frame,
            text="تحديث الدفعة",
            width=15,
            command=self.update_payment_clicked,
        ).grid(row=row_idx, column=0, columnspan=2, pady=10)

    # ==========================
    #   منطق الدفعات
    # ==========================

    def prepare_payments_for_month(self, year: int, month: int):
        """
        تجهيز سجلات الدفعات لهذا الشهر:
        لكل يتيم حالته فعّال وله كفالة فعّالة (إن وجدت) ننشئ سطر دفعة إن لم يكن موجوداً.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT o.id, o.name, COALESCE(s.monthly_amount, 0)
            FROM orphans o
            LEFT JOIN sponsorships s
                ON o.id = s.orphan_id
                AND (s.status = 'فعّالة' OR s.status IS NULL)
            WHERE o.status = 'فعّال'
            """
        )
        orphans = cursor.fetchall()

        for orphan_id, name, monthly_amount in orphans:
            if monthly_amount is None:
                monthly_amount = 0.0

            cursor.execute(
                """
                SELECT id FROM payments
                WHERE orphan_id = ? AND month = ? AND year = ?
                """,
                (orphan_id, month, year),
            )
            row = cursor.fetchone()
            if row:
                continue

            cursor.execute(
                """
                INSERT INTO payments
                    (orphan_id, month, year, required_amount,
                     paid_amount, status, payment_date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    orphan_id,
                    month,
                    year,
                    monthly_amount,
                    0.0,
                    "غير مدفوع",
                    "",
                    "",
                ),
            )

        self.conn.commit()

    def load_payments_for_month(self, year: int, month: int):
        """تحميل الدفعات في جدول Treeview"""
        for row in self.pay_tree.get_children():
            self.pay_tree.delete(row)

        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT
                p.id,
                o.id,
                o.name,
                p.required_amount,
                p.paid_amount,
                p.status
            FROM payments p
            JOIN orphans o ON o.id = p.orphan_id
            WHERE p.month = ? AND p.year = ?
            ORDER BY o.id ASC
            """,
            (month, year),
        )
        rows = cursor.fetchall()

        for pid, oid, name, req, paid, status in rows:
            req = req or 0.0
            paid = paid or 0.0
            remaining = req - paid

            if paid <= 0:
                tag = "unpaid"
            elif paid < req:
                tag = "partial"
            else:
                tag = "full"

            self.pay_tree.insert(
                "",
                tk.END,
                values=(pid, oid, name, req, paid, remaining, status),
                tags=(tag,),
            )

    def load_payments_clicked(self):
        month_str = self.var_month.get().strip()
        year_str = self.var_year.get().strip()

        if not month_str or not year_str:
            messagebox.showwarning("تنبيه", "يرجى اختيار الشهر والسنة.")
            return

        try:
            month = int(month_str)
            year = int(year_str)
        except ValueError:
            messagebox.showwarning("تنبيه", "الشهر والسنة يجب أن يكونا أرقاماً صحيحة.")
            return

        if not (1 <= month <= 12):
            messagebox.showwarning("تنبيه", "رقم الشهر يجب أن يكون بين 1 و 12.")
            return

        self.load_payments_for_month(year, month)

        if not self.pay_tree.get_children():
            messagebox.showinfo(
                "معلومة",
                "لا توجد دفعات لهذا الشهر.\nيمكنك الضغط على 'إنشاء دفعات الشهر' لتوليدها."
            )

    def create_payments_clicked(self):
        month_str = self.var_month.get().strip()
        year_str = self.var_year.get().strip()

        if not month_str or not year_str:
            messagebox.showwarning("تنبيه", "يرجى اختيار الشهر والسنة.")
            return

        try:
            month = int(month_str)
            year = int(year_str)
        except ValueError:
            messagebox.showwarning("تنبيه", "الشهر والسنة يجب أن يكونا أرقاماً صحيحة.")
            return

        if not (1 <= month <= 12):
            messagebox.showwarning("تنبيه", "رقم الشهر يجب أن يكون بين 1 و 12.")
            return

        try:
            self.prepare_payments_for_month(year, month)
            self.load_payments_for_month(year, month)
            messagebox.showinfo("تم", "تم إنشاء/تحديث دفعات هذا الشهر بنجاح.")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء إنشاء الدفعات:\n{e}")

    def on_payment_select(self, event):
        selected = self.pay_tree.selection()
        if not selected:
            return

        item = self.pay_tree.item(selected[0])
        pid, oid, name, req, paid, remaining, status = item["values"]

        self.var_selected_payment_id.set(str(pid))
        self.var_pay_paid.set(str(paid))
        self.var_pay_status.set(status if status else "")

        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT payment_date, notes
            FROM payments
            WHERE id = ?
            """,
            (pid,),
        )
        row = cursor.fetchone()
        if row:
            self.var_pay_date.set(row[0] or "")
            self.pay_notes_text.delete("1.0", tk.END)
            self.pay_notes_text.insert("1.0", row[1] or "")
        else:
            self.var_pay_date.set("")
            self.pay_notes_text.delete("1.0", tk.END)

    def update_payment_clicked(self):
        pid_str = self.var_selected_payment_id.get().strip()
        if not pid_str:
            messagebox.showwarning("تنبيه", "لم يتم اختيار أي دفعة لتحديثها.")
            return

        try:
            pid = int(pid_str)
        except ValueError:
            messagebox.showwarning("تنبيه", "رقم الدفعة غير صحيح.")
            return

        selected = self.pay_tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "يرجى اختيار الدفعة من الجدول أولاً.")
            return

        item = self.pay_tree.item(selected[0])
        _, _, _, req, _, _, _ = item["values"]

        paid_str = self.var_pay_paid.get().strip()
        try:
            paid = float(paid_str) if paid_str else 0.0
        except ValueError:
            messagebox.showwarning("تنبيه", "المبلغ المدفوع يجب أن يكون عدداً.")
            return

        status = self.var_pay_status.get().strip()
        if not status:
            if paid <= 0:
                status = "غير مدفوع"
            elif paid < req:
                status = "مدفوع جزئياً"
            else:
                status = "مدفوع بالكامل"

        date_str = self.var_pay_date.get().strip()
        notes = self.pay_notes_text.get("1.0", tk.END).strip()

        cursor = self.conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE payments
                SET paid_amount = ?, status = ?, payment_date = ?, notes = ?
                WHERE id = ?
                """,
                (paid, status, date_str, notes, pid),
            )
            self.conn.commit()

            month = int(self.var_month.get())
            year = int(self.var_year.get())
            self.load_payments_for_month(year, month)

            messagebox.showinfo("تم", "تم تحديث بيانات الدفعة بنجاح.")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تحديث الدفعة:\n{e}")
