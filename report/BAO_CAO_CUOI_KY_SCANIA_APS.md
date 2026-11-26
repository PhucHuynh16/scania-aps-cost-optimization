# Tối ưu hóa chi phí bảo trì dự đoán hệ thống khí nén xe tải Scania

**Học phần:** Nhập môn Tối ưu hóa — Học kỳ 1, Năm học 2026–2027  
**Đơn vị đào tạo:** Khoa Công nghệ Thông tin — Trường Đại học Văn Lang  
**Sinh viên thực hiện:** Huỳnh Phúc (MSSV: 2474802010314)  
**Kho mã nguồn GitHub:** [https://github.com/PhucHuynh16/scania-aps-cost-optimization](https://github.com/PhucHuynh16/scania-aps-cost-optimization)  
**Tập dữ liệu nghiên cứu:** *APS Failure at Scania Trucks* — UCI Machine Learning Repository #421 (Scania CV AB, 2016)

---

## TÓM TẮT ĐỀ TÀI

Báo cáo trình bày việc mô hình hóa và giải bài toán tối ưu hóa chi phí quyết định kiểm tra hệ thống khí nén (Air Pressure System — APS) trên xe tải hạng nặng Scania dựa trên bộ dữ liệu công khai UCI #421 (60.000 mẫu phát triển, 16.000 mẫu kiểm thử độc lập, 170 thuộc tính cảm biến số). Bài toán mang hai đặc trưng cốt lõi của tối ưu hóa ứng dụng trong công nghiệp: (1) ma trận chi phí sai lầm bất đối xứng 50:1 theo chuẩn benchmark IDA 2016, trong đó bỏ sót một xe hỏng APS (False Negative — FN) chịu phạt 500 đơn vị chi phí còn kiểm tra thừa APS trên xe hỏng bộ phận khác (False Positive — FP) chịu phạt 10 đơn vị; và (2) giả định ràng buộc năng lực tiếp nhận của xưởng bảo dưỡng không vượt quá 10% tổng số xe trong chu kỳ đánh giá ($M = TP + FP \le \lfloor N/10 \rfloor$).

Quy trình thực nghiệm tách biệt nghiêm ngặt ba phân vùng Train (48.000 mẫu), Validation (12.000 mẫu) và Official Test (16.000 mẫu). Trên tập Validation, ba mô hình đường cơ sở (G4 Baselines) thiết lập mốc tham chiếu tốt nhất là Logistic Regression tại ngưỡng lý thuyết Bayes $\tau = 10/510 \approx 0.0196$ với tổng chi phí **10.230 đơn vị** ($M = 509 \le 1.200$). Ở giai đoạn tối ưu hóa chính (Phase 2), thuật toán lấy mẫu Bayes Optuna TPE (`seed = 42`, ngân sách 20 trials tuần tự) kết hợp tối ưu hóa chính xác trên toàn bộ tập ngưỡng ứng viên xác suất duy nhất của Random Forest tìm được cấu hình khả thi tốt nhất quan sát được tại **Trial 16** ($\tau^* = 0.323244$), hạ chi phí Validation xuống **6.330 đơn vị** ($M = 578 \le 1.200$, giảm 38,12% so với Logistic Regression và tiết kiệm 93,67% so với không can thiệp). Khi đóng băng cấu hình này để đánh giá độc lập một lần trên 16.000 mẫu Official Test (Gate G10), chính sách đạt tổng chi phí **13.840 đơn vị**, tiết kiệm **92,62%** so với mốc không can thiệp (187.500 đơn vị), phát hiện 357/375 ca hỏng APS (Recall 95,20%) và sử dụng 841/1.600 lượt công suất xưởng.

---

## 1. ĐẶT VẤN ĐỀ

### 1.1. Bối cảnh bài toán bảo trì hệ thống khí nén APS
Trên các dòng xe tải hạng nặng của Scania, hệ thống cấp khí nén (APS) tạo áp suất khí để vận hành phanh chính, phanh đỗ và cơ cấu sang số. Nếu một hư hỏng thuộc hệ thống APS không được phát hiện kịp thời khi xe vào trạm dịch vụ, sự cố mất áp suất giữa hành trình sẽ gây dừng xe đột xuất trên đường cao tốc, kéo theo chi phí cứu hộ, chậm trễ giao hàng và rủi ro mất an toàn. Ngược lại, nếu mở quy trình tháo kiểm tra chuyên sâu APS một cách tràn lan cho mọi xe vào xưởng, trạm dịch vụ sẽ tốn thêm giờ công kiểm tra không cần thiết và nhanh chóng bị quá tải cầu nâng cũng như thiết bị đo kiểm chuyên dụng.

### 1.2. Bản chất dữ liệu và ngữ nghĩa lớp nhãn UCI #421
Theo tài liệu gốc của Scania CV AB (IDA 2016 Industrial Challenge), bộ dữ liệu gồm các lượt xe vào xưởng dịch vụ với hai lớp nhãn:
- **Lớp dương (`pos`, $y = 1$):** Xe gặp sự cố xuất phát từ một bộ phận cụ thể thuộc hệ thống khí nén APS (chiếm 1.000/60.000 mẫu, tương đương 1,67% trong tập phát triển; và 375/16.000 mẫu, tương đương 2,34% trong tập Official Test).
- **Lớp âm (`neg`, $y = 0$):** Xe vào xưởng do hư hỏng ở **các bộ phận khác không liên quan đến APS** (như động cơ, hệ thống điện hoặc truyền động), không phải là xe hoàn toàn khỏe mạnh.

Mỗi quan sát gồm 170 thuộc tính cảm biến số đã được ẩn danh tên vật lý (ký hiệu từ `aa_000` đến `eg_000`, bao gồm cả các bộ đếm đơn lẻ và các bin tần suất dạng histogram) với tỷ lệ khuyết thiếu giá trị (`na`) đáng kể ở nhiều cột.

### 1.3. Mục tiêu và câu hỏi tối ưu hóa
Nghiên cứu chuyển bài toán phân loại nhị phân mất cân bằng thành bài toán ra quyết định tối ưu có ràng buộc tài nguyên, nhằm trả lời câu hỏi trung tâm: *Với dữ liệu cảm biến lịch sử và giới hạn xưởng chỉ tiếp nhận kiểm tra chuyên sâu APS tối đa cho 10% số lượt xe, cần lựa chọn bộ siêu tham số mô hình học máy $\theta$ và ngưỡng xác suất hành động $\tau$ như thế nào để cực tiểu hóa tổng chi phí sai lầm benchmark mà không vi phạm trần công suất xưởng, đồng thời vẫn duy trì hiệu quả khi kiểm tra độc lập trên tập Official Test?*

---

## 2. MÔ HÌNH HÓA BÀI TOÁN TỐI ƯU

### 2.1. Biến quyết định và miền tìm kiếm
Xét một tập đánh giá gồm $N$ quan sát $\{(x_i, y_i)\}_{i=1}^N$ với $x_i \in \mathbb{R}^{170}$ và $y_i \in \{0, 1\}$. Mô hình phân loại rừng ngẫu nhiên (`RandomForestClassifier`) được huấn luyện trên tập Train với vector siêu tham số $\theta \in \Theta$ sẽ sinh ra điểm xác suất dự báo lớp dương $p_i(\theta) = P(y_i = 1 \mid x_i; \theta) \in [0, 1]$.

Quyết định đưa xe thứ $i$ vào kiểm tra APS được xác định qua ngưỡng phân loại $\tau \in [0, 1]$ theo quy ước hợp đồng ngưỡng `P02` (sử dụng dấu bất đẳng thức không ngặt để giữ nguyên nhóm các quan sát có cùng xác suất dự báo, không tách ngẫu nhiên):

$$a_i(\theta, \tau) = \mathbb{I}\big(p_i(\theta) \ge \tau\big) \in \{0, 1\}$$

Trong đó $a_i = 1$ tương ứng với đề xuất kiểm tra chuyên sâu APS và $a_i = 0$ tương ứng với không kiểm tra APS. Vector biến quyết định của bài toán tối ưu là $x = (\theta, \tau) \in \Omega = \Theta \times [0, 1]$, với không gian siêu tham số $\Theta$ được khóa cố định tại tệp cấu hình `configs/scania/phase2_optimization.json`:
- $n_{\text{estimators}} \in \{20, 30, 40, 50, 60\}$ (số lượng cây quyết định, nguyên, bước nhảy 10).
- $\text{max\_depth} \in \{4, 5, \dots, 12\}$ (độ sâu tối đa của mỗi cây, nguyên, bước nhảy 1).
- $\text{min\_samples\_split} \in \{2, 3, \dots, 10\}$ (số mẫu tối thiểu để phân tách nút trong, nguyên, bước nhảy 1).
- $\text{max\_features} \in [0.20, 0.50]$ (tỷ lệ đặc trưng xét ngẫu nhiên tại mỗi nút tách, số thực liên tục).

Các tham số còn lại của mô hình được giữ cố định để đảm bảo tính tất định và xử lý mất cân bằng lớp: `class_weight = "balanced"`, `bootstrap = True`, `random_state = 42`, `n_jobs = 1`.

### 2.2. Hàm mục tiêu chi phí bất đối xứng
Theo chuẩn đánh giá IDA 2016 của Scania CV AB, ma trận chi phí sai lầm gán trọng số $c_{FP} = 10$ cho mỗi trường hợp kiểm tra thừa ($y_i = 0, a_i = 1$), $c_{FN} = 500$ cho mỗi trường hợp bỏ sót lỗi APS ($y_i = 1, a_i = 0$), và bằng $0$ cho các quyết định đúng ($TP, TN$). Tổng chi phí trên phân vùng $N$ quan sát là:

$$f(\theta, \tau) = 10 \cdot FP(\theta, \tau) + 500 \cdot FN(\theta, \tau) = 10 \sum_{i=1}^N (1 - y_i) a_i(\theta, \tau) + 500 \sum_{i=1}^N y_i \big(1 - a_i(\theta, \tau)\big)$$

Đặt $P = \sum_{i=1}^N y_i$ là tổng số ca lỗi APS thực tế và $M(\theta, \tau) = \sum_{i=1}^N a_i(\theta, \tau) = TP + FP$ là tổng số lượt xe đưa vào kiểm tra APS, hàm mục tiêu có thể viết lại tương đương dưới dạng đại số $f(\theta, \tau) = 10 M(\theta, \tau) + 500 P - 510 \cdot TP(\theta, \tau)$. Đơn vị của $f(\theta, \tau)$ là **đơn vị chi phí benchmark quy ước**, không đại diện trực tiếp cho tiền tệ thanh toán thực tế.

### 2.3. Ràng buộc công suất xưởng và bài toán tối ưu tổng quát
Để phản ánh giới hạn tiếp nhận của trạm bảo dưỡng, đồ án áp đặt giả định kịch bản vận hành: tổng số lượt xe đưa vào kiểm tra APS không vượt quá 10% kích thước phân vùng đánh giá:

$$M(\theta, \tau) = TP(\theta, \tau) + FP(\theta, \tau) \le K = \left\lfloor \frac{N}{10} \right\rfloor$$

Cụ thể, $K_{\text{val}} = \lfloor 12.000 / 10 \rfloor = 1.200$ lượt xe trên tập Validation và $K_{\text{test}} = \lfloor 16.000 / 10 \rfloor = 1.600$ lượt xe trên tập Official Test. Mọi cặp $(\theta, \tau)$ sinh ra $M(\theta, \tau) > K$ đều bị xếp vào trạng thái không khả thi (`INFEASIBLE`). Bài toán tối ưu hóa hoàn chỉnh trên tập Validation được viết thành:

$$\min_{\theta \in \Theta,\; \tau \in [0, 1]} \; f(\theta, \tau) = 10 \cdot FP(\theta, \tau) + 500 \cdot FN(\theta, \tau) \quad \text{sao cho} \quad g(\theta, \tau) = TP(\theta, \tau) + FP(\theta, \tau) - 1.200 \le 0$$

### 2.4. Mối liên hệ với ngưỡng tỷ lệ chi phí Bayes không ràng buộc
Trong bài toán không giới hạn công suất, nếu điểm $p$ là xác suất đã hiệu chuẩn, kiểm tra có chi phí kỳ vọng thấp hơn hoặc bằng bỏ qua khi $10(1-p)\le500p$, tức $p\ge10/510\approx0{,}019608$. Khi có giới hạn công suất, cần kiểm tra tính khả thi của ngưỡng này. Ở Trial 16, điểm lưới gần nhất $0{,}02$ đòi hỏi 2.313 lượt kiểm tra, vượt trần 1.200.

---

## 3. PHƯƠNG PHÁP ĐƯỜNG CƠ SỞ & THUẬT TOÁN TỐI ƯU HÓA

### 3.1. Hệ thống mô hình đường cơ sở (Gate G4 Baselines)
Ba mô hình đường cơ sở được cài đặt tại `src/scania/baselines.py` và cấu hình khóa tại `configs/scania/g4_baselines.json`:
1. **B0 — Majority Dummy:** Chính sách phản ứng thụ động $a_i = 0, \forall i$ (không đưa xe nào vào kiểm tra APS). Chi phí tham chiếu của B0 bằng $500 P$ ($100.000$ đơn vị trên Validation; $187.500$ đơn vị trên Official Test).
2. **B1 — Decision Stump:** Cây quyết định một tầng `DecisionTreeClassifier(max_depth=1, random_state=42)` huấn luyện trên tập Train đã điền khuyết trung vị, chấm tại hai ngưỡng cố định: ngưỡng mặc định $\tau = 0.5000$ (chính sách chính) và ngưỡng tỷ lệ chi phí Bayes $\tau = 10/510 \approx 0.0196$ (chính sách phụ).
3. **B2 — Logistic Regression:** Hồi quy logistic `LogisticRegression(C=1.0, solver="lbfgs", max_iter=2000, random_state=42)` huấn luyện trên tập Train đã điền khuyết trung vị và chuẩn hóa `StandardScaler`, chấm tại cùng hai ngưỡng cố định $\tau = 0.5000$ và $\tau = 10/510 \approx 0.0196$.

### 3.2. Phương pháp tối ưu hóa chính (Phase 2: Random Forest + Optuna TPE hai tầng)
Phương pháp tối ưu hóa chính (`src/scania/phase2_optimization.py`) giải bài toán hai tầng lồng nhau trong ngân sách 20 lượt đánh giá mô hình:
- **Tầng ngoài — Tìm kiếm siêu tham số bằng Optuna TPE:** Bộ lấy mẫu `TPESampler(seed=42)` xây dựng ước lượng mật độ hạt nhân phân tách giữa nhóm cấu hình có hàm mục tiêu thấp và nhóm cấu hình còn lại để đề xuất tuần tự 20 bộ siêu tham số $\theta^{(0)}, \dots, \theta^{(19)} \in \Theta$. Mỗi trial chỉ được phép gọi đúng 1 lần `model.fit()` trên 48.000 mẫu Train (kiểm soát bởi bộ đếm bền vững `FitCounter` ghi nhận trạng thái xuống đĩa trước khi huấn luyện).
- **Tầng trong — Tối ưu hóa chính xác ngưỡng quyết định có ràng buộc (không huấn luyện lại):**
  - Với vector điểm xác suất dự báo $p = p(\theta^{(t)}) \in [0, 1]^{12000}$ trên tập Validation, hàm `enumerate_threshold_candidates(p)` liệt kê tập tất cả các giá trị ngưỡng ứng viên phân biệt $T(p) = \{0.0, 1.0\} \cup \text{unique}(p)$. Vì hàm bước $a_i = \mathbb{I}(p_i \ge \tau)$ chỉ đổi trạng thái tại đúng các giá trị $p_i$ xuất hiện trong dữ liệu, tập $T(p)$ bao phủ toàn bộ các vector quyết định khả dĩ trên $[0, 1]$.
  - Hàm `evaluate_threshold_candidates_vectorized` sắp xếp mảng xác suất một lần duy nhất và dùng mảng tổng tích lũy kết hợp `np.searchsorted(..., side="left")` để tính chính xác $(TP, FP, FN, M, \text{Cost})$ cho mọi $\tau \in T(p)$. Các ứng viên vi phạm $M > 1.200$ bị loại; trong số các ứng viên thỏa mãn $M \le 1.200$, thuật toán chọn $\tau^*$ đạt chi phí nhỏ nhất theo thứ tự phá hòa tất định: `(total_cost, M, -threshold)`.
- **Phân biệt với lưới trực quan hóa 101 điểm:** Song song với việc chọn nghiệm ứng viên chính xác $\tau^* \in T(p)$, hệ thống tính thêm các chỉ số trên lưới đều 101 điểm $\tau \in \{0.00, 0.01, \dots, 1.00\}$ lưu vào trường `threshold_curve` trong tệp kết quả JSON. Lưới 101 điểm này chỉ dùng để vẽ đồ thị đánh đổi và lập bảng khảo sát độ nhạy, hoàn toàn không làm giảm độ chính xác của bước chọn ngưỡng $\tau^*$.

---

## 4. DỮ LIỆU & THIẾT KẾ THỰC NGHIỆM

### 4.1. Nguồn gốc dữ liệu, bản quyền và kiểm tra toàn vẹn
Dữ liệu do Scania CV AB công bố qua UCI #421 (DOI [10.24432/C51S51](https://doi.org/10.24432/C51S51)). Trang UCI ghi giấy phép CC BY 4.0. Tài liệu mô tả đi kèm bản phân phối ghi thông báo GPLv3 hoặc mới hơn của Scania. Kho nộp bài có ZIP gốc, CSV phát triển, manifest thu thập và dữ liệu Train/Validation đã tiền xử lý. Kích thước và mã băm SHA-256 được ghi tại [data/README.md](../data/README.md).

### 4.2. Phân vùng dữ liệu và quy trình tiền xử lý chống rò rỉ (Giao thức G3)
Theo pipeline G3 (`scripts/run_scania_pipeline.py`, mã băm đối tượng ổn định `efe781b7e564073a2a764e70a41cfe5c3e8975d33cc38b0fa297ef09f51767bb`):
- **Phân vùng Train (48.000 mẫu — 80%):** Gồm 800 ca `pos` (1,67%) và 47.200 ca `neg` (98,33%). Bộ tiền xử lý nhánh cây (`SimpleImputer(strategy="median")`) và nhánh tuyến tính (`SimpleImputer(strategy="median")` + `StandardScaler()`) chỉ được `fit` trên 48.000 mẫu Train này.
- **Phân vùng Validation (12.000 mẫu — 20%):** Gồm 200 ca `pos` (1,67%) và 11.800 ca `neg` (98,33%), tách phân tầng với `seed = 42`, rời nhau hoàn toàn với Train. Chỉ áp dụng phép biến đổi tĩnh `transform` từ bộ tiền xử lý đã học trên Train.
- **Official Test (16.000 mẫu)** có 375 ca pos (2,34%) và 15.625 ca neg (97,66%). CSV nằm trong ZIP gốc và được giữ ngoài quá trình phát triển. G10 Run 003 là lượt duy nhất có kết quả chấm điểm. Hai lần đọc trước đó dừng do lỗi kỹ thuật như mô tả ở Mục 6.2.

### 4.3. Môi trường tính toán và giám sát tài nguyên
Thực nghiệm chạy trên hệ điều hành Windows 11 x64, Python `3.11.9`, với các phiên bản thư viện khóa tại `configs/scania/phase2_requirements.lock.txt`: `numpy==2.4.6`, `scipy==1.17.1`, `scikit-learn==1.9.1`, `optuna==5.0.0`, `joblib==1.6.0`, `threadpoolctl==3.7.0`. Mọi tiến trình thực nghiệm thật đều khởi chạy bên trong **Windows Job Object** với giới hạn cứng: `1` luồng tính toán bản địa (`OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, kiểm tra qua `NativeSession`), trần bộ nhớ `2048 MB`, và giới hạn thời gian `900 giây` cho Phase 2 (`180 giây` cho Gate G10).

---

## 5. KẾT QUẢ THỰC NGHIỆM

### 5.1. Kết quả đường cơ sở G4 trên tập Validation (Run `scania_g4_b2_real_002`)
Bảng dưới đây trình bày kết quả đo đạc thực tế của 5 chính sách đường cơ sở trên 12.000 mẫu Validation (200 ca lỗi APS thực tế, trần công suất $K_{\text{val}} = 1.200$):

| Mã | Mô hình cơ sở | Ngưỡng $\tau$ | TP | FP | TN | FN | Precision | Recall | Chi phí | Xe vào $M$ | Tiết kiệm vs B0 | Trạng thái |
|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| P1 | B0: Majority Dummy | N/A | 0 | 0 | 11.800 | 200 | N/A | 0,00% | 100.000 | 0 | 0,00% | FEASIBLE |
| P2 | B1: Decision Stump | 0,5000 | 0 | 0 | 11.800 | 200 | N/A | 0,00% | 100.000 | 0 | 0,00% | FEASIBLE |
| P3 | B1: Decision Stump | 0,0196 | 160 | 253 | 11.547 | 40 | 38,74% | 80,00% | 22.530 | 413 | 77,47% | FEASIBLE |
| P4 | B2: Logistic Regression | 0,5000 | 129 | 48 | 11.752 | 71 | 72,88% | 64,50% | 35.980 | 177 | 64,02% | FEASIBLE |
| **P5** | **B2: Logistic Regression** | **0,0196** | **186** | **323** | **11.477** | **14** | **36,54%** | **93,00%** | **10.230** | **509** | **89,77%** | **FEASIBLE** |

Tại ngưỡng mặc định $0,5000$, cây quyết định 1 tầng (P2) không gán lá nào có xác suất $\ge 0,5$ nên suy biến về B0 ($100.000$ đơn vị), còn Logistic Regression (P4) bỏ sót tới 71 ca lỗi ($35.980$ đơn vị). Khi hạ xuống ngưỡng tỷ lệ chi phí Bayes $\tau = 10/510 \approx 0,0196$, chính sách P5 của Logistic Regression giảm chi phí xuống **10.230 đơn vị** ($M = 509 \le 1.200$), trở thành mốc tham chiếu tốt nhất của giai đoạn G4.

### 5.2. Kết quả 20 Trials tối ưu hóa Phase 2 (Run `scania_phase2_rf_optuna_002`)
Toàn bộ 20 trials tuần tự của Optuna TPE hoàn tất trong `543,06 giây` (20/20 lượt `fit` thành công, đỉnh RAM `159,82 MB`). Dữ liệu trích xuất từ `trials_summary.csv` như sau:

| Trial | Chi phí | $M$ | Ngưỡng $\tau^*$ | TP | FP | FN | $n_{\text{est}}$ | depth | split | feat | Fit (s) | Trạng thái |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 0 | 7.840 | 576 | 0,2588 | 192 | 384 | 8 | 30 | 12 | 8 | 0,380 | 18,80 | FEASIBLE |
| 1 | 7.790 | 724 | 0,4363 | 195 | 529 | 5 | 20 | 5 | 2 | 0,460 | 7,00 | FEASIBLE |
| 2 | 6.750 | 569 | 0,3154 | 194 | 375 | 6 | 50 | 10 | 2 | 0,491 | 34,68 | FEASIBLE |
| 3 | 7.880 | 682 | 0,5201 | 194 | 488 | 6 | 60 | 5 | 3 | 0,255 | 11,76 | FEASIBLE |
| 4 | 7.800 | 572 | 0,3978 | 192 | 380 | 8 | 30 | 8 | 5 | 0,287 | 10,13 | FEASIBLE |
| 5 | 7.310 | 625 | 0,5609 | 194 | 431 | 6 | 50 | 5 | 4 | 0,310 | 11,73 | FEASIBLE |
| 6 | 6.490 | 594 | 0,2417 | 195 | 399 | 5 | 40 | 11 | 3 | 0,354 | 21,62 | FEASIBLE |
| 7 | 7.520 | 697 | 0,5887 | 195 | 502 | 5 | 40 | 4 | 7 | 0,251 | 6,21 | FEASIBLE |
| 8 | 6.970 | 693 | 0,1801 | 196 | 497 | 4 | 20 | 12 | 10 | 0,443 | 14,61 | FEASIBLE |
| 9 | 7.540 | 699 | 0,5696 | 195 | 504 | 5 | 30 | 4 | 8 | 0,332 | 6,14 | FEASIBLE |
| 10 | 6.340 | 579 | 0,2408 | 195 | 384 | 5 | 60 | 12 | 7 | 0,433 | 71,20 | FEASIBLE |
| 11 | 6.790 | 675 | 0,1739 | 196 | 479 | 4 | 50 | 11 | 4 | 0,388 | 32,75 | FEASIBLE |
| 12 | 7.060 | 600 | 0,2261 | 194 | 406 | 6 | 60 | 12 | 7 | 0,435 | 44,51 | FEASIBLE |
| 13 | 6.880 | 633 | 0,2428 | 195 | 438 | 5 | 20 | 10 | 2 | 0,484 | 14,20 | FEASIBLE |
| 14 | 7.280 | 622 | 0,2200 | 194 | 428 | 6 | 40 | 12 | 6 | 0,500 | 32,49 | FEASIBLE |
| 15 | 6.890 | 634 | 0,3268 | 195 | 439 | 5 | 60 | 8 | 7 | 0,370 | 27,30 | FEASIBLE |
| **16** | **6.330** | **578** | **0,3232** | **195** | **383** | **5** | **50** | **10** | **10** | **0,427** | **38,61** | **BEST** |
| 17 | 6.650 | 610 | 0,2858 | 195 | 415 | 5 | 60 | 10 | 8 | 0,441 | 70,21 | FEASIBLE |
| 18 | 7.070 | 652 | 0,2589 | 195 | 457 | 5 | 50 | 9 | 9 | 0,497 | 31,83 | FEASIBLE |
| 19 | 7.240 | 618 | 0,2392 | 194 | 424 | 6 | 50 | 11 | 10 | 0,440 | 33,46 | FEASIBLE |

Cả 20/20 trials đều tìm được ngưỡng khả thi ($M \in [569, 724] \le 1.200$) với chi phí dao động trong khoảng $[6.330, 7.880]$, thấp hơn đáng kể so với mốc B2 ($10.230$). Đường chi phí khả thi tốt nhất lũy tiến (`best-so-far`) giảm qua các mốc: $7.840$ (Trial 0) $\to 7.790$ (Trial 1) $\to 6.750$ (Trial 2) $\to 6.490$ (Trial 6) $\to 6.340$ (Trial 10) $\to \mathbf{6.330}$ (**Trial 16** theo đánh số từ 0 của Optuna, tức lượt thử thứ **17/20** trên trục hoành 1–20 của Hình 1).

![Hình 1](../figures/optimization/optimization_convergence.png)

![Hình 2](../figures/optimization/cost_vs_capacity_tradeoff.png)

### 5.3. Kết quả đánh giá độc lập trên tập Official Test (Gate G10 — Run `scania_g10_official_test_003`)
Chính sách tốt nhất quan sát được tại Trial 16 ($n_{\text{estimators}} = 50$, $\text{max\_depth} = 10$, $\text{min\_samples\_split} = 10$, $\text{max\_features} = 0,426866$, $\tau^* = 0,3232440937634324$) được đóng băng hoàn toàn. Do Phase 2 không lưu tệp nhị phân của mô hình ra đĩa, Gate G10 thực hiện đúng 1 lần huấn luyện lại tất định trên 48.000 mẫu Train (`31,05s`), kiểm tra chốt chặn hồi quy Validation khớp chính xác 100% các chỉ số của Trial 16 ($TP = 195, FP = 383, FN = 5, TN = 11.417, \text{Cost} = 6.330, M = 578$), sau đó suy luận một lượt duy nhất (`0,039s`) trên 16.000 mẫu Official Test:

| Chỉ số đánh giá | B0 Dummy (Test) | Validation Guard (12.000 mẫu) | **Official Test Độc lập (16.000 mẫu)** |
|---|:---:|:---:|:---:|
| Số ca lỗi APS thực tế ($P$) | 375 (2,34%) | 200 (1,67%) | **375 (2,34%)** |
| True Positives (TP) / False Positives (FP) | 0 / 0 | 195 / 383 | **357 / 484** |
| False Negatives (FN) / True Negatives (TN) | 375 / 15.625 | 5 / 11.417 | **18 / 15.141** |
| Độ nhạy (Recall) / Precision | 0,00% / N/A | 97,50% / 33,74% | **95,20% / 42,45%** |
| Độ đặc hiệu (Specificity) / F1-Score | 100,00% / 0,0000 | 96,75% / 0,5013 | **96,90% / 0,5872** |
| ROC-AUC / PR-AUC | N/A | 0,9903 / 0,7059 | **0,9861 / 0,7495** |
| Chi phí thành phần ($10 \cdot FP$ + $500 \cdot FN$) | 0 + 187.500 | 3.830 + 2.500 | **4.840 + 9.000** |
| **Tổng chi phí benchmark** | **187.500** | **6.330** | **13.840** |
| Lượt xe vào xưởng ($M \le K$) | $0 \le 1.600$ | $578 \le 1.200$ | **841 $\le$ 1.600 (Dư 759 lượt)** |
| **Tỷ lệ tiết kiệm so với B0** | 0,00% | 93,67% | **92,62% (Giảm 173.660 đơn vị)** |

---

## 6. THẢO LUẬN, PHÂN TÍCH ĐỘ NHẠY & HẠN CHẾ NGHIÊN CỨU

### 6.1. Phân tích đánh đổi và độ nhạy theo ngưỡng quyết định $\tau$
Bảng dưới đây trích xuất các điểm đặc trưng từ đường cong 101 điểm `threshold_curve` của cấu hình Trial 16 trên tập Validation (`best_policy.json`):

| Ngưỡng $\tau$ | 0,04 | 0,05 | 0,09 | 0,20 | 0,30 | 0,32 | **0,3232 ($\tau^*$)** | 0,33 | 0,34 | 0,35 | 0,50 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Số ca TP | 198 | 197 | 197 | 196 | 195 | 195 | **195** | 193 | 191 | 190 | 184 |
| Số ca FP | 1.116 | 998 | 758 | 505 | 400 | 385 | **383** | 379 | 373 | 367 | 295 |
| Số ca FN | 2 | 3 | 3 | 4 | 5 | 5 | **5** | 7 | 9 | 10 | 16 |
| Lượt xe $M$ | 1.314 | 1.195 | 955 | 701 | 595 | 580 | **578** | 572 | 564 | 557 | 479 |
| Tổng chi phí | 12.160 | 11.480 | 9.080 | 7.050 | 6.500 | 6.350 | **6.330** | 7.290 | 8.230 | 8.670 | 10.950 |
| Khả thi ($M \le 1200$) | Không | Có | Có | Có | Có | Có | **Có** | Có | Có | Có | Có |

Từ dữ liệu thực nghiệm trên, rút ra ba nhận xét quan trọng:
1. **Ranh giới khả thi trên lưới.** Ngưỡng $0{,}02$ cần 2.313 lượt kiểm tra và ngưỡng $0{,}04$ cần 1.314 lượt, đều vượt trần 1.200. Từ $0{,}05$ (1.195 lượt) trở đi, các ngưỡng trên lưới thỏa ràng buộc.
2. **Vùng chi phí thấp $\tau \in [0,20; 0,32]$:** Trong khoảng này, số ca bỏ sót $FN$ chỉ dao động từ 4 đến 5 ca trong khi $FP$ giảm đều từ 505 xuống 385, giữ tổng chi phí trong dải $[6.350; 7.050]$ và đạt cực tiểu quan sát được $6.330$ tại ngưỡng ứng viên xác suất chính xác $\tau^* = 0,323244$.
3. **Độ nhạy bất đối xứng sắc nét khi $\tau \ge 0,33$:** Chỉ cần tăng nhẹ ngưỡng từ $0,3232$ lên $0,33$, mô hình bỏ sót thêm 2 xe hỏng APS ($FN$ tăng từ 5 lên 7, cộng thêm $1.000$ đơn vị phạt), làm tổng chi phí nhảy vọt lên $7.290$, tiếp tục tăng lên $8.230$ ($\tau = 0,34$) và $8.670$ ($\tau = 0,35$). Vì vậy, phía bên phải của $\tau^*$ không phẳng mà rất nhạy với sai số ước lượng xác suất.

### 6.2. Phân tích các trường hợp chạy lỗi kỹ thuật được bảo lưu
Các lượt chạy dừng sớm giúp giải thích giới hạn thời gian và cách dùng Official Test. Các lượt G4 và Phase 2 có minh chứng trong thư mục [results/scania_aps](../results/scania_aps/). Hai lượt G10 gặp lỗi được lưu trong hồ sơ phát triển.
- G4 Run 001 dừng ở bước kiểm tra môi trường do thiếu metadata của pytest. Lượt chạy ghi nhận 0 lần fit.
- Phase 2 Run 001 chạm giới hạn 300 giây sau 11 lần fit hoàn tất và một lần fit bị ngắt. Run 002 dùng giới hạn 900 giây và lưu đủ 20 kết quả trial.
- G10 Run 001 và 002 đã đọc CSV Official Test vào bộ nhớ rồi dừng tại bước kiểm tra bộ tiền xử lý hoặc nạp thư viện. Cả hai lượt đều dừng trước dự đoán và chấm điểm. Chính sách Trial 16 giữ nguyên.

### 6.3. Hạn chế của nghiên cứu (Limitations)
1. **Thực nghiệm đơn hạt giống (`seed = 42`):** Bộ tối ưu hóa Optuna TPE và mô hình Random Forest trong Phase 2 mới được thực thi với một hạt giống ngẫu nhiên cố định (`seed = 42`) và ngân sách 20 trials; chưa thực hiện lặp lại trên nhiều hạt giống độc lập để báo cáo trung bình và độ lệch chuẩn (`mean ± std`), đồng thời nghiệm Trial 16 chỉ là nghiệm khả thi tốt nhất quan sát được trong 20 trials chứ không phải nghiệm tối ưu toàn cục được chứng minh toán học.
2. Baseline và ngân sách so sánh. Random Forest mặc định đã được bổ sung với một lượt fit và hai cách chọn ngưỡng trên cùng Validation (Phụ lục D). Cấu hình này và Trial 16 khác cả trọng số lớp và siêu tham số. So sánh G4 với Phase 2 còn khác họ mô hình và ngân sách fit.
3. **Khoảng cách giữa mô hình benchmark tĩnh và vận hành thực tế:** Hàm chi phí $10 \cdot FP + 500 \cdot FN$ và trần công suất $10\%$ là mô hình tĩnh trên các bản ghi ẩn danh (không có mã định danh từng xe hay dấu thời gian liên tục), chưa phản ánh chi phí phụ tùng, ca kíp nhân công hay điều độ hàng đợi động tại trạm bảo dưỡng.
4. Mô hình đã huấn luyện và lịch sử phát triển. Checkpoint Trial 16 được refit sau nghiệm thu để dự đoán CSV. Kết quả G10 thuộc lượt đánh giá lịch sử. Bản công bố có lịch sử Git riêng, với các mốc dẫn về kho phát triển tại docs/DEVELOPMENT_HISTORY.md.

---

## 7. KẾT LUẬN

Nghiên cứu đã hoàn thành chuỗi quy trình tối ưu hóa ứng dụng từ phát biểu bài toán công nghiệp, lập mô hình toán học có ràng buộc, xây dựng đường cơ sở, cài đặt thuật toán tối ưu hóa hai tầng đến kiểm định độc lập trên tập Official Test:
1. **Nghiệm và cấu hình được chọn cuối cùng:** Bộ siêu tham số `RandomForestClassifier` tại **Trial 16** (`n_estimators = 50`, `max_depth = 10`, `min_samples_split = 10`, `max_features = 0,426866`, `class_weight = "balanced"`, `random_state = 42`) kết hợp ngưỡng quyết định đóng băng **$\tau^* = 0,3232440937634324$**.
2. **Căn cứ lựa chọn bằng số liệu:** Trên tập Validation 12.000 mẫu, cấu hình này đạt chi phí thấp nhất trong 20 trials là **6.330 đơn vị** (giảm 38,12% so với mốc G4 tốt nhất là Logistic Regression 10.230 đơn vị), bắt đúng 195/200 ca lỗi APS (Recall 97,50%) và chỉ sử dụng 578/1.200 lượt công suất xưởng. Trên tập Official Test độc lập 16.000 mẫu (Gate G10), chính sách đóng băng đạt chi phí **13.840 đơn vị** (tiết kiệm **92,62%** so với không can thiệp), Recall đạt **95,20%** (357/375 ca lỗi) và sử dụng **841/1.600** lượt công suất xưởng. Baseline bổ sung ghi nhận 5.420 trên cùng Validation (Phụ lục D). Trial 16 vẫn là nghiệm chính thức dùng cho G10.
3. **Điều kiện áp dụng:** Chính sách phù hợp làm bộ lọc hỗ trợ quyết định sơ cấp khi phân phối dữ liệu cảm biến đầu vào tương thích với quy trình thu thập của Scania UCI #421 và tỷ lệ chi phí bỏ sót lỗi cao gấp nhiều lần chi phí kiểm tra tại xưởng; khi triển khai thực tế cần hiệu chuẩn lại theo đơn giá bảo dưỡng và năng lực xưởng theo từng ca làm việc.

---

## PHỤ LỤC & KHAI BÁO CÔNG CỤ HỖ TRỢ AI

### Phụ lục A. Tóm tắt giả mã quy trình tối ưu hóa hai tầng (Phase 2)
1. **Đầu vào:** Tập Train $(X_{\text{train}}, y_{\text{train}})$ kích thước $48.000 \times 170$ đã điền khuyết trung vị; tập Validation $(X_{\text{val}}, y_{\text{val}})$ kích thước $12.000 \times 170$; trần công suất $K = 1.200$; ngân sách $B = 20$ trials; hạt giống `seed = 42`.
2. **Lặp $t = 0, 1, \dots, 19$ với `Optuna TPESampler(seed=42)`:**
   - Lấy mẫu $\theta^{(t)} = (n_{\text{estimators}}, \text{max\_depth}, \text{min\_samples\_split}, \text{max\_features}) \in \Theta$.
   - Ghi nhận trạng thái bắt đầu vào `FitCounter`, huấn luyện `model = RandomForestClassifier(theta^(t))` trên $(X_{\text{train}}, y_{\text{train}})$ và tính xác suất $p = \text{model.predict\_proba}(X_{\text{val}})[:, 1]$.
   - Tạo tập ngưỡng ứng viên $T(p) = \{0, 1\} \cup \text{unique}(p)$, tính vector hóa $(TP(\tau), FP(\tau), FN(\tau), M(\tau), \text{Cost}(\tau))$ cho mọi $\tau \in T(p)$.
   - Chọn $\tau^{*(t)} = \arg\min_{\tau \in T(p):\, M(\tau) \le 1200} \big(\text{Cost}(\tau),\, M(\tau),\, -\tau\big)$, lưu bền vững kết quả trial kèm lưới 101 điểm `threshold_curve` và trả $\text{Cost}(\tau^{*(t)})$ về cho Optuna.
3. **Đầu ra:** Nghiệm khả thi có chi phí thấp nhất $(\theta^*, \tau^*)$ qua 20 trials, được kiểm tra toàn vẹn bằng mã băm SHA-256 trước khi khóa cho bước đánh giá độc lập Gate G10.

### Phụ lục B. Liên kết kho mã nguồn & Lệnh kiểm tra nhanh
- **GitHub Repository:** [https://github.com/PhucHuynh16/scania-aps-cost-optimization](https://github.com/PhucHuynh16/scania-aps-cost-optimization)
- **Lệnh trình diễn kết quả đã lưu và kiểm tra mã băm toàn vẹn SHA-256 (Read-Only):**
  - `python scripts/demo.py` (trình bày đầy đủ kết quả, kiểm định nhất quán toán học và mã băm SHA-256 của 32 tệp kết quả).
  - `python scripts/demo.py --verify` (kiểm tra độc lập mã băm toàn vẹn SHA-256, trả mã thoát khác 0 nếu thiếu hoặc sai lệch dữ liệu).

- Web Demo · Cài lockfile Phase 2, chạy python app.py và mở http://localhost:8501. Mục Dự đoán CSV dùng checkpoint đã kiểm chứng và cho phép đặt giới hạn công suất.
- **Kiểm chứng Web Demo:** `python app.py --verify` kiểm tra dữ liệu trước khi mở trình duyệt.

### Phụ lục C. Khai báo công cụ hỗ trợ AI (AI Assistance Disclosure)
Thực hiện quy định tại Mục 10 của Đề bài tập lớn cá nhân (`DE_BAI_TAP_LON_CA_NHAN_5_TUAN_GITHUB_PORTFOLIO.pdf`):
- **Công cụ AI đã sử dụng:** Sinh viên có sử dụng công cụ trợ lý AI (Codex và Google Antigravity) để hỗ trợ lập trình khung điều phối tiến trình con an toàn (Windows Job Object, I/O guard), viết các bài kiểm thử đơn vị tự động (`pytest`), tạo script xuất biểu đồ/tài liệu báo cáo và đối soát lỗi trình bày.
- **Phần sinh viên tự thực hiện, kiểm chứng và chịu trách nhiệm hoàn toàn:** Xác lập mô hình toán học (biến quyết định, hàm mục tiêu $10 \cdot FP + 500 \cdot FN$, ràng buộc công suất $M \le K$), giải thích đúng ngữ nghĩa nhãn `pos`/`neg` từ tài liệu gốc UCI #421, kiểm soát quy trình chống rò rỉ dữ liệu Test, trực tiếp đối chiếu từng con số trong bảng/biểu đồ với các tệp kết quả JSON/CSV gốc và chịu trách nhiệm toàn diện về nội dung báo cáo cũng như phần bảo vệ cá nhân.

### Phụ lục D. Random Forest mặc định và checkpoint bổ sung

Thực nghiệm bổ sung dùng cùng Train 48.000 và Validation 12.000 của G3, seed 42 và một luồng. Random Forest mặc định có 100 cây và class_weight=None. Cả hai ngưỡng của baseline dùng cùng một fit. Ngưỡng 0,1 được chọn bằng quy tắc P02 như Phase 2.

| Chính sách | TP | FP | FN | TN | Chi phí | M/K |
|---|---:|---:|---:|---:|---:|---:|
| RF mặc định · τ=0,5 | 144 | 19 | 56 | 11.781 | 28.190 | 163/1.200 |
| RF mặc định · τ=0,1 | 194 | 242 | 6 | 11.558 | 5.420 | 436/1.200 |
| Trial 16 · τ≈0,323244 | 195 | 383 | 5 | 11.417 | 6.330 | 578/1.200 |

ROC-AUC / Average Precision lần lượt là 0,9921 / 0,8959 cho hai hàng Random Forest mặc định, và 0,9903 / 0,7059 cho Trial 16.

Precision / Recall / F1 theo thứ tự ba hàng là 0,8834 / 0,7200 / 0,7934, 0,4450 / 0,9700 / 0,6101, 0,3374 / 0,9750 / 0,5013.

RF mặc định + quét ngưỡng đạt 5.420, thấp nhất trong các chính sách trên Validation và thấp hơn Trial 16 910 đơn vị (14,38%). Chính sách này giảm 141 FP và 142 lượt kiểm tra, đổi lại tăng 1 FN và Recall giảm từ 97,50% xuống 97,00%. Hai cấu hình khác siêu tham số và class_weight (None và balanced), nên chưa tách được tác động riêng của Optuna.

Baseline fit 45,75 giây và dự đoán Validation 0,110 giây, đỉnh bộ nhớ của job 162,95 MiB. Refit Trial 16 fit 36,01 giây và dự đoán 0,034 giây, đỉnh job 158,02 MiB.

Checkpoint bổ sung khớp số liệu, ngưỡng và 101 điểm lưới Validation lịch sử của Trial 16. Checkpoint dành cho dự đoán CSV. Kết quả Official Test vẫn lấy từ lượt G10 đã lưu.

![Web Demo dự đoán 12 dòng minh họa từ Validation](../figures/web_demo/du-doan-truc-tiep.png)
