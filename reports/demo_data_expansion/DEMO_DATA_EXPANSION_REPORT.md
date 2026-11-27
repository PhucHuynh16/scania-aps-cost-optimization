# Báo Cáo Nghiệm Thu Cuối Cùng — Mở Rộng Dữ Liệu CSV Demo & Kiểm Chứng Nguồn Dữ Liệu Bên Ngoài (Scania APS UCI #421)

**Dự án:** Tối ưu hóa chi phí bảo trì dự đoán hệ thống khí nén xe tải Scania APS (`UCI #421`)  
**Tác tử thực hiện:** Antigravity  
**Chế độ thực thi:** Song song với Codex trên worktree và branch cô lập  
**Ngày nghiệm thu:** `2026-11-27`  
**Trạng thái tổng thể:** **`READY FOR OWNER REVIEW`**

---

## 1. Môi Trường Thực Thi, Worktree, Branch & Kiểm Tra Tương Thích Phiên Bản Mới Nhất

| Hạng mục | Giá trị xác minh thực tế | Trạng thái |
|---|---|---|
| **Repository chính** | `D:\Năm 3\HK1_2026\Nhập môn tối ưu hóa\baitaplon\portfolio_final` (`https://github.com/PhucHuynh16/scania-aps-cost-optimization.git`) | **`PASS`** |
| **Commit cơ sở (Release v1.0 tag)** | `3ea8e79` (`release: publish verified Scania APS coursework`, tag `v1.0`) | **`PASS`** |
| **HEAD mới nhất của `origin/main`** | `f55e043` (`Delete slides directory` — chỉ xóa 3 tệp trong `slides/`, không thay đổi bất kỳ tệp mã nguồn, dữ liệu, mô hình hay Web Demo nào so với `3ea8e79`) | **`PASS`** |
| **Worktree cô lập của Antigravity** | `D:\Năm 3\HK1_2026\Nhập môn tối ưu hóa\baitaplon\worktrees\antigravity-scania-demo-data-expansion` | **`PASS`** |
| **Branch riêng của Antigravity** | `antigravity/scania-demo-data-expansion` (Draft PR #1: `https://github.com/PhucHuynh16/scania-aps-cost-optimization/pull/1`) | **`PASS`** |
| **Môi trường Python kiểm chứng** | Python `3.11.9` + lockfile Phase 2 (`scikit-learn==1.9.1`, `numpy==2.4.6`, `scipy==1.17.1`, `joblib==1.6.0`, `optuna==5.0.0`) | **`PASS`** |
| **Xung đột với Codex / Release v1.0** | `0` xung đột — Không chạm vào working directory của Codex (`portfolio_final` hay `worktrees/codex`), không sửa bất kỳ tệp mã nguồn, checkpoint, báo cáo Word/PDF hay kết quả Official Test nào. | **`PASS`** |

### Đối chiếu tính tương thích giữa phiên bản Antigravity đã kiểm tra, `main` (`v1.0`) và workspace của Codex

Đã kiểm tra trực tiếp mã băm SHA-256 và `git diff` giữa worktree của Antigravity (`antigravity/scania-demo-data-expansion`), nhánh `main` cục bộ (`3ea8e79` / tag `v1.0`), `origin/main` (`f55e043`) và thư mục làm việc `portfolio_final` của Codex:

1. **Hợp đồng 170 thuộc tính (`src/scania/contracts.py`):** Khớp tuyệt đối 100% (`FEATURES` gồm 170 cột `aa_000..eg_000`, `SCHEMA_SHA256 = fb832a2c220bdcd38d970a1dba34bb1e3d1d08900490e4b258a21b9c6d50f634`).
2. **Cấu hình và Checkpoint mô hình (`configs/scania/live_model.json` & `results/scania_aps/rf_supplement/trial16_refit_20261127_02/`):** Khớp tuyệt đối 100% (`model_version = trial16_refit_20261127_02`, `manifest_sha256 = 3a657ea6e21da8eb565c812d35499b396416435250de52209c69c684a4d955d0`, ngưỡng đã khóa $\tau^* = 0.3232440937634324$).
3. **Bộ tiền xử lý G3 (`data/processed/scania_aps/official_20261029_04/tree_preprocessor.joblib`):** Khớp tuyệt đối 100% (SHA-256: `b23a955a54e453f250b55b95e61cc0fce445a231bdc4a830de55d18f1b3e7ada`).
4. **API dự đoán và giao diện Web Demo (`app.py`, `src/scania/live_prediction.py`, `web_demo/index.html`, `web_demo/live.js`, `web_demo/dashboard.js`):** `0` dòng khác biệt giữa worktree Antigravity, `3ea8e79` (`v1.0`) và `origin/main` (`f55e043`). Trong thư mục `portfolio_final`, Codex chỉ có thư mục ảnh biểu đồ báo cáo chưa theo dõi `figures/report/` (phục vụ xuất báo cáo Word/PDF ở thư mục cha), hoàn toàn không sửa đổi `app.py`, schema, checkpoint, preprocessor hay API `/api/predict`.
5. **Yêu cầu kiểm thử tích hợp lại (Re-integration Test Note):** Trường hợp sau thời điểm này Codex có bất kỳ commit bổ sung nào vào `main` làm thay đổi giao diện hoặc tài liệu trước khi chốt hợp nhất, cần chạy lại 3 lệnh kiểm chứng chuẩn (`python app.py --verify`, `unittest test_live_prediction.py`, `unittest test_web_demo.py`) sau khi rebase/merge để đảm bảo tính tương thích toàn cục.

---

## 2. Danh Sách Các Tệp CSV Đã Tạo, Nguồn Gốc, Bản Quyền & Lý Do Thiết Kế

### 2.1. Các lô CSV trích xuất từ dữ liệu Validation thực tế (`data/examples/demo_cases/`)

Toàn bộ 8 tệp dưới đây được trích xuất từ tệp nguồn `data/raw/scania_aps/aps_failure_training_set.csv` (SHA-256: `bb484302e3a3a1c8ef5e1f0129c4dc7cbd58f350867f95b575461ca21ab6b9da`), **chỉ lấy từ 12.000 mẫu thuộc phân vùng Validation G3 đã khóa** (`official_20261029_04`, `stable_digest`: `efe781b7e564073a2a764e70a41cfe5c3e8975d33cc38b0fa297ef09f51767bb`). Không sử dụng bất kỳ bản ghi nào từ Official Test (`16.000` mẫu), không tạo dữ liệu cảm biến giả, không chọn mẫu theo điểm dự đoán.

| STT | Tệp CSV | Số dòng | Số cột | Nhãn thực tế (`pos` / `neg`) | Số dòng có `na` (Tổng ô `na`) | Seed | Kích thước (Bytes) | Mã băm SHA-256 | Phân loại |
|---:|---|---:|---:|---|---:|---:|---:|---|---|
| 1 | `demo_normal.csv` | 20 | 171 | `0 pos` / `20 neg` | 19 (209 ô) | `42` | 16.621 | `490c61a10bee6b35238543b9f017cf7bb6ac42b7892a1bfb6e611be8b363fbf7` | **`PASS`** |
| 2 | `demo_failure.csv` | 20 | 171 | `20 pos` / `0 neg` | 18 (541 ô) | `43` | 19.439 | `98ee4edb709f54561e97cb130e3334d0381e4cecf1377f2bb9906080db67ea0e` | **`PASS`** |
| 3 | `demo_mixed.csv` | 100 | 171 | `10 pos` / `90 neg` | 99 (1.464 ô) | `44` | 75.923 | `158281a1d562d97a61313e79fb5a7275b9938e2b5950477a9c0923b804dd87a8` | **`PASS`** |
| 4 | `demo_missing_values.csv` | 30 | 171 | `0 pos` / `30 neg` | 30 (445 ô) | `45` | 23.348 | `47e449ca881967f6baa2ff6335d9950c3ff0c9bb31b6e706b195780a3d83ebbf` | **`PASS`** |
| 5 | `demo_capacity.csv` | 200 | 171 | `20 pos` / `180 neg` | 197 (3.040 ô) | `46` | 152.625 | `237e354a79d35244013e8a7fde2a4f3e7316baff8aa22dceaefbe6e794d5b118` | **`PASS`** |
| 6 | `demo_large_batch.csv` | 1.000 | 171 | `21 pos` / `979 neg` | 991 (14.129 ô) | `47` | 746.986 | `417c02aed42992aa910be0361e01f6571880b552793f51f02219595de6e50457` | **`PASS`** |
| 7 | `demo_unlabeled.csv` | 50 | 170 | Không có cột `class` (`1 pos` / `49 neg` ẩn) | 49 (758 ô) | `48` | 39.012 | `9b0687c99b5e2ce1d3137b8601cfedee3f454a22951f11e0ee82d58b340d7368` | **`PASS`** |
| 8 | `demo_invalid.csv` | 5 | 171 | `0 pos` / `5 neg` (Header sai schema) | 5 (44 ô) | `N/A` | 4.950 | `ba5af166acf234945f7ddf08bc5a13a5dd74a2a4db90ba17cb7f084c4d9b7cfb` | **`PASS`** |

- **Giải thích việc `demo_invalid.csv` sử dụng 5 dòng dữ liệu (thay vì 10 dòng theo gợi ý ban đầu):** Trong `src/scania/live_prediction.py` (`parse_csv`, dòng 38–52), trình kiểm tra hợp đồng dữ liệu đọc dòng header đầu tiên (dòng 1) và lập tức ném lỗi `UploadError("CSV không đúng schema Scania APS: thiếu 1 cột (eg_000), có 1 cột ngoài schema.")` trước khi đọc xuống bất kỳ dòng dữ liệu nào. Do lỗi schema cột được quyết định 100% tại dòng header, việc sử dụng 5 dòng dữ liệu đầu tiên của tập Validation (`validation_positions_zero_based = [0, 1, 2, 3, 4]`) là vừa đủ để tạo một tệp CSV nhiều dòng hợp lệ về cú pháp nhưng sai schema, giữ tệp nhỏ gọn (`4.950` bytes) và đã được ghi rõ trong `DEMO_DATA_MANIFEST.json` (`row_count_rationale`).

### 2.2. Tệp CSV từ nguồn bên ngoài đã xác minh (`data/examples/external_sources/`)

| STT | Tệp CSV | Phân loại nguồn | Nguồn gốc | Số dòng | Số cột | Nhãn thực tế | Kích thước (Bytes) | Mã băm SHA-256 | Trạng thái |
|---:|---|---|---|---:|---:|---|---:|---|---|
| 9 | `uci414_ida2016_duplicate_validation_50.csv` | `COMPATIBLE_DUPLICATE` | UCI Machine Learning Repository #414 (`IDA2016Challenge`, DOI: `10.24432/C5V60Q`) — 50 mẫu đầu tiên theo thứ tự tệp thuộc phân vùng Validation G3 | 50 | 171 | `2 pos` / `48 neg` | 38.484 | `28fb0bd55db814dbd160b1e1e746508ff0d27988d35224536b179d25056c0f89` | **`PASS`** |

- **Xác nhận không coi UCI #414 là dữ liệu độc lập:** Tệp `to_uci/aps_failure_training_set.csv` bên trong gói `ida2016challenge.zip` của UCI #414 có mã băm SHA-256 `bb484302e3a3a1c8ef5e1f0129c4dc7cbd58f350867f95b575461ca21ab6b9da`, trùng khớp 100% từng byte với tệp `aps_failure_training_set.csv` của UCI #421. Do đó, tệp `uci414_ida2016_duplicate_validation_50.csv` được phân loại nghiêm ngặt là **`COMPATIBLE_DUPLICATE` (bản sao trùng nguồn gốc UCI, tuyệt đối không phải dữ liệu độc lập)**.
- **Giấy phép, thông báo bản quyền và nghĩa vụ ghi nguồn:** Toàn bộ các tệp CSV phân phối lại đều bắt nguồn từ bộ dữ liệu của **Scania CV AB (`Copyright (c) 2016 Scania CV AB`, Donors: Tony Lindgren & Jonas Biteus)**, được phát hành trên UCI Machine Learning Repository dưới giấy phép **CC BY 4.0** kèm thông báo **GNU General Public License v3 (or later)** trong [`data/raw/scania_aps/aps_failure_description.txt`](../../data/raw/scania_aps/aps_failure_description.txt). Thông báo bản quyền, DOI (`10.24432/C51S51`, `10.24432/C5V60Q`) và nghĩa vụ ghi nguồn đã được ghi nhận đầy đủ trong `README.md` và `EXTERNAL_SOURCES_MANIFEST.json`.

---

## 3. Kết Quả Tìm Kiếm & Kiểm Chứng Các Nguồn Dữ Liệu Bên Ngoài (Phương Án 2)

- **Kết luận về nguồn dữ liệu độc lập (`COMPATIBLE_INDEPENDENT`):** **`NO_VERIFIED_COMPATIBLE_EXTERNAL_DATA`** — **Chưa tìm thấy nguồn độc lập tương thích trong phạm vi khảo sát** (bao gồm UCI Machine Learning Repository, OpenML, Kaggle, GitHub, Zenodo, Researchdata.se / Swedish National Data Service, Nature Scientific Data, Figshare, Mendeley Data và IEEE DataPort).
- **Lý do kỹ thuật:** 170 thuộc tính `aa_000..eg_000` của bộ Scania APS 2016 được ẩn danh bằng quy ước riêng và không công bố đơn vị vật lý hay ánh xạ cảm biến. Bộ dữ liệu thực tế mới nhất của Scania CV AB là **SCANIA Component X Dataset (2024–2025)** theo dõi linh kiện động cơ khác dưới dạng chuỗi thời gian đa bảng với tên cột mã số (`167_0..397_35`), không tương thích (`INCOMPATIBLE`) với mô hình 170 thuộc tính hiện tại.

### Bảng Nguồn Được Chấp Nhận Và Nguồn Bị Loại Trong Phạm Vi Khảo Sát

| Mã nguồn | Tên nguồn & URL | Phân loại | Quyết định | Lý do chấp nhận / loại bỏ dựa trên bằng chứng kiểm chứng |
|---|---|---|---|---|
| **EXT-01** | **UCI #414 — IDA2016Challenge** (`https://archive.ics.uci.edu/dataset/414/ida2016challenge`, DOI: `10.24432/C5V60Q`) | `COMPATIBLE_DUPLICATE` | **CHẤP NHẬN** *(Ghi rõ trùng nguồn)* | Tải trực tiếp `ida2016challenge.zip` (SHA-256: `5336e4b6...`). Tệp `to_uci/aps_failure_training_set.csv` bên trong có SHA-256 `bb484302...` trùng 100% từng byte với UCI #421. Giấy phép CC BY 4.0 / GPLv3 cho phép phân phối lại. Đã trích 50 mẫu thuộc Validation G3 vào `uci414_ida2016_duplicate_validation_50.csv`. |
| **EXT-02** | **GitHub `jieqiong-pang/APS-Failure-at-Scania-Trucks-Data-Set`** | `COMPATIBLE_DUPLICATE` | **LOẠI** *(Chỉ lưu metadata)* | Tệp `aps_failure_training_set.csv` tải xuống có SHA-256 `bb484302...` trùng 100% với EXT-01 và UCI #421, nhưng repo GitHub cá nhân không khai báo tệp `LICENSE` riêng. |
| **EXT-03** | **GitHub `atagunduzalp/truck-data-analysis`** | `COMPATIBLE_DUPLICATE` | **LOẠI** *(Chỉ lưu metadata)* | Tệp `aps_failure_training_set.csv` (`44.668.322` B, SHA-256: `cbbcc17b...`) là bản cắt bỏ 20 dòng lời dẫn GPLv3 đầu tệp (chênh lệch đúng `872` B); đối chiếu 60.000 dòng dữ liệu khớp 100% với UCI #421 (`ata_data == raw_data: True`). Loại khỏi phân phối tệp vì repo đã cắt thông báo bản quyền GPLv3 và không có `LICENSE`. |
| **EXT-04** | **Kaggle `uciml/aps-failure-at-scania-trucks-data-set`** | `COMPATIBLE_DUPLICATE` | **LOẠI** *(Chỉ lưu metadata)* | Bản sao trực tiếp của UCI #421 trên Kaggle (nguồn gốc của EXT-03); yêu cầu xác thực tài khoản Kaggle khi tải. |
| **EXT-05** | **OpenML #41138 — `APSFailure` (v1)** (`https://www.openml.org/d/41138`) | `PARTIALLY_COMPATIBLE` | **LOẠI** | Tệp `APSFailure.arff` (`78.399.357` B, SHA-256: `e95128fc...`) ở định dạng ARFF, dùng ký hiệu `?` cho dữ liệu thiếu (bị `parse_csv` từ chối) và gộp chung 60.000 dòng Train + 16.000 dòng Official Test của UCI #421. |
| **EXT-06** | **OpenML #46908 — `APSFailure` (v2 TabArena)** (`https://www.openml.org/d/46908`) | `PARTIALLY_COMPATIBLE` | **LOẠI** | Tệp `APSFailure.arff` (`78.323.905` B, SHA-256: `14fd7b78...`) ở định dạng ARFF, đổi tên cột `class` thành `AirPressureSystemFailure` (gây lỗi ngoài schema) và gộp lẫn Official Test. |
| **EXT-07** | **SCANIA Component X Dataset (2024–2025)** (`https://doi.org/10.5878/bnh5-ka77`, Nature Scientific Data `10.1038/s41597-025-04802-6`) | `INCOMPATIBLE` | **LOẠI** | Bộ dữ liệu chuỗi thời gian đa bảng của Scania cho linh kiện động cơ `Component X` với ~107 thuộc tính mã số (`167_0..397_35`, `Spec_0..7`), hoàn toàn khác hệ thống APS và 170 cột `aa_000..eg_000`. |
| **EXT-08** | **MetroPT-3 APU Dataset (UCI #791)** (`https://doi.org/10.24432/C5VW3R`) | `INCOMPATIBLE` | **LOẠI** | Dữ liệu hệ thống sản xuất khí nén tàu điện ngầm gồm 15 cột cảm biến vật lý 1 Hz, không có 170 thuộc tính của xe tải Scania. |
| **EXT-09** | **AI4I 2020 Predictive Maintenance (UCI #601)** (`https://doi.org/10.24432/C5HS5C`) | `INCOMPATIBLE` | **LOẠI** | Dữ liệu máy phay công nghiệp tổng hợp gồm 14 cột. |
| **EXT-10** | **Zenodo #22834903 — CAOS TruckVitals** (`https://zenodo.org/records/22834903`) | `INCOMPATIBLE` | **LOẠI** | Báo cáo PDF và mã mô phỏng xe tải mỏ, chỉ trích dẫn bài toán Scania APS chứ không chứa dữ liệu 170 thuộc tính. |

---

## 4. Kết Quả Kiểm Chứng Trực Tiếp Trên Giao Diện Trình Duyệt Web Demo & HTTP Backend

Quá trình kiểm chứng đã được thực hiện đầy đủ trên cả **giao diện trình duyệt thực tế** (`http://localhost:8517`, cổng riêng không xung đột với Codex) lẫn **HTTP backend & unit tests**:
1. **Kiểm chứng trình duyệt thực tế (Live Browser UI Verification):** Khởi động `python app.py --port 8517` trong worktree riêng và điều khiển trình duyệt mở `http://localhost:8517` (xác nhận trạng thái header `32 / 32 artifact đã xác minh`), chuyển sang tab **Dự đoán CSV** (`button[data-tab="live"]`), lần lượt kiểm tra toàn bộ **10/10 tệp CSV** (1 CSV mẫu ban đầu qua nút `#live-sample` + 9 CSV bổ sung qua `#live-file` và `#live-upload`). Đã kiểm chứng trực tiếp thao tác đổi ngưỡng `#live-threshold`, đổi đơn vị/giới hạn công suất (`#live-mode`, `#live-capacity`), bật/tắt ưu tiên Top-$K$ (`#live-prioritize`), hiển thị bảng chỉ số `#live-metrics`, ma trận nhầm lẫn `#live-matrix`, bảng kết quả từng dòng `#live-rows` và nhấn nút **Xuất CSV kết quả** (`#live-export` tải xuống `scania_aps_predictions.csv`).
2. **Bằng chứng ảnh chụp màn hình trình duyệt thực tế (`reports/demo_data_expansion/screenshots/`):** Đã lưu 14 ảnh chụp màn hình thực tế từ trình duyệt (bao gồm cả các ảnh cuộn khung dưới hiển thị rõ ma trận nhầm lẫn, chỉ số Recall `—` khi $P=0$, bảng từng dòng và nút xuất CSV).
3. **Đối chiếu khớp tuyệt đối giữa JSON, CSV xuất ra, Giao diện Web và `tree_validation.npy` (G3):** Mọi giá trị điểm dự đoán, $TP, FP, FN, TN, \text{Precision}, \text{Recall}, F1$, công suất $K$, số đề xuất $M$ và chi phí $C$ trên giao diện trình duyệt khớp 100% với [`DEMO_EXECUTION_RESULTS.json`](DEMO_EXECUTION_RESULTS.json), [`CSV_SCHEMA_VALIDATION.json`](CSV_SCHEMA_VALIDATION.json) và tệp CSV xuất ra.

### 4.1. Bảng Kết Quả Kiểm Chứng Schema, HTTP Endpoint & Bằng Chứng Ảnh Chụp Giao Diện

| Tệp CSV | Số dòng | Số cột | Dung lượng (B) | Kiểm tra `parse_csv` | Mã HTTP `/api/predict` | Khớp `tree_validation.npy` | Xuất CSV (`#live-export`) | Ảnh chụp giao diện trình duyệt thực tế (`reports/demo_data_expansion/screenshots/`) | Kết luận |
|---|---:|---:|---:|---|---:|---|---|---|---|
| `scania_validation_sample.csv` | 12 | 171 | 10.493 | `PASS` | `200 OK` | `EXACT_MATCH` | `PASS` (1.132 B) | [`01_scania_validation_sample.png`](screenshots/01_scania_validation_sample.png) | **`PASS`** |
| `demo_normal.csv` | 20 | 171 | 16.621 | `PASS` | `200 OK` | `EXACT_MATCH` | `PASS` (1.787 B) | [`02_demo_normal.png`](screenshots/02_demo_normal.png), [`12_demo_normal_metrics_matrix.png`](screenshots/12_demo_normal_metrics_matrix.png) | **`PASS`** |
| `demo_failure.csv` | 20 | 171 | 19.439 | `PASS` | `200 OK` | `EXACT_MATCH` | `PASS` (1.844 B) | [`03_demo_failure_priority.png`](screenshots/03_demo_failure_priority.png) | **`PASS`** |
| `demo_mixed.csv` | 100 | 171 | 75.923 | `PASS` | `200 OK` | `EXACT_MATCH` | `PASS` (9.520 B) | [`04_demo_mixed_priority.png`](screenshots/04_demo_mixed_priority.png) | **`PASS`** |
| `demo_missing_values.csv` | 30 | 171 | 23.348 | `PASS` | `200 OK` | `EXACT_MATCH` | `PASS` (2.662 B) | [`05_demo_missing_values.png`](screenshots/05_demo_missing_values.png) | **`PASS`** |
| `demo_capacity.csv` | 200 | 171 | 152.625 | `PASS` | `200 OK` | `EXACT_MATCH` | `PASS` (19.373 B) | [`06a_demo_capacity_default_priority.png`](screenshots/06a_demo_capacity_default_priority.png), [`06b_demo_capacity_custom_and_export.png`](screenshots/06b_demo_capacity_custom_and_export.png), [`11_demo_capacity_metrics_matrix_rows.png`](screenshots/11_demo_capacity_metrics_matrix_rows.png) | **`PASS`** |
| `demo_large_batch.csv` | 1.000 | 171 | 746.986 | `PASS` | `200 OK` | `EXACT_MATCH` | `PASS` (89.261 B) | [`07_demo_large_batch.png`](screenshots/07_demo_large_batch.png) | **`PASS`** |
| `demo_unlabeled.csv` | 50 | 170 | 39.012 | `PASS` | `200 OK` | `EXACT_MATCH` | `PASS` (4.787 B) | [`08_demo_unlabeled.png`](screenshots/08_demo_unlabeled.png), [`13_demo_unlabeled_rows_export.png`](screenshots/13_demo_unlabeled_rows_export.png) | **`PASS`** |
| `demo_invalid.csv` | 5 | 171 | 4.950 | `UploadError` | `400 Bad Request` | `N/A` (Bị chặn) | `N/A` | [`09_demo_invalid.png`](screenshots/09_demo_invalid.png) | **`PASS`** |
| `uci414_ida2016_duplicate_validation_50.csv` | 50 | 171 | 38.484 | `PASS` | `200 OK` | `EXACT_MATCH` | `PASS` (4.442 B) | [`10_external_uci414_duplicate.png`](screenshots/10_external_uci414_duplicate.png) | **`PASS`** |

---

### 4.2. Bảng So Sánh Đồng Thời Precision, Recall, $FN$, Tổng Chi Phí Và Công Suất Giữa Các Chính Sách

Bảng dưới đây trình bày đồng thời **Trần công suất $K$, Số lượt kiểm tra đề xuất $M$, Precision, Recall, số lỗi bỏ sót $FN$, số báo động giả $FP$, $TP$, $TN$, F1-score và Tổng chi phí $C = 10 \times FP + 500 \times FN$** ở ngưỡng nghiên cứu đã khóa $\tau^* = 0.3232440937634324$:

| Tệp CSV | $N$ (`pos`/`neg`) | Trần công suất $K$ ($10\%$) | Chính sách áp dụng | Số lượt kiểm tra ($M$) | Khả thi công suất ($M \le K$) | $TP$ | $FP$ | $FN$ | $TN$ | Precision | Recall | F1-score | Tổng chi phí $C = 10\text{FP} + 500\text{FN}$ |
|---|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **`demo_normal.csv`** | 20 (`0 / 20`) | 2 | Theo ngưỡng ($\tau^*$) | **1** | Khả thi ($1 \le 2$) | 0 | 1 | 0 | 19 | `0.00%` | **`—`** ($P=0$) | `0.00%` | **10** |
| **`demo_failure.csv`** | 20 (`20 / 0`) | 2 | Theo ngưỡng ($\tau^*$) | **19** | Vượt trần ($19 > 2$) | 19 | 0 | 1 | 0 | `100.00%` | `95.00%` | `97.44%` | **500** |
| ↳ *`demo_failure.csv`* | 20 (`20 / 0`) | 2 | Sau ưu tiên Top-$K$ ($K=2$) | **2** | Khả thi ($2 \le 2$) | 2 | 0 | 18 | 0 | `100.00%` | `10.00%` | `18.18%` | **9.000** |
| **`demo_mixed.csv`** | 100 (`10 / 90`) | 10 | Theo ngưỡng ($\tau^*$) | **11** | Vượt trần ($11 > 10$) | 9 | 2 | 1 | 88 | `81.82%` | `90.00%` | `85.71%` | **520** |
| ↳ *`demo_mixed.csv`* | 100 (`10 / 90`) | 10 | Sau ưu tiên Top-$K$ ($K=10$) | **10** | Khả thi ($10 \le 10$) | 8 | 2 | 2 | 88 | `80.00%` | `80.00%` | `80.00%` | **1.020** |
| **`demo_missing_values.csv`** | 30 (`0 / 30`) | 3 | Theo ngưỡng ($\tau^*$) | **1** | Khả thi ($1 \le 3$) | 0 | 1 | 0 | 29 | `0.00%` | **`—`** ($P=0$) | `0.00%` | **10** |
| **`demo_capacity.csv`** | 200 (`20 / 180`) | 20 | Theo ngưỡng ($\tau^*$) | **21** | Vượt trần ($21 > 20$) | 18 | 3 | 2 | 177 | `85.71%` | `90.00%` | `87.80%` | **1.030** |
| ↳ *`demo_capacity.csv`* | 200 (`20 / 180`) | 20 | Sau ưu tiên Top-$K$ ($K=20$) | **20** | Khả thi ($20 \le 20$) | 17 | 3 | 3 | 177 | `85.00%` | `85.00%` | `85.00%` | **1.530** |
| **`demo_large_batch.csv`** | 1.000 (`21 / 979`) | 100 | Theo ngưỡng ($\tau^*$) | **49** | Khả thi ($49 \le 100$) | 19 | 30 | 2 | 949 | `38.78%` | `90.48%` | `54.29%` | **1.300** |
| **`demo_unlabeled.csv`** | 50 (*Không nhãn*) | 5 | Theo ngưỡng ($\tau^*$) | **7** | Vượt trần ($7 > 5$) | `—` | `—` | `—` | `—` | `—` | `—` | `—` | `—` *(Không có nhãn)* |
| ↳ *`demo_unlabeled.csv`* | 50 (*Không nhãn*) | 5 | Sau ưu tiên Top-$K$ ($K=5$) | **5** | Khả thi ($5 \le 5$) | `—` | `—` | `—` | `—` | `—` | `—` | `—` | `—` *(Không có nhãn)* |
| **`scania_validation_sample.csv`** | 12 (`4 / 8`) | 1 | Theo ngưỡng ($\tau^*$) | **5** | Vượt trần ($5 > 1$) | 4 | 1 | 0 | 7 | `80.00%` | `100.00%` | `88.89%` | **10** |
| ↳ *`scania_validation_sample.csv`* | 12 (`4 / 8`) | 1 | Sau ưu tiên Top-$K$ ($K=1$) | **1** | Khả thi ($1 \le 1$) | 1 | 0 | 3 | 8 | `100.00%` | `25.00%` | `40.00%` | **1.500** |
| **`uci414_ida2016_duplicate_validation_50.csv`** | 50 (`2 / 48`) | 5 | Theo ngưỡng ($\tau^*$) | **4** | Khả thi ($4 \le 5$) | 2 | 2 | 0 | 46 | `50.00%` | `100.00%` | `66.67%` | **20** |

### 4.3. Phân Tích Chuyên Sâu: Sự Đánh Đổi Giữa Ngưỡng $\tau$, Trần Công Suất $K$ Và Chính Sách Top-$K$

Kết quả đối chiếu 5 kịch bản trên **`demo_capacity.csv`** ($N = 200$, `20 pos` / `180 neg`):

| Kịch bản điều chỉnh trên `demo_capacity.csv` | Ngưỡng $\tau$ | Trần công suất $K$ | Ưu tiên Top-$K$ | $M_{\text{ngưỡng}}$ | $M_{\text{cuối}}$ | $TP$ | $FP$ | $FN$ | $TN$ | Precision | Recall | F1-score | Tổng chi phí $C$ |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1. Ngưỡng nghiên cứu $\tau^*$, không cắt theo trần $K$ | `0.323244` | `20` ($10\%$) | Tắt | 21 | 21 | 18 | 3 | 2 | 177 | `85.71%` | `90.00%` | `87.80%` | **1.030** |
| 2. Ngưỡng nghiên cứu $\tau^*$, bật ưu tiên Top-$K$ ($10\%$) | `0.323244` | `20` ($10\%$) | Bật | 21 | 20 | 17 | 3 | 3 | 177 | `85.00%` | `85.00%` | `85.00%` | **1.530** |
| 3. Ngưỡng nghiên cứu $\tau^*$, siết công suất còn $5\%$ | `0.323244` | `10` ($5\%$) | Bật | 21 | 10 | 10 | 0 | 10 | 180 | `100.00%` | `50.00%` | `66.67%` | **5.000** |
| 4. Tăng ngưỡng lên $\tau = 0.50$ (ngưỡng mặc định cổ điển) | `0.500000` | `20` ($10\%$) | Tắt | 17 | 17 | 16 | 1 | 4 | 179 | `94.12%` | `80.00%` | `86.49%` | **2.010** |
| 5. Hạ ngưỡng xuống $\tau = 0.15$, bật ưu tiên Top-$K$ ($10\%$) | `0.150000` | `20` ($10\%$) | Bật | 26 | 20 | 17 | 3 | 3 | 177 | `85.00%` | `85.00%` | `85.00%` | **1.530** |

**Nhận xét kỹ thuật bắt buộc:**
1. **Chính sách Top-$K$ không phải lúc nào cũng làm giảm chi phí:** Vai trò của chính sách ưu tiên Top-$K$ (`threshold_then_top_k`) là **đảm bảo tính khả thi vận hành** ($M_{\text{cuối}} \le K$) khi số xe vượt ngưỡng $M_{\text{ngưỡng}} > K$. Khi áp trần công suất $K$, hệ thống buộc phải loại bỏ $M_{\text{ngưỡng}} - K$ xe có điểm thấp nhất trong nhóm đã qua ngưỡng. Nếu trong các xe bị cắt bỏ có chứa xe hỏng APS thật ($y=1$), mỗi xe đó chuyển từ $TP$ sang $FN$ làm chi phí tăng thêm $+500$ (như ở Kịch bản 2: cắt 1 xe từ $M=21$ về $K=20$ làm $FN$ tăng từ $2 \to 3$, chi phí tăng từ $1.030 \to 1.530$; hoặc Kịch bản 3: siết công suất xuống $K=10$ giúp $\text{Precision}$ đạt $100\%$ và $FP=0$, nhưng $\text{Recall}$ giảm xuống $50\%$, $FN$ tăng lên $10$, khiến chi phí tăng lên $5.000$). Ngược lại, so với việc hạ ngưỡng quá thấp mà không có trần công suất (Kịch bản 5: ở $\tau = 0.15$, ngưỡng đề xuất $M=26$ gồm $17\text{ TP}$ và $9\text{ FP}$ với chi phí $1.590$), việc bật ưu tiên Top-$K$ ($K=20$) loại bỏ đúng $6$ ca $FP$ ở đuôi, giúp giảm chi phí từ $1.590$ xuống $1.530$ và đưa số lượt khám về đúng trần $K=20$.
2. **Xử lý chỉ số không xác định khi lô không có mẫu `pos` ($P = 0$):** Trên `demo_normal.csv` ($0\text{ pos}, 20\text{ neg}$) và `demo_missing_values.csv` ($0\text{ pos}, 30\text{ neg}$), do tổng số mẫu dương thực tế $P = TP + FN = 0$, chỉ số $\text{Recall} = TP / (TP + FN)$ có mẫu số bằng $0$ nên không xác định. Cả hàm `evaluate_policy` ở backend (`recall: null`) lẫn hàm `evaluate` trong `web_demo/live.js` (`tp + fn ? tp / (tp + fn) : null`, hiển thị qua `percent(null) -> "—"`) đều xử lý chuẩn xác và hiển thị ký hiệu **`—`** trên bảng giao diện (xem ảnh chụp [`12_demo_normal_metrics_matrix.png`](screenshots/12_demo_normal_metrics_matrix.png)).

---

## 5. Phân Biệt Rõ Kết Quả Demo Và Kết Quả Đánh Giá Khoa Học

| Tiêu chí | Kết quả trên các lô CSV Demo (`data/examples/demo_cases/`) | Kết quả Đánh giá Khoa học Chính thức của Đồ án (`results/scania_aps/`) |
|---|---|---|
| **Tập dữ liệu & Quy mô** | Các lát cắt nhỏ ($12, 20, 30, 50, 100, 200, 1.000$ dòng) trích từ tập Validation G3 (`12.000` mẫu). | Toàn bộ tập Validation (`12.000` mẫu: `200 pos`, `11.800 neg`) và tập kiểm thử độc lập **Official Test** (`16.000` mẫu: `375 pos`, `15.625 neg`, Gate G10 Run 003). |
| **Tỷ lệ lớp dương (`pos`)** | Được thiết kế đa dạng theo kịch bản tính năng ($0\%$, $10\%$, $100\%$ hoặc $\sim 2.1\%$). | Tỷ lệ tự nhiên của quần thể: Validation $1.67\%$ `pos`; Official Test $2.34\%$ `pos`. |
| **Mục đích sử dụng** | Kiểm thử trực tiếp luồng tải tệp, bắt lỗi schema, điền khuyết `na`, thay đổi ngưỡng/công suất/ưu tiên Top-$K$ và xuất CSV trên Web Demo. | Đánh giá khoa học, so sánh Baselines G4, chọn siêu tham số/ngưỡng ở Phase 2 và nghiệm thu khả năng tổng quát hóa độc lập ở Gate G10. |
| **Kết quả chuẩn đã khóa** | Thay đổi theo từng lô và cấu hình người dùng thử nghiệm trên giao diện. | **Validation (Trial 16, $\tau^* = 0.323244$):** $C_{\text{val}} = 6.330$ ($TP=195, FP=383, FN=5, TN=11.417, M=578 \le 1.200$, $\text{Recall}=97.50\%$).<br>**Official Test (G10 Run 003):** $C_{\text{test}} = 13.840$ ($TP=357, FP=484, FN=18, TN=15.141, M=841 \le 1.600$, $\text{Precision}=42.45\%, \text{Recall}=95.20\%$, giảm $92.62\%$ chi phí so với B0 $187.500$). |

---

## 6. Bảng Phân Loại Trạng Thái Nghiệm Thu Cuối Cùng

| STT | Hạng mục yêu cầu theo OWNER DIRECTIVE — DEMO DATA FINAL ACCEPTANCE | Kết quả & Bằng chứng thực tế | Phân loại |
|---:|---|---|---|
| 1 | **Kiểm chứng giao diện web thực tế:** Khởi động Web Demo trên cổng riêng (`8517`), kiểm tra trực tiếp trên trình duyệt toàn bộ 9 CSV bổ sung + 1 CSV mẫu ban đầu (tải file, dự đoán, ma trận nhầm lẫn, đổi ngưỡng, đổi công suất, bật/tắt Top-$K$, xuất CSV, file unlabeled, file invalid) và lưu ảnh chụp màn hình thực tế | Đã kiểm chứng trực tiếp 10/10 tệp trên `http://localhost:8517` bằng trình duyệt và lưu 14 ảnh chụp màn hình thực tế tại `reports/demo_data_expansion/screenshots/` | **`PASS`** |
| 2 | **Kiểm tra tính tương thích với phiên bản mới nhất:** Kiểm tra HEAD của `main` (`3ea8e79` tag `v1.0` & `origin/main` `f55e043`) và workspace của Codex; đối chiếu schema, checkpoint, preprocessor và API dự đoán | Schema (`170` cột), checkpoint (`trial16_refit_20261127_02`), preprocessor (`tree_preprocessor.joblib`) và API `/api/predict` khớp 100% (`0` dòng diff code); ghi rõ yêu cầu chạy lại 3 lệnh test tích hợp nếu Codex có commit mới trước khi merge | **`PASS`** |
| 3 | **Rà soát dữ liệu và artifact:** Xác minh membership G3 và SHA-256 của toàn bộ CSV; ma trận trùng lặp trong manifest; giấy phép/bản quyền Scania CV AB (CC BY 4.0 / GPLv3); 0% Official Test; không coi UCI #414 là dữ liệu độc lập; giải thích rõ `demo_invalid.csv` dùng 5 dòng | Đã xác minh 100% mẫu hợp lệ thuộc Validation G3, cập nhật `row_count_rationale` cho `demo_invalid.csv` (5 dòng) và bổ sung đầy đủ thông báo bản quyền/nghĩa vụ ghi nguồn vào manifest & README | **`PASS`** |
| 4 | **Sửa các nhận định chưa chính xác:** Dùng đúng nhận định *"chưa tìm thấy nguồn độc lập tương thích trong phạm vi khảo sát"*; xác định xe `neg` chỉ là xe không mang nhãn lỗi liên quan đến APS (không gọi là xe hoàn toàn an toàn); không khẳng định Top-$K$ luôn giảm chi phí; trình bày đồng thời Precision, Recall, $FN$, chi phí và công suất; kiểm tra xử lý chỉ số không xác định (`Recall = —` khi $P=0$); phân biệt rõ kết quả demo và kết quả đánh giá khoa học | Đã cập nhật đồng bộ trên toàn bộ báo cáo, manifest và hướng dẫn demo tiếng Việt | **`PASS`** |
| 5 | **Kiểm chứng cuối cùng & Cập nhật Git/PR:** Chạy lại toàn bộ unit tests (`app.py --verify`, `test_live_prediction.py`, `test_web_demo.py`), đối chiếu số liệu JSON/CSV/UI/Báo cáo, kiểm tra `git diff`, commit, push lên branch `antigravity/scania-demo-data-expansion` và cập nhật Draft PR #1 | Toàn bộ unit tests đạt `OK (PASS)`, `0` tệp ngoài phạm vi bị sửa đổi, đã push và cập nhật Draft PR #1 | **`PASS`** |

---

## 7. Danh Sách Toàn Bộ Artifact Bàn Giao Trên Branch `antigravity/scania-demo-data-expansion`

Không có bất kỳ tệp hiện có nào của dự án bị chỉnh sửa hoặc xóa (`0` modified/deleted tracked files from base commit `3ea8e79`). Toàn bộ các tệp bàn giao nằm gọn trong 3 thư mục được chỉ định:

- **Thư mục `data/examples/demo_cases/` (10 tệp):**
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
- **Thư mục `data/examples/external_sources/` (3 tệp):**
  11. `data/examples/external_sources/uci414_ida2016_duplicate_validation_50.csv`
  12. `data/examples/external_sources/EXTERNAL_SOURCES_MANIFEST.json`
  13. `data/examples/external_sources/README.md`
- **Thư mục `reports/demo_data_expansion/` (6 tệp báo cáo/JSON + 14 ảnh chụp màn hình trình duyệt thực tế):**
  14. `reports/demo_data_expansion/EXTERNAL_DATA_SOURCE_AUDIT.md`
  15. `reports/demo_data_expansion/EXTERNAL_SOURCE_REGISTRY.json`
  16. `reports/demo_data_expansion/CSV_SCHEMA_VALIDATION.json`
  17. `reports/demo_data_expansion/DEMO_EXECUTION_RESULTS.json`
  18. `reports/demo_data_expansion/DEMO_DATA_EXPANSION_REPORT.md`
  19. `reports/demo_data_expansion/DEMO_INSTRUCTIONS_VI.md`
  20. `reports/demo_data_expansion/screenshots/01_scania_validation_sample.png`
  21. `reports/demo_data_expansion/screenshots/02_demo_normal.png`
  22. `reports/demo_data_expansion/screenshots/03_demo_failure_priority.png`
  23. `reports/demo_data_expansion/screenshots/04_demo_mixed_priority.png`
  24. `reports/demo_data_expansion/screenshots/05_demo_missing_values.png`
  25. `reports/demo_data_expansion/screenshots/06a_demo_capacity_default_priority.png`
  26. `reports/demo_data_expansion/screenshots/06b_demo_capacity_custom_and_export.png`
  27. `reports/demo_data_expansion/screenshots/07_demo_large_batch.png`
  28. `reports/demo_data_expansion/screenshots/08_demo_unlabeled.png`
  29. `reports/demo_data_expansion/screenshots/09_demo_invalid.png`
  30. `reports/demo_data_expansion/screenshots/10_external_uci414_duplicate.png`
  31. `reports/demo_data_expansion/screenshots/11_demo_capacity_metrics_matrix_rows.png`
  32. `reports/demo_data_expansion/screenshots/12_demo_normal_metrics_matrix.png`
  33. `reports/demo_data_expansion/screenshots/13_demo_unlabeled_rows_export.png`
