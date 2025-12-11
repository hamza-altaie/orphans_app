# main.py
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import sqlite3
from datetime import datetime
import os

# استيراد الملفات
from db_setup import DB_NAME, create_tables
from orphans_screen import OrphansScreen
from payments_screen import PaymentsScreen
from settings_screen import SettingsScreen
from statistics_screen import StatisticsScreen

# استيراد الشاشات الجديدة
from students_screen import StudentsScreen
from housing_screen import HousingScreen

class SplashScreen(ttk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.overrideredirect(True)
        self.geometry(f"450x280+{(self.winfo_screenwidth()-450)//2}+{(self.winfo_screenheight()-280)//2}")
        
        main_frame = ttk.Frame(self, padding=20, bootstyle="light")
        main_frame.pack(expand=True, fill="both")
        
        ttk.Label(main_frame, text="نظام الكفالة والرعاية المتكامل", font=("Segoe UI", 20, "bold"), bootstyle="primary").pack(pady=20)
        ttk.Label(main_frame, text="جارٍ التحميل...", font=("Segoe UI", 10)).pack()
        
        pb = ttk.Progressbar(main_frame, mode="indeterminate", length=350, bootstyle="primary-striped")
        pb.pack(pady=10)
        pb.start(10)

class MainApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="flatly")
        self.title("نظام الكفالة والرعاية المتكامل")
        self.geometry("1280x850")
        
        self.conn = sqlite3.connect(DB_NAME)
        create_tables(self.conn)

        self.style.configure('.', font=('Segoe UI', 10))
        self.style.configure('Treeview', rowheight=28)
        self.style.configure('Treeview.Heading', font=('Segoe UI', 11, 'bold'))
        self.style.layout('Custom.TNotebook.Tab', [])

        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill="both", expand=True)

        self.show_dashboard()

    def clear_container(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_container()
        
        dash_frame = ttk.Frame(self.main_container, padding=40)
        dash_frame.pack(fill="both", expand=True)

        ttk.Label(dash_frame, text="مرحباً بك في النظام المتكامل", font=("Segoe UI", 24, "bold"), bootstyle="dark").pack(pady=(0, 30))

        # منطقة البطاقات
        cards_frame = ttk.Frame(dash_frame)
        cards_frame.pack(expand=True, fill="both")

        # الصف الأول: الأنظمة
        row1 = ttk.Frame(cards_frame)
        row1.pack(pady=15)

        # ترتيب الأزرار لليمين
        self.create_dash_btn(row1, "دعم السكن", "warning", self.load_housing_system)
        self.create_dash_btn(row1, "كفالة الطلاب", "success", self.load_students_system)
        self.create_dash_btn(row1, "كفالة الأيتام", "primary", self.load_orphans_system)

        # الصف الثاني: الأدوات
        row2 = ttk.Frame(cards_frame)
        row2.pack(pady=15)

        self.create_dash_btn(row2, "حول البرنامج", "info", self.load_about_page)
        self.create_dash_btn(row2, "الإعدادات", "secondary", self.load_settings_page)

        ttk.Label(dash_frame, text="Hamza Altaie © 2025", bootstyle="secondary").pack(side="bottom", pady=20)

    def create_dash_btn(self, parent, text, color, command):
        btn = ttk.Button(parent, text=text, bootstyle=f"{color}", width=22, command=command)
        # padding خارجي للزر ليبتعد عن أخيه
        btn.pack(side="right", padx=15, ipady=15)

    def create_top_nav(self, title, color):
        header = ttk.Frame(self.main_container, bootstyle=color, padding=10)
        header.pack(fill="x", side="top")
        
        ttk.Label(header, text=title, font=("Segoe UI", 16, "bold"), bootstyle=f"inverse-{color}").pack(side="right", padx=10)
        ttk.Button(header, text="الرئيسية 🏠", bootstyle="light-outline", command=self.show_dashboard).pack(side="left")
        return header

    # --- تحميل الأنظمة ---
    def load_orphans_system(self):
        self.clear_container()
        self.create_top_nav("نظام كفالة الأيتام", "primary")
        
        notebook = ttk.Notebook(self.main_container, style='Custom.TNotebook')
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # أزرار التنقل العلوية الخاصة بالأيتام
        nav_frame = ttk.Frame(self.main_container)
        nav_frame.pack(before=notebook, fill="x", padx=10)

        def switch(idx): notebook.select(idx)
        
        # عند استخدام side=RIGHT:
        # أول زر يُكتب في الكود -> يظهر في أقصى اليمين (الأول)
        # آخر زر يُكتب في الكود -> يظهر في أقصى اليسار (الأخير)

        # 1. الأيتام (أول زر يمين)
        ttk.Button(nav_frame, text="الأيتام", bootstyle="outline-primary", command=lambda: switch(0)).pack(side=RIGHT, padx=2)
        
        # 2. الدفعات
        ttk.Button(nav_frame, text="الدفعات", bootstyle="outline-success", command=lambda: switch(1)).pack(side=RIGHT, padx=2)
        
        # 3. الإحصائيات
        ttk.Button(nav_frame, text="الإحصائيات", bootstyle="outline-warning", command=lambda: switch(2)).pack(side=RIGHT, padx=2)
        
        # 4. الإعدادات (آخر زر يسار)
        ttk.Button(nav_frame, text="الإعدادات", bootstyle="outline-secondary", command=lambda: switch(3)).pack(side=RIGHT, padx=2)

        # إضافة الصفحات (يجب أن يتطابق الترتيب هنا مع أرقام switch أعلاه)
        notebook.add(OrphansScreen(notebook, self.conn))      # index 0
        notebook.add(PaymentsScreen(notebook, self.conn))     # index 1
        notebook.add(StatisticsScreen(notebook, self.conn))   # index 2
        notebook.add(SettingsScreen(notebook, self.conn))     # index 3
        
        switch(0)

    def load_students_system(self):
        self.clear_container()
        self.create_top_nav("نظام كفالة الطلاب", "success")
        
        # حاوية رئيسية
        container = ttk.Frame(self.main_container)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # شاشة الطلاب مباشرة
        StudentsScreen(container, self.conn).pack(fill="both", expand=True)

    def load_housing_system(self):
        self.clear_container()
        self.create_top_nav("نظام دعم السكن", "warning")
        
        container = ttk.Frame(self.main_container)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        HousingScreen(container, self.conn).pack(fill="both", expand=True)

    def load_settings_page(self):
        self.clear_container()
        self.create_top_nav("الإعدادات العامة", "secondary")
        
        container = ttk.Frame(self.main_container, padding=20)
        container.pack(fill="both", expand=True)
        
        # نستخدم شاشة الإعدادات الموجودة
        SettingsScreen(container, self.conn).pack(fill="both", expand=True)

    def load_about_page(self):
        self.clear_container()
        self.create_top_nav("حول البرنامج", "info")
        
        about_frame = ttk.Frame(self.main_container, padding=50)
        about_frame.pack(fill="both", expand=True)
        
        # --- 1. عرض الصورة (الشعار) ---
        # ملاحظة: يجب أن تضع صورة باسم "logo.png" بجانب ملف main.py
        # أو قم بتغيير الاسم أدناه ليطابق اسم صورتك
        image_path = "logo.png" 
        
        if os.path.exists(image_path):
            try:
                # نحفظ الصورة في متغير global أو self حتى لا يحذفها جامع القمامة
                self.logo_img = ttk.PhotoImage(file=image_path)
                ttk.Label(about_frame, image=self.logo_img).pack(pady=(0, 20))
            except Exception as e:
                ttk.Label(about_frame, text=f"(خطأ في تحميل الصورة: {e})", bootstyle="danger").pack()
        else:
            # رسالة في حال عدم وجود الصورة
            ttk.Label(about_frame, text="(قم بوضع ملف logo.png هنا لعرض الشعار)", bootstyle="secondary").pack(pady=(0, 20))

        # --- 2. النصوص (عربي + إنكليزي) ---
        
        # اسم النظام
        ttk.Label(about_frame, text="نظام كفالة الأيتام والرعاية", font=("Segoe UI", 22, "bold")).pack(pady=5)
        ttk.Label(about_frame, text="Orphans & Care Sponsorship System", font=("Segoe UI", 16), bootstyle="secondary").pack(pady=(0, 20))
        
        ttk.Separator(about_frame).pack(fill="x", pady=20)
        
        # معلومات المطور
        ttk.Label(about_frame, text="تم التطوير بواسطة:", font=("Segoe UI", 12)).pack()
        
        # الاسم عربي وانكليزي
        developer_text = "Hamza Altaie  |  حمزة الطائي"
        ttk.Label(about_frame, text=developer_text, font=("Segoe UI", 18, "bold"), bootstyle="success").pack(pady=10)
        
        # التواصل
        ttk.Label(about_frame, text="للتواصل : 07766900989", font=("Segoe UI", 12)).pack(pady=5)

    def on_closing(self):
        self.conn.close()
        self.destroy()

if __name__ == "__main__":
    app = MainApp()
    app.withdraw()
    splash = SplashScreen(app)
    def finish():
        splash.destroy()
        app.deiconify()
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.after(1500, finish)
    app.mainloop()