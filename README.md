# Kanji Mind-Map (JLPT N5 + N4)

Interactive kanji mind-maps organized by JLPT level, showing on'yomi and kun'yomi
readings with heuristic sample vocabulary.  The same data is rendered as a
printable PDF for each level.

![App screenshot](docs/screenshot.png)

---

## What it does

- **Web app** (static, no build step) — browse N5 and N4 kanji grouped into
  radical-based or hand-transcribed mind-map trees.  Click any kanji node to
  open a detail panel showing stroke count, meanings, on'yomi/kun'yomi
  readings, and example words for each reading.
- **Print / PDF** — `print.html?level=N5` (or `N4`) renders all trees and a
  reference table suitable for printing or exporting to PDF.  PDFs
  (`kanji-N5.pdf`, `kanji-N4.pdf`) are built in CI and downloadable as an
  artifact from the Actions tab, or generated locally (see below).
- **Offline-first** — all data is bundled in `data/n5.json` and `data/n4.json`
  (no runtime network calls from the browser).

---

## Data counts

| Level | Kanji in JSON | Roots (tree groups) |
|-------|--------------|---------------------|
| N5    | 79           | 16 (auto-grouped by Kangxi radical) |
| N4    | 187 (incl. ~21 N5 building-block kanji that appear in curated trees) | 48 (32 curated + 16 auto) |

---

## Hybrid tree-data design

N4 trees were **hand-transcribed** from source mind-map screenshots into
`scripts/trees_n4.py`.  Each root object carries a `kanji` list of child
nodes, each of which may carry further children; the result mirrors the
thematic groupings in the source images.

N5 trees (and the N4 remainder not covered by the curated list) are
**auto-grouped by Kangxi radical** using `scripts/trees_auto.py`.  The script
maps each kanji to its Kangxi radical glyph and builds one root node per
radical.

Both strategies produce the same JSON shape (`data/schema.json`), so the
front-end treats them identically.

> **On/kun vocabulary note:** Example words are selected heuristically from
> JMdict — on'yomi examples are matched by a reading-substring of the
> on-yomi; kun'yomi examples are matched by a reading-prefix of the full kun
> reading (excluding on-reading words).  The selection is example-quality and
> is not exhaustive.

---

## Local development

### Prerequisites

- Python 3.10+ (commands shown use `python`; substitute `python3` on macOS/Linux)
- Node.js 18+
- Git

### 1 — Install dependencies

```bash
python -m venv .venv
# Windows
.venv\Scripts\pip install -r requirements.txt
# macOS / Linux
.venv/bin/pip install -r requirements.txt

# Install Playwright browser (only needed for PDF generation)
python -m playwright install chromium
```

### 2 — Download raw sources (one-time)

```bash
python -m scripts.fetch_sources
```

This downloads KANJIDIC2 and JMdict into `raw/` (gitignored).

### 3 — Build data files

```bash
python -m scripts.build_data
```

Writes `data/n5.json` and `data/n4.json`.

> **Important:** always run pipeline scripts as modules (`python -m scripts.build_data`,
> not `python scripts/build_data.py`) from the repo root — they use
> package-relative imports.

### 4 — Serve the web app

```bash
npm run serve
```

Then open http://localhost:8000.

### 5 — Generate PDFs locally

```bash
python -m pdf.generate_pdf
```

Writes `pdf/kanji-N5.pdf` and `pdf/kanji-N4.pdf`.

---

## Running tests

```bash
# JavaScript (Node built-in runner, 7 tests)
npm test

# Python (pytest, 17 tests)
python -m pytest
```

---

## How to add N3, N2, or N1 later

The schema and code already treat level as a parameter; adding a new level
requires three small steps:

1. **Data** — in `scripts/build_data.py`, add the new level key to
   `_jlpt_chars` (it maps level strings like `"N3"` to the corresponding
   character set).
2. **Trees (optional)** — create `scripts/trees_n3.py` with hand-curated roots
   following the same pattern as `scripts/trees_n4.py`, then import it in
   `build_data.py`.  If no curated file exists, `trees_auto.py` will
   auto-group every kanji in that level by Kangxi radical.
3. **Navigation** — add a `<button data-level="N3">N3</button>` (or equivalent)
   to the `#levels` nav in `index.html` and a matching entry in the level list
   in `print.html`.

No structural changes to `js/` or `css/` are needed.

---

## Deployment

The app is deployed to **GitHub Pages** from the `main` branch via
`.github/workflows/pages.yml`.  Push to `main` to trigger a new deployment.

PDF artifacts are built by `.github/workflows/pdf.yml` on every push and
can be downloaded from the Actions tab.

---

## Attribution

| Asset | Source | Licence |
|-------|--------|---------|
| Kanji readings & meanings | KANJIDIC2, © The Electronic Dictionary Research and Development Group (EDRDG) | CC BY-SA 4.0 |
| Vocabulary examples | JMdict, © EDRDG | CC BY-SA 4.0 |
| JLPT level lists | [davidluzgouveia/kanji-data](https://github.com/davidluzgouveia/kanji-data) (pinned commit SHA in `scripts/sources.py`) | MIT |
| Japanese font | Noto Sans JP, © Google | SIL Open Font Licence 1.1 (OFL) |

The generated files `data/n5.json` and `data/n4.json` are derivative works of
KANJIDIC2 and JMdict and are therefore distributed under **CC BY-SA 4.0**.

Source mind-map screenshots used during N4 tree transcription are third-party
material and are **not** included in this repository (listed in `.gitignore`).
