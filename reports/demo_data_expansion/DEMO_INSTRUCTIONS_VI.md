# Hướng Dẫn Thao Tác & Lựa Chọn Tệp CSV Khi Trình Diễn Web Demo Trước Giảng Viên

**Dự án:** Tối ưu hóa chi phí bảo trì dự đoán hệ thống khí nén xe tải Scania APS (UCI #421)  
**Ứng dụng:** `app.py` (Web Demo cục bộ tại `http://localhost:8501`)  
**Checkpoint đã khóa:** `trial16_refit_20261127_02` (Random Forest 50 cây, `class_weight="balanced"`, ngưỡng tối ưu chi phí $\tau^* = 0.3232440937634324$)  
**Bộ tiền xử lý đã khóa:** `data/processed/scania_aps/official_20261029_04/tree_preprocessor.joblib` (`SimpleImputer(strategy="median")` học trên `48.000` mẫu Train)

---

## 1. Khởi Động Nhanh Trước Buổi Bảo Vệ / Demo

Từ thư mục gốc của đồ án, kiểm tra toàn vẹn artifact và mở máy chủ Web Demo:

```powershell
# 1. Kiểm chứng toàn vẹn 32 artifact lịch sử, 20 trial Optuna và 101 điểm lưới ngưỡng Validation
.\.venv\Scripts\python.exe app.py --verify

# 2. Khởi động máy chủ Web Demo tại http://localhost:8501
.\.venv\Scripts\python.exe app.py
```

Sau đó mở trình duyệt tại [http://localhost:8501](http://localhost:8501) và chuyển sang mục **Dự đoán CSV** (Live Prediction).

> **Lưu ý giải thích với Giảng viên:**
> - Toàn bộ các tệp CSV trong `data/examples/demo_cases/` là **dữ liệu trích từ phân vùng Validation nghiên cứu (`12.000` mẫu G3)** nhằm minh họa trực tiếp luồng suy luận, kiểm tra hợp đồng dữ liệu và tối ưu hóa quyết định theo ngưỡng/công suất trên giao diện Web.
> - Đây **không phải** là dữ liệu kiểm thử độc lập (`Official Test` — `16.000` mẫu niêm phong trong `aps+failure+at+scania+trucks.zip`). Kết quả đánh giá độc lập duy nhất trên Official Test nằm ở thẻ **Official Test (Gate G10 Run 003)** trên bảng điều khiển lịch sử ($C_{\text{test}} = 37.820$, giảm $79.83\%$ so với $187.500$).

---

## 2. Bảng Lựa Chọn Nhanh Tệp CSV Theo Kịch Bản Câu Hỏi Của Giảng Viên

| Kịch bản trình diễn / Câu hỏi của Giảng viên | Tệp CSV khuyến nghị sử dụng | Số dòng | Kết quả mặc định ($\tau^* = 0.323244$, $K = 10\%$) | Điểm nhấn cần thuyết minh |
|---|---|---:|---|---|
| **Kịch bản 1 (Mặc định):** *"Hãy chạy thử một lô hỗn hợp tiêu chuẩn để xem ma trận nhầm lẫn và chi phí."* | `data/examples/demo_cases/demo_mixed.csv` | `100` (`10 pos`, `90 neg`) | Theo ngưỡng: $M = 11 > K = 10$ ($TP=9, FP=2, FN=1, TN=88$, $C = 520$). Bật ưu tiên top-$K$ ($K=10$): giữ $10$ xe điểm cao nhất ($TP=8, FP=2, FN=2, TN=88$, $C = 1.020$). | Minh họa rõ ràng công thức chi phí bất đối xứng $C = 10 \times FP + 500 \times FN$ và sự đánh đổi giữa ngưỡng phân loại với trần công suất xưởng $K$. |
| **Kịch bản 2 (Ràng buộc công suất xưởng):** *"Khi số xe vượt ngưỡng nhiều hơn năng lực sửa chữa $K$ của xưởng thì hệ thống xử lý thế nào?"* | `data/examples/demo_cases/demo_capacity.csv` | `200` (`20 pos`, `180 neg`) | Công suất $10\%$ là $K = 20$ lượt, nhưng ngưỡng $\tau^*$ đề xuất $M = 21$ lượt (vượt $1$ lượt, báo đỏ **Không khả thi theo ngưỡng**). Khi tích chọn **Ưu tiên điểm cao nhất khi vượt K**, hệ thống cắt đúng về $K = 20$ lượt ($TP=17, FP=3, FN=3, TN=177$, $C = 1.530$). | Trình diễn trực tiếp ràng buộc công suất thực tế $M \le K$ và chính sách `threshold_then_top_k`. Có thể giảm tiếp công suất xuống $5\%$ ($K = 10$) để thấy hệ thống giữ lại đúng $10$ xe có điểm rủi ro cao nhất (đạt $TP=10, FP=0, Precision = 100\%$). |
| **Kịch bản 3 (Độ nhạy phát hiện lỗi APS):** *"Mô hình có bắt được các xe bị hỏng hệ thống khí nén APS thực sự không?"* | `data/examples/demo_cases/demo_failure.csv` | `20` (`20 pos`, `0 neg`) | Ngưỡng $\tau^*$ bắt được **$19 / 20$ xe lỗi APS** ($TP=19, FN=1, Recall = 95.00\%, Precision = 100\%, C = 500$). Nếu so với ngưỡng mặc định $\tau = 0.50$, mô hình chỉ bắt được $18/20$ xe ($FN=2, C = 1.000$). | Chứng minh vì sao việc hạ ngưỡng từ $0.50$ xuống $\tau^* = 0.323244$ giúp giảm thiểu lỗi bỏ sót xe hỏng ($FN$, phạt $500$/xe). |
| **Kịch bản 4 (Kiểm soát báo động giả trên xe không hỏng APS):** *"Nếu đưa vào toàn bộ xe không bị lỗi APS thì mô hình có báo động giả nhiều không?"* | `data/examples/demo_cases/demo_normal.csv` | `20` (`0 pos`, `20 neg`) | Ngưỡng $\tau^*$ chỉ phát sinh **$1$ báo động giả** trên $20$ xe ($TN=19, FP=1, M=1 \le K=2$, chi phí $C = 10$). | Cho thấy điểm dự đoán trung vị của nhóm `neg` rất thấp ($\text{median} = 0.00975$), chỉ có 1/20 xe có triệu chứng gần giống APS vượt ngưỡng. |
| **Kịch bản 5 (Xử lý dữ liệu cảm biến bị khuyết):** *"Dữ liệu thực tế từ xe tải có rất nhiều ô trống `na`, hệ thống xử lý thế nào?"* | `data/examples/demo_cases/demo_missing_values.csv` | `30` (`0 pos`, `30 neg`, $100\%$ dòng có `na`, tổng $445$ ô `na`) | Tải và suy luận thành công trong $\sim 46\text{ ms}$ ($TN=29, FP=1, M=1 \le K=3, C = 10$). | Giải thích quy trình tiền xử lý không rò rỉ: mọi ô `na` được điền bằng vector trung vị cố định đã học trên `48.000` mẫu Train (`tree_preprocessor.joblib`, SHA-256 được xác minh trước mỗi lượt dự đoán). |
| **Kịch bản 6 (Vận hành thực tế không có nhãn):** *"Trong thực tế khi xe mới về xưởng thì làm gì đã có cột nhãn `class`?"* | `data/examples/demo_cases/demo_unlabeled.csv` | `50` (`170` cột, không có cột `class`) | Hệ thống chấm điểm 50 xe, đề xuất $M = 7$ xe theo ngưỡng (hoặc $5$ xe sau ưu tiên $K=5$), đồng thời hiển thị thông báo: *"Lô chưa có nhãn class. Chi phí, FP, FN và các chỉ số đánh giá cần nhãn thực tế."* | Chứng minh hệ thống tách biệt minh bạch giữa chế độ suy luận vận hành (chỉ xuất điểm và quyết định) và chế độ kiểm định có nhãn (tính $TP, FP, FN, TN, C$), tuyệt đối không bịa chỉ số khi thiếu nhãn. |
| **Kịch bản 7 (Hiệu năng dự đoán hàng loạt):** *"Hệ thống xử lý lô tối đa 1.000 xe mất bao lâu?"* | `data/examples/demo_cases/demo_large_batch.csv` | `1.000` (`21 pos`, `979 neg`) | Xử lý toàn bộ $1.000 \times 170$ giá trị trong **$\sim 160\text{ ms}$**; đề xuất $M = 49 \le K = 100$ (Khả thi ngay theo ngưỡng), bắt được $19/21$ xe lỗi ($TP=19, FP=30, FN=2, TN=949, Recall = 90.48\%, C = 1.300$). | Minh họa tốc độ suy luận tức thời ở ngưỡng giới hạn `MAX_ROWS = 1.000` và phân bố mất cân bằng tự nhiên ($\sim 2.1\%$ `pos`). |
| **Kịch bản 8 (Kiểm tra bắt lỗi Schema / Hợp đồng dữ liệu):** *"Nếu người dùng tải lên file CSV sai tên cột hoặc thiếu cảm biến thì sao?"* | `data/examples/demo_cases/demo_invalid.csv` | `5` (thiếu `eg_000`, thừa `invalid_sensor_xyz`) | Máy chủ trả về `HTTP 400 Bad Request` trong $< 30\text{ ms}$ và hiển thị rõ thông báo đỏ: *"CSV không đúng schema Scania APS: thiếu 1 cột (eg_000), có 1 cột ngoài schema."* | Chứng minh chốt chặn `FeatureContract` kiểm tra nghiêm ngặt đủ tên và đúng thứ tự 170 thuộc tính trước khi cho phép mô hình chạy. |
| **Kịch bản 9 (Dữ liệu từ nguồn lưu trữ bên ngoài):** *"Có thử nghiệm với tệp dữ liệu tải từ kho bên ngoài không?"* | `data/examples/external_sources/uci414_ida2016_duplicate_validation_50.csv` | `50` (`2 pos`, `48 neg`) | Chạy thành công (`HTTP 200`, $\sim 63\text{ ms}$), đề xuất $M = 4 \le K = 5$, bắt đủ $2/2$ xe lỗi ($TP=2, FP=2, FN=0, TN=46, Recall = 100\%, C = 20$). | Giải thích rõ đây là nguồn `COMPATIBLE_DUPLICATE` trích từ bản lưu trữ **UCI #414 (`IDA2016Challenge`)**, trùng nguồn gốc với UCI #421. |

---

## 3. Quy Trình 5 Bước Thao Tác Trực Tiếp Trên Giao Diện Web Demo

1. **Bước 1 — Tải tệp CSV:**
   - Tại khung **Dự đoán CSV**, nhấn nút chọn tệp (`#live-file`) và trỏ tới một trong các tệp ở bảng trên (khuyến nghị bắt đầu bằng `data/examples/demo_cases/demo_mixed.csv` hoặc `demo_capacity.csv`), sau đó nhấn **Dự đoán CSV tải lên**.
2. **Bước 2 — Quan sát kết quả ở ngưỡng nghiên cứu đã khóa ($\tau^* = 0.3232440937634324$):**
   - Chỉ ra phiên bản checkpoint `trial16_refit_20261127_02`, tổng số dòng $N$, công suất $K = \lfloor 0.10 \times N \rfloor$, số đề xuất theo ngưỡng $M$ và trạng thái khả thi ($M \le K$ hoặc vượt công suất $M > K$).
3. **Bước 3 — Thử nghiệm thay đổi ngưỡng phân loại ($\tau$) và công suất ($K$):**
   - Trên tệp `demo_capacity.csv` ($N = 200$, $K = 20$, $M = 21$):
     - Tích vào ô **Ưu tiên điểm cao nhất khi vượt K** (`#live-prioritize`) $\rightarrow$ thấy bảng chỉ số tự động bổ sung dòng thứ hai **"Sau ưu tiên"** với số đề xuất được đưa về đúng $K = 20$, cột thứ 4 trong bảng chi tiết từng xe hiển thị quyết định sau khi cắt theo thứ hạng điểm.
     - Đổi chế độ công suất từ **Phần trăm lô (%)** sang **Số lượt tối đa (K)** hoặc nhập `5` (%) $\rightarrow$ công suất giảm xuống $K = 10$, chính sách ưu tiên giữ lại đúng 10 xe có điểm rủi ro cao nhất (cả 10 xe đều là `pos` thực tế, $TP = 10, FP = 0, Precision = 100\%$).
     - Thử nâng ngưỡng $\tau$ lên `0.50` (ngưỡng mặc định chưa tối ưu chi phí) $\rightarrow$ số xe được đề xuất giảm xuống $M = 17 \le K = 20$, nhưng số lỗi bỏ sót tăng lên $FN = 4$, làm chi phí tăng từ $1.030$ lên $2.010$ ($+980$ đơn vị chi phí).
4. **Bước 4 — Xuất CSV kết quả quyết định:**
   - Nhấn nút **Xuất CSV kết quả** (`#live-export`) để tải tệp `scania_aps_predictions.csv` xuống máy. Mở tệp để giảng viên thấy đầy đủ 8 cột chuẩn hóa:
     `row,aps_positive_score,threshold,threshold_action,capacity_action,capacity_limit,model_version,policy`.
5. **Bước 5 — Trình diễn xử lý dữ liệu không nhãn và bắt lỗi schema:**
   - Tải tiếp `demo_unlabeled.csv` để minh họa chế độ suy luận thuần túy khi chưa có nhãn thực tế.
   - Cuối cùng tải `demo_invalid.csv` để minh họa thông báo chặn lỗi schema tức thời.
