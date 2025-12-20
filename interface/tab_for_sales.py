import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from services import ProductService, CustomerService, BillService
import mysql.connector
from mysql.connector import Error

class SaleTab(ttk.Frame):
    def __init__(self, parent, employee):
        super().__init__(parent)
        self.employee = employee
        self.current_customer = None
        self.cart = []

        self.product_service = ProductService()
        self.customer_service = CustomerService()
        self.bill_service = BillService()

        self.create_widgets()

    def create_widgets(self):
        left_frame = tk.Frame(self)
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Tìm khách hàng
        customer_frame = tk.LabelFrame(left_frame, text="THÔNG TIN KHÁCH HÀNG", font=("Arial", 12, "bold"))
        customer_frame.pack(fill="x", pady=10)

        tk.Label(customer_frame, text="Số điện thoại:", font=("Arial", 12)).pack(side="left", padx=10, pady=10)
        self.entry_phone = tk.Entry(customer_frame, font=("Arial", 12), width=20)
        self.entry_phone.pack(side="left", padx=5, pady=10)
        tk.Button(customer_frame, text="Tìm khách", font=("Arial", 10), bg="#3498db", fg="white",
                  command=self.search_customer).pack(side="left", padx=10, pady=10)

        self.lbl_customer = tk.Label(customer_frame, text="Khách vãng lai", font=("Arial", 12, "bold"), fg="#27ae60")
        self.lbl_customer.pack(side="left", padx=20, pady=10)

        # Giỏ hàng
        cart_frame = tk.LabelFrame(left_frame, text="GIỎ HÀNG", font=("Arial", 12, "bold"))
        cart_frame.pack(fill="both", expand=True, pady=10)

        columns = ("STT", "Tên sản phẩm", "SL", "Giá", "Thành tiền")
        self.tree_cart = ttk.Treeview(cart_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree_cart.heading(col, text=col)
            self.tree_cart.column(col, width=120, anchor="center")
        self.tree_cart.pack(fill="both", expand=True, padx=10, pady=10)

        # Tổng tiền
        self.lbl_total = tk.Label(left_frame, text="TỔNG TIỀN: 0 VND", font=("Arial", 18, "bold"), fg="red")
        self.lbl_total.pack(pady=10)

        # Nút thanh toán & hủy
        btn_frame = tk.Frame(left_frame)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="THANH TOÁN", font=("Arial", 14, "bold"), bg="#27ae60", fg="white", width=15, height=4,
                  command=self.checkout).pack(side="left", padx=20)
        tk.Button(btn_frame, text="HỦY GIỎ", font=("Arial", 12), bg="#e74c3c", fg="white", width=12, height=4,
                  command=self.clear_cart).pack(side="left", padx=20)

        right_frame = tk.Frame(self)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        search_frame = tk.LabelFrame(right_frame, text="TÌM SẢN PHẨM", font=("Arial", 12, "bold"))
        search_frame.pack(fill="x", pady=10)

        tk.Label(search_frame, text="Tên sản phẩm:", font=("Arial", 12)).pack(side="left", padx=10, pady=10)
        self.entry_search = tk.Entry(search_frame, font=("Arial", 12), width=40)
        self.entry_search.pack(side="left", padx=5, pady=10)
        tk.Button(search_frame, text="Tìm", font=("Arial", 10), bg="#3498db", fg="white",
                  command=self.search_products).pack(side="left", padx=10, pady=10)
        tk.Button(search_frame, text="Tất cả", font=("Arial", 10),
                  command=self.load_all_products).pack(side="left", padx=10, pady=10)

        # Danh sách sản phẩm
        prod_frame = tk.LabelFrame(right_frame, text="DANH SÁCH SẢN PHẨM", font=("Arial", 12, "bold"))
        prod_frame.pack(fill="both", expand=True)

        columns_prod = ("ID", "Tên sản phẩm", "Giá", "Tồn kho")
        self.tree_products = ttk.Treeview(prod_frame, columns=columns_prod, show="headings", height=20)
        for col in columns_prod:
            self.tree_products.heading(col, text=col)
            self.tree_products.column(col, width=180, anchor="center")
        self.tree_products.pack(fill="both", expand=True, padx=10, pady=10)

        # Double click để thêm vào giỏ
        self.tree_products.bind("<Double-1>", self.add_to_cart)

        # Load sản phẩm ban đầu
        self.load_all_products()

    def load_all_products(self):
        products = self.product_service.get_all_products()
        self.update_product_tree(products)

    def search_products(self):
        keyword = self.entry_search.get().strip()
        if not keyword:
            self.load_all_products()
            return
        products = self.product_service.search_products(keyword)
        self.update_product_tree(products)

    def update_product_tree(self, products):
        # Xóa cũ
        for item in self.tree_products.get_children():
            self.tree_products.delete(item)
        # Thêm mới
        for p in products:
            self.tree_products.insert("", "end", values=(
                p.product_id,
                p.name,
                f"{p.price:,.0f}",
                p.quantity
            ))

    def search_customer(self):
        phone = self.entry_phone.get().strip()
        if not phone:
            self.current_customer = None
            self.lbl_customer.config(text="Khách vãng lai", fg="#27ae60")
            return

        # Tìm khách cũ
        customer = self.customer_service.get_customer_by_phone(phone)
        if customer:
            self.current_customer = customer
            points = getattr(customer, 'shopping_point', 0)  # Lấy điểm từ object
            self.lbl_customer.config(text=f"{customer.name} - Điểm: {points}", fg="#27ae60")
            return

        # Nếu không tìm thấy → hỏi tạo mới
        if messagebox.askyesno("Khách mới", f"Không tìm thấy khách với SĐT {phone}.\nBạn muốn tạo khách hàng mới không?"):
            name = simpledialog.askstring("Tên khách", "Nhập tên khách hàng:", initialvalue="Khách lẻ")
            if name and name.strip():
                new_customer = self.customer_service.create_customer(name.strip(), phone)
                if new_customer:
                    self.current_customer = new_customer
                    self.lbl_customer.config(text=f"{new_customer.name} - Điểm: 0", fg="#27ae60")
                    messagebox.showinfo("Thành công", f"Đã tạo khách mới: {new_customer.name}\nSĐT: {phone}")
                else:
                    messagebox.showerror("Lỗi", "Không thể tạo khách mới! (SĐT có thể đã tồn tại)")
            else:
                messagebox.showinfo("Hủy", "Không tạo khách mới.")
                self.current_customer = None
                self.lbl_customer.config(text="Khách vãng lai", fg="#27ae60")
        else:
            self.current_customer = None
            self.lbl_customer.config(text="Khách vãng lai", fg="#27ae60")

    def load_all_products(self):
        products = self.product_service.get_all_products()
        self.update_product_tree(products)

    def search_products(self):
        keyword = self.entry_search.get().strip()
        if not keyword:
            self.load_all_products()
            return
        products = self.product_service.search_products(keyword)
        self.update_product_tree(products)

    def update_product_tree(self, products):
        for item in self.tree_products.get_children():
            self.tree_products.delete(item)
        for p in products:
            self.tree_products.insert("", "end", values=(p.product_id, p.name, f"{p.price:,.0f}", p.quantity))

    def add_to_cart(self, event):
        selected = self.tree_products.selection()
        if not selected:
            return
        item = self.tree_products.item(selected[0])
        product_id = item['values'][0]
        product = self.product_service.get_product_by_id(product_id)
        if not product:
            messagebox.showerror("Lỗi", "Không tìm thấy sản phẩm!")
            return
        if product.quantity <= 0:
            messagebox.showwarning("Hết hàng", f"Sản phẩm {product.name} đã hết hàng!")
            return

        qty = simpledialog.askinteger("Số lượng", f"Nhập số lượng (tồn kho: {product.quantity}):",
                                      minvalue=1, maxvalue=product.quantity)
        if qty:
            # Kiểm tra đã có trong giỏ chưa
            for item in self.cart:
                if item['product'].product_id == product.product_id:
                    item['quantity'] += qty
                    break
            else:
                self.cart.append({'product': product, 'quantity': qty})
            self.refresh_cart()

    def refresh_cart(self):
        for item in self.tree_cart.get_children():
            self.tree_cart.delete(item)
        total = 0
        for i, item in enumerate(self.cart, 1):
            p = item['product']
            qty = item['quantity']
            subtotal = qty * p.price
            total += subtotal
            self.tree_cart.insert("", "end", values=(i, p.name, qty, f"{p.price:,.0f}", f"{subtotal:,.0f}"))
        self.lbl_total.config(text=f"TỔNG TIỀN: {total:,.0f} VND")

    def clear_cart(self):
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn hủy giỏ hàng?"):
            self.cart = []
            self.refresh_cart()

    def checkout(self):
        if not self.cart:
            messagebox.showwarning("Giỏ trống", "Chưa có sản phẩm nào trong giỏ hàng!")
            return

        # Disable nút thanh toán để tránh bấm nhiều lần
        for widget in self.winfo_parent().winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Button) and child.cget("text") == "THANH TOÁN":
                        child.config(state="disabled")

        # Chạy thanh toán trong thread riêng để không đơ app
        import threading
        threading.Thread(target=self._process_checkout, daemon=True).start()

    def _process_checkout(self):
        try:
            # Tính tổng tiền
            total = sum(item['quantity'] * item['product'].price for item in self.cart)
            customer_id = getattr(self.current_customer, 'customer_id', None)
            used_points = 0

            if self.current_customer:
                fresh = self.customer_service.get_customer_by_phone(self.current_customer.phone_number)
                current_points = getattr(fresh, 'shopping_point', 0) if fresh else 0
                if current_points > 0:
                    max_use = min(current_points, total)
                    # Dùng queue để hỏi user từ main thread
                    from queue import Queue
                    queue = Queue()

                    def ask_use_points():
                        result = messagebox.askyesno("Dùng điểm?", f"Khách có {current_points:,} điểm. Dùng giảm giá?")
                        queue.put(result)

                    self.after(0, ask_use_points)
                    if queue.get():
                        def ask_amount():
                            amount = simpledialog.askinteger("Dùng điểm", f"Nhập số điểm (tối đa {max_use:,}):",
                                                             minvalue=0, maxvalue=max_use)
                            queue.put(amount)

                        self.after(0, ask_amount)
                        used_points_input = queue.get()
                        used_points = used_points_input if used_points_input is not None else 0

            final_total = total - used_points

            # Xác nhận cuối
            queue = Queue()

            def confirm_payment():
                result = messagebox.askyesno("Xác nhận",
                                             f"Tổng tiền: {total:,.0f} VND\n"
                                             f"Dùng điểm: {used_points:,}\n"
                                             f"Thành tiền: {final_total:,.0f} VND\n\n"
                                             f"Thanh toán?")
                queue.put(result)

            self.after(0, confirm_payment)
            if not queue.get():
                self.after(0, self._enable_payment_button)
                return

            # Thanh toán thực tế
            bill = self.bill_service.create_bill(customer_id=customer_id, employee_id=self.employee['employee_id'])
            if not bill:
                self.after(0, lambda: messagebox.showerror("Lỗi", "Không thể tạo hóa đơn!"))
                self.after(0, self._enable_payment_button)
                return

            success = True
            for item in self.cart:
                if not self.bill_service.add_item_to_bill(bill.bill_id, item['product'].product_id, item['quantity']):
                    success = False
                    break

            if success and used_points > 0 and customer_id:
                self.bill_service.apply_points(bill.bill_id, used_points, customer_id)

            if success:
                points_earned = final_total // 100000
                self.bill_service.complete_bill(bill.bill_id, customer_id, points_earned)

                self.after(0, lambda: messagebox.showinfo("Thành công!",
                                                          f"Thanh toán thành công!\n"
                                                          f"Thành tiền: {final_total:,.0f} VND\n"
                                                          f"Điểm mới: +{points_earned}"))

                self.after(0, self.clear_cart)
                if customer_id:
                    self.after(0, self._refresh_customer_points)
                self.after(0, self.load_all_products)
            else:
                self.after(0, lambda: messagebox.showerror("Lỗi", "Thanh toán thất bại! Có thể hết hàng."))

        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Lỗi hệ thống", f"Lỗi: {e}"))
            print(f"[CHECKOUT THREAD ERROR] {e}")
        finally:
            self.after(0, self._enable_payment_button)

    def _enable_payment_button(self):
        for widget in self.winfo_parent().winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Button) and child.cget("text") == "THANH TOÁN":
                        child.config(state="normal")

    def _refresh_customer_points(self):
        if self.current_customer:
            updated = self.customer_service.get_customer_by_phone(self.current_customer.phone_number)
            if updated:
                self.current_customer = updated
                self.lbl_customer.config(text=f"{updated.name} - Điểm: {updated.shopping_point}")