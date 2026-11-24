"""The opening shot, animated from its storyboard.

Sequence 1 of the storyboard is drawn as one continuous shot in 24 frames (plates 126 and 223).
In most frames a small ruled rectangle marks the part of the picture the camera travels into,
and the next frame shows what is found there. This script makes that journey: it pushes into
each frame toward its rectangle while the next frame's drawing fades up inside it.

The drawings are the storyboard's. The movement between them, the timing, the titles and the
sound are this edition's. Nothing here is footage.

usage: opening.py <realesr-general-x4v3.pth> <fonts dir> <out dir> [--preview]
"""
import math, os, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frames')) else '/home/user/dunebyjodorowsky'
W, H, FPS = 1920, 1080, 24
PW, PH, PY = 1920, 800, 96                       # the picture: a 2.4 to 1 window, with room for the caption below
PAPER = np.array([226, 236, 240], np.float32)    # BGR: warm paper
RATE = 0.40                                      # camera speed: natural log of magnification gained per second
MIN_T = 2.6

# Each frame: (plate index, frame number, where the camera goes, the storyboard's English caption).
# "Where the camera goes" is the ruled rectangle as (centre x, centre y, width), in fractions of the
# frame, read off the drawing by hand. Where a frame has no rectangle, ('to', point here, point in the
# next frame, magnification) says which detail carries over, which is this edition's reading.
SHOT = [
    (125, 1, ('to', (.472, .471), (.528, .471), 10.0), 'Galaxy approaching'),
    (125, 2, ('to', (.528, .471), (.453, .506), 1.9), 'Closer'),
    (125, 3, ('to', (.453, .506), (.5, .5), 4.0), ''),
    (125, 4, (.502, .506, .108), 'Into the galaxy – pure white'),
    (125, 5, ('to', (.5, .5), (.5, .5), 3.0), 'Millions of stars – a blaze of light and color – dissolve through to…'),
    (125, 6, (.513, .503, .186), 'Nebulae'),
    (125, 7, (.501, .500, .130), 'Into a shadow – cluster of planets appears'),
    (125, 8, (.507, .497, .189), 'Closer on planets – space battlefield becomes visible'),
    (125, 9, (.503, .497, .153), 'Passing dead Guild convoy – approaching man'),
    (125, 10, (.498, .491, .259), 'Passing dead smuggler'),
    (125, 11, (.508, .503, .158), 'Passing smuggler’s hand – full of blue spice (writhing) – approaching Sardaukar ship…'),
    (125, 12, (.493, .494, .288), 'Closer to pirate ship – spice spilled out – Sardaukar shuttles moving around it'),
    (222, 1, (.508, .491, .262), 'Closer on Sardaukar shuttles – crawling on the wreck – huge mounds of spice'),
    (222, 2, (.502, .497, .132), 'Past Sardaukars – Guild convoy in distance'),
    (222, 3, (.498, .491, .193), 'Toward the Guild convoy'),
    (222, 4, ('to', (.267, .380), (.5, .5), 3.5), 'Past the convoy'),
    (222, 5, (.501, .511, .233), 'Through interstellar space – 2 observation probes cross frame – toward asteroid cluster'),
    (222, 6, ('to', (.5, .5), (.5, .5), 3.0), 'Through asteroids'),
    (222, 7, ('to', (.5, .5), (.5, .5), 3.0), 'Past an asteroid with factories – toward a cluster of planets'),
    (222, 8, ('to', (.608, .454), (.5, .5), 4.0), 'Through planetary cluster – planets connected by bridges of light – toward a distant dark sun'),
    (222, 9, (.499, .494, .182), 'Approaching dark sun'),
    (222, 10, (.504, .494, .224), 'Closer to sun – golden planet orbiting'),
    (222, 11, (.496, .494, .337), 'Toward golden planet'),
    (222, 12, (.499, .494, .205), 'Closer'),
]


CROP = {(125, 6): (92, 29, 896, 374)}            # this frame was cut off-centre: its own border is further right


def window(spec):
    """The part of the frame the next frame shows: (left, top, width) in fractions of the frame."""
    if spec[0] == 'to':
        _, a, b, z = spec
        return a[0] - b[0] / z, a[1] - b[1] / z, 1 / z
    cx, cy, w = spec
    return cx - w / 2, cy - w / 2, w


def inner(gray):
    dark = gray < 120
    rows = np.where(dark.mean(1) > 0.5)[0]; cols = np.where(dark[:400].mean(0) > 0.5)[0]
    top = max([r for r in rows if r < 80] or [22]) + 4; bot = min([r for r in rows if 300 < r < 420] or [380]) - 4
    left = max([c for c in cols if c < 80] or [22]) + 4; right = min([c for c in cols if 820 < c < 880] or [864]) - 4
    return left, top, right, bot


def load_frames(model_path):
    """Each frame's drawing, without its ruled border or caption, enlarged, as ink density (0 paper, 1 black)."""
    sys.path.insert(0, os.path.join(REPO, 'tools'))
    import sr
    model = sr.load(model_path, 32)
    out = []
    for pl, k, _, _ in SHOT:
        bgr = cv2.imread(os.path.join(REPO, 'frames', f'{pl}-{k:02d}.webp'))
        l, t, r, b = CROP.get((pl, k)) or inner(cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY))
        crop = bgr[t:b, l:r]
        up = sr.upscale(model, cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
        up = cv2.cvtColor(up, cv2.COLOR_RGB2BGR)
        soft = cv2.resize(crop, (up.shape[1], up.shape[0]), interpolation=cv2.INTER_LANCZOS4)
        mix = cv2.addWeighted(up, 0.6, soft, 0.4, 0)
        g = cv2.cvtColor(cv2.resize(mix, (PW * 2, PH * 2), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY).astype(np.float32)
        paper = np.percentile(g, 85)
        ink = np.clip(1 - g / paper, 0, 1)
        ink[ink < 0.035] = 0                                     # paper noise is not ink
        out.append(ink)
        print('frame', pl, k, crop.shape, 'paper', round(float(paper)), flush=True)
    return out


def place(ink, left, top, width):
    """Draw a frame so that its part (left, top, width) fills the picture. Parts outside the frame are paper."""
    s = ink.shape[1] / PW                                         # source pixels per picture pixel at magnification 1
    z = 1 / width
    M = np.float32([[z / s, 0, -left * PW * z], [0, z / s, -top * PH * z]])
    return cv2.warpAffine(ink, M, (PW, PH), flags=cv2.INTER_AREA if z < s else cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=0)


def smooth(a, b, x):
    t = min(1, max(0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def font(d, name, size):
    return ImageFont.truetype(os.path.join(d, name), size)


def text_layer(lines, fonts_dir, y0=None, gap=18, fill=(236, 226, 204)):
    """lines: [(text, font file, size, colour or None)] centred. Returns BGR float image and alpha."""
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    sizes = [d.textbbox((0, 0), t, font=font(fonts_dir, f, s)) for t, f, s, _ in lines]
    total = sum(b[3] - b[1] for b in sizes) + gap * (len(lines) - 1)
    y = (H - total) // 2 if y0 is None else y0
    for (t, f, s, c), b in zip(lines, sizes):
        d.text(((W - (b[2] - b[0])) // 2 - b[0], y - b[1]), t, font=font(fonts_dir, f, s), fill=(c or fill) + (255,))
        y += b[3] - b[1] + gap
    a = np.asarray(im).astype(np.float32)
    return a[:, :, 2::-1].copy(), a[:, :, 3:4] / 255


def wrap(text, fnt, width):
    d = ImageDraw.Draw(Image.new('RGB', (10, 10))); out, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=fnt) <= width or not cur: cur = t
        else: out.append(cur); cur = w
    return out + [cur] if cur else out


def caption_layer(text, letter, fonts_dir):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = font(fonts_dir, 'CourierPrime.ttf', 34); small = font(fonts_dir, 'CourierPrime-Bold.ttf', 20)
    d.text((60, PY + PH + 30), 'FRAME ' + letter, font=small, fill=(156, 123, 60, 255))
    lines = wrap(text, f, W - 520) if text else []
    y = PY + PH + 24 + (0 if len(lines) > 1 else 20)
    for ln in lines[:3]:
        d.text(((W - d.textlength(ln, font=f)) / 2, y), ln, font=f, fill=(236, 226, 204, 255)); y += 44
    a = np.asarray(im).astype(np.float32)
    return a[:, :, 2::-1].copy(), a[:, :, 3:4] / 255


def main():
    model_path, fonts_dir, out_dir = sys.argv[1:4]
    preview = '--preview' in sys.argv
    os.makedirs(out_dir, exist_ok=True)
    inks = load_frames(model_path)
    wins = [window(s[2]) for s in SHOT]
    durs = [max(MIN_T, math.log(1 / w[2]) / RATE) for w in wins]
    print('seconds per frame:', [round(d, 1) for d in durs], 'shot', round(sum(durs), 1), flush=True)

    HEAD, HOLD, TAIL = 9.0, 1.6, 9.0                              # title, a still look at frame A, end card
    total = HEAD + HOLD + sum(durs) + TAIL
    nframes = int(round(total * FPS))
    caps = [caption_layer(s[3], 'ABCDEFGHIJKLMNOPQRSTUVWX'[i], fonts_dir) for i, s in enumerate(SHOT)]
    gold = (76, 170, 217)[::-1]
    title = text_layer([('DUNE', 'Anton.ttf', 250, gold), ('THE OPENING SHOT', 'CourierPrime-Bold.ttf', 40, None),
                        ('animated from the storyboard’s 24 frames', 'CourierPrime.ttf', 30, None)], fonts_dir, gap=34)
    note = text_layer([('Adapted from the surviving materials of Alejandro Jodorowsky’s unmade film.', 'CourierPrime.ttf', 30, None),
                       ('The drawings are the storyboard’s, by Jean Giraud (Moebius).', 'CourierPrime.ttf', 30, None),
                       ('The camera movement between them was made by software for this edition.', 'CourierPrime.ttf', 30, None),
                       ('It is not footage, and no film was shot.', 'CourierPrime.ttf', 30, None)], fonts_dir, gap=22)
    end = text_layer([('Sequence 1: “un seul plan séquence / one continuous shot”', 'CourierPrime-Bold.ttf', 32, None),
                      ('Storyboard plates 126 and 223. Captions are the storyboard’s own.', 'CourierPrime.ttf', 28, None),
                      ('Where a frame carries no camera mark, the path into the next frame is this edition’s reading.', 'CourierPrime.ttf', 28, None),
                      ('Movement, timing, titles and sound: this edition. Unofficial; the art remains the artists’.', 'CourierPrime.ttf', 28, None)], fonts_dir, gap=22)

    yy, xx = np.mgrid[0:PH, 0:PW].astype(np.float32)
    vig = 1 - 0.34 * np.clip(((xx / PW - .5) ** 2 + ((yy / PH - .5) * PH / PW) ** 2) / 0.30, 0, 1)[..., None] ** 1.5
    rng = np.random.default_rng(7)

    out = os.path.join(out_dir, 'opening-silent.mp4')
    enc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'slow', '-crf', '24' if not preview else '30', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    starts = np.concatenate([[0], np.cumsum(durs)])
    step = 6 if preview else 1
    for n in range(0, nframes, step):
        t = n / FPS
        frame = np.zeros((H, W, 3), np.float32)
        ts = t - HEAD - HOLD                                      # time into the travelling shot
        if t >= HEAD - 1.0 and ts < starts[-1] + 1.2:
            tt = min(max(ts, 0), starts[-1] - 1e-4)
            i = int(np.searchsorted(starts, tt, side='right') - 1); u = (tt - starts[i]) / durs[i]
            l, tp, wd = wins[i]
            cw = wd ** u                                          # the camera's field, as a fraction of frame i
            cl, ct = l * (1 - cw) / (1 - wd), tp * (1 - cw) / (1 - wd)
            ink = place(inks[i], cl, ct, cw)
            mag = 1 / cw                                          # what we fly past goes out of focus and thins, like something near the lens
            sig = 2.6 * max(0.0, mag - 1.5)
            if sig > 0.8:
                f = int(min(8, max(1, sig // 2)))
                small = cv2.resize(ink, (PW // f, PH // f), interpolation=cv2.INTER_AREA) if f > 1 else ink
                small = cv2.GaussianBlur(small, (0, 0), sig / f)
                ink = cv2.resize(small, (PW, PH), interpolation=cv2.INTER_LINEAR) if f > 1 else small
            ink = ink * (1 - 0.4 * smooth(1.5, 5.0, mag)) * (1 - smooth(0.62, 0.98, u))
            if i + 1 < len(inks):
                nxt = place(inks[i + 1], (cl - l) / wd, (ct - tp) / wd, cw / wd)   # the next frame, sitting in its rectangle
                ink = 1 - (1 - ink) * (1 - nxt * smooth(0.30, 0.88, u))
            pic = PAPER * (1 - 0.94 * ink[..., None]) * vig
            pic += rng.normal(0, 2.2, (PH, PW, 1)).astype(np.float32)            # grain
            pic *= 1 + 0.012 * math.sin(t * 9.1) * math.sin(t * 2.3)             # a little lamp flicker
            fade = smooth(HEAD - 1.0, HEAD + 0.6, t) * (1 - smooth(starts[-1] - 0.2, starts[-1] + 1.2, ts))
            frame[PY:PY + PH] = pic * fade
            ci = i if u < 0.86 or i + 1 >= len(caps) else i + 1                  # the caption changes as the next frame takes over
            ca = min(smooth(0.0, 0.10, u), 1 - smooth(0.76, 0.86, u)) if ci == i else smooth(0.86, 0.96, u)
            if i == 0: ca = max(ca, 1 - smooth(0.0, 0.1, u)) if ts <= 0 else ca
            ca *= fade * (1 if ts > -HOLD else 0)
            img, al = caps[ci]; frame = frame * (1 - al * ca) + img * al * ca
        if t < HEAD:
            a1 = smooth(0.3, 1.5, t) * (1 - smooth(3.6, 4.4, t)); a2 = smooth(4.6, 5.4, t) * (1 - smooth(HEAD - 1.4, HEAD - 0.6, t))
            frame = frame * (1 - title[1] * a1) + title[0] * title[1] * a1
            frame = frame * (1 - note[1] * a2) + note[0] * note[1] * a2
        te = t - (HEAD + HOLD + starts[-1])
        if te > 1.0:
            a = smooth(1.0, 2.2, te) * (1 - smooth(TAIL - 1.2, TAIL - 0.2, te))
            frame = frame * (1 - end[1] * a) + end[0] * end[1] * a
        buf = np.clip(frame, 0, 255).astype(np.uint8).tobytes()
        for _ in range(step): enc.stdin.write(buf)
        if n % (FPS * 10) == 0: print('rendered', round(t), 'of', round(total), 's', flush=True)
    enc.stdin.close(); enc.wait()
    print('wrote', out, round(total, 1), 's')


if __name__ == '__main__':
    main()
