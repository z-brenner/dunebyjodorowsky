/* Jodorowsky's Dune. The early draft of the screenplay, told scene by scene with
   the surviving art beside it. Plates keep the page numbers of the source file. */
(function () {
  "use strict";
  var D = window.DUNE, P = D.plates, SC = window.DUNE_SCRIPT || { scenes: [] };
  var $ = function (s, el) { return (el || document).querySelector(s); };
  var $$ = function (s, el) { return Array.prototype.slice.call((el || document).querySelectorAll(s)); };
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
  var pad = function (i) { return ("00" + i).slice(-3); };
  var roman = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"];
  var KIND = { board: "Storyboard sheet", frame: "Storyboard frame", color: "Colour storyboard", design: "Costume", lineup: "Cast sheet", machine: "Machine", giger: "Giedi Prime", vision: "Screenplay picture", script: "Script page", relic: "The book", tarot: "Notebook", apoc: "From elsewhere" };

  var src = function (i) { return "art/" + pad(i) + ".webp"; };
  /* The scan as found. Normally plates/NNN.jpg; a hosted copy may instead bundle the scans
     into a few pack files (window.DUNE_PACK) and cut each one out on request. */
  var PACK = window.DUNE_PACK, packs = {}, cut = {};
  function original(i) {
    if (!PACK) return Promise.resolve("plates/" + pad(i) + ".jpg");
    if (cut[i]) return Promise.resolve(cut[i]);
    var e = PACK.at[i];
    packs[e[0]] = packs[e[0]] || fetch(PACK.files[e[0]]).then(function (r) { return r.arrayBuffer(); });
    return packs[e[0]].then(function (buf) { return (cut[i] = URL.createObjectURL(new Blob([buf.slice(e[1], e[1] + e[2])], { type: "image/jpeg" }))); });
  }
  var size = function (i) { return P[i].r ? [P[i].r[0], P[i].r[1]] : [P[i].w, P[i].h]; };
  var state = function (i) { return P[i].r && P[i].r[2].length ? "Restored" : "Original scan"; };
  var placing = { s: "Placed by the screenplay", l: "Placed by this edition (likely the screenplay's picture)", e: "Placed by this edition" };

  /* which scene each plate sits in */
  var SCENE_OF = {}, ART = {};
  SC.scenes.forEach(function (sc) { sc.b.forEach(function (b) { if (b[0] === "i" && b[3] !== null && SCENE_OF[b[3]] === undefined) SCENE_OF[b[3]] = sc.n; }); });
  Object.keys(D.place).forEach(function (n) { D.place[n].forEach(function (i) { if (SCENE_OF[i] === undefined) SCENE_OF[i] = +n; }); });
  SC.scenes.forEach(function (sc) {
    var ids = [];
    sc.b.forEach(function (b) { if (b[0] === "i" && b[3] !== null && SCENE_OF[b[3]] === sc.n && ids.indexOf(b[3]) < 0) ids.push(b[3]); });
    (D.place[sc.n] || []).forEach(function (i) { if (ids.indexOf(i) < 0) ids.push(i); });
    ART[sc.n] = ids;
  });
  var chapterOf = function (n) { for (var k = 0; k < D.chapters.length; k++) if (n >= D.chapters[k].a && n <= D.chapters[k].b) return k; return 0; };
  /* Shots: every storyboard frame and screenplay picture, in story order. A sheet that could be
     cut into frames gives one shot per frame; anything else is one shot. */
  var SHOTS = [], FIRST_SHOT = {}, SHOT_OF = {}, IN_REEL = { board: 1, frame: 1, color: 1, vision: 1 };
  /* Steps: the film told in order. Every shot is a step. A scene with no shot is told by cards of
     its own script, a few paragraphs to a card, so the sequence runs through the whole screenplay.
     AT gives a step's place (counting from 1) by its address; FIRST gives a scene's first step. */
  var STEPS = [], AT = {}, FIRST = {}, CARDS = 0, CARD_WORDS = 70, wordsIn = function (b) { return (b[0] === "d" ? b[2] : b[1]).split(/\s+/).length; };
  function addStep(st) { STEPS.push(st); AT[st.id] = STEPS.length; if (!FIRST[st.sc]) FIRST[st.sc] = st.id; }
  function addShot(sh) { SHOTS.push(sh); if (SHOT_OF[sh.i] === undefined) SHOT_OF[sh.i] = SHOTS.length; addStep({ id: "shot-" + SHOTS.length, sc: sh.sc, sh: sh, n: SHOTS.length }); }
  SC.scenes.forEach(function (sc) {
    var before = SHOTS.length;
    (ART[sc.n] || []).forEach(function (i) {
      if (!IN_REEL[P[i].room]) return;
      if (FIRST_SHOT[sc.n] === undefined) FIRST_SHOT[sc.n] = SHOTS.length + 1;
      var k;
      if (P[i].f) for (k = 1; k <= P[i].f; k++) addShot({ i: i, k: k, sc: sc.n });
      else {
        addShot({ i: i, k: 0, sc: sc.n });                                     /* the whole sheet first, so nothing is lost */
        for (k = 1; k <= (P[i].fd || 0); k++) addShot({ i: i, k: k, sc: sc.n, d: 1 });
      }
    });
    if (SHOTS.length > before) return;
    var pages = [], cur = { b: [], w: 0 };
    sc.b.forEach(function (b, x) {
      if (b[0] !== "a" && b[0] !== "d" && b[0] !== "t") return;
      var w = wordsIn(b);
      if (cur.b.length && cur.w + w > CARD_WORDS) { pages.push(cur); cur = { b: [], w: 0 }; }
      cur.b.push(x); cur.w += w;
    });
    if (cur.b.length) pages.push(cur);
    var last = pages[pages.length - 1], prev = pages[pages.length - 2];
    if (prev && last.w < 18) { prev.b = prev.b.concat(last.b); prev.w += last.w; pages.pop(); }   /* no card for a stray last line */
    pages.forEach(function (pg, x) { CARDS++; addStep({ id: "script-" + sc.n + "-" + (x + 1), sc: sc.n, b: pg.b, w: pg.w, pg: x + 1, of: pages.length }); });
  });
  var sceneBy = {}; SC.scenes.forEach(function (sc) { sceneBy[sc.n] = sc; });
  var CH_STEPS = D.chapters.map(function () { return { first: "", at: 0, n: 0 }; }), STEP_SCENES = [];
  STEPS.forEach(function (st, x) {
    var c = CH_STEPS[chapterOf(st.sc)]; if (!c.n) { c.first = st.id; c.at = x + 1; } c.n++;
    if (STEP_SCENES[STEP_SCENES.length - 1] !== st.sc) STEP_SCENES.push(st.sc);
  });
  var stepLabel = function (st) { return st.sh ? "Shot " + st.n + " of " + SHOTS.length : (st.sc ? "Scene " + st.sc + " · script" : "Title page") + (st.of > 1 ? " " + st.pg + " of " + st.of : ""); };
  var sceneName = function (n) { return n ? "Scene " + n : "Title page"; };

  /* ---------- pieces ---------- */
  var store = { get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } }, set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} } };
  function img(i, eager, sizes) {
    var p = P[i], s = size(i), full = "art/" + pad(i) + ".webp", half = "view/" + pad(i) + ".webp";
    return "<img" + (p.v ? ' src="' + half + '" srcset="' + half + " " + p.v[0] + "w, " + full + " " + s[0] + 'w" sizes="' + (sizes || "(max-width: 860px) 94vw, 56vw") + '"' : ' src="' + full + '"') +
      ' width="' + s[0] + '" height="' + s[1] + '" alt="' + esc(p.t) + '"' + (eager ? "" : ' loading="lazy"') + ' decoding="async">';
  }
  function plate(i) {
    var p = P[i];
    return '<figure class="plate k-' + p.room + '"><a class="pl" href="#plate-' + (i + 1) + '" data-i="' + i + '">' + img(i) + "</a><figcaption><b>" + (i + 1) + "</b><span>" + esc(p.t) +
      "<small>" + esc(D.credits[p.c] || "") + " · " + state(i) + (p.by ? " · " + placing[p.by] : "") + "</small></span></figcaption></figure>";
  }
  function thumb(i) {
    var p = P[i], s = p.s, sh = D.sheets[s[0]];
    var bx = sh[1] === s[3] ? 0 : s[1] / (sh[1] - s[3]) * 100, by = sh[2] === s[4] ? 0 : s[2] / (sh[2] - s[4]) * 100;
    return '<a class="pl th" href="#plate-' + (i + 1) + '" data-i="' + i + '" title="' + esc((i + 1) + ". " + p.t) + '" style="aspect-ratio:' + s[3] + "/" + s[4] +
      ";background-image:url(thumbs/" + sh[0] + ");background-size:" + (sh[1] / s[3] * 100) + "% " + (sh[2] / s[4] * 100) + "%;background-position:" + bx + "% " + by + '%"><i>' + (i + 1) + "</i></a>";
  }
  var CREDITS = '<div class="credits"><span>michel seydoux presents</span><span>alexandro jodorowsky’s</span><strong>DUNE</strong><span>from frank herbert’s novel</span><span>design by jean giraud · machines by chris foss<br>special effects by dan o’bannon<br>dialogue by m. demuth and a. jodorowsky</span></div>';

  /* ---------- contents ---------- */
  function home() {
    var restored = P.filter(function (p) { return p.r && p.r[2].length; }).length, straight = P.filter(function (p) { return p.r && p.r[2].indexOf("straightened") >= 0; }).length;
    var withArt = SC.scenes.filter(function (sc) { return sc.n && ART[sc.n].length; }).length, at = +store.get("dune.at") || 0, lastStep = store.get("dune.step") || (+store.get("dune.shot") > 1 ? "shot-" + store.get("dune.shot") : ""), ls = STEPS[AT[lastStep] - 1];
    var film = D.chapters.map(function (c, k) {
      var cells = "";
      for (var n = c.a; n <= c.b; n++) if (ART[n]) cells += '<a href="#scene-' + n + '"' + (ART[n].length ? ' class="has"' : "") + ' title="Scene ' + n + (ART[n].length ? ", has art" : ", script only") + '"><span>Scene ' + n + "</span></a>";
      return '<div class="fm-ch"><b>' + roman[k] + "</b><div>" + cells + "</div></div>";
    }).join("");
    return '<section class="hero gut"><div class="hero-text">' + CREDITS + '<p class="lede">The film Alejandro Jodorowsky prepared in the mid-1970s and never shot, told here from what survives of it: the early draft of the screenplay, and the drawings and paintings made for it.</p>' +
      '<p class="starts"><a class="btn solid" href="#ch-1">Begin</a>' + '<a class="btn" href="#shots">Shot by shot</a><a class="btn" href="#watch">Watch</a>' + (ls && AT[lastStep] > 1 ? '<a class="btn" href="#' + lastStep + '">Continue shot by shot · ' + (ls.sh ? "shot " + ls.n : sceneName(ls.sc).toLowerCase()) + "</a>" : "") + (at ? '<a class="btn" href="#scene-' + at + '">Continue at scene ' + at + "</a>" : "") + '</p></div><figure class="hero-art"><a class="pl" href="#plate-172" data-i="171">' + img(171, true, "(max-width: 860px) 94vw, 50vw") + "</a><figcaption>Plate 172 · Chris Foss · " + state(171) + "</figcaption></figure></section>" +
      '<section class="gut"><ol class="chapters">' + D.chapters.map(function (c, k) {
        return '<li><a href="#ch-' + (k + 1) + '"><span class="ch-pic">' + img(c.key, k < 3, "(max-width: 600px) 94vw, 320px") + '</span><span class="ch-no">' + roman[k] + "</span><h2>" + esc(c.title) + "</h2><p>" + esc(c.text) + "</p><small>Scenes " + c.a + (c.b > c.a ? "–" + c.b : "") + "</small></a></li>";
      }).join("") + "</ol></section>" +
      '<section class="film gut"><h2>The whole film</h2><p>One mark for each of the ' + (SC.scenes.length - 1) + " scenes, grouped by chapter. Gold has art, " + withArt + ' in all. The rest are told by the script alone.</p><div class="film-map">' + film + "</div></section>" +
      '<section class="notes gut"><h2>What you are looking at</h2><div class="notes-grid">' +
      "<div><h3>The words</h3><p>All " + (SC.scenes.length - 1) + " scenes of the early draft, as typed. Nothing inside a scene has been rewritten or summarised. The chapter titles and their one-line descriptions are this edition’s.</p></div>" +
      "<div><h3>The pictures</h3><p>Every picture comes from one 448-page file of scans gathered online. " + restored + " of them have been restored for this edition: uneven lighting flattened on the pencil sheets, " + straight + " photographed sheets straightened, and small scans enlarged four times by a neural upscaler.</p></div>" +
      "<div><h3>What restoring changes</h3><p>Upscaling invents detail. The fine texture in a restored plate was made by a machine guessing from a small scan, and tiny typed captions do not become readable. Each plate says whether it is restored, and the viewer shows the untouched scan on request.</p></div>" +
      "<div><h3>Where pictures sit</h3><p>Some pictures are placed by the screenplay’s own list of illustrations. The rest, including all the storyboard, are placed by this edition from sequence numbers and captions. Each plate says which. The storyboard is a later version of the film than this draft, so the fit is loose.</p></div>" +
      "<div><h3>Shot by shot</h3><p>The whole film in order, one step at a time. " + SHOTS.length + " steps are shots: storyboard frames and the screenplay’s pictures, each beside its scene. The other " + CARDS + " are cards of the script, a few paragraphs each, for the " + STEP_SCENES.filter(function (n) { return n && !FIRST_SHOT[n]; }).length + " scenes no shot survives for; most of the film after scene 48 is told this way. Where a sheet’s printed grid could be found, software cut the sheet into its frames and squared each one up. On other sheets it found what frames it could; those sheets are shown whole first, then the frames as close-ups.</p></div>" +
      "<div><h3>The sound</h3><p>Off until you press Sound. It is generated in your browser as you read: a low drone, wind and a few bell notes, in a different mood for each chapter. It is not a recording and not music made for the film; this edition wrote it.</p></div>" +
      "<div><h3>The gaps</h3><p>" + withArt + " of the " + (SC.scenes.length - 1) + " scenes have art. Nothing was drawn to fill the others. Where no picture survives, the scene is told by the script alone and says so.</p></div>" +
      "<div><h3>Whose work it is</h3><p>Jean Giraud (Moebius), Chris Foss, H.R. Giger and Alejandro Jodorowsky. It remains theirs and their estates’. This is an unofficial study edition.</p></div>" +
      '</div><p class="more"><a class="btn" href="#art">See all the art</a></p></section>';
  }

  /* ---------- a chapter ---------- */
  var FOLD = 14, KEEP = 8;
  function sceneHtml(sc, open) {
    var parts = [], missing = [];
    sc.b.forEach(function (b) {
      if (b[0] === "a") parts.push("<p>" + esc(b[1]) + "</p>");
      else if (b[0] === "d") parts.push('<p class="dlg"><b>' + esc(b[1]) + "</b><span>" + esc(b[2]) + "</span></p>");
      else if (b[0] === "t") parts.push('<p class="ttl">TITLE : ' + esc(b[1]) + "</p>");
      else if (b[0] === "i" && b[3] === null) missing.push(b[1]);
    });
    var text = !open && parts.length > FOLD ? parts.slice(0, KEEP).join("") + '<div class="rest" hidden>' + parts.slice(KEEP).join("") +
      '</div><button type="button" class="btn more" data-more>Read the rest of this scene · ' + (parts.length - KEEP) + " more</button>" : parts.join("");
    var ids = ART[sc.n], art = ids.map(plate).join("");
    if (missing.length) art += '<p class="lost"><b>In the typescript, not in the archive</b>' + missing.map(esc).join("<br>") + "</p>";
    return '<article class="scene' + (ids.length ? "" : " bare") + '" id="sc-' + sc.n + '" data-n="' + sc.n + '"><header><b>' + sc.n + "</b>" + (sc.h ? "<h3>" + esc(sc.h) + "</h3>" : "") +
      (ids.length ? (FIRST_SHOT[sc.n] ? '<a class="to-shots" href="#shot-' + FIRST_SHOT[sc.n] + '">Shot by shot →</a>' : "") : "<small>No art survives for this scene</small>") + '</header><div class="sc-text">' + text + "</div>" + (art ? '<div class="sc-art" data-ctx>' + art + "</div>" : "") + "</article>";
  }
  function chapter(k) {
    var c = D.chapters[k], scenes = SC.scenes.filter(function (sc) { return sc.n >= c.a && sc.n <= c.b; }), openAll = store.get("dune.open") === "1";
    var map = scenes.map(function (sc) { return '<a href="#scene-' + sc.n + '"' + (ART[sc.n].length ? ' class="has"' : "") + ' title="Scene ' + sc.n + (sc.h ? ": " + esc(sc.h) : "") + '">' + sc.n + "</a>"; }).join("");
    var nav = '<nav class="ch-nav gut"><a class="btn" href="' + (k ? "#ch-" + k : "#home") + '">' + (k ? "← " + esc(D.chapters[k - 1].title) : "← Contents") + "</a>" +
      (k < D.chapters.length - 1 ? '<a class="btn solid" href="#ch-' + (k + 2) + '">' + esc(D.chapters[k + 1].title) + " →</a>" : '<a class="btn solid" href="#art">All the art →</a>') + "</nav>";
    return '<header class="ch-head gut"><span class="label">Chapter ' + roman[k] + " of X · scenes " + c.a + (c.b > c.a ? "–" + c.b : "") + "</span><h1>" + esc(c.title) + '</h1><p class="lede">' + esc(c.text) + "</p>" +
      '<div class="map" aria-label="Scenes in this chapter">' + map + '</div><p class="map-key"><i class="has"></i> has art <i></i> script only' +
      '<button type="button" class="link" data-fold>' + (openAll ? "Fold long scenes" : "Open every scene in full") + "</button></p></header>" +
      '<div class="scenes gut">' + scenes.map(function (sc) { return sceneHtml(sc, openAll); }).join("") + "</div>" + nav;
  }

  /* ---------- all the art ---------- */
  function art() {
    var out = '<header class="ch-head gut"><span class="label">448 plates</span><h1>The Art</h1><p class="lede">Everything in the file, grouped by hand. Open any plate to see it large and to compare the restoration with the scan as found.</p><div class="jump">' +
      D.groups.map(function (g) { return '<a href="#art" data-scroll="g-' + g.id + '">' + esc(g.title) + "</a>"; }).join("") + "</div></header>";
    var repeats = P.filter(function (p) { return p.dup !== undefined; });
    D.groups.forEach(function (g) {
      var ids = P.filter(function (p) { return g.kinds.indexOf(p.room) >= 0 && p.dup === undefined; }).map(function (p) { return p.i; });
      out += '<section class="group gut" id="g-' + g.id + '"><h2>' + esc(g.title) + " <small>" + ids.length + "</small></h2><p>" + esc(g.text) + '</p><div class="grid" data-ctx>' + ids.map(thumb).join("") + "</div></section>";
    });
    out += '<section class="group gut"><details><summary>' + repeats.length + ' repeat scans</summary><p>The same pictures in other scans, crops or watermarks. Not restored.</p><div class="grid" data-ctx>' + repeats.map(function (p) { return thumb(p.i); }).join("") + "</div></details></section>";
    return out + '<nav class="ch-nav gut"><a class="btn" href="#home">← Contents</a></nav>';
  }

  /* ---------- plate viewer ---------- */
  var view = $("#view"), stage = $("#view-stage"), vimg = $("#view-img"), side = $("#view-side"), ctx = [], cur = -1, showOrig = false, zoomed = false;
  function pan(e) {
    if (!zoomed || !e) return; var r = stage.getBoundingClientRect();
    vimg.style.transform = "translate(" + ((r.left + r.width / 2 - e.clientX) * 1.9) + "px," + ((r.top + r.height / 2 - e.clientY) * 1.9) + "px) scale(2.8)";
  }
  function setZoom(on, e) { zoomed = on; stage.classList.toggle("zoomed", on); if (on) pan(e); else vimg.style.transform = ""; }
  stage.addEventListener("click", function (e) { setZoom(!zoomed, e); });
  stage.addEventListener("pointermove", pan);
  function show(i) {
    var opening = view.hidden, was = side.contains(document.activeElement) ? document.activeElement.getAttribute("data-v") : null;
    if (opening) opener = document.activeElement;
    var p = P[i], s; cur = i; setZoom(false); view.hidden = false; document.body.style.overflow = "hidden";
    var isRestored = p.r && p.r[2].length;
    if (!isRestored) showOrig = false;
    s = showOrig ? [p.w, p.h] : size(i);
    vimg.width = s[0]; vimg.height = s[1]; vimg.alt = p.t;
    if (p.r && !showOrig) vimg.src = src(i);
    else { vimg.removeAttribute("src"); original(i).then(function (u) { if (cur === i) vimg.src = u; }); }
    var rows = "", row = function (k, v) { rows += "<div><dt>" + k + "</dt><dd>" + v + "</dd></div>"; };
    row("By", esc(D.credits[p.c] || ""));
    row("What it is", KIND[p.room] + (p.seq ? ", sequence " + p.seq.join(" and ") + " of the storyboard" : ""));
    if (p.cap) row("Typed beneath the frame", esc(p.cap[1]) + "<br><em>" + esc(p.cap[0]) + "</em>");
    if (SCENE_OF[i] !== undefined) row("In the story", '<a href="#scene-' + SCENE_OF[i] + '">Scene ' + SCENE_OF[i] + "</a> · " + placing[p.by || "e"]);
    if (isRestored) row("This image", (showOrig ? "The scan as found, " + p.w + " × " + p.h + " px." : "Restored: " + p.r[2].join(", ") + ". " + p.r[0] + " × " + p.r[1] + " px, from a " + p.w + " × " + p.h + " scan. Detail added by upscaling is machine-made.") +
      '<br><button type="button" class="btn" data-v="flip">' + (showOrig ? "Show the restoration" : "Show the scan as found") + "</button>");
    else row("This image", "The scan as found, " + p.w + " × " + p.h + " px. Not restored" + (p.dup !== undefined ? " (a repeat scan)." : "."));
    if (p.n) row("Note", esc(p.n).replace(/plate (\d+)/g, function (m, n) { return '<a href="#plate-' + (+n + 1) + '">plate ' + (+n + 1) + "</a>"; }));
    if (p.var) row("Other scans of this picture", p.var.map(function (v) { return '<a href="#plate-' + (v + 1) + '">' + (v + 1) + "</a>"; }).join(", "));
    var pos = ctx.indexOf(i);
    side.innerHTML = '<span class="label">Plate ' + (i + 1) + " of 448</span><h2>" + esc(p.t) + "</h2><dl>" + rows + '</dl><div class="view-nav"><button type="button" class="btn" data-v="prev" aria-label="Previous plate"' + (pos <= 0 ? " disabled" : "") +
      '>←</button><button type="button" class="btn" data-v="next" aria-label="Next plate"' + (pos < 0 || pos >= ctx.length - 1 ? " disabled" : "") + '>→</button><button type="button" class="btn solid" data-v="close">Close</button></div>';
    side.scrollTop = 0;
    if (opening || was) {                                                  /* keyboard focus goes into the viewer and stays on the control just used */
      var to = (was && $('[data-v="' + was + '"]:not([disabled])', side)) || $('[data-v="close"]', side);
      if (to) to.focus({ preventScroll: true });
    }
  }
  var opener = null;
  view.addEventListener("keydown", function (e) {                          /* Tab cycles inside the viewer */
    if (e.key !== "Tab") return;
    var f = $$("a[href], button:not([disabled])", side), a = document.activeElement; if (!f.length) return;
    if (!side.contains(a)) { e.preventDefault(); f[0].focus(); }
    else if (e.shiftKey && a === f[0]) { e.preventDefault(); f[f.length - 1].focus(); }
    else if (!e.shiftKey && a === f[f.length - 1]) { e.preventDefault(); f[0].focus(); }
  });
  function step(d) { var pos = ctx.indexOf(cur) + d; if (pos >= 0 && pos < ctx.length) location.hash = "plate-" + (ctx[pos] + 1); }
  function closeView() { location.hash = back; }
  side.addEventListener("click", function (e) {
    var b = e.target.closest("[data-v]"); if (!b) return;
    if (b.dataset.v === "flip") { showOrig = !showOrig; show(cur); } else if (b.dataset.v === "close") closeView(); else step(b.dataset.v === "next" ? 1 : -1);
  });

  /* ---------- shot by shot ---------- */
  function shotSrc(sh) { return sh.k ? "frames/" + pad(sh.i) + "-" + ("0" + sh.k).slice(-2) + ".webp" : (P[sh.i].v ? "view/" : "art/") + pad(sh.i) + ".webp"; }
  function para(b, cls) {
    var c = cls ? " " + cls : "";
    return b[0] === "a" ? '<p class="' + c.trim() + '">' + esc(b[1]) + "</p>" : b[0] === "d" ? '<p class="dlg' + c + '"><b>' + esc(b[1]) + "</b><span>" + esc(b[2]) + "</span></p>" : '<p class="ttl' + c + '">TITLE : ' + esc(b[1]) + "</p>";
  }
  function stepHtml(pos) {
    var st = STEPS[pos - 1], sh = st.sh, p = sh && P[sh.i], sc = sceneBy[st.sc], k = chapterOf(st.sc), text = "", stage;
    /* the scene's script, with the lines on the card marked, and the typescript's own picture notes where it has them */
    sc.b.forEach(function (b, x) {
      if (b[0] === "a" || b[0] === "d" || b[0] === "t") text += para(b, st.b && st.b.indexOf(x) >= 0 ? "now" : "");
      else if (b[0] === "i") text += '<p class="pic' + (sh && b[3] === sh.i ? " now" : "") + '"><b>Picture in the typescript</b>' + esc(b[1]) + " · " +
        (b[3] === null ? "not in the archive" : '<a href="#' + (SHOT_OF[b[3]] ? "shot-" + SHOT_OF[b[3]] : "plate-" + (b[3] + 1)) + '"' + (SHOT_OF[b[3]] ? "" : ' class="pl" data-i="' + b[3] + '"') + ">" + (b[4] ? "" : "likely ") + "plate " + (b[3] + 1) + "</a>") + "</p>";
    });
    var at = STEP_SCENES.indexOf(st.sc), prevSc = STEP_SCENES[at - 1], nextSc = STEP_SCENES[at + 1], prev = STEPS[pos - 2], next = STEPS[pos];
    if (sh) {
      var dims = sh.k ? D.frame : (p.v || size(sh.i));
      var what = sh.d ? "Close-up " + sh.k + " of " + p.fd + " from plate " + (sh.i + 1) + ", found and squared up by software. The whole sheet comes just before these; the software may have missed frames on it"
        : sh.k ? "Frame " + sh.k + " of " + p.f + ", cut from plate " + (sh.i + 1) + " and squared up by this edition" + (p.fp && p.fp.indexOf(sh.k) >= 0 ? ". The photograph cuts this frame off" : "") + (p.fe && p.fe.indexOf(sh.k) >= 0 ? ". Its ruled lines could not be found, so the cut is an estimate and may be off-centre" : "") : KIND[p.room] + ", plate " + (sh.i + 1);
      stage = '<a class="pl" href="#plate-' + (sh.i + 1) + '" data-i="' + sh.i + '" title="See the whole plate"><img src="' + shotSrc(sh) + '" width="' + dims[0] + '" height="' + dims[1] + '" alt="' + esc(p.t) + '"></a>' +
        '<p class="shot-cap"><b>' + esc(p.t) + "</b>" + esc(what) + " · " + esc(D.credits[p.c] || "") + " · " + state(sh.i) + " · " + placing[p.by || "e"] + "</p>";
    } else {
      var others = ART[st.sc].length;
      stage = '<div class="card' + (st.sc ? "" : " title") + '" tabindex="0"><div class="card-in">' + (st.sc ? '<span class="label">Scene ' + st.sc + (st.of > 1 ? " · " + st.pg + " of " + st.of : "") + "</span>" + (sc.h && st.pg === 1 ? "<h3>" + esc(sc.h) + "</h3>" : "") : "") +
        '<div class="sc-text">' + st.b.map(function (x) { return para(sc.b[x], ""); }).join("") + "</div></div></div>" +
        '<p class="shot-cap">' + (st.sc ? "<b>Scene " + st.sc + ", told by the script</b>The screenplay as typed" + (st.of > 1 ? ", card " + st.pg + " of " + st.of + " for this scene" : "") + ". No storyboard or picture of this scene survives, and none was made for this edition" +
        (others ? '. <a href="#scene-' + st.sc + '">' + others + (others > 1 ? " design plates are" : " design plate is") + " placed with this scene</a>" : "")
        : '<b>The title page</b>The screenplay as typed. Its cast list names a picture for each character; <a href="#scene-0">' + others + " plates are placed with it</a>") + "</p>";
    }
    return '<div class="shot"><div class="shot-stage">' + stage +
      '<div class="shot-map" aria-label="Chapters">' + CH_STEPS.map(function (c, x) {
        if (!c.n) return "";
        var done = x < k ? 100 : x > k ? 0 : (pos - c.at + 1) / c.n * 100;
        return '<a href="#' + c.first + '" style="flex:' + c.n + '" title="' + roman[x] + ". " + esc(D.chapters[x].title) + ", " + c.n + ' steps"' + (x === k ? ' aria-current="true"' : "") + '><i style="width:' + done + '%"></i><span>Chapter ' + roman[x] + ", " + esc(D.chapters[x].title) + "</span></a>";
      }).join("") + "</div>" +
      '<nav class="shot-nav"><a class="btn' + (prev ? "" : " off") + '" href="#' + (prev || st).id + '" aria-label="Previous step">←</a><span>' + stepLabel(st) + '</span><button type="button" class="btn" data-auto aria-pressed="' + auto + '">' + (auto ? "Pause" : "Play") + '</button><a class="btn solid' + (next ? "" : " off") + '" href="#' + (next || st).id + '" aria-label="Next step">→</a></nav>' +
      '<p class="shot-jump">' + (prevSc !== undefined ? '<a href="#' + FIRST[prevSc] + '">← ' + sceneName(prevSc) + "</a>" : "<span></span>") + (nextSc !== undefined ? '<a href="#' + FIRST[nextSc] + '">Scene ' + nextSc + " →</a>" : "<span></span>") + "</p></div>" +
      '<aside class="shot-side" data-sc="' + st.sc + '"><span class="label">Chapter ' + roman[k] + " · " + esc(D.chapters[k].title) + '</span><h2>' + (st.sc ? "<b>" + st.sc + "</b>" : "") + esc(sc.h || "Scene " + st.sc) + '</h2><p class="shot-note">' +
      (sh ? "The script for this scene. The storyboard is a later version of the film, so a shot may not match these lines. " : st.sc ? "The script for this scene. The marked lines are the ones on the card. " : "The typescript’s first page and its list of the cast. ") + '<a href="#scene-' + st.sc + '">Open the scene</a></p><div class="sc-text">' + text + "</div></aside></div>";
  }
  function stepReady(pos) {
    store.set("dune.step", STEPS[pos - 1].id);
    var next = STEPS[pos]; if (next && next.sh) { var im = new Image(); im.src = shotSrc(next.sh); }
  }
  /* the side panel follows the step: to the marked lines if there are any, else it stays where the reader left it */
  function sideFollow(keep) {
    var side = $(".shot-side"), now = side && $(".now", side); if (!side) return;
    if (side.scrollHeight <= side.clientHeight + 1) return;                /* on a phone the panel is part of the page; leave the page alone */
    if (now) side.scrollTop = Math.max(0, now.offsetTop - side.clientHeight * 0.3); else if (keep) side.scrollTop = keep;
  }
  /* Play: step to the next shot by itself. It waits while the plate viewer is open or the tab is hidden. */
  var auto = false, autoTimer = 0, AUTO_MS = 7000, READ_MS = 330;          /* a shot stays seven seconds; a card stays about a third of a second a word */
  function dwell(st) { return st.sh ? AUTO_MS : Math.max(AUTO_MS, st.w * READ_MS); }
  function armAuto() {
    clearTimeout(autoTimer);
    var pos = AT[rendered];
    if (!pos) auto = false;
    if (!auto || !view.hidden || document.hidden) return;
    if (pos >= STEPS.length) { auto = false; var b = $("[data-auto]"); if (b) { b.textContent = "Play"; b.setAttribute("aria-pressed", "false"); } return; }
    autoTimer = setTimeout(function () { location.hash = STEPS[pos].id; }, dwell(STEPS[pos - 1]));
  }
  document.addEventListener("visibilitychange", armAuto);

  /* ---------- watch: film made from the materials ---------- */
  var FILMS = [
    { id: "opening", title: "The opening shot", len: "1 min 52 s", from: "Sequence 1, “un seul plan séquence / one continuous shot”", plate: 125, link: "See the 24 frames one by one",
      text: "The storyboard draws the film’s opening as one unbroken shot across the galaxy, in 24 frames. This is that shot, moving: the camera travels into each drawing and the next one surfaces where the storyboard says it should.",
      how: "In most frames the storyboard rules a small rectangle to show where the camera goes next; the film pushes into that rectangle while the next drawing fades up inside it. Eight frames carry no rectangle, and there the path into the next frame is this edition’s reading. The captions are the storyboard’s own English lines." },
    { id: "museum", title: "The Museum of Man", len: "3 min 11 s", from: "Scenes 1 to 9 of the screenplay", scene: 1, link: "Read from scene 1",
      text: "A ship crosses the galaxy and lands in a dead city. Twelve dog-beings walk into a steel temple, find a crucified man at the end of an empty hall, and discover that he is a projector.",
      how: "The pictures are the illustrated screenplay’s own, each shown at the scene the typescript calls for it, in colour as drawn. The typescript’s pictures for scenes 2 to 5 are not in the archive, so those scenes appear as words on black. The ship is scene 1’s picture, shown under scene 3’s line." },
    { id: "history", title: "The history of man", len: "3 min 6 s", from: "Scenes 10 to 14 of the screenplay", scene: 10, link: "Read from scene 10",
      text: "What the robot projects: the Earth destroyed, the galaxy conquered, the machines doing everything, and the revolt against them.",
      how: "Three of the five scenes have their picture; the typescript’s pictures for scenes 12 and 14 are not in the archive, so the wall at the edge of the galaxy and the revolt against the machines appear as words on black. The picture of the exploding Earth is also shown under the first lines of scene 11." },
    { id: "harkonnen", title: "The Harkonnen castle", len: "1 min 47 s", from: "Scenes 39 and 40 of the screenplay", scene: 39, link: "Read the two scenes",
      text: "The approach to the castle, and Peter and Feyd at chess on its balcony. The words are the screenplay’s; the pictures are the storyboard’s, with one drawing from the illustrated screenplay.",
      how: "Each line sits under the storyboard frame whose own caption describes it; that pairing is this edition’s. The pan up the castle and the push toward its head follow camera notes written on the drawing. Three of the frames survive only as a small scan and look soft." },
    { id: "robot", title: "The robot", len: "2 min 41 s", from: "Scene 43 of the screenplay, first part", scene: 43, link: "Read the scene",
      text: "Paul’s gymnasium on the day the Atreides leave Caladan. His masters sit in ceremony beside a stranger in a large hat; the hat comes off, and under it is a faceless ball of steel.",
      how: "Each line sits under the storyboard frame whose own caption describes it. The first two captions are the storyboard’s own, shown in a dimmer colour: the draft does not have the ship. Idaho’s blow and his speech have no picture, so they appear as words on black." },
    { id: "duel", title: "The duel", len: "2 min 19 s", from: "Scene 43 of the screenplay, the fight", scene: 43, link: "Read the scene",
      text: "Paul against the robot, which records every move he makes and grows stronger with each one.",
      how: "The duel survives on three overlapping sheets and three single frames; where a frame exists more than once, the cleanest copy is used. The storyboard stops before the fight ends, so the last three paragraphs, the table cut in two, the robot destroyed, Leto’s entrance, appear as words on black." }
  ];
  function watchPage() {
    return '<section class="watch gut"><span class="label">Adapted from the surviving materials</span><h1>Watch</h1>' +
      '<p class="lede">Pieces of the film, made from what survives of it: the production’s own drawings set in motion under the screenplay’s own words. No film was shot, and nothing here was drawn or generated to fill a gap.</p>' +
      '<p class="film-index">' + FILMS.map(function (f) { return '<a class="btn" href="#watch" data-scroll="film-' + f.id + '">' + esc(f.title) + "<small>" + f.len + "</small></a>"; }).join("") + "</p>" +
      FILMS.map(function (f) {
        return '<article class="film-item" id="film-' + f.id + '"><h2>' + esc(f.title) + '</h2><p class="film-text">' + f.text + "</p>" +
          '<video controls playsinline preload="metadata" poster="film/' + f.id + '.jpg" src="film/' + f.id + '.mp4"></video>' +
          '<p class="watch-cap">' + f.len + ", with sound · " + f.from + ' · <a href="#' + (f.scene ? "scene-" + f.scene : "shot-" + (SHOT_OF[f.plate] || 1)) + '">' + f.link + "</a></p>" +
          '<p class="film-how"><b>How it was made</b>' + f.how + "</p></article>";
      }).join("") +
      '<div class="notes-grid">' +
      "<div><h3>What is the production’s</h3><p>Every picture, and every word under one. The drawings are the storyboard’s, by Jean Giraud (Moebius) from Jodorowsky’s shot list, and the illustrated screenplay’s. Nothing was redrawn or coloured.</p></div>" +
      "<div><h3>What this edition made</h3><p>The movement of the camera, the cutting from one picture to the next, the timing, the paper tone and grain, the titles, and the choice of which picture goes with which line.</p></div>" +
      "<div><h3>The sound</h3><p>A recording of this site’s generated score, in the mood of the chapter each piece belongs to: a drone, wind and bell notes. It is not music made for the film, and there are no voices.</p></div>" +
      "<div><h3>What it is not</h3><p>Footage. These are animatics: storyboards set in motion the way they describe themselves. Each one says so on its first and last card.</p></div>" +
      "</div></section>";
  }

  /* ---------- whichever column is shorter stays in view ---------- */
  function layout() {
    var avail = window.innerHeight - 80, wide = window.innerWidth > 860;
    var m = $$(".scene").map(function (el) { var t = $(".sc-text", el), a = $(".sc-art", el); return [el, t ? t.offsetHeight : 0, a && !el.classList.contains("bare") ? a.offsetHeight : 0]; });
    m.forEach(function (x) {
      x[0].classList.toggle("stick-art", wide && x[2] > 0 && x[2] <= avail && x[2] < x[1]);
      x[0].classList.toggle("stick-text", wide && x[2] > 0 && x[1] <= avail && x[1] < x[2]);
    });
  }
  function unfold(el) { var r = $(".rest", el), b = $("[data-more]", el); if (r) r.hidden = false; if (b) b.remove(); }
  var watch = null;
  function chapterReady() {
    requestAnimationFrame(layout);
    if (watch) watch.disconnect();
    if (!("IntersectionObserver" in window)) return;
    watch = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) store.set("dune.at", e.target.dataset.n); }); }, { rootMargin: "-30% 0px -60% 0px" });
    $$(".scene").forEach(function (el) { watch.observe(el); });
  }

  /* ---------- search the screenplay ---------- */
  var lastQ = "";
  function mark(text, words) {
    var re = new RegExp("(" + words.map(function (w) { return w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }).join("|") + ")", "gi");
    return text.split(re).map(function (part, k) { return k % 2 ? "<mark>" + esc(part) + "</mark>" : esc(part); }).join("");
  }
  function find() {
    return '<header class="ch-head gut"><span class="label">' + (SC.scenes.length - 1) + ' scenes</span><h1>Find</h1><p class="lede">Search the screenplay. Results quote the script’s own lines.</p>' +
      '<input type="search" id="q" placeholder="worm, Jessica, spice" aria-label="Search the screenplay" autocomplete="off"><p class="map-key" id="q-n" aria-live="polite"></p></header><div class="results gut" id="results"></div>';
  }
  function findReady() {
    var q = $("#q"), out = $("#results"), note = $("#q-n"), timer = 0;
    var run = function () {
      var words = q.value.toLowerCase().split(/\s+/).filter(function (w) { return w.length > 1; }), html = "", count = 0; lastQ = q.value;
      if (!words.length) { out.innerHTML = ""; note.textContent = "Type at least two letters."; return; }
      SC.scenes.forEach(function (sc) {
        if (!sc.n) return;
        var lines = [];
        sc.b.forEach(function (b) { if (b[0] === "a" || b[0] === "t") lines.push(b[1]); else if (b[0] === "d") lines.push(b[1] + " : " + b[2]); });
        var all = (sc.h + " " + lines.join(" ")).toLowerCase();
        if (!words.every(function (w) { return all.indexOf(w) >= 0; }) || ++count > 60) return;
        var hits = lines.filter(function (l) { var low = l.toLowerCase(); return words.some(function (w) { return low.indexOf(w) >= 0; }); }).slice(0, 2).map(function (l) {
          var low = l.toLowerCase(), at = Math.min.apply(null, words.map(function (w) { var x = low.indexOf(w); return x < 0 ? 1e9 : x; })), st = Math.max(0, at - 70);
          return "<em>" + mark((st ? "…" : "") + l.slice(st, st + 230) + (l.length > st + 230 ? "…" : ""), words) + "</em>";
        });
        html += '<a class="hit" href="#scene-' + sc.n + '"><b>' + sc.n + "</b><span><strong>" + esc(sc.h || "Scene " + sc.n) + "</strong>" + hits.join("") + (ART[sc.n].length ? "<small>Has art</small>" : "") + "</span></a>";
      });
      out.innerHTML = html; note.textContent = count ? count + (count === 1 ? " scene" : " scenes") + (count > 60 ? ", first 60 shown" : "") : "Nothing in the script matches.";
    };
    q.value = lastQ; q.addEventListener("input", function () { clearTimeout(timer); timer = setTimeout(run, 160); }); run(); q.focus();
  }

  /* ---------- sound: a generated score, off until asked for ---------- */
  var score = window.DuneScore, snd = $("#snd");
  function moodFor(id) { var m = /^ch-(\d+)$/.exec(id); return m ? +m[1] - 1 : AT[id] ? chapterOf(STEPS[AT[id] - 1].sc) : -1; }
  if (score && score.supported && snd) {
    snd.hidden = false;
    var setSound = function (want) { var is = score.playing(); if (want !== is) is = score.toggle(); snd.setAttribute("aria-pressed", String(is)); snd.textContent = is ? "Sound on" : "Sound"; return is; };
    snd.addEventListener("click", function () { store.set("dune.sound", setSound(!score.playing()) ? "1" : "0"); });
    if (store.get("dune.sound") === "1") {                                  /* browsers only allow sound after a click or key press */
      var wake = function (e) { document.removeEventListener("pointerdown", wake); document.removeEventListener("keydown", wake); if (!e.target.closest || !e.target.closest("#snd")) setSound(true); };
      document.addEventListener("pointerdown", wake); document.addEventListener("keydown", wake);
    }
  }

  /* ---------- router ---------- */
  var main = $("#main"), rendered = "", back = "home";
  /* one film at a time */
  main.addEventListener("play", function (e) { $$(".watch video").forEach(function (v) { if (v !== e.target) v.pause(); }); }, true);
  function render(id) {
    rendered = back = id;
    var m = /^ch-(\d+)$/.exec(id);
    var sm = AT[id], side = $(".shot-side"), keep = sm && side && +side.dataset.sc === STEPS[sm - 1].sc ? side.scrollTop : 0;
    var ae = document.activeElement, refocus = null;
    if (sm && ae && ae.closest && ae.closest(".shot-stage")) refocus = ae.matches("[data-auto]") ? "[data-auto]" : ae.closest(".shot-nav") ? '.shot-nav a[aria-label="' + ae.getAttribute("aria-label") + '"]' :
      ae.closest(".shot-jump") ? ".shot-jump a:" + (ae.previousElementSibling ? "last-child" : "first-child") : ae.closest(".shot-map") ? ".shot-map a[aria-current]" : ae.closest(".card") ? ".card" : ".shot-stage .pl";
    main.innerHTML = m ? chapter(+m[1] - 1) : sm ? stepHtml(sm) : id === "art" ? art() : id === "find" ? find() : id === "watch" ? watchPage() : home();
    if (refocus) { var to = $(refocus + ":not(.off)") || $(".shot-nav a:not(.off)"); if (to) to.focus({ preventScroll: true }); }
    $$(".bar a[data-nav]").forEach(function (a) { a.classList.toggle("on", a.dataset.nav === (m ? "film" : sm ? "shots" : id)); });
    $("#here").textContent = m ? roman[+m[1] - 1] + " · " + D.chapters[+m[1] - 1].title : sm ? stepLabel(STEPS[sm - 1]) : "";
    if (score) score.setMood(moodFor(id));
    if (id === "watch" && score && score.playing() && snd) snd.click();    /* the film has its own sound */
    if (m) chapterReady(); else if (id === "find") findReady(); else if (sm) { stepReady(sm); sideFollow(keep); }
  }
  function route() { clearTimeout(autoTimer); go(); armAuto(); }
  function go() {
    var h = location.hash.replace(/^#/, "") || "home", m;
    if ((m = /^plate-(\d+)$/.exec(h)) && +m[1] >= 1 && +m[1] <= 448) {
      var i = +m[1] - 1;
      if (!rendered) render(SCENE_OF[i] !== undefined ? "ch-" + (chapterOf(SCENE_OF[i]) + 1) : "art");
      if (ctx.indexOf(i) < 0) ctx = [i];
      show(i); return;
    }
    if (!view.hidden) {
      view.hidden = true; document.body.style.overflow = ""; cur = -1;
      if (opener && document.contains(opener)) opener.focus({ preventScroll: true });
      opener = null;
      if (h === rendered || h === back) return;
    }
    if ((m = /^scene-(\d+)$/.exec(h))) {
      var id = "ch-" + (chapterOf(+m[1]) + 1); if (rendered !== id) render(id); back = h;
      var el = $("#sc-" + m[1]); if (el) { unfold(el); layout(); el.scrollIntoView(); } return;
    }
    if (h === "film") h = "ch-1";
    if (h === "shots") h = STEPS[0].id;
    if ((m = /^shot-(\d+)$/.exec(h))) h = "shot-" + Math.min(SHOTS.length, Math.max(1, +m[1]));
    else if ((m = /^script-(\d+)(-\d+)?$/.exec(h))) h = AT[h] ? h : FIRST[+m[1]] || "home";   /* a scene that has shots goes to its first shot */
    else if (!/^ch-(10|[1-9])$/.test(h) && h !== "art" && h !== "find" && h !== "watch") h = "home";
    if (h !== rendered) { render(h); window.scrollTo(0, 0); }
  }
  document.addEventListener("click", function (e) {
    var j = e.target.closest("[data-scroll]");
    if (j) { e.preventDefault(); var t = document.getElementById(j.dataset.scroll); if (t) t.scrollIntoView({ behavior: "smooth" }); return; }
    var play = e.target.closest("[data-auto]");
    if (play) { auto = !auto; play.textContent = auto ? "Pause" : "Play"; play.setAttribute("aria-pressed", String(auto)); armAuto(); return; }
    var more = e.target.closest("[data-more]");
    if (more) { unfold(more.closest(".scene")); layout(); return; }
    if (e.target.closest("[data-fold]")) { store.set("dune.open", store.get("dune.open") === "1" ? "0" : "1"); var keep = rendered; rendered = ""; render(keep); return; }
    var a = e.target.closest("a.pl");
    if (a && a.dataset.i) { var box = a.closest("[data-ctx]"); showOrig = false; if (box) ctx = $$("a.pl[data-i]", box).map(function (x) { return +x.dataset.i; }); }
  });
  document.addEventListener("keydown", function (e) {
    if (view.hidden) {
      var sm = AT[rendered];
      if (sm && e.target.tagName !== "INPUT" && (e.key === "ArrowRight" || e.key === "ArrowLeft")) location.hash = STEPS[Math.min(STEPS.length, Math.max(1, sm + (e.key === "ArrowRight" ? 1 : -1))) - 1].id;
      return;
    }
    if (e.key === "Escape") closeView(); else if (e.key === "ArrowRight") step(1); else if (e.key === "ArrowLeft") step(-1);
  });
  var touch = null;                                                      /* swipe left or right on a shot */
  main.addEventListener("touchstart", function (e) { touch = e.touches.length === 1 && e.target.closest(".shot-stage") ? [e.touches[0].clientX, e.touches[0].clientY] : null; }, { passive: true });
  main.addEventListener("touchend", function (e) {
    if (!touch) return; var dx = e.changedTouches[0].clientX - touch[0], dy = e.changedTouches[0].clientY - touch[1], sm = AT[rendered]; touch = null;
    if (sm && Math.abs(dx) > 50 && Math.abs(dx) > 2 * Math.abs(dy)) location.hash = STEPS[Math.min(STEPS.length, Math.max(1, sm + (dx < 0 ? 1 : -1))) - 1].id;
  }, { passive: true });
  var rz = 0;
  window.addEventListener("resize", function () { clearTimeout(rz); rz = setTimeout(layout, 150); });
  window.addEventListener("hashchange", route);
  route();
})();
