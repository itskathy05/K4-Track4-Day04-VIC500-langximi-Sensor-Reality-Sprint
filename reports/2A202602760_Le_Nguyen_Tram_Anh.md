# BÁO CÁO CÁ NHÂN — SENSOR REALITY SPRINT

## Thông tin sinh viên

- **Họ và tên:** Lê Nguyễn Trâm Anh
- **MSSV:** 2A202602760
- **Đề tài nhóm:** Camera Degradation Health Score cho hệ thống thị giác máy
- **Phần phụ trách:** Khảo sát tài liệu, phân tích related work và xây dựng khung phương pháp

## 1. Mục tiêu phần việc cá nhân

Trong dự án này, tôi phụ trách khảo sát hướng **Image Quality Assessment for Machine Vision**, lựa chọn tài liệu liên quan và chuyển hóa các khái niệm trong paper thành một khung đánh giá có thể triển khai trong benchmark nhỏ của nhóm. Câu hỏi tôi tập trung giải quyết là:

> Một ảnh vẫn có thể nhìn tương đối rõ đối với con người nhưng có còn đủ tin cậy đối với mô hình phát hiện vật thể hay không?

Phần việc của tôi gồm:

1. Đọc và tổng hợp hai nguồn chính về đánh giá chất lượng ảnh theo tác vụ máy.
2. Xác định input, output, giả định và metric phù hợp với bài toán camera drone/ADAS.
3. Phân biệt rõ đóng góp của paper với phương pháp do nhóm tự xây dựng.
4. Đối chiếu mô tả phương pháp với `bench.py` và kết quả trong `results/`.
5. Diễn giải ý nghĩa kỹ thuật của kết quả để hỗ trợ quyết định triển khai.

## 2. Bối cảnh bài toán

Trong hệ thống drone hoặc ADAS, camera là một phần của chuỗi đo lường gồm cảm biến, truyền dữ liệu, tiền xử lý và mô hình nhận thức. Chất lượng khung hình có thể suy giảm do mất nét, rung chuyển động, nhiễu, thiếu sáng, cháy sáng hoặc nén mạnh. Các lỗi này tác động trực tiếp đến bounding box, class và confidence của detector.

Các metric ảnh truyền thống thường mô tả mức độ đẹp hoặc giống ảnh tham chiếu theo cảm nhận con người. Tuy nhiên, một hệ thống tự động cần biết ảnh có còn duy trì được đầu ra của tác vụ downstream hay không. Vì vậy, project sử dụng góc nhìn **machine-centric**: chất lượng ảnh được xem xét thông qua ảnh hưởng của degradation lên detector.

## 3. Cơ sở học thuật

### 3.1. Machine Preference Database — Li et al., CVPR 2025

Paper *Image Quality Assessment: From Human to Machine Preference* chỉ ra rằng đánh giá theo Human Visual System và đánh giá theo Machine Vision System có thể không đồng nhất. Với máy, “ảnh tốt” phụ thuộc vào tác vụ downstream, mô hình kiểm thử và metric của tác vụ, thay vì chỉ phụ thuộc vào mức dễ nhìn đối với con người.

Paper đề xuất bài toán Image Quality Assessment for Machine Vision và xây dựng **Machine Preference Database (MPD)** với 30.000 cặp ảnh reference/distorted và 2,25 triệu annotation chi tiết. Kết quả của paper cho thấy các IQA metric thiên về cảm nhận con người chưa mô tả chính xác preference của mô hình thị giác máy.

Đóng góp được nhóm kế thừa từ paper này là **cách đặt vấn đề**: cần kiểm tra một chỉ số chất lượng ảnh bằng mức suy giảm của detector. Nhóm không tái huấn luyện mô hình của paper và không sử dụng MPD trong benchmark.

### 3.2. MIQA — Wang et al., arXiv:2508.19850

Paper *Image Quality Assessment for Machines: Paradigm, Large-scale Database, and Models* trình bày một workflow MIQA theo hướng end-to-end và phân biệt hai nhóm tín hiệu quan trọng:

- **Consistency:** mức ổn định của đầu ra mô hình giữa ảnh bị suy giảm và ảnh sạch tương ứng.
- **Accuracy:** mức đúng của đầu ra mô hình so với ground truth.

MIQA xây dựng MIQD-2.5M với 2,5 triệu mẫu, 75 mô hình thị giác, 250 loại degradation và ba nhóm tác vụ. Paper cũng đề xuất RA-MIQA để phân tích suy giảm theo vùng ảnh.

Project của nhóm chỉ tham khảo **paradigm consistency/accuracy**. Nhóm không chạy RA-MIQA, không sử dụng trọng số của RA-MIQA và không tuyên bố health score của nhóm là mô hình MIQA đã được huấn luyện.

### 3.3. Liên hệ giữa paper và project

| Thành phần | Nguồn paper | Cách nhóm triển khai |
|---|---|---|
| Cách nhìn machine-centric | Li et al. | Đánh giá ảnh bằng phản ứng của detector YOLO |
| Ảnh reference/distorted | MPD và MIQA | Dùng cùng một frame trước và sau corruption |
| Consistency | MIQA | So khớp prediction trên ảnh lỗi với prediction trên ảnh sạch |
| Accuracy | MIQA | Đo tỷ lệ ground-truth box được detector khớp |
| Health score | Không lấy từ paper | Heuristic no-reference do nhóm tự xây dựng |
| RA-MIQA | Wang et al. | Không chạy trong project |

Bảng trên phân biệt rõ tri thức được tham khảo với phần nhóm trực tiếp hiện thực.

## 4. Khung phương pháp của nhóm

### 4.1. Input, output và giả định

**Input** của một lượt đánh giá gồm:

- frame camera sạch `I_clean`;
- frame suy giảm `I_distorted` được tạo từ cùng frame nguồn;
- detector YOLO và cấu hình inference cố định;
- ground-truth box khi tính accuracy.

**Output** gồm:

- các đặc trưng no-reference: Laplacian variance, entropy, brightness và clipped-pixel ratio;
- health score trong khoảng `[0, 1]`;
- detector consistency F1;
- ground-truth recall và confidence trung bình.

Benchmark giữ nguyên nội dung frame và chỉ thay đổi một corruption tại một thời điểm. Prediction trên frame sạch được dùng làm reference khi tính consistency. Các median trên tập baseline được dùng để hiệu chuẩn health score cho platform đang xét.

### 4.2. Thiết kế degradation

Mã nguồn `bench.py` tạo sáu nhóm degradation với nhiều mức cường độ:

| Degradation | Tham số và các mức thử |
|---|---|
| Gaussian blur | `sigma = 1, 2, 4, 8` |
| Motion blur | `kernel = 9, 21, 41 px` |
| Gaussian noise | `sigma = 10, 25, 50` |
| Thiếu sáng | `gamma = 2.0, 3.0, 4.5` |
| Cháy sáng | `gamma = 0.5, 0.3, 0.15` |
| JPEG compression | `quality = 30, 10, 3` |

Cộng với baseline, mỗi frame được đánh giá trong 20 điều kiện. Thiết kế one-factor-at-a-time giúp liên hệ biến động metric với từng loại lỗi cụ thể.

### 4.3. Health score no-reference

Nhóm xây dựng một health score nhẹ, không cần ground truth tại thời điểm vận hành. Với ảnh xám `I`, các thành phần được tính như sau:

```text
L = Var(Laplacian(I))
E = -Σ p(i) log2 p(i)
B = mean(I)
C = tỷ lệ pixel có mức xám ≤ 5 hoặc ≥ 250
```

Trong đó `L` biểu diễn năng lượng biên/chi tiết, `E` là entropy, `B` là brightness và `C` đo tỷ lệ pixel bị crush hoặc clip. Với `L_ref`, `E_ref`, `B_ref` là median của baseline, mã nguồn chuẩn hóa:

```text
H_sharp = clip(log(1 + L) / log(1 + L_ref), 0, 1)
H_entropy = clip(E / E_ref, 0, 1)
H_exposure = clip(1 - |B - B_ref| / 128, 0, 1) × (1 - C)
H = H_sharp × H_entropy × H_exposure
```

Phép nhân làm cho một kênh chất lượng thấp kéo health score tổng xuống. Đây là heuristic do nhóm thiết kế để tạo proxy metric có chi phí thấp; nó không phải công thức của MPD hay MIQA.

### 4.4. Metric theo tác vụ máy

**Consistency F1.** Prediction trên ảnh lỗi và ảnh sạch được ghép one-to-one khi cùng class và `IoU ≥ 0.5`. Từ số cặp khớp, chương trình tính precision, recall và F1. Consistency cao cho biết detector ổn định so với baseline, nhưng không tự chứng minh prediction đúng.

**Ground-truth recall.** Với mỗi ground-truth box, chương trình tìm detection cùng class có `IoU ≥ 0.5`. Metric `gt_hit` là tỷ lệ ground-truth box có detection phù hợp. Metric này phản ánh accuracy trực tiếp hơn consistency.

**Spearman correlation.** Hệ số Spearman giữa health score và consistency được dùng để kiểm tra health score có xếp hạng mức suy giảm detector đúng xu hướng hay không. Giá trị gần 1 thể hiện quan hệ đồng biến mạnh; giá trị gần 0 thể hiện khả năng dự báo thứ hạng yếu.

## 5. Thiết lập benchmark và bằng chứng chạy được

Benchmark chính sử dụng 75 frame được lấy từ 5 video drone, seed 0, detector YOLO11n, `imgsz = 640`, `confidence = 0.10` và ngưỡng ghép box `IoU = 0.5`. Với 20 điều kiện trên mỗi frame, tổng số lượt inference là:

```text
75 frame × 20 điều kiện = 1.500 lượt inference
```

Kết quả chi tiết nằm trong `results/results.csv`; trung bình theo điều kiện nằm trong `results/summary.csv`; xu hướng các metric nằm trong `results/curves.png`; failure case trực quan nằm trong `results/failure_case.png`.

Một số kết quả đại diện từ `summary.csv`:

| Điều kiện | Health | Consistency F1 | GT recall |
|---|---:|---:|---:|
| Baseline | 0.724 | 1.000 | 0.093 |
| Gaussian blur, σ=8 | 0.095 | 0.391 | 0.000 |
| Motion blur, kernel=41 | 0.404 | 0.407 | 0.000 |
| Noise, σ=50 | 0.779 | 0.516 | 0.000 |
| Dark, γ=4.5 | 0.078 | 0.428 | 0.000 |
| Overexpose, γ=0.15 | 0.011 | 0.543 | 0.147 |
| JPEG, quality=3 | 0.393 | 0.369 | 0.000 |

Các giá trị cho thấy health score phản ứng rõ với blur, thiếu sáng và cháy sáng. Noise là trường hợp đáng chú ý: health trung bình vẫn cao 0.779 trong khi GT recall giảm về 0.000. Trên toàn bộ 1.425 mẫu suy giảm, Spearman giữa health và consistency chỉ đạt **0.079**. Vì vậy, health score tổng hợp hiện tại chưa đủ mạnh để thay thế metric theo detector.

## 6. Failure case và diễn giải kỹ thuật

Failure case cụ thể nằm ở video `Backpack_0`, frame 5156, Gaussian noise `sigma = 50`:

- health score: **0.917**;
- consistency: **0.000**;
- GT hit: **0.000**;
- Laplacian variance: **16.706**, cao khoảng 8,4 lần median baseline 1.988.

Quan sát này cho thấy Laplacian variance có thể xem nhiễu cao tần là chi tiết sắc nét, làm `H_sharp` bão hòa gần 1 dù detector đã mất toàn bộ box khớp. Đây là một diễn giải phù hợp với dữ liệu đo và giải thích tại sao một metric ảnh đơn giản có thể lệch khỏi machine preference.

Failure case củng cố luận điểm của hai paper: chất lượng theo đặc trưng ảnh hoặc cảm nhận thị giác không tự động đồng nghĩa với chất lượng đối với downstream model. Việc đánh giá cần gắn với detector, loại degradation và cấu hình platform.

## 7. Trade-off và quyết định kỹ thuật

Khi dùng health score như một gate với điều kiện “failure = consistency < 0.5”, ngưỡng `tau = 0.7` phát hiện được **81,1%** failure nhưng tạo **79,2%** false alarm trên benchmark drone. Ngưỡng này ưu tiên bắt lỗi nhưng sẽ flag nhiều frame mà detector vẫn còn ổn định.

Từ kết quả trên, tôi đề xuất sử dụng health score hiện tại như tín hiệu **monitoring/triage** kết hợp với các kênh khác. Hệ thống thực tế nên log riêng `H_sharp`, `H_entropy`, `H_exposure`, noise estimate, detector confidence, latency, timestamp, camera ID và phiên bản model. Quyết định fallback nên dựa trên nhiều frame liên tiếp và được hiệu chuẩn theo từng camera, detector và điều kiện vận hành.

Đặc biệt, cần bổ sung một kênh ước lượng noise hoặc thay thành phần sharpness bằng metric có khả năng phân biệt cạnh thật với nhiễu cao tần. Sau đó có thể đánh giá lại failure recall, false-alarm rate và latency trước khi dùng score để tự động down-weight camera.

## 8. Đóng góp cá nhân

Trong phạm vi được phân công, tôi đã:

- khảo sát và tổng hợp hướng machine-centric IQA từ MPD và MIQA;
- xác định mối liên hệ giữa reference/distorted image, consistency và accuracy với benchmark của nhóm;
- chuẩn hóa phần mô tả input, output, giả định và metric;
- phân biệt rõ phương pháp trong paper với health heuristic do nhóm xây dựng;
- đối chiếu mô tả thuật toán với các hàm `health_metrics()`, `health_score()`, `match_f1()` và `gt_hit()` trong `bench.py`;
- đọc `summary.csv`, `results.csv` và failure case để diễn giải kết quả theo góc nhìn machine-centric;
- đề xuất cách sử dụng health score và các tín hiệu cần bổ sung khi chuyển sang hệ thống thực tế.

## 9. Kết luận cá nhân

Qua phần nghiên cứu và đối chiếu thực nghiệm, tôi kết luận rằng đánh giá camera cho drone/ADAS cần bám vào hiệu năng của downstream model. Health score nhẹ có ưu điểm là tính được trực tiếp từ ảnh và phù hợp cho giám sát thời gian thực, nhưng phải được kiểm định bằng consistency và accuracy trên đúng camera, detector và loại degradation.

Kết quả Spearman 0.079 cùng failure case noise cho thấy giá trị lớn nhất của benchmark không chỉ là tạo một điểm health, mà là xác định được lúc proxy metric không còn phản ánh đúng trạng thái của detector. Hướng triển khai phù hợp là giữ health score như một tín hiệu hỗ trợ, bổ sung noise-aware metric và hiệu chuẩn threshold trên dữ liệu vận hành trước khi kích hoạt fallback tự động.

## 10. Tài liệu tham khảo và artifact

1. C. Li et al., “Image Quality Assessment: From Human to Machine Preference,” *Proceedings of CVPR*, pp. 7570–7581, 2025. https://openaccess.thecvf.com/content/CVPR2025/html/Li_Image_Quality_Assessment_From_Human_to_Machine_Preference_CVPR_2025_paper.html
2. X. Wang, Y. Zhang, and W. Lin, “Image Quality Assessment for Machines: Paradigm, Large-scale Database, and Models,” arXiv:2508.19850, 2025. https://arxiv.org/abs/2508.19850
3. Mã nguồn benchmark của nhóm: `bench.py`.
4. Kết quả thực nghiệm: `results/results.csv`, `results/summary.csv`, `results/curves.png`, `results/failure_case.png`.
5. Tóm tắt trình bày: `slide.pdf`.
