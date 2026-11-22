#!/usr/bin/env python3
"""Bundle the original scans for a hosted copy that limits the number of files.

    python3 tools/pack_hosted.py OUT_DIR

Writes OUT_DIR/packs/p0.jpg ... (each a plain concatenation of plates/NNN.jpg)
and OUT_DIR/assets/pack.js, an index of where each scan sits. A page that loads
pack.js before app.js reads the scans from the packs instead of from plates/.
The repository itself does not use this; it serves plates/ directly.
"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIMIT = 9_000_000

def main():
    out = sys.argv[1]
    os.makedirs(os.path.join(out, "packs"), exist_ok=True); os.makedirs(os.path.join(out, "assets"), exist_ok=True)
    files, at, buf = [], [], b""
    def flush():
        nonlocal buf
        name = "packs/p%d.jpg" % len(files)
        open(os.path.join(out, name), "wb").write(buf); files.append(name); buf = b""
    for i in range(448):
        data = open(os.path.join(ROOT, "plates", "%03d.jpg" % i), "rb").read()
        if buf and len(buf) + len(data) > LIMIT: flush()
        at.append([len(files), len(buf), len(data)]); buf += data
    flush()
    open(os.path.join(out, "assets", "pack.js"), "w").write("window.DUNE_PACK=" + json.dumps(dict(files=files, at=at), separators=(",", ":")) + ";\n")
    print(len(files), "packs")

if __name__ == "__main__":
    main()
