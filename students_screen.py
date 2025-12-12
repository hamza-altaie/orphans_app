# students_screen.py
import tkinter as tk
from tkinter import ttk, messagebox
from ttkbootstrap.constants import *
import sqlite3
from typing import Optional

class StudentsScreen(ttk.Frame):
    def __init__(self, parent, conn: sqlite3.Connection):
        super().__init__(parent)
        self.conn = conn
        
        # تقسيم الشاشة: الجدول (يسار 0)، الفورم (يمين 1)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=3)   # الجدول
        self.columnconfigure(1, weight=2)   # الفورم

        # المتغيرات
        self.var_id = tk.StringVar()
        self.var_name = tk.StringVar()
        self.var_phone = tk.StringVar()     # رقم الهاتف
        self.var_stage = tk.StringVar()
        self.var_school = tk.StringVar()
        self.var_monthly_amount = tk.StringVar()
        
        self.search_var = tk.StringVar()

        self.create_widgets()
        self.load_students()

    # ==========================
    #   دوال مساعدة (نفس orphans_screen)
    # ==========================
    def _apply_right_tag(self, text_widget: tk.Text):
        text_widget.tag_configure("right", justify="right")
        text_widget.tag_add("right", "1.0", "end")

    def create_widgets(self):
        style = ttk.Style(self)
        style.configure("Students.Treeview", rowheight=28)

        # ====== يسار: قائمة الطلاب ======
        table_frame = ttk.LabelFrame(
            self, text="سجل الطلاب", padding=5, labelanchor="ne", style="Card.TLabelframe"
        )
        table_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # شريط البحث
        search_frame = ttk.Frame(table_frame)
        search_frame.pack(fill="x", padx=5, pady=(0, 5))

        ttk.Label(search_frame, text="بحث بالاسم :\u200f").pack(side=RIGHT, padx=5)
        entry_search = ttk.Entry(search_frame, textvariable=self.search_var, justify="right")
        entry_search.pack(side=RIGHT, padx=5)
        entry_search.bind("<Return>", lambda e: self.load_students())
        ttk.Button(search_frame, text="بحث", command=self.load_students, width=10).pack(side=RIGHT, padx=5)

        # الجدول
        self.tree_scroll_y = ttk.Scrollbar(table_frame, orient="vertical")
        self.tree_scroll_y.pack(side="right", fill="y")

        columns = ("id", "name", "phone", "stage", "amount")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            displaycolumns=("amount", "stage", "phone", "name", "id"), # RTL
            yscrollcommand=self.tree_scroll_y.set,
            style="Students.Treeview"
        )
        self.tree.pack(expand=True, fill="both")
        self.tree_scroll_y.config(command=self.tree.yview)

        self.tree.heading("id", text="رقم")
        self.tree.heading("name", text="الاسم")
        self.tree.heading("phone", text="الهاتف")
        self.tree.heading("stage", text="المرحلة")
        self.tree.heading("amount", text="الكفالة")
        
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("name", width=140, anchor="center")
        self.tree.column("phone", width=100, anchor="center")
        self.tree.column("stage", width=100, anchor="center")
        self.tree.column("amount", width=90, anchor="center")

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # ====== يمين: الفورم ======
        form_frame = ttk.LabelFrame(
            self, text="بيانات الطالب", padding=10, labelanchor="ne", style="Card.TLabelframe"
        )
        form_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        
        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=0)

        self.row_idx = 0
        def add_row(label, widget):
            nonlocal self
            widget.grid(row=self.row_idx, column=0, sticky="ew", pady=4, padx=(0, 5))
            ttk.Label(form_frame, text=label + " :\u200f").grid(row=self.row_idx, column=1, sticky="e", pady=4, padx=(5, 0))
            self.row_idx += 1

        # الحقول
        add_row("رقم الملف", ttk.Entry(form_frame, textvariable=self.var_id, state="readonly", justify="right"))
        add_row("الاسم الثلاثي", ttk.Entry(form_frame, textvariable=self.var_name, justify="right", font=("Arial", 11)))
        add_row("رقم الهاتف", ttk.Entry(form_frame, textvariable=self.var_phone, justify="right"))
        
        stages = ["الابتدائية", "المتوسطة", "الإعدادية", "جامعي"]
        cb_stage = ttk.Combobox(form_frame, textvariable=self.var_stage, values=stages, state="readonly", justify="right")
        add_row("المرحلة الدراسية", cb_stage)
        
        add_row("المدرسة/الجامعة", ttk.Entry(form_frame, textvariable=self.var_school, justify="right"))
        
        ttk.Separator(form_frame).grid(row=self.row_idx, column=0, columnspan=2, sticky="ew", pady=10)
        self.row_idx += 1
        
        add_row("مبلغ الكفالة", ttk.Entry(form_frame, textvariable=self.var_monthly_amount, justify="right"))

        # الملاحظات
        self.notes_text = tk.Text(form_frame, width=35, height=4, wrap="word")
        self.notes_text.grid(row=self.row_idx, column=0, sticky="ew", pady=4, padx=(0, 5))
        self._apply_right_tag(self.notes_text)
        self.notes_text.bind("<KeyRelease>", lambda e: self._apply_right_tag(self.notes_text))
        
        ttk.Label(form_frame, text="ملاحظات :\u200f").grid(row=self.row_idx, column=1, sticky="ne", pady=4, padx=(5, 0))
        self.row_idx += 1

        # الأزرار
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=self.row_idx, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="جديد", bootstyle="secondary", width=10, command=self.clear_form).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="حفظ", bootstyle="success", width=10, command=self.save_student).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="حذف", bootstyle="danger", width=10, command=self.delete_student).grid(row=0, column=0, padx=5)

    def load_students(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        cursor = self.conn.cursor()
        query = """
            SELECT s.id, s.name, s.phone, s.school_stage, COALESCE(sp.monthly_amount, 0), s.school_name, s.notes
            FROM students s
            LEFT JOIN student_sponsorships sp ON s.id = sp.student_id
            WHERE s.name LIKE ?
        """
        cursor.execute(query, (f"%{self.search_var.get()}%",))
        
        for i, row in enumerate(cursor.fetchall(), start=1):
            # row: 0=id, 1=name, 2=phone, 3=stage, 4=amount, 5=school, 6=notes
            # نستخدم i للعرض، و row[0] كـ ID حقيقي
            display_vals = (i, row[1], row[2], row[3], row[4])
            self.tree.insert("", "end", iid=str(row[0]), values=display_vals)

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        sid = sel[0]
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT s.id, s.name, s.phone, s.school_stage, s.school_name, s.notes, COALESCE(sp.monthly_amount, 0)
            FROM students s
            LEFT JOIN student_sponsorships sp ON s.id = sp.student_id
            WHERE s.id=?
        """, (sid,))
        
        row = cursor.fetchone()
        if row:
            self.var_id.set(row[0])
            self.var_name.set(row[1])
            self.var_phone.set(row[2] or "")
            self.var_stage.set(row[3] or "")
            self.var_school.set(row[4] or "")
            self.var_monthly_amount.set(row[6])
            
            self.notes_text.delete("1.0", tk.END)
            self.notes_text.insert("1.0", row[5] or "")
            self._apply_right_tag(self.notes_text)

    def save_student(self):
        name = self.var_name.get().strip()
        if not name:
            messagebox.showwarning("تنبيه", "الاسم مطلوب")
            return
        
        phone = self.var_phone.get()
        stage = self.var_stage.get()
        school = self.var_school.get()
        notes = self.notes_text.get("1.0", tk.END).strip()
        
        try:
            amount = float(self.var_monthly_amount.get() or 0)
        except ValueError:
            amount = 0.0

        cursor = self.conn.cursor()
        try:
            if self.var_id.get():
                # تحديث
                uid = self.var_id.get()
                cursor.execute("""
                    UPDATE students 
                    SET name=?, phone=?, school_stage=?, school_name=?, notes=? 
                    WHERE id=?
                """, (name, phone, stage, school, notes, uid))
                
                # تحديث الكفالة
                # (لتحسين الأداء يمكن التحقق من وجود سجل كفالة أولاً، هنا سنستخدم طريقة مبسطة)
                cursor.execute("SELECT id FROM student_sponsorships WHERE student_id=?", (uid,))
                if cursor.fetchone():
                    cursor.execute("UPDATE student_sponsorships SET monthly_amount=? WHERE student_id=?", (amount, uid))
                else:
                    cursor.execute("INSERT INTO student_sponsorships (student_id, monthly_amount) VALUES (?, ?)", (uid, amount))

            else:
                # جديد
                cursor.execute("""
                    INSERT INTO students (name, phone, school_stage, school_name, notes) 
                    VALUES (?, ?, ?, ?, ?)
                """, (name, phone, stage, school, notes))
                uid = cursor.lastrowid
                
                cursor.execute("INSERT INTO student_sponsorships (student_id, monthly_amount) VALUES (?, ?)", (uid, amount))
            
            self.conn.commit()
            self.load_students()
            messagebox.showinfo("تم", "تم الحفظ بنجاح")
        except Exception as e:
            messagebox.showerror("خطأ", str(e))

    def delete_student(self):
        if not self.var_id.get(): return
        if messagebox.askyesno("تأكيد", "حذف الطالب؟"):
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM students WHERE id=?", (self.var_id.get(),))
            self.conn.commit()
            self.load_students()
            self.clear_form()

    def clear_form(self):
        self.var_id.set("")
        self.var_name.set("")
        self.var_phone.set("")
        self.var_stage.set("")
        self.var_school.set("")
        self.var_monthly_amount.set("")
        self.notes_text.delete("1.0", tk.END)
        self.tree.selection_remove(self.tree.selection())