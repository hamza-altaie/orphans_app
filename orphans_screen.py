# orphans_screen.py
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from typing import Optional, Tuple
from tkcalendar import DateEntry

# قائمة محافظات العراق
GOVERNORATES = [
    "",
    "بغداد",
    "نينوى",
    "البصرة",
    "النجف",
    "كربلاء",
    "الأنبار",
    "ديالى",
    "صلاح الدين",
    "واسط",
    "ميسان",
    "ذي قار",
    "المثنى",
    "بابل",
    "كركوك",
    "دهوك",
    "أربيل",
    "السليمانية",
    "القادسية",
]


class OrphansScreen(ttk.Frame):
    def __init__(self, parent, conn: sqlite3.Connection):
        super().__init__(parent)

        self.conn = conn

        # تقسيم الفريم إلى عمودين: يسار (قائمة الأيتام) + يمين (الفورم)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=3)   # الجدول
        self.columnconfigure(1, weight=2)   # الفورم

        # متغيرات بيانات اليتيم
        self.var_id = tk.StringVar()
        self.var_name = tk.StringVar()
        self.var_gender = tk.StringVar()
        self.var_age = tk.StringVar()
        self.var_governorate = tk.StringVar()
        self.var_address = tk.StringVar()
        self.var_guardian_name = tk.StringVar()
        self.var_guardian_phone = tk.StringVar()
        self.var_status = tk.StringVar(value="فعّال")

        # متغيرات بيانات الكفالة
        self.var_monthly_amount = tk.StringVar()
        self.var_sponsorship_status = tk.StringVar(value="فعّالة")
        self.var_sponsorship_start = tk.StringVar()

        self.create_widgets()
        self.load_orphans()

    # ==========================
    #   دوال مساعدة لمحاذاة Text
    # ==========================
    def _apply_right_tag(self, text_widget: tk.Text):
        """محاذاة النص في Text لليمين باستخدام tag (بدل justify)."""
        text_widget.tag_configure("right", justify="right")
        text_widget.tag_add("right", "1.0", "end")

    # ======== دوال التحقق من الأرقام ========
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
        """إنشاء الواجهات (الجدول + الفورم)"""

        # ستايل للـ Treeview
        style = ttk.Style(self)
        style.configure("Orphans.Treeview", rowheight=28)

        # ====== يسار: قائمة الأيتام ======
        table_frame = ttk.LabelFrame(
            self, text="قائمة الأيتام", padding=5, labelanchor="ne"
        )
        table_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # شريط تمرير
        self.tree_scroll_y = ttk.Scrollbar(table_frame, orient="vertical")
        self.tree_scroll_y.pack(side="right", fill="y")

        # جدول الأيتام (نعرضه من اليمين لليسار باستخدام displaycolumns)
        self.tree = ttk.Treeview(
            table_frame,
            columns=("id", "name", "age", "governorate", "status", "monthly_amount"),
            show="headings",
            displaycolumns=("monthly_amount", "status", "governorate", "age", "name", "id"),
            yscrollcommand=self.tree_scroll_y.set,
            style="Orphans.Treeview",
        )
        self.tree.pack(expand=True, fill="both")

        self.tree_scroll_y.config(command=self.tree.yview)

        # عناوين الأعمدة
        self.tree.heading("id", text="الرقم")
        self.tree.heading("name", text="الاسم")
        self.tree.heading("age", text="العمر")
        self.tree.heading("governorate", text="المحافظة")
        self.tree.heading("status", text="حالة اليتيم")
        self.tree.heading("monthly_amount", text="المبلغ الشهري")

        # حجم الأعمدة
        self.tree.column("id", width=60, anchor="center")
        self.tree.column("name", width=180, anchor="center")
        self.tree.column("age", width=60, anchor="center")
        self.tree.column("governorate", width=100, anchor="center")
        self.tree.column("status", width=80, anchor="center")
        self.tree.column("monthly_amount", width=100, anchor="center")

        # حدث اختيار صف
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # ====== يمين: نموذج بيانات اليتيم والكفالة ======
        form_frame = ttk.LabelFrame(
            self, text="بيانات اليتيم والكفالة", padding=10, labelanchor="ne"
        )
        form_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)

        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=0)

        row_idx = 0

        # أوامر التحقق للأرقام
        vcmd_int = (self.register(self._validate_int), "%P")
        vcmd_float = (self.register(self._validate_float), "%P")

        def add_row(label_text: str, widget):
            """يضيف حقل + عنوانه في صف واحد، مع النقطتين بعد النص."""
            nonlocal row_idx
            widget.grid(row=row_idx, column=0, sticky="w", pady=4, padx=(0, 5))
            ttk.Label(form_frame, text=label_text + " :\u200f").grid(
                row=row_idx, column=1, sticky="e", pady=4, padx=(5, 0)
            )
            row_idx += 1

        # رقم اليتيم (قراءة فقط)
        entry_id = ttk.Entry(
            form_frame, textvariable=self.var_id, state="readonly", width=10, justify="right"
        )
        add_row("رقم اليتيم", entry_id)

        # الاسم الثلاثي
        entry_name = ttk.Entry(
            form_frame, textvariable=self.var_name, width=35, justify="right"
        )
        add_row("الاسم الثلاثي", entry_name)

        # الجنس
        gender_combo = ttk.Combobox(
            form_frame,
            textvariable=self.var_gender,
            values=["", "ذكر", "أنثى"],
            width=12,
            state="readonly",
            justify="right",
        )
        gender_combo.current(0)
        add_row("الجنس", gender_combo)

        # العمر (أرقام فقط)
        entry_age = ttk.Entry(
            form_frame,
            textvariable=self.var_age,
            width=10,
            justify="right",
            validate="key",
            validatecommand=vcmd_int,
        )
        add_row("العمر (بالسنوات)", entry_age)

        # المحافظة - قائمة منسدلة
        gov_combo = ttk.Combobox(
            form_frame,
            textvariable=self.var_governorate,
            values=GOVERNORATES,
            width=20,
            state="readonly",
            justify="right",
        )
        gov_combo.current(0)
        add_row("المحافظة", gov_combo)

        # العنوان الكامل
        entry_address = ttk.Entry(
            form_frame, textvariable=self.var_address, width=35, justify="right"
        )
        add_row("العنوان الكامل", entry_address)

        # اسم ولي الأمر
        entry_guard_name = ttk.Entry(
            form_frame, textvariable=self.var_guardian_name, width=35, justify="right"
        )
        add_row("اسم ولي الأمر", entry_guard_name)

        # هاتف ولي الأمر (أرقام فقط)
        entry_guard_phone = ttk.Entry(
            form_frame,
            textvariable=self.var_guardian_phone,
            width=20,
            justify="right",
            validate="key",
            validatecommand=vcmd_int,
        )
        add_row("هاتف ولي الأمر", entry_guard_phone)

        # حالة اليتيم
        status_combo = ttk.Combobox(
            form_frame,
            textvariable=self.var_status,
            values=["فعّال", "موقوف", "منسحب"],
            width=12,
            state="readonly",
            justify="right",
        )
        status_combo.current(0)
        add_row("حالة اليتيم", status_combo)

        # ملاحظات عامة
        self.notes_text = tk.Text(form_frame, width=35, height=3, wrap="word")
        self.notes_text.grid(row=row_idx, column=0, sticky="w", pady=4, padx=(0, 5))
        self._apply_right_tag(self.notes_text)
        self.notes_text.bind(
            "<KeyRelease>", lambda e: self._apply_right_tag(self.notes_text)
        )
        ttk.Label(form_frame, text="ملاحظات (عن الوضع العام) :\u200f").grid(
            row=row_idx, column=1, sticky="e", pady=4, padx=(5, 0)
        )
        row_idx += 1

        # فاصل
        ttk.Separator(form_frame, orient="horizontal").grid(
            row=row_idx, column=0, columnspan=2, sticky="ew", pady=10
        )
        row_idx += 1

        ttk.Label(form_frame, text="بيانات الكفالة", font=("Arial", 10, "bold")).grid(
            row=row_idx, column=1, columnspan=2, sticky="e", pady=(0, 5)
        )
        row_idx += 1

        # المبلغ الشهري (رقم عشري)
        entry_amount = ttk.Entry(
            form_frame,
            textvariable=self.var_monthly_amount,
            width=12,
            justify="right",
            validate="key",
            validatecommand=vcmd_float,
        )
        add_row("المبلغ الشهري", entry_amount)

        # تاريخ بدء الكفالة - مع تقويم
        entry_start = DateEntry(
            form_frame,
            textvariable=self.var_sponsorship_start,
            width=15,
            justify="right",
            date_pattern="yyyy-mm-dd",   # شكل التاريخ اللي ينحفظ بالنص
        )
        add_row("تاريخ بدء الكفالة", entry_start)

        # حالة الكفالة
        sponsorship_status_combo = ttk.Combobox(
            form_frame,
            textvariable=self.var_sponsorship_status,
            values=["فعّالة", "موقوفة", "منتهية"],
            width=12,
            state="readonly",
            justify="right",
        )
        sponsorship_status_combo.current(0)
        add_row("حالة الكفالة", sponsorship_status_combo)

        # ملاحظات الكفالة
        self.sponsorship_notes_text = tk.Text(
            form_frame, width=35, height=3, wrap="word"
        )
        self.sponsorship_notes_text.grid(
            row=row_idx, column=0, sticky="w", pady=4, padx=(0, 5)
        )
        self._apply_right_tag(self.sponsorship_notes_text)
        self.sponsorship_notes_text.bind(
            "<KeyRelease>", lambda e: self._apply_right_tag(self.sponsorship_notes_text)
        )
        ttk.Label(form_frame, text="ملاحظات الكفالة :\u200f").grid(
            row=row_idx, column=1, sticky="e", pady=4, padx=(5, 0)
        )
        row_idx += 1

        # أزرار التحكم
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=row_idx, column=0, columnspan=2, pady=15)

        ttk.Button(btn_frame, text="جديد", width=10, command=self.clear_form).grid(
            row=0, column=0, padx=5
        )
        ttk.Button(
            btn_frame, text="حفظ", width=10, command=self.save_orphan_and_sponsorship
        ).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="حذف", width=10, command=self.delete_orphan).grid(
            row=0, column=2, padx=5
        )

    # ==========================
    #   عمليات قاعدة البيانات
    # ==========================

    def load_orphans(self):
        """تحميل الأيتام مع بيانات الكفالة إلى الجدول"""
        for row in self.tree.get_children():
            self.tree.delete(row)

        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT
                o.id,
                o.name,
                o.age,
                o.governorate,
                o.status,
                COALESCE(s.monthly_amount, 0)
            FROM orphans o
            LEFT JOIN sponsorships s
                ON o.id = s.orphan_id
                AND (s.status = 'فعّالة' OR s.status IS NULL)
            ORDER BY o.id ASC
            """
        )
        for row in cursor.fetchall():
            self.tree.insert("", tk.END, values=row)

    def get_orphan_by_id(self, orphan_id: int) -> Optional[Tuple]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM orphans WHERE id = ?", (orphan_id,))
        return cursor.fetchone()

    def get_sponsorship_by_orphan(self, orphan_id: int) -> Optional[Tuple]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, orphan_id, monthly_amount, start_date, status, notes
            FROM sponsorships
            WHERE orphan_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (orphan_id,),
        )
        return cursor.fetchone()

    def insert_orphan(self, data: dict) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO orphans
                (name, gender, age, governorate, address,
                 guardian_name, guardian_phone, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["name"],
                data["gender"],
                data["age"],
                data["governorate"],
                data["address"],
                data["guardian_name"],
                data["guardian_phone"],
                data["status"],
                data["notes"],
            ),
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_orphan(self, orphan_id: int, data: dict):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE orphans
            SET name = ?, gender = ?, age = ?, governorate = ?, address = ?,
                guardian_name = ?, guardian_phone = ?, status = ?, notes = ?
            WHERE id = ?
            """,
            (
                data["name"],
                data["gender"],
                data["age"],
                data["governorate"],
                data["address"],
                data["guardian_name"],
                data["guardian_phone"],
                data["status"],
                data["notes"],
                orphan_id,
            ),
        )
        self.conn.commit()

    def insert_or_update_sponsorship(self, orphan_id: int, data: dict):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id FROM sponsorships WHERE orphan_id = ? ORDER BY id DESC LIMIT 1",
            (orphan_id,),
        )
        row = cursor.fetchone()
        if row:
            sponsorship_id = row[0]
            cursor.execute(
                """
                UPDATE sponsorships
                SET monthly_amount = ?, start_date = ?, status = ?, notes = ?
                WHERE id = ?
                """,
                (
                    data["monthly_amount"],
                    data["start_date"],
                    data["status"],
                    data["notes"],
                    sponsorship_id,
                ),
            )
        else:
            cursor.execute(
                """
                INSERT INTO sponsorships
                    (orphan_id, monthly_amount, start_date, status, notes)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    orphan_id,
                    data["monthly_amount"],
                    data["start_date"],
                    data["status"],
                    data["notes"],
                ),
            )
        self.conn.commit()

    def delete_orphan_db(self, orphan_id: int):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM payments WHERE orphan_id = ?", (orphan_id,))
        cursor.execute("DELETE FROM sponsorships WHERE orphan_id = ?", (orphan_id,))
        cursor.execute("DELETE FROM orphans WHERE id = ?", (orphan_id,))
        self.conn.commit()

    # ==========================
    #   منطق الواجهة
    # ==========================

    def clear_form(self):
        """تفريغ حقول الفورم"""
        self.var_id.set("")
        self.var_name.set("")
        self.var_gender.set("")
        self.var_age.set("")
        self.var_governorate.set("")
        self.var_address.set("")
        self.var_guardian_name.set("")
        self.var_guardian_phone.set("")
        self.var_status.set("فعّال")
        self.notes_text.delete("1.0", tk.END)

        self.var_monthly_amount.set("")
        self.var_sponsorship_status.set("فعّالة")
        self.var_sponsorship_start.set("")
        self.sponsorship_notes_text.delete("1.0", tk.END)

        self.tree.selection_remove(self.tree.selection())

    def form_orphan_data(self) -> Optional[dict]:
        """قراءة بيانات اليتيم من الفورم"""
        name = self.var_name.get().strip()
        if not name:
            messagebox.showwarning("تنبيه", "حقل الاسم الثلاثي مطلوب.")
            return None

        age_str = self.var_age.get().strip()
        age_val: Optional[int] = None
        if age_str:
            if not age_str.isdigit():
                messagebox.showwarning("تنبيه", "حقل العمر يجب أن يكون رقماً صحيحاً.")
                return None
            age_val = int(age_str)

        data = {
            "name": name,
            "gender": self.var_gender.get().strip(),
            "age": age_val,
            "governorate": self.var_governorate.get().strip(),
            "address": self.var_address.get().strip(),
            "guardian_name": self.var_guardian_name.get().strip(),
            "guardian_phone": self.var_guardian_phone.get().strip(),
            "status": self.var_status.get().strip() or "فعّال",
            "notes": self.notes_text.get("1.0", tk.END).strip(),
        }
        return data

    def form_sponsorship_data(self) -> Optional[dict]:
        """قراءة بيانات الكفالة من الفورم (اختياري)"""
        amount_str = self.var_monthly_amount.get().strip()
        start_date = self.var_sponsorship_start.get().strip()
        status = self.var_sponsorship_status.get().strip() or "فعّالة"
        notes = self.sponsorship_notes_text.get("1.0", tk.END).strip()

        if not amount_str and not start_date and not notes:
            # لا توجد بيانات كفالة مدخلة
            return None

        try:
            amount_val = float(amount_str) if amount_str else 0.0
        except ValueError:
            messagebox.showwarning("تنبيه", "المبلغ الشهري يجب أن يكون رقمياً.")
            return None

        data = {
            "monthly_amount": amount_val,
            "start_date": start_date,
            "status": status,
            "notes": notes,
        }
        return data

    def save_orphan_and_sponsorship(self):
        """حفظ أو تحديث اليتيم مع بيانات الكفالة"""
        orphan_data = self.form_orphan_data()
        if not orphan_data:
            return

        sponsorship_data = self.form_sponsorship_data()
        orphan_id_str = self.var_id.get().strip()

        try:
            if orphan_id_str:
                orphan_id = int(orphan_id_str)
                self.update_orphan(orphan_id, orphan_data)
            else:
                orphan_id = self.insert_orphan(orphan_data)
                self.var_id.set(str(orphan_id))

            if sponsorship_data is not None:
                self.insert_or_update_sponsorship(orphan_id, sponsorship_data)

            self.load_orphans()
            messagebox.showinfo("نجاح", "تم حفظ بيانات اليتيم والكفالة بنجاح.")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء الحفظ:\n{e}")

    def delete_orphan(self):
        """حذف يتيم محدد"""
        orphan_id_str = self.var_id.get().strip()
        if not orphan_id_str:
            messagebox.showwarning("تنبيه", "لم يتم اختيار أي يتيم للحذف.")
            return

        confirm = messagebox.askyesno(
            "تأكيد الحذف", "هل أنت متأكد من حذف هذا اليتيم وجميع بيانات كفالته؟"
        )
        if not confirm:
            return

        try:
            self.delete_orphan_db(int(orphan_id_str))
            self.load_orphans()
            self.clear_form()
            messagebox.showinfo("نجاح", "تم حذف اليتيم وبيانات الكفالة المرتبطة به.")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء الحذف:\n{e}")

    def on_tree_select(self, event):
        """عند اختيار يتيم من الجدول تحميل بياناته في الفورم"""
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0])
        orphan_id = item["values"][0]

        row = self.get_orphan_by_id(int(orphan_id))
        if not row:
            return

        # row = (id, name, gender, age, governorate, address,
        #        guardian_name, guardian_phone, status, notes)
        self.var_id.set(row[0])
        self.var_name.set(row[1])
        self.var_gender.set(row[2] or "")
        self.var_age.set(str(row[3]) if row[3] is not None else "")
        self.var_governorate.set(row[4] or "")
        self.var_address.set(row[5] or "")
        self.var_guardian_name.set(row[6] or "")
        self.var_guardian_phone.set(row[7] or "")
        self.var_status.set(row[8] or "فعّال")
        self.notes_text.delete("1.0", tk.END)
        self.notes_text.insert("1.0", row[9] or "")
        self._apply_right_tag(self.notes_text)

        sponsorship = self.get_sponsorship_by_orphan(int(orphan_id))
        if sponsorship:
            # sponsorship = (id, orphan_id, monthly_amount, start_date, status, notes)
            self.var_monthly_amount.set(
                str(sponsorship[2]) if sponsorship[2] is not None else ""
            )
            self.var_sponsorship_start.set(sponsorship[3] or "")
            self.var_sponsorship_status.set(sponsorship[4] or "فعّالة")
            self.sponsorship_notes_text.delete("1.0", tk.END)
            self.sponsorship_notes_text.insert("1.0", sponsorship[5] or "")
            self._apply_right_tag(self.sponsorship_notes_text)
        else:
            self.var_monthly_amount.set("")
            self.var_sponsorship_start.set("")
            self.var_sponsorship_status.set("فعّالة")
            self.sponsorship_notes_text.delete("1.0", tk.END)
            self._apply_right_tag(self.sponsorship_notes_text)
