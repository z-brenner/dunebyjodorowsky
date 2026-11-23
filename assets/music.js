/* A generated score. Nothing here is a recording: the browser synthesises a low drone, wind
   and sparse bell notes, with a different mood for each chapter. It is silent until the
   listener turns it on. Written for this edition; it is not music made for the film. */
(function () {
  "use strict";
  var AC = window.AudioContext || window.webkitAudioContext;
  var ctx = null, master, tone, lfoDepth, voices = [], windLevel, windBand, bellBus, tap, playing = false, bellTimer = 0, windTimer = 0, mood = null;

  var HIJAZ = [0, 1, 4, 5, 7, 8, 10], MINOR = [0, 2, 3, 5, 7, 8, 10], OPEN = [0, 2, 7, 9, 12];
  /* root: drone pitch in Hz. bright: filter cut-off. wind: 0 to 1. every: seconds between bell notes. */
  var MOODS = [
    { root: 61.7, bright: 420, wind: 0.45, every: 15, scale: MINOR },   /* I    The Museum of Man   */
    { root: 73.4, bright: 950, wind: 0.12, every: 7, scale: HIJAZ },    /* II   The Golden Planet   */
    { root: 65.4, bright: 700, wind: 0.35, every: 10, scale: MINOR },   /* III  Caladan             */
    { root: 49.0, bright: 300, wind: 0.18, every: 17, scale: HIJAZ },   /* IV   The Harkonnens      */
    { root: 73.4, bright: 820, wind: 0.08, every: 5, scale: OPEN },     /* V    The Gymnasium       */
    { root: 55.0, bright: 600, wind: 0.6, every: 8, scale: HIJAZ },     /* VI   The Deadly Trap     */
    { root: 58.3, bright: 480, wind: 0.9, every: 13, scale: HIJAZ },    /* VII  The Desert          */
    { root: 82.4, bright: 1150, wind: 0.22, every: 6, scale: OPEN },    /* VIII The Water of Life   */
    { root: 51.9, bright: 450, wind: 0.5, every: 9, scale: MINOR },     /* IX   The War             */
    { root: 73.4, bright: 1300, wind: 0.3, every: 5, scale: OPEN }      /* X    I Am Paul           */
  ];
  var REST = { root: 58.3, bright: 520, wind: 0.55, every: 14, scale: HIJAZ };   /* contents, art, search */

  function noise(seconds, shape) {
    var buf = ctx.createBuffer(1, Math.floor(ctx.sampleRate * seconds), ctx.sampleRate), d = buf.getChannelData(0);
    for (var i = 0; i < d.length; i++) d[i] = (Math.random() * 2 - 1) * (shape ? shape(i / d.length) : 1);
    return buf;
  }
  function build() {
    ctx = new AC();
    master = ctx.createGain(); master.gain.value = 0;
    var limit = ctx.createDynamicsCompressor(); limit.threshold.value = -14; limit.ratio.value = 6;
    tap = ctx.createAnalyser(); tap.fftSize = 2048;
    master.connect(limit); limit.connect(tap); tap.connect(ctx.destination);

    /* a room: three seconds of decaying noise as an impulse response */
    var room = ctx.createConvolver(); room.buffer = noise(3.2, function (t) { return Math.pow(1 - t, 2.4); });
    var wet = ctx.createGain(); wet.gain.value = 0.5; room.connect(wet); wet.connect(master);

    /* the drone: four voices through one slowly breathing low-pass filter */
    tone = ctx.createBiquadFilter(); tone.type = "lowpass"; tone.Q.value = 0.8; tone.connect(master); tone.connect(room);
    [["sawtooth", 1, 0.085], ["sawtooth", 1.004, 0.085], ["sine", 0.5, 0.2], ["triangle", 1.498, 0.05]].forEach(function (v) {
      var o = ctx.createOscillator(), g = ctx.createGain(); o.type = v[0]; g.gain.value = v[2]; o.connect(g); g.connect(tone); o.start();
      voices.push({ osc: o, ratio: v[1] });
    });
    var lfo = ctx.createOscillator(); lfo.frequency.value = 0.045; lfoDepth = ctx.createGain(); lfo.connect(lfoDepth); lfoDepth.connect(tone.frequency); lfo.start();

    /* wind: looped noise through a band-pass filter that wanders */
    var src = ctx.createBufferSource(); src.buffer = noise(4); src.loop = true;
    windBand = ctx.createBiquadFilter(); windBand.type = "bandpass"; windBand.Q.value = 0.9; windBand.frequency.value = 500;
    windLevel = ctx.createGain(); windLevel.gain.value = 0;
    src.connect(windBand); windBand.connect(windLevel); windLevel.connect(master); src.start();

    /* bells go through an echo into the room */
    bellBus = ctx.createGain(); bellBus.gain.value = 0.55;
    var echo = ctx.createDelay(1.5); echo.delayTime.value = 0.46; var back = ctx.createGain(); back.gain.value = 0.34;
    bellBus.connect(echo); echo.connect(back); back.connect(echo); echo.connect(room); bellBus.connect(room); bellBus.connect(master);
  }
  function apply(seconds) {
    var m = mood || REST, t = ctx.currentTime, tau = seconds / 3;
    voices.forEach(function (v) { v.osc.frequency.setTargetAtTime(m.root * v.ratio, t, tau); });
    tone.frequency.setTargetAtTime(m.bright, t, tau); lfoDepth.gain.setTargetAtTime(m.bright * 0.35, t, tau);
  }
  function gust() {
    if (!playing) return;
    var m = mood || REST, t = ctx.currentTime;
    windBand.frequency.setTargetAtTime(280 + Math.random() * 900, t, 2.5);
    windLevel.gain.setTargetAtTime(m.wind * (0.05 + Math.random() * 0.13), t, 2);
    windTimer = setTimeout(gust, 2500 + Math.random() * 4000);
  }
  function bell() {
    if (!playing) return;
    var m = mood || REST, t = ctx.currentTime + 0.05;
    var step = m.scale[Math.floor(Math.random() * m.scale.length)] + 12 * (2 + Math.floor(Math.random() * 2));
    var f = m.root * Math.pow(2, step / 12), length = 4 + Math.random() * 4, loud = 0.05 + Math.random() * 0.06;
    [[1, 1], [2.76, 0.22], [5.4, 0.07]].forEach(function (p) {            /* a struck-metal spectrum */
      var o = ctx.createOscillator(), g = ctx.createGain(); o.frequency.value = f * p[0];
      g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(loud * p[1], t + 0.015); g.gain.exponentialRampToValueAtTime(0.0001, t + length / p[0]);
      o.connect(g); g.connect(bellBus); o.start(t); o.stop(t + length / p[0] + 0.1);
    });
    bellTimer = setTimeout(bell, m.every * (0.5 + Math.random()) * 1000);
  }
  function start() {
    if (!AC) return false;
    if (!ctx) build();
    if (ctx.state === "suspended") ctx.resume();
    playing = true; apply(0.3);
    master.gain.cancelScheduledValues(ctx.currentTime); master.gain.setTargetAtTime(0.6, ctx.currentTime, 1.4);
    clearTimeout(bellTimer); clearTimeout(windTimer); gust(); bellTimer = setTimeout(bell, 2500);
    return true;
  }
  function stop() {
    if (!ctx) return;
    playing = false; clearTimeout(bellTimer); clearTimeout(windTimer);
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
    setMood: function (k) { var m = MOODS[k] || null; if (m === mood) return; mood = m; if (ctx && playing) apply(6); },
    /* loudest sample in the last few milliseconds, 0 to 1 (used to check it is audible and not clipping) */
    level: function () {
      if (!tap) return 0; var d = new Float32Array(tap.fftSize), peak = 0; tap.getFloatTimeDomainData(d);
      for (var i = 0; i < d.length; i++) peak = Math.max(peak, Math.abs(d[i]));
      return peak;
    }
  };
})();
