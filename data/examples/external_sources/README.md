# Danh Mục Dữ Liệu Thực Tế Từ Nguồn Bên Ngoài (Phương Án 2)

Thư mục này lưu trữ danh mục kiểm chứng (`EXTERNAL_SOURCES_MANIFEST.json`) và tệp CSV mẫu đã được xác minh tính tương thích kỹ thuật cũng như quyền phân phối lại theo Phương án 2.

---

## 1. Kết Luận Tổng Thể Về Tìm Kiếm Dữ Liệu Độc Lập

- **Trạng thái kết luận:** `NO_VERIFIED_COMPATIBLE_EXTERNAL_DATA` (đối với phân loại `COMPATIBLE_INDEPENDENT`).
- **Giải thích dựa trên bằng chứng thực tế:**
  1. Bộ dữ liệu **Scania APS (`UCI #421` / `IDA 2016 Industrial Challenge`)** sử dụng `170` thuộc tính vận hành được Scania CV AB ẩn danh bằng mã chữ cái hai ký tự kèm chỉ số bin (`aa_000` đến `eg_000`) và không công bố tên cảm biến vật lý gốc vì lý do bảo mật công nghiệp.
  2. Bộ dữ liệu thực tế mới nhất do chính Scania CV AB và Đại học Stockholm công bố gần đây là **SCANIA Component X Dataset (2024–2025)** ([DOI: 10.5878/bnh5-ka77](https://doi.org/10.5878/bnh5-ka77), công bố trên *Nature Scientific Data* [DOI: 10.1038/s41597-025-04802-6](https://doi.org/10.1038/s41597-025-04802-6)). Tuy nhiên, bộ dữ liệu này theo dõi một linh kiện động cơ khác (`Component X`) dưới dạng chuỗi thời gian đa bảng (`vehicle_id`, `time_step`) và sử dụng hệ mã số hoàn toàn khác (`167_0..167_9`, `158_0..158_9`, `397_0..397_35`...). Do đó, **SCANIA Component X** thuộc phân loại `INCOMPATIBLE` — tuyệt đối không thể ánh xạ cưỡng bức hay điền cột giả để chạy trên mô hình 170 thuộc tính `aa_000..eg_000`.
  3. Tất cả các nguồn bên ngoài trên UCI (`#414`), OpenML (`#41138`, `#46908`), Kaggle và GitHub có đủ `170` thuộc tính `aa_000..eg_000` đều được kiểm chứng bằng mã băm SHA-256 và đối chiếu từng bản ghi là **bản sao hoặc tập con trực tiếp của bộ dữ liệu IDA 2016 Challenge (`COMPATIBLE_DUPLICATE` hoặc `PARTIALLY_COMPATIBLE`)**.

---

## 2. Tệp CSV Đã Xác Minh Trong Thư Mục Này (`COMPATIBLE_DUPLICATE`)

| Tên tệp | Phân loại | Nguồn gốc | Số dòng | Số cột | Nhãn thực tế | Kích thước | Mã băm SHA-256 |
|---|---|---|---:|---:|---|---:|---|
| `uci414_ida2016_duplicate_validation_50.csv` | `COMPATIBLE_DUPLICATE` | UCI Machine Learning Repository #414 (`IDA2016Challenge` — [DOI: 10.24432/C5V60Q](https://doi.org/10.24432/C5V60Q)) | 50 | 171 | `2 pos` / `48 neg` | 38.484 B | `28fb0bd55db814dbd160b1e1e746508ff0d27988d35224536b179d25056c0f89` |

### Lưu ý bắt buộc khi sử dụng `uci414_ida2016_duplicate_validation_50.csv`

- **Tuyệt đối không gọi đây là dữ liệu độc lập:** Tệp `to_uci/aps_failure_training_set.csv` tải từ UCI #414 (`https://archive.ics.uci.edu/static/public/414/ida2016challenge.zip`, SHA-256 ZIP: `5336e4b643c4915931879c3db0535139e188732e74122badf0a4eb1749b4e8cb`) có mã băm SHA-256 là `bb484302e3a3a1c8ef5e1f0129c4dc7cbd58f350867f95b575461ca21ab6b9da`, **trùng khớp 100% từng byte** với tệp `aps_failure_training_set.csv` của UCI #421.
- **Lý do chọn 50 mẫu theo danh sách Validation G3:** Để tránh đưa các mẫu thuộc tập `Train (48.000 mẫu)` vào bài demo dự đoán, 50 dòng trong tệp này được lọc từ 50 dòng đầu tiên theo thứ tự xuất hiện trong `to_uci/aps_failure_training_set.csv` (UCI #414) thuộc phân vùng Validation G3 (`official_20261029_04`).
- **Quyền sử dụng và phân phối:** Được phát hành công khai trên UCI Machine Learning Repository theo giấy phép **CC BY 4.0** (kèm thông báo **GNU GPLv3-or-later** của Scania CV AB trong tệp mô tả gốc).

---

## 3. Các Nguồn Chỉ Lưu Metadata (`EXTERNAL_SOURCES_MANIFEST.json`)

Đối với các nguồn bản sao trên GitHub không đính kèm tệp `LICENSE` rõ ràng (`jieqiong-pang`, `atagunduzalp`), nguồn yêu cầu xác thực tài khoản (`Kaggle`), các nguồn định dạng `ARFF` đã biến đổi ký hiệu thiếu/tên cột và trộn lẫn tập Official Test (`OpenML #41138`, `OpenML #46908`), hoặc các nguồn không tương thích (`SCANIA Component X`, `MetroPT-3`, `AI4I 2020`, `Zenodo #22834903`), kho lưu trữ chỉ lưu metadata, URL chính xác, mã băm SHA-256 kiểm chứng và hướng dẫn truy cập tại:
- [`EXTERNAL_SOURCES_MANIFEST.json`](EXTERNAL_SOURCES_MANIFEST.json)
- [`../../reports/demo_data_expansion/EXTERNAL_DATA_SOURCE_AUDIT.md`](../../reports/demo_data_expansion/EXTERNAL_DATA_SOURCE_AUDIT.md)
- [`../../reports/demo_data_expansion/EXTERNAL_SOURCE_REGISTRY.json`](../../reports/demo_data_expansion/EXTERNAL_SOURCE_REGISTRY.json)
