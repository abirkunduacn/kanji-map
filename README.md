# Kanji Mind-Map (JLPT N5 + N4)

Interactive kanji mind-maps organized by JLPT level, showing on'yomi and kun'yomi
readings with heuristic sample vocabulary.  The same data is rendered as a
printable PDF for each level.

![App screenshot](docs/screenshot.png)

---

## What it does

- **Web app** (static, no build step) — browse N5 and N4 kanji arranged into
  "built-from" mind-map trees, where each kanji branches off the simpler kanji
  it is structurally composed of (e.g. 一 → 元 → 院, 十 → 土 → 主 → 注).  Click
  any kanji node — including the root building-block — to open a detail panel
  showing stroke count, meanings, on'yomi/kun'yomi readings, and example words
  for each reading.
- **Print / PDF** — `print.html?level=N5` (or `N4`) renders all trees and a
  reference table suitable for printing or exporting to PDF.  PDFs
  (`kanji-N5.pdf`, `kanji-N4.pdf`) are built in CI and downloadable as an
  artifact from the Actions tab, or generated locally (see below).
- **Offline-first** — all data is bundled in `data/n5.json` and `data/n4.json`
  (no runtime network calls from the browser).

---

## Data counts

| Level | Kanji in JSON | Clusters |
|-------|--------------|----------|
| N5    | 79           | 10 (chains are short — N5 kanji are mostly primitive building blocks) |
| N4    | 227 (N4 kanji plus the N5 building-block kanji that connect them into chains) | 29 |

---

## Connection model: structural "built-from" trees

Every edge in the mind-map is a real **"is built from"** relationship, computed
from Ideographic Description Sequences (IDS) by `scripts/trees_ids.py`:

- A kanji's **parent** is the most specific *in-scope* kanji that appears in its
  structural decomposition.  So 字 hangs off **子** (字 = ⿱宀子), never off an
  unrelated component, and chains deepen naturally: 一 → 元 → 院, 十 → 土 → 主 → 注.
- **Roots** are real kanji building-blocks (一, 月, 言, 車 …) with no in-scope
  parent; they are clickable like any other node.
- The **N5 view** restricts parents to N5 kanji.  The **N4 view** uses N5 ∪ N4
  so N5 kanji can connect N4 kanji into chains, keeping only trees that contain
  at least one N4 kanji.
- Kanji with no in-scope parent *and* no children are collected into a single
  **"Other (standalone)"** cluster.

This replaced an earlier approach (hand-transcribed trees + Kangxi-radical
grouping) that produced wrong edges (e.g. 字 grouped under 月) and shallow,
disconnected chains.

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

This downloads KANJIDIC2, JMdict, the JLPT level list, and the IDS
decomposition file into `raw/` (gitignored).

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

# Python (pytest, 16 tests)
python -m pytest
```

---

## How to add N3, N2, or N1 later

The schema and code already treat level as a parameter; adding a new level
requires three small steps:

1. **Data** — in `scripts/build_data.py`, add the new level key to
   `_jlpt_chars` (it maps level strings like `"N3"` to the corresponding
   character set), then call `trees_ids.build_forest(...)` for it in `main()`
   exactly as N4 does (scope = lower levels ∪ this level, `required` = this
   level's kanji).  No new tree module is needed — the IDS builder works for
   every level automatically.
2. **Navigation** — add a `<button data-level="N3">N3</button>` (or equivalent)
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
| Kanji structural decomposition (IDS) | [cjkvi-ids](https://github.com/cjkvi/cjkvi-ids), based on the CHISE IDS database (pinned commit SHA in `scripts/sources.py`) | GPLv2 |
| Japanese font | Noto Sans JP, © Google | SIL Open Font Licence 1.1 (OFL) |

> The IDS data (GPLv2) is used only at **build time** to compute factual
> "kanji-X-is-built-from-kanji-Y" relationships; the source file is never
> committed or redistributed.  The generated `data/*.json` contains those
> derived facts together with the EDRDG-derived readings/vocabulary and is
> distributed under **CC BY-SA 4.0**.

The generated files `data/n5.json` and `data/n4.json` are derivative works of
KANJIDIC2 and JMdict and are therefore distributed under **CC BY-SA 4.0**.

Source mind-map screenshots used during N4 tree transcription are third-party
material and are **not** included in this repository (listed in `.gitignore`).
