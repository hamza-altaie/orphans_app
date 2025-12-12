# housing_screen.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from ttkbootstrap.constants import *
import sqlite3

class HousingScreen(ttk.Frame):
    def __init__(self, parent, conn: sqlite3.Connection):
        super().__init__(parent)
        self.conn = conn
        
        # تقسيم الشاشة
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=3) # الجدول يسار
        self.columnconfigure(1, weight=2) # الفورم يمين

        self.var_id = tk.StringVar()
        self.var_name = tk.StringVar()
        self.var_phone = tk.StringVar()   # رقم الهاتف
        self.var_type = tk.StringVar()
        self.var_status = tk.StringVar()
        self.var_amount = tk.StringVar()
        
        self.search_var = tk.StringVar()

        self.create_widgets()
        self.load_data()

    def _apply_right_tag(self, text_widget: tk.Text):
        text_widget.tag_configure("right", justify="right")
        text_widget.tag_add("right", "1.0", "end")

    def _validate_number(self, val):
        """السماح فقط بالأرقام أو النص الفارغ"""
        return val == "" or val.isdigit()    

    def create_widgets(self):
        vcmd = (self.register(self._validate_number), '%P')
        style = ttk.Style(self)
        style.configure("Housing.Treeview", rowheight=28)

        # ====== 1. الجدول (يسار - العمود 0) ======
        table_frame = ttk.LabelFrame(self, text="مشاريع السكن", padding=5, labelanchor="ne")
        table_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # البحث
        search_frame = ttk.Frame(table_frame)
        search_frame.pack(fill="x", pady=5)
        
        ttk.Label(search_frame, text="بحث بالاسم :\u200f").pack(side=RIGHT, padx=5)
        entry_search = ttk.Entry(search_frame, textvariable=self.search_var, justify="right")
        entry_search.pack(side=RIGHT, padx=5)
        entry_search.bind("<Return>", lambda e: self.load_data())
        ttk.Button(search_frame, text="بحث", command=self.load_data, width=10).pack(side=RIGHT, padx=5)

        self.tree_scroll_y = ttk.Scrollbar(table_frame, orient="vertical")
        self.tree_scroll_y.pack(side="right", fill="y")

        columns = ("id", "name", "phone", "type", "status", "amount")
        self.tree = ttk.Treeview(
            table_frame, 
            columns=columns, 
            show="headings", 
            displaycolumns=("amount", "status", "type", "phone", "name", "id"), # RTL
            yscrollcommand=self.tree_scroll_y.set,
            style="Housing.Treeview"
        )
        self.tree.pack(fill="both", expand=True)
        self.tree_scroll_y.config(command=self.tree.yview)
        
        self.tree.heading("id", text="رقم")
        self.tree.heading("name", text="المستفيد")
        self.tree.heading("phone", text="الهاتف")
        self.tree.heading("type", text="نوع الدعم")
        self.tree.heading("status", text="الحالة")
        self.tree.heading("amount", text="المبلغ")
        
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("name", width=140, anchor="center")
        self.tree.column("phone", width=100, anchor="center")
        self.tree.column("type", width=80, anchor="center")
        self.tree.column("status", width=80, anchor="center")
        self.tree.column("amount", width=80, anchor="center")
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select)



        # ---- أزرار التصدير ----
        export_frame = ttk.Frame(table_frame)
        export_frame.pack(fill="x", padx=5, pady=(5, 0))

        ttk.Button(export_frame, text="Excel تصدير", command=self.export_to_excel, width=15).pack(side="right", padx=(5, 0))
        ttk.Button(export_frame, text="PDF تصدير", command=self.export_to_pdf, width=15).pack(side="right", padx=(5, 0))



        # ====== 2. الفورم (يمين - العمود 1) ======
        form_frame = ttk.LabelFrame(self, text="بيانات المشروع", padding=10, labelanchor="ne")
        form_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)

        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=0)
        
        self.row_idx = 0
        def add_row(label, widget):
            nonlocal self
            widget.grid(row=self.row_idx, column=0, sticky="ew", pady=4, padx=(0, 5))
            ttk.Label(form_frame, text=label + " :\u200f").grid(row=self.row_idx, column=1, sticky="e", pady=4, padx=(5, 0))
            self.row_idx += 1

        add_row("رقم الملف", ttk.Entry(form_frame, textvariable=self.var_id, state="readonly", justify="right"))
        add_row("المستفيد", ttk.Entry(form_frame, textvariable=self.var_name, justify="right", font=("Arial", 11)))
        add_row("رقم الهاتف", ttk.Entry(form_frame, textvariable=self.var_phone, justify="right", validate="key", validatecommand=vcmd))
        
        add_row("نوع الدعم", ttk.Combobox(form_frame, textvariable=self.var_type, values=["بناء", "ترميم", "إيجار"], state="readonly", justify="right"))
        add_row("حالة المشروع", ttk.Combobox(form_frame, textvariable=self.var_status, values=["قيد الدراسة", "جاري التنفيذ", "مكتمل"], state="readonly", justify="right"))
        add_row("المبلغ التقديري", ttk.Entry(form_frame, textvariable=self.var_amount, justify="right", validate="key", validatecommand=vcmd))
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
        
        # ترتيب الأزرار: جديد (يمين)، حفظ (وسط)، حذف (يسار)
        ttk.Button(btn_frame, text="جديد", bootstyle="secondary", width=10, command=self.clear).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="حفظ", bootstyle="warning", width=10, command=self.save).grid(row=0, column=1, padx=5)
        # زر الحذف الجديد
        ttk.Button(btn_frame, text="حذف", bootstyle="danger", width=10, command=self.delete_housing).grid(row=0, column=0, padx=5)

    def load_data(self):
        for row in self.tree.get_children(): self.tree.delete(row)
        cursor = self.conn.cursor()
        
        query = "SELECT id, name, phone, support_type, project_status, amount_allocated, notes FROM housing_beneficiaries WHERE name LIKE ?"
        cursor.execute(query, (f"%{self.search_var.get()}%",))
        
        for i, row in enumerate(cursor.fetchall(), start=1):
            # row: 0=id, 1=name, 2=phone, 3=type, 4=status, 5=amount, 6=notes
            display_vals = (i, row[1], row[2], row[3], row[4], row[5])
            self.tree.insert("", "end", iid=str(row[0]), values=display_vals)

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        uid = sel[0]
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM housing_beneficiaries WHERE id=?", (uid,))
        row = cursor.fetchone()
        if row:
            # ترتيب الحقول في DB كما في db_setup:
            # id(0), name(1), phone(2), governorate(3), address(4), status(5), support(6), amount(7), proj_stat(8), notes(9)
            # *تنبيه*: الترتيب يعتمد على db_setup. تأكد من تطابقه.
            # في الكود أعلاه استخدمنا: id, name, phone, governorate, address, housing_status, support_type, amount, project_status, notes
            self.var_id.set(row[0])
            self.var_name.set(row[1])
            self.var_phone.set(row[2] or "")
            self.var_type.set(row[6] or "")
            self.var_amount.set(row[7] or "")
            self.var_status.set(row[8] or "")
            
            self.notes_text.delete("1.0", tk.END)
            self.notes_text.insert("1.0", row[9] or "")
            self._apply_right_tag(self.notes_text)

    def save(self):
        # 1. التحقق من وجود الاسم وإظهار تنبيه إذا كان فارغاً
        name = self.var_name.get().strip()
        if not name:
            messagebox.showwarning("تنبيه", "يرجى إدخال اسم المستفيد")
            return
        
        phone = self.var_phone.get()
        typ = self.var_type.get()
        status = self.var_status.get()
        try:
            amount = float(self.var_amount.get() or 0)
        except:
            amount = 0.0
        notes = self.notes_text.get("1.0", tk.END).strip()

        # 2. استخدام try...except لاكتشاف الأخطاء
        try:
            cursor = self.conn.cursor()
            
            if self.var_id.get():
                # تحديث
                uid = self.var_id.get()
                cursor.execute("""
                    UPDATE housing_beneficiaries 
                    SET name=?, phone=?, support_type=?, amount_allocated=?, project_status=?, notes=? 
                    WHERE id=?
                """, (name, phone, typ, amount, status, notes, uid))
            else:
                # إضافة جديد
                cursor.execute("""
                    INSERT INTO housing_beneficiaries (name, phone, support_type, amount_allocated, project_status, notes) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (name, phone, typ, amount, status, notes))
            
            self.conn.commit()
            self.load_data()
            self.clear()
            
            # 3. إظهار رسالة النجاح
            messagebox.showinfo("نجاح", "تم حفظ البيانات بنجاح")
            
        except Exception as e:
            # في حال وجود خطأ في قاعدة البيانات
            messagebox.showerror("خطأ", f"حدث خطأ أثناء الحفظ:\n{e}")



    def delete_housing(self):
        # 1. التحقق من اختيار مشروع للحذف
        uid = self.var_id.get()
        if not uid:
            messagebox.showwarning("تنبيه", "يرجى اختيار مشروع من الجدول أولاً لحذفه")
            return

        # 2. رسالة تأكيد
        confirm = messagebox.askyesno(
            "تأكيد الحذف", 
            "هل أنت متأكد من حذف هذا المشروع وكافة بياناته؟\n(لا يمكن التراجع عن هذا الإجراء)"
        )
        if not confirm:
            return

        try:
            cursor = self.conn.cursor()
            
            # 3. حذف الدفعات المرتبطة أولاً (لتجنب مشاكل بقايا البيانات)
            cursor.execute("DELETE FROM housing_payments WHERE housing_id=?", (uid,))
            
            # 4. حذف المشروع نفسه
            cursor.execute("DELETE FROM housing_beneficiaries WHERE id=?", (uid,))
            
            self.conn.commit()
            
            # 5. تحديث الواجهة
            self.load_data() # تحديث الجدول
            self.clear()     # تفريغ الحقول
            
            messagebox.showinfo("نجاح", "تم حذف المشروع بنجاح")
            
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء الحذف:\n{e}")     
            
               

    def clear(self):
        self.var_id.set("")
        self.var_name.set("")
        self.var_phone.set("")
        self.var_type.set("")
        self.var_amount.set("")
        self.var_status.set("")
        self.notes_text.delete("1.0", tk.END)
        self.tree.selection_remove(self.tree.selection())
        


    # ==========================
    #   التصدير إلى Excel / PDF
    # ==========================
    def _collect_current_rows(self):
        rows = []
        for iid in self.tree.get_children():
            # values = (id, name, phone, type, status, amount)
            values = self.tree.item(iid)["values"]
            if values:
                rows.append(values)
        return rows

    def export_to_excel(self):
        rows = self._collect_current_rows()
        if not rows:
            messagebox.showinfo("معلومة", "لا توجد بيانات.")
            return

        try:
            from openpyxl import Workbook
            from openpyxl.styles import Alignment
        except ImportError:
            messagebox.showerror("خطأ", "مكتبة openpyxl غير مثبتة.")
            return

        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")],
            title="حفظ تقرير السكن", initialfile="تقرير_مشاريع_السكن.xlsx"
        )
        if not file_path: return

        wb = Workbook()
        ws = wb.active
        ws.title = "مشاريع السكن"
        
        ws.append(["رقم", "المستفيد", "الهاتف", "نوع الدعم", "الحالة", "المبلغ"])
        
        total = 0.0
        for r in rows:
            try: amt = float(r[5] or 0)
            except: amt = 0.0
            total += amt
            ws.append([r[0], r[1], r[2], r[3], r[4], amt])

        ws.append(["", "", "", "", "المجموع", total])

        for row in ws.iter_rows():
            for cell in row:
                cell.alignment = Alignment(horizontal='right')
        
        try:
            wb.save(file_path)
            messagebox.showinfo("تم", "تم التصدير بنجاح.")
        except Exception as e:
            messagebox.showerror("خطأ", str(e))

    def export_to_pdf(self):
        rows = self._collect_current_rows()
        if not rows: return

        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            import arabic_reshaper
            from bidi.algorithm import get_display
        except ImportError:
            messagebox.showerror("خطأ", "مكتبات PDF غير مثبتة.")
            return

        font_name = "Helvetica"
        for p in [r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\tahoma.ttf"]:
            try:
                pdfmetrics.registerFont(TTFont("ArabicFont", p))
                font_name = "ArabicFont"
                break
            except: continue

        def ar(text):
            if not text: return ""
            try: return get_display(arabic_reshaper.reshape(str(text)))
            except: return str(text)

        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")],
            title="حفظ تقرير السكن", initialfile="تقرير_مشاريع_السكن.pdf"
        )
        if not file_path: return

        c = canvas.Canvas(file_path, pagesize=A4)
        w, h = A4
        
        c.setFont(font_name, 16)
        c.drawRightString(w-50, h-50, ar("تقرير مشاريع السكن"))
        
        # الإحداثيات
        y = h - 80
        x_id = w - 40
        x_name = w - 80
        x_phone = w - 200
        x_type = w - 300
        x_status = w - 380
        x_amount = w - 460

        def draw_header():
            nonlocal y
            c.setFont(font_name, 10)
            c.drawRightString(x_id, y, ar("رقم"))
            c.drawRightString(x_name, y, ar("المستفيد"))
            c.drawRightString(x_phone, y, ar("الهاتف"))
            c.drawRightString(x_type, y, ar("النوع"))
            c.drawRightString(x_status, y, ar("الحالة"))
            c.drawRightString(x_amount, y, ar("المبلغ"))
            y -= 10
            c.line(40, y, w-40, y)
            y -= 20

        draw_header()

        for r in rows:
            if y < 50:
                c.showPage()
                y = h - 50
                draw_header()
            
            # r = (id, name, phone, type, status, amount)
            c.drawRightString(x_id, y, str(r[0]))
            c.drawRightString(x_name, y, ar(r[1]))
            c.drawRightString(x_phone, y, str(r[2]))
            c.drawRightString(x_type, y, ar(r[3]))
            c.drawRightString(x_status, y, ar(r[4]))
            c.drawRightString(x_amount, y, str(r[5]))
            y -= 20

        try:
            c.save()
            messagebox.showinfo("تم", "تم تصدير ملف PDF بنجاح.")
        except Exception as e:
            messagebox.showerror("خطأ", str(e))    

        