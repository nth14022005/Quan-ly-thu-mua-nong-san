import os
import pyodbc

# 1. Custom Exceptions (Xử lý ngoại lệ tự định nghĩa)
class QuaTaiTrongException(Exception):
    def __init__(self, message="Khối lượng nông sản vượt quá mức cho phép của xe!"):
        self.message = message
        super().__init__(self.message)

class SaiDinhDangToaDoException(Exception):
    def __init__(self, message="Tọa độ GPS phải là số thực (Float) hợp lệ."):
        self.message = message
        super().__init__(self.message)

# 2. Database Connection Class
class DBConnection:
    def __init__(self):
        # Đã cập nhật đúng tên Server name lấy từ SQL Server của mày
        self.conn_str = (
            r'DRIVER={ODBC Driver 17 for SQL Server};'
            f'SERVER={os.getenv("TMNS_SQL_SERVER", "localhost")};'
            f'DATABASE={os.getenv("TMNS_SQL_DATABASE", "TMNS")};'
            r'Trusted_Connection=yes;'
        )
    
    def get_connection(self):
        return pyodbc.connect(self.conn_str)

# 3. Class Nhà Vườn
class NhaVuon:
    def __init__(self, ma_nv, ten_nv, vi_do, kinh_do):
        if not isinstance(vi_do, float) or not isinstance(kinh_do, float):
            raise SaiDinhDangToaDoException()
        self.ma_nv = ma_nv
        self.ten_nv = ten_nv
        self.vi_do = vi_do
        self.kinh_do = kinh_do

    def lay_toa_do_gps(self):
        return self.vi_do, self.kinh_do

# 4. Class Xe Tải (Áp dụng kế thừa OOP)
class XeTai:
    def __init__(self, bien_so, ten_tai_xe, tai_trong_toi_da):
        self.bien_so = bien_so
        self.ten_tai_xe = ten_tai_xe
        self.tai_trong_toi_da = tai_trong_toi_da
        self.khoi_luong_hien_tai = 0

    def kiem_tra_tai_trong(self, khoi_luong_them):
        if self.khoi_luong_hien_tai + khoi_luong_them > self.tai_trong_toi_da:
            raise QuaTaiTrongException(f"Xe {self.bien_so} (Tải trọng max: {self.tai_trong_toi_da}T) không thể chở thêm {khoi_luong_them}T.")
        return True

class XeTaiNhe(XeTai):
    def __init__(self, bien_so, ten_tai_xe, tai_trong_toi_da):
        super().__init__(bien_so, ten_tai_xe, tai_trong_toi_da)
        self.loai_xe = "Xe Tải Nhẹ"

class XeTaiNang(XeTai):
    def __init__(self, bien_so, ten_tai_xe, tai_trong_toi_da):
        super().__init__(bien_so, ten_tai_xe, tai_trong_toi_da)
        self.loai_xe = "Xe Tải Nặng"