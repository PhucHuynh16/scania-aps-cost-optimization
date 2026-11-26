# Nghiệm thu bản nộp Scania APS

Ngày kiểm tra 26/11/2026. HEAD của nhánh main công khai và bản làm việc trước khi chỉnh sửa là `af4d7893d717c7b9c33d7253152f6fe475554f2a`, gồm 238 tệp. [Bản công bố](https://github.com/PhucHuynh16/scania-aps-cost-optimization)

## Kiểm tra kỹ thuật

| Hạng mục | Kết quả |
|---|---|
| Demo | `demo.py`, `--summary`, `--verify` và `--notes` đều thoát mã 0. Bộ xác minh kiểm tra 32/32 mã băm và các đẳng thức chi phí, ma trận nhầm lẫn và công suất. |
| Kết quả thực nghiệm | 20/20 bản ghi trial khớp bảng CSV. Kiểm tra lại chi phí, tính khả thi và 2.020 điểm lưới từ kết quả lưu. Trial 16 đạt 6.330 đơn vị trên Validation. Kết quả G10 đã lưu là 13.840 đơn vị trên Official Test. |
| Dữ liệu | 12/12 tệp chuẩn trùng kích thước và SHA-256 với bản sao lưu. Bảy tệp trong thư mục `recreate_antigravity_20261107_01` là bản sao trùng từng byte. `raw/ai4i2020.csv` thuộc đề tài trước. Đủ dữ liệu Scania APS cần cho bộ hồ sơ. |
| Môi trường | Hai môi trường ảo Python 3.11.9 mới cài được từ lockfile G3 và Phase 2. Kiểm tra tương thích thư viện đều thoát mã 0. |
| Kiểm thử | 104 kiểm thử toán học, dữ liệu tổng hợp và G10 an toàn, cộng 26 kiểm thử Phase 2 đều qua. Các ca gọi đường thực thi thật hoặc không thuộc tập lệnh kiểm tra đã chọn được bỏ qua. |
| Báo cáo và slide | Báo cáo có 8 trang nội dung và 1 trang phụ lục. Slide có 8 trang. PDF xuất từ Word và PowerPoint, đã kiểm tra từng trang. Liên kết GitHub mở được từ cả hai PDF. |
| Gói mã nguồn | CRC và từng tệp giải nén đã được đối chiếu. Bản giải nén chạy đủ bốn chế độ demo, kiểm tra manifest G10 và chạy 104 kiểm thử an toàn, tất cả thoát mã 0. |
| Phạm vi | Nghiệm thu đọc các kết quả đã lưu và dùng dữ liệu tổng hợp trong kiểm thử. CSV Official Test vẫn nằm trong ZIP gốc trong suốt quá trình nghiệm thu. |

## Điều kiện học thuật còn thiếu

- Nhánh main của bản công bố có hai commit, dưới mức năm mốc của đề bài. Tám mốc có bằng chứng được dẫn về kho phát triển. Cần xác nhận với giảng viên cách nộp kèm lịch sử hoặc dùng kho có lịch sử gốc. [Lịch sử phát triển](docs/DEVELOPMENT_HISTORY.md)
- Thực nghiệm dùng một seed. Checkpoint bổ sung phục vụ dự đoán cục bộ. Chạy lại lượt thực nghiệm lịch sử phụ thuộc vào hồ sơ phê duyệt, commit và môi trường tương ứng.

[Ma trận đối chiếu đề bài](docs/scania/FINAL_COMPLIANCE_MATRIX.md) · [Hướng dẫn chạy](HUONG_DAN_CHAY.md)

## Bổ sung ngày 27/11/2026

- Ngân sách 2/2 lượt fit đã dùng. Hai lần khởi động đầu dừng trước fit do lỗi đường dẫn Unicode của thư viện số. Các lần chạy sau dùng NativeSession và Windows Job Object. Official Test tiếp tục niêm phong.
- Random Forest mặc định đạt 28.190 tại ngưỡng 0,5 và 5.420 tại ngưỡng 0,1. Cả hai chính sách cùng một lần fit. Kết quả 5.420 thấp hơn 6.330 của Trial 16 trên Validation. Hai mô hình khác siêu tham số và `class_weight`. [Minh chứng](results/scania_aps/rf_supplement/default_rf_20261127_02/metrics.json)
- Checkpoint 218.969 byte, SHA-256 `641fb7aa354a51e1714050a054a3232bf7226dd15b7d5f70aaf3903d9b6dec38`. Refit khớp TP/FP/FN/TN = 195/383/5/11.417, chi phí 6.330, M/K = 578/1.200, ROC-AUC, Average Precision, ngưỡng và 101 điểm lưới. Artifact lịch sử chỉ lưu số liệu tổng hợp, nên chưa thể đối chiếu từng điểm xác suất lịch sử. [Minh chứng](results/scania_aps/rf_supplement/trial16_refit_20261127_02/metrics.json)
- 115 kiểm thử an toàn đã qua, gồm 104 ca nghiệp vụ cũ, 6 ca Web Demo và 5 ca Live Prediction. Chrome đã kiểm tra tải lô, ngưỡng, công suất phần trăm và số lượt, K = 0, đồng điểm, chi phí có nhãn, lô không nhãn, xuất CSV, lỗi CSV và giao diện hẹp. So sánh trực tiếp với `predict_proba()` và mảng G3 ở 12 dòng mẫu đạt. [Web Demo](WEB_DEMO.md)
