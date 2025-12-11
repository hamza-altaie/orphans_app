# students_screen.py
import tkinter as tk
from tkinter import ttk, messagebox
from ttkbootstrap.constants import *
import sqlite3

class StudentsScreen(ttk.Frame):
    def __init__(self, parent, conn: sqlite3.Connection):
        super().__init__(parent)
        self.conn = conn
        
        # مطابقة orphans_screen: الجدول يسار (0) والفورم يمين (1)
        self.columnconfigure(0, weight=3) # الجدول
        self.columnconfigure(1, weight=2) # الفورم
        self.rowconfigure(0, weight=1)

        # المتغيرات
        self.var_id = tk.StringVar()
        self.var_name = tk.StringVar()
        self.var_stage = tk.StringVar()
        self.var_school = tk.StringVar()
        self.var_monthly_amount = tk.StringVar()
        
        self.create_widgets()
        self.load_students()

    def create_widgets(self):
        # --- 1. الجدول (يسار - العمود 0) ---
        table_frame = ttk.LabelFrame(self, text="سجل الطلاب", padding=5)
        table_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # شريط بحث بسيط (مطابق للأيتام)
        search_frame = ttk.Frame(table_frame)
        search_frame.pack(fill="x", pady=5)
        
        # العناصر تضاف من اليمين لليسار (Label -> Entry -> Button)
        # لكن في orphans_screen تم استخدام Grid بترتيب معين
        ttk.Label(search_frame, text="بحث بالاسم:").pack(side=RIGHT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, justify="right")
        search_entry.pack(side=RIGHT, padx=5)
        search_entry.bind("<Return>", lambda e: self.load_students())
        ttk.Button(search_frame, text="بحث", command=self.load_students, width=10).pack(side=RIGHT, padx=5)

        # التري فيو
        columns = ("id", "name", "stage", "amount")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="primary.Treeview")
        
        self.tree.heading("id", text="رقم الطالب")
        self.tree.heading("name", text="الاسم الثلاثي")
        self.tree.heading("stage", text="المرحلة الدراسية")
        self.tree.heading("amount", text="مبلغ الكفالة")
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("name", width=150, anchor="center")
        self.tree.column("stage", width=100, anchor="center")
        self.tree.column("amount", width=100, anchor="center")

        # RTL: عكس العرض (المبلغ يسار ... الرقم يمين)
        self.tree["displaycolumns"] = ("amount", "stage", "name", "id")
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # --- 2. الفورم (يمين - العمود 1) ---
        form_frame = ttk.LabelFrame(self, text="بيانات الطالب", padding=10)
        form_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # إعداد Grid للفورم (مطابق لـ orphans_screen: Widget=col0, Label=col1)
        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=0)

        self.row_idx = 0
        def add_row(label, widget):
            widget.grid(row=self.row_idx, column=0, sticky="ew", pady=5, padx=5)
            ttk.Label(form_frame, text=label + ":").grid(row=self.row_idx, column=1, sticky="e", pady=5, padx=5)
            self.row_idx += 1

        # رقم الملف
        add_row("رقم الملف", ttk.Entry(form_frame, textvariable=self.var_id, state="readonly", justify="right"))
        
        # الاسم
        add_row("الاسم الثلاثي", ttk.Entry(form_frame, textvariable=self.var_name, justify="right"))
        
        # المرحلة
        stages = ["الابتدائية", "المتوسطة", "الإعدادية", "جامعي"]
        cb_stage = ttk.Combobox(form_frame, textvariable=self.var_stage, values=stages, state="readonly", justify="right")
        add_row("المرحلة الدراسية", cb_stage)
        
        # المدرسة
        add_row("المدرسة/الجامعة", ttk.Entry(form_frame, textvariable=self.var_school, justify="right"))
        
        # الفاصل
        ttk.Separator(form_frame).grid(row=self.row_idx, column=0, columnspan=2, sticky="ew", pady=15)
        self.row_idx += 1
        
        # الكفالة
        add_row("مبلغ الكفالة", ttk.Entry(form_frame, textvariable=self.var_monthly_amount, justify="right"))

        # الأزرار (في الأسفل)
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=self.row_idx, column=0, columnspan=2, pady=20)
        
        # الترتيب: جديد، حفظ، حذف
        ttk.Button(btn_frame, text="جديد", bootstyle="secondary", width=10, command=self.clear_form).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="حفظ", bootstyle="success", width=10, command=self.save_student).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="حذف", bootstyle="danger", width=10, command=self.delete_student).pack(side=LEFT, padx=5)

    def load_students(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        cursor = self.conn.cursor()
        query = """
            SELECT s.id, s.name, s.school_stage, COALESCE(sp.monthly_amount, 0), s.school_name
            FROM students s
            LEFT JOIN student_sponsorships sp ON s.id = sp.student_id
            WHERE s.name LIKE ?
        """
        search_val = f"%{self.search_var.get()}%"
        cursor.execute(query, (search_val,))
        for row in cursor.fetchall():
            self.tree.insert("", "end", iid=row[0], values=(row[0], row[1], row[2], row[3]))

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        student_id = sel[0]
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM students WHERE id=?", (student_id,))
        s_data = cursor.fetchone() 
        
        cursor.execute("SELECT monthly_amount FROM student_sponsorships WHERE student_id=?", (student_id,))
        sp_data = cursor.fetchone()

        if s_data:
            self.var_id.set(s_data[0])
            self.var_name.set(s_data[1])
            self.var_stage.set(s_data[4])
            self.var_school.set(s_data[5])
        
        if sp_data:
            self.var_monthly_amount.set(sp_data[0])
        else:
            self.var_monthly_amount.set("")

    def save_student(self):
        name = self.var_name.get()
        if not name: return
        try:
            cursor = self.conn.cursor()
            if self.var_id.get():
                uid = self.var_id.get()
                cursor.execute("UPDATE students SET name=?, school_stage=?, school_name=? WHERE id=?", 
                               (name, self.var_stage.get(), self.var_school.get(), uid))
                cursor.execute("UPDATE student_sponsorships SET monthly_amount=? WHERE student_id=?", 
                               (self.var_monthly_amount.get(), uid))
            else:
                cursor.execute("INSERT INTO students (name, school_stage, school_name) VALUES (?, ?, ?)", 
                               (name, self.var_stage.get(), self.var_school.get()))
                uid = cursor.lastrowid
                cursor.execute("INSERT INTO student_sponsorships (student_id, monthly_amount) VALUES (?, ?)", 
                               (uid, self.var_monthly_amount.get()))
            
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
        self.var_stage.set("")
        self.var_school.set("")
        self.var_monthly_amount.set("")