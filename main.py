# main.py
import tkinter as tk
from tkinter import ttk
import sqlite3

from db_setup import DB_NAME, create_tables
from orphans_screen import OrphansScreen
from payments_screen import PaymentsScreen


def main():
    root = tk.Tk()
    root.title("نظام كفالة الأيتام")
    root.state("zoomed")
    root.resizable(True, True)

    # شبكة رئيسية: صف للتبويبات + صف للمحتوى
    root.rowconfigure(0, weight=0)   # سطر التبويبات
    root.rowconfigure(1, weight=1)   # سطر المحتوى
    root.columnconfigure(0, weight=1)

    # اتصال واحد مشترك
    conn = sqlite3.connect(DB_NAME)
    create_tables(conn)

    # ====== سطر التبويبات (يميل لليمين) ======
    tabs_frame = ttk.Frame(root)
    tabs_frame.grid(row=0, column=0, sticky="ew")
    tabs_frame.columnconfigure(0, weight=1)  # فراغ من اليسار
    tabs_frame.columnconfigure(1, weight=0)
    tabs_frame.columnconfigure(2, weight=0)

    # فريم المحتوى اللي راح نبدّل بينه
    content_frame = ttk.Frame(root)
    content_frame.grid(row=1, column=0, sticky="nsew")
    content_frame.rowconfigure(0, weight=1)
    content_frame.columnconfigure(0, weight=1)

    # الشاشات
    orphans_tab = OrphansScreen(content_frame, conn)
    payments_tab = PaymentsScreen(content_frame, conn)

    for f in (orphans_tab, payments_tab):
        f.grid(row=0, column=0, sticky="nsew")

    # دالة تبديل التبويب
    def show_tab(tab_name: str):
        if tab_name == "orphans":
            orphans_tab.tkraise()
            btn_orphans.state(["pressed"])
            btn_payments.state(["!pressed"])
        else:
            payments_tab.tkraise()
            btn_payments.state(["pressed"])
            btn_orphans.state(["!pressed"])

    # أزرار التبويب – مرتبة من اليمين لليسار
    style = ttk.Style(root)
    style.configure("Tab.TButton", padding=(10, 5))

    btn_payments = ttk.Button(
        tabs_frame,
        text="الدفعات الشهرية",
        style="Tab.TButton",
        command=lambda: show_tab("payments"),
    )
    btn_payments.grid(row=0, column=2, padx=(5, 10), pady=5, sticky="e")

    btn_orphans = ttk.Button(
        tabs_frame,
        text="الأيتام والكفالات",
        style="Tab.TButton",
        command=lambda: show_tab("orphans"),
    )
    btn_orphans.grid(row=0, column=1, padx=(5, 0), pady=5, sticky="e")

    # فراغ يتمدّد من جهة اليسار حتى تبقى الأزرار ملتصقة باليمين
    ttk.Label(tabs_frame, text="").grid(row=0, column=0, sticky="ew")

    # إظهار تبويب الأيتام كبداية
    show_tab("orphans")

    def on_closing():
        conn.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
