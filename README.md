# TMNS – Phần mềm điều phối thu mua nông sản

Dự án cá nhân Python có giao diện desktop, sử dụng SQL Server và dịch vụ tính lộ trình. Mã nguồn được xây dựng với **AI hỗ trợ**; tác giả tự cấu hình môi trường và chạy thử các chức năng trong quá trình học tập.

## Mã nguồn chính
- `app_ui.py`: giao diện ứng dụng.
- `core_logic.py`: kết nối SQL Server và xử lý nghiệp vụ.
- `routing_api.py`: thành phần truy vấn lộ trình.
- `helpers.py`, `test_helpers.py`: tiện ích và thử nghiệm.

## Chạy thử
1. Cài Python và các thư viện trong `requirements.txt` (một số thư viện có thể cần cấu hình bổ sung).
2. Cài ODBC Driver 17 for SQL Server và chuẩn bị SQL Server.
3. Khai báo biến môi trường `TMNS_SQL_SERVER` (mặc định `localhost`) và `TMNS_SQL_DATABASE` (mặc định `TMNS`). Chuỗi kết nối hiện dùng Windows Authentication.
4. Chạy `python app_ui.py` sau khi đã chuẩn bị CSDL theo cấu trúc ứng dụng yêu cầu.

**Lưu ý:** Bản gốc không có script SQL đầy đủ trong bộ mã nguồn chọn để chia sẻ. Chưa xác nhận chạy hoàn chỉnh trên máy mới. Đã loại `.venv`, file EXE, bản đồ HTML xuất sẵn và báo cáo chứa thông tin cá nhân.
