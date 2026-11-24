"""Các hàm thuần túy (pure helpers) - không phụ thuộc GUI, dễ unit-test."""
from __future__ import annotations


def parse_coordinates(raw: str) -> tuple[float, float]:
    """Phân tích chuỗi toạ độ 'kinh độ, vĩ độ' -> (kinh_do, vi_do).

    Raises:
        ValueError: nếu chuỗi sai định dạng, không parse được, hoặc
                    ngoài phạm vi hợp lệ (kinh độ -180..180, vĩ độ -90..90).
    """
    parts = raw.split(',')
    if len(parts) != 2:
        raise ValueError("Sai định dạng: cần 'kinh độ, vĩ độ' (ví dụ: 105.783, 10.045)")
    try:
        kinh_do = float(parts[0].strip())
        vi_do = float(parts[1].strip())
    except ValueError as e:
        raise ValueError("Sai định dạng: cần 'kinh độ, vĩ độ' (ví dụ: 105.783, 10.045)") from e
    if not (-180 <= kinh_do <= 180 and -90 <= vi_do <= 90):
        raise ValueError("Toạ độ ngoài phạm vi hợp lệ (kinh độ -180..180, vĩ độ -90..90)")
    return kinh_do, vi_do


# Đơn giá theo loại xe (VNĐ/km)
DON_GIA_XE = {
    "Nhẹ": 15000,
    "Nặng": 25000,
}


def don_gia_theo_loai_xe(loai_xe: str) -> int:
    """Trả về đơn giá VNĐ/km theo loại xe (mặc định xe nhẹ)."""
    for tu_khoa, gia in DON_GIA_XE.items():
        if tu_khoa in loai_xe:
            return gia
    return DON_GIA_XE["Nhẹ"]


def tinh_chi_phi(khoang_cach_km: float, loai_xe: str) -> int:
    """Tính chi phí vận chuyển (VNĐ) = quãng đường x đơn giá."""
    return int(khoang_cach_km * don_gia_theo_loai_xe(loai_xe))


def dinh_dang_vnd(chi_phi: int) -> str:
    """Định dạng số tiền kiểu Việt Nam: 1234567 -> '1.234.567'."""
    return "{:,}".format(chi_phi).replace(',', '.')
