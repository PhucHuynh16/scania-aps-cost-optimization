# Hướng dẫn chạy Scania APS

Dùng Python 3.11.9 tại thư mục gốc của repository hoặc thư mục vừa giải nén. [Repository nộp bài](https://github.com/PhucHuynh16/scania-aps-cost-optimization)

## Web Demo

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r configs/scania/phase2_requirements.lock.txt
.\.venv\Scripts\python.exe app.py
```

Mở [localhost:8501](http://localhost:8501). Chọn **Dự đoán CSV**, sau đó **Chạy CSV mẫu Validation**. Với môi trường đã kích hoạt, chạy `python app.py`. Dừng bằng Ctrl+C. Nếu cổng 8501 đang bận, thêm `--port 8502` và mở [localhost:8502](http://localhost:8502). [Hướng dẫn và định dạng CSV](WEB_DEMO.md)

## Demo trên terminal

Demo đọc cấu hình và kết quả CSV/JSON đã lưu bằng thư viện chuẩn Python. Các lệnh dưới đây dùng được trên bản ZIP, kể cả khi thư mục không có lịch sử Git.

```powershell
python scripts/demo.py
python scripts/demo.py --verify
python scripts/demo.py --summary
python scripts/demo.py --notes
```

Lệnh mặc định trình bày mô hình hóa, baseline, hội tụ, đánh đổi chi phí–công suất và kết quả Official Test đã lưu. `--verify` kiểm tra công thức và 32 mã băm SHA-256. `--summary` in bảng số liệu, còn `--notes` in dàn ý bảo vệ 5–7 phút. Lệnh thoát với mã khác 0 nếu phát hiện lỗi kiểm chứng.

## Môi trường kiểm thử

Windows x64 và Python 3.11.9 là môi trường của thực nghiệm. Dùng lockfile Phase 2 cho kiểm thử và các bộ xác minh bên dưới. Để tái tạo riêng tiền xử lý G3, tạo môi trường khác và cài `configs/scania/g3_requirements.lock.txt`. `requirements.txt` là danh sách thư viện cho phát triển và xuất tài liệu.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r configs/scania/phase2_requirements.lock.txt
.\.venv\Scripts\python.exe -m pip check
```

Kiểm tra an toàn bằng dữ liệu tổng hợp, các hợp đồng toán học và kết quả đã lưu. Các lệnh sau dùng được trên bản ZIP.

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/scania/test_cost_model.py tests/scania/test_constraints.py tests/scania/test_evaluation.py tests/scania/test_baselines.py tests/scania/test_pipeline.py tests/scania/test_g10_evaluation.py -k "not test_official_test_unsealed_fails_without_authorization and not test_synthetic_end_to_end_pipeline"
.\.venv\Scripts\python.exe scripts/run_scania_g10.py verify
```

## Dữ liệu và phạm vi tái lập

Kho đã kèm 12 tệp dữ liệu UCI #421 và dữ liệu tiền xử lý G3. CSV Official Test nằm trong ZIP gốc của UCI. Chi tiết nguồn, mã băm và lệnh tùy chọn để tái tạo Train/Validation có trong tài liệu dữ liệu. Lệnh tái tạo G3 cần chạy trong bản clone có Git. [Dữ liệu Scania APS](data/README.md)

Các lệnh thực nghiệm thật có cơ chế kiểm tra hồ sơ phê duyệt gắn với commit và đường dẫn dữ liệu. Bản công bố hỗ trợ kiểm tra kết quả đã lưu, kiểu dữ liệu và giao thức bằng demo và kiểm thử; thực thi lại các lượt lịch sử cần môi trường và điều kiện phê duyệt tương ứng. Checkpoint bổ sung cho Live Prediction đã đi kèm. Máy chủ kiểm tra SHA-256 của checkpoint và preprocessor trước khi dự đoán.

[Báo cáo](report/BAO_CAO_CUOI_KY_SCANIA_APS.pdf) · [Slide](slides/SLIDES_THUYET_TRINH_SCANIA_APS.pdf) · [Lịch sử phát triển](docs/DEVELOPMENT_HISTORY.md)
