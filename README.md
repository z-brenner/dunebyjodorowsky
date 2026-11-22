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
| **The Visions** | Colour-pencil plates from an illustrated edition of the screenplay. |
| **The Word** | Script pages, with five passages typed out as they appear. |
| **The Alchemist** | Jodorowsky's tarot notebooks, which travelled in the same file. |
| **The Relic** | The book as an object, and what its makers did next. |
| **The Atlas** | All 448 plates in file order, with filters and search. |

Every plate opens in a viewer with zoom, its credit, any caption typed beneath it, its sequence number, and other scans of the same picture. **Draw a plate** in the top bar picks one at random.

Plate numbers match the page numbers of the source PDF.

## How the film order was worked out

Each storyboard sheet in the book carries a sequence number in its top-right corner ("12 DUNE"). Those numbers place 36 of the first 90 sequences. Loose frames with no number are placed by what their captions describe, and are labelled "placed by caption". Frames that could not be placed are kept in a "loose leaves" strip at the end.

## What is uncertain

- The file is not a complete copy of the book. Most sequences are missing.
- 77 plates are repeat scans of a picture that appears elsewhere in the file. The rooms show one copy; the Atlas keeps all of them.
- Several costume identifications follow a fan-made chart included in the file (plate 304). Captions inside the archive disagree about Duncan Idaho's costume. Plates say which caption they follow.
- Casting marked *reported* is repeated in accounts of the production but is not confirmed by anything in the archive.
- Five items appear to come from other Dune productions and are kept apart in the Relic room.

## Rebuilding from the PDF

```
python3 tools/build.py /path/to/Jodorowskys_Dune.pdf
```

Needs Python 3, Pillow and poppler's `pdfimages`. It writes `plates/` (the original JPEGs, untouched), `thumbs/` (sprite sheets) and `assets/data.js`. The catalogue of titles, credits, sequences, captions and reel order is `tools/catalog.py`.

## Rights

The MIT licence in this repository covers the code only (`index.html`, `assets/site.css`, `assets/app.js`, `tools/`).

The images in `plates/` and `thumbs/` are the work of Jean Giraud (Moebius), Chris Foss, H.R. Giger, Alejandro Jodorowsky and others, and remain the property of the artists and their estates. They are not licensed by this repository. This is an unofficial study project.
