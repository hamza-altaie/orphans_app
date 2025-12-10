# statistics_screen.py
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


class StatisticsScreen(ttk.Frame):
    def __init__(self, parent, conn: sqlite3.Connection):
        super().__init__(parent)

        self.conn = conn

        # متغيرات النصوص للإحصائيات
        self.total_orphans_var = tk.StringVar()
        self.active_orphans_var = tk.StringVar()
        self.stopped_orphans_var = tk.StringVar()
        self.withdrawn_orphans_var = tk.StringVar()
        self.total_monthly_amount_var = tk.StringVar()

        self.create_widgets()
        self.refresh_stats()

    def create_widgets(self):
        # تقسيم رئيسي: فوق ملخص – تحت جدول المحافظات
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        # ===== ملخص عام =====
        summary_frame = ttk.LabelFrame(
            self,
            text="ملخص عام",
            padding=10,
            labelanchor="ne",
            style="Card.TLabelframe",
        )
        summary_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))

        # نخلي الأعمدة تتمدد
        summary_frame.columnconfigure(0, weight=1)
        summary_frame.columnconfigure(1, weight=1)

        # دالة مساعدة لإضافة سطر (عنوان + قيمة)
        def add_summary_row(row, label_text, var):
            ttk.Label(summary_frame, text=f": {label_text}").grid(
                row=row, column=1, sticky="e", padx=5, pady=3
            )
            ttk.Label(summary_frame, textvariable=var).grid(
                row=row, column=0, sticky="w", padx=5, pady=3
            )

        add_summary_row(0, "إجمالي عدد الأيتام", self.total_orphans_var)
        add_summary_row(1, "عدد الأيتام الفعّالين", self.active_orphans_var)
        add_summary_row(2, "الأيتام الموقوفين", self.stopped_orphans_var)
        add_summary_row(3, "الأيتام المنسحبين", self.withdrawn_orphans_var)
        add_summary_row(4, "إجمالي المبالغ الشهرية الفعّالة", self.total_monthly_amount_var)

        # زر تحديث
        refresh_btn = ttk.Button(
            summary_frame,
            text="تحديث الأرقام",
            command=self.refresh_stats,
            width=18,
        )
        refresh_btn.grid(row=0, column=2, rowspan=2, padx=10, pady=3, sticky="n")

        # ===== جدول الأيتام حسب المحافظة =====
        gov_frame = ttk.LabelFrame(
            self,
            text="توزيع الأيتام حسب المحافظة",
            padding=10,
            labelanchor="ne",
            style="Card.TLabelframe",
        )
        gov_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))

        gov_frame.rowconfigure(0, weight=1)
        gov_frame.columnconfigure(0, weight=1)

        self.gov_tree = ttk.Treeview(
            gov_frame,
            columns=("governorate", "count"),
            show="headings",
            height=8,
        )
        self.gov_tree.heading("governorate", text="المحافظة")
        self.gov_tree.heading("count", text="عدد الأيتام")

        self.gov_tree.column("governorate", anchor="center", width=160)
        self.gov_tree.column("count", anchor="center", width=80)

        scroll_y = ttk.Scrollbar(gov_frame, orient="vertical", command=self.gov_tree.yview)
        self.gov_tree.configure(yscrollcommand=scroll_y.set)

        self.gov_tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")

    def refresh_stats(self):
        """إعادة حساب وعرض الإحصائيات"""
        try:
            cur = self.conn.cursor()

            # إجمالي الأيتام
            cur.execute("SELECT COUNT(*) FROM orphans")
            total_orphans = cur.fetchone()[0] or 0

            # الأيتام حسب الحالة
            cur.execute("SELECT COUNT(*) FROM orphans WHERE status = 'فعّال'")
            active_orphans = cur.fetchone()[0] or 0

            cur.execute("SELECT COUNT(*) FROM orphans WHERE status = 'موقوف'")
            stopped_orphans = cur.fetchone()[0] or 0

            cur.execute("SELECT COUNT(*) FROM orphans WHERE status = 'منسحب'")
            withdrawn_orphans = cur.fetchone()[0] or 0

            # إجمالي المبالغ الشهرية للكفالات الفعّالة
            cur.execute(
                """
                SELECT COALESCE(SUM(monthly_amount), 0)
                FROM sponsorships
                WHERE status = 'فعّالة'
                """
            )
            total_monthly_amount = cur.fetchone()[0] or 0

            # تعيين القيم للـ Labels
            self.total_orphans_var.set(str(total_orphans))
            self.active_orphans_var.set(str(active_orphans))
            self.stopped_orphans_var.set(str(stopped_orphans))
            self.withdrawn_orphans_var.set(str(withdrawn_orphans))
            self.total_monthly_amount_var.set(f"{total_monthly_amount:.0f}")

            # جدول توزيع الأيتام حسب المحافظة
            for item in self.gov_tree.get_children():
                self.gov_tree.delete(item)

            cur.execute(
                """
                SELECT
                    CASE
                        WHEN governorate IS NULL OR TRIM(governorate) = '' THEN 'غير محدد'
                        ELSE governorate
                    END AS gov,
                    COUNT(*) AS cnt
                FROM orphans
                GROUP BY gov
                ORDER BY cnt DESC
                """
            )

            for gov, cnt in cur.fetchall():
                self.gov_tree.insert("", tk.END, values=(gov, cnt))

        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تحميل الإحصائيات:\n{e}")
