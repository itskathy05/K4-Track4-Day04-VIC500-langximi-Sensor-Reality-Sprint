# Sensor Reality Sprint: Camera Degradation Health Score

Mini project evaluating camera image degradation for drone and ADAS object detection.

## Repository map

- `bench.py`: creates blur, motion blur, noise, exposure, and JPEG corruptions; runs detector metrics and writes benchmark outputs.
- `results/`: primary drone benchmark outputs and evidence.
- `reports/`: five individual report drafts, one per team member.
- `slide.pdf`: one-page project summary following the class template.
- `TEAMMATES.md`: task ownership and individual deliverables.
- `requirements.txt`: Python dependencies.

## Reproduce the primary runs

Use Python 3.10 or newer. Put the datasets at the expected relative paths and YOLO model files in the repository root. The dataset and model weights are external assets and are not committed.

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python bench.py yolo11n.pt 640 drone
.venv\Scripts\python bench.py yolo26m.pt 1280 kitti
```

Expected data paths:

- `data/observing/train/annotations/annotations.json`
- `data/observing/train/samples/<video>/drone_video.mp4`
- `data/kitti/images/val/*.png`
- `data/kitti/labels/val/*.txt`

## Method summary

The team-built health heuristic multiplies normalized sharpness, entropy, and exposure scores. Consistency F1 compares detections on a degraded frame with detections on the corresponding clean frame. It measures output stability, not correctness. Ground-truth recall measures detector hits against labels. The project uses a machine-centric image-quality framing and references MIQA metrics; it does not run RA-MIQA.

The primary run uses 75 drone frames, 20 conditions, and 1,500 inferences. The KITTI cross-check uses 20 images. The selected drone CSV summaries, plot, and failure example are included in `results/`; the slide summarizes the KITTI cross-check separately.

## References

- Li et al., CVPR 2025, *Image Quality Assessment: From Human to Machine Preference*: [paper](https://openaccess.thecvf.com/content/CVPR2025/html/Li_Image_Quality_Assessment_From_Human_to_Machine_Preference_CVPR_2025_paper.html).
- MIQA, arXiv:2508.19850, detection consistency and accuracy metrics: [paper](https://arxiv.org/abs/2508.19850).

## Team and reports

See `TEAMMATES.md`. Each report draft is a starting point for its named member to review and complete with the work they personally performed.
