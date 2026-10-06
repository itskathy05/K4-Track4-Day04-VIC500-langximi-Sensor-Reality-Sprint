# Báo cáo cá nhân — Hồ Đăng Phúc

**MSSV:** 2A202602796
**Phần phụ trách:** Health score và metric detector.

> Bản nháp theo phân công. Thành viên bổ sung mô tả công việc mình trực tiếp thực hiện trước khi nộp.

## Định nghĩa metric

Health heuristic là tích của ba thành phần sharpness, entropy và exposure được chuẩn hoá theo median baseline. Consistency F1 so khớp box cùng class giữa prediction trên frame lỗi và frame sạch tại IoU ≥ 0.5. Metric này đo độ ổn định output. GT recall đo tỷ lệ ground-truth box được detector khớp đúng class tại IoU ≥ 0.5.

## Hiện thực trong code

Đối chiếu các hàm `health_metrics()`, `health_score()`, `iou()`, `match_f1()` và `gt_hit()` trong `bench.py`. Mô tả rõ Laplacian variance có thể tăng vì noise, nên không diễn giải nó như phép đo sharpness hoàn hảo.

## Bằng chứng và kết quả

Dùng `results/summary.csv` và `results/results.csv` để minh hoạ health/consistency/GT recall theo điều kiện. Nêu rõ consistency không chứng minh detector đúng.

## Phần việc cá nhân

**Tôi trực tiếp thực hiện:** _[bổ sung phần bạn đã làm liên quan đến công thức, code hoặc kiểm tra metric]._

## Kết luận cá nhân

_[Bổ sung metric nào hữu ích, metric nào dễ sai và vì sao cần hiệu chuẩn theo loại lỗi.]_
