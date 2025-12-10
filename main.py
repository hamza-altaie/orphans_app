# main.py
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import sqlite3
from datetime import datetime

# استيراد ملفاتك
from db_setup import DB_NAME, create_tables
from orphans_screen import OrphansScreen
from payments_screen import PaymentsScreen
from settings_screen import SettingsScreen
from statistics_screen import StatisticsScreen

# ==========================
#   شاشة التحميل (Splash Screen)
# ==========================
class SplashScreen(ttk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.overrideredirect(True)
        
        width = 450
        height = 280
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        main_frame = ttk.Frame(self, padding=20, bootstyle="light")
        main_frame.pack(expand=True, fill="both")

        ttk.Label(
            main_frame, 
            text="نظام كفالة الأيتام", 
            font=("Segoe UI", 22, "bold"),
            bootstyle="primary"
        ).pack(pady=(20, 10))

        ttk.Label(
            main_frame, 
            text="جارٍ تحميل الواجهة...", 
            font=("Segoe UI", 10),
            bootstyle="secondary"
        ).pack(pady=(0, 5))

        self.progress = ttk.Progressbar(
            main_frame, 
            mode="indeterminate", 
            length=350, 
            bootstyle="primary-striped"
        )
        self.progress.pack(pady=10)
        self.progress.start(10)

# ==========================
#   التطبيق الرئيسي
# ==========================
class MainApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="flatly")
        
        self.title("نظام كفالة الأيتام")
        self.geometry("1200x800")
        
        self.conn = sqlite3.connect(DB_NAME)
        create_tables(self.conn)

        # تحسين الخطوط
        self.style.configure('.', font=('Segoe UI', 10))
        self.style.configure('Treeview', rowheight=30)
        self.style.configure('Treeview.Heading', font=('Segoe UI', 11, 'bold'))

        # إخفاء شريط التبويبات الأصلي
        self.style.layout('Custom.TNotebook.Tab', []) 
        self.style.layout('Custom.TNotebook', [('Notebook.client', {'sticky': 'nswe'})])

        self.create_layout()

    def create_layout(self):
        # 1. الشريط العلوي
        header_frame = ttk.Frame(self, padding=(10, 10))
        header_frame.pack(fill="x", side=TOP)

        # 2. منطقة المحتوى
        self.notebook = ttk.Notebook(self, style='Custom.TNotebook')
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # --- إنشاء الصفحات ---
        self.orphans_screen = OrphansScreen(self.notebook, self.conn)
        self.payments_screen = PaymentsScreen(self.notebook, self.conn)
        self.stats_screen = StatisticsScreen(self.notebook, self.conn)
        self.settings_screen = SettingsScreen(self.notebook, self.conn)
        
        self.about_frame = ttk.Frame(self.notebook, padding=20)
        self.create_about_content(self.about_frame)

        # إضافة الصفحات
        self.notebook.add(self.orphans_screen)   # 0
        self.notebook.add(self.payments_screen)  # 1
        self.notebook.add(self.stats_screen)     # 2
        self.notebook.add(self.settings_screen)  # 3
        self.notebook.add(self.about_frame)      # 4

        # --- إنشاء أزرار التنقل (ألوان مختارة بعناية) ---
        self.nav_buttons = [] 

        # الترتيب من اليمين لليسار:
        
        # 1. الأيتام (أزرق - أساسي)
        self.create_nav_button(header_frame, "الأيتام والكفالات", 0, "primary")
        
        # 2. الدفعات (أخضر - مال)
        self.create_nav_button(header_frame, "الدفعات الشهرية", 1, "success")
        
        # 3. الإحصائيات (برتقالي - تقارير)
        self.create_nav_button(header_frame, "الإحصائيات", 2, "warning")
        
        # 4. الإعدادات (رمادي - أدوات)
        self.create_nav_button(header_frame, "الإعدادات", 3, "secondary")
        
        # 5. حول البرنامج (سماوي - معلومات)
        self.create_nav_button(header_frame, "حول البرنامج", 4, "info")
        
        # تفعيل الصفحة الأولى
        self.switch_tab(0)

    def create_nav_button(self, parent, text, index, color_name):
        """إنشاء زر مع تحديد لونه الخاص"""
        # الحالة الافتراضية: مفرغ (Outline)
        btn = ttk.Button(
            parent, 
            text=text, 
            bootstyle=f"outline-{color_name}", 
            width=18,
            command=lambda: self.switch_tab(index)
        )
        btn.pack(side=RIGHT, padx=5)
        
        # نحفظ الزر + رقمه + لونه المخصص
        self.nav_buttons.append((btn, index, color_name))

    def switch_tab(self, index):
        """الانتقال للصفحة وتحديث ألوان الأزرار"""
        self.notebook.select(index)

        for btn, btn_index, color_name in self.nav_buttons:
            if btn_index == index:
                # الزر النشط: يمتلئ بلونه المخصص
                btn.configure(bootstyle=color_name) 
            else:
                # الزر غير النشط: يصبح مفرغاً بلونه المخصص
                btn.configure(bootstyle=f"outline-{color_name}")

    def create_about_content(self, parent):
        """محتوى شاشة حول البرنامج"""
        
        main_container = ttk.Frame(parent)
        main_container.pack(expand=True, fill="both", padx=50, pady=20)

        # القسم الأول
        sys_frame = ttk.Labelframe(
            main_container, 
            text=" عن النظام ", 
            padding=20, 
            bootstyle="info"
        )
        sys_frame.pack(fill="x", pady=(0, 20))

        ttk.Label(
            sys_frame, 
            text="نظام كفالة الأيتام", 
            font=("Segoe UI", 18, "bold"), 
            bootstyle="inverse-info"
        ).pack(pady=10)

        ttk.Label(sys_frame, text="الإصدار 1.0", font=("Segoe UI", 11)).pack()
        ttk.Label(sys_frame, text="نظام لإدارة بيانات الأيتام، الكفلاء، والدفعات الشهرية.", bootstyle="secondary").pack(pady=5)

        # القسم الثاني
        dev_frame = ttk.Labelframe(
            main_container, 
            text=" معلومات المطور ", 
            padding=20, 
            bootstyle="success"
        )
        dev_frame.pack(fill="x")

        ttk.Label(dev_frame, text="تم التطوير والبرمجة بواسطة:", font=("Segoe UI", 10), bootstyle="secondary").pack(anchor="e")
        
        developer_name = "Hamza Altaie" 
        
        ttk.Label(
            dev_frame, 
            text=developer_name, 
            font=("Segoe UI", 16, "bold"), 
            bootstyle="success"
        ).pack(anchor="e", pady=(0, 10))

        ttk.Separator(dev_frame, bootstyle="secondary").pack(fill="x", pady=10)

        contact_info = [
            ("📱 الهاتف", "07766900989"),
            ("📧 البريد", "hamza.altaie@gmail.com"),
            ("📍 العنوان", "العراق - بغداد"),
        ]

        for label, value in contact_info:
            row = ttk.Frame(dev_frame)
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=value, font=("Segoe UI", 11, "bold"), bootstyle="dark").pack(side=LEFT)
            ttk.Label(row, text=f": {label}", font=("Segoe UI", 11), bootstyle="secondary").pack(side=RIGHT)

        ttk.Label(
            main_container, 
            text=f"جميع الحقوق محفوظة © {datetime.now().year}", 
            font=("Segoe UI", 9), 
            bootstyle="secondary"
        ).pack(side=BOTTOM, pady=20)

    def on_closing(self):
        self.conn.close()
        self.destroy()

if __name__ == "__main__":
    app = MainApp()
    app.withdraw()
    splash = SplashScreen(app)
    
    def finish_splash():
        splash.destroy()
        app.deiconify()
        app.protocol("WM_DELETE_WINDOW", app.on_closing)

    app.after(2000, finish_splash)
    app.mainloop()