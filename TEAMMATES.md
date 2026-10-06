# Phân công công việc nhóm

Mỗi thành viên phụ trách một phần nội dung và hoàn thiện báo cáo cá nhân tương ứng trong `reports/`. Các báo cáo hiện là bản nháp theo phân công; mỗi người cần ghi trung thực phần việc mình trực tiếp thực hiện trước khi nộp.

## 1. Nguyễn Thị Thùy Dương — 2A202602905

**Phụ trách:** Bối cảnh bài toán camera và thiết kế dữ liệu/corruption.

- Mô tả use case camera RGB trên video drone và phần đối chiếu ADAS/KITTI.
- Trình bày cách lấy mẫu 75 frame từ 5 video drone và 20 ảnh KITTI, seed và ánh xạ nhãn.
- Giải thích các loại corruption, mức độ áp dụng và cách tạo dữ liệu suy giảm.
- Đối chiếu mô tả với mã nguồn, ghi chú dữ liệu cần có để chạy lại benchmark.

**Bằng chứng:** `bench.py` (`FAULTS`, `sample_frames()`, `sample_kitti()`), `results/curves.png`, `slide.pdf`.

**Báo cáo cá nhân:** `reports/2A202602905_Nguyen_Thi_Thuy_Duong.md`.

## 2. Lê Nguyễn Trâm Anh — 2A202602760

**Phụ trách:** Tìm hiểu paper và giải thích phương pháp.

- Tóm tắt hướng machine-centric image quality trong Li et al. (CVPR 2025).
- Giải thích cách tham khảo các phép đo consistency/accuracy từ MIQA (arXiv:2508.19850).
- Phân biệt đóng góp của các paper với heuristic health score do nhóm xây dựng; nêu rõ nhóm không chạy RA-MIQA.
- Làm rõ input, output, giả định và vai trò dự kiến của health score.

**Bằng chứng:** `README.md`, `bench.py`, cùng các liên kết paper trong README.

**Báo cáo cá nhân:** `reports/2A202602760_Le_Nguyen_Tram_Anh.md`.

## 3. Hồ Đăng Phúc — 2A202602796

**Phụ trách:** Health score và định nghĩa metric detector.

- Giải thích Laplacian variance, entropy, exposure và công thức health score nhân các thành phần đã chuẩn hóa.
- Giải thích box matching tại IoU 0.5, consistency F1 và ground-truth recall.
- Phân biệt metric đặc trưng ảnh, độ ổn định đầu ra detector và mức detector khớp nhãn.
- Đối chiếu công thức và mô tả metric với implementation và CSV.

**Bằng chứng:** `bench.py` (`health_metrics()`, `health_score()`, `iou()`, `match_f1()`, `gt_hit()`), `results/results.csv`, `results/summary.csv`.

**Báo cáo cá nhân:** `reports/2A202602796_Ho_Dang_Phuc.md`.

## 4. Nguyễn Văn Xuân Lộc — 2A202602870

**Phụ trách:** Cấu hình chạy benchmark và phân tích số liệu.

- Ghi lại detector, image size, confidence, IoU, seed, số mẫu, số điều kiện và runtime của các lượt chạy.
- Trình bày cấu hình drone và phép đối chiếu KITTI/ADAS, ghi rõ khác biệt về model và độ phân giải.
- Đối chiếu kết quả Spearman, baseline KITTI và các số liệu được đưa lên slide với nguồn tương ứng.
- Nêu rõ số liệu KITTI được trích trong slide/báo cáo tóm tắt; chỉ trích CSV/log khi các artifact đó có trong bản repo.

**Bằng chứng có trong repo:** `results/summary.csv`, `results/results.csv`, `results/curves.png`, `slide.pdf`, cấu hình chạy trong `bench.py`.

**Báo cáo cá nhân:** `reports/2A202602870_Nguyen_Van_Xuan_Loc.md`.

## 5. Nguyễn Văn Quốc Việt — 2A2026xxxxx

**Phụ trách:** Phân tích failure case, quyết định kỹ thuật và tích hợp nội dung cuối.

- Giải thích case Gaussian noise và phân biệt quan sát đo được với giả thuyết về nguyên nhân.
- Diễn giải trade-off của ngưỡng health score bằng failure recall và false-alarm rate.
- Đề xuất dữ liệu cần log, cách flag camera suy giảm và hướng fallback/thu thập dữ liệu cần đánh giá tiếp.
- Kiểm tra tính nhất quán giữa README, slide, kết quả benchmark và năm báo cáo cá nhân.

**Bằng chứng có trong repo:** `results/failure_case.png`, `results/summary.csv`, `results/results.csv`, `slide.pdf`, cùng các ngưỡng và phép tính trong `bench.py`.

**Báo cáo cá nhân:** `reports/2A2026xxxxx_Nguyen_Van_Quoc_Viet.md`.

> **Lưu ý MSSV:** MSSV của Quốc Việt hiện được cung cấp dưới dạng `2A2026xxxxx`. Cập nhật MSSV đầy đủ trong file này và tên file báo cáo khi có thông tin chính xác.

## Yêu cầu chung cho báo cáo cá nhân

Mỗi báo cáo cần nêu phần việc được phân công, giải thích phương pháp/phân tích, dẫn ít nhất một artifact của repo hoặc paper, ghi bằng chứng đã kiểm tra và kết luận cá nhân. Không viết phần việc dự kiến như thể đã được thực hiện hoặc đo đạc.
