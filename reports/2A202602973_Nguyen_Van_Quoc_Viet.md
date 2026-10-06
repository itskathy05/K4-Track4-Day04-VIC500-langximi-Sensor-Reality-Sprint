# Báo cáo cá nhân — Nguyễn Văn Quốc Việt

**MSSV:** 2A202602973
**Phần phụ trách:** Failure case, engineering decision và tích hợp báo cáo.

## Failure case

Đây là case được `bench.py` tự chọn: trong các mẫu có health ≥ min(0.8, percentile 90) = 0.8, lấy mẫu có consistency thấp nhất. Kết quả là Backpack_0, frame 5156, Gaussian noise σ=50:

| Điều kiện | Laplacian var. | Health | Consistency | GT hit | Số box |
|---|---:|---:|---:|---:|---:|
| baseline | 1452.3 | 0.852 | 1.000 | 0.000 | 1 |
| noise σ=10 | 2271.0 | 0.899 | 1.000 | 0.000 | 1 |
| noise σ=25 | 6054.8 | 0.896 | 1.000 | 0.000 | 1 |
| noise σ=50 | 16706.0 | **0.917** | **0.000** | 0.000 | 0 |

_Nguồn: `results/results.csv`; ảnh minh hoạ: `results/failure_case.png`._

**Quan sát đo được:**

- Noise càng mạnh thì Laplacian variance càng tăng: lên 16706, gấp khoảng 8.4 lần median baseline của tập drone (1988.2) và 11.5 lần chính frame này lúc sạch. Thành phần `h_sharp` vì vậy bị kẹp ở 1.0, nên health của frame nhiễu nặng nhất (0.917) còn cao hơn frame sạch (0.852).
- Ở σ=50, detector mất box duy nhất nên consistency về 0. Nhưng **GT hit bằng 0 ngay từ baseline**: trên frame sạch, detector đã không bắt được chiếc balo (box GT rất nhỏ). Vì vậy case này cho thấy *output detector mất ổn định*. Nó không cho thấy detector "đang đúng rồi bị noise làm sai". Slide ghi "GT hit=0.000" mà không nói rõ điều này, nên người đọc dễ hiểu nhầm.
- Case này không phải ngoại lệ. Có 77 mẫu health ≥ 0.8 mà consistency < 0.5; trong đó 57 mẫu là noise, 19 là JPEG và 1 là dark. Spearman giữa health và consistency **trong nhóm noise là −0.161**, tức là ngược chiều mong muốn. Với blur Gaussian là 0.230 và với dark là 0.314.

**Giả thuyết (chưa kiểm định):** noise thêm năng lượng tần số cao, mà Laplacian variance lại hiểu năng lượng đó là "chi tiết/độ nét". Muốn khẳng định quan hệ nhân quả cần ablation: thay `h_sharp` bằng một phép đo bền với noise (ví dụ ước lượng noise rồi trừ ra, hoặc đo sharpness trên ảnh đã khử nhiễu nhẹ) rồi xem lỗi có biến mất không.

## Trade-off của ngưỡng health

Quy tắc trong `bench.py`: bật cờ khi `health < tau`; một mẫu được coi là "failure" khi `consistency < 0.5`. Trên 1425 mẫu có corruption (618 failure, 807 không failure):

| tau | Failure recall | False-alarm rate |
|---:|---:|---:|
| 0.5 | 62.9% | 56.8% |
| 0.6 | 71.2% | 69.4% |
| 0.7 | 81.1% | 79.2% |
| 0.8 | 87.5% | 85.4% |

Điểm cần nói rõ là **ở mọi ngưỡng, failure recall chỉ cao hơn false-alarm rate 2–6 điểm %**. Nghĩa là trên tập này, score gần như chưa phân biệt được frame làm detector hỏng với frame không làm hỏng; đây là trên tổng mọi loại lỗi. Điều này cũng khớp với Spearman tổng 0.079. Bỏ noise ra cũng chỉ cải thiện rất ít: ở tau=0.7, recall 91.8% và false alarm 88.1%. Lý do là blur, dark và overexpose kéo health xuống thấp ở mọi mức, kể cả ở những mức detector vẫn ổn định. Riêng noise thì score gần như không phản ứng: ở tau=0.7 chỉ bắt được 17/91 failure (18.7%).

Có hai yếu tố làm phép đo này kém tin cậy:

- Health của frame sạch đã dao động rộng (0.269–0.985, median 0.767). Vì vậy tau=0.7 bật cờ cả với nhiều frame không hề bị lỗi.
- Trên frame sạch, detector chỉ đạt GT recall trung bình 0.093, và 37/75 frame không có box nào. Khi frame sạch không có box, consistency chỉ còn hai giá trị 1 hoặc 0, tuỳ detector có sinh box mới hay không. Vì thế nhãn "failure" ở đây phần lớn phản ánh độ ổn định của một detector vốn yếu trên vật nhỏ nhìn từ drone.

## Engineering decision

1. **Dùng score cho monitoring/logging, không dùng để tự động điều khiển xe/drone.** Bằng chứng: false alarm gần bằng failure recall ở mọi ngưỡng, và score phản ứng ngược với noise.
2. **Tách cờ theo từng loại lỗi thay vì một ngưỡng chung.** Score theo từng thành phần có ích với từng lỗi riêng: blur thì xem `h_sharp`, dark/overexpose thì xem `h_exp`. Noise cần một kênh phát hiện riêng. Hướng này đúng với kết luận trên slide, nhưng nhóm chưa đo ngưỡng cho từng loại lỗi; đó là việc cần làm tiếp.
3. **Dữ liệu cần log khi vận hành:** health tổng và từng kênh (sharp/entropy/exposure, tỉ lệ pixel bị clip), noise estimate, số box và confidence, consistency hoặc GT trên mẫu có nhãn, detector version, imgsz/conf, timestamp, latency.
4. **Fallback đề xuất (chưa kiểm chứng):** khi có ≥3 frame liên tiếp vượt ngưỡng đã hiệu chuẩn cho từng loại lỗi, đánh dấu camera là degraded và chuyển sang frame/camera dự phòng. Trước khi dùng thật cần đo lại trên video có nhãn từ camera vận hành, với nhiều seed và nhiều cảnh.

## Phần việc cá nhân

**Tôi trực tiếp thực hiện:**

- Phân tích `results/results.csv`: Spearman theo từng loại lỗi, bảng failure recall/false alarm ở 4 ngưỡng, tỉ lệ bắt failure theo từng loại lỗi, và trường hợp bỏ noise.
- Phân tích failure case Backpack_0/5156 trên toàn bộ 20 điều kiện. Phát hiện GT hit đã bằng 0 ở baseline, và thống kê 77 mẫu "health cao, detector hỏng" theo loại lỗi.
- Diễn giải trade-off của ngưỡng; chỉ ra rằng failure recall ≈ false-alarm rate, và giải thích ảnh hưởng của detector yếu cùng các frame không có box.

## Kết luận cá nhân

Health score hiện tại chỉ nên dùng làm tín hiệu monitoring cho từng loại lỗi, chưa nên dùng làm cổng an toàn. Trên tập drone, score hầu như không phân biệt được frame làm detector hỏng (recall ≈ false alarm) và phản ứng ngược với noise. Trước khi triển khai cần: (1) thêm kênh ước lượng noise và đo lại failure case; (2) hiệu chuẩn ngưỡng cho từng loại lỗi và từng camera, rồi báo cáo recall và false alarm cho từng loại; (3) dùng detector hoặc dataset mà baseline GT recall đủ cao, để "failure" phản ánh việc mất dự đoán đúng chứ không chỉ là output dao động; (4) kiểm chứng trên video thật từ camera vận hành với nhiều seed.
