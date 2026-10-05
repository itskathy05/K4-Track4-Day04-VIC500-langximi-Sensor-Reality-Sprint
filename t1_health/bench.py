"""T1 - Camera degradation health score vs. machine-centric quality (drone footage).

Follows the machine-centric IQA paradigm (MPD, CVPR 2025) with the detection score
definitions of MIQA (arXiv 2508.19850): consistency = distorted preds vs clean preds,
accuracy = distorted preds vs ground truth. Question: do cheap no-reference health
metrics (blur / entropy / exposure) track what the detector actually loses?

Run:  .venv/Scripts/python.exe t1_health/bench.py
"""
import json, random, time
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / "data/observing/train"
import sys
MODEL = sys.argv[1] if len(sys.argv) > 1 else "yolo11n.pt"
IMGSZ = int(sys.argv[2]) if len(sys.argv) > 2 else 640
DATASET = sys.argv[3] if len(sys.argv) > 3 else "drone"   # "drone" | "kitti"
OUT = ROOT / ("results" + ("" if MODEL == "yolo11n.pt" else f"_{Path(MODEL).stem}") + ("" if IMGSZ == 640 else f"_{IMGSZ}") + ("" if DATASET == "drone" else f"_{DATASET}"))
SEED, FRAMES_PER_VIDEO, CONF, IOU_T = (0, 15, 0.10, 0.5) if DATASET == "drone" else (42, 0, 0.10, 0.5)
N_IMAGES = 20  # KITTI only: random images from val split
# KITTI class -> COCO id (car/van->car, truck->truck, pedestrian/sitting/cyclist->person, tram->train; misc skipped)
KITTI2COCO = {0: 2, 1: 2, 2: 7, 3: 0, 4: 0, 5: 0, 6: 6}
# drone target class -> COCO class id (Jacket / Lifering have no COCO class -> excluded)
VIDEOS = {"Backpack_0": 24, "Laptop_0": 63, "MobilePhone_0": 67, "Person1_0": 0, "WaterBottle_0": 39}

# Faults: one factor at a time, levels named by their real parameter.
def gauss_blur(img, s):  return cv2.GaussianBlur(img, (0, 0), s)
def motion_blur(img, k):
    k = int(k)
    ker = np.zeros((k, k), np.float32); ker[k // 2, :] = 1 / k
    return cv2.filter2D(img, -1, ker)
def gauss_noise(img, s, rng): return np.clip(img + rng.normal(0, s, img.shape), 0, 255).astype(np.uint8)
def gamma(img, g):       return (255 * (img / 255.0) ** g).astype(np.uint8)   # g>1 darker, g<1 brighter
def jpeg(img, q):        return cv2.imdecode(cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, int(q)])[1], 1)

FAULTS = {
    "gauss_blur": ("sigma", [1, 2, 4, 8], gauss_blur),
    "motion_blur": ("kernel_px", [9, 21, 41], motion_blur),
    "noise": ("sigma", [10, 25, 50], gauss_noise),
    "dark": ("gamma", [2.0, 3.0, 4.5], gamma),
    "overexpose": ("gamma", [0.5, 0.3, 0.15], gamma),
    "jpeg": ("quality", [30, 10, 3], jpeg),
}

# ---- no-reference health metrics (HVS-style proxies, no labels needed) ----
def health_metrics(img):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hist = np.bincount(g.ravel(), minlength=256) / g.size
    nz = hist[hist > 0]
    return {
        "lap_var": float(cv2.Laplacian(g, cv2.CV_64F).var()),       # sharpness; higher = sharper
        "entropy": float(-(nz * np.log2(nz)).sum()),                 # bits, max 8
        "brightness": float(g.mean()),                               # 0..255
        "clipped": float(((g <= 5) | (g >= 250)).mean()),            # fraction of crushed pixels
    }

def health_score(m, ref):
    """GSHI-style multiplicative score in [0,1]; one bad channel drags the score down.
    ref = baseline medians (per-platform calibration, as GSHI also requires)."""
    h_sharp = np.clip(np.log1p(m["lap_var"]) / np.log1p(ref["lap_var"]), 0, 1)
    h_ent = np.clip(m["entropy"] / ref["entropy"], 0, 1)
    h_exp = np.clip(1 - abs(m["brightness"] - ref["brightness"]) / 128, 0, 1) * (1 - m["clipped"])
    return float(h_sharp * h_ent * h_exp)

# ---- machine-centric scores (MIQA definitions, single image, F1 of matched boxes) ----
def iou(a, b):
    x1, y1, x2, y2 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    return inter / ((a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter + 1e-9)

def match_f1(pred, ref):
    """pred/ref: list of (box, cls). Greedy one-to-one match, IoU>=IOU_T and same class."""
    if not pred and not ref: return 1.0
    used, tp = set(), 0
    for pb, pc in pred:
        for j, (rb, rc) in enumerate(ref):
            if j not in used and pc == rc and iou(pb, rb) >= IOU_T:
                used.add(j); tp += 1; break
    p = tp / len(pred) if pred else 0.0
    r = tp / len(ref) if ref else 0.0
    return 2 * p * r / (p + r) if p + r else 0.0

def spearman(a, b):  # rank + Pearson (no scipy needed)
    return round(a.rank().corr(b.rank()), 3)

def detect(model, img):
    r = model.predict(img, conf=CONF, imgsz=IMGSZ, verbose=False)[0]
    return [(tuple(b), int(c), float(s)) for b, c, s in
            zip(r.boxes.xyxy.tolist(), r.boxes.cls.tolist(), r.boxes.conf.tolist())]

def gt_hit(dets, gts):
    """Accuracy: recall of GT boxes (IoU>=IOU_T, right COCO class) + mean best confidence."""
    best = [max([s for b, c, s in dets if c == cls and iou(b, box) >= IOU_T], default=0.0) for box, cls in gts]
    return (float(np.mean([x > 0 for x in best])), float(np.mean(best))) if best else (1.0, 0.0)

def sample_frames():
    ann = {v["video_id"]: v for v in json.load(open(DATA / "annotations/annotations.json"))}
    rng, out = random.Random(SEED), []
    for vid, cls_id in VIDEOS.items():
        boxes = [b for seg in ann[vid]["annotations"] for b in seg["bboxes"]]
        cap = cv2.VideoCapture(str(DATA / f"samples/{vid}/drone_video.mp4"))
        for b in sorted(rng.sample(boxes, FRAMES_PER_VIDEO), key=lambda b: b["frame"]):
            cap.set(cv2.CAP_PROP_POS_FRAMES, b["frame"])
            ok, img = cap.read()
            if ok:
                out.append(dict(video=vid, frame=b["frame"], cls=cls_id, img=img,
                                gts=[((b["x1"], b["y1"], b["x2"], b["y2"]), cls_id)]))
    return out

def sample_kitti():
    root = ROOT.parent / "data/kitti"
    paths = sorted((root / "images/val").glob("*.png"))
    out = []
    for p in random.Random(SEED).sample(paths, N_IMAGES):
        img = cv2.imread(str(p)); h, w = img.shape[:2]; gts = []
        for line in open(root / "labels/val" / (p.stem + ".txt")).read().splitlines():
            if not line.strip(): continue
            c, x, y, bw, bh = map(float, line.split())
            if int(c) in KITTI2COCO:
                gts.append((((x - bw / 2) * w, (y - bh / 2) * h, (x + bw / 2) * w, (y + bh / 2) * h), KITTI2COCO[int(c)]))
        out.append(dict(video="kitti", frame=p.stem, img=img, gts=gts))
    return out

def main():
    OUT.mkdir(exist_ok=True)
    t0 = time.time()
    model = YOLO(str(ROOT / MODEL))
    frames = sample_frames() if DATASET == "drone" else sample_kitti()
    print(f"sampled {len(frames)} frames, dataset={DATASET} (seed={SEED})")
    rng = np.random.default_rng(SEED)

    rows = []
    for f in frames:
        clean = detect(model, f["img"])
        clean_bc = [(b, c) for b, c, _ in clean]
        conds = [("baseline", "none", 0, f["img"])]
        for name, (param, levels, fn) in FAULTS.items():
            for lv in levels:
                img = fn(f["img"], lv, rng) if name == "noise" else fn(f["img"], lv)
                conds.append((name, param, lv, img))
        for name, param, lv, img in conds:
            dets = detect(model, img) if name != "baseline" else clean
            hit, conf = gt_hit(dets, f["gts"])
            rows.append(dict(video=f["video"], frame=f["frame"], fault=name, param=param, level=lv,
                             **health_metrics(img), consistency=match_f1([(b, c) for b, c, _ in dets], clean_bc),
                             gt_hit=hit, gt_conf=conf, n_det=len(dets)))
    df = pd.DataFrame(rows)

    ref = df[df.fault == "baseline"][["lap_var", "entropy", "brightness"]].median().to_dict()
    df["health"] = [health_score(r, ref) for r in df.to_dict("records")]
    df.to_csv(OUT / "results.csv", index=False)

    # --- summary table: mean per condition ---
    summ = (df.groupby(["fault", "param", "level"], sort=False)
              [["lap_var", "entropy", "brightness", "health", "consistency", "gt_hit", "gt_conf"]]
              .mean().round(3).reset_index())
    summ.to_csv(OUT / "summary.csv", index=False)

    # --- does health track machine quality? Spearman over all distorted samples ---
    d = df[df.fault != "baseline"]
    corr = {m: spearman(d[m], d["consistency"])
            for m in ["lap_var", "entropy", "brightness", "health"]}
    per_fault = {fname: spearman(g["health"], g["consistency"])
                 for fname, g in d.groupby("fault")}

    # --- monitor as a fallback gate: flag frame if health < tau; "failure" = consistency < 0.5 ---
    gate = []
    for tau in [0.5, 0.6, 0.7, 0.8]:
        fail, flag = d.consistency < 0.5, d.health < tau
        gate.append(dict(tau=tau, failure_recall=round((fail & flag).sum() / max(fail.sum(), 1), 3),
                         false_alarm=round((~fail & flag).sum() / max((~fail).sum(), 1), 3)))
    gate = pd.DataFrame(gate)
    gate.to_csv(OUT / "gate.csv", index=False)

    # --- plots: metric vs fault level ---
    fig, axes = plt.subplots(2, 3, figsize=(14, 7.5), constrained_layout=True)
    base = summ[summ.fault == "baseline"].iloc[0]
    for ax, (name, (param, levels, _)) in zip(axes.ravel(), FAULTS.items()):
        s = summ[summ.fault == name]
        x = ["0"] + [str(l) for l in levels]
        for col, lab in [("consistency", "consistency F1 (vs clean)"), ("gt_hit", "GT recall@0.5"),
                         ("health", "health score")]:
            ax.plot(x, [base[col]] + s[col].tolist(), marker="o", label=lab)
        ax.set_title(name); ax.set_xlabel(param + " (0 = baseline)"); ax.set_ylim(0, 1.05); ax.grid(alpha=.3)
    axes[0, 0].legend(fontsize=8)
    fig.savefig(OUT / "curves.png", dpi=120)

    fig, ax = plt.subplots(figsize=(6.5, 5))
    for name, g in d.groupby("fault"):
        ax.scatter(g.health, g.consistency, s=10, alpha=.5, label=name)
    ax.set_xlabel("health score (no-reference)"); ax.set_ylabel("detector consistency F1")
    ax.set_title(f"Spearman rho = {corr['health']}"); ax.legend(fontsize=8); ax.grid(alpha=.3)
    fig.savefig(OUT / "scatter_health_vs_consistency.png", dpi=120, bbox_inches="tight")

    # --- evidence images: one frame, every fault at its strongest level; plus the failure case ---
    f = frames[0]
    tiles = [("baseline", f["img"])] + [
        (f"{n} {p}={lv[-1]}", (fn(f["img"], lv[-1], np.random.default_rng(SEED)) if n == "noise"
                              else fn(f["img"], lv[-1]))) for n, (p, lv, fn) in FAULTS.items()]
    fig, axes = plt.subplots(2, 4, figsize=(16, 5.2), constrained_layout=True)
    for ax, (t, im) in zip(axes.ravel(), tiles):
        ax.imshow(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)); ax.set_title(t, fontsize=9); ax.axis("off")
    axes.ravel()[-1].axis("off")
    fig.savefig(OUT / "examples.png", dpi=100)

    # failure case = high health, low consistency (monitor says OK, detector is broken)
    fc = d[(d.health >= min(0.8, d.health.quantile(0.9)))].sort_values("consistency").iloc[0]
    fc_frame = next(x for x in frames if x["video"] == fc.video and x["frame"] == fc.frame)
    fn = FAULTS[fc.fault][2]
    fc_img = fn(fc_frame["img"], fc.level, np.random.default_rng(SEED)) if fc.fault == "noise" else fn(fc_frame["img"], fc.level)
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.6), constrained_layout=True)
    for ax, (t, im) in zip(axes, [("baseline", fc_frame["img"]),
                                  (f"{fc.fault} {fc.param}={fc.level}: health={fc.health:.2f}, "
                                   f"consistency={fc.consistency:.2f}", fc_img)]):
        im = im.copy()
        for (x1, y1, x2, y2), _ in fc_frame["gts"]:
            cv2.rectangle(im, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        ax.imshow(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)); ax.set_title(t, fontsize=9); ax.axis("off")
    fig.savefig(OUT / "failure_case.png", dpi=110)

    meta = dict(seed=SEED, frames=len(frames), dataset=DATASET, videos=VIDEOS if DATASET == "drone" else "kitti val", detector=f"{MODEL} (COCO) imgsz={IMGSZ}", conf=CONF,
                iou=IOU_T, faults={k: [v[0], v[1]] for k, v in FAULTS.items()}, baseline_ref=ref,
                spearman_vs_consistency=corr, spearman_health_per_fault=per_fault,
                failure_case=fc[["video", "frame", "fault", "param", "level", "lap_var", "health",
                                 "consistency", "gt_hit"]].to_dict(),
                runtime_s=round(time.time() - t0, 1))
    json.dump(meta, open(OUT / "run_meta.json", "w"), indent=2, default=float)
    print(summ.to_string(index=False)); print("spearman vs consistency:", corr)
    print("per-fault health rho:", per_fault); print(gate.to_string(index=False))
    print("failure case:", meta["failure_case"]); print("runtime", meta["runtime_s"], "s")

if __name__ == "__main__":
    main()
