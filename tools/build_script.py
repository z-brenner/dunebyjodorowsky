#!/usr/bin/env python3
"""Turn the text transcription of the early-draft screenplay into assets/script.js.

    python3 tools/build_script.py "/path/to/Jodorowskys Dune Early Draft - Text.pdf"

Needs poppler's `pdftotext`. Each scene becomes a list of blocks:
    ["a", text]                   action
    ["d", speaker, text]          dialogue
    ["t", text]                   superimposed title
    ["i", label, number, plate, sure]   illustration slot (plate is null when the
                                  picture is not in the image archive)
    ["p", page]                   page number of the original typescript
"""
import json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import catalog as C

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCENE = re.compile(r"^\s*(\d{1,3})\s*(\(continued\))?\s*$")
PAGE = re.compile(r"^-{6,}\s*p(\d+)\s*-+\s*$")
ILL = re.compile(r"^\[Illustration\s*(?:#(\d+))?\s*:\s*(.*?)\]?\s*$")
SPEAK = re.compile(r"^([A-Z][A-Z0-9 .,'’\-/&]{0,46}?)\s*(\([^)]{1,60}\))?\s*:\s*(.*)$")
SPEAK_DASH = re.compile(r"^([A-Z][A-Z .'’\-]{2,40}?)\s+-\s+(\S.*[a-z].*)$")
NOT_SPEAKER = ("INTERIOR", "EXTERIOR", "DECOR", "TECHNICAL")


def main():
    pdf = sys.argv[1]
    raw = subprocess.run(["pdftotext", "-layout", pdf, "-"], check=True, capture_output=True, text=True).stdout
    lines = raw.replace("\f", "\n").split("\n")
    vocab = set(re.findall(r"[a-z]+(?:-[a-z]+)?", raw.lower()))

    def join(parts):
        out = ""
        for p in parts:
            p = re.sub(r"\s+", " ", p.strip())
            if not p: continue
            m = re.search(r"([A-Za-z]+)-$", out)
            n = re.match(r"([a-z]+)", p)
            if m and n:
                whole, hyph = (m.group(1) + n.group(1)).lower(), (m.group(1) + "-" + n.group(1)).lower()
                out = out[:-1] + p if (whole in vocab or hyph not in vocab) else out + p
            else:
                out = (out + " " + p) if out else p
        return out

    scenes = [dict(n=0, h="Title page and cast", b=[])]
    cur = scenes[0]; para = []

    def flush():
        nonlocal para
        if not para: return
        blocks = []; kind = None; buf = []; who = ""
        def close():
            nonlocal buf, kind
            if buf:
                text = join(buf)
                if text or kind == "d":
                    blocks.append(["d", who, text] if kind == "d" else [kind, text])
            buf = []; kind = None
        for ln in para:
            s = ln.strip()
            m = SPEAK.match(s); d = None if m else SPEAK_DASH.match(s)
            name = (m or d).group(1).strip() if (m or d) else ""
            if name.startswith("TITLE") and m:
                close(); kind = "t"; buf = [m.group(3)]; continue
            if (m or d) and not name.startswith(NOT_SPEAKER) and not name.startswith("TITLE"):
                close(); kind = "d"
                who = name + (" " + m.group(2) if m and m.group(2) else "")
                buf = [m.group(3) if m else d.group(2)]; continue
            if kind is None: kind = "a"
            buf.append(s)
        close()
        # a scene's first all-capitals paragraph is its slug line
        if not cur["b"] and not cur["h"] and blocks and blocks[0][0] == "a" and not re.search(r"[a-z]", blocks[0][1]) and len(blocks[0][1]) < 110:
            cur["h"] = re.sub(r"\s*\.\s+", ". ", blocks.pop(0)[1]).strip()
        cur["b"].extend(blocks); para = []

    for ln in lines:
        m = SCENE.match(ln)
        if m and cur["n"] <= int(m.group(1)) <= cur["n"] + 2:
            flush(); n = int(m.group(1))
            if n != cur["n"]:
                cur = dict(n=n, h="", b=[]); scenes.append(cur)
            continue
        p = PAGE.match(ln)
        if p: flush(); cur["b"].append(["p", int(p.group(1))]); continue
        if ln.strip().startswith("------------"): flush(); continue
        i = ILL.match(ln.strip())
        if i:
            flush(); label = i.group(2).strip()
            plate, sure = C.ILLUS.get(label, (None, True))
            cur["b"].append(["i", label, int(i.group(1)) if i.group(1) else None, plate, sure]); continue
        if not ln.strip(): flush(); continue
        para.append(ln)
    flush()
    for s in scenes:  # drop page marks that trail a scene with nothing after them
        while s["b"] and s["b"][-1][0] == "p": s["b"].pop()

    missing = [k for k in C.ILLUS if not any(b[0] == "i" and b[1] == k for s in scenes for b in s["b"])]
    assert not missing, missing
    out = dict(scenes=scenes, pages=C.SCRIPT_PAGES, reels=C.REEL_SCENES)
    with open(os.path.join(ROOT, "assets", "script.js"), "w") as fh:
        fh.write("window.DUNE_SCRIPT=" + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n")
    nb = sum(len(s["b"]) for s in scenes)
    ill = [b for s in scenes for b in s["b"] if b[0] == "i"]
    print("scenes %d | blocks %d | illustrations %d, %d matched to plates" % (len(scenes) - 1, nb, len(ill), sum(1 for b in ill if b[3] is not None)))
    return scenes

if __name__ == "__main__":
    main()
