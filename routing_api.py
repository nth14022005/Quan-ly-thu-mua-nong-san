import requests

class TuyenDuongAPI:
    def __init__(self):
        # Sử dụng OSRM (Open Source Routing Machine) - API miễn phí và tương thích cực tốt với Leaflet
        self.base_url = "http://router.project-osrm.org/route/v1/driving/"

    def tinh_quang_duong_ngan_nhat(self, toa_do_bat_dau, toa_do_ket_thuc):
        """
        toa_do_bat_dau: tuple (Kinh độ, Vĩ độ) - ví dụ tọa độ Vựa trái cây ở Cần Thơ
        toa_do_ket_thuc: tuple (Kinh độ, Vĩ độ) - ví dụ tọa độ Nhà Vườn
        Lưu ý quan trọng của API này: Phải truyền theo thứ tự KINH ĐỘ rồi tới VĨ ĐỘ (Longitude, Latitude)
        """
        # Trích xuất kinh độ, vĩ độ từ tuple
        kinh_do_1, vi_do_1 = toa_do_bat_dau
        kinh_do_2, vi_do_2 = toa_do_ket_thuc

        # Ghép thành chuỗi URL theo chuẩn của OSRM
        url = f"{self.base_url}{kinh_do_1},{vi_do_1};{kinh_do_2},{vi_do_2}?overview=false"

        try:
            # Gửi request lên server
            response = requests.get(url)
            
            # Kiểm tra xem API có trả về thành công không (HTTP 200)
            if response.status_code == 200:
                data = response.json() # Ép kiểu dữ liệu JSON trả về
                
                # Trích xuất khoảng cách (đơn vị mét) từ file JSON
                khoang_cach_met = data['routes'][0]['distance']
                
                # Đổi ra kilomet cho dễ nhìn
                khoang_cach_km = round(khoang_cach_met / 1000, 2)
                return khoang_cach_km
            else:
                print(f"Lỗi kết nối API: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Đã xảy ra lỗi khi gọi API định tuyến: {e}")
            return None

# Chạy test thử
if __name__ == "__main__":
    api = TuyenDuongAPI()
    
    # Tọa độ test ở Cần Thơ (Nhớ là Kinh độ trước, Vĩ độ sau)
    # Vựa trung tâm: Kinh độ 105.783, Vĩ độ 10.045
    vua_trung_tam = (105.783, 10.045) 
    
    # Nhà vườn A: Kinh độ 105.742, Vĩ độ 10.021
    nha_vuon_a = (105.742, 10.021)   
    
    khoang_cach = api.tinh_quang_duong_ngan_nhat(vua_trung_tam, nha_vuon_a)
    
    if khoang_cach:
        print(f"Quãng đường ngắn nhất từ vựa trung tâm đến nhà vườn là: {khoang_cach} km")