import customtkinter as ctk
from tkinter import ttk
from tkinter import messagebox
import tkintermapview
import logging
import traceback
from datetime import datetime
from routing_api import TuyenDuongAPI
from core_logic import DBConnection
from helpers import parse_coordinates, tinh_chi_phi, dinh_dang_vnd

# --- CẤU HÌNH GIAO DIỆN ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AppDieuPhoi(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hệ thống Quản lý và Tối ưu lộ trình Thu mua Nông sản")
        self.state("zoomed")
        self.api = TuyenDuongAPI()

        # --- KẾT NỐI DATABASE ---
        self.db_ok = False
        self.db_conn = None
        self.cursor = None
        try:
            self.db_conn = DBConnection().get_connection()
            self.cursor = self.db_conn.cursor()
            
            # Lấy danh sách Nhà Vườn
            self.cursor.execute("SELECT MaNV, TenNV, ViDo, KinhDo FROM NhaVuon")
            self.danh_sach_nv = {row.TenNV: {"MaNV": row.MaNV, "KinhDo": row.KinhDo, "ViDo": row.ViDo} for row in self.cursor.fetchall()}
            
            # Lấy danh sách Biển số xe kèm tải trọng từ bảng XeTai
            self.cursor.execute("SELECT BienSoXe, TaiTrongToiDa, LoaiXe FROM XeTai")
            self.danh_sach_xe_dict = {}
            for row in self.cursor.fetchall():
                chuoi_hien_thi = f"{row.BienSoXe} - {row.TaiTrongToiDa} Tấn ({row.LoaiXe})"
                self.danh_sach_xe_dict[chuoi_hien_thi] = row.BienSoXe
                
            self.db_ok = True
        except Exception as e:
            logging.error("Không thể kết nối SQL Server:\n%s", traceback.format_exc())
            messagebox.showerror("Lỗi CSDL", f"Không thể kết nối SQL Server:\n{e}")
            self.danh_sach_nv = {}
            self.danh_sach_xe_dict = {}

        # --- TIÊU ĐỀ ---
        self.lbl_title = ctk.CTkLabel(self, text="HỆ THỐNG ĐIỀU PHỐI VẬN TẢI & LOGISTICS", font=ctk.CTkFont(size=22, weight="bold"))
        self.lbl_title.pack(pady=(5, 5))

        # --- KHUNG NHẬP LIỆU (Căn giữa) ---
        self.frame_main = ctk.CTkFrame(self, corner_radius=10)
        self.frame_main.pack(pady=5, padx=20, fill="x")

        # Cột trái
        self.frame_left = ctk.CTkFrame(self.frame_main, fg_color="transparent")
        self.frame_left.pack(side="left", padx=20, pady=5)

        ctk.CTkLabel(self.frame_left, text="📍 Điểm xuất phát (TT Cần Thơ):", font=ctk.CTkFont(weight="bold", size=13)).pack(anchor="w")
        self.entry_vua = ctk.CTkEntry(self.frame_left, width=260, height=30)
        self.entry_vua.insert(0, "105.783, 10.045")
        self.entry_vua.pack(anchor="w", pady=2)

        ctk.CTkLabel(self.frame_left, text="🚚 Phân bổ loại xe:", font=ctk.CTkFont(weight="bold", size=13)).pack(anchor="w", pady=(5,0))
        self.cbo_xe = ctk.CTkComboBox(self.frame_left, values=["Xe Tải Nhẹ (15K/km)", "Xe Tải Nặng (25K/km)"], width=260, height=30)
        self.cbo_xe.pack(anchor="w", pady=2)

        # Cột giữa
        self.frame_mid = ctk.CTkFrame(self.frame_main, fg_color="transparent")
        self.frame_mid.pack(side="left", padx=20, pady=5)

        ctk.CTkLabel(self.frame_mid, text="🎯 Điểm đến (Nhà vườn):", font=ctk.CTkFont(weight="bold", size=13)).pack(anchor="w")
        self.cbo_vuon = ctk.CTkComboBox(self.frame_mid, values=list(self.danh_sach_nv.keys()), width=260, height=30)
        if self.danh_sach_nv:
            self.cbo_vuon.set(list(self.danh_sach_nv.keys())[0])
        self.cbo_vuon.pack(anchor="w", pady=2)

        ctk.CTkLabel(self.frame_mid, text="⚖️ Khối lượng thu mua (Tấn):", font=ctk.CTkFont(weight="bold", size=13)).pack(anchor="w", pady=(5,0))
        self.entry_khoi_luong = ctk.CTkEntry(self.frame_mid, width=260, height=30)
        self.entry_khoi_luong.insert(0, "5.0")
        self.entry_khoi_luong.pack(anchor="w", pady=2)

        ctk.CTkLabel(self.frame_mid, text="🚗 Biển số xe:", font=ctk.CTkFont(weight="bold", size=13)).pack(anchor="w", pady=(5,0))
        values_xe = list(self.danh_sach_xe_dict.keys()) if hasattr(self, 'danh_sach_xe_dict') and self.danh_sach_xe_dict else ["Chưa có dữ liệu xe"]
        self.cbo_bien_so = ctk.CTkComboBox(self.frame_mid, values=values_xe, width=260, height=30)
        self.cbo_bien_so.pack(anchor="w", pady=2)

        # Cột phải (Nút bấm chức năng)
        self.frame_right = ctk.CTkFrame(self.frame_main, fg_color="transparent")
        self.frame_right.pack(side="right", padx=20, pady=5, expand=True)

        self.btn_tinh = ctk.CTkButton(self.frame_right, text="1. TÍNH TOÁN & VẼ BẢN ĐỒ", command=self.xu_ly_tinh_toan, height=35, width=200, font=ctk.CTkFont(weight="bold", size=13))
        self.btn_tinh.pack(pady=4)

        self.btn_luu = ctk.CTkButton(self.frame_right, text="2. CHỐT LỆNH ĐIỀU XE", command=self.luu_csdl, height=35, width=200, fg_color="#b85c00", hover_color="#914900", font=ctk.CTkFont(weight="bold", size=13))
        self.btn_luu.pack(pady=4)

        self.btn_lichsu = ctk.CTkButton(self.frame_right, text="3. XEM LỊCH SỬ ĐIỀU XE", command=self.xem_lich_su, height=35, width=200, fg_color="#4a4a4a", hover_color="#2b2b2b", font=ctk.CTkFont(weight="bold", size=13))
        self.btn_lichsu.pack(pady=4)

        # Nếu CSDL không khả dụng thì vô hiệu hóa các nút phụ thuộc dữ liệu
        if not self.db_ok:
            self.btn_luu.configure(state="disabled")
            self.btn_lichsu.configure(state="disabled")

        # --- NHÃN KẾT QUẢ TÍNH TOÁN ---
        self.lbl_ketqua = ctk.CTkLabel(self, text="-- km | Chi phí dự kiến: 0 VNĐ", font=ctk.CTkFont(size=20, weight="bold"), text_color="#2FA572")
        self.lbl_ketqua.pack(pady=5)

        # --- KHUNG BẢN ĐỒ TRỰC QUAN ---
        self.map_frame = ctk.CTkFrame(self, corner_radius=10)
        self.map_frame.pack(pady=10, padx=30, fill="both", expand=True)

        self.map_widget = tkintermapview.TkinterMapView(self.map_frame, corner_radius=10)
        self.map_widget.pack(fill="both", expand=True)

        # Nguồn bản đồ Google Maps
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=vi&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.map_widget.set_position(10.045, 105.783) # Mặc định Ninh Kiều, Cần Thơ
        self.map_widget.set_zoom(13)

        # Các biến hỗ trợ logic
        self.khoang_cach_hien_tai: float = 0
        self.chi_phi_hien_tai: int = 0  # <--- Biến lưu tạm tiền cước
        self.ma_nv_dang_chon: str = ""
        self.current_path: "tkintermapview.MapPath | None" = None

    def xu_ly_tinh_toan(self):
        try:
            vua_toado = parse_coordinates(self.entry_vua.get())
            ten_nv = self.cbo_vuon.get()
            if not ten_nv: return

            vuon_data = self.danh_sach_nv[ten_nv]
            vuon_toado = (vuon_data["KinhDo"], vuon_data["ViDo"])
            self.ma_nv_dang_chon = vuon_data["MaNV"]

            # GỌI API ĐỊNH TUYẾN
            self.khoang_cach_hien_tai = self.api.tinh_quang_duong_ngan_nhat(vua_toado, vuon_toado)

            if self.khoang_cach_hien_tai:
                # TÍNH CHI PHÍ VẬN TẢI
                chi_phi = tinh_chi_phi(self.khoang_cach_hien_tai, self.cbo_xe.get())
                self.chi_phi_hien_tai = chi_phi
                
                chi_phi_str = dinh_dang_vnd(chi_phi)
                self.lbl_ketqua.configure(text=f"{self.khoang_cach_hien_tai} km | Chi phí: {chi_phi_str} VNĐ")

                # VẼ ĐƯỜNG TRÊN BẢN ĐỒ MAPVIEW
                self.map_widget.delete_all_marker()
                if self.current_path:
                    self.current_path.delete()

                vi_do_vua, kinh_do_vua = vua_toado[1], vua_toado[0]
                vi_do_vuon, kinh_do_vuon = vuon_toado[1], vuon_toado[0]

                self.map_widget.set_position(vi_do_vua, kinh_do_vua)
                self.map_widget.set_zoom(13)
                self.map_widget.set_marker(vi_do_vua, kinh_do_vua, text="Vựa Trung Tâm")
                self.map_widget.set_marker(vi_do_vuon, kinh_do_vuon, text=ten_nv)
                self.current_path = self.map_widget.set_path([(vi_do_vua, kinh_do_vua), (vi_do_vuon, kinh_do_vuon)])
            else:
                messagebox.showerror("Lỗi", "Không thể tìm được đường đi qua API OSRM!")

        except Exception as e:
            logging.error("Lỗi Logic (xu_ly_tinh_toan):\n%s", traceback.format_exc())
            messagebox.showerror("Lỗi Logic", f"Đã xảy ra lỗi: {e}")

    def luu_csdl(self):
        if not self.ma_nv_dang_chon or self.khoang_cach_hien_tai == 0:
            messagebox.showwarning("Cảnh báo", "Vui lòng tính toán lộ trình trước khi chốt lệnh!")
            return

        try:
            # Kiểm tra khối lượng
            try:
                khoi_luong = float(self.entry_khoi_luong.get().strip().replace(',', '.'))
            except ValueError:
                messagebox.showwarning("Cảnh báo", "Khối lượng phải là số (ví dụ: 5.0)")
                return
            if khoi_luong <= 0:
                messagebox.showwarning("Cảnh báo", "Khối lượng phải lớn hơn 0!")
                return

            # Kiểm tra biển số xe
            chuoi_xe_chon = self.cbo_bien_so.get().strip()
            bien_so = self.danh_sach_xe_dict.get(chuoi_xe_chon, "")
            
            if not bien_so:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn biển số xe hợp lệ!")
                return

            ngay_hien_tai = datetime.now().strftime("%Y-%m-%d")

            # Sinh mã đơn hàng
            self.cursor.execute("SELECT MAX(MaDH) FROM DonHangThuMua WHERE MaDH LIKE 'DH%' AND MaDH NOT LIKE 'DH%[^0-9]%'")
            max_ma = self.cursor.fetchone()[0]
            so_thu_tu = int(str(max_ma)[2:]) + 1 if max_ma else 1
            ma_dh = f"DH{so_thu_tu:03d}"
            while True:
                self.cursor.execute("SELECT 1 FROM DonHangThuMua WHERE MaDH = ?", ma_dh)
                if self.cursor.fetchone() is None:
                    break
                so_thu_tu += 1
                ma_dh = f"DH{so_thu_tu:03d}"

            # --- INSERT KÈM CỘT ChiPhiVanTai ---
            sql = """
                INSERT INTO DonHangThuMua (MaDH, MaNV, BienSoXe, KhoiLuongThuMua, ChiPhiVanTai, NgayThuMua, TrangThai)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            params = (ma_dh, self.ma_nv_dang_chon, bien_so, khoi_luong, self.chi_phi_hien_tai, ngay_hien_tai, "Đã chốt xe")
            self.cursor.execute(sql, params)
            self.db_conn.commit()

            messagebox.showinfo("Hoàn tất", f"Đã ghi nhận thành công lệnh điều xe mã: {ma_dh} (xe {bien_so}).")
        except Exception as e:
            logging.error("Lỗi SQL Server (luu_csdl):\n%s", traceback.format_exc())
            messagebox.showerror("Lỗi SQL Server", f"Không thể lưu dữ liệu:\n{e}")

    def xem_lich_su(self):
        """Mở lịch sử điều xe, cho phép chọn một dòng để sửa hoặc xóa."""
        if not self.db_ok or self.cursor is None:
            messagebox.showerror("Lỗi CSDL", "Không có kết nối SQL Server.")
            return

        win_lichsu = ctk.CTkToplevel(self)
        win_lichsu.title("Lịch sử chốt lệnh điều xe")
        win_lichsu.geometry("1150x520")
        win_lichsu.minsize(950, 420)
        win_lichsu.attributes("-topmost", True)

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview", background="#2a2d2e", foreground="white",
            rowheight=30, fieldbackground="#2a2d2e", font=("Arial", 11)
        )
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
        style.map("Treeview", background=[("selected", "#22559b")])

        columns = ("MaDH", "TenNV", "BienSoXe", "KhoiLuong", "ChiPhi", "Ngay", "TrangThai")
        tree = ttk.Treeview(win_lichsu, columns=columns, show="headings", selectmode="browse")

        headings = {
            "MaDH": "Mã Đơn",
            "TenNV": "Tên Nhà Vườn (Vựa)",
            "BienSoXe": "Biển Số Xe",
            "KhoiLuong": "Khối Lượng",
            "ChiPhi": "Chi Phí (VNĐ)",
            "Ngay": "Ngày Chốt",
            "TrangThai": "Trạng Thái",
        }
        for col, title in headings.items():
            tree.heading(col, text=title)

        widths = {
            "MaDH": 95, "TenNV": 250, "BienSoXe": 140,
            "KhoiLuong": 125, "ChiPhi": 145, "Ngay": 130, "TrangThai": 150,
        }
        for col, width in widths.items():
            tree.column(col, width=width, anchor="center" if col != "TenNV" else "w")

        tree.pack(fill="both", expand=True, padx=10, pady=(10, 5))

        def tai_lai_lich_su():
            """Đọc lại bảng lịch sử sau khi cập nhật/xóa."""
            for item in tree.get_children():
                tree.delete(item)

            sql = """
                SELECT d.MaDH, n.TenNV, d.BienSoXe, d.KhoiLuongThuMua,
                       d.ChiPhiVanTai, d.NgayThuMua, d.TrangThai
                FROM DonHangThuMua d
                LEFT JOIN NhaVuon n ON d.MaNV = n.MaNV
                ORDER BY d.NgayThuMua DESC, d.MaDH DESC
            """
            self.cursor.execute(sql)
            for row in self.cursor.fetchall():
                khoi_luong_str = f"{row.KhoiLuongThuMua} Tấn"
                chi_phi_str = dinh_dang_vnd(row.ChiPhiVanTai or 0)
                ngay = row.NgayThuMua.strftime("%Y-%m-%d") if hasattr(row.NgayThuMua, "strftime") else str(row.NgayThuMua or "")[:10]
                tree.insert(
                    "", "end",
                    values=(row.MaDH, row.TenNV or "(Không có tên)", row.BienSoXe or "",
                            khoi_luong_str, chi_phi_str, ngay, row.TrangThai or "")
                )

        def lay_ma_don_dang_chon():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Chưa chọn đơn", "Mày hãy chọn một dòng trong lịch sử trước.", parent=win_lichsu)
                return None
            return str(tree.item(selected[0], "values")[0])

        def sua_don_dang_chon():
            ma_dh = lay_ma_don_dang_chon()
            if not ma_dh:
                return

            try:
                self.cursor.execute(
                    """SELECT MaDH, MaNV, BienSoXe, KhoiLuongThuMua,
                              ChiPhiVanTai, NgayThuMua, TrangThai
                       FROM DonHangThuMua WHERE MaDH = ?""",
                    (ma_dh,)
                )
                order = self.cursor.fetchone()
                if not order:
                    messagebox.showerror("Không tìm thấy", f"Không tìm thấy lệnh {ma_dh} trong CSDL.", parent=win_lichsu)
                    tai_lai_lich_su()
                    return
            except Exception as e:
                logging.error("Lỗi đọc đơn cần sửa:\n%s", traceback.format_exc())
                messagebox.showerror("Lỗi CSDL", f"Không thể đọc thông tin đơn hàng:\n{e}", parent=win_lichsu)
                return

            edit_win = ctk.CTkToplevel(win_lichsu)
            edit_win.title(f"Sửa lệnh {ma_dh}")
            edit_win.geometry("500x510")
            edit_win.resizable(False, False)
            edit_win.transient(win_lichsu)
            edit_win.grab_set()

            ctk.CTkLabel(
                edit_win, text=f"SỬA LỆNH ĐIỀU XE {ma_dh}",
                font=ctk.CTkFont(size=18, weight="bold")
            ).pack(pady=(16, 10))

            form = ctk.CTkFrame(edit_win, fg_color="transparent")
            form.pack(fill="both", expand=True, padx=24, pady=4)

            def add_label(row_index, label_text):
                ctk.CTkLabel(form, text=label_text, anchor="w").grid(
                    row=row_index, column=0, sticky="w", padx=(0, 12), pady=7
                )

            garden_names = list(self.danh_sach_nv.keys())
            garden_by_id = {str(v["MaNV"]): name for name, v in self.danh_sach_nv.items()}
            garden_current = garden_by_id.get(str(order.MaNV), garden_names[0] if garden_names else "")

            truck_plates = sorted(set(self.danh_sach_xe_dict.values()))
            plate_current = str(order.BienSoXe or "")
            if plate_current and plate_current not in truck_plates:
                truck_plates.append(plate_current)

            add_label(0, "Nhà vườn")
            cbo_garden = ctk.CTkComboBox(form, values=garden_names, width=285)
            cbo_garden.grid(row=0, column=1, sticky="ew", pady=7)
            if garden_current:
                cbo_garden.set(garden_current)

            add_label(1, "Biển số xe")
            cbo_plate = ctk.CTkComboBox(form, values=truck_plates, width=285)
            cbo_plate.grid(row=1, column=1, sticky="ew", pady=7)
            cbo_plate.set(plate_current)

            add_label(2, "Khối lượng (tấn)")
            entry_weight = ctk.CTkEntry(form, width=285)
            entry_weight.grid(row=2, column=1, sticky="ew", pady=7)
            entry_weight.insert(0, str(order.KhoiLuongThuMua if order.KhoiLuongThuMua is not None else ""))

            add_label(3, "Chi phí (VNĐ)")
            entry_cost = ctk.CTkEntry(form, width=285)
            entry_cost.grid(row=3, column=1, sticky="ew", pady=7)
            entry_cost.insert(0, str(order.ChiPhiVanTai if order.ChiPhiVanTai is not None else 0))

            add_label(4, "Ngày chốt (YYYY-MM-DD)")
            entry_date = ctk.CTkEntry(form, width=285, placeholder_text="2026-10-13")
            entry_date.grid(row=4, column=1, sticky="ew", pady=7)
            date_current = order.NgayThuMua.strftime("%Y-%m-%d") if hasattr(order.NgayThuMua, "strftime") else str(order.NgayThuMua or "")[:10]
            entry_date.insert(0, date_current)

            add_label(5, "Trạng thái")
            entry_status = ctk.CTkEntry(form, width=285)
            entry_status.grid(row=5, column=1, sticky="ew", pady=7)
            entry_status.insert(0, str(order.TrangThai or ""))

            form.grid_columnconfigure(1, weight=1)

            def luu_thay_doi():
                ten_nv = cbo_garden.get().strip()
                bien_so = cbo_plate.get().strip()
                if ten_nv not in self.danh_sach_nv:
                    messagebox.showwarning("Dữ liệu chưa hợp lệ", "Hãy chọn nhà vườn có trong danh sách.", parent=edit_win)
                    return
                if not bien_so or bien_so not in truck_plates:
                    messagebox.showwarning("Dữ liệu chưa hợp lệ", "Hãy chọn biển số xe hợp lệ.", parent=edit_win)
                    return

                try:
                    khoi_luong = float(entry_weight.get().strip().replace(",", "."))
                    if khoi_luong <= 0:
                        raise ValueError("Khối lượng phải lớn hơn 0.")
                except ValueError:
                    messagebox.showwarning("Dữ liệu chưa hợp lệ", "Khối lượng phải là số lớn hơn 0.", parent=edit_win)
                    return

                try:
                    chi_phi_text = entry_cost.get().strip().replace(".", "").replace(",", "")
                    chi_phi = int(chi_phi_text)
                    if chi_phi < 0:
                        raise ValueError("Chi phí không được âm.")
                except ValueError:
                    messagebox.showwarning("Dữ liệu chưa hợp lệ", "Chi phí phải là số nguyên không âm, ví dụ 174000.", parent=edit_win)
                    return

                ngay_text = entry_date.get().strip()
                try:
                    ngay_chot = datetime.strptime(ngay_text, "%Y-%m-%d")
                except ValueError:
                    messagebox.showwarning("Ngày chưa hợp lệ", "Nhập ngày theo dạng YYYY-MM-DD, ví dụ 2026-10-13.", parent=edit_win)
                    return

                trang_thai = entry_status.get().strip()
                if not trang_thai:
                    messagebox.showwarning("Dữ liệu chưa hợp lệ", "Trạng thái không được để trống.", parent=edit_win)
                    return

                ma_nv = self.danh_sach_nv[ten_nv]["MaNV"]
                try:
                    self.cursor.execute(
                        """UPDATE DonHangThuMua
                           SET MaNV = ?, BienSoXe = ?, KhoiLuongThuMua = ?,
                               ChiPhiVanTai = ?, NgayThuMua = ?, TrangThai = ?
                           WHERE MaDH = ?""",
                        (ma_nv, bien_so, khoi_luong, chi_phi, ngay_chot, trang_thai, ma_dh)
                    )
                    self.db_conn.commit()
                    messagebox.showinfo("Đã cập nhật", f"Đã sửa thông tin lệnh {ma_dh}.", parent=edit_win)
                    edit_win.destroy()
                    tai_lai_lich_su()
                except Exception as e:
                    try:
                        self.db_conn.rollback()
                    except Exception:
                        pass
                    logging.error("Lỗi cập nhật đơn hàng:\n%s", traceback.format_exc())
                    messagebox.showerror("Lỗi CSDL", f"Không thể cập nhật lệnh {ma_dh}:\n{e}", parent=edit_win)

            actions = ctk.CTkFrame(edit_win, fg_color="transparent")
            actions.pack(fill="x", padx=24, pady=(8, 16))
            ctk.CTkButton(actions, text="LƯU THAY ĐỔI", command=luu_thay_doi, width=150).pack(side="left", padx=(0, 10))
            ctk.CTkButton(actions, text="HỦY", command=edit_win.destroy, width=100, fg_color="#555555", hover_color="#444444").pack(side="left")

        def xoa_don_dang_chon():
            ma_dh = lay_ma_don_dang_chon()
            if not ma_dh:
                return

            dong_y = messagebox.askyesno(
                "Xác nhận xóa",
                f"Mày có chắc muốn xóa lệnh {ma_dh}?\nThao tác này không thể hoàn tác.",
                parent=win_lichsu
            )
            if not dong_y:
                return

            try:
                self.cursor.execute("DELETE FROM DonHangThuMua WHERE MaDH = ?", (ma_dh,))
                if self.cursor.rowcount == 0:
                    self.db_conn.rollback()
                    messagebox.showwarning("Không tìm thấy", f"Lệnh {ma_dh} không còn trong CSDL.", parent=win_lichsu)
                    tai_lai_lich_su()
                    return
                self.db_conn.commit()
                tai_lai_lich_su()
                messagebox.showinfo("Đã xóa", f"Đã xóa lệnh {ma_dh}.", parent=win_lichsu)
            except Exception as e:
                try:
                    self.db_conn.rollback()
                except Exception:
                    pass
                logging.error("Lỗi xóa đơn hàng:\n%s", traceback.format_exc())
                messagebox.showerror("Lỗi CSDL", f"Không thể xóa lệnh {ma_dh}:\n{e}", parent=win_lichsu)

        def dong_danh_sach():
            win_lichsu.destroy()

        button_frame = ctk.CTkFrame(win_lichsu, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=(4, 10))
        ctk.CTkButton(button_frame, text="SỬA DÒNG ĐANG CHỌN", command=sua_don_dang_chon, width=190).pack(side="left", padx=(0, 8))
        ctk.CTkButton(button_frame, text="XÓA DÒNG ĐANG CHỌN", command=xoa_don_dang_chon, width=190, fg_color="#b3261e", hover_color="#8f1d17").pack(side="left", padx=8)
        ctk.CTkButton(button_frame, text="LÀM MỚI", command=tai_lai_lich_su, width=110, fg_color="#555555", hover_color="#444444").pack(side="left", padx=8)
        ctk.CTkButton(button_frame, text="ĐÓNG", command=dong_danh_sach, width=100, fg_color="#555555", hover_color="#444444").pack(side="right")

        # Nhấp đúp một dòng để mở cửa sổ sửa nhanh.
        tree.bind("<Double-1>", lambda _event: sua_don_dang_chon())

        try:
            tai_lai_lich_su()
        except Exception as e:
            logging.error("Không thể tải dữ liệu lịch sử:\n%s", traceback.format_exc())
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu lịch sử:\n{e}", parent=win_lichsu)

if __name__ == "__main__":
    app = AppDieuPhoi()
    app.mainloop()