#!/usr/bin/env python3
"""Cut the storyboard sheets into single frames.

    python3 tools/frames.py

Reads art/NNN.webp for every storyboard sheet and finds the book's printed grid of
frames (tools/grid.py). The grid says roughly where each frame is; this tool then
looks for that frame's own four ruled lines close by and cuts to those, because a
photographed page curls and a flat grid drifts by a few percent at its far rows.

Each frame is written with its caption strip to frames/NNN-KK.webp at one size.
A frame the photograph cuts off is kept and recorded as partial. A drawn frame
whose own lines cannot be found is still kept, cut where the grid says it is and
recorded as estimated, so no drawing drops out of the sequence. A sheet is cut
only if at least half its frames are found whole; otherwise it is left as a sheet.
Writes tools/frames.json. Needs numpy, opencv and Pillow.
"""
import json, os, shutil, sys
import cv2, numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import catalog as C, grid as G

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = 900                                   # width of every frame image
MARGIN = 0.035                            # paper kept around the frame, in frame widths
S = 1000                                  # working scale: one frame width in pixels
PAD_X, PAD_Y = 0.12, 0.07                 # how far around the predicted frame to look
FH = 1 / G.ASPECT                         # frame height, in frame widths
PITCH = G.PITCH_Y / G.ASPECT              # row pitch, in frame widths
CAPTION = PITCH - FH                      # caption strip height
NOT_STANDARD = {400}                      # checked by eye: a pasted-up strip of frames with no caption rows
NO_ESTIMATES = {91}                       # checked by eye: the bottom row is one wide box holding a typed colour legend, not frames


def peaks(profile, lo, hi, least=0.5):
    """Positions in [lo, hi) where a ruled line crosses: local maxima of the profile above `least`."""
    lo, hi = max(lo, 1), min(hi, len(profile) - 1); out = []
    for x in range(lo, hi):
        if profile[x] >= least and profile[x] >= profile[x - 1] and profile[x] > profile[x + 1]: out.append(x)
    return out


def pair(a, b, want, expect_a, slack):
    """The (a, b) pair closest to `want` apart, then nearest to where the grid expects it.
    Distance apart comes first so a neighbouring frame's edge, one gutter further on, loses."""
    best, score = None, None
    for p in a:
        for q in b:
            if abs((q - p) - want) > slack: continue
            sc = abs((q - p) - want) + 0.3 * abs(p - expect_a)
            if score is None or sc < score: best, score = (p, q), sc
    return best


def find(patch):
    """The frame's own lines in a patch warped around the grid's prediction.

    Returns (left, right, top, bottom, missing) in patch pixels. `missing` lists the sides
    whose line could not be found; their positions fall back to the grid's."""
    gray = cv2.cvtColor(patch, cv2.COLOR_RGB2GRAY); paper = float(np.percentile(gray, 80))
    dark = (gray < paper - 45).astype(np.uint8)
    L, T = int(PAD_X * S), int(PAD_Y * S); R, B = L + S, T + int(FH * S); h = B - T
    wide = cv2.dilate(dark, np.ones((13, 1), np.uint8))                 # tolerate a little slope
    rows = wide[:, L + int(.15 * S):L + int(.85 * S)].mean(1)
    tb = pair(peaks(rows, T - 55, T + 55), peaks(rows, B - 60, B + 60), h, T, 0.09 * h)
    missing = []
    if tb: top, bottom = tb
    else:
        t = peaks(rows, T - 55, T + 55); b = peaks(rows, B - 60, B + 60)
        if t: top = min(t, key=lambda v: abs(v - T)); bottom = top + h; missing.append("bottom")
        elif b: bottom = min(b, key=lambda v: abs(v - B)); top = bottom - h; missing.append("top")
        else: top, bottom = T, B; missing += ["top", "bottom"]
    tall = cv2.dilate(dark, np.ones((1, 13), np.uint8))
    cols = tall[top + int(.3 * h):top + int(.9 * h)].mean(0)            # below the frame number printed at top left
    lr = pair(peaks(cols, L - 100, L + 100), peaks(cols, R - 100, R + 100), S, L, 0.06 * S)
    if lr: left, right = lr
    else:
        l = peaks(cols, L - 100, L + 100); r = peaks(cols, R - 100, R + 100)
        if l: left = min(l, key=lambda v: abs(v - L)); right = left + S; missing.append("right")
        elif r: right = min(r, key=lambda v: abs(v - R)); left = right - S; missing.append("left")
        else: left, right = L, R; missing += ["left", "right"]
    return left, right, top, bottom, missing


def main():
    rows = {int(l.split("|")[0]): l.split("|")[1] for l in C.ROWS.strip().splitlines()}
    skip = {k for g in C.SAME for k in g[1:]}
    out_dir = os.path.join(ROOT, "frames"); shutil.rmtree(out_dir, ignore_errors=True); os.makedirs(out_dir)
    Hh = int(round((FH + CAPTION + MARGIN - 0.01) * W / (1 + 2 * MARGIN)))
    pw, ph = int((1 + 2 * PAD_X) * S), int((PITCH + 2 * PAD_Y) * S)
    log, partial, estimated, left_whole = {}, {}, {}, {}
    for i in range(448):
        path = os.path.join(ROOT, "art", "%03d.webp" % i)
        if rows[i] != "board" or i in skip or not os.path.exists(path): continue
        if i in NOT_STANDARD: left_whole[i] = "not the book's standard sheet"; continue
        rgb = np.array(Image.open(path).convert("RGB"))
        found = G.locate(cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY))
        if found is None: left_whole[i] = "no grid"; continue
        Hm, cells, located = found
        cs = [c for c, r, _ in located]; rs = [r for c, r, _ in located]
        outward = lambda c, r: ({"left"} if c == min(cs) else set()) | ({"right"} if c == max(cs) else set()) | ({"top"} if r == min(rs) else set()) | ({"bottom"} if r == max(rs) else set())
        keep = []
        for c, r, quad in located:
            x, y = c * G.PITCH_X, r * PITCH
            src = G.apply(Hm, [[x - PAD_X, y - PAD_Y], [x + 1 + PAD_X, y - PAD_Y], [x + 1 + PAD_X, y + PITCH + PAD_Y], [x - PAD_X, y + PITCH + PAD_Y]])
            patch = cv2.warpPerspective(rgb, cv2.getPerspectiveTransform(src, np.array([[0, 0], [pw, 0], [pw, ph], [0, ph]], np.float32)), (pw, ph), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
            l, rt, t, b, missing = find(patch)
            rough = len(missing) > 1 or not set(missing) <= outward(c, r)
            if rough and i in NO_ESTIMATES: continue
            if rough:                                                                    # its own lines were not found: keep the
                l, t = int(PAD_X * S), int(PAD_Y * S); rt, b = l + S, t + int(FH * S)    # drawing, cut where the grid says it is
                missing = []
            inside = cv2.cvtColor(patch[t + 22:b - 22, l + 40:rt - 40], cv2.COLOR_RGB2GRAY).astype(np.float32)
            # ink is darker than the paper right around it; a photograph's shading is not. One small mark counts.
            drawn = inside.size > 0 and int((inside < cv2.blur(inside, (61, 61)) - 45).sum()) >= 60
            fw = rt - l; m = int(MARGIN * fw); cap = int((CAPTION - 0.01) * fw * (b - t) / (FH * fw))
            x0, x1, y0, y1 = l - m, rt + m, t - m, b + cap
            canvas = np.full((max(y1, ph) - min(y0, 0), max(x1, pw) - min(x0, 0), 3), 255, np.uint8)
            ox, oy = -min(x0, 0), -min(y0, 0); canvas[oy:oy + ph, ox:ox + pw] = patch
            crop = canvas[y0 + oy:y1 + oy, x0 + ox:x1 + ox]
            keep.append((cv2.resize(crop, (W, Hh), interpolation=cv2.INTER_AREA), bool(missing), drawn, rough))
        whole = sum(1 for _, p, _, rg in keep if not p and not rg)                      # ruled frames found whole, drawn in or not
        if whole < 0.5 * len(located) or whole < 3:
            left_whole[i] = "%d of %d frames found whole" % (whole, len(located)); continue
        keep = [(img, p, rg) for img, p, drawn, rg in keep if drawn]                    # a ruled frame nobody drew in is not a shot
        if len(keep) < 2: left_whole[i] = "fewer than two drawn frames"; continue
        for n, (img, p, rg) in enumerate(keep, 1):
            Image.fromarray(img).save(os.path.join(out_dir, "%03d-%02d.webp" % (i, n)), "WEBP", quality=78, method=5)
            if p: partial.setdefault(str(i), []).append(n)
            if rg: estimated.setdefault(str(i), []).append(n)
        log[str(i)] = len(keep)
    json.dump(dict(w=W, h=Hh, n=log, partial=partial, estimated=estimated), open(os.path.join(ROOT, "tools", "frames.json"), "w"), separators=(",", ":"))
    print("sheets cut: %d | frames: %d (%d partial, %d estimated) | each %d x %d" % (len(log), sum(log.values()), sum(len(v) for v in partial.values()), sum(len(v) for v in estimated.values()), W, Hh))
    print("left whole:", left_whole)

if __name__ == "__main__":
    main()
