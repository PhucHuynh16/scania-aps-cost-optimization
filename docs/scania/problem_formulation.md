# Đặc Tả Toán Học Bài Toán Tối Ưu Hóa Chi Phí Bảo Trì Scania APS (`problem_formulation.md`)

- **Đề tài:** Tối ưu hóa chi phí bảo trì dự đoán hệ thống khí nén xe tải Scania APS (UCI #421)
- **Repository chính thức:** [https://github.com/PhucHuynh16/scania-aps-cost-optimization](https://github.com/PhucHuynh16/scania-aps-cost-optimization)

---

## 1. Mục tiêu và phạm vi bài toán

Xây dựng mô hình dự đoán sự cố hệ thống khí nén (Air Pressure System — APS) trên xe tải hạng nặng Scania và lựa chọn chính sách quyết định kiểm tra có tổng chi phí sai lầm benchmark thấp nhất dưới ràng buộc công suất xưởng tối đa $10\%$, so sánh khách quan giữa các mô hình đường cơ sở (`B0`, `B1`, `B2`) và phương pháp `RandomForestClassifier` kết hợp `Optuna TPE` trên cùng giao thức dữ liệu.

## 2. Dữ liệu, nhãn lớp và đơn vị quan sát

- **Tập dữ liệu chính:** [APS Failure at Scania Trucks — UCI #421](https://archive.ics.uci.edu/dataset/421/aps+failure+at+scania+trucks), DOI [10.24432/C51S51](https://doi.org/10.24432/C51S51).
- **Mã hóa nhãn lớp:** `pos = 1` (hư hỏng thuộc hệ thống APS), `neg = 0` (xe vào xưởng do hư hỏng ở bộ phận khác ngoài APS, không đồng nghĩa xe hoàn toàn khỏe mạnh).
- **Hành động quyết định:** `a = 1` là đề xuất đưa xe vào quy trình kiểm tra chuyên sâu APS; `a = 0` là không đề xuất kiểm tra chuyên sâu APS.
- **Đơn vị phân tích (Contract P01):** Mỗi dòng dữ liệu là một quan sát độc lập kèm nhãn lớp và $170$ đặc trưng số ẩn danh (`aa_000`..`ee_000`). Dữ liệu gốc không chứa mã định danh xe (vehicle ID) hay dấu thời gian (timestamp).
- **Phân vùng dữ liệu:** Tập phát triển gốc $60.000$ mẫu được tách phân tầng (`seed = 42`) thành **Train** ($48.000$ mẫu) và **Validation** ($12.000$ mẫu); tập **Official Test** ($16.000$ mẫu) được giữ niêm phong độc lập tới cổng đánh giá cuối cùng (Gate G10). Mọi bộ tiền xử lý chỉ được `fit` trên tập Train.

## 3. Biến quyết định và hàm mục tiêu

```text
x = (θ, τ),  θ ∈ Θ,  τ ∈ [0, 1]
p_i(θ) = P(y_i = 1 | x_i; θ)  (xác suất lớp dương dự báo từ mô hình fit trên Train)
a_i(θ, τ) = I[p_i(θ) >= τ]
FP(θ, τ) = Σ (1 - y_i) * a_i(θ, τ)
FN(θ, τ) = Σ y_i * (1 - a_i(θ, τ))
min C_APS(θ, τ) = 10 * FP(θ, τ) + 500 * FN(θ, τ)
```

- Đơn vị của hàm mục tiêu là **đơn vị chi phí benchmark quy ước** (`benchmark_cost_units`), trong đó $TP$ và $TN$ có chi phí sai lầm bằng $0$.
- Đặt $P = \sum y_i$ là tổng số ca lỗi APS thực tế và $M = \sum a_i = TP + FP$ là tổng số lượt xe đưa vào kiểm tra APS:
  $$C_{\text{APS}} = 10 M + 500 P - 510 \cdot TP, \qquad C_{B0} = 500 P$$

## 4. Ràng buộc công suất xưởng và quy ước ngưỡng (Contract P02)

- Trần công suất xưởng trên phân vùng $N$ quan sát: $K = \lfloor N / 10 \rfloor$, yêu cầu $M(\theta, \tau) \le K$ ($K_{\text{val}} = 1.200$ trên Validation; $K_{\text{test}} = 1.600$ trên Official Test).

| Hạng mục hợp đồng P02 | Quy tắc xử lý chuẩn hóa |
|---|---|
| Miền & phép so sánh | $\tau \in [0, 1]$, phép so sánh không ngặt `>=`, $p_i \in [0, 1]$ hữu hạn; không làm tròn hoặc cắt ngưỡng |
| Xử lý đồng hạng (Ties) | Các quan sát có cùng xác suất $p_i$ được giữ nguyên nhóm; không tách ngẫu nhiên hoặc cắt `top-k` để ép vừa trần $K$ |
| Hai đầu mút | $\tau = 0$ chọn toàn bộ quan sát (kể cả $p_i = 0$); $\tau = 1$ chỉ chọn các quan sát có $p_i = 1$; `B0` là chính sách $a_i = 0$ riêng biệt |
| Vi phạm công suất | `excess = max(0, M - K)`, `excess_rate = excess / N`; khả thi khi và chỉ khi `excess == 0` |
| Tập ngưỡng ứng viên | $T(p) = \{0.0, 1.0\} \cup \text{unique}(p_{\text{val}})$, sắp xếp tăng dần và loại trùng chính xác |

## 5. Quy tắc lựa chọn nghiệm khả thi và phá hòa tất định

1. Lọc tất cả các ứng viên hợp lệ và thỏa mãn ràng buộc khả thi ($M \le K$).
2. Chọn ứng viên có chi phí quan sát trên tập Validation `total_cost` nhỏ nhất.
3. Trong trường hợp đồng chi phí tối thiểu (chênh lệch tuyệt đối $\le 10^{-9}$): ưu tiên ứng viên sử dụng ít công suất $M$ hơn, sau đó ưu tiên ngưỡng $\tau$ lớn hơn.
4. Nếu một cấu hình không có bất kỳ ngưỡng nào khả thi trên $[0, 1]$, ghi nhận trạng thái `NO_FEASIBLE_CANDIDATE` (không tự ý thay thế bằng `B0`).

## 6. Hệ thống mô hình đường cơ sở (Gate G4) và phương pháp chính (Phase 2)

| Phương pháp | Cấu hình & Quy tắc đánh giá |
|---|---|
| **B0 — Majority Dummy** | Luôn dự đoán $a_i = 0$ (không có mô hình xác suất, chi phí tham chiếu $500 P$) |
| **B1 — Decision Stump** | `DecisionTreeClassifier(max_depth=1, random_state=42)` trên dữ liệu điền khuyết trung vị; đánh giá tại $\tau = 0,5$ và $\tau = 10/510$ |
| **B2 — Logistic Regression** | `LogisticRegression(C=1.0, solver="lbfgs", max_iter=2000, random_state=42)` sau điền khuyết trung vị và `StandardScaler`; đánh giá tại $\tau = 0,5$ và $\tau = 10/510$ |
| **Phase 2 — Random Forest + Optuna TPE** | `RandomForestClassifier` (`class_weight="balanced"`, `random_state=42`, `n_jobs=1`) kết hợp `TPESampler(seed=42)` trong 20 trials tuần tự và tối ưu ngưỡng chính xác trên $T(p)$ |
