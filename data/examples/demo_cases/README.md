# Bộ Dữ Liệu CSV Demo Trích Xuất Từ Tập Validation (Phương Án 1)

> **CẢNH BÁO HỌC THUẬT QUAN TRỌNG — PHÂN BIỆT KẾT QUẢ DEMO VÀ ĐÁNH GIÁ KHOA HỌC:**
> Toàn bộ 8 tệp CSV trong thư mục `data/examples/demo_cases/` được trích xuất từ **phân vùng Validation nghiên cứu đã khóa** (`12.000` mẫu thuộc giao thức G3 `official_20261029_04`, tách phân tầng từ `aps_failure_training_set.csv` với `seed = 42`).
> - **Mục đích sử dụng:** Phục vụ **trình diễn chức năng vận hành của Web Demo** (kiểm tra hợp đồng schema, điền khuyết dữ liệu thiếu `na`, tính điểm APS positive, thử nghiệm thay đổi ngưỡng phân loại $\tau$, giới hạn công suất xưởng $K$, chính sách ưu tiên Top-$K$ và xuất CSV kết quả).
> - **Không phải dữ liệu kiểm thử độc lập:** Đây là các lát cắt nhỏ trích từ tập Validation đã dùng để chọn mô hình/ngưỡng ở Phase 2, **KHÔNG PHẢI** dữ liệu kiểm thử độc lập (`Official Test` — `16.000` mẫu niêm phong trong `aps+failure+at+scania+trucks.zip`).
> - **Không đánh đồng kết quả demo với kết quả đánh giá khoa học:** Các chỉ số ($TP, FP, FN, TN, \text{Precision}, \text{Recall}, F1$, chi phí $C$) trên từng lô demo nhỏ ($12$ đến $1.000$ dòng) phụ thuộc vào kích thước lô và tỷ lệ lấy mẫu của lô đó; tuyệt đối không dùng số liệu của các lô demo để thay thế kết quả nghiệm thu khoa học trên toàn tập Validation (`12.000` mẫu, chi phí Trial 16 là $6.330$ ở $M = 578 \le 1.200$) hay kết quả đánh giá độc lập trên Official Test (`16.000` mẫu, Gate G10 Run 003, chi phí $13.840$ ở $M = 841 \le 1.600$).

---

## 1. Nguồn Gốc Dữ Liệu, Bản Quyền & Tính Toàn Vẹn

- **Tệp nguồn gốc:** `data/raw/scania_aps/aps_failure_training_set.csv`
  - **Kích thước:** `44.669.194` bytes
  - **SHA-256:** `bb484302e3a3a1c8ef5e1f0129c4dc7cbd58f350867f95b575461ca21ab6b9da`
- **Thông báo bản quyền & Nghĩa vụ ghi nguồn (License & Attribution):**
  - **Tên bộ dữ liệu gốc:** *APS Failure at Scania Trucks* (UCI Machine Learning Repository #421, DOI: [10.24432/C51S51](https://doi.org/10.24432/C51S51); bản lưu trữ IDA 2016 Challenge UCI #414, DOI: [10.24432/C5V60Q](https://doi.org/10.24432/C5V60Q)).
  - **Chủ sở hữu bản quyền gốc:** `Copyright (c) 2016 Scania CV AB` (Vagnmakarvägen 1, 151 32 Södertälje, Stockholm, Sweden). Donors: Tony Lindgren (`tony@dsv.su.se`, Stockholm University) và Jonas Biteus (`jonas.biteus@scania.com`, Scania CV AB).
  - **Giấy phép:** Trang UCI phát hành dưới giấy phép **Creative Commons Attribution 4.0 International (CC BY 4.0)**; tệp mô tả gốc [`data/raw/scania_aps/aps_failure_description.txt`](../../raw/scania_aps/aps_failure_description.txt) kèm thông báo **GNU General Public License v3 (or later)** của Scania CV AB. Mọi bản phân phối lại các lát cắt CSV trong thư mục này đều giữ nguyên dẫn chiếu bản quyền về Scania CV AB, UCI Machine Learning Repository và tệp mô tả gốc trong kho lưu trữ.
- **Ngữ nghĩa chính xác của nhãn lớp (`pos` và `neg`):**
  - Theo tài liệu gốc của Scania CV AB (`aps_failure_description.txt`, mục 4):
    - **`pos` ($y = 1$):** Xe tải gặp lỗi ở một linh kiện cụ thể thuộc hệ thống khí nén (**Air Pressure System — APS**).
    - **`neg` ($y = 0$):** Xe tải không mang nhãn lỗi liên quan đến hệ thống APS (trong bộ dữ liệu gốc, nhóm `neg` gồm các xe tải vào xưởng do gặp sự cố ở **các bộ phận khác ngoài hệ thống APS**, vì vậy **không gọi xe `neg` là xe hoàn toàn an toàn hay không có bất kỳ hỏng hóc nào**).
- **Hồ sơ phân vùng G3 đã khóa:**
  - `data/processed/scania_aps/official_split.json` — SHA-256: `543b61e8c436c2f0f394b000e9e6ca9a8097a14b71373a8d9b2a3d3f4fd97a6b`
  - `data/processed/scania_aps/official_20261029_04/membership.npz` — SHA-256: `ca09b816674b54ef7976b03f87f67f920a62cf367ad98ced38071f9485f4d35f`
  - `results/scania_aps/g3/official_20261029_04/stable_manifest.json` — `stable_digest`: `efe781b7e564073a2a764e70a41cfe5c3e8975d33cc38b0fa297ef09f51767bb`

---

## 2. Danh Mục 8 Tệp CSV Demo

| Tệp CSV | Số dòng | Số cột | Phân bố nhãn thực tế | Số dòng có `na` (Tổng ô `na`) | Seed | Kích thước (Bytes) | Mã băm SHA-256 | Mục đích trình diễn |
|---|---:|---:|---|---:|---:|---:|---|---|
| `demo_normal.csv` | 20 | 171 | `0 pos` / `20 neg` | 19 (209 ô) | `42` | 16.621 | `490c61a10bee6b35238543b9f017cf7bb6ac42b7892a1bfb6e611be8b363fbf7` | Lô 20 xe không mang nhãn lỗi liên quan đến APS (100% `neg`), kiểm tra tỷ lệ báo động giả ($FP$) và cách hiển thị chỉ số Recall không xác định (`—`) khi $P = 0$. |
| `demo_failure.csv` | 20 | 171 | `20 pos` / `0 neg` | 18 (541 ô) | `43` | 19.439 | `98ee4edb709f54561e97cb130e3334d0381e4cecf1377f2bb9906080db67ea0e` | Lô 20 xe mang nhãn lỗi APS thực tế (100% `pos`), kiểm tra độ nhạy ($Recall$) và minh họa việc áp trần công suất cứng Top-$K$ ($K=2$) làm tăng $FN$ và tăng tổng chi phí. |
| `demo_mixed.csv` | 100 | 171 | `10 pos` / `90 neg` | 99 (1.464 ô) | `44` | 75.923 | `158281a1d562d97a61313e79fb5a7275b9938e2b5950477a9c0923b804dd87a8` | Lô hỗn hợp ($10\%$ `pos`), minh họa trực quan ma trận nhầm lẫn, hàm chi phí $C = 10 \times FP + 500 \times FN$ và sự đánh đổi khi cắt giảm số lượt kiểm tra theo trần $K$. |
| `demo_missing_values.csv` | 30 | 171 | `0 pos` / `30 neg` | 30 (445 ô) | `45` | 23.348 | `47e449ca881967f6baa2ff6335d9950c3ff0c9bb31b6e706b195780a3d83ebbf` | 100% mẫu trong lô đều chứa dữ liệu thiếu (`na`), kiểm chứng bộ tiền xử lý `tree_preprocessor.joblib` (`SimpleImputer(strategy="median")` học trên Train) và xử lý Recall không xác định (`—`). |
| `demo_capacity.csv` | 200 | 171 | `20 pos` / `180 neg` | 197 (3.040 ô) | `46` | 152.625 | `237e354a79d35244013e8a7fde2a4f3e7316baff8aa22dceaefbe6e794d5b118` | Lô 200 mẫu phục vụ demo ràng buộc công suất xưởng bảo trì ($K = 20$ ở mức $10\%$, trong khi số đề xuất theo ngưỡng là $M = 21 > K$), kích hoạt chính sách ưu tiên Top-$K$. |
| `demo_large_batch.csv` | 1.000 | 171 | `21 pos` / `979 neg` | 991 (14.129 ô) | `47` | 746.986 | `417c02aed42992aa910be0361e01f6571880b552793f51f02219595de6e50457` | Lô lớn đạt ngưỡng tối đa `MAX_ROWS = 1.000` dòng của Web Demo, phản ánh đúng tỷ lệ mất cân bằng tự nhiên ($\approx 2.1\%$ `pos`) và kiểm tra tốc độ suy luận hàng loạt. |
| `demo_unlabeled.csv` | 50 | 170 | Không có cột `class` (ẩn `1 pos` / `49 neg`) | 49 (758 ô) | `48` | 39.012 | `9b0687c99b5e2ce1d3137b8601cfedee3f454a22951f11e0ee82d58b340d7368` | Kịch bản vận hành thực tế khi xe vào xưởng chưa có cột nhãn `class`: hệ thống chỉ xuất điểm rủi ro APS và quyết định bảo trì, không tính $TP/FP/FN/TN$ hay chi phí. |
| `demo_invalid.csv` | 5 | 171 | `0 pos` / `5 neg` (Header lỗi) | 5 (44 ô) | `N/A` | 4.950 | `ba5af166acf234945f7ddf08bc5a13a5dd74a2a4db90ba17cb7f084c4d9b7cfb` | Tệp cố ý sai schema (thiếu cột `eg_000`, thêm cột lạ `invalid_sensor_xyz`) để kiểm chứng Web Demo chặn tệp ngay tại bước kiểm tra hợp đồng dữ liệu (`HTTP 400`). |

### Giải thích rõ vì sao `demo_invalid.csv` sử dụng 5 dòng dữ liệu (thay vì 10 dòng theo đề xuất ban đầu)

Trong hàm `parse_csv(payload, features)` tại `src/scania/live_prediction.py` (dòng 38–52), chốt chặn kiểm tra hợp đồng schema (`FeatureContract`) đọc dòng header đầu tiên (`next(reader, [])`), đối chiếu danh sách cột với `170` thuộc tính bắt buộc (`aa_000..eg_000`) và **ném ngoại lệ `UploadError` ngay tại dòng header trước khi đọc xuống bất kỳ dòng dữ liệu nào**. Do đó, số lượng dòng dữ liệu phía sau dòng header ($5$ dòng hay $10$ dòng) không làm thay đổi luồng bắt lỗi schema. Việc trích đúng `5` dòng đầu tiên của tập Validation (`validation_positions_zero_based = [0, 1, 2, 3, 4]`) đảm bảo tệp là một CSV đa dòng có cấu trúc bảng thực tế nhưng giữ dung lượng tối giản (`4.950` bytes) và tuân thủ quy định *"không ép đủ số lượng nếu không cần thiết"*.

---

## 3. Phương Pháp Lấy Mẫu & Mức Độ Trùng Lặp Giữa Các Tệp

Mỗi tệp hợp lệ được lấy mẫu độc lập với một `seed` cố định (`42` đến `48`) từ tập Validation `12.000` mẫu. Chi tiết vị trí dòng (`validation_positions_zero_based` trong tập Validation và `data_row_positions_zero_based` trong tệp `aps_failure_training_set.csv`) được lưu đầy đủ trong [`DEMO_DATA_MANIFEST.json`](DEMO_DATA_MANIFEST.json).

### Ma trận số lượng mẫu trùng lặp giữa các tệp (Pairwise Row Overlap Count)

| Tệp | `normal` (20) | `failure` (20) | `mixed` (100) | `missing` (30) | `capacity` (200) | `large_batch` (1000) | `unlabeled` (50) | `invalid` (5) | `validation_sample` (12) | `uci414_dup` (50) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **`demo_normal.csv`** | **20** | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 |
| **`demo_failure.csv`** | 0 | **20** | 2 | 0 | 3 | 4 | 0 | 0 | 1 | 0 |
| **`demo_mixed.csv`** | 0 | 2 | **100** | 0 | 2 | 9 | 1 | 0 | 0 | 0 |
| **`demo_missing_values.csv`** | 0 | 0 | 0 | **30** | 1 | 1 | 0 | 0 | 0 | 1 |
| **`demo_capacity.csv`** | 0 | 3 | 2 | 1 | **200** | 25 | 1 | 0 | 0 | 0 |
| **`demo_large_batch.csv`** | 4 | 4 | 9 | 1 | 25 | **1000** | 2 | 0 | 0 | 4 |
| **`demo_unlabeled.csv`** | 0 | 0 | 1 | 0 | 1 | 2 | **50** | 0 | 0 | 1 |
| **`demo_invalid.csv`** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **5** | 5 | 0 |
| **`scania_validation_sample.csv`** | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 5 | **12** | 0 |
| **`uci414_ida2016_duplicate_validation_50.csv`** | 0 | 0 | 0 | 1 | 0 | 4 | 1 | 0 | 0 | **50** |
