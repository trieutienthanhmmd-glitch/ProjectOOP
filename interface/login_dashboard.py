import tkinter as tk
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error

class LoginWindow:
    def __init__(self, root, on_success_callback):
        self.root = root
        self.on_success_callback = on_success_callback
        self.root.title("Đăng nhập hệ thống siêu thị")
        self.root.geometry("750x650")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f2f5")

        self.create_widgets()

    def create_widgets(self):
        # Tiêu đề
        title = tk.Label(self.root, text="ĐĂNG NHẬP HỆ THỐNG",
                         font=("Arial", 28, "bold"), bg="#f0f2f5", fg="#2c3e50")
        title.pack(pady=(60, 40))

        # Khung form chính (căn giữa)
        form_frame = tk.Frame(self.root, bg="#ffffff", relief="ridge", bd=4, padx=50, pady=40)
        form_frame.pack(pady=20, ipadx=30, ipady=30)

        # Mã nhân viên
        label_id = tk.Label(form_frame, text="Mã nhân viên:", font=("Arial", 16), bg="#ffffff")
        label_id.grid(row=0, column=0, sticky="e", pady=20, padx=20)
        self.entry_id = tk.Entry(form_frame, font=("Arial", 16), width=30, justify="center")
        self.entry_id.grid(row=0, column=1, pady=20, padx=20)

        # CMND/CCCD
        label_pass = tk.Label(form_frame, text="CMND/CCCD:", font=("Arial", 16), bg="#ffffff")
        label_pass.grid(row=1, column=0, sticky="e", pady=20, padx=20)
        self.entry_pass = tk.Entry(form_frame, font=("Arial", 16), width=30, justify="center", show="*")
        self.entry_pass.grid(row=1, column=1, pady=20, padx=20)

        # NÚT ĐĂNG NHẬP - ĐẶT RIÊNG RA NGOÀI FORM ĐỂ KHÔNG BỊ ẨN
        btn_frame = tk.Frame(self.root, bg="#f0f2f5")
        btn_frame.pack(pady=50)

        self.btn_login = tk.Button(btn_frame, text="ĐĂNG NHẬP", font=("Arial", 18, "bold"),
                                   bg="#3498db", fg="white", width=25, height=2,
                                   relief="raised", bd=5, cursor="hand2",
                                   command=self.login)
        self.btn_login.pack()

        # Hiệu ứng hover cho nút
        self.btn_login.bind("<Enter>", lambda e: self.btn_login.config(bg="#2980b9"))
        self.btn_login.bind("<Leave>", lambda e: self.btn_login.config(bg="#3498db"))

    def login(self):
        emp_id = self.entry_id.get().strip()
        password = self.entry_pass.get().strip()

        if not emp_id or not password:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return

        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='123456789',
                database='quản lý siêu thị',
                charset='utf8mb4'
            )
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT employee_id, name, title 
                FROM employee 
                WHERE employee_id = %s AND identification = %s AND is_working = 1
            """, (emp_id, password))
            employee = cursor.fetchone()
            cursor.close()
            conn.close()

            if employee:
                messagebox.showinfo("Thành công", f"Chào mừng {employee['name']} ({employee['title']})!")
                self.root.destroy()
                self.on_success_callback(employee)
            else:
                messagebox.showerror("Thất bại", "Sai mã nhân viên hoặc CMND/CCCD!")
        except Error as e:
            messagebox.showerror("Lỗi kết nối", f"Không thể kết nối database:\n{e}")