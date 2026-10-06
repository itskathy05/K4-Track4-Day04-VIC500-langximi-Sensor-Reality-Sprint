# Báo cáo cá nhân — Nguyễn Thị Thùy Dương
**MSSV:** 2A202602905
**Phần phụ trách:** Bối cảnh bài toán camera, thiết kế dữ liệu và mô phỏng suy giảm ảnh.
**Chủ đề:** T1 — Camera Degradation Health Score trên video drone, đối chiếu thêm với KITTI/ADAS.

## 1. Bối cảnh và mục tiêu
Camera RGB là cảm biến đầu vào quan trọng của drone và hệ thống hỗ trợ lái xe.
Chất lượng ảnh có thể suy giảm do mất nét, rung chuyển động, nhiễu cảm biến, thiếu sáng, cháy sáng hoặc nén mạnh.
Các lỗi này có thể khiến detector bỏ sót vật thể, sinh thêm box hoặc thay đổi lớp dự đoán.
Vì vậy, nhóm xây dựng benchmark để kiểm tra liệu một health score không cần nhãn có phản ánh được mức suy giảm của detector hay không.
Benchmark sử dụng góc nhìn machine-centric image quality: chất lượng ảnh được xem xét theo ảnh hưởng lên tác vụ máy.
Input gồm frame sạch, phiên bản bị corruption và detector YOLO.
Output gồm health score của ảnh, consistency F1 so với prediction sạch và GT recall khi có nhãn.
Consistency chỉ đo độ ổn định của output detector, không khẳng định prediction là đúng.
## 2. Dữ liệu drone
Lượt chạy chính sử dụng dữ liệu tại `data/observing/train` với annotation trong `annotations/annotations.json`.
Năm video được chọn là `Backpack_0`, `Laptop_0`, `MobilePhone_0`, `Person1_0` và `WaterBottle_0`.
Mỗi video cung cấp 15 frame có bounding box, tạo thành tổng cộng 75 mẫu sạch.
Việc lấy mẫu dùng `random.Random(0)`, nhờ đó có thể lặp lại danh sách frame nếu dữ liệu đầu vào không thay đổi.
Hàm `sample_frames()` gom các bounding box của từng video rồi lấy mẫu ngẫu nhiên theo seed cố định.
Video được đọc bằng OpenCV và con trỏ được đưa tới đúng chỉ số frame trước khi lấy ảnh.
Mỗi mẫu lưu tên video, chỉ số frame, ảnh, lớp COCO và bounding box ground truth tương ứng.
Các lớp được ánh xạ sang COCO gồm backpack 24, laptop 63, mobile phone 67, person 0 và bottle 39.
Jacket và lifering không có lớp COCO phù hợp nên không được đưa vào năm video đánh giá này.
## 3. Dữ liệu KITTI đối chiếu
KITTI được dùng như phép kiểm chứng chéo gần với bối cảnh ADAS hơn dữ liệu drone.
Hàm `sample_kitti()` chọn 20 ảnh PNG ngẫu nhiên từ tập validation bằng seed 42.
Nhãn YOLO chuẩn hóa được đổi sang tọa độ pixel trước khi tính IoU với prediction.
Các lớp KITTI được ánh xạ gần đúng sang COCO: car và van thành car, truck thành truck, tram thành train.
Pedestrian, person sitting và cyclist được quy về person; lớp misc bị bỏ qua.
Phép ánh xạ này chỉ là xấp xỉ vì taxonomy của KITTI và COCO không hoàn toàn giống nhau.
Ngoài ra, cấu hình KITTI dùng YOLO26m ở `imgsz=1280`, khác YOLO11n ở `imgsz=640` của lượt chạy drone.
Do đó, kết quả KITTI chỉ nên dùng để đối chiếu xu hướng, không so sánh trực tiếp con số tuyệt đối giữa hai tập.
Repo hiện không chứa thư mục artifact KITTI nên các số KITTI trên slide chưa thể kiểm tra lại từ CSV trong repo.
## 4. Thiết kế corruption
Mỗi corruption được áp dụng độc lập lên cùng frame sạch để tránh trộn lẫn ảnh hưởng của nhiều lỗi.
Benchmark có 19 mức lỗi và một baseline, tức 20 điều kiện cho mỗi frame.

| Corruption | Tham số và mức | Cách mô phỏng |
|---|---|---|
| Gaussian blur | sigma = 1, 2, 4, 8 | Làm mờ bằng Gaussian kernel để mô phỏng mất nét. |
| Motion blur | kernel = 9, 21, 41 px | Dùng kernel ngang để mô phỏng chuyển động tương đối của camera. |
| Gaussian noise | sigma = 10, 25, 50 | Cộng nhiễu chuẩn vào từng kênh màu rồi giới hạn về [0,255]. |
| Thiếu sáng | gamma = 2.0, 3.0, 4.5 | Gamma lớn hơn 1 làm ảnh tối dần. |
| Cháy sáng | gamma = 0.5, 0.3, 0.15 | Gamma nhỏ hơn 1 làm ảnh sáng mạnh dần. |
| JPEG | quality = 30, 10, 3 | Mã hóa và giải mã JPEG ở chất lượng ngày càng thấp. |

Các mức được đặt tên bằng tham số vật lý thực sự thay vì nhãn chung như nhẹ, vừa hoặc nặng.
Cách biểu diễn này giúp người khác tái tạo corruption và hiểu chính xác độ mạnh của từng điều kiện.
Nhiễu dùng `numpy.random.default_rng(SEED)` để kiểm soát tính ngẫu nhiên trong một lượt chạy.
Các ảnh sau corruption không được lưu toàn bộ nhằm tránh làm repo quá lớn; kết quả metric được lưu trong CSV.
## 5. Bằng chứng và nhận xét kết quả
Lượt chạy drone tạo 75 × 20 = 1.500 dòng trong `results/results.csv`.
Biểu đồ `results/curves.png` cho thấy consistency thường giảm khi blur, motion blur, tối hoặc JPEG mạnh hơn.
Ví dụ, Gaussian blur sigma 8 làm consistency trung bình giảm từ 1,000 xuống 0,391.
Motion blur 41 px làm consistency giảm xuống 0,407, còn JPEG quality 3 đạt 0,369.
Noise là trường hợp bất thường quan trọng của thiết kế hiện tại.
Khi sigma tăng từ 10 lên 50, consistency giảm từ 0,677 xuống 0,516 nhưng health vẫn quanh 0,77–0,78.
Nguyên nhân hợp lý là nhiễu tần số cao làm Laplacian variance tăng và bị hiểu nhầm thành độ sắc nét.
Failure case tại `Backpack_0`, frame 5156 minh họa health 0,917 nhưng consistency bằng 0.
Baseline GT recall của drone chỉ đạt 0,093 vì detector COCO khó phát hiện các vật thể nhỏ từ góc nhìn trên cao.
Vì vậy, kết quả drone chủ yếu phản ánh độ ổn định prediction chứ chưa chứng minh detector nhận diện đúng.
Điều này cho thấy lựa chọn dữ liệu và detector baseline phù hợp là điều kiện quan trọng trước khi đánh giá health score.
## 6. Hạn chế và kết luận cá nhân
Thử nghiệm mới dùng 75 frame drone, 20 ảnh KITTI và một seed nên chưa đại diện cho mọi camera hoặc điều kiện môi trường.
Các lỗi đều là corruption tổng hợp, áp dụng riêng lẻ; benchmark chưa có rung phức tạp, mưa, sương, bẩn ống kính hay nhiều lỗi đồng thời.
Việc hiệu chuẩn và đánh giá dùng cùng tập ảnh cũng chưa phản ánh khả năng tổng quát sang camera mới.
Khi mở rộng, cần dùng nhiều video, nhiều seed, corruption thực tế và một detector có baseline GT recall đủ cao.
Theo tôi, thiết kế một lỗi tại một thời điểm phù hợp cho bước phân tích ban đầu vì giúp xác định phản ứng với từng nguyên nhân.
Tuy nhiên, một health score chung chưa mô tả tốt mọi corruption, đặc biệt là Gaussian noise.
Nên bổ sung bộ ước lượng noise riêng và hiệu chuẩn ngưỡng theo từng camera, detector và loại lỗi.
Health score hiện phù hợp để monitoring và thu thập dữ liệu, chưa nên dùng trực tiếp để điều khiển drone hoặc xe.
