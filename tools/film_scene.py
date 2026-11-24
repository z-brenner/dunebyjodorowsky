"""Scenes as film: the surviving pictures cut together under the screenplay's own lines.

Each film is an edit list (EDITS below): which picture, how the camera moves over it, and which
lines of the script sit under it. The pictures and the words are the production's. The edit, the
camera movement, the timing, the titles and the sound are this edition's, and each film says so on
screen. Nothing here is footage, and nothing is drawn or generated.

Every line of script in an edit list is checked against assets/script.js before anything is
rendered: if it is not word for word in the scene it claims to come from, the build stops.

usage: film_scene.py <name> <fonts dir> <out dir> [--preview | --stills | --cues]
"""
import json, math, os, re, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
W, H, FPS = 1920, 1080, 24
PW, PH, PY = 1920, 800, 96                # the picture: a 2.4 to 1 window, with the words below it
ASPECT = PW / PH
MIX = 0.8                                 # seconds for one picture to dissolve into the next
READ = 0.34                               # seconds a word stays up
GOLD, PAPER_TXT, DIM, BOARD = (217, 170, 76), (236, 226, 204), (156, 123, 60), (190, 160, 110)
LIMIT = 25 * 1024 * 1024                  # the host serves no file larger than this

# A shot: (source, camera, lines[, seconds to hold a shot that has no words; 3 if not given])
#   source  ('plate', index[, (l, t, r, b)])    a whole restored plate, art/NNN.webp, or the part of it inside
#                                               its drawn border, as fractions of the plate
#           ('frame', index, n[, (l, t, r, b)]) a frame cut from a sheet, frames/NNN-KK.webp. The drawing
#                                               inside its ruled border is found by itself, or given in pixels
#           ('closeup', index, n)               the same, for a sheet whose frames were found one at a time
#           ('text',)                           no picture survives: the words alone, on black
#   camera  None or 'in' (slow push), 'out', 'left', 'right', 'rush' (fast push), or
#           [(x, y, width), ...]  the part of the picture on screen at the start, (middle,) and end,
#           as fractions of the picture: left, top, width. Height follows from the screen's shape.
#   lines   [(speaker or None, text)]  words of the screenplay, unaltered.
#           'SCENE' marks a slate. 'BOARD' marks a caption printed on the storyboard, not the script.
#           ('NUM', n) shows nothing itself: from here on, the label above the picture names scene n.
# A film's 'score' says how the music moves: {shot number: intensity} or {shot number: (intensity, accent)}
# or (intensity, accent, seconds into the shot). Intensity runs from 0, hushed, to 1, full; it holds until the
# next entry. An accent is 'hit', 'swell' or 'drop'. --cues writes these as times for tools/record_score.js.
#   T(scene, k) fetches block k of a scene from assets/script.js, so long passages are not retyped;
#   T(scene, k, a, b) fetches its sentences a to b. J(...) joins fetched pieces into one line.
F, C = 'frame', 'closeup'


def _script():
    raw = open(os.path.join(REPO, 'assets', 'script.js'), encoding='utf-8').read()
    return json.loads(raw[raw.index('{'):raw.rindex('}') + 1])


SCRIPT = {sc['n']: [b for b in sc['b'] if b[0] in 'adt'] for sc in _script()['scenes']}


def T(scene, k, a=None, b=None):
    blk = SCRIPT[scene][k]; text = blk[-1]
    if a is not None: text = ' '.join(re.split(r'(?<=[.!?])\s+', text)[a:b])
    return (blk[1] if blk[0] == 'd' else None, text)


def J(*parts):
    return (parts[0][0], ' '.join(x[1] for x in parts))


# the illustrated screenplay's pictures, inside their drawn borders
P194, P45, P40, P8 = ('plate', 193, (.235, .145, .75, .89)), ('plate', 44, (.023, .036, .974, .959)), ('plate', 39, (.042, .047, .965, .929)), ('plate', 7, (.025, .038, .973, .955))
P42, P18, P43 = ('plate', 41, (.036, .066, .963, .944)), ('plate', 17, (.044, .045, .957, .942)), ('plate', 42, (.056, .05, .959, .929))
P48, P44, P11 = ('plate', 47, (.028, .04, .971, .964)), ('plate', 43, (.033, .034, .963, .936)), ('plate', 10, (.03, .038, .971, .961))
ALONE = ('text',)
EDITS = {
    'harkonnen': {
        'title': 'THE HARKONNEN CASTLE', 'score': {0: .35, 1: .5, 2: (.6, 'hit'), 3: .5, 4: .4, 6: .45, 7: .55, 8: (.5, 'swell'), 9: .4, 11: .6, 12: .65}, 'sub': 'scenes 39 and 40, from the screenplay and the storyboard', 'mood': 3, 'scenes': [39, 40],
        'pictures': ['The pictures are the production’s: the storyboard by Jean Giraud (Moebius),', 'and one drawing from the illustrated screenplay, artist uncredited in the source.'],
        'end': ['Scenes 39 and 40 of the early draft. Plates 28, 284, 26, 50, 140, 443 and 90.',
                'Each line sits under the storyboard frame whose own caption describes it; that pairing is this edition’s.',
                'The pan up the castle and the push toward its head follow the storyboard’s written camera notes.',
                'Edit, movement, timing, titles and sound: this edition. Unofficial; the art remains the artists’.'],
        'shots': [
            (('plate', 27), [(0.0, 0.26, 1.0), (0.2, 0.084, 0.8)],
             [('SCENE', 'Scene 39 – Exterior. Harkonnen castle'), (None, 'Approaches to the sombre castle, bathed in the sound of sea waves.')]),
            (('plate', 283), [(0.08, 0.68, 0.86), (0.08, 0.03, 0.86), (0.315, 0.036, 0.30)],
             [(None, 'Bestial laughter. Music. Snatches of conversation.')]),
            (('plate', 25), [(0.02, 0.10, 0.96), (0.15, 0.24, 0.70)], [], 4.2),
            (('plate', 49), [(0.03, 0.04, 0.94), (0.39, 0.51, 0.42)],
             [(None, 'On the central balcony, Peter, the Baron’s Mentat, and Feyd Rautha, the Baron’s nephew and lover, can be seen playing chess.')]),
            ((F, 139, 2, (28, 28, 859, 376)), None,
             [('SCENE', 'Scene 40 – Exterior. Harkonnen castle balcony'), (None, 'Peter and Feyd are sitting opposite each other.')]),
            ((F, 139, 1, (27, 28, 861, 376)), None,
             [(None, 'They are playing chess with a set where the pieces are shaped like spiders and scorpions on the Mentat’s side- and like butterflies and wasps on the nephew’s side.')]),
            ((F, 442, 1, (31, 31, 870, 384)), None,
             [(None, 'Beside Peter there is an outfit containing 24 hypodermic syringes arranged inside a clock-face. The syringes are filled with liquid spice.')]),
            ((F, 442, 2, (31, 31, 870, 384)), None,
             [(None, 'Peter looks at the time on a tiny watch-ring, takes out a syringe, places it in a surgical revolver and injects it into his leg.')]),
            ((F, 442, 3, (31, 31, 870, 384)), None,
             [(None, 'As the liquid progressively enters his blood, he moans with pleasure.')]),
            ((F, 89, 6, (27, 27, 860, 374)), None, [('Feyd', 'Why is my uncle giving a party? We’ve just lost Dune !')]),
            ((F, 89, 7, (26, 27, 857, 374)), None, [('Peter', 'Lost Dune ?')]),
            ((F, 89, 8, (28, 27, 858, 373)), None, [(None, 'And he bursts out laughing.')]),
            ((F, 89, 9, (24, 28, 772, 374)), None, [], 4.2),
        ],
    },
    'museum': {
        'title': 'THE MUSEUM OF MAN', 'score': {0: (.3, 'swell'), 1: .2, 2: .35, 3: .2, 5: .35, 6: .4, 8: (.3, 'drop'), 9: .4, 10: .45, 11: (.6, 'hit'), 12: .65, 13: .6, 14: .45, 15: .5, 17: (.65, 'swell'), 18: (.75, 'hit', 6.5)}, 'sub': 'scenes 1 to 9, from the screenplay and its own pictures', 'mood': 0, 'scenes': list(range(1, 10)),
        'pictures': ['The pictures are the illustrated screenplay\u2019s own. Their artist is not credited in the source.'],
        'end': ['Scenes 1 to 9 of the early draft. Plates 194, 45, 40, 8, 42, 18 and 43.',
                'Each picture is the one the typescript calls for at that scene, except plate 45, the ship: it belongs to scene 1 and is shown under scene 3.',
                'The typescript\u2019s pictures for scenes 2 to 5 are not in the archive, so those scenes are shown as words.',
                'Edit, movement, timing, titles and sound: this edition. Unofficial; the art remains the artists\u2019.'],
        'shots': [
            (P194, [(0.0, 0.10, 1.0), (0.0, 0.38, 1.0)], [('NUM', 1), T(1, 0)]),
            (ALONE, None, [('NUM', 2), T(2, 0)]),
            (P45, [(0.0, 0.15, 1.0), (0.08, 0.20, 0.84)], [('NUM', 3), T(3, 0)]),
            (ALONE, None, [('NUM', 4), T(4, 0)]),
            (ALONE, None, [('NUM', 5), J(T(5, 0), T(5, 1))]),
            (P40, [(0.34, 0.10, 0.66), (0.0, 0.08, 0.70)], [('NUM', 6), T(6, 0)]),
            (P8, [(0.42, 0.0, 0.58), (0.50, 0.02, 0.50)], [('NUM', 7), T(7, 0)]),
            (P8, [(0.0, 0.28, 0.62), (0.0, 0.13, 1.0)], [('NUM', 8), T(8, 0)]),
            (P42, [(0.0, 0.14, 1.0), (0.05, 0.17, 0.90)], [('NUM', 9), T(9, 0)]),
            (P42, [(0.0, 0.30, 0.90), (0.0, 0.52, 0.62)], [T(9, 1)]),
            (P42, [(0.20, 0.20, 0.80), (0.30, 0.24, 0.70)], [T(9, 2)]),
            (P42, [(0.30, 0.24, 0.70), (0.62, 0.45, 0.38)], [T(9, 3)]),
            (P18, [(0.0, 0.20, 1.0), (0.0, 0.25, 0.90)], [T(9, 4)]),
            (P18, [(0.0, 0.27, 0.90), (0.20, 0.60, 0.52)], [T(9, 5)]),
            (P18, [(0.20, 0.60, 0.52), (0.0, 0.02, 0.62)], [J(T(9, 6), T(9, 7))]),
            (P18, [(0.0, 0.02, 0.62), (0.10, 0.03, 0.42)], [T(9, 8), T(9, 9)]),
            (P43, [(0.0, 0.0, 0.60), (0.0, 0.05, 0.50)], [T(9, 10, 0, 3)]),
            (P43, [(0.0, 0.12, 0.62), (0.38, 0.10, 0.62)], [T(9, 10, 3, 4)]),
            (P43, [(0.10, 0.30, 0.90), (0.0, 0.18, 1.0)], [J(T(9, 11), T(9, 12))]),
        ],
    },
    'history': {
        'title': 'THE HISTORY OF MAN', 'score': {0: (.7, 'hit'), 1: .6, 2: .5, 4: .7, 5: .55, 6: (.25, 'drop'), 8: .4, 10: .45, 11: .4, 12: .55, 13: .6, 14: (.65, 'hit', 9)}, 'sub': 'scenes 10 to 14: what the robot projects', 'mood': 0, 'scenes': list(range(10, 15)),
        'pictures': ['The pictures are the illustrated screenplay\u2019s own. Their artist is not credited in the source.'],
        'end': ['Scenes 10 to 14 of the early draft. Plates 48, 44 and 11.',
                'Each picture is the one the typescript calls for at that scene. Plate 48 is also shown under the first lines of scene 11.',
                'The typescript\u2019s pictures for scenes 12 and 14 are not in the archive, so those scenes are shown as words.',
                'Edit, movement, timing, titles and sound: this edition. Unofficial; the art remains the artists\u2019.'],
        'shots': [
            (P48, [(0.30, 0.0, 0.70), (0.38, 0.05, 0.60)], [('NUM', 10), J(T(10, 0), T(10, 1))]),
            (P48, [(0.30, 0.10, 0.70), (0.0, 0.42, 0.62)], [T(10, 2)]),
            (P48, [(0.0, 0.13, 1.0), (0.04, 0.15, 0.92)], [T(10, 3)]),
            (P48, [(0.0, 0.42, 0.62), (0.10, 0.25, 0.80)], [('NUM', 11), J(T(11, 0), T(11, 1)), T(11, 2)]),
            (P44, [(0.0, 0.20, 1.0), (0.20, 0.30, 0.70)], [T(11, 3)]),
            (P44, [(0.20, 0.30, 0.70), (0.42, 0.50, 0.56)], [T(11, 4)]),
            (ALONE, None, [('NUM', 12), T(12, 0)]),
            (ALONE, None, [T(12, 1)]),
            (P11, [(0.40, 0.0, 0.60), (0.30, 0.25, 0.70)], [('NUM', 13), T(13, 0, 0, 1)]),
            (P11, [(0.05, 0.55, 0.66), (0.10, 0.56, 0.60)], [T(13, 0, 1, 2)]),
            (P11, [(0.0, 0.10, 0.50), (0.0, 0.12, 0.36)], [T(13, 0, 2, 3)]),
            (P11, [(0.04, 0.15, 0.92), (0.0, 0.17, 1.0)], [T(13, 1)]),
            (ALONE, None, [('NUM', 14), T(14, 0)]),
            (ALONE, None, [T(14, 1), T(14, 2)]),
            (ALONE, None, [T(14, 3), T(14, 4)]),
        ],
    },
    'robot': {
        'title': 'THE ROBOT', 'score': {0: (.35, 'swell'), 1: .4, 2: .3, 3: .35, 4: .3, 7: (.55, 'hit'), 8: .45, 9: .5, 10: (.7, 'hit', 1.2), 11: .6, 12: .5, 13: .45, 14: .4, 15: .55}, 'sub': 'scene 43, Paul’s gymnasium: the first part', 'mood': 4, 'scenes': [43],
        'pictures': ['The pictures are the production’s: the storyboard by Jean Giraud (Moebius).'],
        'end': ['Scene 43 of the early draft, to the start of the duel. Plates 117, 218 and 219.',
                'Each line sits under the storyboard frame whose own caption describes it; that pairing is this edition’s.',
                'The first two captions are the storyboard’s own: the draft does not have the ship. One passage has no picture and is shown as words.',
                'Edit, movement, timing, titles and sound: this edition. Unofficial; the art remains the artists’.'],
        'shots': [
            ((F, 217, 1), 'in', [('SCENE', 'Scene 43 – Interior : Paul’s gymnasium'), ('BOARD', 'Guild ship in space – stars moving')]),
            ((F, 217, 2), 'in', [('BOARD', 'Closer on Guild ship – showing dome with gymnasium on side – stars moving')]),
            ((F, 217, 3), 'right', [(None, 'A gymnasium. Weights, ladders, ropes, trapeziums, etc.. On the walls, anatomical engravings and very advanced geometrical studies can be seen.'),
                                    (None, 'On a table, two by two, are all kinds of arms : pickaxes and masses of arms, sticks, hooks, saws, etc..')]),
            ((F, 217, 4), 'in', [(None, 'On a platform, dressed as Masters at arms, Duncan Idaho, Gurney Halleck, Thufir Hawatt and Wellington Yueh are all sitting in great ceremony,'),
                                 (None, 'together with a mysterious individual wearing a large hat and full clothes.'),
                                 (None, 'Impossible to see who he is. His hand is rhythmically waving a fan.')]),
            ((F, 218, 6), 'in', [(None, 'Paul, dressed for combat, with his shield, sword-belt and sword, bows in front of his masters. He raises his head and makes as if to speak, but the stranger’s presence stops him. He seems very sad.')]),
            ((F, 116, 4), 'in', [('HAWATT', 'Speak. He’s a friend.')]),
            ((F, 218, 6), 'out', [('PAUL', 'We are leaving Caladan today. I’d prefer not to have a lesson.')]),
            (('text',), None, [(None, 'Idaho gives a violent roar and, with a punch, knocks him down.'),
                               ('IDAHO', 'Don’t mix feelings and fighting. Happy or sad, the Harkonnen won’t spare your life. If you can’t defend yourself, you might as well die straight away.')]),
            ((F, 217, 5), 'right', [(None, 'Hawatt moves towards the stranger, takes the fan away from him, as well as his hat.')]),
            ((F, 217, 6), 'in', []),
            ((F, 217, 7), 'rush', [(None, 'A faceless ball of steel appears : It’s a robot!')]),
            ((F, 218, 1), 'out', []),
            ((F, 218, 2), 'in', [('THUFIR', 'This robot will judge your courage, your speed and resistance. You cannot defeat him. If you try, you’ll die. The longer the fight lasts, the more he’ll confirm his superiority over you and the better he’ll attack.')]),
            ((F, 218, 7), 'in', [(None, 'Thufir Hawatt opens a window in the robot’s head. He reveals a microphone micro-cell.'), ('THUFIR', 'What’s your name ?')]),
            ((F, 218, 6), 'in', [('PAUL', 'Paul.')]),
            ((F, 218, 3), 'left', [('THUFIR', 'He has recorded your voice. From now on, you alone can stop the fight.')]),
        ],
    },
    'duel': {
        'title': 'THE DUEL', 'score': {0: .5, 2: .55, 3: (.75, 'hit'), 4: .7, 5: (.75, 'hit', 1.5), 6: .7, 7: .8, 9: .9, 12: 1.0, 13: (1.0, 'hit'), 14: .9, 15: 1.0, 16: .8, 17: (.9, 'hit', 9.5), 18: (.35, 'drop')}, 'sub': 'scene 43, Paul’s gymnasium: the fight with the robot', 'mood': 4, 'scenes': [43],
        'pictures': ['The pictures are the production’s: the storyboard by Jean Giraud (Moebius).'],
        'end': ['Scene 43 of the early draft: the duel. Plates 21, 41, 117, 219, 220 and 285.',
                'Each line sits under the storyboard frame whose own caption describes it; that pairing is this edition’s.',
                'No storyboard survives for the end of the fight, so its last three paragraphs are shown as words.',
                'Edit, movement, timing, titles and sound: this edition. Unofficial; the art remains the artists’.'],
        'shots': [
            ((F, 218, 4), 'in', [('SCENE', 'Scene 43 – the duel'), (None, 'Thufir pushes a button. The machine gets up, draws its sword and slowly comes face to face with Paul.')]),
            (('plate', 20), [(0.05, 0.12, 0.90), (0.09, 0.14, 0.82)], [(None, 'It records each of his movements, the sound of his breathing, the beat of his heart.')]),
            ((F, 218, 5), 'left', []),
            ((F, 116, 1), 'rush', [(None, 'Paul attacks the robot and tries to throw him to the ground.')]),
            ((C, 219, 3), 'in', [(None, 'The machine, clumsy as first, becomes more agile and stronger as it records Paul.')]),
            ((C, 219, 2), 'right', [(None, 'The robot falls down and gets back up, each time more powerful.')]),
            (('plate', 40), [(0.05, 0.07, 0.90), (0.12, 0.10, 0.76)], []),
            (('plate', 284), [(0.045, 0.075, 0.925), (0.12, 0.12, 0.78)], [(None, 'The fight becomes faster and more sustained.')]),
            ((C, 219, 7), 'in', [(None, 'The robot records each blow, movement or noise made by Paul.')]),
            ((C, 219, 8), 'left', [(None, 'The combat is now taking place at a giddy rate.')]),
            ((C, 219, 9), 'right', []),
            ((C, 219, 4), 'in', [(None, 'Paul doesn’t want to surrender. He feels himself overcome by a suicidal euphoria.')]),
            ((C, 219, 10), 'rush', [(None, 'The robot becomes monstrously aggressive.')]),
            ((C, 219, 11), 'rush', []),
            ((F, 116, 4), 'in', [('THUFIR', 'That’s enough !')]),
            ((C, 219, 9), 'rush', [('DUNCAN', 'Stop him !')]),
            (('text',), None, [(None, 'Paul continues fighting. The machine’s capacities are increasing. Paul falls down. As he dodges it, a blow of the robot’s sword cuts the table in two and splits open the floor.')]),
            (('text',), None, [(None, 'Thufir breaks a pane of glass and takes out a laser-thrower Idaho and Halleck throw themselves on to Paul and make him roll across the floor. Thufir shoots. The robot explodes, throwing its smoking parts out on to the ground.')]),
            (('text',), None, [(None, 'While everyone gets up and makes sure that nobody is hurt, Leto, followed by Jessica and a group of soldiers, enters the gymnasium with a sword in his hand.')]),
        ],
    },
}


def smooth(a, b, x):
    t = min(1, max(0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def check_words(E):
    """Stop unless every script line in the edit is word for word in the scenes it names."""
    raw = open(os.path.join(REPO, 'assets', 'script.js'), encoding='utf-8').read()
    script = json.loads(raw[raw.index('{'):raw.rindex('}') + 1])
    flat = lambda s: ' '.join(s.replace('’', "'").split())
    text = flat(' '.join(' '.join(str(x) for x in b[1:]) for sc in script['scenes'] if sc['n'] in E['scenes'] for b in sc['b'] if b[0] in 'adt'))
    bad = [tx for _, _, lines, *_ in E['shots'] for sp, tx in lines if sp not in ('SCENE', 'BOARD', 'NUM') and flat(tx) not in text]
    if bad: sys.exit('not in the screenplay as typed:\n  ' + '\n  '.join(bad))


def inner(gray):
    """The drawing inside a cut frame's own ruled border."""
    dark = gray < 125
    h, w = gray.shape
    rows = np.where(dark[:, w // 5: w * 4 // 5].mean(1) > 0.45)[0]
    top = max([r for r in rows if r < 90] or [22]) + 4
    bot = min([r for r in rows if 300 < r < 440] or [380]) - 4
    cols = np.where(dark[top + 10:bot - 10].mean(0) > 0.45)[0]
    left = max([c for c in cols if c < 110] or [22]) + 4
    right = min([c for c in cols if c > 760] or [866]) - 4
    return left, top, right, bot


def load(src):
    """The picture as float BGR, and a short label saying what it is."""
    if src[0] == 'text': return None, 'THE SCRIPT ALONE · NO PICTURE SURVIVES'
    if src[0] == 'plate':
        im = cv2.imread(os.path.join(REPO, 'art', f'{src[1]:03d}.webp'))
        if len(src) > 2:
            h, w = im.shape[:2]; l, t, r, b = src[2]; im = im[int(t * h):int(b * h), int(l * w):int(r * w)]
        return im.astype(np.float32), f'PLATE {src[1] + 1}'
    kind, i, n = src[:3]
    im = cv2.imread(os.path.join(REPO, 'frames', f'{i:03d}-{n:02d}.webp'))
    l, t, r, b = src[3] if len(src) > 3 else inner(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY))
    im = cv2.resize(im[t:b, l:r], None, fx=2, fy=2, interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
    return im * np.array([0.90, 0.955, 0.975], np.float32), f'PLATE {i + 1} · ' + ('FRAME ' if kind == F else 'CLOSE-UP ') + str(n)   # white paper warmed a little


def camera(im, how):
    """Where the camera starts and ends on a picture, for a named move."""
    if isinstance(how, list): return how
    a = im.shape[1] / im.shape[0]
    full = min(1.0, ASPECT / a)                               # the widest view that still fills the screen
    box = lambda w, fx=0.5: (fx * (1 - w), (1 - w * a / ASPECT) / 2, w)
    return {'in': [box(full), box(full * 0.92)], 'out': [box(full * 0.92), box(full)], 'rush': [box(full), box(full * 0.74)],
            'left': [box(full * 0.93, 1.0), box(full * 0.93, 0.0)], 'right': [box(full * 0.93, 0.0), box(full * 0.93, 1.0)]}[how or 'in']


def view(im, cam, u):
    """The picture as the camera sees it at progress u (0 to 1) through its positions."""
    if im is None: return np.zeros((PH, PW, 3), np.float32)
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
    """lines: [(text, font file, size, colour)], centred on a black screen. A line too wide for the screen is wrapped."""
    lines = [(part, f, sz, c) for t, f, sz, c in lines for part in wrap(t, font(fonts, f, sz), W - 200)]
    def draw(d):
        boxes = [d.textbbox((0, 0), t, font=font(fonts, f, s)) for t, f, s, _ in lines]
        y = (H - sum(b[3] - b[1] for b in boxes) - gap * (len(lines) - 1)) // 2
        for (t, f, s, c), b in zip(lines, boxes):
            if b[2] - b[0] > W - 80: sys.exit('a card line is wider than the screen: ' + t)
            d.text(((W - (b[2] - b[0])) // 2 - b[0], y - b[1]), t, font=font(fonts, f, s), fill=c + (255,)); y += b[3] - b[1] + gap
    return layer(draw)


def words_layer(speaker, text, label, fonts, alone=False):
    """The words under the picture, and the label above it. alone: no picture, so the words take the screen."""
    text = text.replace("'", '\u2019')                    # typewriter apostrophes are shown as printed ones
    def draw(d):
        size = 46 if alone else 34
        f = font(fonts, 'CourierPrime.ttf', size); b = font(fonts, 'CourierPrime-Bold.ttf', size); small = font(fonts, 'CourierPrime-Bold.ttf', 20)
        d.text((60, PY - 44), label, font=small, fill=DIM + (255,))          # what the picture is, above it and out of the way of the words
        if not text: return
        if speaker == 'SCENE':
            t = text.upper(); d.text(((W - d.textlength(t, font=b)) / 2, PY + PH + 46), t, font=b, fill=GOLD + (255,)); return
        named = speaker and speaker != 'BOARD'
        lines = wrap(text, f, W - (520 if alone else 560 if not named else 420)); step = 62 if alone else 44 if not named else 40
        if alone: y = PY + (PH - step * (len(lines) + (1 if named else 0))) // 2
        else: y = PY + PH + (14 if named else 24 + (0 if len(lines) > 1 else 20))
        if named:
            t = speaker.upper(); d.text(((W - d.textlength(t, font=b)) / 2, y), t, font=b, fill=GOLD + (255,)); y += step
        for ln in lines:
            d.text(((W - d.textlength(ln, font=f)) / 2, y), ln, font=f, fill=(BOARD if speaker == 'BOARD' else PAPER_TXT) + (255,)); y += step
        if not alone and y > H - 6: sys.exit('too many lines to fit under the picture: ' + text)
    return layer(draw)


def sentences(text, most=26, commas_too=True):
    """Split a long paragraph where its sentences end, and a very long sentence at a comma, so each
    piece can be read in one go. No word is changed."""
    parts, cur = [], ''
    for w in text.split():
        cur = (cur + ' ' + w).strip()
        if w[-1] in '.!?' and len(cur.split()) >= 6: parts.append(cur); cur = ''
    if cur: parts.append(cur)
    out = []
    for p in parts:
        if out and len((out[-1] + ' ' + p).split()) <= most: out[-1] += ' ' + p
        else: out.append(p)
    done = []
    for p in out:
        ws = p.split()
        commas = [i for i, w in enumerate(ws[:-1]) if w.endswith(',')]
        if commas_too and len(ws) > most + 4 and commas:
            k = min(commas, key=lambda i: (abs(i + 1 - len(ws) / 2), -i)) + 1
            done += [' '.join(ws[:k]), ' '.join(ws[k:])]
        else: done.append(p)
    return done


def main():
    name, fonts, out_dir = sys.argv[1:4]
    preview, stills, cues_only = '--preview' in sys.argv, '--stills' in sys.argv, '--cues' in sys.argv
    E = EDITS[name]; os.makedirs(out_dir, exist_ok=True)
    check_words(E)

    # the timeline: when each shot starts, and which words are up when
    shots, cues, t, scene_no = [], [], 0.0, None
    for src, cam, lines, *hold in E['shots']:
        im, label = load(src)
        alone = im is None
        for sp, tx in lines:
            if sp == 'NUM': scene_no = tx
        lines = [x for x in lines if x[0] != 'NUM']
        if scene_no is not None: label = f'SCENE {scene_no} \u00b7 ' + label
        pieces = []
        for sp, tx in lines:
            for p in ([tx] if sp in ('SCENE', 'BOARD') else sentences(tx, 40 if alone else 22 if sp else 26, not alone)): pieces.append((sp, p))
        times = [2.8 if sp == 'SCENE' else max(2.4, 1.0 + READ * len(p.split())) for sp, p in pieces]
        dur = max(4.2 if pieces else (hold[0] if hold else 3.0), sum(times) + 0.6) + (1.5 if isinstance(cam, list) and len(cam) > 2 else 0)
        at = t + 0.3
        for (sp, p), d in zip(pieces, times): cues.append((at, at + d, sp, p, label, alone)); at += d
        shots.append({'im': im, 'cam': None if alone else camera(im, cam), 'start': t, 'dur': dur, 'label': label})
        t += dur
    body = t
    HEAD, TAIL = 9.5, 9.5
    total = HEAD + body + TAIL
    print('shots', len(shots), 'body', round(body, 1), 'total', round(total, 1), flush=True)
    if cues_only:                                              # when the music should move, in seconds from the start of the film
        out, level = [{'t': 0, 'intensity': 0.25}, {'t': 0.4, 'accent': 'swell'}], 0.25
        for k, sh in enumerate(shots):
            v = E.get('score', {}).get(k)
            if v is None: continue
            v = v if isinstance(v, tuple) else (v,)
            out.append({'t': round(HEAD + sh['start'] - 0.6, 2), 'intensity': v[0], 'ramp': 2.5}); level = v[0]
            if len(v) > 1: out.append({'t': round(HEAD + sh['start'] + (v[2] if len(v) > 2 else 0.2), 2), 'accent': v[1]})
        out.append({'t': round(HEAD + body - 0.5, 2), 'intensity': 0.2, 'ramp': 4})
        path = os.path.join(out_dir, name + '-cues.json'); json.dump(sorted(out, key=lambda c: c['t']), open(path, 'w'), indent=1)
        print('wrote', path, len(out), 'cues; mood', E['mood'], '; record', math.ceil(total) + 3, 'seconds'); return

    layers = {}
    def words(sp, tx, label, alone=False):
        k = (sp, tx, label)
        if k not in layers: layers[k] = words_layer(sp, tx, label, fonts, alone)
        return layers[k]
    title = card([('DUNE', 'Anton.ttf', 250, GOLD), (E['title'], 'CourierPrime-Bold.ttf', 40, PAPER_TXT), (E['sub'], 'CourierPrime.ttf', 30, PAPER_TXT)], fonts, gap=34)
    note = card([(x, 'CourierPrime.ttf', 30, PAPER_TXT) for x in ['Adapted from the surviving materials of Alejandro Jodorowsky’s unmade film.'] + E['pictures'] +
                 ['The words under them are the screenplay’s, as typed.', 'The edit, the camera movement and the sound were made for this edition. It is not footage.']], fonts)
    end = card([(E['end'][0], 'CourierPrime-Bold.ttf', 30, PAPER_TXT)] + [(x, 'CourierPrime.ttf', 27, PAPER_TXT) for x in E['end'][1:]], fonts)

    yy, xx = np.mgrid[0:PH, 0:PW].astype(np.float32)
    vig = 1 - 0.34 * np.clip(((xx / PW - .5) ** 2 + ((yy / PH - .5) * PH / PW) ** 2) / 0.30, 0, 1)[..., None] ** 1.5
    rng = np.random.default_rng(11)

    def compose(t):
        tb = t - HEAD
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
            pic = pic * vig + rng.normal(0, 2.2, (PH, PW, 1)).astype(np.float32) * (pic.mean() > 1)
            pic *= 1 + 0.012 * math.sin(t * 9.1) * math.sin(t * 2.3)
            fade = smooth(HEAD - 1.0, HEAD + 0.8, t) * (1 - smooth(body - 0.3, body + 1.5, tb))
            frame[PY:PY + PH] = pic * fade
            cue = next((c for c in cues if c[0] <= tc < c[1]), None)
            if cue:
                a = min(smooth(cue[0], cue[0] + 0.3, tc), 1 - smooth(cue[1] - 0.3, cue[1], tc)) * fade
                img, al = words(cue[2], cue[3], cue[4], cue[5])
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
        return np.clip(frame, 0, 255).astype(np.uint8)

    if stills:                                                 # one look at every shot, with its first words, to check an edit before rendering it
        times = [HEAD + s['start'] + min(s['dur'] * 0.5, 2.2) for s in shots]
        cols = 4; cw, chh = 480, 270
        sheet = np.zeros((chh * ((len(times) + cols - 1) // cols), cw * cols, 3), np.uint8)
        for n, tt in enumerate(times):
            sheet[(n // cols) * chh:(n // cols + 1) * chh, (n % cols) * cw:(n % cols + 1) * cw] = cv2.resize(compose(tt), (cw, chh), interpolation=cv2.INTER_AREA)
        out = os.path.join(out_dir, name + '-stills.jpg'); cv2.imwrite(out, sheet, [cv2.IMWRITE_JPEG_QUALITY, 86]); print('wrote', out); return

    out = os.path.join(out_dir, name + '-silent.mp4')
    # Up to two minutes, constant quality. Up to about three, a little more compression. Longer than that, a
    # near-lossless master is rendered first and then encoded in two passes to a size the host will serve.
    sized = not preview and total > 170
    first = os.path.join(out_dir, name + '-master.mp4') if sized else out
    quality = ['-preset', 'veryfast', '-crf', '14'] if sized else ['-preset', 'slow', '-crf', '30' if preview else '24' if total <= 120 else '26']
    enc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264'] + quality + ['-pix_fmt', 'yuv420p', '-movflags', '+faststart', first], stdin=subprocess.PIPE)
    step = 6 if preview else 1
    for n in range(0, int(round(total * FPS)), step):
        buf = compose(n / FPS).tobytes()
        for _ in range(step): enc.stdin.write(buf)
        if n % (FPS * 10) == 0: print('rendered', round(n / FPS), 'of', round(total), 's', flush=True)
    enc.stdin.close(); enc.wait()
    if sized:
        rate = int(min(1300, LIMIT * 0.86 * 8 / 1000 / total - 128))          # kilobits a second, leaving room for the sound
        log = os.path.join(out_dir, name + '-2pass')
        for n, sink in ((1, ['-f', 'null', os.devnull]), (2, ['-movflags', '+faststart', out])):
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', first, '-c:v', 'libx264', '-preset', 'slow', '-b:v', f'{rate}k',
                            '-pass', str(n), '-passlogfile', log, '-pix_fmt', 'yuv420p', '-an'] + sink, check=True)
        print('encoded to', rate, 'kbit/s', flush=True)
    size = os.path.getsize(out)
    print('wrote', out, round(total, 1), 's', round(size / 1e6, 1), 'MB', '' if preview or size < LIMIT * 0.9 else '  TOO LARGE FOR THE HOST ONCE SOUND IS ADDED')


if __name__ == '__main__':
    main()
