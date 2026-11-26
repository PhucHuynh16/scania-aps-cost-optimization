# SLIDES THUYẾT TRÌNH BẢO VỆ BÀI TẬP LỚN: NHẬP MÔN TỐI ƯU HÓA (8 SLIDES)

**Đề tài:** Tối ưu hóa Chi phí Bảo trì Dự đoán Hệ thống Khí nén Xe tải nặng Scania APS (UCI #421)  
**Sinh viên thực hiện:** Huỳnh Phúc (MSSV: 2474802010314) — Khoa Công nghệ Thông tin, Trường Đại học Văn Lang  
**Kho mã nguồn:** [https://github.com/PhucHuynh16/scania-aps-cost-optimization](https://github.com/PhucHuynh16/scania-aps-cost-optimization)  
**Thời lượng trình bày & demo:** 5–7 phút

---

## SLIDE 1: TỔNG QUAN ĐỀ TÀI & KẾT QUẢ CHÍNH
- **Bài toán ứng dụng:** Hỗ trợ quyết định kiểm tra chuyên sâu hệ thống khí nén (APS) cho xe tải nặng Scania trên bộ dữ liệu công khai UCI #421 (60.000 mẫu phát triển, 16.000 mẫu Official Test, 170 đặc trưng số).
- **Đặc thù tối ưu hóa:**
  - Chi phí sai lầm bất đối xứng 50:1 theo chuẩn IDA 2016: bỏ sót lỗi APS ($FN$) phạt **500**, kiểm tra thừa ($FP$) phạt **10**.
  - Ràng buộc năng lực tiếp nhận của xưởng: $M = TP + FP \le \lfloor N/10 \rfloor$ ($1.200$ xe trên Validation; $1.600$ xe trên Test).
- **Kết quả chính đạt được:**
  - Baseline tốt nhất G4 (Logistic Regression, $\tau = 0,0196$): **10.230** đơn vị chi phí Validation ($M = 509$).
  - Tối ưu hóa Phase 2 (Random Forest + Optuna TPE, Trial 16, $\tau^* = 0,323244$): **6.330** đơn vị Validation ($M = 578$, **-38,12%** so với B2).
  - Đánh giá độc lập Gate G10 (Official Test 16.000 mẫu): **13.840** đơn vị (**-92,62%** so với B0 $187.500$, Recall **95,20%**, $M = 841 \le 1.600$).

---

## SLIDE 2: MÔ HÌNH HÓA TOÁN HỌC & KHÔNG GIAN BIẾN QUYẾT ĐỊNH
- **Ngữ nghĩa nhãn lớp chuẩn UCI #421:**
  - Lớp dương ($y = 1$, 1,67%): Xe hỏng thuộc hệ thống khí nén APS.
  - Lớp âm ($y = 0$, 98,33%): Xe vào xưởng do hỏng **các bộ phận khác ngoài APS** (không phải xe khỏe mạnh hoàn toàn).
- **Biến quyết định $x = (\theta, \tau) \in \Theta \times [0, 1]$:**
  - Siêu tham số Random Forest $\theta$: $n_{\text{estimators}} \in \{20..60\}$ (bước 10), $\text{max\_depth} \in [4, 12]$, $\text{min\_samples\_split} \in [2, 10]$, $\text{max\_features} \in [0,20; 0,50]$.
  - Ngưỡng quyết định $\tau \in [0, 1]$: hành động kiểm tra $a_i(\theta, \tau) = \mathbb{I}[P(y_i = 1 \mid x_i; \theta) \ge \tau]$.
- **Bài toán tối ưu hóa có ràng buộc:**
  - Hàm mục tiêu: $\min_{\theta, \tau} f(\theta, \tau) = 10 \cdot FP(\theta, \tau) + 500 \cdot FN(\theta, \tau)$ [đơn vị chi phí benchmark].
  - Ràng buộc công suất xưởng: $M(\theta, \tau) = TP(\theta, \tau) + FP(\theta, \tau) \le K = \lfloor N / 10 \rfloor$.

---

## SLIDE 3: RÀNG BUỘC CÔNG SUẤT XƯỞNG & SỰ ĐÁNH ĐỔI VẬN HÀNH
- **Giả định kịch bản năng lực xưởng ($10\%$ quy mô phân vùng):**
  - Validation ($N = 12.000$): $K_{\text{val}} = 1.200$ lượt xe; Official Test ($N = 16.000$): $K_{\text{test}} = 1.600$ lượt xe.
  - Chính sách có $M \le K$ là khả thi (`FEASIBLE`); nếu $M > K$ là bất khả thi (`INFEASIBLE`) và bị loại bỏ.
- **Hai cực đánh đổi đối lập:**
  - Hạ ngưỡng $\tau \to 0$ để bắt trọn lỗi APS ($FN \to 0$) $\Rightarrow$ cảnh báo giả $FP$ tăng vọt, vượt trần công suất $M > K$ (`INFEASIBLE`).
  - Tại $\tau=1$, Trial 16 không đưa xe nào vào kiểm tra, bỏ sót 200 ca và có chi phí bằng B0 (100.000 đơn vị).

---

## SLIDE 4: NGƯỠNG TỶ LỆ CHI PHÍ BAYES & THUẬT TOÁN TỐI ƯU HAI TẦNG
- **Ngưỡng Bayes lý thuyết khi không có ràng buộc công suất:**
  - Cực tiểu hóa kỳ vọng chi phí: $10(1 - P) \le 500 P \iff P \ge \tau^*_{\text{Bayes}} = 10 / 510 \approx 0,019608$.
  - Hạn chế khi áp dụng trực tiếp: giả định xác suất hiệu chuẩn hoàn hảo và bỏ qua trần công suất $M \le K$ (trên lưới ngưỡng của Trial 16, $\tau=0{,}02$ cần 2.313 lượt, vượt trần 1.200).
- **Giải thuật tối ưu hai tầng Phase 2 (ngân sách 20 trials tuần tự, `seed = 42`):**
  - **Tầng ngoài:** `Optuna TPESampler` đề xuất $\theta \in \Theta$, huấn luyện đúng 1 mô hình/trial trên Train 48.000 mẫu.
  - **Tầng trong:** Đánh giá vector hóa chính xác toàn bộ tập ứng viên xác suất duy nhất $T(p) = \{0, 1\} \cup \text{unique}(p_{\text{val}})$ để chọn $\tau^*$ khả thi có chi phí nhỏ nhất; đồng thời xuất lưới đều 101 điểm phục vụ vẽ đồ thị đánh đổi.

---

## SLIDE 5: GIAO THỨC DỮ LIỆU G3 & ĐƯỜNG CƠ SỞ G4 BASELINES
- **Phân vùng dữ liệu G3 chống rò rỉ (`stable_digest: efe781b7...`):**
  - **Train:** 48.000 mẫu (800 `pos`, 47.200 `neg`) — dùng độc quyền để `fit` bộ điền khuyết `median`, `StandardScaler` và mô hình.
  - **Validation:** 12.000 mẫu (200 `pos`, 11.800 `neg`), tách phân tầng `seed = 42`, rời nhau hoàn toàn với Train.
  - **Official Test:** 16.000 mẫu (375 `pos`, 15.625 `neg`) — giữ niêm phong trong suốt Phase 2, chỉ chấm 1 lần tại Gate G10.
- **Ba mô hình đường cơ sở G4:**
  - **B0:** Majority Dummy ($a_i = 0$, chi phí tham chiếu $100.000$ trên Validation).
  - **B1:** Decision Stump (`max_depth=1`) chấm tại $\tau = 0,5000$ và $\tau = 0,0196$.
  - **B2:** Logistic Regression (`L-BFGS, max_iter=2000`) chấm tại $\tau = 0,5000$ và $\tau = 0,0196$.

---

## SLIDE 6: KẾT QUẢ THỰC NGHIỆM 5 CHÍNH SÁCH ĐƯỜNG CƠ SỞ G4 (VALIDATION)

| Chính sách | Mô hình cơ sở | Ngưỡng $\tau$ | TP | FP | FN | Chi phí | Xe vào $M$ | Khả thi ($M \le 1200$) | Tiết kiệm vs B0 |
|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| P1 | B0: Majority Dummy | N/A | 0 | 0 | 200 | 100.000 | 0 | FEASIBLE | 0,00% |
| P2 | B1: Decision Stump | 0,5000 | 0 | 0 | 200 | 100.000 | 0 | FEASIBLE | 0,00% |
| P3 | B1: Decision Stump | 0,0196 | 160 | 253 | 40 | 22.530 | 413 | FEASIBLE | 77,47% |
| P4 | B2: Logistic Regression | 0,5000 | 129 | 48 | 71 | 35.980 | 177 | FEASIBLE | 64,02% |
| **P5 (Mốc G4)** | **B2: Logistic Regression** | **0,0196** | **186** | **323** | **14** | **10.230** | **509** | **FEASIBLE** | **89,77%** |

- **Nhận xét:** Hạ ngưỡng từ $0,5000$ xuống $\tau = 10/510 \approx 0,0196$ giúp Logistic Regression giảm mạnh $FN$ từ 71 xuống 14 ca, thiết lập mốc chuẩn G4 là **10.230 đơn vị** ($M = 509 \le 1.200$, thời gian chạy 6,06s, đỉnh RAM 201,90 MB).

- **Baseline Random Forest bổ sung:** Một fit Random Forest mặc định trên Train (class_weight=None). Chi phí Validation 28.190 tại τ=0,5, và 5.420 tại τ=0,1 (M=436). 5.420 là mức thấp nhất trên Validation, thấp hơn Trial 16 (6.330, M=578) 14,38%. Hai cấu hình khác siêu tham số và class_weight (None và balanced). Kết quả G10 tiếp tục dùng chính sách Trial 16.

---

## SLIDE 7: KẾT QUẢ TỐI ƯU HÓA PHASE 2 & ĐỘ NHẠY NGƯỠNG (TRIAL 16)
- **Nghiệm khả thi tốt nhất quan sát được trong 20 trials (`trial_number = 16`, lượt chạy thứ 17/20):**
  - Siêu tham số: `n_estimators = 50`, `max_depth = 10`, `min_samples_split = 10`, `max_features = 0,427`.
  - Ngưỡng chọn từ ứng viên xác suất chính xác: $\tau^* = 0,323244$.
  - Kết quả Validation: $TP = 195/200$ (Recall **97,50%**), $FP = 383$, $FN = 5$, tổng chi phí **6.330 đơn vị** (**-38,12%** so với B2), $M = 578 \le 1.200$ (thời gian chạy 543,06s, đỉnh RAM 159,82 MB).
- **Độ nhạy trên lưới 101 điểm của Trial 16:**
  - $\tau \le 0,04$: vượt công suất xưởng ($\tau = 0,04 \Rightarrow M = 1.314$, bất khả thi); từ $\tau = 0,05$ ($M = 1.195$) và $\tau = 0,09$ ($M = 955$) đã khả thi.
  - $\tau \in [0,20; 0,32]$: chi phí giữ ở mức thấp $[6.350; 7.050]$; từ $\tau \ge 0,33$ chi phí tăng dốc ($7.290 \to 8.230 \to 8.670$) do tăng $FN$.

---

## SLIDE 8: ĐÁNH GIÁ OFFICIAL TEST (G10), HẠN CHẾ & TÍNH TÁI LẬP
- **Đánh giá độc lập Official Test (Gate G10 — Run `scania_g10_official_test_003`, $N = 16.000$, $K = 1.600$):**
  - Khóa cấu hình Trial 16, huấn luyện lại tất định 1 lần trên Train 48k (khớp chính xác Validation Guard `6.330`), chấm Test 1 lần (0 tinh chỉnh):
  - Kết quả: $TP = 357/375$ (Recall **95,20%**), $FP = 484$, $FN = 18$, $TN = 15.141$, Precision **42,45%**, ROC-AUC **0,9861**.
  - Tổng chi phí: **13.840 đơn vị**, tiết kiệm **92,62%** so với B0 ($187.500$), lượt xe vào xưởng $M = 841 \le 1.600$ (`FEASIBLE`).
- **Hạn chế nghiên cứu & Minh bạch học thuật:**
  - Thực nghiệm dùng seed 42. Chi phí và trần 10% là giả định tĩnh. Điểm RF chưa hiệu chỉnh xác suất rủi ro.
  - Ở G10 Runs 001/002 bị dừng sớm, tệp CSV Test chỉ nạp vào RAM trước khi dừng tại chốt kiểm tra preprocessor, không có dự đoán hay tinh chỉnh. Toàn bộ 32 tệp kết quả G4, Phase 2, G10 được kiểm tra toàn vẹn bằng mã băm SHA-256.
  - Xem khai báo công cụ hỗ trợ và phần sinh viên tự kiểm chứng ở Phụ lục C của báo cáo.
  - **Web Demo:** Cài lockfile Phase 2, chạy `python app.py` và mở [localhost:8501](http://localhost:8501). Checkpoint Trial 16 khớp Validation và dùng để dự đoán CSV, thử ngưỡng/công suất và xuất kết quả.
