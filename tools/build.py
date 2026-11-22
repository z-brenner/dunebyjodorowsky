#!/usr/bin/env python3
"""Build the site's image set and data file from the source PDF.

    python3 tools/build.py /path/to/Jodorowskys_Dune.pdf

Needs poppler's `pdfimages` and Pillow. Writes plates/, thumbs/ and
assets/data.js at the repository root.
"""
import json, os, subprocess, sys, tempfile, shutil
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import catalog as C

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TH = 260          # thumbnail height in the sprite sheets
SHEET_W = 2340    # sprite sheet width
SHEET_ROWS = 8


def extract(pdf, out):
    subprocess.run(["pdfimages", "-all", pdf, os.path.join(out, "p")], check=True)
    files = sorted(f for f in os.listdir(out) if f.startswith("p-"))
    assert len(files) == 448, len(files)
    return [os.path.join(out, f) for f in files]


def dhash(im, n=12):
    g = im.convert("L").resize((n + 1, n), Image.LANCZOS)
    px = list(g.get_flattened_data())
    bits = 0
    for y in range(n):
        for x in range(n):
            bits = (bits << 1) | (px[y * (n + 1) + x] > px[y * (n + 1) + x + 1])
    return bits


def avg_color(im):
    s = im.convert("RGB").resize((24, 24), Image.LANCZOS)
    px = list(s.get_flattened_data())
    # weight saturated pixels so paper white does not wash everything out
    tot = [0, 0, 0]; wsum = 0
    for r, g, b in px:
        w = (max(r, g, b) - min(r, g, b)) + 12
        tot[0] += r * w; tot[1] += g * w; tot[2] += b * w; wsum += w
    return "#%02x%02x%02x" % tuple(int(t / wsum) for t in tot)


def main():
    pdf = sys.argv[1]
    tmp = tempfile.mkdtemp()
    files = extract(pdf, tmp)
    plates_dir = os.path.join(ROOT, "plates"); thumbs_dir = os.path.join(ROOT, "thumbs")
    os.makedirs(plates_dir, exist_ok=True)
    shutil.rmtree(thumbs_dir, ignore_errors=True); os.makedirs(thumbs_dir)

    rows = {}
    for line in C.ROWS.strip().splitlines():
        i, room, title, credit, who, note = line.split("|", 5)
        rows[int(i)] = dict(room=room, t=title, c=credit, who=[w for w in who.split(",") if w], n=note)
    assert sorted(rows) == list(range(448)), "catalogue must cover every plate"

    seq_of = {}
    for s, ids in C.SEQ.items():
        for i in ids:
            seq_of.setdefault(i, []).append(s)

    rpath = os.path.join(ROOT, "tools", "restored.json")
    restored = json.load(open(rpath)) if os.path.exists(rpath) else {}
    placed = {}
    for label, (plate, sure) in C.ILLUS.items(): placed.setdefault(plate, "s" if sure else "l")
    for sc, ids in C.PLACE.items():
        for k in ids: placed.setdefault(k, "e")
    plates, hashes, thumbs = [], [], []
    for i, f in enumerate(files):
        im = Image.open(f); im.load()
        shutil.copyfile(f, os.path.join(plates_dir, "%03d.jpg" % i))
        w, h = im.size
        apath = os.path.join(ROOT, "art", "%03d.webp" % i)
        t = (Image.open(apath) if str(i) in restored and os.path.exists(apath) else im).convert("RGB")
        if t.size != im.size: tw0, th0 = t.size
        else: tw0, th0 = w, h
        tw = max(1, round(tw0 * TH / th0))
        if tw > 620:  # very wide plates: cap the width, letting height shrink
            tw = 620
        t = t.resize((tw, TH if tw < 620 else max(1, round(th0 * 620 / tw0))), Image.LANCZOS)
        thumbs.append(t); hashes.append(dhash(im))
        r = rows[i]
        p = dict(i=i, w=w, h=h, room=r["room"], t=r["t"], c=r["c"], col=avg_color(im))
        if r["who"]: p["who"] = r["who"]
        if r["n"]: p["n"] = r["n"]
        if i in seq_of: p["seq"] = seq_of[i]
        if i in C.CAP: p["cap"] = list(C.CAP[i])
        if str(i) in restored: r = restored[str(i)]; p["r"] = [r["w"], r["h"], r["did"]]
        if i in placed: p["by"] = placed[i]
        plates.append(p)

    # the same picture in more than one scan: curated groups first, then exact repeats
    parent = list(range(448)); best_of = {}
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for g in C.SAME:
        for k in g[1:]: parent[find(k)] = find(g[0])
        best_of[find(g[0])] = g[0]
    for a in range(448):
        for b in range(a + 1, 448):
            ra, rb = plates[a]["w"] / plates[a]["h"], plates[b]["w"] / plates[b]["h"]
            if abs(ra - rb) / ra > 0.12: continue
            if bin(hashes[a] ^ hashes[b]).count("1") <= 14 and find(a) != find(b):
                keep = best_of.get(find(a), best_of.get(find(b)))
                parent[find(b)] = find(a)
                if keep is not None: best_of[find(a)] = keep
    groups = {}
    for a in range(448): groups.setdefault(find(a), []).append(a)
    for root, g in groups.items():
        if len(g) < 2: continue
        best = best_of.get(root)
        if best is None: best = max(g, key=lambda k: plates[k]["w"] * plates[k]["h"])
        for k in g:
            plates[k]["var"] = [x for x in g if x != k]
            if k != best: plates[k]["dup"] = best

    # pack thumbnails into sprite sheets
    sheets = []; x = y = 0; cur = []; rowh = 0
    def flush():
        nonlocal cur, x, y, rowh
        if not cur: return
        H = y + rowh
        sh = Image.new("RGB", (SHEET_W, H), (12, 10, 14))
        for (i, t, px, py) in cur:
            sh.paste(t, (px, py))
            plates[i]["s"] = [len(sheets), px, py, t.width, t.height]
        name = "s%02d.webp" % len(sheets)
        sh.save(os.path.join(thumbs_dir, name), "WEBP", quality=74, method=6)
        sheets.append([name, SHEET_W, H]); cur = []; x = y = rowh = 0
    nrow = 0
    for i, t in enumerate(thumbs):
        if x + t.width > SHEET_W:
            x = 0; y += rowh; rowh = 0; nrow += 1
            if nrow == SHEET_ROWS: nrow = 0; flush()
        cur.append((i, t, x, y)); x += t.width; rowh = max(rowh, t.height)
    flush()

    for sc, ids in C.PLACE.items():
        for k in ids: assert "dup" not in plates[k], ("placed plate is a repeat scan", k)
    data = dict(
        plates=plates, sheets=sheets, credits=C.CREDITS,
        chapters=[dict(id=a, title=b, a=c, b=d, key=e, text=f) for a, b, c, d, e, f in C.CHAPTERS],
        place={str(k): v for k, v in C.PLACE.items()},
        groups=[dict(id=a, title=b, text=c, kinds=d) for a, b, c, d in C.GROUPS],
    )
    os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    with open(os.path.join(ROOT, "assets", "data.js"), "w") as fh:
        fh.write("window.DUNE=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n")
    shutil.rmtree(tmp)
    dups = sum(1 for p in plates if "dup" in p)
    print("plates 448 | sheets %d | duplicate scans %d | unique %d" % (len(sheets), dups, 448 - dups))

if __name__ == "__main__":
    main()
