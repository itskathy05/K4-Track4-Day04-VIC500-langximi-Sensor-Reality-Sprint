# Báo cáo cá nhân — Hồ Đăng Phúc

**MSSV:** 2A202602796
**Phần phụ trách:** Health score và metric detector.
**Chủ đề:** T1 — Camera degradation health score (drone, đối chứng thêm trên KITTI/ADAS).

## Định nghĩa metric

- **Health score** = `h_sharp · h_entropy · h_exposure` (dạng nhân, mượn ý tưởng GSHI: một kênh xấu kéo cả điểm xuống). Mỗi thành phần ∈ [0,1], chuẩn hoá theo median của baseline:
  - `h_sharp = log(1+LapVar) / log(1+LapVar_ref)` (Laplacian variance),
  - `h_entropy = entropy / entropy_ref` (Shannon entropy ảnh xám),
  - `h_exposure = (1 − |brightness − brightness_ref|/128) · (1 − tỷ lệ pixel cháy/tối)`.
- **Consistency F1** (theo định nghĩa "consistency" của MIQA, arXiv 2508.19850): F1 giữa box dự đoán trên ảnh lỗi và box dự đoán trên ảnh sạch, khớp một-một, cùng class, IoU ≥ 0.5. Không cần nhãn. Đo **độ ổn định output**, không đo độ đúng.
- **GT recall@0.5** (theo "accuracy" của MIQA): tỷ lệ box ground-truth được detector khớp đúng class tại IoU ≥ 0.5.
- **Tương quan:** Spearman (xếp hạng rồi Pearson, không dùng scipy) giữa health và consistency.
- **Cổng fallback:** gắn cờ frame khi health < τ; coi là "lỗi detector" khi consistency < 0.5; báo cáo failure recall và false alarm theo τ.

## Hiện thực trong code

File `t1_health/bench.py`:

| Hàm | Việc làm |
|---|---|
| `health_metrics()` | Laplacian variance, entropy, brightness, % pixel cháy/tối |
| `health_score()` | Gộp kiểu nhân, chuẩn hoá theo median baseline |
| `iou()`, `match_f1()` | Khớp box greedy một-một, IoU ≥ 0.5, cùng class → consistency F1 |
| `gt_hit()` | Recall box GT (có map class KITTI → COCO) và độ tin cậy |
| `spearman()` | Xếp hạng + Pearson |
| `FAULTS` | 6 loại lỗi, mức đặt tên theo tham số thật (blur σ, kernel px, noise σ, gamma, JPEG quality) |

## Bằng chứng và kết quả

**Thiết lập.**
- Drone: 5 video train (Backpack, Laptop, MobilePhone, Person1, WaterBottle), 15 frame/video, `seed = 0` → 75 frame, 20 điều kiện (baseline + 6 lỗi × 3–4 mức).
- KITTI: 20 ảnh ngẫu nhiên từ `images/val`, `SEED = 42`, `N_IMAGES = 20`.
- Detector: YOLO11n, YOLO26n/s/m (COCO pretrained), imgsz 640 và 1280; CPU rồi GPU RTX 4050.

**Kết quả drone (YOLO11n, trung bình 75 frame/điều kiện)** — nguồn `results/summary.csv`:

| Điều kiện | Health | Consistency | GT recall |
|---|---|---|---|
| Baseline | 0.72 | 1.00 | 0.093 |
| Gaussian blur σ = 8 | 0.10 | 0.39 | 0.000 |
| Motion blur 41 px | 0.40 | 0.41 | 0.000 |
| **Noise σ = 50** | **0.78 ↑** | 0.52 | 0.000 |
| Dark γ = 4.5 | 0.08 | 0.43 | 0.000 |
| JPEG q = 3 | 0.39 | 0.37 | 0.000 |

- ρ(health, consistency) theo frame chỉ 0.08; riêng noise là −0.16.
- **Failure case:** Backpack_0, frame 5156, noise σ = 50: health 0.92 ("khỏe"), Laplacian var 16 706, consistency 0.00 (`results/failure_case.png`).
- **Hạn chế lớn của drone:** ở baseline detector COCO chỉ tìm GT ở 7–10/75 frame (chỉ Person1); Backpack/Laptop/MobilePhone/WaterBottle luôn 0/15 ở mọi model và imgsz. Nên GT recall gần như vô nghĩa trên drone, kết luận dựa chủ yếu vào consistency (proxy).

**Đối chứng KITTI (YOLO26m, imgsz 1280)** — nguồn `results_yolo26m_1280_kitti/summary.csv`: detector hoạt động thật (GT recall baseline 0.85). ρ(health, consistency) theo loại lỗi: Gaussian blur 0.84, JPEG 0.72, dark 0.51, overexpose 0.50, motion blur 0.32, **noise −0.16**; tổng chung chỉ 0.17. Cháy sáng γ = 0.15 làm health tụt còn 0.07 nhưng GT recall gần như không đổi (0.84) → báo động nhầm.

**So sánh model** (KITTI, GT recall tại lỗi nặng, `results_*_kitti/`):

| Model | Baseline | Blur σ=8 | Noise σ=50 | JPEG q=3 |
|---|---|---|---|---|
| YOLO11n 640 | 0.80 | 0.29 | 0.49 | 0.31 |
| YOLO26m 640 | 0.84 | 0.49 | 0.61 | 0.23 |
| YOLO26m 1280 | 0.85 | 0.29 | 0.69 | 0.02 |

Không có model nào tốt nhất cho mọi loại lỗi; tăng imgsz giúp noise/tối nhưng làm blur/JPEG kém hơn.

**Cổng fallback (drone, YOLO11n):** τ = 0.7 bắt 81% frame lỗi nhưng báo nhầm 79% → gần như ngẫu nhiên ở mức frame.

**Consistency không chứng minh detector đúng:** nó chỉ so output với output của chính detector trên ảnh sạch. Nếu detector sai ở ảnh sạch (như drone) thì consistency cao vẫn vô nghĩa.

## Phần việc cá nhân

**Tôi trực tiếp thực hiện:** 

- Chọn paper theo tiêu chí mới + duyệt + có code: MPD (CVPR 2025) làm paradigm, MIQA (arXiv 2508.19850) lấy công thức consistency/accuracy; loại GSHI vì chưa được bình duyệt và không có code (chỉ mượn ý tưởng gộp kiểu nhân).
- Hiện thực `health_metrics()`, `health_score()`, `match_f1()`, `gt_hit()` và pipeline benchmark (fault có tham số, seed cố định, xuất CSV/plot/ảnh failure case).
- Kiểm tra metric: phát hiện noise làm Laplacian variance tăng → health sai chiều; kiểm tra cổng fallback (failure recall / false alarm theo τ).
- Mở rộng thí nghiệm: YOLO11n/26n/26s/26m, imgsz 640/1280, CPU → GPU (cài lại torch CUDA), thêm bộ KITTI để kiểm chứng chéo.
- Sửa lỗi gặp phải: thiếu scipy (tự viết Spearman), kiểu tham số OpenCV với `int`, lỗi đặt tên thư mục kết quả làm ghi đè `results/` (đã sửa và chạy lại).

## Kết luận cá nhân

- **Hữu ích:** health score thủ công bám tốt detector *trong từng loại lỗi* blur, JPEG, dark (ρ 0.5–0.84 trên KITTI). Consistency F1 hữu ích vì không cần nhãn, nhưng phải đi kèm GT recall khi detector chạy được.
- **Dễ sai:** (1) noise đánh lừa Laplacian variance (health tăng khi detector hỏng); (2) cháy sáng bị phạt nặng dù detector gần như không ảnh hưởng; (3) tương quan gộp mọi lỗi chỉ ~0.03–0.18; (4) trên drone, detector COCO không thấy vật nhỏ nên mọi metric dựa trên nó yếu.
- **Vì sao cần hiệu chuẩn theo loại lỗi:** cùng một mức health (ví dụ 0.3), blur là nguy hiểm còn overexpose thì vô hại; và thang này đổi theo từng detector/imgsz. Đề xuất: thêm kênh ước lượng noise vào health (Immerkær/MAD), calibrate theo cặp (detector, loại lỗi); kiểm chứng bằng việc ρ cho noise chuyển từ âm sang dương và false alarm giảm ở cùng mức failure recall. Đề xuất này **chưa được chạy**.
- **Giới hạn:** drone chỉ 75 frame / 5 video, KITTI 20 ảnh, một seed; lỗi tổng hợp và riêng lẻ, chưa đo latency; map class KITTI → COCO là xấp xỉ (van → car).