# orphans_screen.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from typing import Optional, Tuple
from ttkbootstrap.widgets import DateEntry

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

        # متغيرات الفلترة / البحث
        self.filter_name = tk.StringVar()
        self.filter_governorate = tk.StringVar()
        self.filter_status = tk.StringVar()

        self.create_widgets()
        self.load_orphans()

    # ==========================
    #   دوال مساعدة
    # ==========================
    def _apply_right_tag(self, text_widget: tk.Text):
        """محاذاة النص في Text لليمين باستخدام tag (بدل justify)."""
        text_widget.tag_configure("right", justify="right")
        text_widget.tag_add("right", "1.0", "end")

    def _fmt_amount(self, value) -> str:
        """تنسيق مبلغ (للمبلغ الشهري عند التصدير)."""
        if value is None:
            return "0"
        try:
            v = float(value)
        except (TypeError, ValueError):
            return str(value)
        if v.is_integer():
            return str(int(v))
        return f"{v:.2f}"
    

    def _validate_int(self, value: str) -> bool:
        """السماح فقط بأرقام صحيحة أو فراغ في حقل العمر."""
        return value == "" or value.isdigit()


    # ==========================
    #   الواجهة
    # ==========================

    def create_widgets(self):
        """إنشاء الواجهات (الجدول + الفورم)"""

        # أوامر تحقق للأرقام (مثلاً للعمر)
        vcmd_int = (self.register(self._validate_int), "%P")

        # ستايل للـ Treeview
        style = ttk.Style(self)
        style.configure("Orphans.Treeview", rowheight=28)

        # ====== يسار: قائمة الأيتام ======
        table_frame = ttk.LabelFrame(
            self, text="قائمة الأيتام", padding=5, labelanchor="ne", style="Card.TLabelframe"
        )
        table_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # ----- شريط البحث والفلترة فوق الجدول -----
        search_frame = ttk.Frame(table_frame)
        search_frame.pack(fill="x", padx=5, pady=(0, 5))

        search_frame.columnconfigure(0, weight=1)

        # بحث بالاسم
        ttk.Label(search_frame, text="بحث بالاسم (يحتوي على):\u200f").grid(
            row=0, column=3, sticky="e", padx=3, pady=2
        )
        entry_search_name = ttk.Entry(
            search_frame,
            textvariable=self.filter_name,
            width=20,
            justify="right",
        )
        entry_search_name.grid(row=0, column=2, sticky="e", padx=3, pady=2)

        # المحافظة
        ttk.Label(search_frame, text="المحافظة:\u200f").grid(
            row=1, column=3, sticky="e", padx=3, pady=2
        )
        combo_filter_gov = ttk.Combobox(
            search_frame,
            textvariable=self.filter_governorate,
            values=GOVERNORATES,
            width=18,
            state="readonly",
            justify="right",
        )
        combo_filter_gov.grid(row=1, column=2, sticky="e", padx=3, pady=2)
        combo_filter_gov.current(0)

        # حالة اليتيم
        ttk.Label(search_frame, text="حالة اليتيم:\u200f").grid(
            row=1, column=1, sticky="e", padx=3, pady=2
        )
        combo_filter_status = ttk.Combobox(
            search_frame,
            textvariable=self.filter_status,
            values=["", "فعّال", "موقوف", "منسحب"],
            width=14,
            state="readonly",
            justify="right",
        )
        combo_filter_status.grid(row=1, column=0, sticky="e", padx=3, pady=2)
        combo_filter_status.current(0)

        # أزرار الفلترة
        btn_apply_filter = ttk.Button(
            search_frame,
            text="تطبيق الفلترة",
            width=15,
            command=self.apply_filters,
        )
        btn_apply_filter.grid(row=0, column=0, sticky="w", padx=3, pady=2)

        btn_clear_filter = ttk.Button(
            search_frame,
            text="مسح الفلترة",
            width=15,
            command=self.clear_filters,
        )
        btn_clear_filter.grid(row=0, column=1, sticky="w", padx=3, pady=2)

        # Enter في حقل الاسم = تطبيق الفلترة
        entry_search_name.bind("<Return>", lambda e: self.apply_filters())

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
        self.tree.heading("id", text="رقم الييم")
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

        # ---- أزرار التصدير تحت الجدول ----
        export_frame = ttk.Frame(table_frame)
        export_frame.pack(fill="x", padx=5, pady=(5, 0))

        btn_excel = ttk.Button(
            export_frame,
            text="Excel تصدير الأيتام إلى",
            width=22,
            command=self.export_to_excel,
        )
        btn_excel.pack(side="right", padx=(5, 0))

        btn_pdf = ttk.Button(
            export_frame,
            text="PDF تصدير الأيتام إلى",
            width=22,
            command=self.export_to_pdf,
        )
        btn_pdf.pack(side="right", padx=(5, 0))

        # ====== يمين: نموذج بيانات اليتيم والكفالة ======
        form_frame = ttk.LabelFrame(
            self, text="بيانات اليتيم والكفالة", padding=10, labelanchor="ne", style="Card.TLabelframe"
        )

        form_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)

        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=0)

        row_idx = 0

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
        add_row("رقم الملف", entry_id)

        # الاسم الثلاثي
        entry_name = tk.Entry(
            form_frame, 
            textvariable=self.var_name, 
            width=35, 
            justify="right", 
            font=("Arial", 11)
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

        # العمر
        entry_age = ttk.Entry(
            form_frame,
            textvariable=self.var_age,
            width=10,
            justify="right",
            validate="key",
            validatecommand=vcmd_int,  # يسمح فقط بالأرقام أو فراغ
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

        # هاتف ولي الأمر
        entry_guard_phone = ttk.Entry(
            form_frame,
            textvariable=self.var_guardian_phone,
            width=20,
            justify="right",
            validate="key",
            validatecommand=vcmd_int,   # ⬅️ أرقام فقط
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

        # المبلغ الشهري
        entry_amount = ttk.Entry(
            form_frame,
            textvariable=self.var_monthly_amount,
            width=12,
            justify="right",
            validate="key",
            validatecommand=vcmd_int,   # ⬅️ أرقام فقط
        )
        add_row("المبلغ الشهري", entry_amount)

        # تاريخ بدء الكفالة - باستخدام تقويم ttkbootstrap
        # لاحظ: غيرنا date_pattern إلى dateformat واستخدمنا صيغة %Y-%m-%d
        entry_start = DateEntry(
            form_frame,
            width=15,
            dateformat='%Y-%m-%d',
        )
        # نربط المتغير والنص لليمين يدوياً لأن DateEntry هنا عبارة عن حاوية
        entry_start.entry.configure(textvariable=self.var_sponsorship_start, justify="right")
        
        # نستخدم pack أو grid للحاوية نفسها
        # لاحظ: الدالة add_row تتوقع widget، لذا سنمرر لها entry_start
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
        """تحميل الأيتام مع بيانات الكفالة إلى الجدول (مع تطبيق الفلترة إن وجدت)"""
        for row in self.tree.get_children():
            self.tree.delete(row)

        cursor = self.conn.cursor()

        query = """
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
            WHERE 1=1
        """
        params = []

        # تطبيق الفلاتر
        name_filter = self.filter_name.get().strip()
        gov_filter = self.filter_governorate.get().strip()
        status_filter = self.filter_status.get().strip()

        if name_filter:
            query += " AND o.name LIKE ?"
            params.append(f"%{name_filter}%")

        if gov_filter:
            query += " AND o.governorate = ?"
            params.append(gov_filter)

        if status_filter:
            query += " AND o.status = ?"
            params.append(status_filter)

        query += " ORDER BY o.id ASC"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        # التعديل: نستخدم enumerate لعمل عداد (i) يبدأ من 1
        for i, row in enumerate(rows, start=1):
            real_id = row[0]  # هذا هو الـ ID الحقيقي من قاعدة البيانات
            
            # نجهز القيم للعرض: نضع العداد (i) في أول عمود بدلاً من الـ ID الحقيقي
            # row[1] هو الاسم، row[2] العمر... إلخ
            display_values = (i, row[1], row[2], row[3], row[4], row[5])
            
            # نستخدم real_id كمعرف للصف (iid) لنسترجعه عند النقر
            self.tree.insert("", tk.END, iid=str(real_id), values=display_values)

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

    def apply_filters(self):
        """تطبيق قيم البحث/الفلترة الحالية على الجدول"""
        self.load_orphans()

    def clear_filters(self):
        """مسح الفلاتر وإعادة تحميل كل الأيتام"""
        self.filter_name.set("")
        self.filter_governorate.set("")
        self.filter_status.set("")
        self.load_orphans()

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

        # التعديل: الـ orphan_id الآن هو نفسه الـ selected[0] لأننا خزنناه في الـ iid
        orphan_id = selected[0]

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

        # ==========================
    #   التصدير إلى Excel / PDF
    # ==========================

    def _collect_current_rows(self):
        """جمع الصفوف الظاهرة حالياً في جدول الأيتام."""
        rows = []
        for iid in self.tree.get_children():
            values = self.tree.item(iid)["values"]
            if values:
                # (id, name, age, governorate, status, monthly_amount)
                rows.append(values)
        return rows

    def export_to_excel(self):
        rows = self._collect_current_rows()
        if not rows:
            messagebox.showinfo("معلومة", "لا توجد بيانات في الجدول للتصدير.")
            return

        try:
            from openpyxl import Workbook
            from openpyxl.styles import Alignment, Font
        except ImportError:
            messagebox.showerror(
                "خطأ",
                "مكتبة openpyxl غير مثبتة.\n\nرجاءً نفّذ الأمر التالي داخل بيئة المشروع:\n\npip install openpyxl",
            )
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("ملفات Excel", "*.xlsx")],
            initialfile="تقرير_الأيتام.xlsx",
            title="حفظ تقرير الأيتام كملف Excel",
        )
        if not file_path:
            return

        wb = Workbook()
        ws = wb.active
        ws.title = "الأيتام"

        headers = ["رقم اليتيم", "الاسم", "العمر", "المحافظة",
                   "حالة اليتيم", "المبلغ الشهري"]

        ws.append(headers)

        total_monthly = 0.0

        for (oid, name, age, gov, status, monthly) in rows:
            try:
                m_val = float(monthly or 0)
            except ValueError:
                m_val = 0.0
            total_monthly += m_val

            ws.append([
                oid,
                name,
                age if age is not None else "",
                gov,
                status,
                m_val,
            ])

        # صف مجموع المبالغ الشهرية
        ws.append([])
        ws.append([
            "", "", "", "مجموع المبالغ الشهرية",
            "",
            total_monthly,
        ])

        align_right = Alignment(horizontal="right")
        bold_font = Font(bold=True)

        # ترويسة
        for cell in ws[1]:
            cell.font = bold_font
            cell.alignment = align_right

        # بقية الخلايا يمين
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
            for cell in row:
                cell.alignment = align_right

        # صف المجموع بولد
        for cell in ws[ws.max_row]:
            cell.font = bold_font

        try:
            wb.save(file_path)
            messagebox.showinfo("تم", "تم تصدير تقرير الأيتام إلى ملف Excel بنجاح.")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء حفظ ملف Excel:\n{e}")

    def export_to_pdf(self):
        """تصدير قائمة الأيتام الظاهرة في الجدول إلى PDF مع دعم العربية"""
        # جمع الصفوف من جدول الأيتام
        rows = []
        for iid in self.tree.get_children():
            values = self.tree.item(iid)["values"]
            # values = (id, name, age, governorate, status, monthly_amount)
            if values:
                rows.append(values)

        if not rows:
            messagebox.showinfo("معلومة", "لا توجد بيانات في الجدول للتصدير.")
            return

        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            import arabic_reshaper
            from bidi.algorithm import get_display
        except ImportError:
            messagebox.showerror(
                "خطأ",
                "مكتبات reportlab / arabic_reshaper / python-bidi غير مثبتة.\n\n"
                "رجاءً نفّذ الأمر:\n"
                "pip install reportlab arabic_reshaper python-bidi",
            )
            return

        # تسجيل خط عربي
        def register_arabic_font():
            font_paths = [
                r"C:\Windows\Fonts\arial.ttf",
                r"C:\Windows\Fonts\trado.ttf",
                r"C:\Windows\Fonts\Tahoma.ttf",
            ]
            for p in font_paths:
                try:
                    pdfmetrics.registerFont(TTFont("ArabicMain", p))
                    return "ArabicMain"
                except Exception:
                    continue
            return "Helvetica"

        font_name = register_arabic_font()

        # تجهيز النص العربي
        def ar(text: str) -> str:
            if text is None:
                return ""
            s = str(text)
            try:
                reshaped = arabic_reshaper.reshape(s)
                return get_display(reshaped)
            except Exception:
                return s

        from app_settings import get_default_export_dir
        initial_name = "تقرير_الأيتام.pdf"
        initial_dir = get_default_export_dir() or ""

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("ملفات PDF", "*.pdf")],
            initialfile=initial_name,
            initialdir=initial_dir,
            title="حفظ تقرير الأيتام كملف PDF",
        )
        if not file_path:
            return

        page_width, page_height = A4
        c = canvas.Canvas(file_path, pagesize=A4)

        # عنوان
        c.setFont(font_name, 14)
        c.drawRightString(page_width - 40, page_height - 40, ar("تقرير الأيتام"))

        # مواضع الأعمدة (من اليمين لليسار)
        y = page_height - 70
        x_id = page_width - 40
        x_name = x_id - 50
        x_age = x_name - 140
        x_gov = x_age - 50
        x_status = x_gov - 80
        x_amount = x_status - 80

        def draw_header():
            nonlocal y
            c.setFont(font_name, 9)
            c.drawRightString(x_id, y, ar("الرقم"))
            c.drawRightString(x_name, y, ar("اسم اليتيم"))
            c.drawRightString(x_age, y, ar("العمر"))
            c.drawRightString(x_gov, y, ar("المحافظة"))
            c.drawRightString(x_status, y, ar("حالة اليتيم"))
            c.drawRightString(x_amount, y, ar("المبلغ الشهري"))
            y -= 15
            c.line(40, y + 5, page_width - 40, y + 5)

        # رسم الهيدر أول مرة
        draw_header()
        c.setFont(font_name, 9)
        y -= 10

        # تعبئة الصفوف
        for (oid, name, age, gov, status, monthly_amount) in rows:
            if y < 60:
                # صفحة جديدة
                c.showPage()
                c.setFont(font_name, 14)
                c.drawRightString(page_width - 40, page_height - 40, ar("تقرير الأيتام"))
                y = page_height - 70
                draw_header()
                c.setFont(font_name, 9)
                y -= 10

            c.drawRightString(x_id, y, str(oid))
            c.drawRightString(x_name, y, ar(name))
            c.drawRightString(
                x_age, y, str(age) if age not in (None, "") else ""
            )
            c.drawRightString(x_gov, y, ar(gov))
            c.drawRightString(x_status, y, ar(status))
            c.drawRightString(x_amount, y, str(monthly_amount or 0))
            y -= 14

        c.showPage()
        try:
            c.save()
            messagebox.showinfo("تم", "تم تصدير تقرير الأيتام إلى ملف PDF بنجاح.")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء حفظ ملف PDF:\n{e}")

