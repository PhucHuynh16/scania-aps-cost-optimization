# Báo Cáo Kiểm Chứng Các Nguồn Dữ Liệu Thực Tế Bên Ngoài (Phương Án 2)

**Dự án:** Tối ưu hóa chi phí bảo trì dự đoán hệ thống khí nén xe tải Scania APS (UCI #421)  
**Nhánh thực hiện:** `antigravity/scania-demo-data-expansion`  
**Commit cơ sở:** `3ea8e79` (`release: publish verified Scania APS coursework`)  
**Ngày kiểm chứng:** `2026-11-27`

---

## 1. Kết Luận Tổng Quát

- **Kết luận về nguồn dữ liệu độc lập (`COMPATIBLE_INDEPENDENT`):**
  > **`NO_VERIFIED_COMPATIBLE_EXTERNAL_DATA`** — **Chưa tìm thấy nguồn độc lập tương thích trong phạm vi khảo sát** (bao gồm UCI Machine Learning Repository, OpenML, Kaggle, GitHub, Zenodo, Researchdata.se / Swedish National Data Service, Nature Scientific Data, Figshare, Mendeley Data và IEEE DataPort).
- **Tổng hợp kết quả phân loại trên 10 nguồn dữ liệu thực tế đã rà soát và kiểm chứng:**
  - `COMPATIBLE_INDEPENDENT`: **0** nguồn (chưa tìm thấy nguồn độc lập tương thích trong phạm vi khảo sát).
  - `COMPATIBLE_DUPLICATE`: **4** nguồn (`EXT-01` UCI #414, `EXT-02` GitHub `jieqiong-pang`, `EXT-03` GitHub `atagunduzalp`, `EXT-04` Kaggle `uciml` — tất cả đều là bản sao trùng nguồn gốc UCI #421, tuyệt đối không coi UCI #414 hay các bản mirror là dữ liệu độc lập).
  - `PARTIALLY_COMPATIBLE`: **2** nguồn (`EXT-05` OpenML #41138, `EXT-06` OpenML #46908 TabArena).
  - `INCOMPATIBLE`: **4** nguồn (`EXT-07` SCANIA Component X 2024–2025, `EXT-08` MetroPT-3 APU, `EXT-09` AI4I 2020, `EXT-10` Zenodo #22834903 CAOS TruckVitals).
  - `UNVERIFIED`: **0** nguồn.

### Lý giải kỹ thuật vì sao chưa tìm thấy nguồn độc lập tương thích trong phạm vi khảo sát

1. **Đặc thù ẩn danh độc quyền của Scania CV AB (2016):** Bộ dữ liệu *APS Failure at Scania Trucks* công bố tại cuộc thi *IDA 2016 Industrial Challenge* gồm `170` thuộc tính vận hành được mã hóa dưới dạng `Identifier_Bin` bằng 2 chữ cái viết thường (`aa_000`, `ab_000`, ..., `eg_000`), bao gồm các bộ đếm số học tích lũy (numerical counters) và 7 biến histogram. Scania CV AB không công bố bảng ánh xạ từ các mã `aa_000..eg_000` sang tên cảm biến vật lý thực tế hay đơn vị đo. Do đó, trong phạm vi các kho dữ liệu công khai được khảo sát, chưa tìm thấy đơn vị độc lập nào công bố bộ dữ liệu riêng có cùng 170 cột `aa_000..eg_000` với cùng thang đo và phân phối bin.
2. **Sự thay đổi hoàn toàn về schema trong công bố mới của Scania (2024–2025):** Khi Scania CV AB và Đại học Stockholm công bố bộ dữ liệu bảo trì dự đoán thế hệ mới — **SCANIA Component X Dataset** (*Nature Scientific Data*, 2025, DOI: `10.1038/s41597-025-04802-6`; *Swedish National Data Service*, DOI: `10.5878/bnh5-ka77`) — họ chuyển sang bài toán dự đoán lỗi trên một linh kiện động cơ khác (`Component X`), tổ chức dưới dạng chuỗi thời gian đa bảng (`operational_readouts.csv`, `specifications.csv`, `tte.csv`) và đặt tên thuộc tính bằng mã số (`167_0..167_9`, `158_0..158_9`, `397_0..397_35`...). Vì khác linh kiện, khác cấu trúc thời gian và khác hoàn toàn tập thuộc tính, bộ dữ liệu này là `INCOMPATIBLE` với mô hình 170 thuộc tính hiện tại.
3. **Mọi nguồn bên ngoài khớp 170 thuộc tính `aa_000..eg_000` đều là bản sao của IDA 2016 Challenge:** Kiểm tra mã băm SHA-256 ở cấp độ tệp và so khớp từng dòng ở cấp độ bản ghi chứng minh tất cả các bản phân phối trên UCI (`#414`), GitHub, Kaggle và OpenML đều bắt nguồn từ đúng 60.000 mẫu Train và 16.000 mẫu Test của IDA 2016 Challenge.

---

## 2. Bảng Tổng Hợp 10 Nguồn Dữ Liệu Đã Kiểm Chứng

| Mã nguồn | Tên bộ dữ liệu & Nền tảng | URL / DOI | Số dòng × Thuộc tính | Định dạng | Mức độ trùng lặp với UCI #421 | Phân loại | Quyết định đưa vào Demo |
|---|---|---|---|---|---|---|---|
| **EXT-01** | **IDA2016Challenge** (UCI Machine Learning Repository #414) | [archive.ics.uci.edu/dataset/414](https://archive.ics.uci.edu/dataset/414/ida2016challenge) (`10.24432/C5V60Q`) | `60.000` Train + `16.000` Test × `171` cột | ZIP chứa CSV (20 dòng lời dẫn + header dòng 21) | **100% cấp độ byte** (SHA-256 tệp CSV trùng khớp tuyệt đối) | `COMPATIBLE_DUPLICATE` | **CHẤP NHẬN** (Trích 50 mẫu Validation: `uci414_ida2016_duplicate_validation_50.csv`, ghi rõ trùng nguồn) |
| **EXT-02** | **APS-Failure-at-Scania-Trucks-Data-Set** (GitHub `jieqiong-pang`) | [github.com/jieqiong-pang/APS-Failure-at-Scania-Trucks-Data-Set](https://github.com/jieqiong-pang/APS-Failure-at-Scania-Trucks-Data-Set) | `60.000` Train + `16.000` Test × `171` cột | CSV (có 20 dòng lời dẫn GPLv3) | **100% cấp độ byte** (SHA-256: `bb484302...`) | `COMPATIBLE_DUPLICATE` | **LOẠI** (Trùng byte 100% với EXT-01/UCI #421; repo cá nhân không khai báo LICENSE riêng) |
| **EXT-03** | **truck-data-analysis** (GitHub `atagunduzalp`) | [github.com/atagunduzalp/truck-data-analysis](https://github.com/atagunduzalp/truck-data-analysis) | `60.000` Train + `16.000` Test × `171` cột | CSV chuẩn (đã cắt bỏ 20 dòng lời dẫn, dòng 1 là header) | **100% cấp độ bản ghi** (`60.000` dòng dữ liệu trùng khớp từng ký tự) | `COMPATIBLE_DUPLICATE` | **LOẠI** (Chỉ lưu metadata/SHA-256 vì repo không khai báo LICENSE riêng và nội dung trùng 100% với EXT-01) |
| **EXT-04** | **Air Pressure System Failures in Scania Trucks** (Kaggle `uciml`) | [kaggle.com/datasets/uciml/aps-failure-at-scania-trucks-data-set](https://www.kaggle.com/datasets/uciml/aps-failure-at-scania-trucks-data-set) | `60.000` Train + `16.000` Test × `171` cột | CSV chuẩn (bản gốc của EXT-03) | **100% cấp độ bản ghi** | `COMPATIBLE_DUPLICATE` | **LOẠI** (Chỉ lưu metadata; bản sao UCI #421 trên Kaggle yêu cầu tài khoản khi tải) |
| **EXT-05** | **APSFailure v1** (OpenML #41138) | [openml.org/d/41138](https://www.openml.org/d/41138) | `76.000` dòng × `171` thuộc tính | ARFF / Parquet | **100% nguồn dữ liệu** (gộp 60k Train + 16k Official Test) | `PARTIALLY_COMPATIBLE` | **LOẠI** (Định dạng ARFF, ký hiệu thiếu `?` thay vì `na`, định dạng số `.0` và gộp lẫn Official Test) |
| **EXT-06** | **APSFailure v2 — TabArena** (OpenML #46908) | [openml.org/d/46908](https://www.openml.org/d/46908) | `76.000` dòng × `171` thuộc tính | ARFF / Parquet | **100% nguồn dữ liệu** (gộp 60k Train + 16k Official Test) | `PARTIALLY_COMPATIBLE` | **LOẠI** (Định dạng ARFF, đổi tên cột `class` thành `AirPressureSystemFailure`, gộp lẫn Official Test) |
| **EXT-07** | **SCANIA Component X Dataset** (Researchdata.se / Nature Scientific Data) | [doi.org/10.5878/bnh5-ka77](https://doi.org/10.5878/bnh5-ka77) / `10.1038/s41597-025-04802-6` | Đa bảng chuỗi thời gian × `~107` thuộc tính (`167_0..397_35`, `Spec_0..7`) | CSV đa bảng (`operational_readouts`, `tte`, `specifications`) | **0%** (Bộ dữ liệu độc lập mới của Scania) | `INCOMPATIBLE` | **LOẠI** (Khác linh kiện mục tiêu, khác cấu trúc chuỗi thời gian và khác hoàn toàn schema thuộc tính) |
| **EXT-08** | **MetroPT-3 Dataset (APU Compressor)** (UCI #791 / Zenodo) | [archive.ics.uci.edu/dataset/791](https://archive.ics.uci.edu/dataset/791/metropt+3+dataset) (`10.24432/C5VW3R`) | `1.516.948` dòng × `15` thuộc tính | CSV chuỗi thời gian 1 Hz | **0%** | `INCOMPATIBLE` | **LOẠI** (Hệ thống khí nén tàu điện ngầm chỉ có 15 cột cảm biến vật lý, không tương thích schema 170 cột) |
| **EXT-09** | **AI4I 2020 Predictive Maintenance** (UCI #601) | [archive.ics.uci.edu/dataset/601](https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset) (`10.24432/C5HS5C`) | `10.000` dòng × `14` thuộc tính | CSV | **0%** | `INCOMPATIBLE` | **LOẠI** (Dữ liệu máy phay tổng hợp 14 cột, không tương thích mô hình Scania APS) |
| **EXT-10** | **CAOS TruckVitals Regime Conditioning Benchmark** (Zenodo #22834903) | [zenodo.org/records/22834903](https://zenodo.org/records/22834903) (`10.5281/zenodo.22834903`) | Báo cáo PDF + mã mô phỏng đội xe tải mỏ | PDF / Python | **0%** (Chỉ trích dẫn bài toán UCI #421) | `INCOMPATIBLE` | **LOẠI** (Không chứa bảng dữ liệu thực tế 170 thuộc tính Scania APS) |

---

## 3. Hồ Sơ Kiểm Chứng Chi Tiết Từng Nguồn

### 3.1. `EXT-01` — UCI Machine Learning Repository #414 (`IDA2016Challenge`)

- **Tên bộ dữ liệu:** `IDA2016Challenge` (*APS Failure and Operational Data for Scania Trucks*)
- **URL chính xác:** `https://archive.ics.uci.edu/dataset/414/ida2016challenge` (Tệp tải xuống: `https://archive.ics.uci.edu/static/public/414/ida2016challenge.zip`, DOI: `10.24432/C5V60Q`)
- **Tác giả / Đơn vị công bố:** Scania CV AB (Södertälje, Sweden); Donors: Tony Lindgren (`tony@dsv.su.se`) & Jonas Biteus (`jonas.biteus@scania.com`)
- **Thời gian công bố:** Tháng 09/2016 (cập nhật trên UCI #414 ngày 17/01/2017)
- **Nguồn gốc và phương pháp thu thập:** Thu thập từ hệ thống khí nén (Air Pressure System — APS) trên xe tải hạng nặng Scania trong vận hành thực tế hằng ngày phục vụ cuộc thi *IDA 2016 Industrial Challenge*.
- **Giấy phép sử dụng:** CC BY 4.0 trên trang danh mục UCI; thông báo GNU General Public License v3 (or later) của Scania CV AB trong tệp `to_uci/aps_failure_description.txt`.
- **Số dòng và số thuộc tính:** `60.000` dòng phát triển (`59.000 neg`, `1.000 pos`) và `16.000` dòng kiểm thử (`15.625 neg`, `375 pos`), mỗi dòng gồm `171` cột (`class` + `170` thuộc tính từ `aa_000` đến `eg_000`).
- **Định dạng dữ liệu:** Tệp nén ZIP chứa thư mục `to_uci/` gồm 2 tệp CSV và 1 tệp TXT. Mỗi tệp CSV có 20 dòng đầu là thông báo bản quyền GPLv3, dòng 21 là header cột, từ dòng 22 trở đi là dữ liệu phân cách bằng dấu phẩy, giá trị thiếu ghi là `na`.
- **Ý nghĩa và đơn vị đo của thuộc tính:** Các bộ đếm tích lũy đơn lẻ và 7 biến histogram đa bin theo điều kiện vận hành; tên và đơn vị đo đã được ẩn danh hoàn toàn.
- **Cách xác định nhãn lỗi:** `pos` là lỗi xảy ra tại một linh kiện cụ thể thuộc hệ thống APS; `neg` là các xe tải gặp lỗi ở bộ phận khác không liên quan đến APS.
- **Khả năng tương thích với schema hiện tại:** Tương thích 100% sau khi bỏ 20 dòng lời dẫn đầu tệp và trích xuất lô tối đa 1.000 dòng / 4 MiB.
- **Mức độ trùng lặp với UCI #421:** **Trùng khớp 100% cấp độ byte** đối với toàn bộ 3 tệp thành phần bên trong ZIP:
  - `uci_414_ida2016challenge.zip`: `20.957.291` bytes — SHA-256: `5336e4b643c4915931879c3db0535139e188732e74122badf0a4eb1749b4e8cb` (khác kích thước ZIP với UCI #421 do mức nén ZIP và tiền tố thư mục `to_uci/`).
  - `to_uci/aps_failure_training_set.csv`: `44.669.194` bytes — SHA-256: `bb484302e3a3a1c8ef5e1f0129c4dc7cbd58f350867f95b575461ca21ab6b9da` (**trùng 100% với UCI #421**).
  - `to_uci/aps_failure_test_set.csv`: `11.943.558` bytes — SHA-256: `2cdf6f7661c7b4c63333c93cdec36a3a82350176b604a2312cf82799fb2712f3` (**trùng 100% với tệp trong ZIP của UCI #421**).
  - `to_uci/aps_failure_description.txt`: `4.874` bytes — SHA-256: `57b1eb3c551a678ffc1c8112e5b34c566dd16457642563f58aeb3ca65beeb820` (**trùng 100% với UCI #421**).
- **Kết luận và bằng chứng kiểm chứng:** Phân loại **`COMPATIBLE_DUPLICATE`**. Đã trích xuất 50 mẫu đầu tiên theo thứ tự dòng của `to_uci/aps_failure_training_set.csv` thuộc phân vùng Validation G3 để tạo tệp `data/examples/external_sources/uci414_ida2016_duplicate_validation_50.csv` (SHA-256: `28fb0bd55db814dbd160b1e1e746508ff0d27988d35224536b179d25056c0f89`) và ghi rõ là dữ liệu trùng nguồn UCI, không phải dữ liệu độc lập.

---

### 3.2. `EXT-02` — GitHub Mirror (`jieqiong-pang/APS-Failure-at-Scania-Trucks-Data-Set`)

- **URL chính xác:** `https://github.com/jieqiong-pang/APS-Failure-at-Scania-Trucks-Data-Set`
- **Tác giả / Thời gian công bố:** Jieqiong Pang — Ngày tạo repo: `2020-02-09`.
- **Giấy phép sử dụng:** Repo không khai báo tệp `LICENSE` riêng; tệp `aps_failure_description.txt` giữ nguyên thông báo GPLv3 của Scania CV AB.
- **Số dòng, thuộc tính và định dạng:** `60.000` dòng × `171` cột (CSV có 20 dòng lời dẫn đầu tệp).
- **SHA-256 tệp tải xuống:**
  - `aps_failure_training_set.csv`: `44.669.194` bytes — SHA-256: `bb484302e3a3a1c8ef5e1f0129c4dc7cbd58f350867f95b575461ca21ab6b9da` (**trùng 100% với UCI #421**).
  - `aps_failure_description.txt`: `4.874` bytes — SHA-256: `57b1eb3c551a678ffc1c8112e5b34c566dd16457642563f58aeb3ca65beeb820`.
- **Kết luận:** Phân loại **`COMPATIBLE_DUPLICATE`**. Bản sao byte-for-byte của UCI #421. Chỉ lưu metadata vì đã có lát cắt từ nguồn chính thức UCI #414 (`EXT-01`).

---

### 3.3. `EXT-03` — GitHub Mirror (`atagunduzalp/truck-data-analysis`)

- **URL chính xác:** `https://github.com/atagunduzalp/truck-data-analysis`
- **Tác giả / Thời gian công bố:** Alp Atagündüz — Ngày tạo repo: `2020-06-28`.
- **Nguồn gốc:** Bản mirror từ Kaggle (`uciml/aps-failure-at-scania-trucks-data-set`), trong đó 20 dòng lời dẫn GPLv3 ở đầu tệp CSV đã được cắt bỏ để dòng 1 là header `class,aa_000,...,eg_000`.
- **Giấy phép sử dụng:** Repo không có tệp `LICENSE` riêng (`license: null` trên GitHub API); tệp `aps_failure_description.txt` đã bị cắt phần header GPLv3 (còn `2.694` bytes).
- **Số dòng, thuộc tính và định dạng:** `60.000` dòng dữ liệu + `1` dòng header (`60.001` dòng tổng cộng) × `171` cột, định dạng CSV chuẩn UTF-8.
- **SHA-256 tệp tải xuống:**
  - `aps_failure_training_set.csv`: `44.668.322` bytes — SHA-256: `cbbcc17b812feaff4433b4aac7fb1e94b8a95381e93a29e63069afd20782d5d8`.
  - `aps_failure_description.txt`: `2.694` bytes — SHA-256: `e1ab65c879f4a79b65c5fc7696d837d6b1b8851436e987b29647a8966006584b`.
- **Kiểm chứng trùng lặp cấp độ bản ghi:** Đối chiếu trực tiếp 60.000 dòng dữ liệu của tệp này với 60.000 dòng dữ liệu (dòng 22..60021) của UCI #421 `aps_failure_training_set.csv` cho kết quả **`ata_data == raw_data: True` (trùng khớp 100% từng ký tự trên cả 60.000 dòng)**. Chênh lệch dung lượng `44.669.194 - 44.668.322 = 872` bytes chính xác là dung lượng của 20 dòng lời dẫn đầu tệp.
- **Kết luận:** Phân loại **`COMPATIBLE_DUPLICATE`**. Chỉ lưu metadata và mã băm SHA-256 (không phân phối lại tệp từ repo thiếu thông báo bản quyền GPLv3).

---

### 3.4. `EXT-04` — Kaggle Mirror (`uciml/aps-failure-at-scania-trucks-data-set`)

- **URL chính xác:** `https://www.kaggle.com/datasets/uciml/aps-failure-at-scania-trucks-data-set`
- **Tác giả / Thời gian công bố:** UCI Machine Learning Community Mirror trên Kaggle (2017).
- **Nguồn gốc & Định dạng:** Bản sao bộ dữ liệu UCI #421 đã bỏ 20 dòng lời dẫn đầu tệp (nguồn gốc trực tiếp của các repo GitHub như `EXT-03` và `ursulacervantes/scania-trucks`).
- **Kết luận:** Phân loại **`COMPATIBLE_DUPLICATE`**. Trùng 100% dữ liệu với UCI #421. Chỉ lưu metadata và hướng dẫn truy cập.

---

### 3.5. `EXT-05` — OpenML #41138 (`APSFailure` Version 1)

- **URL chính xác:** `https://www.openml.org/d/41138` (Tệp tải xuống: `https://openml.org/data/v1/download/19335511/APSFailure.arff`)
- **Tác giả / Thời gian công bố:** Scania, Tony Lindgren, Jonas Biteus (Tải lên OpenML ngày `2018-08-15T20:54:50`).
- **Giấy phép:** Khai báo `CC0` trên metadata OpenML, ghi chú `Data was published under the GNU GPL v3 license` trong phần mô tả.
- **Số dòng, thuộc tính và định dạng:** `76.000` dòng × `171` thuộc tính (`@ATTRIBUTE class {pos, neg}` + `170` thuộc tính từ `aa_000` đến `eg_000`), định dạng **ARFF**.
- **SHA-256 tệp tải xuống:**
  - `openml_41138.json`: `1.184` bytes — SHA-256: `cb57257e767d97ab2a16725f9e2533e9a709cdd57f9df457ca5db7e757a04348`.
  - `openml_41138_APSFailure.arff`: `78.399.357` bytes — SHA-256: `e95128fc82ef5d5bc5a732b0bc63dea0f6e285cc60f31290c81f82ea13429c4f`.
- **Phân tích tính tương thích và mức độ trùng lặp:**
  1. Gộp chung `60.000` mẫu Train và `16.000` mẫu Official Test của UCI #414/#421 vào cùng một tệp.
  2. Định dạng tệp là ARFF (`@RELATION`, `@ATTRIBUTE`, `@DATA`), ký hiệu giá trị thiếu là dấu hỏi chấm (`?`) thay vì `na`, và nhiều số nguyên được xuất kèm hậu tố `.0` (ví dụ `2130706438.0`).
  3. Trình đọc `parse_csv` của Web Demo yêu cầu định dạng CSV chuẩn và chỉ nhận giá trị thiếu là `""` hoặc `"na"` (ký hiệu `?` sẽ gây lỗi `UploadError: cần số hữu hạn hoặc na`).
- **Kết luận:** Phân loại **`PARTIALLY_COMPATIBLE`** (và trùng 100% nguồn dữ liệu với UCI #421). Bị loại khỏi bộ CSV demo để tuân thủ quy tắc không ép sửa định dạng và không chạm vào 16.000 mẫu Official Test.

---

### 3.6. `EXT-06` — OpenML #46908 (`APSFailure` Version 2 — TabArena)

- **URL chính xác:** `https://www.openml.org/d/46908` (Tệp tải xuống: `https://openml.org/data/v1/download/22125219/APSFailure.arff`)
- **Tác giả / Thời gian công bố:** TabArena Team (`2025-04-30T19:54:32`), trích dẫn nguồn `https://doi.org/10.24432/C5V60Q` (UCI #414).
- **Giấy phép:** `CC BY 4.0`.
- **Số dòng, thuộc tính và định dạng:** `76.000` dòng × `171` thuộc tính, định dạng **ARFF**.
- **SHA-256 tệp tải xuống:**
  - `openml_46908.json`: `2.383` bytes — SHA-256: `d18d6442b145f374672126ad807473b38700655c66b7a4e905d507c597fed4a1`.
  - `openml_46908_APSFailure.arff`: `78.323.905` bytes — SHA-256: `14fd7b78bb6d1257eb8165f6294f720f6f867fc60bb413f0e4398ef6e5a2bb00`.
- **Phân tích tính tương thích:** Bên cạnh định dạng ARFF và việc gộp chung 60.000 mẫu Train + 16.000 mẫu Test, nhóm TabArena đã **đổi tên cột nhãn từ `class` sang `AirPressureSystemFailure`** (`@ATTRIBUTE AirPressureSystemFailure {neg, pos}`). Trong `parse_csv`, mọi cột khác `"class"` đều được coi là thuộc tính đầu vào, nên cột `AirPressureSystemFailure` sẽ bị từ chối với lỗi `CSV không đúng schema Scania APS: có 1 cột ngoài schema`.
- **Kết luận:** Phân loại **`PARTIALLY_COMPATIBLE`**. Bị loại khỏi bộ CSV demo.

---

### 3.7. `EXT-07` — SCANIA Component X Dataset (2024–2025)

- **URL chính xác:** `https://researchdata.se/en/catalogue/dataset/2024-34` / `https://doi.org/10.5878/bnh5-ka77`
- **Bài báo công bố:** *SCANIA Component X Dataset: A Real-World Multivariate Time Series Dataset for Predictive Maintenance*, **Nature Scientific Data** (2025), DOI: `10.1038/s41597-025-04802-6`.
- **Tác giả / Đơn vị công bố:** Zahra Kharazian, Tony Lindgren, Jonas Biteus, et al. (Scania CV AB, Stockholm University, Halmstad University).
- **Giấy phép:** `CC BY 4.0`.
- **Cấu trúc và thuộc tính:**
  - Theo dõi một linh kiện động cơ ẩn danh (`Component X`) dưới dạng chuỗi thời gian đa biến (`vehicle_id`, `time_step`).
  - Gồm 14 biến vận hành chia thành các bin histogram và bộ đếm số học mang **mã định danh bằng số**: `167_0..167_9`, `158_0..158_9`, `272_0..272_9`, `291_0..291_10`, `459_0..459_19`, `397_0..397_35`, `171_0`, `666_0`, `837_0`, `100_0`... kết hợp với bảng cấu hình tĩnh `Spec_0..Spec_7` và bảng thời gian sống sót `tte.csv` (~107 cột đặc trưng).
- **Khả năng tương thích:** **Hoàn toàn không tương thích (`INCOMPATIBLE`)** với mô hình `trial16_refit_20261127_02` vốn yêu cầu đúng 170 cột `aa_000..eg_000` của hệ thống khí nén APS.
- **Kết luận:** Phân loại **`INCOMPATIBLE`**. Tuyệt đối không ánh xạ cưỡng bức hay tạo cột giả.

---

### 3.8. `EXT-08`, `EXT-09`, `EXT-10` — Các Bộ Dữ Liệu Bảo Trì Dự Đoán Khác Trên UCI & Zenodo

- **`EXT-08` — MetroPT-3 Dataset (UCI #791, DOI: `10.24432/C5VW3R`):** Dữ liệu chuỗi thời gian 1 Hz từ hệ thống sản xuất khí nén (Air Production Unit — APU) của tàu điện ngầm Porto (`1.516.948` dòng × `15` cột cảm biến vật lý như `TP2`, `TP3`, `DV_pressure`, `Oil_temperature`, `Motor_current`). Dù cùng bài toán bảo trì hệ thống khí nén, schema 15 cột vật lý hoàn toàn khác với 170 cột ẩn danh của Scania APS. Phân loại: **`INCOMPATIBLE`**.
- **`EXT-09` — AI4I 2020 Predictive Maintenance Dataset (UCI #601, DOI: `10.24432/C5HS5C`):** Dữ liệu máy phay công nghiệp (`10.000` dòng × `14` cột). Hợp đồng `src/scania/contracts.py` đã ghi rõ `AI4I is independent`. Phân loại: **`INCOMPATIBLE`**.
- **`EXT-10` — Zenodo #22834903 (`CAOS TruckVitals`, DOI: `10.5281/zenodo.22834903`):** Truy vấn API Zenodo (`zenodo_aps.json`, SHA-256: `4a7e2e48b4f79728a2cb00bd18db5a8e3c1e2e8b5c920cd89481699b100caf51`; `zenodo_scania.json`, SHA-256: `516dacafc2d6235f59fc73d5cbea2e910c442b7c1e56069b8fa041c9cc3c0693`) xác nhận kết quả liên quan nhất trên Zenodo là báo cáo benchmark *Regime Conditioning Recovers Detection, Not Localisation* trên dữ liệu mô phỏng xe tải mỏ (chỉ trích dẫn DOI `10.24432/C51S51` của Scania APS chứ không chứa dữ liệu Scania APS). Phân loại: **`INCOMPATIBLE`**.
