# Jodorowsky's Dune Bible

An interactive reading of the production book for the *Dune* that Alejandro Jodorowsky prepared in the mid-1970s and never shot.

The source is a 448-page, image-only PDF: a scrapbook of storyboard sheets, costume plates, paintings, script pages and photographs of the book. This site takes it apart and puts it back together so it can be explored.

## What is in it

Open `index.html` in a browser. There is no build step and no server.

| Room | What it holds |
| --- | --- |
| **The Screening** | The storyboard in running order, as ten reels. A projector plays it with the typed French and English captions as subtitles, and ends the way the storyboard does: the whole screen goes blue. |
| **The Players** | Moebius's costume designs grouped by house, with the casting Jodorowsky wanted. |
| **The Machines** | Chris Foss's ships, cars and palaces. |
| **Giedi Prime** | H.R. Giger's Harkonnen castle, sketch sheets and furniture. |
| **The Visions** | Colour-pencil plates from an illustrated typescript of the screenplay, in script order. |
| **The Word** | The complete early draft of the screenplay (153 numbered scenes) as a reader, with a scene list, search, and the archive's pictures set into the text where the typescript had them. |
| **The Alchemist** | Jodorowsky's tarot notebooks, which travelled in the same file. |
| **The Relic** | The book as an object, and what its makers did next. |
| **The Atlas** | All 448 plates in file order, with filters and search. |

Every plate opens in a viewer with zoom, its credit, any caption typed beneath it, its sequence number, and other scans of the same picture. **Draw a plate** in the top bar picks one at random.

Plate numbers match the page numbers of the source PDF.

The script is cross-linked: colour plates and photographed script pages link to their scene, each storyboard reel links to the matching scenes of the draft, and each character shows how often they speak and where they first do.

## How the film order was worked out

Each storyboard sheet in the book carries a sequence number in its top-right corner ("12 DUNE"). Those numbers place 36 of the first 90 sequences. Loose frames with no number are placed by what their captions describe, and are labelled "placed by caption". Frames that could not be placed are kept in a "loose leaves" strip at the end.

## What is uncertain

- The file is not a complete copy of the book. Most sequences are missing.
- 77 plates are repeat scans of a picture that appears elsewhere in the file. The rooms show one copy; the Atlas keeps all of them.
- Several costume identifications follow a fan-made chart included in the file (plate 304). Captions inside the archive disagree about Duncan Idaho's costume. Plates say which caption they follow.
- Casting marked *reported* is repeated in accounts of the production but is not confirmed by anything in the archive.
- Five items appear to come from other Dune productions and are kept apart in the Relic room.
- The early draft and the storyboard are different versions of the film. The scene ranges linked from each reel are approximate.
- The typescript had 76 pictures. 39 slots are filled from the archive; four of those matches are marked "likely" because they were made by content, not by a caption. The other slots are shown empty.
- The transcription has no scene 101, and one page headed "85 (continued)" with no scene 85 before it. Both are left as found.

## Rebuilding from the sources

```
python3 tools/build.py /path/to/Jodorowskys_Dune.pdf
python3 tools/build_script.py "/path/to/Jodorowskys Dune Early Draft - Text.pdf"
```

Needs Python 3, Pillow and poppler (`pdfimages`, `pdftotext`).

- `build.py` writes `plates/` (the original JPEGs, untouched), `thumbs/` (sprite sheets) and `assets/data.js`.
- `build_script.py` parses the text transcription of the early draft into scenes, dialogue, superimposed titles, page marks and illustration slots, and writes `assets/script.js`.
- `tools/catalog.py` holds the catalogue: titles, credits, sequences, captions, reel order, and which archive plate fills which illustration slot.

## Rights

The MIT licence in this repository covers the code only (`index.html`, `assets/site.css`, `assets/app.js`, `tools/`).

The screenplay text in `assets/script.js` is by Alejandro Jodorowsky, from a transcription hosted on the Internet Archive ("Jodorowsky's Dune Early Draft – Text"). It is not licensed by this repository either.

The images in `plates/` and `thumbs/` are the work of Jean Giraud (Moebius), Chris Foss, H.R. Giger, Alejandro Jodorowsky and others, and remain the property of the artists and their estates. They are not licensed by this repository. This is an unofficial study project.
