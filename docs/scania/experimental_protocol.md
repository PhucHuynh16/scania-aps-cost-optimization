# Giao Thức Thực Nghiệm & Chống Rò Rỉ Dữ Liệu Scania APS (`experimental_protocol.md`)

- **Đề tài:** Tối ưu hóa chi phí bảo trì dự đoán hệ thống khí nén xe tải Scania APS (UCI #421)
- **Repository chính thức:** [https://github.com/PhucHuynh16/scania-aps-cost-optimization](https://github.com/PhucHuynh16/scania-aps-cost-optimization)

---

## 1. Ranh giới phân vùng dữ liệu và nguyên tắc chống rò rỉ (No Data Leakage)

| Phân vùng dữ liệu | Mục đích sử dụng được phép | Hành vi bị nghiêm cấm |
|---|---|---|
| **Official Train gốc ($60.000$ mẫu trước khi tách)** | Kiểm toán tính toàn vẹn tệp, schema 170 cột, định dạng nhãn `pos`/`neg`, tỷ lệ khuyết thiếu `na` và kiểm tra trùng lặp (Giai đoạn G2). | Không `fit` bộ điền khuyết, bộ chuẩn hóa hay mô hình phân loại trên toàn bộ $60.000$ mẫu trước khi tách Validation. |
| **Train ($48.000$ mẫu sau khi tách — 80%)** | Dùng độc quyền để `fit` bộ điền khuyết `SimpleImputer(strategy="median")`, bộ chuẩn hóa `StandardScaler` và huấn luyện các mô hình học máy. | Không gộp Validation hoặc Official Test vào quá trình huấn luyện. |
| **Validation ($12.000$ mẫu sau khi tách — 20%)** | Chỉ áp dụng `transform` từ bộ tiền xử lý đã học trên Train; dùng để đánh giá G4 Baselines và lựa chọn cặp $(\theta^*, \tau^*)$ trong 20 trials của Phase 2. | Không `fit` lại imputer/scaler trên Validation; không sửa nhãn hoặc lọc dòng. |
| **Official Test ($16.000$ mẫu độc lập)** | Giữ niêm phong trong suốt G2, G3, G4 và Phase 2; chỉ mở tại Gate G10 để biến đổi bằng `tree_preprocessor.joblib` của Train và chấm điểm đúng 1 lần với chính sách $(\theta^*, \tau^*)$ đã đóng băng. | Tuyệt đối không dùng Official Test để khảo sát EDA, chọn đặc trưng, tinh chỉnh siêu tham số hay điều chỉnh ngưỡng quyết định $\tau$. |

## 2. Hợp đồng dữ liệu nguồn và kiểm toán G2 (Contracts P01 & P03)

- **Nguồn dữ liệu chính thức:** [UCI Machine Learning Repository #421](https://archive.ics.uci.edu/dataset/421/aps+failure+at+scania+trucks), DOI [10.24432/C51S51](https://doi.org/10.24432/C51S51).
- **Quy tắc kiểm tra tệp nguồn:**
  - Tệp nén gốc `aps+failure+at+scania+trucks.zip` (`56.618.034` bytes, SHA-256: `5504d0402f54faaf97ac0ca085a621645763f5cfea2eb29c592b057d43d4db89`).
  - Tệp phát triển `aps_failure_training_set.csv` (`44.669.194` bytes, SHA-256: `bb484302e3a3a1c8ef5e1f0129c4dc7cbd58f350867f95b575461ca21ab6b9da`): bỏ qua 20 dòng lời dẫn đầu tệp, đọc dòng tiêu đề thứ 21 gồm cột `class` và đúng $170$ cột đặc trưng số từ `aa_000` đến `ee_000`.
  - Nhãn mục tiêu chỉ chấp nhận hai giá trị hợp lệ `pos -> 1` và `neg -> 0`; các giá trị khuyết thiếu trong 170 cột đặc trưng được biểu diễn bằng chuỗi `na` và chuyển thành `NaN`.
  - Định danh dòng nguồn (Source-row ID): bộ ba `(official_train_sha256, "train", data_row_number)` đánh số từ $1$ đến $60.000$ theo đúng thứ tự gốc, không đưa vào ma trận đặc trưng $X$.

## 3. Hợp đồng phân tách Train/Validation G3 (Contract P04)

- Thực hiện đúng một lệnh `train_test_split` trên chỉ số vị trí $0..59.999$ của tập phát triển với `test_size = 0.20`, `shuffle = True`, `stratify = y`, `random_state = 42`.
- Kết quả thu được:
  - **Train:** $48.000$ mẫu ($800$ `pos` — $1,67\%$; $47.200$ `neg` — $98,33\%$).
  - **Validation:** $12.000$ mẫu ($200$ `pos` — $1,67\%$; $11.800$ `neg` — $98,33\%$).
- Hai tập hoàn toàn rời nhau ($\text{Train} \cap \text{Validation} = \emptyset$) và hợp lại phủ kín đúng $60.000$ mẫu gốc. Mã băm đối tượng ổn định (`stable_digest`) của phân vùng G3 chính thức (`official_20261029_04`) là `efe781b7e564073a2a764e70a41cfe5c3e8975d33cc38b0fa297ef09f51767bb`.

## 4. Hợp đồng tiền xử lý chỉ học trên Train (Contract P05)

1. **Nhánh mô hình cây (`tree_preprocessor.joblib`):**
   - Kiểm tra hợp đồng 170 cột số theo đúng thứ tự (`FeatureContract`).
   - Điền khuyết bằng `SimpleImputer(strategy="median", keep_empty_features=True, add_indicator=False, copy=True)` chỉ `fit` trên $48.000$ mẫu Train; xuất ma trận `float64` `tree_train.npy` ($48.000 \times 170$) và `tree_validation.npy` ($12.000 \times 170$).
2. **Nhánh hồi quy tuyến tính (`lr_preprocessor.joblib`):**
   - Sau bước điền khuyết trung vị trên Train, nối tiếp `StandardScaler()` chỉ `fit` trên $48.000$ mẫu Train (với cột hằng số có độ lệch chuẩn $\sigma = 0$ như `cd_000`, `StandardScaler` của `scikit-learn` giữ hệ số chia bằng $1$ để không sinh `NaN`); xuất `lr_train.npy` và `lr_validation.npy`.

## 5. Ma trận 10 nhóm kiểm thử đường ống dữ liệu (`G301`–`G310`)

| Mã kiểm thử | Nội dung kiểm chứng trong `tests/scania/test_pipeline.py` |
|---|---|
| `G301` | Kiểm tra bộ phân tích cú pháp CSV (header, 170 cột số, nhãn `pos`/`neg`, token `na` và từ chối định dạng sai). |
| `G302` | Chặn thực thi (`Blocked`) khi mã băm tệp nguồn, cấu hình hoặc phiên bản thư viện không khớp. |
| `G303` | Phát hiện chính xác các dòng trùng lặp vector đặc trưng $X$ kèm mặt nạ khuyết thiếu. |
| `G304` | Kiểm chứng tính phân tầng 80/20, tính rời nhau và tính tất định của `official_split` với `seed = 42`. |
| `G305` | Xác minh định danh dòng nguồn (Source-row ID) và mã băm thứ tự ID (`ordered_ids_sha256`). |
| `G306` | Kiểm thử sentinel chứng minh `SimpleImputer` và `StandardScaler` chỉ học thống kê từ tập Train, không bị ảnh hưởng bởi giá trị trên tập Validation. |
| `G307` | Xử lý an toàn giá trị khuyết mới trên Validation và từ chối giá trị vô cực (`Inf`) hoặc chuỗi bất hợp lệ. |
| `G308` | Chốt chặn bảo vệ chứng minh quy trình G3 hoàn toàn không mở hoặc đọc tệp `aps_failure_test_set.csv`. |
| `G309` | Cơ chế ghi độc quyền theo `run_id`, bảo toàn nhật ký chẩn đoán khi xảy ra lỗi. |
| `G310` | Hai lượt chạy tái lập độc lập với cùng cấu hình và dữ liệu sinh ra cùng mã băm `stable_digest`. |
