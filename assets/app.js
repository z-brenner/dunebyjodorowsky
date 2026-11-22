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

  /* ---------- pieces ---------- */
  function img(i, eager) {
    var s = size(i);
    return '<img src="' + src(i) + '" width="' + s[0] + '" height="' + s[1] + '" alt="' + esc(P[i].t) + '"' + (eager ? "" : ' loading="lazy"') + ' decoding="async">';
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
    var withArt = SC.scenes.filter(function (sc) { return sc.n && ART[sc.n].length; }).length;
    return '<section class="hero gut"><div class="hero-text">' + CREDITS + '<p class="lede">The film Alejandro Jodorowsky prepared in the mid-1970s and never shot, told here from what survives of it: the early draft of the screenplay, and the drawings and paintings made for it.</p>' +
      '<a class="btn solid" href="#ch-1">Begin</a></div><figure class="hero-art"><a class="pl" href="#plate-172" data-i="171">' + img(171, true) + "</a><figcaption>Plate 172 · Chris Foss · " + state(171) + "</figcaption></figure></section>" +
      '<section class="gut"><ol class="chapters">' + D.chapters.map(function (c, k) {
        return '<li><a href="#ch-' + (k + 1) + '"><span class="ch-pic">' + img(c.key, k < 3) + '</span><span class="ch-no">' + roman[k] + "</span><h2>" + esc(c.title) + "</h2><p>" + esc(c.text) + "</p><small>Scenes " + c.a + (c.b > c.a ? "–" + c.b : "") + "</small></a></li>";
      }).join("") + "</ol></section>" +
      '<section class="notes gut"><h2>What you are looking at</h2><div class="notes-grid">' +
      "<div><h3>The words</h3><p>All " + (SC.scenes.length - 1) + " scenes of the early draft, as typed. Nothing inside a scene has been rewritten or summarised. The chapter titles and their one-line descriptions are this edition’s.</p></div>" +
      "<div><h3>The pictures</h3><p>Every picture comes from one 448-page file of scans gathered online. " + restored + " of them have been restored for this edition: uneven lighting flattened on the pencil sheets, " + straight + " photographed sheets straightened, and small scans enlarged four times by a neural upscaler.</p></div>" +
      "<div><h3>What restoring changes</h3><p>Upscaling invents detail. The fine texture in a restored plate was made by a machine guessing from a small scan, and tiny typed captions do not become readable. Each plate says whether it is restored, and the viewer shows the untouched scan on request.</p></div>" +
      "<div><h3>Where pictures sit</h3><p>Some pictures are placed by the screenplay’s own list of illustrations. The rest, including all the storyboard, are placed by this edition from sequence numbers and captions. Each plate says which. The storyboard is a later version of the film than this draft, so the fit is loose.</p></div>" +
      "<div><h3>The gaps</h3><p>" + withArt + " of the " + (SC.scenes.length - 1) + " scenes have art. Nothing was drawn to fill the others. Where no picture survives, the scene is told by the script alone and says so.</p></div>" +
      "<div><h3>Whose work it is</h3><p>Jean Giraud (Moebius), Chris Foss, H.R. Giger and Alejandro Jodorowsky. It remains theirs and their estates’. This is an unofficial study edition.</p></div>" +
      '</div><p class="more"><a class="btn" href="#art">See all the art</a></p></section>';
  }

  /* ---------- a chapter ---------- */
  function sceneHtml(sc) {
    var text = "", missing = [];
    sc.b.forEach(function (b) {
      if (b[0] === "a") text += "<p>" + esc(b[1]) + "</p>";
      else if (b[0] === "d") text += '<p class="dlg"><b>' + esc(b[1]) + "</b><span>" + esc(b[2]) + "</span></p>";
      else if (b[0] === "t") text += '<p class="ttl">TITLE : ' + esc(b[1]) + "</p>";
      else if (b[0] === "i" && b[3] === null) missing.push(b[1]);
    });
    var ids = ART[sc.n], art = ids.map(plate).join("");
    if (missing.length) art += '<p class="lost"><b>In the typescript, not in the archive</b>' + missing.map(esc).join("<br>") + "</p>";
    return '<article class="scene' + (ids.length ? "" : " bare") + '" id="sc-' + sc.n + '"><header><b>' + sc.n + "</b>" + (sc.h ? "<h3>" + esc(sc.h) + "</h3>" : "") +
      (ids.length ? "" : "<small>No art survives for this scene</small>") + '</header><div class="sc-text">' + text + "</div>" + (art ? '<div class="sc-art" data-ctx>' + art + "</div>" : "") + "</article>";
  }
  function chapter(k) {
    var c = D.chapters[k], scenes = SC.scenes.filter(function (sc) { return sc.n >= c.a && sc.n <= c.b; });
    var map = scenes.map(function (sc) { return '<a href="#scene-' + sc.n + '"' + (ART[sc.n].length ? ' class="has"' : "") + ' title="Scene ' + sc.n + (sc.h ? ": " + esc(sc.h) : "") + '">' + sc.n + "</a>"; }).join("");
    var nav = '<nav class="ch-nav gut"><a class="btn" href="' + (k ? "#ch-" + k : "#home") + '">' + (k ? "← " + esc(D.chapters[k - 1].title) : "← Contents") + "</a>" +
      (k < D.chapters.length - 1 ? '<a class="btn solid" href="#ch-' + (k + 2) + '">' + esc(D.chapters[k + 1].title) + " →</a>" : '<a class="btn solid" href="#art">All the art →</a>') + "</nav>";
    return '<header class="ch-head gut"><span class="label">Chapter ' + roman[k] + " of X · scenes " + c.a + (c.b > c.a ? "–" + c.b : "") + "</span><h1>" + esc(c.title) + '</h1><p class="lede">' + esc(c.text) + "</p>" +
      '<div class="map" aria-label="Scenes in this chapter">' + map + '</div><p class="map-key"><i class="has"></i> has art <i></i> script only</p></header>' +
      '<div class="scenes gut">' + scenes.map(sceneHtml).join("") + "</div>" + nav;
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
  }
  function step(d) { var pos = ctx.indexOf(cur) + d; if (pos >= 0 && pos < ctx.length) location.hash = "plate-" + (ctx[pos] + 1); }
  function closeView() { location.hash = back; }
  side.addEventListener("click", function (e) {
    var b = e.target.closest("[data-v]"); if (!b) return;
    if (b.dataset.v === "flip") { showOrig = !showOrig; show(cur); } else if (b.dataset.v === "close") closeView(); else step(b.dataset.v === "next" ? 1 : -1);
  });

  /* ---------- router ---------- */
  var main = $("#main"), rendered = "", back = "home";
  function render(id) {
    rendered = back = id;
    var m = /^ch-(\d+)$/.exec(id);
    main.innerHTML = m ? chapter(+m[1] - 1) : id === "art" ? art() : home();
    $$(".bar a[data-nav]").forEach(function (a) { a.classList.toggle("on", a.dataset.nav === (m ? "film" : id)); });
    $("#here").textContent = m ? roman[+m[1] - 1] + " · " + D.chapters[+m[1] - 1].title : "";
  }
  function route() {
    var h = location.hash.replace(/^#/, "") || "home", m;
    if ((m = /^plate-(\d+)$/.exec(h)) && +m[1] >= 1 && +m[1] <= 448) {
      var i = +m[1] - 1;
      if (!rendered) render(SCENE_OF[i] !== undefined ? "ch-" + (chapterOf(SCENE_OF[i]) + 1) : "art");
      if (ctx.indexOf(i) < 0) ctx = [i];
      show(i); return;
    }
    if (!view.hidden) { view.hidden = true; document.body.style.overflow = ""; cur = -1; if (h === rendered) return; }
    if ((m = /^scene-(\d+)$/.exec(h))) {
      var id = "ch-" + (chapterOf(+m[1]) + 1), fresh = rendered !== id; if (fresh) render(id); back = h;
      var el = $("#sc-" + m[1]); if (el) el.scrollIntoView(); return;
    }
    if (h === "film") h = "ch-1";
    if (!/^ch-(10|[1-9])$/.test(h) && h !== "art") h = "home";
    if (h !== rendered) { render(h); window.scrollTo(0, 0); }
  }
  document.addEventListener("click", function (e) {
    var j = e.target.closest("[data-scroll]");
    if (j) { e.preventDefault(); var t = document.getElementById(j.dataset.scroll); if (t) t.scrollIntoView({ behavior: "smooth" }); return; }
    var a = e.target.closest("a.pl");
    if (a && a.dataset.i) { var box = a.closest("[data-ctx]"); showOrig = false; if (box) ctx = $$("a.pl[data-i]", box).map(function (x) { return +x.dataset.i; }); }
  });
  document.addEventListener("keydown", function (e) {
    if (view.hidden) return;
    if (e.key === "Escape") closeView(); else if (e.key === "ArrowRight") step(1); else if (e.key === "ArrowLeft") step(-1);
  });
  window.addEventListener("hashchange", route);
  route();
})();
