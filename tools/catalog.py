"""Catalogue of the 448 plates in the source PDF.

Every row is one PDF page (0-based index = plate number).
Columns:  id | room | title | credit | who | note
Rooms:    board (storyboard sheet), frame (single storyboard frame), color
          (colour storyboard), design (costume), lineup (bible cast sheet),
          machine, giger, vision (colour-pencil scene illustration), script,
          tarot, relic, apoc (material from elsewhere that travelled with the file)
Credits:  M Moebius, F Foss, G Giger, J Jodorowsky, SB storyboard, IS illustrated
          screenplay, U uncredited; a trailing ? means attributed, not confirmed.
"""

CREDITS = {
    "M": "Jean Giraud (Moebius)",
    "M?": "Attributed to Moebius",
    "F": "Chris Foss",
    "F?": "Attributed to Chris Foss",
    "G": "H.R. Giger",
    "G?": "Attributed to H.R. Giger",
    "J": "Alejandro Jodorowsky",
    "SB": "Storyboard drawn by Moebius from Jodorowsky's shot list",
    "IS": "Illustrated screenplay edition, artist uncredited in the source",
    "U": "Uncredited in the source",
    "P": "Photograph, uncredited in the source",
}

ROWS = r"""
0|giger|Harkonnen chair, polished metal|G||Giger's Harkonnen furniture was built after the Jodorowsky production had already collapsed.
1|giger|Harkonnen chair, black|G||
2|machine|Caged vessel in amber haze|F||
3|machine|The Emperor's palace|F||
4|frame|"And pulls his hand out… zoom to"|SB||
5|frame|Paul in mid-leap, pencil rough|SB|paul|
6|design|Costume cards: enthroned dignitary in green; figure in pink|M|court|Photographed in an album sleeve.
7|vision|Dog-headed sentries before the striped tent|IS||
8|frame|A face in three-quarter view, pencil rough|SB||
9|design|Figure in a feathered sunburst collar|U|court|
10|vision|The court in red|IS||
11|frame|Two faces, pencil rough|SB||
12|machine|The Emperor's palace, seen from above|F||
13|design|Costume cards: "Duncan Idaho" and "Leto"|M|duncan,leto|Named as in plate 90. Other captions in this archive give Duncan Idaho a different costume.
14|lineup|Les Atreides: Jessica, Paul, Leto|SB|jessica,paul,leto|
15|lineup|Hawatt, Idaho, Halleck, Yueh|SB|hawat,duncan,gurney,yueh|
16|frame|Four dancers fit anti-gravity bracelets to the Baron|SB|baron|
17|vision|A crucified figure before the blue curtain|IS||
18|vision|DUNE, title panel|IS||
19|frame|A body hangs in the air between robed watchers|SB||
20|frame|The robot's vision of Paul|SB|paul|
21|design|Costume cards: winged armour with skull emblem; Guild envoy|M|court,guild|
22|frame|A suited figure stands over a body in the dust|SB||
23|frame|Blue larva|SB||
24|frame|Baron Harkonnen bursts into laughter|SB|baron|
25|frame|The "head" of the castle|SB||
26|lineup|Feyd Rautha, Uman Kudu, Rabban la Bête|SB|feyd,rabban|
27|frame|The Harkonnen castle on its rock|SB||
28|frame|Zoom on the castle|SB||
29|lineup|Princesse Irulan and l'Empereur|SB|irulan,emperor|
30|frame|A scream, pencil rough|SB|leto|
31|design|Costume cards: white armour with green cape; bird-masked figure in red|M|court|
32|design|Costume cards: General Harkonnen; the Baron in beaded armour|M|general,baron|
33|frame|The Baron, hands joined, pencil rough|SB|baron|
34|design|Costume cards: starred and furred figure; Sardaukar|M|court,sardaukar|
35|frame|"…and bodies of smugglers on the spice"|SB||
36|frame|Peter cuts off Leto's right arm|SB|piter,leto|
37|frame|The Baron afloat between hooded figures|SB|baron|
38|design|Costume cards: dignitary in midnight blue; skeletal suit|M|court|
39|vision|Dog-headed pilots in a red craft|IS||
40|frame|The robot gets up|SB||
41|vision|Rat-headed riders enter the blue hall|IS||
42|vision|A giant head throws its gaze across a barge|IS||
43|vision|Spiked spheres fall among red soldiers|IS||
44|vision|A finned ship in blue space|IS||
45|vision|The green tent-palace and its stair|IS||
46|vision|The amphitheatre pit|IS||
47|vision|A sun-machine burning in magenta|IS||
48|machine|Arcade elevation, half rendered|U||Architectural drawing. Its link to the production is not documented in the source.
49|vision|Cathedral-city in blue, with owl façade|IS||
50|giger|Horned figure, airbrush (archive photograph)|G?||
51|relic|Set note on tracing paper: "partie construite… pour cadre 5"|P||One of a run of photographs of loose production drawings on a table.
52|relic|Tracing-paper frame: two figures on a dune|P||
53|relic|Tracing-paper frames spread on a table|P||
54|vision|Giant spheres roll off the cliff|IS||
55|relic|Plan drawing of a red vehicle|P||
56|machine|Leto's car, a transparency held to the light|F||
57|giger|Harkonnen castle, full-height drawing (archive photograph)|G||
58|vision|Battlefield of towers in pink|IS||
59|vision|Paul, with ships at his shoulder (detail)|IS|paul|
60|vision|The worm takes a harvester|IS||
61|vision|Guards and musicians in the red court|IS||
62|vision|Strongmen, acrobats and an elephant|IS||
63|vision|The robot orchestra|IS||
64|machine|Vessel, frontal elevation, pencil|F||
65|vision|The white bull in the stone hall|IS||
66|machine|Warship, ink|F||
67|vision|A woman lies before the dome-vehicle|IS||
68|script|"An enormous fleet of space war-ships is approaching Dune"|J||
69|machine|Domed machine on a pedestal, pencil|F||
70|design|Enthroned figure in blue with sceptre|M?|emperor|Identification as the Emperor is an attribution.
71|board|Sequence 3, frames 21 on|SB||
72|machine|Leto's car, pencil study|F||
73|machine|A city of pods grown on a tree|U||
74|vision|Hall of hanging banners|IS||
75|machine|Three-wheeled vehicle, pencil study|F||
76|machine|Castle on the shore, ink|F?||
77|frame|He passes his weapon from his right hand to his left|SB||
78|design|The Baron, pencil study|M?|baron|
79|frame|Chani: "The prophecy is coming true!"|SB|paul|
80|board|Sequence 14|SB|baron,piter|
81|design|Figure in striped hose and brown cape, waving|M|court|
82|design|Officers of the Emperor's guard|M|sardaukar|Handwritten notes: "officiers de la garde de l'empereur", "visage blanc".
83|frame|"Soudain… un Fremen…", colour sketch signed Moebius|M||
84|board|Sequence 18|SB||
85|frame|Jamis, infinitely more cautious|SB||
86|board|Sequence 19|SB||
87|color|Colour storyboard: the opening, pinned to a wall|U||
88|board|Sequence 9|SB||
89|board|Sequence 14|SB|baron,piter|
90|design|"Duncan Idaho" and "Leto", labelled|M|duncan,leto|
91|board|Sequence 64: the vision|SB||
92|board|Leto: "Never will they seize our corpses."|SB|leto,paul,yueh|
93|relic|Signatures: Moebius 1996, Jodorowsky|P||
94|board|The ornithopter and the worm|SB||
95|board|Sequence 67, photographed in the book|SB||
96|relic|The book: red cloth, gold stamp|P||
97|machine|Warship with ribbed sail, ink|F||
98|machine|Leto's car|F||
99|board|Sequence 55|SB||
100|giger|Harkonnen castle, the dome|G||
101|board|Sequence 24|SB||
102|board|Sequence 71|SB||
103|machine|Vessel, frontal elevation (bible sheet, sequence 45)|F||
104|lineup|The cast sheet: Les Atreides, Les Harkonnens|SB|jessica,paul,leto,hawat,duncan,gurney,yueh,mother,baron,rabban,piter,feyd,irulan,emperor,kynes|
105|board|Paul sets the thumper; the worm comes|SB|paul|
106|board|Sequence 71|SB||
107|relic|Poster: "Michel Seydoux presents a film by Alexandro Jodorowsky"|F||Painting by Chris Foss.
108|board|Sequence 77|SB||
109|design|Enthroned dignitary in green|M|court|
110|board|Sequence 33|SB||
111|board|Sequence 30|SB||
112|board|Hall of the Caladan palace (sequence 7)|SB||
113|board|Jessica and the ceremony of the spice tea|SB|jessica,paul|
114|giger|Harkonnen castle, the head|G||
115|relic|The book, closed|P||
116|board|Sequence 16: the duel|SB||
117|board|Sequence 75|SB||
118|relic|Title page|P||
119|board|Sequence 67|SB||
120|machine|Caged vessel, pale version|F||
121|frame|A bald profile, charcoal rough|SB||
122|relic|The book in a dust jacket|P||
123|relic|Title page, photographed|P||
124|lineup|The cast sheet|SB|jessica,paul,leto,hawat,duncan,gurney,yueh,mother,baron,rabban,piter,feyd,irulan,emperor,kynes|
125|board|Sequence 1: "un seul plan séquence / one continuous shot"|SB||
126|board|Sequence 15: inside the head of the Harkonnen castle|SB|baron|
127|board|Sequence 22|SB||
128|board|Sequence 24|SB||
129|machine|Leto's car (bible plate)|F||
130|frame|"She slaughters him"|SB|jessica|
131|frame|The Sardaukar is dead… the Fremen makes a sign|SB||
132|frame|Jessica at grips with a massive Sardaukar|SB|jessica|
133|board|Jessica comes into the frame; the crysknife|SB|jessica|
134|relic|The book, rendered|P||
135|board|The ring: "I have a message for the Emperor!"|SB||
136|machine|Set sketch with the note "move in & up"|U||English camera note. Origin uncertain.
137|board|Sequence 33|SB||
138|relic|Signatures: Moebius 1996, Jodorowsky|P||
139|board|Sequence 14|SB|baron,piter|
140|board|Sequence 81|SB||
141|board|Leto: "Never will they seize our corpses."|SB|leto,paul,yueh|
142|frame|Stilgar: "You will lead us now!"|SB||
143|lineup|The cast sheet|SB|jessica,paul,leto,hawat,duncan,gurney,yueh,mother,baron,rabban,piter,feyd,irulan,emperor,kynes|
144|machine|A craft over the erg, painting|U||
145|machine|Ornithopter (bible sheet, sequence 24)|F||
146|machine|Golden tower|F||
147|board|Hall of the Caladan palace (sequence 7)|SB||
148|lineup|Les Atreides: Jessica, Paul, Leto|SB|jessica,paul,leto|
149|board|Sequence 36|SB||
150|giger|Causeway to the castle|G||
151|lineup|Hawatt, Idaho, Halleck, Yueh|SB|hawat,duncan,gurney,yueh|
152|tarot|Notebook: "un diamante"|J||
153|frame|Stilgar shocks the worm with an electric prod|SB||
154|frame|"…riding the worm"|SB||
155|board|Sequence 56: riding the worm|SB||
156|vision|A mountain of idols|IS||
157|board|Sequences 58–59. Stilgar: "We welcome you, Muad'Dib."|SB|paul|
158|machine|Dazzle-painted hull|F||
159|giger|Harkonnen castle, the dome|G||
160|giger|Harkonnen castle, the head (detail)|G||
161|tarot|Notebook: "Esta carta entrega su secreto… si se la invierte"|J||
162|design|The whole cast in costume, composite|M|paul,leto,jessica,duncan,hawat,gurney,yueh,mother,baron,rabban,piter,emperor,kynes,sardaukar,guild|
163|board|Sequence 79|SB||
164|design|Guards, soldiers and courtiers, ink sketches|M|sardaukar,court|
165|board|Sequence 81|SB||
166|board|Hawat defeated: "My Lady Jessica, I've been wrong"|SB|hawat,jessica,paul|
167|frame|Jessica: "You created us just to use us"|SB|jessica,mother|
168|frame|Jessica: "Stick it into your heart!"|SB|jessica|
169|giger|Harkonnen chair, profile|G||
170|machine|Red-and-white vessel, frontal|F||
171|machine|The chequered ships|F||
172|relic|Two men flank the built Sardaukar costume|P||
173|giger|The dome on its tracks|G||
174|design|Sardaukar: design sheet and built costume|M|sardaukar|Magazine page.
175|machine|Isometric plan of a settlement|U||Frame grab. Origin uncertain.
176|relic|The Sardaukar costume on a balcony, colour|P||
177|board|Sequence 1, photographed|SB||
178|machine|Castle among clouds, signed Chris Foss|F||
179|script|Illustrated screenplay, open|IS||
180|script|Illustrated screenplay: the harvester page|IS||
181|script|Screenplay title page|J||"Screenplay by Alexandro Jodorowsky. Adapted from DUNE by Frank Herbert."
182|script|Illustrated screenplay: Emperor of the Galaxy; Baron Harkonnen|IS|emperor,baron|
183|script|Illustrated screenplay: Peter; Feyd Rautha|IS|piter,feyd|
184|script|Illustrated screenplay: Paul, young and adult; Bene Gesserit Mother|IS|paul,mother|
185|script|Illustrated screenplay spread|IS||
186|script|Illustrated screenplay spread|IS||
187|script|Illustrated screenplay spread|IS||
188|script|Illustrated screenplay spread|IS||
189|frame|A spiral of ships|SB||
190|frame|"…passes at high speed"|SB||
191|design|Duncan Idaho; Gurney Halleck, captioned|M|duncan,gurney|"Duncan Idaho, maître d'armes, serviteur et ami du Duc Leto." "Gurney Halleck, guerrier et troubadour, ami du Duc Leto."
192|script|Scene 1: "A space-ship is crossing the galaxy"|J||
193|vision|The almond ship among stars|IS||
194|design|Paul levitating in lotus, pencil|U|paul|
195|design|Sardaukar in red|M?|sardaukar|
196|machine|Ornithopter with insect wings, colour study|U||
197|board|Sequence 7, two sheets|SB||
198|machine|The Emperor's palace, seen from above|F||
199|machine|The Emperor's palace|F||
200|machine|The chequered ships|F||
201|machine|Pirate ship|F||
202|machine|Blue ovoid vessel|F||
203|machine|Leto's car|F||
204|giger|Harkonnen castle drawing, unrolled (archive photograph)|G||
205|relic|"Caverne de l'eau", set drawing|P||
206|relic|"DUNE, séquence 71/73, caverne de l'eau"|P||
207|board|Soft pencil frames: two figures, joined hands|SB||
208|board|Sequence 11|SB||
209|board|Sequence 12|SB||
210|board|Sequence 12|SB||
211|board|Sequence 12|SB||
212|board|Sequence 12|SB||
213|board|Sequence 13|SB||
214|board|Sequence 15: coloured lights play on the wall|SB|baron|
215|board|Sequence 15, redrawn|SB|baron|
216|board|The Baron: "…and his son, and his concubine too"|SB|baron,yueh|
217|board|The Guild ship; Paul enters the gymnasium|SB|paul,hawat|
218|board|Hawat, the robot, the duel|SB|paul,hawat|
219|board|Paul against the robot|SB|paul|
220|apoc|Idaho's convoy reaches the burning village, set beside stills from a 1977 film|U|duncan|A fan comparison sheet. The storyboard frames are from the bible; the stills are not.
221|board|Sequence 1|SB||
222|board|Sequence 1, second sheet|SB||
223|color|Ornithopter and worm, colourised|U||
224|color|Ornithopter and worm, colourised|U||
225|board|Sardaukar and children; the child's sword|SB|sardaukar|
226|color|The Sardaukar swords lunge into the crowd of children|U|sardaukar|
227|board|Arrival on the esplanade of the Senate|SB||
228|board|Sequence 3: le Sénat|SB||
229|board|The Baron: "Where is Paul?"|SB|baron,piter,leto|
230|board|Peter cuts off Leto's limbs|SB|piter,leto,baron|
231|board|The Baron: "Total extermination!"|SB|baron|
232|color|Mixed frames, colour and pencil|U||
233|color|Paul and Jessica leave the shadow of the rocks|U|paul,jessica|
234|color|Jessica assembles the pieces of Leto's body|U|jessica,leto|
235|color|The eye: a vision in twelve frames|U||
236|board|Sequence 3|SB||
237|board|Sequence 4|SB||
238|board|Sequence 4|SB||
239|board|Sequence 5|SB||
240|board|Sequence 5|SB||
241|board|The old woman: "The poison is in your blood. Change it… or die."|SB|jessica,mother|
242|board|Sequence 63|SB||
243|board|Sequence 64: the vision|SB||
244|board|The old woman: "She has transmuted the water of death!"|SB|jessica,mother|
245|board|The duel with Feyd|SB|feyd,paul|
246|machine|Warship with ribbed sail (bible sheet, sequence 6)|F||
247|board|Sequence 6|SB||
248|board|Sequence 6|SB||
249|board|Chani, Stilgar; Paul roars|SB|paul|
250|board|Hall of the Caladan palace (sequence 7)|SB||
251|board|Sequence 7|SB||
252|board|Sequence 7|SB||
253|board|Sequence 8: the Bene Gesserit asteroid, "a beautiful rock covered with gems"|SB|mother|
254|board|Sequence 8|SB||
255|board|Sequence 8|SB||
256|frame|"…and snatches the spectacles"|SB||
257|frame|The eyes of the members of the Guild are blue because of the spice|SB|guild|
258|color|Paul falls heavily… dead|U|paul|
259|color|"I am Paul": Dune covers itself with vegetation|U|paul|
260|color|The luminous planet leaves the galaxy; FIN|U||
261|board|Sequence 9|SB||
262|board|Sequence 9|SB||
263|script|Scene 115: the death of old Kynes|J|kynes|
264|script|Scene 116: the water of life|J|jessica,mother|
265|script|Scene 117: Jessica's visions|J|jessica|
266|frame|Ships descend on Dune|SB||
267|design|Dame Jessica, two plates, captioned|M|jessica|"Dame Jessica, mère de Paul, concubine du Duc Leto, fille naturelle du Baron Harkonnen, appartient à la secte supérieure des Bene-Gesserit."
268|design|Jessica, three costume drawings, ink|M|jessica|
269|script|Scene 67: the smugglers' room|J||
270|script|Scene 115: the death of old Kynes|J|kynes|
271|script|Scene 116: the water of life|J|jessica,mother|
272|script|Scene 125: rocks near the large flat land|J|paul|
273|script|Scene 132: cave for the great ceremony|J|paul,jessica|
274|script|Scene 134: the centre of the cisterns|J|paul,jessica|
275|design|Figure in a feathered sunburst collar|U|court|
276|relic|French poster: Alexandro Jodorowsky, DUNE, Michel Seydoux|P||
277|design|Sardaukar in dark armour|M|sardaukar|
278|design|Figure with a cable cape and orange hose|M|court|
279|lineup|Les Atreides, full line|SB|jessica,paul,leto,hawat,duncan,gurney|
280|design|"Leto"|M|leto|Named as in plate 90.
281|lineup|Les Harkonnens|SB|baron,feyd,piter|
282|design|Figure with rainbow-scaled pauldrons|M|court|
283|frame|Vertical pan up to the "head", with yellow wash|SB||
284|frame|Paul attacks a second time… but the robot stops the blow|SB|paul|
285|frame|"…and snatches the spectacles"|SB||
286|board|Sequence 3, photographed|SB||
287|lineup|The cast sheet, photographed|SB|jessica,paul,leto,hawat,duncan,gurney,yueh,mother,baron,rabban,piter,feyd,irulan,emperor,kynes|
288|design|Duke Leto, two plates|M|leto|
289|design|Costume construction notes: tricot, coton, velours côtelé, peau|M|leto|
290|machine|Leto's car|F||
291|design|Helmeted soldier, pencil and colour, signed Moebius|M|court|
292|apoc|A fencer and a training machine|U||Frame grab. Origin uncertain; it may come from a later Dune production.
293|apoc|Storyboard from another Dune production|U||Handwritten English notes ("Paul looks over to Jessica, worm rears to attack"). Not a bible page.
294|design|Four costumes: Sardaukar, masked dignitary, green armour, winged armour|M|sardaukar,court|
295|script|Screenplay cover|P||
296|tarot|Notebook: "orden definitivo"|J||
297|tarot|Notebook: coins and the chequered lozenges|J||
298|tarot|Notebook: branching diagrams and the elements|J||
299|tarot|Notebook: "el mat", cards laid on two hands|J||
300|tarot|Notebook: "tú, aquí, ahora"|J||
301|machine|Pirate ship|F||
302|design|Rabban la Bête, two plates, captioned|M|rabban|"Rabban la Bête, dictateur, idiot, criminel, hermaphrodite."
303|design|Costume chart with later captions|M|paul,leto,duncan,hawat,mother,emperor,guild,jessica,yueh,kynes,gurney,baron,feyd,rabban,piter,sardaukar|A fan-made index. Several identifications in this archive follow it.
304|relic|The Sardaukar costume, arm raised|P||
305|frame|Paul, standing up, in trance|SB|paul|
306|frame|"Rises up to the roof of the cavern"|SB||
307|frame|"And comes down in wreaths toward the Fremen"|SB||
308|frame|The smoke spreads among the Fremen|SB||
309|frame|General breakdown|SB||
310|frame|Fremens' amazement|SB||
311|frame|Paul levitates|SB|paul|
312|script|"Dune is a deadly trap."|J|paul,leto|
313|machine|Sardaukar ship (bible sheet, sequence 1)|F||
314|machine|"Dune – The Spice Harvester", pencil|F||
315|design|Thufir Hawat, plates with bible inset|M|hawat|
316|design|Docteur Wellington Yueh, captioned|M|yueh|"Docteur Wellington Yueh, victime des circonstances, traître par amour."
317|giger|Harkonnen castle, full-height drawing|G||
318|giger|Spires and dome: plan and elevation|G?||
319|giger|Harkonnen chair, front|G||
320|design|Woman in blue with staff and green cable cape|M|court|
321|board|Sequence 3|SB||
322|giger|Spires around a dome, ink|G?||
323|machine|Hall study in graphite and red|U||
324|tarot|Publication page with an essay by Chus Martínez|P||
325|tarot|Notebook: the red sun|J||
326|tarot|Notebook: "tiempo, espacio" and the castle card|J||
327|design|"Duncan Idaho"|M|duncan|Named as in plate 90.
328|design|Duncan Idaho with a companion|M|duncan|Named as in the captioned plate 191.
329|giger|The worm|G||
330|giger|The worm|G||
331|vision|DUNE, title panel|IS||
332|design|Emperor of the Galaxy|IS|emperor|
333|design|Baron Harkonnen|IS|baron|
334|design|Paul, young and adult|IS|paul|
335|design|Bene Gesserit Mother|IS|mother|
336|design|Sardaukar|IS|sardaukar|
337|vision|The amphitheatre pit|IS||
338|vision|The green tent-palace and its stair|IS||
339|vision|Hall of hanging banners|IS||
340|vision|A sun-machine burning in magenta|IS||
341|vision|Cathedral-city in blue, with owl façade|IS||
342|vision|Battlefield of towers in pink|IS||
343|vision|Giant spheres roll off the cliff|IS||
344|vision|The worm takes a harvester|IS||
345|vision|A woman lies before the dome-vehicle|IS||
346|giger|Causeway to the castle|G||
347|giger|Sketch sheet, "Schloss Harkonnen": the star wheel|G||
348|giger|Sketch sheet, "Schloss Harkonnen": the folding blade|G||
349|giger|Sketch sheet: dome, drawbridge and notes|G||
350|giger|Sketch sheet: wings and spires|G||
351|vision|The fish-boat|IS||
352|apoc|Ornithopter, pencil, signed R. Cobb|U||Signed by Ron Cobb. Likely from a later Dune production.
353|design|The Emperor|M|emperor|Identification follows the chart in plate 303.
354|design|Gurney Halleck|M|gurney|Identification follows the chart in plate 303.
355|frame|"(He burns a butterfly and smokes a long joint)"|SB|feyd|
356|frame|"The whole screen is blue… titles…"|SB||
357|giger|Biomechanical head|G||
358|giger|Sketch sheet, "Schloss Harkonnen": the star wheel|G||
359|giger|Sketch sheet: dome, drawbridge and notes|G||
360|giger|Sketch sheet, "Schloss Harkonnen": the folding blade|G||
361|giger|Sketch sheet: wings and spires|G||
362|machine|Two hull studies, pencil|F||
363|giger|Harkonnen chair, three views|G||
364|machine|Ornithopter on stilt legs, sketch|U||
365|machine|Pirate ship (bible sheet, sequence 1)|F||
366|tarot|Notebook: "la corona de 5"|J||
367|tarot|Notebook: the castle card|J||
368|tarot|Notebook: "un diamante"|J||
369|design|The Baron in beaded armour|M|baron|
370|design|Duncan Idaho with a companion|M|duncan|
371|design|The Emperor|M|emperor|
372|design|Feyd-Rautha enthroned|M|feyd|Identification follows the chart in plate 303.
373|design|The Reverend Mother|M|mother|
374|design|The Baron reclining|M|baron|
375|design|General Harkonnen|M|general|Named as in plate 386.
376|design|Dignitary in midnight blue with staff|M|court|
377|design|Winged armour with skull emblem|M|court|
378|design|Kynes|M|kynes|Identification follows the chart in plate 303.
379|frame|A ship nears a skull-marked moon, pencil rough|SB||
380|design|Duke Leto|M|leto|
381|relic|Title page (auction photograph)|P||
382|board|Sequence 69, photographed in the book|SB|feyd,paul|
383|relic|The book, a copy in blue cloth (auction photograph)|P||
384|giger|Biomechanical head (detail)|G||
385|design|Robed figure with trident staff, pencil|U|mother|
386|design|"General Harkonnen", labelled card|M|general|
387|design|"Gurney Halleck", labelled card|M|gurney|
388|design|Bird-crested figure in white feathers, on a dais|M?|court|
389|relic|The book lying open|P||
390|design|The Reverend Mother|M|mother|
391|machine|Ornithopter, sketch in violet|U||
392|color|Colour storyboard: the opening|U||
393|color|Colour storyboard: the pirates|U||
394|color|Colour storyboard: red and blue|U||
395|color|Colour storyboard: the golden planet|U||
396|color|Colour storyboard: the black sun|U||
397|color|Colour storyboard, last sheet|U||
398|design|Paul|M|paul|
399|design|Armoured officer with fur mantle|M|sardaukar|
400|board|Duel frames, strip|SB|paul|
401|color|Colour storyboard: the opening|U||
402|color|Colour storyboard: the pirates|U||
403|script|Scene 51: a town in the desert|J|duncan|
404|script|"You are the holy child of the legend"|J|paul,jessica,leto|
405|relic|Documentary still: "I have Moebius who was a genius. He was very quick!"|P||
406|design|Thufir Hawat|M|hawat|
407|design|Two Sardaukar in red|M?|sardaukar|
408|design|The Emperor (detail)|M|emperor|
409|giger|Sketch sheet: dome, drawbridge and notes (photograph)|G||
410|design|Paul|M|paul|
411|design|Sardaukar|M|sardaukar|
412|design|Guild envoy|M|guild|Identification follows the chart in plate 303.
413|design|Bird-masked figure in red and blue|M|court|
414|design|Starred and furred figure|M|court|
415|design|Enthroned dignitary in green|M|court|
416|design|Figure in pink with striped sleeves|M|court|
417|design|Sardaukar in dark armour|M|sardaukar|
418|design|"Leto"|M|leto|Named as in plate 90.
419|tarot|Notebook: "el colgado"|J||
420|tarot|Notebook: "tiempo, espacio" and the castle card|J||
421|tarot|Notebook: green annotations|J||
422|tarot|Notebook: branching diagrams and the elements|J||
423|tarot|Notebook: coins and the chequered lozenges|J||
424|tarot|Notebook: cards laid on two hands|J||
425|tarot|Notebook: "la hembra", threads across two hands|J||
426|tarot|Notebook: the red sun|J||
427|tarot|Notebook: "tú, aquí, ahora"|J||
428|relic|Title card of the 2013 documentary|P||
429|machine|Pirate ship (bible sheet, sequence 1)|F||
430|machine|Blue ovoid vessel|F||
431|giger|Giger in his studio|P||
432|design|Skeletal suit|M|court|
433|design|Winged armour with skull emblem|M|court|
434|machine|Golden octagon with an enthroned figure|F?||
435|board|Sequence 85|SB||
436|apoc|Ornithopter, signed R. Cobb|U||Signed by Ron Cobb. Likely from a later Dune production.
437|design|Jessica|M|jessica|
438|giger|Biomechanical landscape|G||
439|design|Figure with rainbow-scaled pauldrons (detail)|M|court|
440|giger|Harkonnen castle, the head|G||
441|design|Figure with a cable cape and orange hose|M|court|
442|board|Peter loads a luminous ampoule; the mentat's brain lights up|SB|piter|
443|design|Enthroned dignitary in green, on yellow|M|court|
444|design|Figure in pink with striped sleeves|M|court|
445|design|Piter De Vries|M|piter|Identification follows the chart in plate 303.
446|design|Rabban la Bête|M|rabban|
447|design|Docteur Wellington Yueh|M|yueh|
"""

# Sequence numbers printed top-right on bible sheets ("12 DUNE").
SEQ = {
    1: [125, 177, 221, 222, 313, 365, 429],
    3: [71, 228, 236, 286, 321],
    4: [237, 238], 5: [239, 240],
    6: [246, 247, 248],
    7: [112, 147, 197, 250, 251, 252],
    8: [253, 254, 255], 9: [88, 261, 262],
    11: [208], 12: [209, 210, 211, 212], 13: [213],
    14: [80, 89, 139], 15: [126, 214, 215],
    16: [116], 18: [84], 19: [86], 22: [127],
    24: [101, 128, 145], 30: [111], 33: [110, 137], 36: [149],
    45: [103], 55: [99], 56: [155], 58: [157], 59: [157],
    63: [242], 64: [91, 243], 67: [95, 119], 69: [382],
    71: [102, 106], 75: [117], 77: [108], 79: [163],
    81: [140, 165], 85: [435], 90: [168, 257],
}

# Bilingual captions typed under the frames, as printed (French / English).
CAP = {
    4: ("Et retire la main – zoom sur…", "And pulls his hand out… zoom to"),
    16: ("4 des danseuses posent des bracelets anti-gravition au Baron", "Four of the dancers place anti-gravity bracelets against the Baron"),
    20: ("Plan subjectif du robot regardant Paul… des symboles mystérieux défilent", "The robot's vision of Paul. Mysterious symbols go past"),
    23: ("Larves bleues", "Blue larva"),
    24: ("Le Baron Harkonnen éclate de rire", "Baron Harkonnen bursts into laughter"),
    25: ("La « tête » du château", "“Head” of the castle"),
    35: ("…des cadavres de contrebandiers gisent dans l'épice.", "…and bodies of smugglers on the spice."),
    36: ("Peter coupe le bras droit de Leto", "Peter cuts off Leto's right arm"),
    40: ("Le robot se relève", "The robot gets up"),
    77: ("Il fait passer son arme de la main droite à la main gauche", "He passes his weapon from his right hand to his left"),
    79: ("Chani : « La prophétie s'accomplit ! Il est le roi des faiseurs d'épice ! Shulud le blanc ! Le vieil homme éternité ! »", "Chani: “The prophecy is coming true! He is the king of spice-makers! Shulud the white! Old man eternity!”"),
    85: ("Jamis, beaucoup plus prudent", "Jamis, infinitely more cautious"),
    92: ("Leto : « Jamais ils ne s'empareront de nos corps. »", "Leto: “Never will they seize our corpses.”"),
    113: ("Jessica : « Tu dois défier Stilgar. Le moment est venu. »", "Jessica: “You have to challenge Stilgar. The moment has come.”"),
    130: ("…l'extermine", "She slaughters him"),
    131: ("Le Sardaukar est mort… le Fremen fait un signe", "The Sardaukar is dead… the Fremen makes a sign"),
    132: ("Jessica aux prises avec un Sardaukar géant", "Jessica at grips with a massive Sardaukar"),
    135: ("Alia : « J'ai un message pour l'Empereur ! »", "Alia: “I have a message for the Emperor!”"),
    142: ("Stilgar : « Tu nous conduiras désormais. »", "Stilgar: “You will lead us now!”"),
    153: ("Stilgar excite le ver avec un aiguillon électrique", "Stilgar shocks the worm with electric prod"),
    154: ("…chevauchant le ver", "…riding the worm"),
    157: ("Stilgar : « Nous te souhaitons la bienvenue, Muad'Dib. »", "Stilgar: “We welcome you, Muad'Dib.”"),
    166: ("Hawatt : « Ma Dame Jessica, je me suis trompé. »", "Hawatt: “My Lady Jessica, I've been wrong.”"),
    167: ("Jessica : « Tu ne nous as créés que pour nous utiliser. Mais nous ne nous inclinerons plus devant toi ! »", "Jessica: “You created us just to use us. But we shall bend before you no more!”"),
    168: ("Jessica : « Plante-le dans ton cœur ! »", "Jessica: “Stick it into your heart!”"),
    189: ("Une spirale de navires", "A spiral of ships"),
    190: ("Passe à grande vitesse", "Passes at high speed"),
    229: ("Baron : « Où est Paul ? »", "Baron: “Where is Paul?”"),
    231: ("Le Baron : « Extermination totale ! »", "The Baron: “Total extermination!”"),
    233: ("Paul et Jessica sortent de l'ombre des rochers", "Paul and Jessica move out of the shadow of the rocks"),
    234: ("Jessica : « Laisse-moi transformer la mort en vie ! »", "Jessica: “Let me change death into life!”"),
    241: ("Voix off de la vieille : « Le poison est dans ton sang. Change-le… ou meurs… »", "Voice-off of the old woman: “The poison is in your blood. Change it… or die…”"),
    244: ("La vieille : « La mort n'a plus pouvoir sur elle ! »", "The old woman: “Death has no longer power over her!”"),
    256: ("…et arrache les lunettes", "…and snatches the spectacles"),
    257: ("Les membres de la Guilde ont les yeux bleuis par l'épice", "The eyes of the members of the Guild are blue because of the spice"),
    258: ("Paul tombe lourdement… mort", "Paul falls heavily… dead"),
    259: ("« Je suis Paul ! »", "“I am Paul!”"),
    260: ("La planète lumineuse traverse la galaxie", "The luminous planet traverses the galaxy"),
    284: ("Deuxième attaque de Paul… mais le robot pare le coup…", "Paul attacks a second time… but the robot stops the blow…"),
    305: ("Paul, debout, en transe", "Paul, standing up, in trance"),
    306: ("Monte vers le plafond de la caverne", "Rises up to the roof of the cavern"),
    307: ("Et puis redescend en volutes vers les Fremens.", "And comes down in wreaths the Fremens"),
    308: ("La fumée se répand parmi les Fremens", "The smoke spreads among"),
    309: ("Défonce générale", "General breakdown"),
    310: ("Stupéfaction des Fremens", "Fremens' amazement"),
    311: ("Paul lévite", "Paul levitates"),
    355: ("(Il brûle un papillon et fume un long joint.)", "(He burns a butterfly and smokes a long joint)"),
    356: ("Tout l'écran est bleu… titres…", "The whole screen is blue… titles…"),
}

# The film in running order. Sheets with a printed sequence number are placed
# by it; loose frames are placed by what their captions describe.
REELS = [
    ("one-shot", "One continuous shot", "Sequence 1",
     "The film opens on a single unbroken move through the galaxy. Ships spiral, pirates strike a convoy, and smugglers lie dead on the spilled spice.",
     [125, 222, 189, 190, 392, 393, 313, 365, 379, 35, 22]),
    ("gold", "The golden planet", "Sequences 3–5",
     "The Emperor's world: the Senate, its esplanade, a festival of children, and the Sardaukar who end it.",
     [228, 227, 236, 71, 321, 225, 226, 237, 238, 239, 240, 395]),
    ("caladan", "Caladan", "Sequences 6–13",
     "The Atreides at home. The hall of the palace, the asteroid of the Bene Gesserit, and the order to leave.",
     [246, 247, 248, 250, 197, 251, 252, 253, 254, 255, 88, 261, 262, 208, 209, 210, 211, 212, 213]),
    ("giedi", "Inside the head", "Sequences 14–15",
     "The Harkonnen castle is built in the Baron's likeness, and the court meets inside its skull.",
     [27, 28, 283, 25, 139, 89, 442, 126, 214, 215, 16, 37, 33, 24, 355]),
    ("training", "The robot", "Sequences 16–19",
     "Paul is trained against a fighting machine while a Guild ship waits overhead.",
     [217, 218, 20, 40, 219, 284, 400, 116, 77, 84, 86]),
    ("arrakis", "The deadly trap", "Sequences 22–36",
     "Arrival on Dune. Ornithopters over the worm, Yueh's dome, then the Baron's order and what Peter does to the Duke.",
     [266, 127, 128, 101, 94, 223, 224, 92, 111, 110, 216, 229, 230, 36, 30, 231, 149]),
    ("desert", "Into the desert", "Sequences 55–59",
     "Jessica gathers the Duke's body and conceives from it. Mother and son reach the Fremen. A duel, a welcome, a first ride.",
     [233, 234, 99, 85, 142, 157, 105, 153, 154, 155, 79, 249]),
    ("water", "The water of life", "Sequences 63–67",
     "The ceremony in the cavern. Jessica transmutes the poison. Smoke fills the cave, the Fremen break down, and Paul rises off the ground.",
     [242, 241, 244, 91, 235, 23, 113, 305, 306, 307, 308, 309, 310, 311, 119, 95]),
    ("war", "The war", "Sequences 69–85",
     "Feyd, the knives, the Sardaukar. The storyboard here survives only in scattered sheets.",
     [382, 245, 133, 166, 102, 106, 117, 108, 163, 165, 435, 130, 131, 132, 135, 207]),
    ("fin", "I am Paul", "Sequence 90 to the end",
     "Jessica defies the Reverend Mother. Paul is killed and speaks from every mouth. Dune turns green, leaves the galaxy, and the screen goes blue.",
     [167, 168, 285, 257, 258, 259, 260, 356]),
]
LOOSE = [4, 5, 8, 11, 19, 121, 83, 394, 396, 397, 232]

# The players. `cast` lists who Jodorowsky wanted; `sure` marks whether the
# casting is firmly documented or only reported.
PLAYERS = [
    ("atreides", "House Atreides", [
        ("paul", "Paul Atreides", "The child of a drop of blood", "Brontis Jodorowsky", True, "The director's son, then a boy, trained in combat for two years for the part."),
        ("leto", "Duke Leto", "", "David Carradine", True, ""),
        ("jessica", "Dame Jessica", "Mère de Paul, concubine du Duc Leto", "", False, "Charlotte Rampling was asked and declined."),
        ("duncan", "Duncan Idaho", "Maître d'armes, serviteur et ami du Duc", "Alain Delon", False, "The archive disagrees with itself about which costume is his."),
        ("gurney", "Gurney Halleck", "Guerrier et troubadour", "Hervé Villechaize", False, ""),
        ("hawat", "Thufir Hawat", "", "", False, ""),
        ("yueh", "Dr Wellington Yueh", "Victime des circonstances, traître par amour", "", False, ""),
    ]),
    ("harkonnen", "House Harkonnen", [
        ("baron", "Baron Harkonnen", "", "Orson Welles", True, "Jodorowsky says he won him over by promising to hire the chef of his favourite Paris restaurant."),
        ("feyd", "Feyd-Rautha", "", "Mick Jagger", True, ""),
        ("rabban", "Rabban la Bête", "Dictateur, idiot, criminel, hermaphrodite", "", False, ""),
        ("piter", "Piter De Vries", "Peter le Mentat", "Udo Kier", True, ""),
        ("general", "General Harkonnen", "", "", False, ""),
    ]),
    ("imperium", "The Imperium", [
        ("emperor", "The Emperor", "Emperor of the Galaxy", "Salvador Dalí", True, "Dalí asked to be the best-paid actor in history. The answer was a fee counted per minute on screen, and a script that kept him there for very few."),
        ("irulan", "Princess Irulan", "", "Amanda Lear", True, ""),
        ("mother", "The Reverend Mother", "Bene Gesserit", "Gloria Swanson", False, ""),
        ("guild", "The Guild", "Eyes blued by the spice", "", False, ""),
        ("sardaukar", "The Sardaukar", "", "", False, "One costume was actually built. Three photographs of it are in this archive."),
    ]),
    ("arrakis", "Dune", [
        ("kynes", "Kynes", "", "", False, ""),
    ]),
    ("court", "Unnamed", [
        ("court", "Figures without a name", "", "", False, "Costume plates that carry no caption anywhere in the archive. They are shown as found."),
    ]),
]

# The same picture reproduced more than once (different scans, crops or
# watermarks). First id in each list is the copy the rooms show; the Atlas
# keeps every one. The build adds any further exact repeats it detects.
SAME = [
    [3, 199], [12, 198], [171, 200], [301, 201], [430, 202], [129, 98, 203, 290],
    [246, 97], [64, 103], [365, 429], [18, 331], [275, 9], [90, 13],
    [277, 417], [278, 441], [280, 418], [282, 439], [410, 398], [317, 57, 204],
    [159, 100], [440, 114], [330, 329], [357, 384], [348, 360], [349, 359, 409],
    [347, 358], [350, 361], [124, 104, 143, 287], [148, 14], [151, 15],
    [125, 221, 177], [250, 147, 112], [91, 243], [285, 256], [152, 368],
    [423, 297], [422, 298], [427, 300], [426, 325], [420, 326, 367],
    [46, 337], [45, 338], [74, 339], [47, 340], [49, 341], [58, 342],
    [54, 343], [60, 344], [67, 345], [392, 87, 401], [393, 402],
    [443, 415, 109], [377, 433], [371, 353, 408], [373, 390], [444, 416],
    [370, 328], [138, 93], [263, 270], [271, 264], [89, 80], [92, 141],
    [110, 137], [346, 150], [165, 140], [236, 286],
]
