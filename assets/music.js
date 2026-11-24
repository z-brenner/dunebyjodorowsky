/* A generated score. Nothing here is a recording: the browser synthesises it as you read. It is
   silent until the listener turns it on. Written for this edition; it is not music made for the film.

   What plays: a drone on a root and its fifth, whose bass note moves away and comes back; the same
   harmony held as a chord two octaves up, where a phone's speaker can play it; a slow
   melody that builds phrases from one short motif in the chapter's scale; bell notes; wind; and,
   when the intensity is raised, a drum. Each chapter has its own root, scale, tempo and balance.
   On the pages the intensity stays low, so there is no drum. The films raise and lower it shot by
   shot (tools/record_score.js plays a list of cues while recording). */
(function () {
  "use strict";
  var AC = window.AudioContext || window.webkitAudioContext;
  var ctx = null, master, bus, roomIn, tap, tone, droneLevel, lfoDepth, voices = [], subOsc, pad = [], padLevel, wind = [], bellBus, leadTone, vib, drumBus, slap, hiss;
  var playing = false, mood = null, intensity = 0.35, timer = 0, shift = 0, step = 0, motif = null, phrase = null, at = 0, next = null;

  var MINOR = [0, 2, 3, 5, 7, 8, 10], DORIAN = [0, 2, 3, 5, 7, 9, 10], PHRYGIAN = [0, 1, 3, 5, 7, 8, 10], HIJAZ = [0, 1, 4, 5, 7, 8, 10], OPEN = [0, 2, 5, 7, 9];
  var HEART = [1, 0, 0, 0.55, 0, 0, 0, 0], MARCH = [1, 0, 0.35, 0, 0.75, 0, 0.35, 0.3];
  /* root: the drone's pitch in Hz.   bright: filter cut-off.          wind: 0 to 1.
     bell: seconds between bells.     voice: how present the melody is. rest: seconds between its phrases.
     tempo: beats a minute.           pulse: how strong the drum can get, and its pattern.
     moves: where the bass may go for a while, in semitones from the root. */
  var MOODS = [
    { root: 61.7, scale: MINOR, bright: 420, wind: 0.45, bell: 15, voice: 0.55, rest: 14, tempo: 50, pulse: 0.55, pat: HEART, moves: [-2, 5] },     /* I    The Museum of Man   */
    { root: 73.4, scale: HIJAZ, bright: 950, wind: 0.12, bell: 7, voice: 0.7, rest: 9, tempo: 60, pulse: 0.4, pat: HEART, moves: [1, 5] },          /* II   The Golden Planet   */
    { root: 65.4, scale: DORIAN, bright: 700, wind: 0.35, bell: 10, voice: 0.8, rest: 10, tempo: 54, pulse: 0.25, pat: HEART, moves: [-2, 5] },     /* III  Caladan             */
    { root: 49.0, scale: PHRYGIAN, bright: 300, wind: 0.18, bell: 17, voice: 0.4, rest: 16, tempo: 44, pulse: 0.7, pat: HEART, moves: [1, -2] },    /* IV   The Harkonnens      */
    { root: 73.4, scale: OPEN, bright: 820, wind: 0.08, bell: 5, voice: 0.55, rest: 9, tempo: 76, pulse: 0.9, pat: MARCH, moves: [5, -2] },         /* V    The Gymnasium       */
    { root: 55.0, scale: HIJAZ, bright: 600, wind: 0.6, bell: 8, voice: 0.55, rest: 11, tempo: 58, pulse: 0.6, pat: HEART, moves: [1, 5] },         /* VI   The Deadly Trap     */
    { root: 58.3, scale: HIJAZ, bright: 480, wind: 0.9, bell: 13, voice: 0.65, rest: 13, tempo: 48, pulse: 0.3, pat: HEART, moves: [1, -2] },       /* VII  The Desert          */
    { root: 82.4, scale: DORIAN, bright: 1150, wind: 0.22, bell: 6, voice: 0.9, rest: 8, tempo: 56, pulse: 0.35, pat: HEART, moves: [5, -2] },      /* VIII The Water of Life   */
    { root: 51.9, scale: PHRYGIAN, bright: 450, wind: 0.5, bell: 9, voice: 0.45, rest: 12, tempo: 84, pulse: 1.0, pat: MARCH, moves: [1, -2] },     /* IX   The War             */
    { root: 73.4, scale: OPEN, bright: 1300, wind: 0.3, bell: 5, voice: 1.0, rest: 7, tempo: 52, pulse: 0.3, pat: HEART, moves: [5, 7] }            /* X    I Am Paul           */
  ];
  var REST = { root: 58.3, scale: HIJAZ, bright: 520, wind: 0.55, bell: 14, voice: 0.5, rest: 15, tempo: 48, pulse: 0, pat: HEART, moves: [1, -2] };   /* contents, art, search */

  function M() { return mood || REST; }
  /* where the chord and the melody sit: two octaves above the drone, or three where that would still be too low to hear on a small speaker */
  function high(m) { return m.root * (m.root * 4 >= 240 ? 4 : 8); }
  function pick(a) { return a[Math.floor(Math.random() * a.length)]; }
  function semis(n) { return Math.pow(2, n / 12); }
  function noise(seconds, channels, shape) {
    var buf = ctx.createBuffer(channels, Math.floor(ctx.sampleRate * seconds), ctx.sampleRate);
    for (var c = 0; c < channels; c++) { var d = buf.getChannelData(c); for (var i = 0; i < d.length; i++) d[i] = (Math.random() * 2 - 1) * (shape ? shape(i / d.length) : 1); }
    return buf;
  }
  function gain(v, to) { var g = ctx.createGain(); g.gain.value = v; if (to) g.connect(to); return g; }
  function pan(v, to) {                                                   /* a place between the left and right speakers; older browsers get the middle */
    if (!ctx.createStereoPanner) return gain(1, to);
    var p = ctx.createStereoPanner(); p.pan.value = v; p.connect(to); return p;
  }

  function build() {
    ctx = new AC();
    master = gain(0);
    var limit = ctx.createDynamicsCompressor(); limit.threshold.value = -14; limit.ratio.value = 6;
    tap = ctx.createAnalyser(); tap.fftSize = 2048;
    master.connect(limit); limit.connect(tap); tap.connect(ctx.destination);
    bus = gain(1, master);

    /* a room: four seconds of decaying noise, different in each ear, with the top rolled off */
    var room = ctx.createConvolver(); room.buffer = noise(4.2, 2, function (t) { return Math.pow(1 - t, 2.6); });
    var roomTone = ctx.createBiquadFilter(); roomTone.type = "lowpass"; roomTone.frequency.value = 3600;
    roomIn = gain(1, room); room.connect(roomTone); roomTone.connect(gain(0.5, master));

    /* the drone: the root and its fifth, each as two slightly detuned voices set apart left and right */
    tone = ctx.createBiquadFilter(); tone.type = "lowpass"; tone.Q.value = 0.8;
    droneLevel = gain(1, bus); tone.connect(droneLevel); droneLevel.connect(gain(0.45, roomIn));
    [["sawtooth", 1, 0.048, -0.5], ["sawtooth", 1.004, 0.048, 0.5], ["sawtooth", 1.4983, 0.026, -0.25], ["sawtooth", 1.5026, 0.026, 0.25], ["triangle", 2.003, 0.03, 0]].forEach(function (v) {
      var o = ctx.createOscillator(); o.type = v[0]; o.connect(gain(v[2], pan(v[3], tone))); o.start();
      voices.push({ osc: o, ratio: v[1] });
    });
    var lfo = ctx.createOscillator(); lfo.frequency.value = 0.045; lfoDepth = gain(0, tone.frequency); lfo.connect(lfoDepth); lfo.start();
    /* an octave below, a sine that swells and fades */
    subOsc = ctx.createOscillator(); var subLevel = gain(0.11, droneLevel); subOsc.connect(subLevel); subOsc.start();
    var breath = ctx.createOscillator(); breath.frequency.value = 0.11; breath.connect(gain(0.035, subLevel.gain)); breath.start();

    /* the chord: root, third or second, fifth and octave, two octaves above the drone. A phone's speaker
       cannot play the drone itself, so this is what carries the harmony there. Each side breathes at its own pace. */
    var padTone = ctx.createBiquadFilter(); padTone.type = "lowpass"; padTone.frequency.value = 1500; padTone.Q.value = 0.5;
    padLevel = gain(1, bus); padTone.connect(padLevel); padLevel.connect(gain(0.7, roomIn));
    [[1, 0.066, -0.6, 0.07], [0, 0.05, 0.3, 0.093], [1.5, 0.054, 0.6, 0.061], [2, 0.038, -0.3, 0.083]].forEach(function (v) {
      var o = ctx.createOscillator(), level = gain(v[1], pan(v[2], padTone)), sway = ctx.createOscillator();
      o.type = "sawtooth"; o.connect(level); o.start();
      sway.frequency.value = v[3]; sway.connect(gain(v[1] * 0.45, level.gain)); sway.start();
      pad.push({ osc: o, ratio: v[0] });                                 /* ratio 0 marks the voice that takes the third */
    });

    /* wind: two loops of noise, one in each ear, each through a band-pass filter that wanders */
    [-0.65, 0.65].forEach(function (side) {
      var src = ctx.createBufferSource(); src.buffer = noise(5, 1); src.loop = true;
      var band = ctx.createBiquadFilter(); band.type = "bandpass"; band.Q.value = 0.9; band.frequency.value = 500;
      var level = gain(0, pan(side, bus)); src.connect(band); band.connect(level); src.start();
      wind.push({ band: band, level: level });
    });

    /* bells go through an echo into the room */
    bellBus = gain(0.7, bus);
    var echo = ctx.createDelay(1.5); echo.delayTime.value = 0.46; var back = gain(0.34, echo);
    bellBus.connect(echo); echo.connect(back); echo.connect(roomIn); bellBus.connect(roomIn);

    /* the melody: a soft voice, mostly heard through the room */
    leadTone = ctx.createBiquadFilter(); leadTone.type = "lowpass"; leadTone.Q.value = 0.7; leadTone.frequency.value = 1300;
    leadTone.connect(gain(0.75, bus)); leadTone.connect(gain(0.9, roomIn));
    vib = ctx.createOscillator(); vib.frequency.value = 5.1; vib.start();

    /* the drum */
    drumBus = gain(1, bus); drumBus.connect(gain(0.22, roomIn));
    slap = noise(0.3, 1); hiss = noise(3, 1);
  }

  /* move every sustained sound to where the mood, the intensity and the bass note now say it should be */
  function apply(seconds) {
    var m = M(), t = ctx.currentTime, tau = seconds / 3, root = m.root * semis(shift), cut = m.bright * (0.75 + 0.9 * intensity);
    voices.forEach(function (v) { v.osc.frequency.setTargetAtTime(root * v.ratio, t, tau); });
    subOsc.frequency.setTargetAtTime(root * 0.5, t, tau);
    var third = m.scale.indexOf(3) >= 0 ? 3 : m.scale.indexOf(4) >= 0 ? 4 : 2;         /* minor, major, or neither */
    var up = high(m) * semis(shift);
    pad.forEach(function (v) { v.osc.frequency.setTargetAtTime(v.ratio ? up * v.ratio : up * semis(third), t, tau); });
    padLevel.gain.setTargetAtTime(0.85 + 0.5 * intensity, t, tau);
    tone.frequency.setTargetAtTime(cut, t, tau); lfoDepth.gain.setTargetAtTime(cut * 0.3, t, tau);
    droneLevel.gain.setTargetAtTime(0.8 + 0.45 * intensity, t, tau);
    leadTone.frequency.setTargetAtTime(900 + m.bright * 0.6, t, tau);
  }

  /* ---- the instruments: each plays one sound at a given time ---- */
  function drum(t, loud, big) {
    var o = ctx.createOscillator(), g = gain(0, drumBus), len = big ? 1.6 : 0.42;
    o.frequency.setValueAtTime(big ? 70 : 92, t); o.frequency.exponentialRampToValueAtTime(big ? 28 : 44, t + (big ? 0.5 : 0.16));
    g.gain.setValueAtTime(0.0001, t); g.gain.linearRampToValueAtTime(loud * 0.5, t + 0.006); g.gain.exponentialRampToValueAtTime(0.0001, t + len);
    o.connect(g); o.start(t); o.stop(t + len + 0.05);
    var body = ctx.createOscillator(), bg = gain(0, drumBus);           /* the note of the drum itself, high enough for a small speaker */
    body.type = "triangle"; body.frequency.setValueAtTime(big ? 150 : 205, t); body.frequency.exponentialRampToValueAtTime(big ? 95 : 130, t + 0.14);
    bg.gain.setValueAtTime(0.0001, t); bg.gain.linearRampToValueAtTime(loud * 0.3, t + 0.005); bg.gain.exponentialRampToValueAtTime(0.0001, t + (big ? 0.7 : 0.26));
    body.connect(bg); body.start(t); body.stop(t + (big ? 0.8 : 0.3));
    var n = ctx.createBufferSource(), band = ctx.createBiquadFilter(), ng = gain(0, drumBus);    /* the hand on the skin */
    n.buffer = slap; band.type = "bandpass"; band.frequency.value = 1700; band.Q.value = 0.9;
    ng.gain.setValueAtTime(loud * 0.16, t); ng.gain.exponentialRampToValueAtTime(0.0001, t + 0.07);
    n.connect(band); band.connect(ng); n.start(t); n.stop(t + 0.1);
  }
  function crash(t, loud) {                                               /* a wash of high noise that dies away */
    var n = ctx.createBufferSource(), high = ctx.createBiquadFilter(), g = gain(0, pan(0, bus));
    n.buffer = hiss; high.type = "highpass"; high.frequency.value = 4800;
    g.gain.setValueAtTime(0.0001, t); g.gain.linearRampToValueAtTime(loud, t + 0.04); g.gain.exponentialRampToValueAtTime(0.0001, t + 2.4);
    n.connect(high); high.connect(g); g.connect(gain(0.6, roomIn)); n.start(t); n.stop(t + 2.6);
  }
  function freqOf(m, degree) {                                            /* a step of the scale, in the register of the chord, on the home note */
    var n = m.scale.length, oct = Math.floor(degree / n), i = ((degree % n) + n) % n;
    return high(m) * semis(m.scale[i] + 12 * oct);
  }
  function steady(m) { var out = []; m.scale.forEach(function (s, i) { if (s === 0 || s === 7) out.push(i); }); return out; }   /* the root and the fifth */
  function bell(t) {
    var m = M(), deg = Math.random() < 0.55 ? pick(steady(m)) : Math.floor(Math.random() * m.scale.length);
    var f = freqOf(m, deg + m.scale.length * Math.floor(Math.random() * 2)), length = 4 + Math.random() * 4, loud = 0.045 + Math.random() * 0.055;
    var place = pan(Math.random() * 1.4 - 0.7, bellBus);
    [[1, 1], [2.76, 0.22], [5.4, 0.07]].forEach(function (p) {            /* a struck-metal spectrum */
      var o = ctx.createOscillator(), g = gain(0, place); o.frequency.value = f * p[0];
      g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(loud * p[1], t + 0.015); g.gain.exponentialRampToValueAtTime(0.0001, t + length / p[0]);
      o.connect(g); o.start(t); o.stop(t + length / p[0] + 0.1);
    });
  }
  function sing(t, f, seconds, loud) {
    var g = gain(0, leadTone), rise = Math.min(0.9, seconds * 0.35), fall = 1.8, wobble = gain(0);
    wobble.gain.setValueAtTime(0, t); wobble.gain.linearRampToValueAtTime(f * 0.006, t + 0.9);   /* the vibrato comes in after the note has started */
    vib.connect(wobble);
    [["sawtooth", 1, 1], ["triangle", 1.003, 0.8]].forEach(function (v) {
      var o = ctx.createOscillator(); o.type = v[0]; o.frequency.value = f * v[1]; wobble.connect(o.frequency);
      o.connect(gain(v[2], g)); o.start(t); o.stop(t + seconds + fall + 0.1);
    });
    g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(loud, t + rise); g.gain.setValueAtTime(loud, t + seconds);
    g.gain.setTargetAtTime(0, t + seconds, fall / 4);
    setTimeout(function () { try { vib.disconnect(wobble); } catch (e) {} }, (t - ctx.currentTime + seconds + fall + 0.5) * 1000);
  }

  /* ---- the melody: one short motif per stretch, repeated at different heights ---- */
  function nearest(m, degree) { var s = steady(m), n = m.scale.length, best = degree, far = 99; for (var o = -1; o <= 1; o++) s.forEach(function (i) { var d = i + o * n; if (Math.abs(d - degree) < far) { far = Math.abs(d - degree); best = d; } }); return best; }
  function newMotif(m) {
    var d = pick(steady(m)), out = [], n = 3 + Math.floor(Math.random() * 3);
    for (var i = 0; i < n; i++) { out.push([d, pick([2, 2, 3, 4])]); d = Math.max(-2, Math.min(m.scale.length + 2, d + pick([-2, -1, -1, 1, 1, 2]))); }
    return out;
  }
  function note(t) {                                                      /* plays the next note; returns the seconds until the one after */
    var m = M(), beat = 60 / m.tempo;
    if (!phrase) {
      if (!motif || Math.random() < 0.3) motif = newMotif(m);
      var lift = pick([0, 0, 0, 1, 2, -1]);
      phrase = motif.map(function (x) { return [x[0] + lift, x[1]]; });
      phrase[phrase.length - 1] = [nearest(m, phrase[phrase.length - 1][0]), 6];             /* come to rest on the root or the fifth */
      at = 0;
    }
    var p = phrase[at++], seconds = p[1] * beat;
    sing(t, freqOf(m, p[0]), seconds, m.voice * 0.13 * (0.7 + 0.6 * intensity));
    if (at < phrase.length) return seconds;
    phrase = null;                                                        /* the phrase is over: leave a silence before the next */
    return seconds + m.rest * (1.5 - intensity) * (0.7 + Math.random() * 0.6);
  }

  /* ---- the bass note leaves home for a while, then returns ---- */
  function turn() {
    if (shift) { shift = 0; apply(7); return 35 + Math.random() * 30; }
    shift = pick(M().moves); apply(7); return 12 + Math.random() * 7;
  }
  function gust() {
    var m = M(), t = ctx.currentTime;
    wind.forEach(function (w) { w.band.frequency.setTargetAtTime(280 + Math.random() * 900, t, 2.5); w.level.gain.setTargetAtTime(m.wind * (0.04 + Math.random() * 0.11), t, 2); });
  }

  /* ---- the clock. Everything is placed on the audio clock a little ahead of time. When the tab is
     hidden the audio clock stops, so nothing is placed, and nothing piles up to ring at once later. ---- */
  function tick() {
    if (!playing || ctx.state !== "running") return;
    var m = M(), now = ctx.currentTime, until = now + 0.4, soon = function (x) { return Math.max(x, now + 0.02); };
    if (!next) next = { beat: now + 0.1, bell: now + 2.5, note: now + 5, gust: now, turn: now + 30 + Math.random() * 20 };
    while (next.beat < until) {
      var hit = m.pat[step], loud = m.pulse * Math.min(1, Math.max(0, (intensity - 0.4) / 0.5));
      if (hit && loud > 0.02) drum(soon(next.beat), loud * hit);
      step = (step + 1) % 8; next.beat += 30 / m.tempo;                   /* eighth notes */
    }
    if (next.bell < until) { bell(soon(next.bell)); next.bell = soon(next.bell) + m.bell * (0.5 + Math.random()) * (1.3 - 0.6 * intensity); }
    if (next.note < until) { var start = soon(next.note); next.note = start + note(start); }
    if (next.gust < until) { gust(); next.gust = now + 2.5 + Math.random() * 4; }
    if (next.turn < until) next.turn = now + turn();
  }

  function start() {
    if (!AC) return false;
    if (!ctx) build();
    playing = true; apply(0.3);
    master.gain.cancelScheduledValues(ctx.currentTime); master.gain.setTargetAtTime(0.8, ctx.currentTime, 1.4);
    if (ctx.state !== "running" && !document.hidden) ctx.resume();
    clearInterval(timer); timer = setInterval(tick, 120);
    return true;
  }
  function stop() {
    if (!ctx) return;
    playing = false; clearInterval(timer);
    master.gain.cancelScheduledValues(ctx.currentTime); master.gain.setTargetAtTime(0, ctx.currentTime, 0.5);
    setTimeout(function () { if (!playing && ctx.state === "running") ctx.suspend(); }, 2500);
  }
  document.addEventListener("visibilitychange", function () {             /* do not play to a hidden tab */
    if (!ctx || !playing) return;
    if (document.hidden) ctx.suspend(); else ctx.resume();
  });

  window.DuneScore = {
    supported: !!AC,
    playing: function () { return playing; },
    toggle: function () { if (playing) { stop(); return false; } return start(); },
    /* k: chapter index 0 to 9, or anything else for the resting mood */
    setMood: function (k) { var m = MOODS[k] || null; if (m === mood) return; mood = m; shift = 0; motif = null; phrase = null; if (ctx && playing) apply(6); },
    /* 0 is hushed, 1 is full. Above 0.4 the drum comes in. The pages leave it at 0.35. */
    setIntensity: function (x, seconds) { intensity = Math.max(0, Math.min(1, x)); if (ctx && playing) apply(seconds || 3); },
    /* a moment: "hit" is a deep drum and a crash, "swell" a rise and fall, "drop" a sudden hush */
    accent: function (kind) {
      if (!ctx || !playing) return;
      var t = ctx.currentTime + 0.03, g = droneLevel.gain, base = 0.8 + 0.45 * intensity;
      if (kind === "hit") { drum(t, 1.1, true); crash(t, 0.06); }
      if (kind === "swell") { g.cancelScheduledValues(t); g.setTargetAtTime(base * 1.7, t, 0.8); g.setTargetAtTime(base, t + 2.6, 1.6); crash(t + 1.6, 0.03); }
      if (kind === "drop") { g.cancelScheduledValues(t); g.setTargetAtTime(base * 0.3, t, 0.25); g.setTargetAtTime(base, t + 4, 1.5); }
    },
    /* loudest sample in the last few milliseconds, 0 to 1 (used to check it is audible and not clipping) */
    level: function () {
      if (!tap) return 0; var d = new Float32Array(tap.fftSize), peak = 0; tap.getFloatTimeDomainData(d);
      for (var i = 0; i < d.length; i++) peak = Math.max(peak, Math.abs(d[i]));
      return peak;
    }
  };
})();
