# Báo cáo cá nhân — Nguyễn Thị Thùy Dương

**MSSV:** 2A202602905
**Phần phụ trách:** Bài toán camera, dữ liệu benchmark và mô phỏng suy giảm.

> Bản nháp theo phân công. Thành viên bổ sung mô tả công việc mình trực tiếp thực hiện trước khi nộp.

## Bài toán và dữ liệu

Project xem camera RGB là một hệ đo có thể bị suy giảm bởi blur, motion blur, noise, thiếu sáng, cháy sáng và nén JPEG. Benchmark drone lấy 75 frame có annotation từ năm video, với seed 0. KITTI cung cấp kiểm chứng chéo trên 20 ảnh val, seed 42.

## Thiết kế corruption

`bench.py` áp dụng từng loại lỗi lên frame sạch, lần lượt ở nhiều mức cường độ. Cách làm này giúp so sánh phản ứng của health score và detector theo từng lỗi, đồng thời giữ cùng frame gốc làm tham chiếu.

## Bằng chứng và kết quả

Tham chiếu `bench.py`, `results/curves.png`, `results/failure_case.png` và cấu hình/dữ liệu mô tả trong `slide.pdf`. Khi chạy lại benchmark, chuẩn bị dataset theo các đường dẫn ở README.

## Phần việc cá nhân

**Tôi trực tiếp thực hiện:** _[bổ sung phần việc đã làm, ví dụ kiểm tra sampling, xác nhận đường dẫn dữ liệu hoặc phân tích corruption]._

## Kết luận cá nhân

_[Bổ sung kết luận về việc chọn dữ liệu/corruption và điều cần kiểm tra khi đưa benchmark sang camera khác.]_
