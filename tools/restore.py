#!/usr/bin/env python3
"""Restore the plates: straighten photographed storyboard sheets (tools/grid.py),
even out the lighting on line art, and upscale with a neural model.

    python3 tools/restore.py MODEL.pth [first last]

MODEL.pth is Real-ESRGAN's `realesr-general-x4v3.pth`. Needs torch, numpy,
opencv and Pillow. Reads plates/NNN.jpg, writes art/NNN.webp and
tools/restored.json (what was done to each plate). Originals are never changed.
"""
import json, os, sys
import cv2, numpy as np, torch
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import catalog as C, grid, sr

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINE_ART = {"board", "frame", "lineup"}       # paper-white drawings: lighting is evened
LONG_SIDE = 2200                               # restored plates are at most this long
NO_STRAIGHTEN = set()                          # plates where straightening was checked by eye and rejected


def straighten(rgb):
    """Undo the camera's view of a photographed sheet, using the book's printed grid of frames.

    Flat scans are left alone, and so is any sheet whose grid cannot be found and
    confirmed (see grid.locate). Nothing is cropped. Returns (image, done)."""
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    if np.percentile(gray, 60) >= 236: return rgb, False      # a flat scan, not a photograph
    found = grid.locate(gray)
    if found is None: return rgb, False
    return grid.rectify(rgb, found[0], found[1])


def even_light(rgb):
    """Flatten uneven lighting on paper and set the paper to white, leaving colour alone."""
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB); L = lab[:, :, 0].astype(np.float32)
    k = max(31, (min(L.shape) // 14) | 1)
    bg = cv2.morphologyEx(L, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    bg = cv2.GaussianBlur(bg, (0, 0), k / 2)
    bg = np.maximum(bg, 0.62 * np.percentile(L, 90))          # do not lift genuinely dark areas
    L = np.clip(L / bg * 250.0, 0, 255)
    b = min(np.percentile(L, 0.5), 70) * 0.55
    lab[:, :, 0] = np.clip((L - b) / (250.0 - b) * 255.0, 0, 255).astype(np.uint8)
    return cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)


def main():
    torch.set_num_threads(os.cpu_count() or 4)
    model = sr.load(sys.argv[1], 32)
    lo, hi = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (0, 447)
    rows = {int(l.split("|")[0]): l.split("|")[1] for l in C.ROWS.strip().splitlines()}
    skip = {k for g in C.SAME for k in g[1:]}                # repeat scans are not restored
    os.makedirs(os.path.join(ROOT, "art"), exist_ok=True)
    log_path = os.path.join(ROOT, "tools", "restored.json")
    log = json.load(open(log_path)) if os.path.exists(log_path) else {}
    for i in range(lo, hi + 1):
        if i in skip or (str(i) in log and os.path.exists(os.path.join(ROOT, "art", "%03d.webp" % i))): continue
        rgb = np.array(Image.open(os.path.join(ROOT, "plates", "%03d.jpg" % i)).convert("RGB")); did = []
        if rows[i] == "board" and i not in NO_STRAIGHTEN:
            rgb, ok = straighten(rgb)
            if ok: did.append("straightened")
        if rows[i] in LINE_ART:
            rgb = even_light(rgb); did.append("lighting evened")
        h, w = rgb.shape[:2]
        if max(h, w) < 1700:
            up = sr.upscale(model, rgb)
            soft = cv2.resize(rgb, (w * 4, h * 4), interpolation=cv2.INTER_LANCZOS4)
            k = 0.55 if rows[i] in LINE_ART else 0.7               # keep some of the scan's own texture
            rgb = cv2.addWeighted(up, k, soft, 1 - k, 0); did.append("upscaled 4×")
        h, w = rgb.shape[:2]
        if max(h, w) > LONG_SIDE:
            f = LONG_SIDE / max(h, w); rgb = cv2.resize(rgb, (round(w * f), round(h * f)), interpolation=cv2.INTER_AREA)
        Image.fromarray(rgb).save(os.path.join(ROOT, "art", "%03d.webp" % i), "WEBP", quality=80, method=5)
        log[str(i)] = dict(w=rgb.shape[1], h=rgb.shape[0], did=did)
        if i % 10 == 0:
            json.dump(log, open(log_path, "w"), separators=(",", ":")); print(i, did, flush=True)
    json.dump(log, open(log_path, "w"), separators=(",", ":"))
    print("restored", len(log))

if __name__ == "__main__":
    main()
