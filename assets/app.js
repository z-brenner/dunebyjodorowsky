/* Jodorowsky's Dune Bible. One page, nine rooms, a plate viewer and a projector.
   Plates are numbered from 1 to 448 to match the pages of the source PDF. */
(function () {
  "use strict";
  var D = window.DUNE, P = D.plates;
  var $ = function (s, el) { return (el || document).querySelector(s); };
  var $$ = function (s, el) { return Array.prototype.slice.call((el || document).querySelectorAll(s)); };
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
  var pad = function (i) { return ("00" + i).slice(-3); };
  var src = function (i) { return "plates/" + pad(i) + ".jpg"; };
  var reduced = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  var roman = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"];

  var ROOMS = [
    { id: "screening", name: "The Screening", line: "The storyboard, put back in running order", pic: 235, rooms: ["board", "frame", "color"] },
    { id: "players", name: "The Players", line: "Costumes, and who was meant to wear them", pic: 371, rooms: ["design", "lineup"] },
    { id: "machines", name: "The Machines", line: "Ships, cars and palaces by Chris Foss", pic: 171, rooms: ["machine"] },
    { id: "giedi", name: "Giedi Prime", line: "The Harkonnen world of H.R. Giger", pic: 440, rooms: ["giger"] },
    { id: "visions", name: "The Visions", line: "Colour plates from an illustrated screenplay", pic: 49, rooms: ["vision"] },
    { id: "word", name: "The Word", line: "Pages of the script", pic: 312, rooms: ["script"] },
    { id: "alchemist", name: "The Alchemist", line: "Jodorowsky's tarot notebooks", pic: 426, rooms: ["tarot"] },
    { id: "relic", name: "The Relic", line: "The book as an object, and what came after", pic: 96, rooms: ["relic", "apoc"] },
    { id: "atlas", name: "The Atlas", line: "All 448 plates, searchable", pic: 162, rooms: [] }
  ];
  var ROOM_OF = {};
  ROOMS.forEach(function (r) { r.rooms.forEach(function (k) { ROOM_OF[k] = r; }); });
  var KIND = { board: "Storyboard sheet", frame: "Storyboard frame", color: "Colour storyboard", design: "Costume design", lineup: "Cast sheet", machine: "Machine", giger: "Giger", vision: "Colour plate", script: "Script", tarot: "Notebook", relic: "The book", apoc: "From elsewhere" };

  var uniq = function (ids) { return ids.filter(function (i) { return P[i].dup === undefined; }); };
  var inRoom = function (kinds) { return P.filter(function (p) { return kinds.indexOf(p.room) >= 0; }).map(function (p) { return p.i; }); };

  /* ---------- building blocks ---------- */
  function thumb(i) {
    var p = P[i], s = p.s, sh = D.sheets[s[0]];
    var bx = sh[1] === s[3] ? 0 : s[1] / (sh[1] - s[3]) * 100, by = sh[2] === s[4] ? 0 : s[2] / (sh[2] - s[4]) * 100;
    return '<span class="th" role="img" aria-label="' + esc(p.t) + '" style="aspect-ratio:' + s[3] + "/" + s[4] +
      ";background-image:url(thumbs/" + sh[0] + ");background-size:" + (sh[1] / s[3] * 100) + "% " + (sh[2] / s[4] * 100) +
      "%;background-position:" + bx + "% " + by + '%"></span>';
  }
  function plateLink(i, inner, cls) { return '<a class="pl ' + (cls || "") + '" href="#plate-' + (i + 1) + '" data-i="' + i + '">' + inner + "</a>"; }
  function img(i, eager) {
    var p = P[i];
    return '<img src="' + src(i) + '" width="' + p.w + '" height="' + p.h + '" alt="' + esc(p.t) + '"' + (eager ? "" : ' loading="lazy"') + ' decoding="async">';
  }
  function figure(i) {
    return "<figure>" + plateLink(i, img(i)) + "<figcaption><b>" + (i + 1) + "</b><span>" + esc(P[i].t) + "</span></figcaption></figure>";
  }
  function wall(ids) { return '<div class="wall" data-ctx>' + ids.map(figure).join("") + "</div>"; }
  function head(room, ledes) {
    var n = ROOMS.indexOf(room);
    return '<header class="room-head gut"><span class="label">Room ' + roman[n] + " of IX</span><h1>" + esc(room.name) + "</h1>" +
      ledes.map(function (t) { return '<p class="lede">' + t + "</p>"; }).join("") + "</header>";
  }
  function foot(room) {
    var n = ROOMS.indexOf(room), next = ROOMS[(n + 1) % ROOMS.length];
    return '<footer class="room-foot gut"><a class="btn" href="#home">Back to the book</a><a class="btn solid" href="#' + next.id + '">Next room: ' + esc(next.name) + "</a></footer>";
  }

  /* ---------- HOME ---------- */
  var CREDITS = '<div class="title-credits"><span>michel<br>seydoux<br>presents</span><span>alexandro<br>jodorowsky’s<strong>DUNE</strong>from frank herbert’s novel</span><span>design by jean giraud<br>machines by chris foss<br>special effects by dan o’bannon<br>dialogue by m. demuth<br>and a. jodorowsky</span></div>';
  var bookSeen = false;
  function home() {
    var counts = {};
    P.forEach(function (p) { counts[p.room] = (counts[p.room] || 0) + 1; });
    var cards = ROOMS.map(function (r, n) {
      var c = r.id === "atlas" ? 448 : r.rooms.reduce(function (a, k) { return a + (counts[k] || 0); }, 0);
      return '<a class="card" href="#' + r.id + '"><span class="card-num">' + roman[n] + '</span><span class="card-pic">' + img(r.pic, true) +
        "</span><h3>" + esc(r.name) + "</h3><p>" + esc(r.line) + "</p><em>" + c + " plates</em></a>";
    }).join("");
    return '<section class="table gut"><div class="book-wrap"><div class="book' + (bookSeen || reduced ? " open" : "") + '" id="book">' +
      '<div class="leaf title" aria-label="Title page">' + CREDITS + "</div>" +
      '<div class="board" id="board" role="button" tabindex="0" aria-label="Open or close the cover">' +
      '<div class="face cloth"><span class="stamp">DUNE</span><small>Open</small></div>' +
      '<div class="face fly"><span class="label">The film that was never shot</span>' +
      "<p>In the mid-1970s Alejandro Jodorowsky spent more than two years preparing a film of Frank Herbert’s <i>Dune</i>. Moebius drew every shot. Chris Foss painted the ships. H.R. Giger designed a planet. Dan O’Bannon planned the effects.</p>" +
      "<p>The whole film was bound into a book and carried to the Hollywood studios. None of them paid for it.</p>" +
      "<p>This is a scrapbook of that book: 448 pages of storyboards, costumes, paintings, script and photographs. Every page is here, sorted into nine rooms.</p></div>" +
      "</div></div></div>" +
      '<div class="under-book"><p>The storyboard has been put back in film order. You can watch it.</p><span><button type="button" class="btn solid" data-act="project">Run the projector</button></span></div></section>' +
      '<section class="spread gut"><div class="spread-head"><h2>Nine rooms</h2><p>Pick one, or draw a plate at random from the top bar.</p></div><div class="cards">' + cards + "</div>" +
      '<div class="colophon"><div><span class="label">What this is</span><p>An unofficial arrangement of one file: a 448-page PDF of images gathered from many places. Nothing was added to it. Plates keep the page numbers of that file, so plate 124 is page 124.</p></div>' +
      '<div><span class="label">What it is not</span><p>It is not a complete copy of the production book. Many storyboard sequences are missing, some pages appear several times in different scans, and a few items come from other Dune projects. Those are marked.</p></div>' +
      '<div><span class="label">Whose work it is</span><p>Drawings and paintings remain the work of Jean Giraud (Moebius), Chris Foss, H.R. Giger, Alejandro Jodorowsky and their estates. Names given as attributed are this site’s reading and may be wrong.</p></div></div></section>';
  }
  function homeReady() {
    var book = $("#book"), board = $("#board");
    if (!book) return;
    var toggle = function () { book.classList.toggle("open"); bookSeen = true; };
    board.addEventListener("click", toggle);
    board.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); toggle(); } });
    if (!bookSeen && !reduced) setTimeout(function () { if ($("#book") === book) { book.classList.add("open"); bookSeen = true; } }, 900);
  }

  /* ---------- SCREENING ---------- */
  var NO_SWEEP = { 250: 1, 126: 1, 253: 1, 228: 1, 246: 1, 313: 1, 365: 1, 249: 1, 213: 1 };
  function cell(i, placed) {
    var p = P[i], tag = p.seq ? '<span class="tag">Seq ' + p.seq.join("–") + "</span>" : (placed ? '<span class="tag inf">Placed by caption</span>' : "");
    var sub = p.cap ? "“" + esc(p.cap[1].replace(/^[“"]|[”"]$/g, "")) + "”" : esc(p.t);
    return '<div class="cell" id="cell-' + i + '">' + plateLink(i, thumb(i)) + tag + '<span class="sub">' + sub + "</span></div>";
  }
  function screening() {
    var room = ROOMS[0], firstOf = {}, max = D.seqs[D.seqs.length - 1];
    D.reels.forEach(function (r) { r.items.forEach(function (i) { (P[i].seq || []).forEach(function (s) { if (firstOf[s] === undefined) firstOf[s] = i; }); }); });
    var map = "";
    for (var s = 1; s <= max; s++) map += firstOf[s] !== undefined ? '<a href="#cell-' + firstOf[s] + '" data-jump="' + firstOf[s] + '" title="Sequence ' + s + '">' + s + "</a>" : "<span>" + s + "</span>";
    var total = D.reels.reduce(function (a, r) { return a + r.items.length; }, 0);
    var reels = D.reels.map(function (r, n) {
      return '<section class="reel" id="reel-' + r.id + '"><div class="reel-info"><span class="label">Reel ' + (n + 1) + " · " + esc(r.span) + "</span><h2>" + esc(r.title) + "</h2><p>" + esc(r.text) +
        '</p><button type="button" class="btn" data-act="project" data-reel="' + n + '">Project from here</button></div><div class="strip" data-ctx tabindex="0" aria-label="' + esc(r.title) + ' frames">' +
        r.items.map(function (i) { return cell(i, true); }).join("") + "</div></section>";
    }).join("");
    var loose = '<section class="reel" id="reel-loose"><div class="reel-info"><span class="label">Unplaced</span><h2>Loose leaves</h2><p>Frames and colour sheets with no sequence number and no caption that says where they belong.</p></div><div class="strip" data-ctx tabindex="0" aria-label="Unplaced frames">' +
      D.loose.map(function (i) { return cell(i, false); }).join("") + "</div></section>";
    return '<div class="screening">' + head(room, [
      "Moebius drew the film shot by shot, about 3,000 drawings, each with a line of direction typed beneath it in French and English. Every sheet carries a sequence number in its corner.",
      "Those numbers put the surviving sheets back in order here. Loose frames with no number are placed by what their captions describe, and say so."
    ]) + '<div class="gut" style="padding-bottom:26px"><div style="max-width:1400px;margin:0 auto"><button type="button" class="btn solid" data-act="project">Run the projector · ' + total + " plates</button></div></div>" +
      '<div class="gut"><div class="seqmap" aria-label="Sequences present in the archive">' + map + '</div><p class="seq-note">Gold squares are sequences with at least one sheet in the archive: ' + Object.keys(firstOf).length + " of the first " + max + ". The rest are missing from this file.</p></div>" +
      reels + loose + foot(room) + "</div>";
  }

  /* ---------- PLAYERS ---------- */
  var FACE = { paul: 410, leto: 380, jessica: 437, duncan: 370, gurney: 354, hawat: 406, yueh: 447, baron: 374, feyd: 372, rabban: 446, piter: 445, general: 375, emperor: 371, irulan: 29, mother: 373, guild: 412, sardaukar: 277, kynes: 378, court: 443 };
  function players() {
    var room = ROOMS[1];
    var houses = D.players.map(function (hs) {
      return '<section class="house gut"><h2>' + esc(hs.title) + "</h2>" + hs.people.map(function (c) {
        var all = P.filter(function (p) { return p.who && p.who.indexOf(c.id) >= 0 && p.dup === undefined; }).map(function (p) { return p.i; });
        all.sort(function (a, b) { return (P[a].room === "design" ? 0 : 1) - (P[b].room === "design" ? 0 : 1) || a - b; });
        var cast = c.cast ? '<div class="castline"><span class="label">To be played by</span><strong>' + esc(c.cast) + "</strong>" + (c.sure ? "" : "<i>reported</i>") + "</div>" :
          '<div class="castline"><span class="label">Casting</span><span class="typed" style="color:var(--paper-dim)">not recorded in this archive</span></div>';
        return '<article class="player" id="who-' + c.id + '" data-ctx><div class="arcana">' + plateLink(FACE[c.id], img(FACE[c.id]), P[FACE[c.id]].w > P[FACE[c.id]].h ? "wide-src" : "") + "<b>" + esc(c.name) + '</b></div><div class="dossier"><h3>' + esc(c.name) + "</h3>" +
          (c.epithet ? '<p class="epi">' + esc(c.epithet) + "</p>" : "") + cast + (c.note ? '<p class="note">' + esc(c.note) + "</p>" : "") +
          '<span class="label">' + all.length + " plates</span><div class=\"minis\">" + all.map(function (i) { return plateLink(i, thumb(i)); }).join("") + "</div></div></article>";
      }).join("") + "</section>";
    }).join("");
    return '<div class="players">' + head(room, [
      "Jean Giraud, who signed his science fiction as Moebius, designed every costume. Jodorowsky cast people for what they already were: a painter as the Emperor, a rock singer as the Baron’s heir.",
      "Casting marked <i>reported</i> is repeated in accounts of the production but is not confirmed by anything in this archive. Where a costume’s owner is uncertain, the plate says which caption it follows."
    ]) + houses + foot(room) + "</div>";
  }

  /* ---------- MACHINES ---------- */
  function machines() {
    var room = ROOMS[2], painted = [171, 301, 3, 12, 129, 2, 430, 158, 170, 146, 434, 120];
    var used = {}; painted.forEach(function (i) { used[i] = 1; });
    var orni = [145, 196, 144, 364, 391], places = [76, 178, 73, 48, 323, 136, 175];
    orni.concat(places).forEach(function (i) { used[i] = 1; });
    var drawn = uniq(inRoom(["machine"])).filter(function (i) { return !used[i]; });
    var text = {
      171: "The best-known image of the project. It became the poster.", 301: "Skull and crossbones on the flank, spice streaming behind. The bible gives it a design sheet in sequence 1.",
      3: "The seat of the Emperor, in gold.", 12: "The same palace from directly above.", 129: "Captioned in the bible plate: Leto’s car."
    };
    var fleet = painted.map(function (i) {
      var p = P[i];
      return '<article class="ship" data-ctx><div class="ship-pic">' + plateLink(i, img(i)) + '</div><div class="ship-info"><span class="label">Plate ' + (i + 1) + " · " + esc(D.credits[p.c]) + "</span><h2>" + esc(p.t) + "</h2>" + (text[i] ? "<p>" + text[i] + "</p>" : "") + "</div></article>";
    }).join("");
    return '<div class="hangar">' + head(room, [
      "Jodorowsky found Chris Foss on the covers of British science-fiction paperbacks and brought him to Paris. He wanted ships that looked alive, patterned like fish and insects.",
      "Twelve paintings first, then the pencil and ink sheets, then the ornithopters."
    ]) + '<div class="fleet gut">' + fleet + "</div>" +
      '<section class="sect gut"><h2>On paper</h2><p class="sub">Ink and pencil sheets. Several are pages of the bible itself, numbered with the sequence in which the machine first appears.</p>' + wall(drawn) + "</section>" +
      '<section class="sect gut"><h2>Ornithopters</h2><p class="sub">Not all by Foss. Two further ornithopters signed by Ron Cobb belong to a later production and are kept in the Relic room.</p>' + wall(orni) + "</section>" +
      '<section class="sect gut"><h2>Places</h2><p class="sub">Castles, a hall, a city in a tree. Some of these arrived in the file without any credit.</p>' + wall(places) + "</section>" + foot(room) + "</div>";
  }

  /* ---------- simple rooms ---------- */
  function giedi() {
    var room = ROOMS[3], ids = uniq(inRoom(["giger"])).filter(function (i) { return i !== 440; });
    var paint = ids.filter(function (i) { return [159, 160, 346, 173, 330, 357, 438, 317, 50, 204, 57].indexOf(i) >= 0; });
    var sketch = ids.filter(function (i) { return [347, 348, 349, 350, 318, 322].indexOf(i) >= 0; });
    var rest = ids.filter(function (i) { return paint.indexOf(i) < 0 && sketch.indexOf(i) < 0; });
    return '<div class="giedi">' + head(room, [
      "Jodorowsky gave the Harkonnen planet to the Swiss painter H.R. Giger. The castle he painted is a fortress in the shape of a body. In sequence 15 the storyboard goes inside its head.",
      "The paintings, then the working sketches headed “Schloss Harkonnen”, then the furniture that was built years afterwards."
    ]) + '<div class="giedi-hero" data-ctx>' + plateLink(440, img(440, true)) + "</div>" +
      '<section class="sect gut"><h2>The castle</h2><p class="sub">Airbrush paintings and the full-height drawing.</p>' + wall(paint) + "</section>" +
      '<section class="sect gut"><h2>Sketch sheets</h2><p class="sub">Drawbridges, blades and spires, with notes in German.</p>' + wall(sketch) + "</section>" +
      '<section class="sect gut"><h2>The chair, and the painter</h2><p class="sub">The Harkonnen chair exists as a real object. It was made after this production had ended.</p>' + wall(rest) + "</section>" + foot(room) + "</div>";
  }
  function visions() {
    var room = ROOMS[4], ids = uniq(inRoom(["vision"]));
    return '<div class="visions" id="visions">' + head(room, [
      "These coloured-pencil scenes come from an illustrated edition of the screenplay. Photographs of that edition are in the Word room. The source does not credit the artist.",
      "They show the film Jodorowsky wrote more than the one Herbert did: dog-headed guards, a robot orchestra, a white bull, a mountain of idols."
    ]) + '<section class="sect gut">' + wall(ids) + "</section>" + foot(room) + "</div>";
  }
  function word() {
    var room = ROOMS[5], ids = uniq(inRoom(["script"]));
    var sheet = function (i, sc, body) { return '<article class="sheet">' + (sc ? '<p class="sc">' + sc + "</p>" : "") + body + '<a href="#plate-' + (i + 1) + '" data-i="' + i + '" class="pl">Read the page · plate ' + (i + 1) + "</a></article>"; };
    var typed = '<div class="sheets gut" data-ctx>' +
      sheet(192, "1", "<p>A space-ship is crossing the galaxy</p>") +
      sheet(312, "", '<p><span class="who">PAUL :</span> I have something to tell you, but I can’t...</p><p><span class="who">LETO :</span> I know. Dune is a deadly trap.</p><p><span class="who">PAUL :</span> Then why are we going ?</p>') +
      sheet(404, "", "<p>An old woman comes up, and kisses the hem of Paul’s cape.</p><p><span class=\"who\">THE OLD WOMAN :</span> You are the holy child of the legend, son of a Bene Guesserit ! You will take us out of this hell !</p><p>One by one, the beggars kiss Jessica’s and Paul’s clothes. Paul is embarrassed.</p>") +
      sheet(263, "115 (continued)", '<p><span class="who">THE OLD KYNES :</span> The excrement of the large worm, and the sperm of its larvae : excrement and seed in mother-water...</p><p>A blue sphere begins to emerge from the sand, becoming enormous... It lifts the old man, envelopes him and tears him into its centre. The sphere explodes in a noise of thunder. A large part of the desert becomes covered in a blue substance, the spice, vibrating and whistling.</p><p>Pardot Kynes, with his arms in a cross, half buried in spice, is lying dead. A spice flower is growing from his open mouth.</p>') +
      sheet(68, "EXTERIOR. INTERPLANETARY SPACE.<br>VIEW FROM THE PLANET DUNE.", "<p>An enormous fleet of space war-ships is approaching Dune threateningly.</p><p>These ships, bearing the Emperor’s emblem, look sinister. They are completely covered with claws, spikes and teeth.</p>") +
      "</div>";
    return '<div class="word">' + head(room, [
      "The screenplay is by Jodorowsky, adapted from Herbert, with English dialogue credited on the title page to Michel Demuth. Only a handful of its pages are in this archive.",
      "Five passages are typed out below exactly as they appear on the page, spelling included. The photographed pages follow."
    ]) + typed + '<section class="sect gut"><h2>The pages</h2><p class="sub">Typescript pages, and photographs of the illustrated edition.</p>' + wall(ids) + "</section>" + foot(room) + "</div>";
  }
  function alchemist() {
    var room = ROOMS[6], ids = uniq(inRoom(["tarot"]));
    return '<div class="alchemist">' + head(room, [
      "These pages are not from the Dune book. They are Jodorowsky’s own notebooks on the Tarot of Marseille, written in Spanish, and whoever assembled the file put them in with everything else.",
      "They are kept together here. Jodorowsky has taught and written about the tarot for decades, and the notebooks show the habit of mind he brought to the film."
    ]) + '<section class="sect gut">' + wall(ids) + "</section>" + foot(room) + "</div>";
  }
  function relic() {
    var room = ROOMS[7];
    var book = [96, 115, 122, 383, 389, 134, 123, 118, 381, 138], around = [107, 276, 428, 405, 172, 176, 304, 51, 52, 53, 55, 205, 206];
    var apoc = uniq(inRoom(["apoc"]));
    return '<div class="relic">' + head(room, [
      "The production book is a thick landscape volume in cloth, stamped DUNE. Only a small number were made for the studios. A copy signed by Moebius and Jodorowsky is among the photographs here.",
      "This room holds the book as a thing: covers, title page, signatures, posters, the one costume that was built, and loose production drawings photographed on a table."
    ]) + '<section class="sect gut"><h2>The object</h2><p class="sub">Red cloth, blue cloth, a dust jacket with the Foss painting, and the title page.</p>' + wall(book) + "</section>" +
      '<section class="sect gut"><h2>Around it</h2><p class="sub">Posters, a frame from the 2013 documentary, the Sardaukar costume, and working drawings on tracing paper.</p>' + wall(around) + "</section>" +
      '<section class="sect gut"><h2>What came after</h2><div class="after">' +
      "<div><h3>1976</h3><p>The money ran out before shooting. The film rights lapsed and passed to another producer. David Lynch’s <i>Dune</i> was released in 1984.</p></div>" +
      "<div><h3>1979</h3><p>Dan O’Bannon wrote <i>Alien</i>. Giger designed its creature, Moebius its spacesuits, and Foss painted early ships for it.</p></div>" +
      "<div><h3>1980</h3><p>Jodorowsky and Moebius began <i>The Incal</i>, a comic that reuses ideas from the unmade film.</p></div>" +
      "<div><h3>2021</h3><p>A copy of the book sold at Christie’s in Paris for €2.66 million, many times its estimate. The buyers learned afterwards that owning the book gave them no rights in its contents.</p></div>" +
      "</div></section>" +
      '<section class="sect gut"><h2>From elsewhere</h2><p class="sub">Five items in the file are not from this production, or cannot be shown to be. They are kept apart so they do not get mistaken for bible pages.</p>' + wall(apoc) + "</section>" + foot(room) + "</div>";
  }

  /* ---------- ATLAS ---------- */
  function atlas() {
    var room = ROOMS[8], kinds = Object.keys(KIND);
    var chips = '<button type="button" aria-pressed="true" data-kind="">All 448</button>' + kinds.map(function (k) {
      return '<button type="button" aria-pressed="false" data-kind="' + k + '">' + KIND[k] + " " + inRoom([k]).length + "</button>";
    }).join("");
    var grid = P.map(function (p) {
      return '<a class="pl" href="#plate-' + (p.i + 1) + '" data-i="' + p.i + '" style="aspect-ratio:' + p.w + "/" + p.h + '" title="' + esc((p.i + 1) + ". " + p.t) + '">' + thumb(p.i) + "<i>" + (p.i + 1) + "</i></a>";
    }).join("");
    return '<div class="atlas">' + head(room, ["Every page of the file, in its original order. Filter by kind, search titles and notes, or hide the repeat scans."]) +
      '<div class="tools gut"><div class="chips" id="chips">' + chips + '</div><div class="tools-row"><input type="search" id="atlas-q" placeholder="Search: Jessica, worm, sequence 12, Foss…" aria-label="Search the plates">' +
      '<label><input type="checkbox" id="atlas-dup"> Hide repeat scans</label><output id="atlas-n">448 plates</output></div></div>' +
      '<div class="grid gut" id="grid" data-ctx>' + grid + "</div>" + foot(room) + "</div>";
  }
  function atlasReady() {
    var grid = $("#grid"); if (!grid) return;
    var kind = "", q = $("#atlas-q"), dup = $("#atlas-dup"), items = $$(".pl", grid);
    var text = P.map(function (p) { return ((p.i + 1) + " " + p.t + " " + (D.credits[p.c] || "") + " " + (p.n || "") + " " + (p.who || []).join(" ") + " " + (p.seq ? "sequence " + p.seq.join(" sequence ") : "") + " " + (p.cap ? p.cap.join(" ") : "") + " " + KIND[p.room]).toLowerCase(); });
    var apply = function () {
      var words = q.value.toLowerCase().split(/\s+/).filter(Boolean), n = 0;
      items.forEach(function (el, i) {
        var p = P[i], ok = (!kind || p.room === kind) && !(dup.checked && p.dup !== undefined) && words.every(function (w) { return text[i].indexOf(w) >= 0; });
        el.hidden = !ok; if (ok) n++;
      });
      $("#atlas-n").textContent = n + (n === 1 ? " plate" : " plates");
    };
    $("#chips").addEventListener("click", function (e) {
      var b = e.target.closest("button"); if (!b) return;
      kind = b.dataset.kind; $$("button", this).forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); }); apply();
    });
    q.addEventListener("input", apply); dup.addEventListener("change", apply);
  }

  /* ---------- LOUPE ---------- */
  var loupe = $("#loupe"), stage = $("#loupe-stage"), limg = $("#loupe-img"), side = $("#loupe-side");
  var ctx = [], cur = -1, oracle = false, Z = { s: 1, x: 0, y: 0 };
  function setZoom() { limg.style.transform = "translate(" + Z.x + "px," + Z.y + "px) scale(" + Z.s + ")"; stage.classList.toggle("zoomed", Z.s > 1.01); }
  function linkPlates(t) { return esc(t).replace(/plate (\d+)/g, function (m, n) { return '<a href="#plate-' + (+n + 1) + '">plate ' + (+n + 1) + "</a>"; }); }
  function showPlate(i) {
    var p = P[i]; cur = i; Z = { s: 1, x: 0, y: 0 }; setZoom();
    loupe.hidden = false; document.body.style.overflow = "hidden";
    loupe.style.setProperty("--glow", p.col);
    stage.classList.toggle("small", p.w < 700);
    limg.src = src(i); limg.alt = p.t; limg.width = p.w; limg.height = p.h;
    var room = ROOM_OF[p.room], rows = "";
    var row = function (k, v) { rows += "<div><dt>" + k + "</dt><dd>" + v + "</dd></div>"; };
    row("Credit", esc(D.credits[p.c] || ""));
    if (p.seq) row("Sequence", p.seq.join(" and ") + ' · <a href="#screening">see it in order</a>');
    if (p.cap) row("Typed beneath the frame", '<span class="capen">' + esc(p.cap[1]) + '</span><br><span class="capfr">' + esc(p.cap[0]) + "</span>");
    if (p.n) row("Note", linkPlates(p.n));
    if (p.who) row("Shows", p.who.map(function (w) { var n = ""; D.players.forEach(function (h) { h.people.forEach(function (c) { if (c.id === w) n = c.name; }); }); return '<a href="#players" data-who="' + w + '">' + esc(n) + "</a>"; }).join(", "));
    if (p.var) row(p.dup !== undefined ? "Repeat scan. Other copies" : "Other scans of this picture", '<span class="minis">' + p.var.map(function (v) { return plateLink(v, thumb(v)); }).join("") + "</span>");
    row("Kept in", '<a href="#' + room.id + '">' + esc(room.name) + "</a> · " + KIND[p.room]);
    row("Scan", p.w + " × " + p.h + " px" + (p.w < 700 ? ". This is all the resolution the file has." : ""));
    var pos = ctx.indexOf(i);
    side.innerHTML = '<span class="no">Plate ' + (i + 1) + " of 448</span><h2>" + esc(p.t) + "</h2><dl>" + rows + '</dl><div class="loupe-nav">' +
      (oracle ? '<button type="button" class="btn solid" data-l="draw">Draw another</button>' :
        '<button type="button" class="btn" data-l="prev"' + (pos <= 0 ? " disabled" : "") + '>Previous</button><button type="button" class="btn" data-l="next"' + (pos < 0 || pos >= ctx.length - 1 ? " disabled" : "") + ">Next</button>") + "</div>";
    side.scrollTop = 0;
  }
  function closeLoupe() { loupe.hidden = true; loupe.classList.remove("flip"); document.body.style.overflow = ""; cur = -1; oracle = false; }
  function step(d) { var pos = ctx.indexOf(cur) + d; if (pos >= 0 && pos < ctx.length) location.hash = "plate-" + (ctx[pos] + 1); }
  function draw() {
    var pool = uniq(P.map(function (p) { return p.i; })), i = pool[Math.floor(Math.random() * pool.length)];
    oracle = true; loupe.classList.remove("flip"); void loupe.offsetWidth; loupe.classList.add("flip");
    if (location.hash === "#plate-" + (i + 1)) showPlate(i); else location.hash = "plate-" + (i + 1);
  }
  side.addEventListener("click", function (e) {
    var b = e.target.closest("[data-l]");
    if (b) { if (b.dataset.l === "draw") draw(); else step(b.dataset.l === "next" ? 1 : -1); return; }
    var w = e.target.closest("[data-who]"); if (w) pendingWho = w.dataset.who;
  });
  $("#loupe-x").addEventListener("click", function () { location.hash = lastRoom; });
  stage.addEventListener("wheel", function (e) { e.preventDefault(); var s = Math.min(6, Math.max(1, Z.s * (e.deltaY < 0 ? 1.18 : 0.85))); if (s === 1) { Z.x = Z.y = 0; } Z.s = s; setZoom(); }, { passive: false });
  var drag = null, moved = false, pts = {};
  stage.addEventListener("pointerdown", function (e) { pts[e.pointerId] = e; drag = { x: e.clientX - Z.x, y: e.clientY - Z.y, d: 0, s: Z.s }; moved = false; stage.setPointerCapture(e.pointerId); });
  stage.addEventListener("pointermove", function (e) {
    if (!drag) return; pts[e.pointerId] = e; var ids = Object.keys(pts);
    if (ids.length === 2) { var a = pts[ids[0]], b = pts[ids[1]], d = Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY); if (!drag.d) drag.d = d; Z.s = Math.min(6, Math.max(1, drag.s * d / drag.d)); moved = true; setZoom(); return; }
    if (Z.s > 1.01) { Z.x = e.clientX - drag.x; Z.y = e.clientY - drag.y; setZoom(); }
    if (Math.abs(e.clientX - drag.x - Z.x) + Math.abs(e.movementX) + Math.abs(e.movementY) > 3) moved = true;
  });
  var up = function (e) {
    delete pts[e.pointerId]; if (!drag) return; if (Object.keys(pts).length) return; drag = null;
    if (!moved && e.type === "pointerup") { if (Z.s > 1.01) Z = { s: 1, x: 0, y: 0 }; else { var r = stage.getBoundingClientRect(); Z.s = 2.6; Z.x = (r.left + r.width / 2 - e.clientX) * 1.6; Z.y = (r.top + r.height / 2 - e.clientY) * 1.6; } setZoom(); }
  };
  stage.addEventListener("pointerup", up); stage.addEventListener("pointercancel", up);

  /* ---------- PROJECTOR ---------- */
  var pj = $("#pj"), gate = $("#pj-gate"), sub = $("#pj-sub"), slate = $("#pj-slate"), bar = $("#pj-bar");
  var Q = [], qi = 0, timer = 0, playing = true, speed = 1, anim = null, started = 0, left = 0;
  function buildQueue() {
    Q = [];
    D.reels.forEach(function (r, n) { Q.push({ k: "title", r: r, n: n }); r.items.forEach(function (i) { Q.push({ k: "plate", i: i, r: r, n: n }); }); });
    Q.push({ k: "fin" });
    bar.innerHTML = D.reels.map(function (r, n) { return '<span style="flex:' + (r.items.length + 1) + '" data-reel="' + n + '" title="' + esc(r.title) + '"><i></i></span>'; }).join("");
  }
  function durOf(it) {
    if (it.k === "title") return 5200; if (it.k === "fin") return 0;
    var p = P[it.i]; return ((p.room === "board" || p.room === "color") && !NO_SWEEP[it.i] && p.w / p.h > 1.1 ? 17000 : (p.cap ? 7000 : 5500));
  }
  function showQ() {
    clearTimeout(timer); if (anim) { anim.cancel(); anim = null; }
    var it = Q[qi]; pj.classList.toggle("blue", it.k === "fin"); sub.innerHTML = "";
    $$("span", bar).forEach(function (s, n) {
      var first = Q.findIndex(function (x) { return x.n === n; }), len = D.reels[n].items.length + 1;
      $("i", s).style.transform = "scaleX(" + Math.max(0, Math.min(1, (qi - first + 1) / len)) + ")";
    });
    if (it.k === "title") {
      gate.innerHTML = '<div class="pj-card"><span class="label">Reel ' + (it.n + 1) + " of " + D.reels.length + " · " + esc(it.r.span) + "</span><h2>" + esc(it.r.title) + "</h2><p>" + esc(it.r.text) + "</p></div>";
      slate.textContent = "Reel " + (it.n + 1) + " · " + it.r.title;
    } else if (it.k === "fin") {
      gate.innerHTML = '<div class="fin"><span class="arrow"></span><h2>Fin</h2>' + CREDITS + "</div>";
      sub.innerHTML = '<p class="en">The whole screen is blue… titles…</p><p class="fr">Tout l’écran est bleu… titres…</p>';
      $("#pj-play").textContent = "Run it again"; playing = false; return;
    } else {
      var p = P[it.i], sweep = (p.room === "board" || p.room === "color") && !NO_SWEEP[it.i] && p.w / p.h > 1.1;
      gate.innerHTML = '<img src="' + src(it.i) + '" alt="' + esc(p.t) + '"' + (p.w < 1000 ? ' class="lowres"' : "") + ">";
      var el = $("img", gate), d = durOf(it) / speed;
      if (!reduced && el.animate) {
        anim = sweep ? el.animate([
          { transform: "scale(1)", offset: 0 }, { transform: "scale(1)", offset: .1 },
          { transform: "scale(2) translate(25%,25%)", offset: .17 }, { transform: "scale(2) translate(-25%,25%)", offset: .38 },
          { transform: "scale(2) translate(25%,0%)", offset: .45 }, { transform: "scale(2) translate(-25%,0%)", offset: .66 },
          { transform: "scale(2) translate(25%,-25%)", offset: .73 }, { transform: "scale(2) translate(-25%,-25%)", offset: .94 },
          { transform: "scale(1)", offset: 1 }
        ], { duration: d, easing: "ease-in-out", fill: "forwards" }) :
          el.animate([{ transform: "scale(1)" }, { transform: "scale(1.09)" }], { duration: d, easing: "linear", fill: "forwards" });
      }
      if (p.cap) sub.innerHTML = '<p class="en">' + esc(p.cap[1]) + '</p><p class="fr">' + esc(p.cap[0]) + "</p>";
      slate.textContent = "Reel " + (it.n + 1) + " · " + it.r.title + " · " + (p.seq ? "Sequence " + p.seq.join("–") : "placed by caption") + " · Plate " + (it.i + 1) + (p.cap ? "" : " · " + p.t);
      var nx = Q[qi + 1]; if (nx && nx.k === "plate") { new Image().src = src(nx.i); }
    }
    left = durOf(it) / speed; started = performance.now();
    if (playing) timer = setTimeout(nextQ, left); else if (anim) anim.pause();
  }
  function nextQ() { if (qi < Q.length - 1) { qi++; showQ(); } }
  function prevQ() { if (qi > 0) { qi--; if (Q[qi].k !== "fin") { playing = true; $("#pj-play").textContent = "Pause"; } showQ(); } }
  function togglePlay() {
    if (Q[qi].k === "fin") { qi = 0; playing = true; $("#pj-play").textContent = "Pause"; showQ(); return; }
    playing = !playing; $("#pj-play").textContent = playing ? "Pause" : "Play";
    if (playing) { started = performance.now(); timer = setTimeout(nextQ, left); if (anim) anim.play(); }
    else { clearTimeout(timer); left = Math.max(300, left - (performance.now() - started)); if (anim) anim.pause(); }
  }
  function openPj(reel) {
    buildQueue(); qi = reel ? Q.findIndex(function (x) { return x.n === reel; }) : 0; playing = true; $("#pj-play").textContent = "Pause";
    pj.hidden = false; document.body.style.overflow = "hidden"; showQ(); $("#pj-play").focus();
  }
  function closePj() { clearTimeout(timer); if (anim) anim.cancel(); pj.hidden = true; pj.classList.remove("blue"); gate.innerHTML = ""; document.body.style.overflow = ""; }
  $("#pj-next").addEventListener("click", nextQ); $("#pj-prev").addEventListener("click", prevQ);
  $("#pj-play").addEventListener("click", togglePlay); $("#pj-exit").addEventListener("click", closePj);
  $("#pj-speed").addEventListener("click", function () { speed = speed === 1 ? 2 : speed === 2 ? 0.5 : 1; this.textContent = "Speed " + (speed === 0.5 ? "½" : speed) + "×"; showQ(); });
  bar.addEventListener("click", function (e) { var s = e.target.closest("[data-reel]"); if (s) { qi = Q.findIndex(function (x) { return x.n === +s.dataset.reel; }); playing = true; $("#pj-play").textContent = "Pause"; showQ(); } });

  /* ---------- router ---------- */
  var VIEWS = { home: home, screening: screening, players: players, machines: machines, giedi: giedi, visions: visions, word: word, alchemist: alchemist, relic: relic, atlas: atlas };
  var main = $("#room"), lastRoom = "home", rendered = "", pendingWho = "", menu = $("#rooms-menu"), btnRooms = $("#btn-rooms");
  menu.innerHTML = ROOMS.map(function (r, n) { return '<a href="#' + r.id + '"><b>' + roman[n] + "</b><span>" + esc(r.name) + "</span><small>" + esc(r.line) + "</small></a>"; }).join("");
  function closeMenu() { menu.hidden = true; btnRooms.setAttribute("aria-expanded", "false"); }
  btnRooms.addEventListener("click", function () { var open = menu.hidden; menu.hidden = !open; this.setAttribute("aria-expanded", String(open)); });
  $("#btn-draw").addEventListener("click", function () { closeMenu(); draw(); });
  function route() {
    var hsh = location.hash.replace(/^#/, "") || "home", m = /^plate-(\d+)$/.exec(hsh);
    closeMenu();
    if (m && +m[1] >= 1 && +m[1] <= 448) {
      var i = +m[1] - 1;
      if (!rendered) render(ROOM_OF[P[i].room].id, true);
      if (ctx.indexOf(i) < 0) ctx = oracle ? [i] : uniq(inRoom(ROOM_OF[P[i].room].rooms)).concat(P[i].dup !== undefined ? [i] : []);
      showPlate(i); return;
    }
    if (!loupe.hidden) closeLoupe();
    if (!VIEWS[hsh]) { if (/^(cell|reel|who)-/.test(hsh)) return; hsh = "home"; }
    if (hsh !== rendered) render(hsh);
    if (pendingWho) { var el = $("#who-" + pendingWho); pendingWho = ""; if (el) el.scrollIntoView(); }
  }
  function render(id, quiet) {
    rendered = lastRoom = id; main.innerHTML = VIEWS[id]();
    var r = ROOMS.filter(function (x) { return x.id === id; })[0];
    $("#here").textContent = r ? "Room " + roman[ROOMS.indexOf(r)] + " · " + r.name : "448 plates · nine rooms";
    $$("a", menu).forEach(function (a) { if (a.getAttribute("href") === "#" + id) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current"); });
    if (id === "home") homeReady(); if (id === "atlas") atlasReady();
    if (!quiet) window.scrollTo(0, 0);
  }
  document.addEventListener("click", function (e) {
    var act = e.target.closest("[data-act='project']");
    if (act) { openPj(act.dataset.reel ? +act.dataset.reel : 0); return; }
    var j = e.target.closest("[data-jump]");
    if (j) { e.preventDefault(); var c = $("#cell-" + j.dataset.jump); if (c) { c.scrollIntoView({ block: "center", inline: "center", behavior: reduced ? "auto" : "smooth" }); c.classList.remove("flash"); void c.offsetWidth; c.classList.add("flash"); } return; }
    var a = e.target.closest("a.pl");
    if (a && a.dataset.i) {
      var box = a.closest("[data-ctx]"); oracle = false; loupe.classList.remove("flip");
      if (box && !loupe.contains(a)) ctx = $$("a.pl[data-i]", box).filter(function (x) { return !x.hidden; }).map(function (x) { return +x.dataset.i; });
      else if (loupe.contains(a)) ctx = [cur].concat(P[cur].var || []).sort(function (x, y) { return x - y; });
    }
    if (!menu.hidden && !e.target.closest(".bar")) closeMenu();
  });
  var vis = null;
  document.addEventListener("mouseover", function (e) {
    var a = e.target.closest("#visions a.pl"); if (!a) return;
    vis = vis || $("#visions"); if (!document.body.contains(vis)) vis = $("#visions");
    if (vis) vis.style.setProperty("--glow", "color-mix(in srgb, " + P[+a.dataset.i].col + " 45%, #0d0a0f)");
  });
  document.addEventListener("keydown", function (e) {
    if (!pj.hidden) {
      if (e.key === "Escape") closePj(); else if (e.key === "ArrowRight") nextQ(); else if (e.key === "ArrowLeft") prevQ();
      else if (e.key === " " && e.target.tagName !== "BUTTON") { e.preventDefault(); togglePlay(); }
      return;
    }
    if (!loupe.hidden) {
      if (e.key === "Escape") location.hash = lastRoom; else if (e.key === "ArrowRight") step(1); else if (e.key === "ArrowLeft") step(-1);
      return;
    }
    if (e.key === "Escape") closeMenu();
  });
  window.addEventListener("hashchange", route);
  route();
})();
