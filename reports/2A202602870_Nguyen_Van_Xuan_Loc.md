# Báo cáo cá nhân — Nguyễn Văn Xuân Lộc

**MSSV:** 2A202602870
**Phần phụ trách:** Cấu hình chạy benchmark và phân tích số liệu.
**Chủ đề:** T1 — Camera degradation health score (drone, đối chiếu KITTI/ADAS).

## 1. Cấu hình thực nghiệm

Cấu hình lấy từ `bench.py` (hằng số ở đầu file và lệnh chạy trong README), đối chiếu với `results/results.csv` và `slide.pdf`.

| | Drone (chạy chính) | KITTI (đối chiếu ADAS) |
|---|---|---|
| Lệnh | `bench.py yolo11n.pt 640 drone` | `bench.py yolo26m.pt 1280 kitti` |
| Detector | YOLO11n (COCO) | YOLO26m (COCO) |
| imgsz | 640 | 1280 |
| Confidence / IoU | 0.10 / 0.5 | 0.10 / 0.5 |
| Seed | 0 | 42 |
| Mẫu | 5 video × 15 frame = 75 frame | 20 ảnh ngẫu nhiên từ `images/val` |
| Điều kiện | 20 (baseline + 6 lỗi × 3–4 mức) | 20 (cùng `FAULTS`) |
| Số lượt suy luận | 75 × 20 = 1.500 | 20 × 20 = 400 (suy ra, slide không ghi) |
| Runtime | 64 s (theo slide) | không có nguồn trong repo |

Hai cấu hình **khác cả model lẫn độ phân giải**, nên KITTI chỉ là phép đối chiếu định tính về hành vi của health score, không phải so sánh công bằng giữa "drone" và "ADAS". Với KITTI, `KITTI2COCO` ánh xạ nhãn gần đúng (van→car, tram→train, cyclist/sitting→person; lớp `misc` bị bỏ).

Điểm cần lưu ý khi chạy lại: số điều kiện trong `FAULTS`: gauss_blur 4 mức, motion_blur 3, noise 3, dark 3, overexpose 3, jpeg 3 = 19 mức + baseline = 20. Thư mục kết quả được đặt tên theo model/imgsz/dataset (`OUT`), nên chạy KITTI không ghi đè `results/` của drone.

## 2. Đối chiếu số liệu với nguồn

Tôi tính lại từ `results/results.csv` (1.500 dòng) và so với slide:

| Số liệu | Slide | Tính lại từ CSV | Kết quả |
|---|---|---|---|
| Số dòng / frame / điều kiện | 1.500 / 75 / 20 | 1.500 / 75 / 20 | Khớp |
| Spearman health–consistency (1.425 mẫu lỗi) | 0.079 | 0.079 | Khớp |
| Spearman lap_var / entropy / brightness | — | 0.100 / 0.204 / 0.159 | Thêm |
| Failure recall / false alarm tại τ=0.7 | 81.1% / 79.2% | 81.1% / 79.2% | Khớp |
| Failure case Backpack_0/5156, noise σ=50 | health 0.917, consistency 0, GT hit 0 | 0.917, 0, 0 | Khớp |
| Lap_var của failure case so với median baseline | 16.706 vs 1.988, ×8.4 | 16.706 vs 1.988 | Khớp |
| KITTI baseline GT recall 0.846 | có trên slide | **không kiểm chứng được** | Chỉ trích từ slide |
| Runtime 64 s | có trên slide | **không kiểm chứng được** | `run_meta.json` không có trong repo |

Spearman theo từng loại lỗi (health vs consistency, drone): dark 0.314, gauss_blur 0.230, jpeg 0.165, motion_blur 0.014, overexpose 0.003, **noise −0.161**.

Health trung bình theo mức noise (từ `results/summary.csv`): 0.771 → 0.780 → 0.779 cho σ = 10/25/50, **cao hơn baseline 0.724** trong khi consistency giảm 1.00 → 0.68 → 0.54 → 0.52. Đây là đúng hiện tượng noise làm Laplacian variance tăng (2.246 → 18.242) nên `h_sharp` bị kẹp ở 1.

## 3. Hạn chế của benchmark drone cần ghi kèm khi trích số

- GT recall baseline trên drone chỉ 0.093: Backpack, Laptop, MobilePhone, WaterBottle đều 0.000; chỉ Person1 đạt 0.467. 37/75 frame sạch không có box nào. Do đó GT recall gần như vô nghĩa trên drone, kết luận dựa chủ yếu vào consistency — vốn chỉ đo độ ổn định so với output của chính detector trên ảnh sạch, không đo độ đúng.
- Bảng "failure recall vs false alarm" gần như đường chéo (recall chỉ hơn false alarm 2–6 điểm % ở mọi τ), khớp với Spearman tổng 0.079.
- Chỉ một seed, 75 frame/5 video, 20 ảnh KITTI; chưa có khoảng tin cậy.

## 4. Giới hạn về bằng chứng KITTI

Slide ghi bằng chứng ở `results_yolo26m_1280_kitti/` (log, CSV, metadata), nhưng thư mục này **không có trong repo** (chỉ có `results/` của drone). Vì vậy trong báo cáo này số KITTI (baseline GT recall 0.846, YOLO26m imgsz 1280, 20 ảnh, seed 42) chỉ được trích từ slide và README, không phải từ CSV tôi tự kiểm tra. Các con số KITTI chi tiết hơn (Spearman theo lỗi, so sánh model) nằm trong báo cáo của bạn Phúc và cũng chưa kiểm chứng được từ repo này.

## Phần việc cá nhân

**Tôi trực tiếp thực hiện:**

- Ghi lại cấu hình chạy (detector, imgsz, conf, IoU, seed, số mẫu, điều kiện, lượt suy luận, runtime) và đối chiếu với `bench.py`.
- Tính lại Spearman tổng và theo từng loại lỗi, bảng gate (τ = 0.5–0.8) và failure case từ `results/results.csv`; so với slide, cả bốn nhóm số đều khớp.
- Phân biệt số liệu kiểm chứng được từ CSV với số chỉ có trên slide (KITTI, runtime 64 s), và ghi rõ giới hạn để không trích nhầm.

## Kết luận cá nhân

Các số trên slide về drone khớp hoàn toàn với `results/results.csv`; số KITTI và runtime chỉ dựa vào slide vì artifact tương ứng không có trong repo. Kết quả quan trọng nhất của benchmark: health score tổng gần như không tương quan với consistency (ρ = 0.079) và đi ngược chiều với noise (ρ = −0.161), vì Laplacian variance tăng theo noise. Khi so sánh hai dataset cần nhớ drone (YOLO11n, 640, detector gần như không thấy vật thể) và KITTI (YOLO26m, 1280, baseline recall 0.846) khác model, độ phân giải và chất lượng detector, nên chỉ so sánh xu hướng, không so sánh con số tuyệt đối. Việc cần làm tiếp: đưa log/CSV KITTI vào repo hoặc ghi rõ cách tái tạo, và chạy nhiều seed.
