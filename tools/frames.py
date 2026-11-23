#!/usr/bin/env python3
"""Cut the storyboard sheets into single frames.

    python3 tools/frames.py

Reads art/NNN.webp for every storyboard sheet, finds the book's printed grid of
frames (tools/grid.py) and, where the grid can be trusted, writes each frame with
its caption strip to frames/NNN-KK.webp, squared up and at one size. Writes
tools/frames.json: how many frames each sheet gave. Sheets whose grid cannot be
confirmed are left whole. Needs numpy, opencv and Pillow.
"""
import json, os, shutil, sys
import cv2, numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import catalog as C, grid as G

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = 900              # width of every frame image
MARGIN = 0.035       # paper kept around the frame, in frame widths


def main():
    rows = {int(l.split("|")[0]): l.split("|")[1] for l in C.ROWS.strip().splitlines()}
    skip = {k for g in C.SAME for k in g[1:]}
    out_dir = os.path.join(ROOT, "frames"); shutil.rmtree(out_dir, ignore_errors=True); os.makedirs(out_dir)
    height = 1 / G.ASPECT; pitch = G.PITCH_Y / G.ASPECT                      # frame height and row pitch, in frame widths
    scale = W / (1 + 2 * MARGIN); Hh = int(round((pitch + MARGIN - 0.01) * scale))
    log = {}
    for i in range(448):
        path = os.path.join(ROOT, "art", "%03d.webp" % i)
        if rows[i] != "board" or i in skip or not os.path.exists(path): continue
        rgb = np.array(Image.open(path).convert("RGB")); gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        found = G.locate(gray)
        if found is None: continue
        Hm, cells, frames = found; n = 0
        for c, r, quad in frames:
            x, y = c * G.PITCH_X, r * pitch
            if np.percentile(gray[cv2.fillConvexPoly(np.zeros(gray.shape, np.uint8), np.rint(G.apply(Hm, [[x + .06, y + .03], [x + .94, y + .03], [x + .94, y + height - .03], [x + .06, y + height - .03]])).astype(np.int32), 1) == 1], 2) > 190:
                continue                                                         # a ruled frame nobody drew in
            src = G.apply(Hm, [[x - MARGIN, y - MARGIN], [x + 1 + MARGIN, y - MARGIN], [x + 1 + MARGIN, y + pitch - 0.01], [x - MARGIN, y + pitch - 0.01]])
            M = cv2.getPerspectiveTransform(src, np.array([[0, 0], [W, 0], [W, Hh], [0, Hh]], np.float32))
            img = cv2.warpPerspective(rgb, M, (W, Hh), flags=cv2.INTER_AREA if np.linalg.norm(src[1] - src[0]) > W else cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
            n += 1
            Image.fromarray(img).save(os.path.join(out_dir, "%03d-%02d.webp" % (i, n)), "WEBP", quality=78, method=5)
        if n: log[str(i)] = n
    json.dump(dict(w=W, h=Hh, n=log), open(os.path.join(ROOT, "tools", "frames.json"), "w"), separators=(",", ":"))
    print("sheets cut: %d | frames: %d | each %d x %d" % (len(log), sum(log.values()), W, Hh))

if __name__ == "__main__":
    main()
