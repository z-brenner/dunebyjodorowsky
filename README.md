# Jodorowsky's Dune Bible

A reading edition of the *Dune* that Alejandro Jodorowsky prepared in the mid-1970s and never shot: the early draft of the screenplay, told scene by scene, with the surviving drawings and paintings beside it.

Open `index.html` in a browser. There is no build step and no server.

## What is in it

- **The Film.** All 153 numbered scenes of the early draft, in ten chapters. Each scene has its text on the left and its art on the right, every picture in the same plate format. A strip at the top of each chapter shows which scenes have art.
- **The Art.** All 448 plates from the image file, grouped: storyboard, pictures from the screenplay, costumes, machines, Giedi Prime, script pages, everything else.
- **The plate viewer.** Any picture opens large, with who made it, what was done to it, where it sits in the story and why, and a button to see the untouched scan.

Plate numbers match the page numbers of the source PDF.

## What was done to the pictures

The source is a 448-page PDF of scans collected online, mostly small. `tools/restore.py` makes a restored copy of each unique picture in `art/`. The originals in `plates/` are never changed.

- **Lighting evened** on storyboard sheets and cast sheets, so grey photographed paper becomes white.
- **Straightened**, for storyboard sheets photographed at an angle. The frames' own ruled edges are used to undo the tilt. A result is kept only if the frames measurably got squarer; flat scans are left alone. This is conservative, so some tilted sheets are not corrected.
- **Upscaled 4×** with Real-ESRGAN (`realesr-general-x4v3`), blended with a plain resize so the scan's own texture is not lost, then capped at 2,200 px on the long side.

Upscaling invents detail. The fine texture in a restored plate was produced by a model guessing from a small scan. Tiny typed captions do not become readable. Restored plates are labelled as restored everywhere they appear.

## What is original and what is this edition's

- **Words inside scenes:** the screenplay as transcribed, unaltered.
- **Chapter titles and one-line chapter descriptions:** this edition's.
- **Pictures placed by the screenplay:** 39 pictures matched to the typescript's own list of illustrations. Four of these matches were made by content and are labelled "likely".
- **Pictures placed by this edition:** everything else, including all the storyboard, placed from sequence numbers and captions (`PLACE` in `tools/catalog.py`). The storyboard is a later version of the film than this draft, so the fit is loose.
- **Gaps:** nothing was drawn or generated to fill scenes with no art. Those scenes are told by the script alone and say so. Pictures the typescript had but the archive lacks are listed by name.

## Other things that are uncertain

- 77 plates are repeat scans of a picture that appears elsewhere in the file. They are not restored and are listed at the end of The Art.
- Several costume identifications follow a fan-made chart in the file (plate 304).
- Five items appear to come from other Dune productions.
- The transcription has no scene 101, and one page headed "85 (continued)" with no scene 85 before it. Both are left as found.

## Rebuilding

```
python3 tools/build.py /path/to/Jodorowskys_Dune.pdf
python3 tools/restore.py /path/to/realesr-general-x4v3.pth
python3 tools/build.py /path/to/Jodorowskys_Dune.pdf        # again, to pick up the restored plates
python3 tools/build_script.py "/path/to/Jodorowskys Dune Early Draft - Text.pdf"
```

Needs Python 3, Pillow and poppler (`pdfimages`, `pdftotext`). `restore.py` also needs PyTorch, NumPy and OpenCV, and takes about half an hour on four CPU cores.

- `tools/catalog.py` is the catalogue: titles, credits, sequences, captions, chapters, and where each picture is placed.
- `tools/sr.py` is a small runner for the upscaling model.
- `tools/restored.json` records what was done to each plate.
- `tools/pack_hosted.py` bundles the original scans into a few files for hosts that cap the number of files per page. The repository itself serves `plates/` directly.

## Rights

The MIT licence in this repository covers the code only (`index.html`, `assets/site.css`, `assets/app.js`, `tools/`).

The screenplay text in `assets/script.js` is by Alejandro Jodorowsky, from a transcription hosted on the Internet Archive. The images in `plates/`, `art/` and `thumbs/` are the work of Jean Giraud (Moebius), Chris Foss, H.R. Giger, Alejandro Jodorowsky and others. Restoring them does not change whose they are. None of it is licensed by this repository. This is an unofficial study edition.
