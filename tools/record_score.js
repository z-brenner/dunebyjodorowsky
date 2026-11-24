// Record the site's generated score (assets/music.js) to a file, in real time, in a headless browser.
// usage: node record_score.js <seconds> <chapter index 0-9> <out.webm> [cues.json]
// cues.json is a list of moments: [{ "t": seconds, "intensity": 0 to 1, "ramp": seconds, "accent": "hit" | "swell" | "drop" }, ...]
// A film's cues come from its edit list: film_scene.py <name> <fonts> <out> --cues, or film_opening.py --cues <out.json>.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
(async () => {
  const seconds = +process.argv[2], mood = +process.argv[3], out = process.argv[4];
  const cues = process.argv[5] ? JSON.parse(fs.readFileSync(process.argv[5], 'utf8')) : [];
  const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const pg = await b.newPage();
  pg.on('pageerror', e => console.log('ERR', e.message));
  await pg.goto('about:blank');
  // Send the score to a recorder instead of the loudspeaker.
  await pg.evaluate(() => {
    const Real = window.AudioContext;
    window.AudioContext = class extends Real {
      constructor() { super(); this.__rec = this.createMediaStreamDestination(); window.__ctx = this; }
      get destination() { return this.__rec; }
    };
  });
  await pg.addScriptTag({ content: fs.readFileSync(path.join(__dirname, '..', 'assets', 'music.js'), 'utf8') });
  const b64 = await pg.evaluate(async ([seconds, mood, cues]) => {
    const S = window.DuneScore;
    S.setMood(mood);
    const first = cues.find(c => c.t <= 0 && c.intensity !== undefined);
    if (first) S.setIntensity(first.intensity, 0.1);
    S.toggle();
    await new Promise(r => setTimeout(r, 300));
    const rec = new MediaRecorder(window.__ctx.__rec.stream, { mimeType: 'audio/webm;codecs=opus', audioBitsPerSecond: 192000 });
    const parts = []; rec.ondataavailable = e => parts.push(e.data);
    rec.start(1000);
    const t0 = performance.now(); let played = 0;
    cues.forEach(c => setTimeout(() => {
      if (c.intensity !== undefined) S.setIntensity(c.intensity, c.ramp || 3);
      if (c.accent) S.accent(c.accent);
      played++;
    }, Math.max(0, c.t * 1000 - (performance.now() - t0))));
    let peak = 0; const iv = setInterval(() => { peak = Math.max(peak, S.level()); }, 250);
    await new Promise(r => setTimeout(r, seconds * 1000));
    clearInterval(iv); rec.stop(); await new Promise(r => { rec.onstop = r; });
    const buf = new Uint8Array(await new Blob(parts).arrayBuffer()); let s = '';
    for (let i = 0; i < buf.length; i += 32768) s += String.fromCharCode.apply(null, buf.subarray(i, i + 32768));
    return [btoa(s), peak, window.__ctx.state, played];
  }, [seconds, mood, cues]);
  fs.writeFileSync(out, Buffer.from(b64[0], 'base64'));
  console.log('recorded', out, fs.statSync(out).size, 'bytes, peak level', b64[1].toFixed(3), 'context', b64[2], '| cues played', b64[3], 'of', cues.length);
  await b.close();
})();
