import pytest

from helpers import parse_coordinates, don_gia_theo_loai_xe, tinh_chi_phi, dinh_dang_vnd


class TestParseCoordinates:
    def test_valid(self):
        assert parse_coordinates("105.783, 10.045") == (105.783, 10.045)

    def test_valid_no_spaces(self):
        assert parse_coordinates("105.783,10.045") == (105.783, 10.045)

    def test_valid_negative(self):
        assert parse_coordinates("-105.0, -10.5") == (-105.0, -10.5)

    @pytest.mark.parametrize("raw", ["105.783", "", "10.0, ", "abc, def", "105.783, 10.045, 9.9"])
    def test_invalid_format_raises(self, raw):
        with pytest.raises(ValueError):
            parse_coordinates(raw)

    @pytest.mark.parametrize("raw", ["200.0, 10.0", "105.0, 95.0", "-200.0, 0.0", "0.0, -95.0"])
    def test_out_of_range_raises(self, raw):
        with pytest.raises(ValueError):
            parse_coordinates(raw)


class TestDonGia:
    def test_xe_nhe(self):
        assert don_gia_theo_loai_xe("Xe Tải Nhẹ (15K/km)") == 15000

    def test_xe_nang(self):
        assert don_gia_theo_loai_xe("Xe Tải Nặng (25K/km)") == 25000

    def test_unknown_defaults_to_nhe(self):
        assert don_gia_theo_loai_xe("Xe cổ tứng") == 15000


class TestTinhChiPhi:
    def test_nhe(self):
        assert tinh_chi_phi(10.0, "Xe Tải Nhẹ (15K/km)") == 150000

    def test_nang(self):
        assert tinh_chi_phi(10.0, "Xe Tải Nặng (25K/km)") == 250000

    def test_zero_distance(self):
        assert tinh_chi_phi(0, "Xe Tải Nặng (25K/km)") == 0

    def test_fractional_distance_is_int(self):
        assert isinstance(tinh_chi_phi(3.5, "Xe Tải Nhẹ (15K/km)"), int)


class TestDinhDangVnd:
    def test_basic(self):
        assert dinh_dang_vnd(1234567) == "1.234.567"

    def test_small(self):
        assert dinh_dang_vnd(500) == "500"

    def test_zero(self):
        assert dinh_dang_vnd(0) == "0"
