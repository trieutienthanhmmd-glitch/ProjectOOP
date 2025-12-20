import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from services import ReportService
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta

class ReportTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.report_service = ReportService()
        self.create_widgets()

    def create_widgets(self):
        # Header
        header = tk.Frame(self)
        header.pack(fill="x", pady=10)

        tk.Label(header, text="BÁO CÁO DOANH THU & HOẠT ĐỘNG", font=("Arial", 22, "bold")).pack(side="left", padx=20)

        tk.Button(header, text="XEM BÁO CÁO MỚI NHẤT", font=("Arial", 14, "bold"), bg="#f39c12", fg="white",
                  width=25, height=2, command=self.refresh_report).pack(side="right", padx=20)

        # Notebook bên trong tab báo cáo (chia 2 phần: Biểu đồ + Chi tiết)
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=20, pady=10)

        # Tab 1: Biểu đồ doanh thu
        chart_tab = ttk.Frame(notebook)
        notebook.add(chart_tab, text="BIỂU ĐỒ DOANH THU")

        self.chart_frame = tk.Frame(chart_tab)
        self.chart_frame.pack(fill="both", expand=True)

        # Tab 2: Báo cáo chi tiết
        detail_tab = ttk.Frame(notebook)
        notebook.add(detail_tab, text="CHI TIẾT BÁO CÁO")

        self.report_text = scrolledtext.ScrolledText(detail_tab, font=("Courier", 11), wrap="none")
        self.report_text.pack(fill="both", expand=True, padx=10, pady=10)

        # Load báo cáo lần đầu
        self.refresh_report()

    def refresh_report(self):
        # Xóa cũ
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # 1. Biểu đồ doanh thu 7 ngày gần nhất
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d')
        revenue_data = self.report_service.get_revenue_by_date_range(start_date, end_date)

        if revenue_data:
            dates = [row['sale_date'].strftime('%d/%m') for row in revenue_data]
            revenues = [row['revenue'] for row in revenue_data]

            fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
            ax.plot(dates, revenues, marker='o', color='#3498db', linewidth=3)
            ax.set_title("DOANH THU 7 NGÀY GẦN NHẤT", fontsize=16, fontweight='bold')
            ax.set_xlabel("Ngày", fontsize=12)
            ax.set_ylabel("Doanh thu (VND)", fontsize=12)
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.tick_params(axis='x', rotation=45)

            # Format y-axis
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:,.0f}"))

            canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        else:
            tk.Label(self.chart_frame, text="Chưa có dữ liệu doanh thu trong 7 ngày gần nhất",
                     font=("Arial", 16), fg="gray").pack(expand=True)

        # 2. Báo cáo text chi tiết
        self.report_text.delete(1.0, tk.END)
        import sys
        from io import StringIO

        old_stdout = sys.stdout
        sys.stdout = captured = StringIO()

        self.report_service.print_all_reports()

        sys.stdout = old_stdout
        self.report_text.insert(tk.END, captured.getvalue())