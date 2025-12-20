import tkinter as tk
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error

class LoginWindow:
    def __init__(self, root, on_success_callback):
        self.root = root
        self.on_success_callback = on_success_callback  # Hàm gọi khi login thành công
        self.root.title("Đăng nhập hệ thống siêu thị")
        self.root.geometry("450x350")
        self.root.resizable(False, False)
        self.root.configure(bg="#f4f6f9")

        self.create_widgets()

    def create_widgets(self):
        # Title
        title = tk.Label(self.root, text="ĐĂNG NHẬP HỆ THỐNG", font=("Arial", 20, "bold"), bg="#f4f6f9", fg="#2c3e50")
        title.pack(pady=40)

        # Form frame
        form = tk.Frame(self.root, bg="#ffffff", relief="groove", bd=3)
        form.pack(pady=20, padx=50, fill="x")

        tk.Label(form, text="Mã nhân viên:", font=("Arial", 12), bg="#ffffff").pack(pady=15)
        self.entry_id = tk.Entry(form, font=("Arial", 12), width=30, justify="center")
        self.entry_id.pack(pady=5)

        tk.Label(form, text="CMND/CCCD:", font=("Arial", 12), bg="#ffffff").pack(pady=15)
        self.entry_pass = tk.Entry(form, font=("Arial", 12), width=30, justify="center", show="*")
        self.entry_pass.pack(pady=5)

        btn = tk.Button(self.root, text="ĐĂNG NHẬP", font=("Arial", 14, "bold"),
                        bg="#3498db", fg="white", width=20, height=2,
                        command=self.login)
        btn.pack(pady=30)

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
                self.root.destroy()  # Đóng cửa sổ login
                self.on_success_callback(employee)  # Gọi main window với thông tin nhân viên
            else:
                messagebox.showerror("Thất bại", "Sai mã nhân viên hoặc CMND!")
        except Error as e:
            messagebox.showerror("Lỗi kết nối", f"Không thể kết nối database: {e}")