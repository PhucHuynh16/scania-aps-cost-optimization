# BÁO CÁO NGHIỆM THU KỸ THUẬT & HỌC THUẬT (`ACCEPTANCE_REPORT.md`)

- **Đề tài:** Tối ưu hóa chi phí bảo trì dự đoán hệ thống khí nén xe tải Scania APS (UCI #421)
- **Học phần:** Nhập môn Tối ưu hóa — Khoa Công nghệ Thông tin, Trường Đại học Văn Lang
- **Sinh viên thực hiện:** Huỳnh Phúc (MSSV: 2474802010314)
- **Repository chính thức:** [https://github.com/PhucHuynh16/scania-aps-cost-optimization](https://github.com/PhucHuynh16/scania-aps-cost-optimization)
- **Nguồn gốc phiên bản (Provenance):** Trích xuất từ nhánh nghiệm thu `antigravity/sc-final-deliverables` tại commit đã xác minh `93d2163e8a4bf31396eaa59b3098f3f6fdb4bf82` thuộc repository phát triển gốc [https://github.com/PhucHuynh16/Predictive-maintenance-cost-optimization](https://github.com/PhucHuynh16/Predictive-maintenance-cost-optimization)

---

## 1. CHÍNH SÁCH TỐI ƯU ĐÃ ĐÓNG BĂNG & KẾT QUẢ THỰC NGHIỆM

Toàn bộ kết quả thực nghiệm tại G3, G4, Phase 2 và Gate G10 được bảo toàn nguyên vẹn 100%, không huấn luyện lại mô hình, không chạy lại Optuna và không truy cập lại tập Official Test:

- **Mô hình & Siêu tham số đóng băng (Phase 2 Optuna Trial #16 [0-indexed], tức lượt thử thứ 17/20):**
  - `estimator`: `RandomForestClassifier`
  - `n_estimators = 50`, `max_depth = 10`, `min_samples_split = 10`, `max_features = 0.4268663927182804`
  - Tham số cố định: `class_weight = "balanced"`, `random_state = 42`, `n_jobs = 1`, `bootstrap = True`
  - Ngưỡng xác suất đóng băng: `tau* = 0.3232440937634324` (`a_i = I(p_i >= tau*)`)

| Giai đoạn & Lượt chạy gốc | Phân vùng ($N$) | $TP$ | $FP$ | $FN$ | $TN$ | Tổng chi phí ($10\cdot FP + 500\cdot FN$) | Lượt xe vào xưởng ($M \le K$) | So sánh tham chiếu |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **G4 B0 (Majority Dummy)** (`scania_g4_b2_real_002`) | Validation ($12.000$) | $0$ | $0$ | $200$ | $11.800$ | **$100.000$** | $0 / 1.200$ (`FEASIBLE`) | Mốc không kiểm tra ($0,00\%$) |
| **G4 B1 (Decision Stump, $\tau=0,0196$)** | Validation ($12.000$) | $160$ | $253$ | $40$ | $11.547$ | **$22.530$** | $413 / 1.200$ (`FEASIBLE`) | $-77,47\%$ so với B0 |
| **G4 B2 (Logistic Regression, $\tau=0,0196$)** | Validation ($12.000$) | $186$ | $323$ | $14$ | $11.477$ | **$10.230$** | $509 / 1.200$ (`FEASIBLE`) | Baseline tốt nhất G4 ($-89,77\%$) |
| **Phase 2 RF + Optuna TPE (Trial 16)** (`scania_phase2_rf_optuna_002`) | Validation ($12.000$) | $195$ | $383$ | $5$ | $11.417$ | **$6.330$** | $578 / 1.200$ (`FEASIBLE`) | **$-93,67\%$ so với B0; $-38,12\%$ so với B2** |
| **Gate G10 Official Test** (`scania_g10_official_test_003`) | Official Test ($16.000$) | $357$ | $484$ | $18$ | $15.141$ | **$13.840$** | $841 / 1.600$ (`FEASIBLE`) | **$-92,62\%$ so với B0 Test ($187.500$)** |

---

## 2. CÁC CHUẨN MỰC KỸ THUẬT & HỌC THUẬT ĐÃ XÁC MINH

1. **Phân tích độ nhạy ngưỡng quyết định trên lưới 101 điểm của Trial 16:**
   - Trích xuất trực tiếp từ `threshold_curve` của Trial 16 (`results/scania_aps/phase2/scania_phase2_rf_optuna_002/best_policy.json` và `durable_fits/trial_016_result.json`): tại $\tau = 0,04$ có $M = 1.314 > 1.200$ (`INFEASIBLE`), nhưng từ $\tau = 0,05$ ($M = 1.195 \le 1.200$, chi phí $11.480$) và $\tau = 0,09$ ($M = 955 \le 1.200$, chi phí $9.080$) chính sách **đã khả thi**. Trong đoạn $\tau \in [0,20; 0,32]$, chi phí duy trì ở vùng thấp $[6.350; 7.050]$; cực tiểu quan sát được đạt $6.330$ tại $\tau^* = 0,323244$; từ $\tau \ge 0,33$, chi phí tăng dốc ($7.290 \to 8.230 \to 8.670$).
2. **Đồng bộ miền tìm kiếm siêu tham số và cơ chế chọn ngưỡng:**
   - Khoảng tìm kiếm `max_features` là `$[0,20; 0,50]$` (cùng `n_estimators` $\in \{20,30,40,50,60\}$, `max_depth` $\in [4,12]$, `min_samples_split` $\in [2,10]$) khớp tuyệt đối với `configs/scania/phase2_optimization.json` và `src/scania/phase2_optimization.py`.
   - Bước tối ưu ngưỡng thực tế duyệt chính xác tập ứng viên xác suất duy nhất $T(p) = \{0, 1\} \cup \text{unique}(p_{\text{val}})$ không cần huấn luyện lại mô hình, còn lưới đều 101 điểm (`0,00..1,00`) chỉ dùng để vẽ đường cong đánh đổi. Nghiệm tìm được là nghiệm khả thi tốt nhất quan sát được trong 20 trials, không tuyên bố là tối ưu toàn cục.
3. **Trình diễn `scripts/demo.py` nạp động hoàn toàn từ artifacts & kiểm định chéo:**
   - Nạp trực tiếp từ `phase2_optimization.json`, `baseline_metrics.json`, `best_policy.json`, `run_summary.json`, `validation_guard_metrics.json`, `test_metrics.json` và `confusion_matrix_test.csv`.
   - Kiểm định toán học tự động (`TP + FP + FN + TN = N`, `Cost = 10*FP + 500*FN`, `M = TP + FP <= K`, khớp ma trận nhầm lẫn CSV và bộ tham số đóng băng) cùng kiểm tra mã băm toàn vẹn SHA-256 trên 32/32 artifacts; trả mã thoát `1` ngay khi thiếu hoặc hỏng dữ liệu.

---

## 3. KIỂM KÊ HIỆN TRẠNG DỮ LIỆU, PREPROCESSOR, CHECKPOINT & LOCKFILES

| Nhóm thành phần | Đường dẫn tương đối từ gốc dự án | Đưa vào Git Repository? | Mục đích & Phương án tái tạo khi thiếu |
|---|---|:---:|---|
| **1. Dữ liệu gốc UCI #421** | `data/raw/scania_aps/aps+failure+at+scania+trucks.zip` (`56.618.034 B`, SHA-256: `5504d040...`)<br>`data/raw/scania_aps/aps_failure_training_set.csv` (`44.669.194 B`, SHA-256: `bb484302...`)<br>`data/raw/scania_aps/aps_failure_description.txt` (`4.874 B`)<br>`data/raw/scania_aps/acquisition_manifest.json` (`1.218 B`) | **CÓ** (đính kèm trực tiếp) | Dữ liệu thô chính thức từ UCI #421 (~101,3 MB). Tệp `aps_failure_test_set.csv` giữ nguyên niêm phong trong `.zip`. Có thể kiểm chứng lại bằng `python scripts/run_scania_acquire.py`. |
| **2. Dữ liệu Train/Val đã tiền xử lý G3** | `data/processed/scania_aps/official_split.json` (`4.969.510 B`)<br>`data/processed/scania_aps/official_20261029_04/membership.npz` (`541.018 B`)<br>`.../tree_train.npy` (`65.280.128 B`), `tree_validation.npy` (`16.320.128 B`)<br>`.../lr_train.npy` (`65.280.128 B`), `lr_validation.npy` (`16.320.128 B`) | **CÓ** (đính kèm trực tiếp) | Ma trận đặc trưng `float64` đã tách phân tầng 80/20 (`48.000 / 12.000`) cho cây quyết định và Logistic Regression (~168,7 MB), khớp `stable_digest` G3. |
| **3. Đối tượng tiền xử lý đã fit (`joblib`)** | `data/processed/scania_aps/official_20261029_04/tree_preprocessor.joblib` (`3.624 B`)<br>`data/processed/scania_aps/official_20261029_04/lr_preprocessor.joblib` (`8.065 B`) | **CÓ** (đính kèm trực tiếp) | Lưu vector trung vị (`SimpleImputer`) và tham số chuẩn hóa (`StandardScaler`) học từ tập Train 48k, khớp mã băm trong `stable_manifest.json`. |
| **4. Trọng số mô hình đã huấn luyện (Model Checkpoints)** | *(Không có tệp `rf_model.joblib` / `*.pkl` cho Random Forest hay B1/B2)* | **KHÔNG TỒN TẠI** | Thiết kế Phase 2 & G10 chỉ lưu siêu tham số + ngưỡng JSON và dùng cơ chế `DETERMINISTIC_TRAIN_REFIT_EVALUATION` (~31 giây refit trên Train 48k với `seed=42`, khớp 100% Validation Guard). Nếu cần suy luận trực tiếp trên dữ liệu mới, cần chạy 1 bước refit từ `configs/scania/g10_evaluation.json` + dữ liệu G3 rồi `joblib.dump()`. |
| **5. Tệp khóa phiên bản thư viện (Lockfiles)** | `requirements.txt`<br>`configs/scania/g3_requirements.lock.txt` (15 gói khóa `==`)<br>`configs/scania/phase2_requirements.lock.txt` (33 gói khóa `==` trên Python `3.11.9`) | **CÓ** | Phục vụ tái lập chính xác môi trường Python `3.11.9` (`scikit-learn==1.9.1`, `optuna==5.0.0`, `numpy==2.4.6`, `scipy==1.17.1`). |
| **6. Artifacts kết quả thực nghiệm cốt lõi** | `results/scania_aps/{g3,g4,phase2,g10}/**` | **CÓ** | Toàn bộ JSON/CSV/checksums của G3 (`official_20261029_04`), G4 (`scania_g4_b2_real_001` & `002`), Phase 2 (`scania_phase2_rf_optuna_001` & `002`) và Gate G10 (`scania_g10_official_test_003`); đủ để chạy ngay **Chế độ A (Demo Read-Only)** không cần tải dữ liệu thô. |

---

## 4. KẾT QUẢ KIỂM THỬ THỰC TẾ

| Hạng mục kiểm tra | Lệnh thực thi | Mã thoát | Kết quả ghi nhận |
|---|---|:---:|---|
| Demo đầy đủ | `python scripts/demo.py` | `0` | In đầy đủ 5 phần + gợi ý thuyết trình 5–7 phút từ JSON/CSV gốc |
| Demo tóm tắt bảng | `python scripts/demo.py --summary` | `0` | In chính xác bảng G4, Phase 2 (kèm độ nhạy $\tau$) và Gate G10 |
| Demo xác minh SHA-256 | `python scripts/demo.py --verify` | `0` | `32/32 ARTIFACTS KHỚP MÃ BĂM SHA-256 VÀ KIỂM ĐỊNH TOÁN HỌC` |
| Demo dàn ý bảo vệ | `python scripts/demo.py --notes` | `0` | In dàn ý thuyết trình 4 chặng trong khung 5–7 phút |
| Kiểm chứng G10 | `python scripts/run_scania_g10.py verify` | `0` | `[PASS] All 9 artifacts verified against stable manifest.` |
| Kiểm chứng G4 & Phase 2 | `verify_run('.../scania_g4_b2_real_002')` & `verify_phase2_run('.../001', '.../002')` | `0` | `G4_AND_PHASE2_ARTIFACTS_VERIFIED_PASS` |
| Bộ kiểm thử đơn vị độc lập | `python -B -m pytest tests/scania -k "not (test_official_test_unsealed_fails_without_authorization or test_synthetic_end_to_end_pipeline or test_EX17_owner_authorization_record_schema_and_semantics or test_R01_locked_config_environment_and_protected_assets or test_cli_preflight_and_synthetic_invocation or test_exact_owner_authorization_binding_and_limit_enforcement or test_g3_hash_terminology_and_distinct_verification or test_exact_owner_comment_parsing_and_mocked_github_api or test_authorization_rejection_of_mismatched_config_and_commit or test_rejection_of_unsealed_test_scope)"` | `0` | **`303 passed`** (`10` ca loại trừ khi chạy ngoài kho Git `.git/` do gọi `git rev-parse HEAD` / `git status` trên lịch sử commit gốc; cả 10 ca này đều đã pass tại repository phát triển gốc) |

---

## 5. CÁC HẠN CHẾ NGHIÊN CỨU & CÔNG BỐ MINH BẠCH

1. **Thực nghiệm một hạt giống (`seed = 42`):** Chưa chạy lặp đa hạt giống (`mean ± std`) cho thuật toán ngẫu nhiên (Random Forest + Optuna TPE) do giới hạn ngân sách thực thi đã khóa (20 trials tuần tự).
2. **Khoảng cách baseline G4 vs Phase 2:** Hệ thống G4 gồm B0, B1, B2 ở ngưỡng cố định (`2 fits`), chưa tách riêng một baseline `RandomForestClassifier` cấu hình mặc định cùng cơ chế quét ngưỡng ứng viên.
3. **Không có tệp `.joblib` trọng số mô hình Random Forest:** Bản demo trình chiếu kết quả thực nghiệm đã lưu (`Mode A`), không thực hiện suy luận trực tiếp (`Mode C`) nếu chưa chạy lại bước refit trên tập Train G3.
4. **Chuỗi đường dẫn thư mục dữ liệu lúc chạy trong 7 tệp JSON lịch sử thuộc `results/`:** Tất cả tài liệu (`README.md`, `report/`, `slides/`, `docs/`, `scripts/demo.py`) hoàn toàn không chứa đường dẫn cá nhân hay khóa bí mật/token. Riêng 7 tệp JSON nhật ký thực nghiệm gốc trong `results/scania_aps/**` (`allowlist.json` và `task_config.json` của `scania_g4_b2_real_002`, `scania_phase2_rf_optuna_001`, `scania_phase2_rf_optuna_002`, `scania_g10_official_test_003`) lưu đường dẫn thư mục `data/processed/...` tại thời điểm worker thực thi; các tệp này **được giữ nguyên không chỉnh sửa** để bảo toàn khớp 100% mã băm SHA-256 gốc trong `checksums.json` và `stable_manifest.json` (32/32 artifacts verified).
5. **Lịch sử phát triển Git thực tế:** Kho phát triển gốc (`https://github.com/PhucHuynh16/Predictive-maintenance-cost-optimization`) được khởi tạo ngày `2026-10-21` (khảo sát bộ dữ liệu mẫu tuần đầu, chuyển chính thức sang Scania APS UCI #421 ngày `2026-10-25`) với hơn 45 commits thực chất qua các cổng kiểm định G1–G10 đến commit nghiệm thu `93d2163e8a4bf31396eaa59b3098f3f6fdb4bf82`.
