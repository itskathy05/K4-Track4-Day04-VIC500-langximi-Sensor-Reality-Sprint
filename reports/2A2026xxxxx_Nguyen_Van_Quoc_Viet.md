# Báo cáo cá nhân — Nguyễn Văn Quốc Việt

**MSSV:** 2A2026xxxxx _(placeholder, cần cập nhật mã đầy đủ)_
**Phần phụ trách:** Failure case, engineering decision và tích hợp báo cáo.

> Bản nháp theo phân công. Thành viên bổ sung mô tả công việc mình trực tiếp thực hiện trước khi nộp.

## Failure case

Ở Backpack_0, frame 5156, Gaussian noise σ=50 cho health 0.917, consistency 0.000 và GT hit 0.000. Laplacian variance của frame là 16.706 so với median baseline 1.988, khoảng 8,4 lần. Dữ liệu ủng hộ nhận xét rằng thành phần sharpness bị noise đánh lừa; cơ chế tần số cao là giải thích của nhóm, chưa phải kiểm định nhân quả.

## Trade-off và quyết định

Theo benchmark được tóm tắt trong `slide.pdf`, tại ngưỡng tau=0.7, failure recall là 81.1% và false-alarm rate là 79.2%. Do false alarm cao, score hiện tại phù hợp cho monitoring, chưa đủ để tự động điều khiển xe/drone. Đề xuất bổ sung noise estimate, log health theo kênh, consistency, latency, timestamp và detector version. Fallback nhiều frame liên tiếp là phương án cần đánh giá thêm, chưa phải kết quả đã kiểm chứng.

## Phần việc cá nhân

**Tôi trực tiếp thực hiện:** _[bổ sung phần phân tích failure, engineering decision hoặc tích hợp mà bạn đã làm]._

## Kết luận cá nhân

_[Bổ sung quyết định triển khai đề xuất và phép đo cần có trước khi áp dụng.]_
