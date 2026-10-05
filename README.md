# Sensor Reality Sprint: Camera Health Benchmark

Source code for a camera degradation benchmark on drone and KITTI/ADAS images.

## Source

- `t1_health/bench.py` applies six image corruptions and calculates image-health features, detector consistency F1, and ground-truth recall.
- `t1_health/requirements.txt` lists the Python dependencies.

## Run

Use Python 3.10 or newer. Place the input data and YOLO weights at the local paths below, then run from the repository root:

```powershell
python -m venv .venv
.venv\Scripts\pip install -r t1_health\requirements.txt
.venv\Scripts\python t1_health\bench.py yolo11n.pt 640 drone
.venv\Scripts\python t1_health\bench.py yolo26m.pt 1280 kitti
```

The script expects these data paths:

- `data/observing/train/annotations/annotations.json`
- `data/observing/train/samples/<video>/drone_video.mp4`
- `data/kitti/images/val/*.png`
- `data/kitti/labels/val/*.txt`

Model files such as `yolo11n.pt` and `yolo26m.pt` belong in `t1_health/`. Dataset files and model weights are external local assets and are ignored by Git.

## Metric note

The health score is the project’s hand-built product of sharpness, entropy, and exposure components. Consistency F1 compares predictions from a degraded frame with predictions from the same clean frame; it measures stability, not correctness. Ground-truth recall measures detector hits against labels.

The project follows machine-centric image-quality work and references consistency/accuracy definitions from MIQA. It does not run RA-MIQA.
