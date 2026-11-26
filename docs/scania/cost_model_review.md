# Mô Hình Chi Phí, Ràng Buộc Công Suất & Đặc Tả Kiểm Thử (`cost_model_review.md`)

- **Đề tài:** Tối ưu hóa chi phí bảo trì dự đoán hệ thống khí nén xe tải Scania APS (UCI #421)
- **Repository chính thức:** [https://github.com/PhucHuynh16/scania-aps-cost-optimization](https://github.com/PhucHuynh16/scania-aps-cost-optimization)

---

## 1. Ma trận chi phí benchmark IDA 2016 và biến đổi đại số

Với nhãn thực tế $y_i \in \{0, 1\}$ (`1 = pos` lỗi thuộc hệ thống APS, `0 = neg` lỗi ngoài APS) và quyết định kiểm tra $a_i \in \{0, 1\}$ (`1` = đề xuất kiểm tra chuyên sâu APS, `0` = không kiểm tra APS), ma trận chi phí sai lầm theo đặc tả [UCI #421](https://archive.ics.uci.edu/dataset/421/aps+failure+at+scania+trucks) là:

| Nhãn thực tế | Quyết định $a_i = 0$ | Quyết định $a_i = 1$ |
|---|---|---|
| $y_i = 0$ (`neg`) | $TN$: $0$ đơn vị | $FP$: **$10$** đơn vị |
| $y_i = 1$ (`pos`) | $FN$: **$500$** đơn vị | $TP$: $0$ đơn vị |

```text
C_APS = Σ [10 * (1 - y_i) * a_i + 500 * y_i * (1 - a_i)] = 10 * FP + 500 * FN
N = TP + FP + FN + TN;   M = TP + FP;   P = TP + FN
C_APS = 10 * M + 500 * P - 510 * TP
C_B0  = 500 * P
absolute_saving = C_B0 - C_APS = 510 * TP - 10 * M
```

Nếu xác suất dự báo $p_i = P(y_i = 1 \mid x_i)$ được hiệu chuẩn hoàn hảo và không có ràng buộc công suất xưởng, ngưỡng hòa vốn kỳ vọng Bayes là $\tau^*_{\text{Bayes}} = \frac{10}{10 + 500} = \frac{10}{510} \approx 0,019608$. Trong thực nghiệm G4 Baselines, hai ngưỡng cố định được khóa để đánh giá B1 và B2 là `PRIMARY = 0.5` và `SECONDARY = 10/510`.

## 2. Ví dụ kiểm tra tính tay trên bộ dữ liệu giả lập (Synthetic Oracles)

Xét lô dữ liệu giả lập `E1` gồm $N = 20$ quan sát (2 mẫu dương, 18 mẫu âm), trần công suất $K = \lfloor 20 / 10 \rfloor = 2$:

| Chính sách minh họa | TP | FP | FN | TN | $M$ | $C_{\text{APS}}$ | Tiết kiệm vs B0 | Tính khả thi ($M \le 2$) |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| $a_i = 0$ mọi hàng (B0) | 0 | 0 | 2 | 18 | 0 | 1.000 | 0 | Khả thi (`true`) |
| Chọn đúng 2 hàng dương | 2 | 0 | 0 | 18 | 2 | 0 | 1.000 | Khả thi (`true`) |
| Chọn 1 dương, 1 âm | 1 | 1 | 1 | 17 | 2 | 510 | 490 | Khả thi (`true`) |
| Chọn 2 hàng âm | 0 | 2 | 2 | 16 | 2 | 1.020 | -20 | Khả thi (`true`) |
| Chọn 2 dương và 1 âm | 2 | 1 | 0 | 17 | 3 | 10 | 990 | Bất khả thi (`false`, vượt 1 lượt) |

Chính sách có chi phí $10$ nhưng $M = 3 > 2$ bị loại khỏi bảng xếp hạng nghiệm khả thi vì vi phạm trần công suất xưởng.

## 3. Hợp đồng giao diện lập trình (API Contracts trong `src/scania/`)

| Hàm / Module | Đặc tả đầu vào, đầu ra và kiểm tra hợp lệ |
|---|---|
| `observed_aps_cost(y, actions)` (`cost_model.py`) | Nhận hai mảng 1 chiều nhị phân cùng độ dài $N > 0$; trả về thành phần chi phí `10*FP`, `500*FN` và tổng `total_cost`. Từ chối mảng rỗng, sai kích thước hoặc giá trị không nhị phân. |
| `capacity_report(actions)` (`constraints.py`) | Tính $N, M, K = \lfloor N / 10 \rfloor$, tỷ lệ bảo trì `maintenance_rate`, số lượt vượt `excess = max(0, M - K)` và cờ `feasible`. |
| `actions_from_probabilities(p, tau)` (`constraints.py`) | Kiểm tra $p \in [0, 1]$ hữu hạn và $\tau \in [0, 1]$; áp dụng chính xác phép so sánh $p_i \ge \tau$. |
| `evaluate_aps_policy(y, actions, scores=None)` (`evaluation.py`) | Tổng hợp ma trận nhầm lẫn, chi phí, công suất, mức tiết kiệm so với B0 và các chỉ số phân loại/xếp hạng (`Precision`, `Recall`, `F1`, `Average Precision`, `ROC-AUC`, `Brier`). |

## 4. Quy ước chỉ số đánh giá và xử lý trường hợp suy biến (Contract P08)

| Chỉ số | Công thức khi xác định | Giá trị & mã lý do khi suy biến |
|---|---|---|
| `total_cost` | $10 \cdot FP + 500 \cdot FN$ | Luôn xác định với đầu vào hợp lệ |
| `cost_per_observation` | $C / N$ | Từ chối $N = 0$ trước khi chia |
| `maintenance_rate` | $M / N$ | Ghi nhận kèm $M, K$, `excess`, `excess_rate` |
| `Precision` | $TP / M$ khi $M > 0$ | $M = 0 \Rightarrow \text{null}$ (`NO_PREDICTED_POSITIVES`) |
| `Recall` | $TP / P$ khi $P > 0$ | $P = 0 \Rightarrow \text{null}$ (`NO_POSITIVES`) |
| `F1` | $2 TP / (P + M)$ khi $P + M > 0$ | $P = M = 0 \Rightarrow \text{null}$ (`NO_TRUE_OR_PREDICTED_POSITIVES`) |
| `Average Precision` | `average_precision_score(y, p)` | Không có mô hình xác suất (B0) $\Rightarrow \text{null}$ (`NO_PROBABILITY_MODEL`) |
| `ROC-AUC` | `roc_auc_score(y, p)` | Chỉ có 1 lớp $\Rightarrow \text{null}$ (`SINGLE_CLASS`); B0 $\Rightarrow$ `NO_PROBABILITY_MODEL` |
| `Brier score` | $\text{mean}((p - y)^2)$ | B0 $\Rightarrow \text{null}$ (`NO_PROBABILITY_MODEL`) |
| `saving_pct` | $100 \cdot (C_{B0} - C) / C_{B0}$ | $C_{B0} = 0 \Rightarrow \text{null}$ (`ZERO_REFERENCE_COST`) |

## 5. Ma trận 16 nhóm kiểm thử đơn vị (`C01`–`R02`)

| Mã nhóm | Nội dung kiểm thử | Tiêu chí đạt (Oracle) |
|---|---|---|
| `C01`–`C06` | Hàm chi phí `cost_model.py` | Tính đúng trọng số $10/500$, bất biến với hoán vị, tính cộng được của chi phí, mức tiết kiệm âm/dương và bắt lỗi dữ liệu đầu vào sai miền. |
| `K01`–`K04` | Ràng buộc công suất & chọn ngưỡng `constraints.py` | Tính đúng $K = \lfloor N / 10 \rfloor$ tại biên, giữ nguyên nhóm đồng hạng (ties), trả về `NO_FEASIBLE_CANDIDATE` khi vô nghiệm và phá hòa tất định `(cost, M, -tau)`. |
| `M01`–`M02` | Chỉ số đánh giá `evaluation.py` | Xử lý đúng các mã `null/reason` khi $M=0$ hoặc B0 không có xác suất; tính đúng AP, ROC-AUC, Brier từ điểm xác suất liên tục. |
| `B01`–`B02` | Đường cơ sở `baselines.py` | Cây quyết định 1 tầng và Logistic Regression chỉ `fit` trên Train, đánh giá đúng tại hai ngưỡng khóa $\tau = 0,5$ và $\tau = 10/510$. |
| `R01`–`R02` | Toàn vẹn cấu hình & khả năng tái lập | Chặn thực thi khi sai lệch mã băm cấu hình/dữ liệu; hai lượt chạy cùng cấu hình và `seed = 42` sinh cùng `stable_digest`. |
