# HƯỚNG DẪN CHẠY VÀ KIỂM TRA DỰ ÁN (`scania-aps-cost-optimization`)

- **Đề tài:** Tối ưu hóa chi phí bảo trì dự đoán hệ thống khí nén xe tải Scania APS (UCI #421)
- **Học phần:** Nhập môn Tối ưu hóa — Khoa Công nghệ Thông tin, Trường Đại học Văn Lang
- **Sinh viên thực hiện:** Huỳnh Phúc (MSSV: 2474802010314)
- **Repository chính thức:** [https://github.com/PhucHuynh16/scania-aps-cost-optimization](https://github.com/PhucHuynh16/scania-aps-cost-optimization)
- **Repository phát triển gốc (lịch sử Git):** [https://github.com/PhucHuynh16/Predictive-maintenance-cost-optimization](https://github.com/PhucHuynh16/Predictive-maintenance-cost-optimization) (commit nguồn: `93d2163e8a4bf31396eaa59b3098f3f6fdb4bf82`)

Tài liệu này phân biệt rõ **ba chế độ vận hành hoàn toàn khác nhau (A, B, C)** của đồ án để giảng viên/người kiểm tra chạy đúng mục đích mà không nhầm lẫn giữa trình diễn kết quả lưu trữ, tái lập huấn luyện và suy luận trực tiếp.

---

## 1. YÊU CẦU MÔI TRƯỜNG & CÀI ĐẶT THƯ VIỆN

- **Hệ điều hành kiểm nghiệm:** Windows 10/11 (x64)
- **Phiên bản Python:** **Python 3.11.x** (đã kiểm định thực tế trên Python `3.11.9`)

### Thiết lập môi trường ảo mới bằng PowerShell tại thư mục gốc repository:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
*(Nếu muốn cài đặt đúng phiên bản thư viện đã khóa lúc chạy thực nghiệm Phase 2, thay dòng cuối bằng `pip install -r configs/scania/phase2_requirements.lock.txt`).*

---

## 2. PHÂN BIỆT BA CHẾ ĐỘ VẬN HÀNH (A vs B vs C)

### CHẾ ĐỘ A — Chạy Demo Trình Diễn Kết Quả Đã Nghiệm Thu (Saved-Results Demo — Khuyến nghị khi chấm/bảo vệ)

- **Bản chất:** **CHỈ ĐỌC (READ-ONLY)** từ các tệp cấu hình và kết quả thực nghiệm JSON/CSV gốc đã lưu trong `results/scania_aps/` và `configs/scania/`.
- **Đặc điểm:**
  - **Không** cần tải dữ liệu thô UCI dung lượng lớn (`data/raw/`).
  - **Không** huấn luyện lại mô hình, **không** chạy lại Optuna, **không** đọc tệp Official Test CSV, và **không** thực hiện suy luận trực tiếp (live inference).
  - Tự động kiểm định chéo tính nhất quán toán học (`TP, FP, FN, TN`, `Cost = 10*FP + 500*FN`, `M = TP + FP <= K`, khớp tham số đóng băng Trial 16) và kiểm tra mã băm toàn vẹn SHA-256 trên toàn bộ **32/32 artifacts** thuộc G4, Phase 2 và Gate G10.
  - Nếu thiếu hoặc hỏng bất kỳ tệp kết quả bắt buộc nào, script báo lỗi rõ ràng ra `stderr` và thoát với mã lỗi khác `0` (`exit code = 1`).

#### Các lệnh PowerShell chạy Demo (thời lượng 5–7 phút bảo vệ):
```powershell
# 1. Chạy toàn bộ quy trình thuyết trình 5 phần + kiểm tra SHA-256 + gợi ý bảo vệ 5–7 phút
python scripts/demo.py

# 2. Chỉ in bảng tóm tắt số liệu đối chiếu G4, Phase 2 và Gate G10
python scripts/demo.py --summary

# 3. Chỉ kiểm tra tính nhất quán toán học & mã băm SHA-256 của 32 artifacts
python scripts/demo.py --verify

# 4. Chỉ in dàn ý thuyết trình 5–7 phút
python scripts/demo.py --notes
```

#### Các lệnh kiểm chứng toàn vẹn và kiểm thử đơn vị an toàn ngay tại thư mục gốc:
```powershell
# Kiểm tra mã băm SHA-256 của Gate G10 Official Test (9 artifacts)
python scripts/run_scania_g10.py verify

# Kiểm tra mã băm SHA-256 của G4 Baselines (11 artifacts) và Phase 2 (12 artifacts)
python -c "from src.scania.g4_artifacts import verify_run; from src.scania.phase2_executor import verify_phase2_run; verify_run('results/scania_aps/g4/scania_g4_b2_real_002'); assert verify_phase2_run('results/scania_aps/phase2/scania_phase2_rf_optuna_002'); print('G4 + Phase 2 VERIFIED PASS')"

# Chạy bộ kiểm thử đơn vị độc lập trong thư mục dự án (loại trừ 2 ca gọi `git rev-parse HEAD` khi không có thư mục `.git`)
python -m pytest tests/scania/test_cost_model.py tests/scania/test_constraints.py tests/scania/test_evaluation.py tests/scania/test_baselines.py tests/scania/test_pipeline.py tests/scania/test_g10_evaluation.py -k "not test_official_test_unsealed_fails_without_authorization and not test_synthetic_end_to_end_pipeline" -v
```
*(Lưu ý: Dùng `python -m pytest` để Python tự động thêm thư mục hiện tại vào `sys.path`. Trong kho Git đầy đủ có `.git/`, toàn bộ 134/134 ca kiểm thử kể cả `test_phase2_optimization.py` đều chạy `PASS`).*

---

### CHẾ ĐỘ B — Tái Lập Quy Trình Tiền Xử Lý, Huấn Luyện & Tối Ưu Hóa (Reproducing Training & Optimization)

- **Bản chất:** Chạy lại quy trình tải dữ liệu gốc UCI #421, tách Train/Validation G3 và kiểm thử đường ống tối ưu hóa.
- **Lưu ý quan trọng:** Repository công bố **không đính kèm tệp dữ liệu thô (`~101 MB`) hay mảng `.npy` trung gian (`~164 MB`)** theo quy định dung lượng và bản quyền dữ liệu.

#### Bước B.1 — Tải dữ liệu gốc UCI #421 và tái tạo phân vùng G3:
```powershell
# Tải tệp ZIP gốc từ UCI #421, kiểm tra SHA-256 và giải nén tập phát triển (giữ nguyên niêm phong Test)
python scripts/run_scania_acquire.py

# Tái tạo phân vùng Train (48.000) / Validation (12.000) theo official_split.json và fit bộ tiền xử lý
python scripts/run_scania_pipeline.py --run-id recreate_local_g3
```
*(Chi tiết đường dẫn và mã băm SHA-256 của từng tệp xem tại `data/README.md`).*

#### Bước B.2 — Chạy kiểm thử đường ống tối ưu hóa trên dữ liệu tổng hợp (không cần quyền GitHub):
```powershell
python -m scripts.run_scania_phase2 synthetic --run-id phase2_synthetic_demo --trials 3
python scripts/run_scania_g10.py synthetic
```

#### Bước B.3 — Về các lệnh chạy thực nghiệm thật (`execute`):
Các lệnh `python -m scripts.run_scania_phase2 execute` và `python scripts/run_scania_g10.py execute` được thiết kế khóa an toàn (`fail-closed`): yêu cầu chạy trong kho Git sạch, đối chiếu đúng commit SHA được cấp quyền và xác thực hồ sơ phê duyệt thực nghiệm đã khóa để ngăn ghi đè bằng chứng gốc hoặc truy cập lại tập Official Test ngoài ý muốn. Người chấm bài không cần chạy lại lệnh `execute` khi nghiệm thu đồ án.

---

### CHẾ ĐỘ C — Suy Luận Trực Tiếp Trên Dữ Liệu Mới (Performing Live Inference on New Data)

- **Hiện trạng thực tế:** Dự án **không lưu sẵn tệp trọng số mô hình Random Forest đã huấn luyện (`.joblib` hoặc `.pkl`)** trong kho mã nguồn trong repository.
  - Ở Phase 2 (`scania_phase2_rf_optuna_002`), hệ thống chỉ lưu cấu hình siêu tham số tốt nhất (`n_estimators=50, max_depth=10, min_samples_split=10, max_features=0.4268663927182804, class_weight='balanced', random_state=42`), ngưỡng quyết định `tau* = 0.3232440937634324` và các bảng chỉ số JSON/CSV.
  - Ở Gate G10 (`scania_g10_official_test_003`), hệ thống thực hiện 1 lần huấn luyện lại xác định trên tập Train 48.000 mẫu (`DETERMINISTIC_TRAIN_REFIT_EVALUATION`), kiểm tra khớp tuyệt đối kết quả Validation (`Cost = 6.330`, `M = 578`) rồi suy luận trên Official Test mà không ghi mô hình `.joblib` ra đĩa.
- **Cách khôi phục nếu muốn suy luận trên dữ liệu mới:**
  1. Tải dữ liệu gốc và chạy `scripts/run_scania_pipeline.py` để tạo `tree_train.npy`, `membership.npz` và `tree_preprocessor.joblib` (chứa trung vị 170 cột cảm biến học từ tập Train).
  2. Khởi tạo `RandomForestClassifier` với đúng bộ siêu tham số đóng băng trong `configs/scania/g10_evaluation.json`, gọi `.fit(X_train, y_train)` một lần (~31 giây trên 1 luồng CPU) và dùng `joblib.dump()` lưu mô hình nếu cần tái sử dụng.
  3. Biến đổi mẫu cảm biến 170 cột mới qua `tree_preprocessor.transform(X_new)`, lấy xác suất lớp dương `p = model.predict_proba(X_proc)[:, 1]` và ra quyết định kiểm tra theo quy tắc đóng băng `action = (p >= 0.3232440937634324)`.

---

## 3. TÀI LIỆU THAM CHIẾU NHANH TRONG GÓI NGHIỆM THU

- **Báo cáo tổng kết học phần:** `report/BAO_CAO_CUOI_KY_SCANIA_APS.pdf` (và `.docx`, `.md`)
- **Slide thuyết trình 8 trang:** `slides/SLIDES_THUYET_TRINH_SCANIA_APS.pdf` (và `.pptx`, `.md`)
- **Hai đồ thị tối ưu hóa thực nghiệm:**
  - `figures/optimization/optimization_convergence.png`
  - `figures/optimization/cost_vs_capacity_tradeoff.png`
- **Ma trận đối chiếu tuân thủ học thuật:** `docs/scania/FINAL_COMPLIANCE_MATRIX.md`
- **Báo cáo nghiệm thu & kiểm kê hiện trạng:** `ACCEPTANCE_REPORT.md` (đồng bộ tại `docs/scania/ACCEPTANCE_REPORT.md`)
