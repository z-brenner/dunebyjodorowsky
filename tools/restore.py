#!/usr/bin/env python3
"""Restore the plates: straighten photographed storyboard sheets, even out the
lighting on line art, and upscale with a neural model.

    python3 tools/restore.py MODEL.pth [first last]

MODEL.pth is Real-ESRGAN's `realesr-general-x4v3.pth`. Needs torch, numpy,
opencv and Pillow. Reads plates/NNN.jpg, writes art/NNN.webp and
tools/restored.json (what was done to each plate). Originals are never changed.
"""
import json, os, sys
import cv2, numpy as np, torch
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import catalog as C, sr

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINE_ART = {"board", "frame", "lineup"}       # paper-white drawings: lighting is evened
LONG_SIDE = 2200                               # restored plates are at most this long
NO_STRAIGHTEN = {212, 261}                    # checked by eye: straightening made these worse


def order(q):
    q = q.reshape(4, 2).astype(np.float32); s = q.sum(1); d = q[:, 0] - q[:, 1]
    return np.array([q[s.argmin()], q[d.argmax()], q[s.argmax()], q[d.argmin()]], np.float32)  # tl tr br bl


def panels(gray):
    """Find the ruled storyboard frames as quadrilaterals."""
    h, w = gray.shape
    bs = max(15, (w // 40) | 1)
    thr = cv2.adaptiveThreshold(cv2.GaussianBlur(gray, (3, 3), 0), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, bs, 8)
    thr = cv2.dilate(thr, np.ones((3, 3), np.uint8))
    cnts, _ = cv2.findContours(thr, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    out = []
    for c in cnts:
        a = cv2.contourArea(c)
        if a < 0.012 * h * w or a > 0.2 * h * w: continue
        p = cv2.approxPolyDP(c, 0.02 * cv2.arcLength(c, True), True)
        if len(p) != 4 or not cv2.isContourConvex(p): continue
        q = order(p); ww = (np.linalg.norm(q[1] - q[0]) + np.linalg.norm(q[2] - q[3])) / 2
        hh = (np.linalg.norm(q[3] - q[0]) + np.linalg.norm(q[2] - q[1])) / 2
        if hh < 1 or not 1.4 < ww / hh < 3.6: continue
        c0 = q.mean(0)
        if any(np.linalg.norm(c0 - o.mean(0)) < 0.25 * hh for o in out): continue   # inner/outer edge of one frame
        out.append(q)
    return out


def fit(pos, slope, span):
    """Slope as a linear function of position, with outliers dropped. Falls back to a constant."""
    pos, slope = np.asarray(pos, float), np.asarray(slope, float)
    keep = np.abs(slope - np.median(slope)) < 0.12
    pos, slope = pos[keep], slope[keep]
    if len(pos) < 8 or np.ptp(pos) < 0.35 * span: return float(np.median(slope)), 0.0
    for _ in range(2):
        b, a = np.polyfit(pos, slope, 1); r = slope - (a + b * pos); ok = np.abs(r) <= 2.5 * (r.std() + 1e-6)
        if ok.all() or ok.sum() < 8: break
        pos, slope = pos[ok], slope[ok]
    return float(a), float(b)


def skew(rgb):
    """How far the ruled frames are from level and upright (0 is perfect), and how many were found."""
    qs = panels(cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY))
    if len(qs) < 4: return None, len(qs)
    e = []
    for q in qs:
        e += [abs((q[1][1] - q[0][1]) / (q[1][0] - q[0][0])), abs((q[2][1] - q[3][1]) / (q[2][0] - q[3][0])),
              abs((q[3][0] - q[0][0]) / (q[3][1] - q[0][1])), abs((q[2][0] - q[1][0]) / (q[2][1] - q[1][1]))]
    return float(np.mean(e)), len(qs)


def straighten(rgb):
    """Straighten, then keep the result only if the frames really did get squarer."""
    if np.percentile(cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY), 60) >= 236: return rgb, False   # a flat scan, not a photograph
    before, n0 = skew(rgb)
    if before is None or before < 0.03: return rgb, False
    out, ok = _straighten(rgb)
    if not ok: return rgb, False
    after, n1 = skew(out)
    if after is None or n1 < 0.7 * n0 or after > 0.65 * before: return rgb, False
    return out, True


def _straighten(rgb):
    """Undo camera tilt and perspective, using the ruled frames' own edges.

    Horizontal frame edges should be level and vertical ones upright. The slope of
    each family is fitted as a function of position, which gives the four sides of
    the sheet as the camera saw it; those are then mapped to a rectangle. Nothing
    is cropped. Returns (image, done)."""
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY); h, w = gray.shape
    qs = panels(gray)
    if len(qs) < 4: return rgb, False
    xc, yc = w / 2, h / 2; hp, hs, vp, vs = [], [], [], []
    for q in qs:
        for p0, p1 in ((q[0], q[1]), (q[3], q[2])):
            m = (p1[1] - p0[1]) / (p1[0] - p0[0]); hs.append(m); hp.append(p0[1] + m * (xc - p0[0]))
        for p0, p1 in ((q[0], q[3]), (q[1], q[2])):
            n = (p1[0] - p0[0]) / (p1[1] - p0[1]); vs.append(n); vp.append(p0[0] + n * (yc - p0[1]))
    a, b = fit(hp, hs, h); c, d = fit(vp, vs, w)
    mt, mb, nl, nr = a, a + b * h, c, c + d * w
    yt, yb = -abs(mt) * xc, h + abs(mb) * xc; xl, xr = -abs(nl) * yc, w + abs(nr) * yc
    def cross(y0, m, x0, n):             # y = y0 + m (x - xc)  meets  x = x0 + n (y - yc)
        y = (y0 + m * (x0 - n * yc - xc)) / (1 - m * n); return [x0 + n * (y - yc), y]
    src = np.array([cross(yt, mt, xl, nl), cross(yt, mt, xr, nr), cross(yb, mb, xr, nr), cross(yb, mb, xl, nl)], np.float32)
    box = np.array([[0, 0], [w, 0], [w, h], [0, h]], np.float32)
    if np.abs(src - box).max() < 0.012 * max(w, h): return rgb, False      # already square to the camera
    if np.abs(src - box).max() > 0.45 * max(w, h): return rgb, False       # the fit is not believable
    W = int(round((np.linalg.norm(src[1] - src[0]) + np.linalg.norm(src[2] - src[3])) / 2))
    Hh = int(round((np.linalg.norm(src[3] - src[0]) + np.linalg.norm(src[2] - src[1])) / 2))
    M = cv2.getPerspectiveTransform(src, np.array([[0, 0], [W, 0], [W, Hh], [0, Hh]], np.float32))
    paper = int(np.percentile(gray, 80))
    return cv2.warpPerspective(rgb, M, (W, Hh), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=(paper,) * 3), True


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
