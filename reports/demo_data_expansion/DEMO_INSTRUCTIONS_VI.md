# Hướng Dẫn Thao Tác & Lựa Chọn Tệp CSV Khi Trình Diễn Web Demo Trước Giảng Viên

**Dự án:** Tối ưu hóa chi phí bảo trì dự đoán hệ thống khí nén xe tải Scania APS (UCI #421)  
**Ứng dụng:** `app.py` (Web Demo cục bộ)  
**Checkpoint đã khóa:** `trial16_refit_20261127_02` (Random Forest 50 cây, `class_weight="balanced"`, ngưỡng tối ưu chi phí $\tau^* = 0.3232440937634324$)  
**Bộ tiền xử lý đã khóa:** `data/processed/scania_aps/official_20261029_04/tree_preprocessor.joblib` (`SimpleImputer(strategy="median")` học trên `48.000` mẫu Train)

---

## 1. Khởi Động Nhanh Trước Buổi Bảo Vệ / Demo

Từ thư mục gốc của đồ án, kiểm tra toàn vẹn artifact và mở máy chủ Web Demo (có thể dùng cổng mặc định `8501` hoặc cổng riêng như `8517` để tránh xung đột với các tiến trình khác):

```powershell
# 1. Kiểm chứng toàn vẹn 32 artifact lịch sử, 20 trial Optuna và 101 điểm lưới ngưỡng Validation
.\.venv\Scripts\python.exe app.py --verify

# 2. Khởi động máy chủ Web Demo (ví dụ cổng 8501 hoặc 8517)
.\.venv\Scripts\python.exe app.py --port 8517
```

Sau đó mở trình duyệt tại `http://localhost:8517` (hoặc `http://localhost:8501`) và chuyển sang mục **Dự đoán CSV** (Live Prediction).

> **4 Nguyên Tắc Học Thuật Bắt Buộc Khi Thuyết Minh Trước Giảng Viên:**
> 1. **Phân biệt rõ kết quả Demo và kết quả Đánh giá Khoa học:** Toàn bộ các tệp CSV trong `data/examples/demo_cases/` là **các lát cắt nhỏ ($5$ đến $1.000$ dòng) trích từ phân vùng Validation nghiên cứu (`12.000` mẫu G3)** nhằm minh họa trực tiếp luồng suy luận, kiểm tra hợp đồng dữ liệu và cơ chế ra quyết định theo ngưỡng/công suất trên giao diện Web. Chúng **không phải** là dữ liệu kiểm thử độc lập (`Official Test` — `16.000` mẫu niêm phong trong `aps+failure+at+scania+trucks.zip`). Kết quả đánh giá khoa học của đồ án phải dẫn chiếu từ toàn tập Validation (`12.000` mẫu, chi phí Trial 16 là $6.330$ ở $M = 578 \le 1.200$) và kết quả đánh giá độc lập duy nhất tại thẻ **Official Test (Gate G10 Run 003)** ($N = 16.000, K = 1.600$, $TP = 357, FP = 484, FN = 18, TN = 15.141$, $\text{Precision} = 42.45\%, \text{Recall} = 95.20\%$, chi phí $C_{\text{test}} = 13.840$, giảm $92.62\%$ so với B0 $187.500$).
> 2. **Ngữ nghĩa chính xác của nhãn `neg`:** Không gọi xe mang nhãn `neg` là *"xe hoàn toàn an toàn"* hay *"xe không có lỗi"*. Theo mô tả gốc của Scania CV AB (`aps_failure_description.txt`), nhóm `neg` là các xe tải vào xưởng do gặp sự cố ở **các bộ phận khác không liên quan đến hệ thống khí nén APS** (chỉ xác định xe không mang nhãn lỗi liên quan đến APS).
> 3. **Bản chất của chính sách ưu tiên Top-$K$ (`threshold_then_top_k`):** Chính sách ưu tiên Top-$K$ là **cơ chế khôi phục tính khả thi về mặt công suất** (cắt giảm số lượt kiểm tra từ $M > K$ về đúng trần $K$ bằng cách giữ lại $K$ xe có điểm rủi ro cao nhất trong số các xe đã qua ngưỡng $\tau$). **Không khẳng định Top-$K$ luôn làm giảm tổng chi phí**: khi các xe bị cắt bỏ do hết công suất xưởng ($M - K$ xe) có chứa xe bị lỗi APS thật ($y = 1$), mỗi ca chuyển từ $TP$ sang $FN$ làm chi phí tăng thêm $+500$ đơn vị (trong khi mỗi ca chuyển từ $FP$ sang $TN$ chỉ giảm được $-10$ đơn vị).
> 4. **Cách xử lý các chỉ số không xác định khi lô không có mẫu `pos` ($P = 0$):** Đối với các lô chỉ gồm các mẫu `neg` ($P = TP + FN = 0$, như `demo_normal.csv` và `demo_missing_values.csv`), mẫu số của $\text{Recall} = TP / (TP + FN)$ bằng $0$ nên Recall không xác định — giao diện Web Demo hiển thị rõ ký hiệu **`—`** (và JSON ghi nhận `null`), tuyệt đối không gán $0\%$ hay chia cho $0$.

---

## 2. Bảng Lựa Chọn Nhanh Tệp CSV & So Sánh Đồng Thời Các Chỉ Số Theo Chính Sách

Khi trình diễn và so sánh các chính sách trên từng tệp, luôn trình bày đồng thời **Công suất ($K$ và số lượt đề xuất $M$), Precision, Recall, số lỗi bỏ sót ($FN$) và Tổng chi phí ($C = 10 \times FP + 500 \times FN$)**:

| Kịch bản trình diễn | Tệp CSV khuyến nghị | $N$ (`pos`/`neg`) | Chính sách ($\tau^* = 0.323244$) | Trần $K$ | Lượt đề xuất $M$ | Precision | Recall | $FN$ ($FP$) | Tổng chi phí $C$ | Điểm nhấn thuyết minh & Ảnh chụp thực tế |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| **1. Mẫu mặc định trên giao diện** | `data/examples/scania_validation_sample.csv` | `12` (`4 / 8`) | Theo ngưỡng<br>Sau ưu tiên Top-$K$ | `1`<br>`1` | `5` (Vượt 4)<br>`1` (Khả thi) | `80.00%`<br>`100.00%` | `100.00%`<br>`25.00%` | `0` (`1`)<br>`3` (`0`) | **10**<br>**1.500** | Nút **Chạy CSV mẫu Validation**. Minh họa khi trần $K=1$ quá hẹp so với 4 xe lỗi APS: cắt từ $M=5$ về $K=1$ khiến $FN$ tăng $0 \to 3$, chi phí tăng $10 \to 1.500$. ([01_scania_validation_sample.png](screenshots/01_scania_validation_sample.png)) |
| **2. Lô hỗn hợp tiêu chuẩn** | `data/examples/demo_cases/demo_mixed.csv` | `100` (`10 / 90`) | Theo ngưỡng<br>Sau ưu tiên Top-$K$ | `10`<br>`10` | `11` (Vượt 1)<br>`10` (Khả thi) | `81.82%`<br>`80.00%` | `90.00%`<br>`80.00%` | `1` (`2`)<br>`2` (`2`) | **520**<br>**1.020** | Minh họa công thức $C = 10\text{FP} + 500\text{FN}$. Khi cắt 1 xe để thỏa trần $K=10$, xe có điểm thấp nhất trong 11 xe vượt ngưỡng là 1 ca `pos` khó phát hiện nên $FN$ tăng $1 \to 2$ ($C: 520 \to 1.020$). ([04_demo_mixed_priority.png](screenshots/04_demo_mixed_priority.png)) |
| **3. Ràng buộc công suất xưởng & Top-$K$** | `data/examples/demo_cases/demo_capacity.csv` | `200` (`20 / 180`) | Theo ngưỡng ($10\%$)<br>Sau ưu tiên ($10\%$)<br>Sau ưu tiên ($5\%$) | `20`<br>`20`<br>`10` | `21` (Vượt 1)<br>`20` (Khả thi)<br>`10` (Khả thi) | `85.71%`<br>`85.00%`<br>`100.00%` | `90.00%`<br>`85.00%`<br>`50.00%` | `2` (`3`)<br>`3` (`3`)<br>`10` (`0`) | **1.030**<br>**1.530**<br>**5.000** | Trình diễn rõ nhất sự đánh đổi đa chiều giữa Công suất $K$, Precision, Recall, $FN$ và Chi phí $C$. Khi siết $K=10$ ($5\%$), Precision đạt $100\%$ nhưng Recall còn $50\%$ ($FN=10 \Rightarrow C=5.000$). ([06a](screenshots/06a_demo_capacity_default_priority.png), [06b](screenshots/06b_demo_capacity_custom_and_export.png), [11](screenshots/11_demo_capacity_metrics_matrix_rows.png)) |
| **4. Độ nhạy phát hiện lỗi APS** | `data/examples/demo_cases/demo_failure.csv` | `20` (`20 / 0`) | Theo ngưỡng<br>Sau ưu tiên Top-$K$ | `2`<br>`2` | `19` (Vượt 17)<br>`2` (Khả thi) | `100.00%`<br>`100.00%` | `95.00%`<br>`10.00%` | `1` (`0`)<br>`18` (`0`) | **500**<br>**9.000** | Theo ngưỡng $\tau^*$, mô hình bắt được $19/20$ xe lỗi APS ($\text{Recall}=95\%, FN=1, C=500$). Nếu xưởng chỉ có công suất $K=2$ lượt, chính sách ưu tiên chỉ nhận được 2 xe điểm cao nhất, bỏ sót $FN=18$ xe ($C=9.000$). ([03_demo_failure_priority.png](screenshots/03_demo_failure_priority.png)) |
| **5. Xe không mang nhãn lỗi APS & Chỉ số `—`** | `data/examples/demo_cases/demo_normal.csv` | `20` (`0 / 20`) | Theo ngưỡng | `2` | `1` (Khả thi) | `0.00%` | **`—`** ($P=0$) | `0` (`1`) | **10** | Lô 20 xe không mang nhãn lỗi liên quan đến APS (`neg`). Chỉ có $1/20$ xe vượt ngưỡng ($FP=1, TN=19, C=10$). Do $P = TP + FN = 0$, cột **Recall** hiển thị rõ ký hiệu **`—`** (không xác định). ([02_demo_normal.png](screenshots/02_demo_normal.png), [12](screenshots/12_demo_normal_metrics_matrix.png)) |
| **6. Điền khuyết dữ liệu thiếu (`na`)** | `data/examples/demo_cases/demo_missing_values.csv` | `30` (`0 / 30`, $445$ ô `na`) | Theo ngưỡng | `3` | `1` (Khả thi) | `0.00%` | **`—`** ($P=0$) | `0` (`1`) | **10** | 100% dòng có giá trị khuyết `na`. Kiểm chứng bộ điền khuyết trung vị `tree_preprocessor.joblib` học trên Train và hiển thị Recall = **`—`** khi $P=0$. ([05_demo_missing_values.png](screenshots/05_demo_missing_values.png)) |
| **7. Hiệu năng dự đoán hàng loạt** | `data/examples/demo_cases/demo_large_batch.csv` | `1.000` (`21 / 979`) | Theo ngưỡng | `100` | `49` (Khả thi) | `38.78%` | `90.48%` | `2` (`30`) | **1.300** | Lô 1.000 mẫu ở tỷ lệ mất cân bằng tự nhiên ($\approx 2.1\%$ `pos`). Số đề xuất $M = 49 \le K = 100$ hoàn toàn khả thi dưới trần $10\%$, bắt được $19/21$ ca lỗi APS trong $\sim 160\text{ ms}$. ([07_demo_large_batch.png](screenshots/07_demo_large_batch.png)) |
| **8. Vận hành thực tế không có nhãn** | `data/examples/demo_cases/demo_unlabeled.csv` | `50` (*Không cột `class`*) | Theo ngưỡng<br>Sau ưu tiên Top-$K$ | `5`<br>`5` | `7` (Vượt 2)<br>`5` (Khả thi) | `—` | `—` | `—` | `—` | Giao diện hiển thị rõ: *"Lô chưa có nhãn class. Chi phí, FP, FN và các chỉ số đánh giá cần nhãn thực tế."* và ẩn bảng chỉ số đánh giá, chỉ xuất điểm và quyết định từng dòng. ([08_demo_unlabeled.png](screenshots/08_demo_unlabeled.png), [13](screenshots/13_demo_unlabeled_rows_export.png)) |
| **9. Chặn lỗi sai hợp đồng Schema** | `data/examples/demo_cases/demo_invalid.csv` | `5` (*Sai header*) | Bị chặn (`HTTP 400`) | `—` | `—` | `—` | `—` | `—` | `—` | Hiển thị thông báo lỗi đỏ: *"CSV không đúng schema Scania APS: thiếu 1 cột (eg_000), có 1 cột ngoài schema."* (Sử dụng 5 dòng vì lỗi header bị chặn ngay ở dòng 1). ([09_demo_invalid.png](screenshots/09_demo_invalid.png)) |
| **10. Lát cắt từ bản lưu trữ UCI #414** | `data/examples/external_sources/uci414_ida2016_duplicate_validation_50.csv` | `50` (`2 / 48`) | Theo ngưỡng | `5` | `4` (Khả thi) | `50.00%` | `100.00%` | `0` (`2`) | **20** | Bản sao trùng nguồn gốc UCI (`COMPATIBLE_DUPLICATE`, **không phải dữ liệu độc lập**), lọc 50 dòng thuộc Validation G3: $M = 4 \le K = 5$, bắt đủ $2/2$ xe lỗi APS ($FN=0, C=20$). ([10_external_uci414_duplicate.png](screenshots/10_external_uci414_duplicate.png)) |

---

## 3. Quy Trình 5 Bước Thao Tác Trực Tiếp Trên Giao Diện Web Demo

1. **Bước 1 — Chạy mẫu mặc định và tải tệp CSV:**
   - Tại tab **Dự đoán CSV**, nhấn **Chạy CSV mẫu Validation** (`#live-sample`) để kiểm tra nhanh lô 12 dòng mặc định, sau đó dùng ô chọn tệp (`#live-file`) để tải lên `demo_capacity.csv` hoặc `demo_mixed.csv` và nhấn **Dự đoán CSV** (`#live-upload`).
2. **Bước 2 — Phân tích đồng thời Công suất, Precision, Recall, $FN$ và Tổng chi phí ở ngưỡng đã khóa ($\tau^* = 0.3232440937634324$):**
   - Trên `demo_capacity.csv` ($N = 200$, $K = 20$ ở mức $10\%$), chỉ ra rằng chính sách **Theo ngưỡng** đề xuất $M = 21$ lượt (vượt trần công suất 1 lượt), đạt $\text{Precision} = 85.71\%, \text{Recall} = 90.00\%, FN = 2, FP = 3$, tổng chi phí $C = 1.030$.
3. **Bước 3 — Thử nghiệm bật/tắt ưu tiên Top-$K$, thay đổi công suất ($K$) và ngưỡng ($\tau$):**
   - Tích chọn **Ưu tiên tối đa K lượt khi vượt trần** (`#live-prioritize`) $\rightarrow$ bảng chỉ số hiển thị song song hai dòng **Theo ngưỡng** ($M=21, C=1.030$) và **Sau ưu tiên** ($M=20=K, TP=17, FP=3, FN=3, \text{Precision}=85.00\%, \text{Recall}=85.00\%, C=1.530$). Giải thích rõ: Top-$K$ giúp khôi phục tính khả thi công suất ($M \le K$), nhưng việc phải bỏ bớt 1 lượt kiểm tra khi xe thứ 21 là một ca `pos` khiến $FN$ tăng từ $2 \to 3$ và chi phí tăng từ $1.030 \to 1.530$.
   - Giảm giới hạn công suất từ `10` (%) xuống `5` (%) ($K = 10$) $\rightarrow$ chính sách **Sau ưu tiên** giữ lại đúng 10 xe có điểm cao nhất (cả 10 xe đều là `pos`, $\text{Precision} = 100\%, FP = 0$), nhưng do xưởng chỉ khám được 10/20 xe lỗi nên $\text{Recall} = 50\%, FN = 10, C = 5.000$.
   - Thử tăng ngưỡng $\tau$ lên `0.50` $\rightarrow$ số lượt đề xuất giảm xuống $M = 17 \le K = 20$ ($\text{Precision} = 94.12\%$), nhưng bỏ sót $FN = 4$ xe lỗi ($\text{Recall} = 80.00\%$), làm tổng chi phí tăng lên $C = 2.010$.
4. **Bước 4 — Xuất CSV kết quả quyết định:**
   - Nhấn nút **Xuất CSV kết quả** (`#live-export`) để tải tệp `scania_aps_predictions.csv` xuống máy, gồm đúng 8 cột: `row,aps_positive_score,threshold,threshold_action,capacity_action,capacity_limit,model_version,policy`.
5. **Bước 5 — Trình diễn trường hợp không có mẫu `pos` (`Recall = —`), lô không nhãn và chặn tệp sai schema:**
   - Tải `demo_normal.csv` để chỉ ra cột `Recall` hiển thị **`—`** khi lô không có mẫu dương thực tế ($P = 0$) và giải thích nhãn `neg` chỉ có nghĩa là không mang nhãn lỗi APS.
   - Tải `demo_unlabeled.csv` để minh họa chế độ vận hành thực tế khi chưa có nhãn `class`.
   - Tải `demo_invalid.csv` để minh họa chốt chặn `FeatureContract` trả về `HTTP 400` ngay lập tức.
