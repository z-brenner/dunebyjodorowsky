"""Scenes as film: the surviving pictures cut together under the screenplay's own lines.

Each film is an edit list (EDITS below): which picture, which part of it the camera starts and ends
on, and which lines of the script sit under it. The pictures and the words are the production's.
The edit, the camera movement, the timing, the titles and the sound are this edition's, and each
film says so on screen. Nothing here is footage, and nothing is drawn or generated.

usage: film_scene.py <name> <fonts dir> <out dir> [--preview]
"""
import math, os, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
W, H, FPS = 1920, 1080, 24
PW, PH, PY = 1920, 800, 96                # the picture: a 2.4 to 1 window, with the words below it
ASPECT = PW / PH
MIX = 0.8                                 # seconds for one picture to dissolve into the next
READ = 0.34                               # seconds a word stays up
GOLD, PAPER_TXT, DIM = (217, 170, 76), (236, 226, 204), (156, 123, 60)

# A shot: (source, camera, lines)
#   source  ('plate', index)                    a whole restored plate, art/NNN.webp
#           ('frame', index, n, (l, t, r, b))   a frame cut from a sheet, frames/NNN-KK.webp, and the
#                                               drawing inside its ruled border, in pixels
#   camera  [(x, y, width), ...]  the part of the picture on screen at the start, (middle,) and end,
#           as fractions of the picture: left, top, width. Height follows from the screen's shape.
#   lines   [(speaker or None, text)]  words of the screenplay, unaltered. 'SCENE' marks a slate.
EDITS = {
    'harkonnen': {
        'title': 'THE HARKONNEN CASTLE',
        'sub': 'scenes 39 and 40, from the screenplay and the storyboard',
        'mood': 3,
        'pictures': 'The pictures are the production’s: the storyboard by Jean Giraud (Moebius),',
        'pictures2': 'and one drawing from the illustrated screenplay, artist uncredited in the source.',
        'end': ['Scenes 39 and 40 of the early draft. Plates 28, 284, 26, 50, 140, 443 and 90.',
                'Each line sits under the storyboard frame whose own caption describes it; that pairing is this edition’s.',
                'The pan up the castle and the push toward its head follow the storyboard’s written camera notes.',
                'Edit, movement, timing, titles and sound: this edition. Unofficial; the art remains the artists’.'],
        'shots': [
            (('plate', 27), [(0.0, 0.26, 1.0), (0.2, 0.084, 0.8)],
             [('SCENE', 'Scene 39 – Exterior. Harkonnen castle'), (None, 'Approaches to the sombre castle, bathed in the sound of sea waves.')]),
            (('plate', 283), [(0.08, 0.68, 0.86), (0.08, 0.03, 0.86), (0.315, 0.036, 0.30)],
             [(None, 'Bestial laughter. Music. Snatches of conversation.')]),
            (('plate', 25), [(0.02, 0.10, 0.96), (0.15, 0.24, 0.70)], []),
            (('plate', 49), [(0.03, 0.04, 0.94), (0.39, 0.51, 0.42)],
             [(None, 'On the central balcony, Peter, the Baron’s Mentat, and Feyd Rautha, the Baron’s nephew and lover, can be seen playing chess.')]),
            (('frame', 139, 2, (28, 28, 859, 376)), None,
             [('SCENE', 'Scene 40 – Exterior. Harkonnen castle balcony'), (None, 'Peter and Feyd are sitting opposite each other.')]),
            (('frame', 139, 1, (27, 28, 861, 376)), None,
             [(None, 'They are playing chess with a set where the pieces are shaped like spiders and scorpions on the Mentat’s side- and like butterflies and wasps on the nephew’s side.')]),
            (('frame', 442, 1, (31, 31, 870, 384)), None,
             [(None, 'Beside Peter there is an outfit containing 24 hypodermic syringes arranged inside a clock-face. The syringes are filled with liquid spice.')]),
            (('frame', 442, 2, (31, 31, 870, 384)), None,
             [(None, 'Peter looks at the time on a tiny watch-ring, takes out a syringe, places it in a surgical revolver and injects it into his leg.')]),
            (('frame', 442, 3, (31, 31, 870, 384)), None,
             [(None, 'As the liquid progressively enters his blood, he moans with pleasure.')]),
            (('frame', 89, 6, (27, 27, 860, 374)), None, [('Feyd', 'Why is my uncle giving a party? We’ve just lost Dune !')]),
            (('frame', 89, 7, (26, 27, 857, 374)), None, [('Peter', 'Lost Dune ?')]),
            (('frame', 89, 8, (28, 27, 858, 373)), None, [(None, 'And he bursts out laughing.')]),
            (('frame', 89, 9, (24, 28, 772, 374)), None, []),
        ],
    },
}


def smooth(a, b, x):
    t = min(1, max(0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def load(src):
    """The picture as float BGR, and a short label saying what it is."""
    if src[0] == 'plate':
        im = cv2.imread(os.path.join(REPO, 'art', f'{src[1]:03d}.webp'))
        return im.astype(np.float32), f'PLATE {src[1] + 1}'
    _, i, n, (l, t, r, b) = src
    im = cv2.imread(os.path.join(REPO, 'frames', f'{i:03d}-{n:02d}.webp'))[t:b, l:r]
    im = cv2.resize(im, None, fx=2, fy=2, interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
    return im * np.array([0.90, 0.955, 0.975], np.float32), f'PLATE {i + 1} · FRAME {n}'      # white paper warmed a little


def default_camera(im):
    """A slow push toward the middle of a picture that already has the screen's shape, or nearly."""
    a = im.shape[1] / im.shape[0]
    w0 = min(1.0, ASPECT / a); h0 = w0 * a / ASPECT
    w1 = w0 * 0.92; h1 = w1 * a / ASPECT
    return [((1 - w0) / 2, (1 - h0) / 2, w0), ((1 - w1) / 2, (1 - h1) / 2, w1)]


def view(im, cam, u):
    """The picture as the camera sees it at progress u (0 to 1) through its positions."""
    n = len(cam) - 1
    k = min(n - 1, int(u * n)); f = smooth(0, 1, u * n - k)
    (x0, y0, w0), (x1, y1, w1) = cam[k], cam[k + 1]
    w = w0 * (w1 / w0) ** f                                   # zoom at a steady rate
    g = f if abs(w1 - w0) < 1e-6 else (w - w0) / (w1 - w0)
    x, y = x0 + (x1 - x0) * g, y0 + (y1 - y0) * g
    ih, iw = im.shape[:2]
    s = PW / (w * iw)
    M = np.float32([[s, 0, -x * iw * s], [0, s, -y * ih * s]])
    return cv2.warpAffine(im, M, (PW, PH), flags=cv2.INTER_CUBIC if s > 1 else cv2.INTER_AREA, borderMode=cv2.BORDER_REPLICATE)


def font(d, name, size):
    return ImageFont.truetype(os.path.join(d, name), size)


def wrap(text, fnt, width):
    d = ImageDraw.Draw(Image.new('RGB', (10, 10))); out, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=fnt) <= width or not cur: cur = t
        else: out.append(cur); cur = w
    return out + [cur] if cur else out


def layer(draw):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); draw(ImageDraw.Draw(im))
    a = np.asarray(im).astype(np.float32)
    return a[:, :, 2::-1].copy(), a[:, :, 3:4] / 255


def card(lines, fonts, gap=22):
    """lines: [(text, font file, size, colour)], centred on a black screen."""
    def draw(d):
        boxes = [d.textbbox((0, 0), t, font=font(fonts, f, s)) for t, f, s, _ in lines]
        y = (H - sum(b[3] - b[1] for b in boxes) - gap * (len(lines) - 1)) // 2
        for (t, f, s, c), b in zip(lines, boxes):
            d.text(((W - (b[2] - b[0])) // 2 - b[0], y - b[1]), t, font=font(fonts, f, s), fill=c + (255,)); y += b[3] - b[1] + gap
    return layer(draw)


def words_layer(speaker, text, label, fonts):
    def draw(d):
        f = font(fonts, 'CourierPrime.ttf', 34); b = font(fonts, 'CourierPrime-Bold.ttf', 34); small = font(fonts, 'CourierPrime-Bold.ttf', 20)
        d.text((60, PY - 44), label, font=small, fill=DIM + (255,))          # what the picture is, above it and out of the way of the words
        if not text: return
        if speaker == 'SCENE':
            t = text.upper(); d.text(((W - d.textlength(t, font=b)) / 2, PY + PH + 46), t, font=b, fill=GOLD + (255,)); return
        lines = wrap(text, f, W - 560); y = PY + PH + (22 if speaker else 24 + (0 if len(lines) > 1 else 20))
        if speaker:
            t = speaker.upper(); d.text(((W - d.textlength(t, font=b)) / 2, y), t, font=b, fill=GOLD + (255,)); y += 44
        for ln in lines[:3]:
            d.text(((W - d.textlength(ln, font=f)) / 2, y), ln, font=f, fill=PAPER_TXT + (255,)); y += 44
    return layer(draw)


def sentences(text, most=26):
    """Split a long paragraph where its sentences end, so each piece can be read in one go. No word is changed."""
    parts, cur = [], ''
    for w in text.split():
        cur = (cur + ' ' + w).strip()
        if w[-1] in '.!?' and len(cur.split()) >= 6: parts.append(cur); cur = ''
    if cur: parts.append(cur)
    out = []
    for p in parts:
        if out and len((out[-1] + ' ' + p).split()) <= most: out[-1] += ' ' + p
        else: out.append(p)
    return out


def main():
    name, fonts, out_dir = sys.argv[1:4]
    preview = '--preview' in sys.argv
    E = EDITS[name]; os.makedirs(out_dir, exist_ok=True)

    # the timeline: when each shot starts, and which words are up when
    shots, cues, t = [], [], 0.0
    for src, cam, lines in E['shots']:
        im, label = load(src)
        pieces = []
        for sp, tx in lines:
            for p in ([tx] if sp == 'SCENE' else sentences(tx)): pieces.append((sp, p))
        times = [2.8 if sp == 'SCENE' else max(2.4, 1.0 + READ * len(p.split())) for sp, p in pieces]
        dur = max(4.2, sum(times) + 0.6) + (1.5 if len(cam or []) > 2 else 0)
        at = t + 0.3
        for (sp, p), d in zip(pieces, times): cues.append((at, at + d, sp, p, label)); at += d
        shots.append({'im': im, 'cam': cam or default_camera(im), 'start': t, 'dur': dur, 'label': label})
        t += dur
    body = t
    HEAD, TAIL = 9.5, 9.5
    total = HEAD + body + TAIL
    print('shots', len(shots), 'body', round(body, 1), 'total', round(total, 1), flush=True)
    for s in shots: print(' ', s['label'], round(s['start'], 1), round(s['dur'], 1), flush=True)

    layers = {}
    def words(sp, tx, label):
        k = (sp, tx, label)
        if k not in layers: layers[k] = words_layer(sp, tx, label, fonts)
        return layers[k]
    title = card([('DUNE', 'Anton.ttf', 250, GOLD), (E['title'], 'CourierPrime-Bold.ttf', 40, PAPER_TXT), (E['sub'], 'CourierPrime.ttf', 30, PAPER_TXT)], fonts, gap=34)
    note = card([('Adapted from the surviving materials of Alejandro Jodorowsky’s unmade film.', 'CourierPrime.ttf', 30, PAPER_TXT),
                 (E['pictures'], 'CourierPrime.ttf', 30, PAPER_TXT), (E['pictures2'], 'CourierPrime.ttf', 30, PAPER_TXT),
                 ('The words under them are the screenplay’s, as typed.', 'CourierPrime.ttf', 30, PAPER_TXT),
                 ('The edit, the camera movement and the sound were made for this edition. It is not footage.', 'CourierPrime.ttf', 30, PAPER_TXT)], fonts)
    end = card([(E['end'][0], 'CourierPrime-Bold.ttf', 30, PAPER_TXT)] + [(x, 'CourierPrime.ttf', 27, PAPER_TXT) for x in E['end'][1:]], fonts)

    yy, xx = np.mgrid[0:PH, 0:PW].astype(np.float32)
    vig = 1 - 0.34 * np.clip(((xx / PW - .5) ** 2 + ((yy / PH - .5) * PH / PW) ** 2) / 0.30, 0, 1)[..., None] ** 1.5
    rng = np.random.default_rng(11)
    out = os.path.join(out_dir, name + '-silent.mp4')
    enc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'slow', '-crf', '30' if preview else '24', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    step = 6 if preview else 1
    nframes = int(round(total * FPS))
    for n in range(0, nframes, step):
        t = n / FPS; tb = t - HEAD
        frame = np.zeros((H, W, 3), np.float32)
        if -1.0 <= tb < body + 1.5:
            tc = min(max(tb, 0), body - 1e-3)
            i = max(k for k, s in enumerate(shots) if s['start'] <= tc)
            s = shots[i]
            pic = view(s['im'], s['cam'], min(1, (tc - s['start']) / (s['dur'] + MIX)))
            if i and tc - s['start'] < MIX:                    # still dissolving in from the shot before
                p = shots[i - 1]
                old = view(p['im'], p['cam'], min(1, (tc - p['start']) / (p['dur'] + MIX)))
                a = smooth(0, MIX, tc - s['start']); pic = old * (1 - a) + pic * a
            pic = pic * vig + rng.normal(0, 2.2, (PH, PW, 1)).astype(np.float32)
            pic *= 1 + 0.012 * math.sin(t * 9.1) * math.sin(t * 2.3)
            fade = smooth(HEAD - 1.0, HEAD + 0.8, t) * (1 - smooth(body - 0.3, body + 1.5, tb))
            frame[PY:PY + PH] = pic * fade
            cue = next((c for c in cues if c[0] <= tc < c[1]), None)
            if cue:
                a = min(smooth(cue[0], cue[0] + 0.3, tc), 1 - smooth(cue[1] - 0.3, cue[1], tc)) * fade
                img, al = words(cue[2], cue[3], cue[4])
            else:
                a = fade; img, al = words(None, '', s['label'])
            frame = frame * (1 - al * a) + img * al * a
        if t < HEAD:
            a1 = smooth(0.3, 1.5, t) * (1 - smooth(3.6, 4.4, t)); a2 = smooth(4.6, 5.4, t) * (1 - smooth(HEAD - 1.4, HEAD - 0.6, t))
            frame = frame * (1 - title[1] * a1) + title[0] * title[1] * a1
            frame = frame * (1 - note[1] * a2) + note[0] * note[1] * a2
        te = tb - body
        if te > 1.2:
            a = smooth(1.2, 2.4, te) * (1 - smooth(TAIL - 1.2, TAIL - 0.2, te))
            frame = frame * (1 - end[1] * a) + end[0] * end[1] * a
        buf = np.clip(frame, 0, 255).astype(np.uint8).tobytes()
        for _ in range(step): enc.stdin.write(buf)
        if n % (FPS * 10) == 0: print('rendered', round(t), 'of', round(total), 's', flush=True)
    enc.stdin.close(); enc.wait()
    print('wrote', out, round(total, 1), 's')


if __name__ == '__main__':
    main()
