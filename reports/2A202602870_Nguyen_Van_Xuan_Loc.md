# Báo cáo cá nhân — Nguyễn Văn Xuân Lộc

**MSSV:** 2A202602870
**Phần phụ trách:** Benchmark, cấu hình chạy và phân tích số liệu.

> Bản nháp theo phân công. Thành viên bổ sung mô tả công việc mình trực tiếp thực hiện trước khi nộp.

## Cấu hình thực nghiệm

Drone: 75 frame từ năm video, YOLO11n, imgsz 640, confidence 0.10, 20 điều kiện, tổng 1.500 lượt suy luận, runtime ghi nhận 64 giây. KITTI: 20 ảnh, seed 42, YOLO26m imgsz 1280, baseline GT recall 0.846, runtime khoảng 22 giây.

## Kết quả

Trên drone, Spearman giữa health và consistency là 0.079. KITTI là một cấu hình khác và cần được ghi đúng model/độ phân giải khi trích số. Đối chiếu các CSV drone có trong repo và ghi riêng số KITTI từ slide tổng kết.

## Bằng chứng

Tham chiếu `results/summary.csv`, `results/results.csv`, `results/curves.png`, cấu hình trong `bench.py` và phần tóm tắt KITTI trong `slide.pdf`. Các file metadata/log chi tiết của lượt KITTI không có trong bản repo này.

## Phần việc cá nhân

**Tôi trực tiếp thực hiện:** _[bổ sung lần chạy, đối chiếu số liệu hoặc phân tích benchmark mà bạn đã làm]._

## Kết luận cá nhân

_[Bổ sung kết quả quan trọng nhất và giới hạn khi so sánh hai dataset/model khác nhau.]_
