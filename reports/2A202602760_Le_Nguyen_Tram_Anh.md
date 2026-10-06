# Báo cáo cá nhân — Lê Nguyễn Trâm Anh

**MSSV:** 2A202602760
**Phần phụ trách:** Paper, related work và khung phương pháp.

> Bản nháp theo phân công. Thành viên bổ sung mô tả công việc mình trực tiếp thực hiện trước khi nộp.

## Nguồn phương pháp

Paper chính là *Image Quality Assessment: From Human to Machine Preference* (Li et al., CVPR 2025), dùng góc nhìn chất lượng ảnh theo tác động lên tác vụ máy. Nhóm tham khảo consistency/accuracy từ MIQA (Wang et al., arXiv:2508.19850). Benchmark hiện tại là triển khai nhỏ trên YOLO; nhóm không chạy RA-MIQA.

## Input, output và giả định

Input gồm frame sạch, frame bị corruption và detector. Output gồm health score, consistency F1 và GT recall. Frame sạch dùng làm tham chiếu cho consistency; mỗi lượt áp một loại corruption lên cùng frame nguồn.

## Bằng chứng và kết quả

Đối chiếu mô tả với `bench.py`, `README.md` và kết quả trong `results/`. Phân biệt kết luận của paper với kết quả nhóm đo và heuristic do nhóm tự thiết kế.

## Phần việc cá nhân

**Tôi trực tiếp thực hiện:** _[bổ sung phần tìm paper, đọc phương pháp hoặc tổng hợp tài liệu mà bạn đã làm]._

## Kết luận cá nhân

_[Bổ sung cách machine-centric framing giúp đặt câu hỏi benchmark và điều gì chưa thể kết luận từ thử nghiệm nhỏ này.]_

## Tài liệu

- Li et al., CVPR 2025, *Image Quality Assessment: From Human to Machine Preference*.
- Wang et al., arXiv:2508.19850, *Image Quality Assessment for Machines: Paradigm, Large-scale Database, and Models*.
