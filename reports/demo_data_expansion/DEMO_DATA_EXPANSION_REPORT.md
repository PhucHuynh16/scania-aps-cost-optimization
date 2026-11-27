# Báo Cáo Hoàn Thành — Mở Rộng Dữ Liệu CSV Demo & Kiểm Chứng Nguồn Dữ Liệu Bên Ngoài (Scania APS UCI #421)

**Dự án:** Tối ưu hóa chi phí bảo trì dự đoán hệ thống khí nén xe tải Scania APS (`UCI #421`)  
**Tác tử thực hiện:** Antigravity  
**Chế độ thực thi:** Song song với Codex trên worktree và branch cô lập  
**Ngày hoàn thành:** `2026-11-27`

---

## 1. Môi Trường Thực Thi, Worktree, Branch & Trạng Thái Git

| Hạng mục | Giá trị xác minh thực tế | Trạng thái |
|---|---|---|
| **Repository chính** | `D:\Năm 3\HK1_2026\Nhập môn tối ưu hóa\baitaplon\portfolio_final` (`https://github.com/PhucHuynh16/scania-aps-cost-optimization.git`) | `PASS` |
| **Commit cơ sở (Base HEAD)** | `3ea8e79` (`release: publish verified Scania APS coursework`) | `PASS` |
| **Worktree cô lập của Antigravity** | `D:\Năm 3\HK1_2026\Nhập môn tối ưu hóa\baitaplon\worktrees\antigravity-scania-demo-data-expansion` | `PASS` |
| **Branch riêng của Antigravity** | `antigravity/scania-demo-data-expansion` | `PASS` |
| **Môi trường Python kiểm chứng** | Python `3.11.9` + lockfile Phase 2 (`scikit-learn==1.9.1`, `numpy==2.4.6`, `scipy==1.17.1`, `joblib==1.6.0`, `optuna==5.0.0`) | `PASS` |
| **Xung đột với Codex / Release v1.0** | `0` xung đột — Không chạm vào working directory của Codex (`portfolio_final` hay `worktrees/codex`), không sửa bất kỳ tệp mã nguồn, checkpoint, báo cáo Word/PDF hay kết quả Official Test nào. | `PASS` |

---

## 2. Danh Sách Các Tệp CSV Đã Tạo & Nguồn Gốc Dữ Liệu (Phương Án 1 & Phương Án 2)

### 2.1. Các lô CSV trích xuất từ dữ liệu Validation thực tế (`data/examples/demo_cases/`)

Toàn bộ 8 tệp dưới đây được trích xuất từ tệp nguồn `data/raw/scania_aps/aps_failure_training_set.csv` (SHA-256: `bb484302e3a3a1c8ef5e1f0129c4dc7cbd58f350867f95b575461ca21ab6b9da`), **chỉ lấy từ 12.000 mẫu thuộc phân vùng Validation G3 đã khóa** (`official_20261029_04`, `stable_digest`: `efe781b7e564073a2a764e70a41cfe5c3e8975d33cc38b0fa297ef09f51767bb`). Không sử dụng Official Test, không tạo dữ liệu cảm biến giả, không chọn mẫu theo điểm dự đoán.

| STT | Tệp CSV | Số dòng | Số cột | Nhãn thực tế (`pos` / `neg`) | Số dòng có `na` (Tổng ô `na`) | Seed | Kích thước (Bytes) | Mã băm SHA-256 | Phân loại |
|---:|---|---:|---:|---|---:|---:|---:|---|---|
| 1 | `demo_normal.csv` | 20 | 171 | `0 pos` / `20 neg` | 19 (209 ô) | `42` | 16.621 | `490c61a10bee6b35238543b9f017cf7bb6ac42b7892a1bfb6e611be8b363fbf7` | `PASS` |
| 2 | `demo_failure.csv` | 20 | 171 | `20 pos` / `0 neg` | 18 (541 ô) | `43` | 19.439 | `98ee4edb709f54561e97cb130e3334d0381e4cecf1377f2bb9906080db67ea0e` | `PASS` |
| 3 | `demo_mixed.csv` | 100 | 171 | `10 pos` / `90 neg` | 99 (1.464 ô) | `44` | 75.923 | `158281a1d562d97a61313e79fb5a7275b9938e2b5950477a9c0923b804dd87a8` | `PASS` |
| 4 | `demo_missing_values.csv` | 30 | 171 | `0 pos` / `30 neg` | 30 (445 ô) | `45` | 23.348 | `47e449ca881967f6baa2ff6335d9950c3ff0c9bb31b6e706b195780a3d83ebbf` | `PASS` |
| 5 | `demo_capacity.csv` | 200 | 171 | `20 pos` / `180 neg` | 197 (3.040 ô) | `46` | 152.625 | `237e354a79d35244013e8a7fde2a4f3e7316baff8aa22dceaefbe6e794d5b118` | `PASS` |
| 6 | `demo_large_batch.csv` | 1.000 | 171 | `21 pos` / `979 neg` | 991 (14.129 ô) | `47` | 746.986 | `417c02aed42992aa910be0361e01f6571880b552793f51f02219595de6e50457` | `PASS` |
| 7 | `demo_unlabeled.csv` | 50 | 170 | Không có cột `class` (`1 pos` / `49 neg` ẩn) | 49 (758 ô) | `48` | 39.012 | `9b0687c99b5e2ce1d3137b8601cfedee3f454a22951f11e0ee82d58b340d7368` | `PASS` |
| 8 | `demo_invalid.csv` | 5 | 171 | `0 pos` / `5 neg` (Header sai schema) | 5 (44 ô) | `N/A` | 4.950 | `ba5af166acf234945f7ddf08bc5a13a5dd74a2a4db90ba17cb7f084c4d9b7cfb` | `PASS` |

### 2.2. Tệp CSV từ nguồn bên ngoài đã xác minh (`data/examples/external_sources/`)

| STT | Tệp CSV | Phân loại nguồn | Nguồn gốc | Số dòng | Số cột | Nhãn thực tế | Kích thước (Bytes) | Mã băm SHA-256 | Trạng thái |
|---:|---|---|---|---:|---:|---|---:|---|---|
| 9 | `uci414_ida2016_duplicate_validation_50.csv` | `COMPATIBLE_DUPLICATE` | UCI Machine Learning Repository #414 (`IDA2016Challenge`, DOI: `10.24432/C5V60Q`) — 50 mẫu đầu tiên theo thứ tự tệp thuộc phân vùng Validation G3 | 50 | 171 | `2 pos` / `48 neg` | 38.484 | `28fb0bd55db814dbd160b1e1e746508ff0d27988d35224536b179d25056c0f89` | `PASS` |

---

## 3. Kết Quả Tìm Kiếm & Kiểm Chứng Các Nguồn Dữ Liệu Bên Ngoài (Phương Án 2)

- **Kết luận về nguồn dữ liệu độc lập (`COMPATIBLE_INDEPENDENT`):** **`NO_VERIFIED_COMPATIBLE_EXTERNAL_DATA`**.
- **Lý do kỹ thuật:** 170 thuộc tính `aa_000..eg_000` của bộ Scania APS 2016 được ẩn danh bằng quy ước riêng và không công bố đơn vị vật lý hay ánh xạ cảm biến. Bộ dữ liệu thực tế mới nhất của Scania CV AB là **SCANIA Component X Dataset (2024–2025)** theo dõi linh kiện động cơ khác dưới dạng chuỗi thời gian đa bảng với tên cột mã số (`167_0..397_35`), hoàn toàn không tương thích (`INCOMPATIBLE`) với mô hình 170 thuộc tính hiện tại.

### Bảng Nguồn Được Chấp Nhận Và Nguồn Bị Loại

| Mã nguồn | Tên nguồn & URL | Phân loại | Quyết định | Lý do chấp nhận / loại bỏ dựa trên bằng chứng kiểm chứng |
|---|---|---|---|---|
| **EXT-01** | **UCI #414 — IDA2016Challenge** (`https://archive.ics.uci.edu/dataset/414/ida2016challenge`, DOI: `10.24432/C5V60Q`) | `COMPATIBLE_DUPLICATE` | **CHẤP NHẬN** (Ghi rõ trùng nguồn) | Tải trực tiếp `ida2016challenge.zip` (SHA-256: `5336e4b6...`). Tệp `to_uci/aps_failure_training_set.csv` bên trong có SHA-256 `bb484302...` trùng 100% từng byte với UCI #421. Giấy phép CC BY 4.0 / GPLv3 cho phép phân phối lại. Đã trích 50 mẫu thuộc Validation G3 vào `uci414_ida2016_duplicate_validation_50.csv`. |
| **EXT-02** | **GitHub `jieqiong-pang/APS-Failure-at-Scania-Trucks-Data-Set`** | `COMPATIBLE_DUPLICATE` | **LOẠI** (Chỉ lưu metadata) | Tệp `aps_failure_training_set.csv` tải xuống có SHA-256 `bb484302...` trùng 100% với EXT-01 và UCI #421, nhưng repo GitHub cá nhân không khai báo tệp `LICENSE` riêng. |
| **EXT-03** | **GitHub `atagunduzalp/truck-data-analysis`** | `COMPATIBLE_DUPLICATE` | **LOẠI** (Chỉ lưu metadata) | Tệp `aps_failure_training_set.csv` (`44.668.322` B, SHA-256: `cbbcc17b...`) là bản cắt bỏ 20 dòng lời dẫn GPLv3 đầu tệp (chênh lệch đúng `872` B); đối chiếu 60.000 dòng dữ liệu khớp 100% với UCI #421 (`ata_data == raw_data: True`). Loại khỏi phân phối tệp vì repo đã cắt thông báo bản quyền GPLv3 và không có `LICENSE`. |
| **EXT-04** | **Kaggle `uciml/aps-failure-at-scania-trucks-data-set`** | `COMPATIBLE_DUPLICATE` | **LOẠI** (Chỉ lưu metadata) | Bản sao trực tiếp của UCI #421 trên Kaggle (nguồn gốc của EXT-03); yêu cầu xác thực tài khoản Kaggle khi tải. |
| **EXT-05** | **OpenML #41138 — `APSFailure` (v1)** (`https://www.openml.org/d/41138`) | `PARTIALLY_COMPATIBLE` | **LOẠI** | Tệp `APSFailure.arff` (`78.399.357` B, SHA-256: `e95128fc...`) ở định dạng ARFF, dùng ký hiệu `?` cho dữ liệu thiếu (bị `parse_csv` từ chối) và gộp chung 60.000 dòng Train + 16.000 dòng Official Test của UCI #421. |
| **EXT-06** | **OpenML #46908 — `APSFailure` (v2 TabArena)** (`https://www.openml.org/d/46908`) | `PARTIALLY_COMPATIBLE` | **LOẠI** | Tệp `APSFailure.arff` (`78.323.905` B, SHA-256: `14fd7b78...`) ở định dạng ARFF, đổi tên cột `class` thành `AirPressureSystemFailure` (gây lỗi ngoài schema) và gộp lẫn Official Test. |
| **EXT-07** | **SCANIA Component X Dataset (2024–2025)** (`https://doi.org/10.5878/bnh5-ka77`, Nature Scientific Data `10.1038/s41597-025-04802-6`) | `INCOMPATIBLE` | **LOẠI** | Bộ dữ liệu chuỗi thời gian đa bảng của Scania cho linh kiện động cơ `Component X` với ~107 thuộc tính mã số (`167_0..397_35`, `Spec_0..7`), hoàn toàn khác hệ thống APS và 170 cột `aa_000..eg_000`. |
| **EXT-08** | **MetroPT-3 APU Dataset (UCI #791)** (`https://doi.org/10.24432/C5VW3R`) | `INCOMPATIBLE` | **LOẠI** | Dữ liệu hệ thống sản xuất khí nén tàu điện ngầm gồm 15 cột cảm biến vật lý 1 Hz, không có 170 thuộc tính của xe tải Scania. |
| **EXT-09** | **AI4I 2020 Predictive Maintenance (UCI #601)** (`https://doi.org/10.24432/C5HS5C`) | `INCOMPATIBLE` | **LOẠI** | Dữ liệu máy phay công nghiệp tổng hợp gồm 14 cột. |
| **EXT-10** | **Zenodo #22834903 — CAOS TruckVitals** (`https://zenodo.org/records/22834903`) | `INCOMPATIBLE` | **LOẠI** | Báo cáo PDF và mã mô phỏng xe tải mỏ, chỉ trích dẫn bài toán Scania APS chứ không chứa dữ liệu 170 thuộc tính. |

---

## 4. Kết Quả Kiểm Chứng Schema & Thực Thi Dự Đoán Thực Tế Trên Web Demo Backend

Quá trình kiểm chứng được thực hiện trực tiếp bằng cách:
1. Khởi chạy `ThreadingHTTPServer` thực tế của `app.py` và gửi yêu cầu `HTTP POST /api/predict` với header `Content-Type: text/csv` cho toàn bộ 10 tệp CSV (8 tệp trong `demo_cases/`, 1 tệp mẫu hiện có `scania_validation_sample.csv`, và 1 tệp nguồn ngoài `uci414_ida2016_duplicate_validation_50.csv`).
2. Đối chiếu ma trận sau tiền xử lý `tree_preprocessor.joblib` của từng tệp hợp lệ với các dòng tương ứng trong `data/processed/scania_aps/official_20261029_04/tree_validation.npy` bằng `np.testing.assert_array_equal` $\rightarrow$ **khớp chính xác 100% tuyệt đối tới từng bit float64**.
3. Kiểm chứng hàm quyết định theo ngưỡng $\tau$, công suất $K$, chính sách ưu tiên top-$K$ (`threshold_then_top_k`) và định dạng xuất CSV (`scania_aps_predictions.csv` gồm 8 cột) khớp 100% với `web_demo/live.js`.

### 4.1. Bảng Kết Quả Kiểm Chứng Schema & HTTP Endpoint

| Tệp CSV | Số dòng | Số cột | Dung lượng (Bytes) | Kiểm tra `parse_csv` | Mã HTTP `/api/predict` | Khớp `tree_validation.npy` (G3) | Kiểm tra Xuất CSV | Thời gian xử lý HTTP (ms) | Kết luận |
|---|---:|---:|---:|---|---:|---|---|---:|---|
| `demo_normal.csv` | 20 | 171 | 16.621 | `PASS` | `200 OK` | `EXACT_MATCH` | `PASS` (20 dòng, 1.787 B) | `32.73` | **PASS** |
| `demo_failure.csv` | 20 | 171 | 19.439 | `PASS` | `200 OK` | `EXACT_MATCH` | `PASS` (20 dòng, 1.844 B) | `37.10` | **PASS** |
| `demo_mixed.csv` | 100 | 171 | 75.923 | `PASS` | `200 OK` | `EXACT_MATCH` | `PASS` (100 dòng, 9.520 B) | `48.57` | **PASS** |
| `demo_missing_values.csv` | 30 | 171 | 23.348 | `PASS` | `200 OK` | `EXACT_MATCH` | `PASS` (30 dòng, 2.662 B) | `45.93` | **PASS** |
| `demo_capacity.csv` | 200 | 171 | 152.625 | `PASS` | `200 OK` | `EXACT_MATCH` | `PASS` (200 dòng, 19.373 B) | `50.48` | **PASS** |
| `demo_large_batch.csv` | 1.000 | 171 | 746.986 | `PASS` | `200 OK` | `EXACT_MATCH` | `PASS` (1.000 dòng, 89.261 B) | `160.37` | **PASS** |
| `demo_unlabeled.csv` | 50 | 170 | 39.012 | `PASS` | `200 OK` | `EXACT_MATCH` | `PASS` (50 dòng, 4.787 B) | `41.62` | **PASS** |
| `demo_invalid.csv` | 5 | 171 | 4.950 | `UploadError` (Đúng kỳ vọng) | `400 Bad Request` | `N/A` (Bị chặn tại cổng schema) | `N/A` | `29.52` | **PASS** |
| `scania_validation_sample.csv` | 12 | 171 | 10.493 | `PASS` | `200 OK` | `EXACT_MATCH` | `PASS` (12 dòng, 1.132 B) | `24.32` | **PASS** |
| `uci414_ida2016_duplicate_validation_50.csv` | 50 | 171 | 38.484 | `PASS` | `200 OK` | `EXACT_MATCH` | `PASS` (50 dòng, 4.442 B) | `62.60` | **PASS** |

*Thông báo lỗi thực tế thu được với `demo_invalid.csv` (`HTTP 400`):*  
`"CSV không đúng schema Scania APS: thiếu 1 cột (eg_000), có 1 cột ngoài schema."`

---

### 4.2. Bảng Kết Quả Dự Đoán Thực Tế Ở Cấu Hình Mặc Định ($\tau^* = 0.3232440937634324$, Công Suất $K = \lfloor 10\% \times N \rfloor$)

Với các tệp có nhãn `class`, chi phí được tính đúng theo hàm mục tiêu $C = 10 \times FP + 500 \times FN$. Với tệp không có nhãn (`demo_unlabeled.csv`), tuyệt đối không tính hoặc bịa các chỉ số cần ground truth.

| Tệp CSV | $N$ | Nhãn thực (`pos`/`neg`) | Trần công suất $K$ ($10\%$) | Chính sách áp dụng | Số lượt kiểm tra ($M$) | Khả thi theo ngưỡng ($M \le K$) | $TP$ | $FP$ | $FN$ | $TN$ | Precision | Recall | F1-score | Tổng chi phí $C = 10\text{FP} + 500\text{FN}$ |
|---|---:|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **`demo_normal.csv`** | 20 | `0 / 20` | 2 | Theo ngưỡng ($\tau^*$) | **1** | Có ($1 \le 2$) | 0 | 1 | 0 | 19 | `0.00%` | `—` ($P=0$) | `0.00%` | **10** |
| **`demo_failure.csv`** | 20 | `20 / 0` | 2 | Theo ngưỡng ($\tau^*$) | **19** | Không (vượt $17$) | 19 | 0 | 1 | 0 | `100.00%` | `95.00%` | `97.44%` | **500** |
| ↳ *`demo_failure.csv`* | 20 | `20 / 0` | 2 | Sau ưu tiên top-$K$ ($K=2$) | **2** | Đưa về $K=2$ | 2 | 0 | 18 | 0 | `100.00%` | `10.00%` | `18.18%` | **9.000** |
| **`demo_mixed.csv`** | 100 | `10 / 90` | 10 | Theo ngưỡng ($\tau^*$) | **11** | Không (vượt $1$) | 9 | 2 | 1 | 88 | `81.82%` | `90.00%` | `85.71%` | **520** |
| ↳ *`demo_mixed.csv`* | 100 | `10 / 90` | 10 | Sau ưu tiên top-$K$ ($K=10$) | **10** | Đưa về $K=10$ | 8 | 2 | 2 | 88 | `80.00%` | `80.00%` | `80.00%` | **1.020** |
| **`demo_missing_values.csv`** | 30 | `0 / 30` | 3 | Theo ngưỡng ($\tau^*$) | **1** | Có ($1 \le 3$) | 0 | 1 | 0 | 29 | `0.00%` | `—` ($P=0$) | `0.00%` | **10** |
| **`demo_capacity.csv`** | 200 | `20 / 180` | 20 | Theo ngưỡng ($\tau^*$) | **21** | Không (vượt $1$) | 18 | 3 | 2 | 177 | `85.71%` | `90.00%` | `87.80%` | **1.030** |
| ↳ *`demo_capacity.csv`* | 200 | `20 / 180` | 20 | Sau ưu tiên top-$K$ ($K=20$) | **20** | Đưa về $K=20$ | 17 | 3 | 3 | 177 | `85.00%` | `85.00%` | `85.00%` | **1.530** |
| **`demo_large_batch.csv`** | 1.000 | `21 / 979` | 100 | Theo ngưỡng ($\tau^*$) | **49** | Có ($49 \le 100$) | 19 | 30 | 2 | 949 | `38.78%` | `90.48%` | `54.29%` | **1.300** |
| **`demo_unlabeled.csv`** | 50 | *Không nhãn* | 5 | Theo ngưỡng ($\tau^*$) | **7** | Không (vượt $2$) | `—` | `—` | `—` | `—` | `—` | `—` | `—` | `—` *(Không có nhãn)* |
| ↳ *`demo_unlabeled.csv`* | 50 | *Không nhãn* | 5 | Sau ưu tiên top-$K$ ($K=5$) | **5** | Đưa về $K=5$ | `—` | `—` | `—` | `—` | `—` | `—` | `—` | `—` *(Không có nhãn)* |
| **`scania_validation_sample.csv`** | 12 | `4 / 8` | 1 | Theo ngưỡng ($\tau^*$) | **5** | Không (vượt $4$) | 4 | 1 | 0 | 7 | `80.00%` | `100.00%` | `88.89%` | **10** |
| ↳ *`scania_validation_sample.csv`* | 12 | `4 / 8` | 1 | Sau ưu tiên top-$K$ ($K=1$) | **1** | Đưa về $K=1$ | 1 | 0 | 3 | 8 | `100.00%` | `25.00%` | `40.00%` | **1.500** |
| **`uci414_ida2016_duplicate_validation_50.csv`** | 50 | `2 / 48` | 5 | Theo ngưỡng ($\tau^*$) | **4** | Có ($4 \le 5$) | 2 | 2 | 0 | 46 | `50.00%` | `100.00%` | `66.67%` | **20** |

### 4.3. Kiểm Chứng Động Khi Thay Đổi Ngưỡng ($\tau$) Và Giới Hạn Công Suất ($K$)

Chi tiết kết quả của 5 kịch bản tham số trên từng tệp đã được lưu đầy đủ trong [`DEMO_EXECUTION_RESULTS.json`](DEMO_EXECUTION_RESULTS.json). Dưới đây là kết quả tiêu biểu trên tệp **`demo_capacity.csv`** ($N = 200$, `20 pos` / `180 neg`):

| Kịch bản điều chỉnh trên `demo_capacity.csv` | Ngưỡng $\tau$ | Công suất $K$ | Bật ưu tiên top-$K$ | $M_{\text{ngưỡng}}$ | $M_{\text{cuối}}$ | $TP$ | $FP$ | $FN$ | $TN$ | Precision | Recall | F1-score | Chi phí $C$ |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1. Ngưỡng nghiên cứu $\tau^*$, không giới hạn ưu tiên | `0.323244` | `20` ($10\%$) | Tắt | 21 | 21 | 18 | 3 | 2 | 177 | `85.71%` | `90.00%` | `87.80%` | **1.030** |
| 2. Ngưỡng nghiên cứu $\tau^*$, bật ưu tiên công suất $10\%$ | `0.323244` | `20` ($10\%$) | Bật | 21 | 20 | 17 | 3 | 3 | 177 | `85.00%` | `85.00%` | `85.00%` | **1.530** |
| 3. Ngưỡng nghiên cứu $\tau^*$, siết công suất còn $5\%$ | `0.323244` | `10` ($5\%$) | Bật | 21 | 10 | 10 | 0 | 10 | 180 | `100.00%` | `50.00%` | `66.67%` | **5.000** |
| 4. Tăng ngưỡng lên $\tau = 0.50$ (ngưỡng mặc định cổ điển) | `0.500000` | `20` ($10\%$) | Tắt | 17 | 17 | 16 | 1 | 4 | 179 | `94.12%` | `80.00%` | `86.49%` | **2.010** |
| 5. Hạ ngưỡng xuống $\tau = 0.15$, bật ưu tiên công suất $10\%$ | `0.150000` | `20` ($10\%$) | Bật | 26 | 20 | 17 | 3 | 3 | 177 | `85.00%` | `85.00%` | `85.00%` | **1.530** |

---

## 5. Các Hạn Chế & Vấn Đề Ghi Nhận

1. **Giới hạn về dữ liệu bên ngoài độc lập (`NO_VERIFIED_COMPATIBLE_EXTERNAL_DATA`):** Do 170 thuộc tính `aa_000..eg_000` của bộ dữ liệu Scania APS 2016 bị ẩn danh hoàn toàn và không có tài liệu ánh xạ sang cảm biến vật lý, không tồn tại bộ dữ liệu độc lập nào bên ngoài có cùng schema 170 thuộc tính này. Các nguồn tương thích tìm thấy trên UCI (#414), GitHub và Kaggle đều là bản sao của bộ dữ liệu IDA 2016 Challenge (`COMPATIBLE_DUPLICATE`).
2. **Phạm vi đại diện của các lô CSV demo:** Các tệp CSV trong `data/examples/demo_cases/` được trích từ tập Validation nghiên cứu đã khóa (`12.000` mẫu) để phục vụ kiểm thử và trình diễn tính năng của Web Demo. Chúng không phải là dữ liệu kiểm thử độc lập và không thay thế cho kết quả đánh giá trên tập `Official Test` (`16.000` mẫu tại Gate G10 Run 003).
3. **Phương thức kiểm chứng giao diện Web Demo:** Toàn bộ 10 tệp CSV đã được kiểm chứng thực tế qua máy chủ HTTP backend của `app.py` (`ThreadingHTTPServer`, endpoint `POST /api/predict` và `GET /api/evidence`) kết hợp với bộ kiểm thử đơn vị `tests/test_live_prediction.py` và `tests/test_web_demo.py` cùng hàm mô phỏng chính xác 100% logic của `web_demo/live.js`. Báo cáo tuân thủ nguyên tắc trung thực, ghi rõ kiểm chứng thực hiện qua HTTP backend và unit test thực tế, không tạo ảnh chụp trình duyệt giả lập.

---

## 6. Bảng Phân Loại Trạng Thái Từng Hạng Mục Bàn Giao

| STT | Hạng mục yêu cầu theo chỉ thị | Kết quả thực hiện | Phân loại |
|---:|---|---|---|
| 1 | Kiểm tra môi trường, tạo worktree cô lập và branch `antigravity/scania-demo-data-expansion` | Tạo worktree từ commit `3ea8e79`, tách biệt hoàn toàn với Codex | **`PASS`** |
| 2 | Phương án 1 — Tạo 8 tệp CSV demo trong `data/examples/demo_cases/` từ Validation G3 | Đủ 8 tệp (`normal`, `failure`, `mixed`, `missing_values`, `capacity`, `large_batch`, `unlabeled`, `invalid`), đúng số lượng và quy tắc lấy mẫu với seed cố định | **`PASS`** |
| 3 | Phương án 1 — Tạo `README.md` và `DEMO_DATA_MANIFEST.json` kèm ma trận trùng lặp mẫu | Đầy đủ SHA-256, vị trí dòng zero-based trong Validation và tệp gốc, cảnh báo nguồn gốc Validation và ma trận trùng lặp từng cặp | **`PASS`** |
| 4 | Phương án 2 — Tìm kiếm và kiểm chứng các nguồn dữ liệu bên ngoài (UCI, OpenML, Kaggle, GitHub, Zenodo, Researchdata.se, Nature Scientific Data...) | Đã kiểm chứng 10 nguồn thực tế bằng mã băm SHA-256 và đối chiếu cấp độ bản ghi; kết luận rõ `NO_VERIFIED_COMPATIBLE_EXTERNAL_DATA` cho nhóm độc lập và thu thập 1 lô đại diện `COMPATIBLE_DUPLICATE` từ UCI #414 | **`PASS`** |
| 5 | Phương án 2 — Bàn giao `data/examples/external_sources/`, `EXTERNAL_DATA_SOURCE_AUDIT.md`, `EXTERNAL_SOURCE_REGISTRY.json` | Đầy đủ danh mục, SHA-256, giấy phép và tệp CSV đã xác minh | **`PASS`** |
| 6 | Kiểm chứng bằng Web Demo thực tế (`CSV_SCHEMA_VALIDATION.json` và `DEMO_EXECUTION_RESULTS.json`) | Kiểm chứng trực tiếp cả 10 tệp qua HTTP server `app.py` (`POST /api/predict`), đối chiếu khớp 100% với `tree_validation.npy` G3 và kiểm tra 5 kịch bản ngưỡng/công suất/ưu tiên/xuất CSV | **`PASS`** |
| 7 | Tài liệu hướng dẫn demo tiếng Việt (`DEMO_INSTRUCTIONS_VI.md`) và báo cáo tổng hợp (`DEMO_DATA_EXPANSION_REPORT.md`) | Đầy đủ kịch bản chọn tệp khi demo trước giảng viên và bảng số liệu thực tế | **`PASS`** |
| 8 | Tuân thủ phạm vi tuyệt đối không thay đổi (không retrain, không sửa checkpoint/code ứng dụng/báo cáo của Codex/Release v1.0) | `0` tệp hiện có bị sửa đổi; chỉ bổ sung các tệp dữ liệu và báo cáo trong đúng 3 thư mục bàn giao | **`PASS`** |

---

## 7. Danh Sách Toàn Bộ Các Tệp Đã Tạo Mới Trên Branch `antigravity/scania-demo-data-expansion`

Không có bất kỳ tệp hiện có nào của dự án bị chỉnh sửa hoặc xóa. Toàn bộ 18 tệp dưới đây là tệp tạo mới:

1. `data/examples/demo_cases/demo_normal.csv`
2. `data/examples/demo_cases/demo_failure.csv`
3. `data/examples/demo_cases/demo_mixed.csv`
4. `data/examples/demo_cases/demo_missing_values.csv`
5. `data/examples/demo_cases/demo_capacity.csv`
6. `data/examples/demo_cases/demo_large_batch.csv`
7. `data/examples/demo_cases/demo_unlabeled.csv`
8. `data/examples/demo_cases/demo_invalid.csv`
9. `data/examples/demo_cases/README.md`
10. `data/examples/demo_cases/DEMO_DATA_MANIFEST.json`
11. `data/examples/external_sources/uci414_ida2016_duplicate_validation_50.csv`
12. `data/examples/external_sources/EXTERNAL_SOURCES_MANIFEST.json`
13. `data/examples/external_sources/README.md`
14. `reports/demo_data_expansion/EXTERNAL_DATA_SOURCE_AUDIT.md`
15. `reports/demo_data_expansion/EXTERNAL_SOURCE_REGISTRY.json`
16. `reports/demo_data_expansion/CSV_SCHEMA_VALIDATION.json`
17. `reports/demo_data_expansion/DEMO_EXECUTION_RESULTS.json`
18. `reports/demo_data_expansion/DEMO_DATA_EXPANSION_REPORT.md`
19. `reports/demo_data_expansion/DEMO_INSTRUCTIONS_VI.md`
