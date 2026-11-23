"""Find the printed grid of frames on a storyboard sheet.

The production book's storyboard sheets are pre-printed: three columns of ruled
frames, each with a caption strip beneath. Because the grid is printed, it is the
same on every sheet, so the camera's view of a sheet can be recovered by fitting
one homography from the ideal grid to the frames that can be found in the image.
That gives every frame's position, including ones the detector missed.

Plane units: one frame is 1 wide and 1/ASPECT tall. Columns repeat every PITCH_X,
rows every PITCH_Y.
"""
import cv2, numpy as np

ASPECT = 2.364    # frame width / height, measured over 342 frames
PITCH_X = 1.059   # column pitch / frame width, measured
PITCH_Y = 1.371   # row pitch / frame height, measured


def order(q):
    q = q.reshape(4, 2).astype(np.float32); s = q.sum(1); d = q[:, 0] - q[:, 1]
    return np.array([q[s.argmin()], q[d.argmax()], q[s.argmax()], q[d.argmin()]], np.float32)  # tl tr br bl


def panels(gray):
    """Ruled frames found directly in the image, as quadrilaterals (tl, tr, br, bl)."""
    h, w = gray.shape
    bs = max(15, (w // 40) | 1)
    thr = cv2.adaptiveThreshold(cv2.GaussianBlur(gray, (3, 3), 0), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, bs, 8)
    thr = cv2.dilate(thr, np.ones((3, 3), np.uint8))
    cnts, _ = cv2.findContours(thr, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    out = []
    for c in cnts:
        a = cv2.contourArea(c)
        if a < 0.006 * h * w or a > 0.45 * h * w: continue
        p = cv2.approxPolyDP(c, 0.02 * cv2.arcLength(c, True), True)
        if len(p) != 4 or not cv2.isContourConvex(p): continue
        q = order(p); ww = (np.linalg.norm(q[1] - q[0]) + np.linalg.norm(q[2] - q[3])) / 2
        hh = (np.linalg.norm(q[3] - q[0]) + np.linalg.norm(q[2] - q[1])) / 2
        if hh < 1 or not 1.4 < ww / hh < 3.6: continue
        c0 = q.mean(0)
        if any(np.linalg.norm(c0 - o.mean(0)) < 0.25 * hh for o in out): continue   # inner/outer edge of one frame
        out.append(q)
    return out


def cell(c, r):
    """Corners of frame (c, r) in plane units."""
    x, y, h = c * PITCH_X, r * PITCH_Y / ASPECT, 1 / ASPECT
    return np.array([[x, y], [x + 1, y], [x + 1, y + h], [x, y + h]], np.float32)


def apply(H, pts):
    p = np.c_[np.asarray(pts, np.float64), np.ones(len(pts))] @ H.T
    return (p[:, :2] / p[:, 2:3]).astype(np.float32)


def fit(gray):
    """Returns (H plane->image, {(c, r): quad found}, error) or None. Needs three frames."""
    qs = panels(gray)
    if len(qs) < 3: return None
    width = np.median([np.linalg.norm(q[1] - q[0]) for q in qs])
    seed = min(qs, key=lambda q: np.linalg.norm(q.mean(0) - np.mean([p.mean(0) for p in qs], 0)))
    u = (seed[1] - seed[0]) * PITCH_X; v = (seed[3] - seed[0]) * PITCH_Y           # one column across, one row down
    B = np.linalg.inv(np.c_[u, v])
    idx = [tuple(np.round(B @ (q[0] - seed[0])).astype(int)) for q in qs]
    H = None
    for _ in range(3):
        cells = {}
        for q, k in zip(qs, idx): cells.setdefault(k, q)
        if len(cells) < 3: return None
        src = np.concatenate([cell(*k) for k in cells]); dst = np.concatenate(list(cells.values()))
        H, mask = cv2.findHomography(src, dst, cv2.RANSAC, 0.06 * width)
        if H is None: return None
        Hi = np.linalg.inv(H)
        new = []
        for q in qs:                                                                  # re-index every frame with the fitted grid
            p = apply(Hi, [q[0]])[0]; new.append((int(round(p[0] / PITCH_X)), int(round(p[1] * ASPECT / PITCH_Y))))
        if new == idx: break
        idx = new
    err = float(np.median(np.linalg.norm(apply(H, src) - dst, axis=1)) / width)
    if err > (0.05 if len(cells) >= 4 else 0.025): return None      # three frames must agree closely
    return H, cells, err


def measure(grays):
    """Frame aspect and grid pitches measured across many sheets (medians)."""
    asp, px, py = [], [], []
    for g in grays:
        qs = panels(g)
        if len(qs) < 4: continue
        for q in qs:
            w = (np.linalg.norm(q[1] - q[0]) + np.linalg.norm(q[2] - q[3])) / 2; h = (np.linalg.norm(q[3] - q[0]) + np.linalg.norm(q[2] - q[1])) / 2
            asp.append(w / h)
            for o in qs:
                d = o[0] - q[0]
                if 0.8 * w < d[0] < 1.5 * w and abs(d[1]) < 0.3 * h: px.append(d[0] / w)
                if 1.2 * h < d[1] < 2.6 * h and abs(d[0]) < 0.3 * w: py.append(d[1] / h)
    return float(np.median(asp)), float(np.median(px)), float(np.median(py)), len(asp), len(px), len(py)


def rectify(rgb, H, cells):
    """Undo the camera's view of the sheet. Returns (image, changed)."""
    h, w = rgb.shape[:2]
    s = float(np.median([np.linalg.norm(q[1] - q[0]) for q in cells.values()]))
    Hi = np.linalg.inv(H); S = np.diag([s, s, 1.0])
    box = np.array([[0, 0], [w, 0], [w, h], [0, h]], np.float32)
    c = apply(S @ Hi, box); lo, hi = c.min(0), c.max(0)
    if (hi - lo).prod() > 1.8 * w * h or (hi - lo).min() < 50:                 # a wild fit: do nothing
        return rgb, False
    q = c - lo; W, Hh = int(round(hi[0] - lo[0])), int(round(hi[1] - lo[1]))
    square = np.array([[0, 0], [W, 0], [W, Hh], [0, Hh]], np.float32)
    if np.abs(q - square).max() < 0.012 * max(W, Hh): return rgb, False        # already square to the camera
    T = np.array([[1, 0, -lo[0]], [0, 1, -lo[1]], [0, 0, 1.0]])
    paper = int(np.percentile(cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY), 80))
    return cv2.warpPerspective(rgb, T @ S @ Hi, (W, Hh), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=(paper,) * 3), True


def edges(gray):
    """Local-minimum image and paper level, for testing whether a ruled line runs where the grid says."""
    k = max(3, int(0.012 * gray.shape[1]) | 1)
    return cv2.erode(gray, np.ones((k, k), np.uint8)), float(np.percentile(gray, 80))


def ruled(lo, paper, quad, n=40):
    """True if every side of `quad` follows a dark line. Each side may sit up to 5% of a frame
    width off the fitted position: frame numbers printed beside the top-left corner get merged
    into the detected frame and pull the fit slightly wide on that side."""
    h, w = lo.shape; t = np.linspace(0.08, 0.92, n)[:, None]
    across = (quad[1] - quad[0]) * 0.0125; down = (quad[3] - quad[0]) * 0.03
    for a, b, step in ((0, 1, down), (1, 2, across), (3, 2, down), (0, 3, across)):
        best = 0.0
        for k in range(-4, 5):
            p = np.rint(quad[a] * (1 - t) + quad[b] * t + step * k).astype(int)
            ok = (p[:, 0] >= 0) & (p[:, 0] < w) & (p[:, 1] >= 0) & (p[:, 1] < h)
            if ok.sum() >= n * 0.9: best = max(best, float((lo[p[ok, 1], p[ok, 0]] < paper - 45).mean()))
        if best < 0.5: return False
    return True


def frames(gray, H, cells):
    """Every frame of the printed grid that is really on the sheet: [(c, r, quad)], in reading order."""
    lo, paper = edges(gray); ks = list(cells); out = []
    for r in range(min(k[1] for k in ks) - 4, max(k[1] for k in ks) + 5):
        for c in range(min(k[0] for k in ks) - 3, max(k[0] for k in ks) + 4):
            q = apply(H, cell(c, r))
            if ruled(lo, paper, q): out.append((c, r, q))
    return out


def locate(gray):
    """A grid that can be trusted. Returns (H, cells, frames) or None.

    Trusted means: at least four detected frames in two or more rows and columns agree on one
    grid, most of them sit on ruled lines where the grid says, and the frames the grid predicts
    between them are really there. Pasted-up collages and sheets with too few clean frames fail."""
    f = fit(gray)
    if f is None: return None
    H, cells, err = f
    cols, rows = sorted({k[0] for k in cells}), sorted({k[1] for k in cells})
    if len(cells) < 4 or len(cols) < 2 or len(rows) < 2: return None
    fr = frames(gray, H, cells); have = {(c, r) for c, r, _ in fr}
    if sum(1 for k in cells if k in have) < 0.75 * len(cells): return None
    inside = [(c, r) for c in range(cols[0], cols[-1] + 1) for r in range(rows[0], rows[-1] + 1)]
    if sum(1 for k in inside if k in have) < 0.7 * len(inside): return None
    return H, cells, fr


def quads(gray, work=1600):
    """Ruled frames found one at a time, with no grid: [quad] in reading order, in image pixels.

    For sheets the grid cannot be fitted to (crops, strips, pasted-up collages). Each dark
    connected shape's convex hull is tested: it must be a four-sided figure with a frame's
    proportions whose four sides all follow a dark line. It can miss frames, so callers must
    not treat the result as the whole sheet."""
    f = work / gray.shape[1]
    g = cv2.resize(gray, (work, int(round(gray.shape[0] * f))), interpolation=cv2.INTER_AREA if f < 1 else cv2.INTER_CUBIC)
    h, w = g.shape; lo, paper = edges(g); found = []
    for block, c, grow in ((41, 8, 3), (41, 14, 3), (81, 10, 5), (25, 6, 1)):
        thr = cv2.adaptiveThreshold(cv2.GaussianBlur(g, (3, 3), 0), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, block, c)
        if grow > 1: thr = cv2.dilate(thr, np.ones((grow, grow), np.uint8))
        for cnt in cv2.findContours(thr, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0]:
            if cv2.contourArea(cnt) < 0.004 * h * w: continue
            hull = cv2.convexHull(cnt); area = cv2.contourArea(hull)
            if area > 0.6 * h * w: continue
            for eps in (0.015, 0.025, 0.04):
                q = cv2.approxPolyDP(hull, eps * cv2.arcLength(hull, True), True)
                if len(q) == 4: break
            else: continue
            if not 0.93 < area / max(cv2.contourArea(q), 1) < 1.07: continue
            q = order(q); ww = (np.linalg.norm(q[1] - q[0]) + np.linalg.norm(q[2] - q[3])) / 2; hh = (np.linalg.norm(q[3] - q[0]) + np.linalg.norm(q[2] - q[1])) / 2
            if hh < 20 or not 2.0 < ww / hh < 2.75: continue
            top, bot, lef, rig = (np.linalg.norm(q[1] - q[0]), np.linalg.norm(q[2] - q[3]), np.linalg.norm(q[3] - q[0]), np.linalg.norm(q[2] - q[1]))
            if abs(top - bot) > 0.12 * ww or abs(lef - rig) > 0.15 * hh: continue        # not a rectangle seen nearly square-on
            def angle(a, b, c):
                u, v = a - b, c - b; return np.degrees(np.arccos(np.clip(u @ v / (np.linalg.norm(u) * np.linalg.norm(v)), -1, 1)))
            if any(abs(angle(q[k - 1], q[k], q[(k + 1) % 4]) - 90) > 12 for k in range(4)): continue
            if not ruled(lo, paper, q): continue
            c0 = q.mean(0)
            if any(np.linalg.norm(c0 - o.mean(0)) < 0.3 * hh for o in found): continue
            found.append(q)
    if found:                                                                          # frames on one sheet are one size
        mid = float(np.median([np.linalg.norm(q[1] - q[0]) for q in found]))
        found = [q for q in found if 0.7 * mid < np.linalg.norm(q[1] - q[0]) < 1.4 * mid]
    if not found: return []
    hh = float(np.median([np.linalg.norm(q[3] - q[0]) for q in found]))
    found.sort(key=lambda q: q.mean(0)[1]); rows, cur = [], [found[0]]
    for q in found[1:]:
        if q.mean(0)[1] - cur[-1].mean(0)[1] < 0.5 * hh: cur.append(q)
        else: rows.append(cur); cur = [q]
    rows.append(cur)
    return [q / f for row in rows for q in sorted(row, key=lambda q: q.mean(0)[0])]
