# Kanji Mind-Map Learning App — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a GitHub-Pages-hosted web app that teaches JLPT kanji (N5 + N4) as interactive mind-maps — each kanji shown with on'yomi/kun'yomi readings and sample vocabulary — plus a printable per-level PDF generated from the same views.

**Architecture:** A static site (vanilla JS + D3.js v7) renders a per-level mind-map tree from a precomputed JSON file; clicking a kanji opens a detail panel with readings and on/kun example vocabulary. A Python data pipeline parses bundled open datasets (KANJIDIC2 for readings/meanings, JMdict for vocabulary) and merges them with the tree structure (N4 transcribed from the source images; N5 auto-grouped by radical) into `data/n5.json` and `data/n4.json`. PDFs are produced by Playwright printing a dedicated print view of each level. GitHub Actions deploys the site to Pages and builds the PDFs.

**Tech Stack:** HTML/CSS/vanilla JS, D3.js v7 (CDN-pinned + vendored fallback), Node's built-in `node:test` for JS logic tests, Python 3.14 (latest-compatible deps) with `lxml` + `pytest` for the data pipeline, Playwright (Python) for PDF, Noto Sans JP bundled font, GitHub Actions for deploy.

## Global Constraints

- **Python execution rule (user global):** NEVER use `python -c "..."`. Any one-off script goes in `Temp/` and is run as a file. Pipeline scripts live in `scripts/` and are part of the repo.
- **Offline-first:** the running web app and the data pipeline must work with no network calls at runtime. Source datasets are downloaded once into `raw/` (gitignored) during data build.
- **No build step for the site:** the deployed site is plain static files (`index.html` + `js/` + `css/` + `data/`). It must open correctly over `http://` (GitHub Pages) and via a local static server. (It need not work over `file://` because it `fetch`es JSON.)
- **Licensing/attribution:** KANJIDIC2 and JMdict are © EDRDG, licensed CC BY-SA 4.0. The README and an in-app footer must credit EDRDG and link the license. Generated `data/*.json` is a derivative and inherits CC BY-SA 4.0.
- **Data schema is fixed** (defined in Task 3) and shared by every task. Validate against it; never invent new fields ad hoc.
- **Japanese font:** bundle `Noto Sans JP` (OFL) under `assets/fonts/` and reference via `@font-face`. Do not rely on system Japanese fonts (CI runners lack them).
- **Levels in scope:** `N5` and `N4` only. The schema and code must treat the level as a parameter so `N3`–`N1` can be added later without code changes.
- **Do not commit the source screenshots:** `Screenshot_*.png` are third-party material (kanji80s.com), used only locally to transcribe the N4 trees. They are gitignored and must never be pushed to the public GitHub repo.
- **Pinned data sources:** JLPT level membership comes from a pinned commit of the MIT-licensed `davidluzgouveia/kanji-data` dataset (`kanji.json`, field `jlpt_new`). Pin the exact commit SHA in `scripts/sources.py` so builds are reproducible.

---

## File Structure

```
Kanji-map/
├── index.html                  # main app shell
├── print.html                  # print-optimized per-level view (used by PDF)
├── .nojekyll                   # tell Pages to serve files as-is
├── css/
│   └── styles.css              # app + print styles
├── assets/fonts/               # Noto Sans JP (woff2) + OFL license
├── js/
│   ├── data-loader.js          # fetch + validate level JSON  (pure, testable)
│   ├── hierarchy.js            # tree → d3.hierarchy input    (pure, testable)
│   ├── mindmap.js              # D3 rendering of the tree
│   ├── detail.js               # kanji detail panel (readings + vocab)
│   └── app.js                  # bootstrap, level switch, wiring
├── data/
│   ├── schema.json             # JSON Schema for a level file
│   ├── n5.json                 # generated
│   └── n4.json                 # generated
├── scripts/                    # Python data pipeline
│   ├── sources.py              # pinned URLs/SHAs + paths
│   ├── fetch_sources.py        # download KANJIDIC2, JMdict, jlpt list → raw/
│   ├── parse_kanjidic.py       # KANJIDIC2 → per-kanji readings/meanings/strokes
│   ├── parse_jmdict.py         # JMdict → vocab index + on/kun selection
│   ├── trees_n4.py             # N4 tree transcribed from source images
│   ├── trees_auto.py           # radical-based auto-grouping (N5 + N4 fallback)
│   └── build_data.py           # orchestrator → data/n5.json, data/n4.json
├── pdf/
│   └── generate_pdf.py         # Playwright: print.html → pdf/kanji-N5.pdf, …
├── tests/
│   ├── python/
│   │   ├── fixtures/           # tiny KANJIDIC2 + JMdict XML fixtures
│   │   ├── test_parse_kanjidic.py
│   │   ├── test_parse_jmdict.py
│   │   ├── test_trees_n4.py
│   │   └── test_build_data.py
│   └── js/
│       ├── data-loader.test.js
│       └── hierarchy.test.js
├── .github/workflows/
│   ├── pages.yml               # deploy static site to GitHub Pages
│   └── pdf.yml                 # build + attach per-level PDFs
├── requirements.txt            # lxml, pytest, jsonschema, playwright
├── package.json                # scripts: test (node --test), serve
├── .gitignore                  # raw/, .venv/, node_modules/, pdf/*.pdf
└── README.md
```

**Decomposition rationale:** parsing (`parse_*.py`), structure (`trees_*.py`), and assembly (`build_data.py`) are separate because they fail and get reviewed independently. On the JS side, the two pure modules (`data-loader.js`, `hierarchy.js`) hold all the testable logic; `mindmap.js`/`detail.js`/`app.js` are thin DOM layers verified manually.

---

## The Source Images (input for Task 5)

Nine screenshots in the project root (`Screenshot_20260626-*.png`) are pages of the **kanji80s.com "JLPT N4 Kanji Mind Map"**. Each page is a tree: a root component on the left branches rightward into related kanji, each labeled with an English meaning. Re-read these at Task 5 to transcribe the full N4 structure. Seed clusters already extracted (root → children, with meanings):

- `一/十` → 生(life)・売(to sell)・士(scholar)・声(voice)・王(king)→主(master)→住(reside)・赤(red)→教(teach)・者(someone)→都(metropolis)・暑(hot)・考(to think)
- `人` → 会(to assemble)・合(fit)→答(answer)・進(advance)・介(between)・界(world/boundary)・以(by means of)・金(gold)→銀(silver)・今(now)
- `口` → 日(sun/day)→車(car)・軍(army)→運(carry)・音(sound)→暗(darkness)・意(idea)・朝(morning)・昼(daytime)・目(eye)→…
- `女` → 安(cheap)・好(fond)・毎(every)→海(sea/ocean)・妹(younger sister)・母(mother)
- `力・乙・也(ground)・几・又・厶・門・月(month/moon)・宀(roof)・尸(corpse)・八・尚` component clusters (see pages 9–12).

---

## Task 1: Project scaffold + dual test harness

**Files:**
- Create: `package.json`, `requirements.txt`, `.gitignore`, `.nojekyll`, `README.md`
- Create: `tests/js/smoke.test.js`, `tests/python/test_smoke.py`
- Create: `scripts/__init__.py` (empty, makes `scripts` importable)

**Interfaces:**
- Produces: `npm test` runs all `tests/js/**/*.test.js` via `node --test`; `pytest` runs `tests/python/`. Both harnesses confirmed working.

- [ ] **Step 1: Write `package.json`**

```json
{
  "name": "kanji-mindmap",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "test": "node --test tests/js/",
    "serve": "python -m http.server 8000"
  }
}
```

- [ ] **Step 2: Write `requirements.txt`**

```
lxml>=5.3
pytest>=8.2
jsonschema>=4.22
playwright>=1.49
```

- [ ] **Step 3: Write `.gitignore`**

```
raw/
.venv/
node_modules/
pdf/*.pdf
__pycache__/
Temp/
# Third-party source screenshots — used only for transcription, never redistributed
Screenshot_*.png
```

- [ ] **Step 4: Write `.nojekyll` (empty file) and a minimal `README.md`**

`README.md`:
```markdown
# Kanji Mind-Map (JLPT N5 + N4)

Interactive kanji mind-maps with on'yomi/kun'yomi readings and sample vocabulary,
plus printable per-level PDFs.

## Data sources
- Readings/meanings: KANJIDIC2 © EDRDG, CC BY-SA 4.0
- Vocabulary: JMdict © EDRDG, CC BY-SA 4.0
- JLPT levels: davidluzgouveia/kanji-data (MIT)

## Develop
1. `python -m venv .venv && .venv/Scripts/pip install -r requirements.txt`
2. `python scripts/fetch_sources.py` (one-time download into `raw/`)
3. `python scripts/build_data.py` (writes `data/n5.json`, `data/n4.json`)
4. `npm run serve` then open http://localhost:8000

## Test
- JS: `npm test`
- Python: `pytest`
```

- [ ] **Step 5: Write the smoke tests**

`tests/js/smoke.test.js`:
```javascript
import { test } from 'node:test';
import assert from 'node:assert/strict';

test('js harness works', () => {
  assert.equal(1 + 1, 2);
});
```

`tests/python/test_smoke.py`:
```python
def test_python_harness_works():
    assert 1 + 1 == 2
```

`scripts/__init__.py`: (empty file)

- [ ] **Step 6: Run both harnesses**

Run: `npm test`
Expected: PASS (1 test).
Run: `pytest tests/python/test_smoke.py -v`
Expected: PASS (1 test).

- [ ] **Step 7: Commit**

```bash
git init
git add .
git commit -m "chore: scaffold project with JS + Python test harnesses"
```

---

## Task 2: Pinned sources + downloader

**Files:**
- Create: `scripts/sources.py`
- Create: `scripts/fetch_sources.py`
- Test: `tests/python/test_sources.py`

**Interfaces:**
- Produces: `scripts.sources` exposes `RAW_DIR: Path`, `KANJIDIC2_PATH: Path`, `JMDICT_PATH: Path`, `JLPT_PATH: Path`, and `SOURCES: list[dict]` (each `{name,url,dest,gzip:bool}`). `fetch_sources.main()` downloads any missing file.

- [ ] **Step 1: Write the failing test**

`tests/python/test_sources.py`:
```python
from scripts import sources

def test_source_paths_are_under_raw():
    for p in (sources.KANJIDIC2_PATH, sources.JMDICT_PATH, sources.JLPT_PATH):
        assert sources.RAW_DIR in p.parents

def test_sources_list_is_pinned():
    assert len(sources.SOURCES) == 3
    # JLPT source must be pinned to an exact commit SHA, not a branch
    jlpt = next(s for s in sources.SOURCES if s["name"] == "jlpt")
    assert "/master/" not in jlpt["url"] and "/main/" not in jlpt["url"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/python/test_sources.py -v`
Expected: FAIL with `ModuleNotFoundError: scripts.sources`.

- [ ] **Step 3: Write `scripts/sources.py`**

```python
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "raw"

KANJIDIC2_PATH = RAW_DIR / "kanjidic2.xml"
JMDICT_PATH = RAW_DIR / "JMdict_e.xml"
JLPT_PATH = RAW_DIR / "kanji-data.json"

# Pinned commit for reproducibility. Update the SHA deliberately, never to a branch.
_KANJI_DATA_SHA = "8d36d2b3ba36c4a78c1d3b3c3b8b6b7d6b6b6b6b"  # replace with verified SHA at exec

SOURCES = [
    {
        "name": "kanjidic2",
        "url": "http://www.edrdg.org/kanjidic/kanjidic2.xml.gz",
        "dest": KANJIDIC2_PATH,
        "gzip": True,
    },
    {
        "name": "jmdict",
        "url": "http://ftp.edrdg.org/pub/Nihongo/JMdict_e.gz",
        "dest": JMDICT_PATH,
        "gzip": True,
    },
    {
        "name": "jlpt",
        "url": f"https://raw.githubusercontent.com/davidluzgouveia/kanji-data/{_KANJI_DATA_SHA}/kanji.json",
        "dest": JLPT_PATH,
        "gzip": False,
    },
]
```

> **At execution:** open `https://github.com/davidluzgouveia/kanji-data/commits/master/kanji.json`, copy the latest full commit SHA, and replace `_KANJI_DATA_SHA`. Verify the URL returns 200 before continuing.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/python/test_sources.py -v`
Expected: PASS.

- [ ] **Step 5: Write `scripts/fetch_sources.py`**

```python
import gzip
import shutil
import urllib.request
from pathlib import Path

from scripts.sources import SOURCES, RAW_DIR


def _download(url: str, dest: Path, is_gzip: bool) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    print(f"Downloading {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "kanji-mindmap-build"})
    with urllib.request.urlopen(req) as resp, open(tmp, "wb") as fh:
        shutil.copyfileobj(resp, fh)
    if is_gzip:
        with gzip.open(tmp, "rb") as gz, open(dest, "wb") as out:
            shutil.copyfileobj(gz, out)
        tmp.unlink()
    else:
        tmp.replace(dest)
    print(f"  -> {dest} ({dest.stat().st_size} bytes)")


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for s in SOURCES:
        if s["dest"].exists():
            print(f"Skip (exists): {s['dest']}")
            continue
        _download(s["url"], s["dest"], s["gzip"])


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Run the downloader once (manual, network)**

Run: `.venv/Scripts/python scripts/fetch_sources.py`
Expected: three files created in `raw/`. Confirm: `raw/kanjidic2.xml` starts with `<?xml`, `raw/JMdict_e.xml` starts with `<?xml`, `raw/kanji-data.json` parses as JSON.

- [ ] **Step 7: Commit**

```bash
git add scripts/sources.py scripts/fetch_sources.py tests/python/test_sources.py
git commit -m "feat: pinned data sources and downloader"
```

---

## Task 3: Level JSON schema + KANJIDIC2 parser

**Files:**
- Create: `data/schema.json`
- Create: `scripts/parse_kanjidic.py`
- Create: `tests/python/fixtures/kanjidic2_min.xml`
- Test: `tests/python/test_parse_kanjidic.py`

**Interfaces:**
- Produces: `parse_kanjidic.parse(path, wanted: set[str]) -> dict[str, KanjiInfo]` where `KanjiInfo` is a `dict` with keys `char:str, meanings:list[str], on:list[str], kun:list[str], strokes:int`. Only kanji in `wanted` are returned.
- Produces: `data/schema.json` — the authoritative JSON Schema for `data/<level>.json`. All later tasks validate against it.

- [ ] **Step 1: Write `data/schema.json`**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["level", "generated", "roots", "kanji"],
  "properties": {
    "level": { "type": "string", "enum": ["N5", "N4", "N3", "N2", "N1"] },
    "generated": { "type": "string" },
    "roots": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "root", "label", "children"],
        "properties": {
          "id": { "type": "string" },
          "root": { "type": "string" },
          "label": { "type": "string" },
          "children": { "type": "array", "items": { "$ref": "#/definitions/node" } }
        }
      }
    },
    "kanji": {
      "type": "object",
      "additionalProperties": { "$ref": "#/definitions/kanjiInfo" }
    }
  },
  "definitions": {
    "node": {
      "type": "object",
      "required": ["char", "label", "children"],
      "properties": {
        "char": { "type": "string", "minLength": 1, "maxLength": 1 },
        "label": { "type": "string" },
        "children": { "type": "array", "items": { "$ref": "#/definitions/node" } }
      }
    },
    "kanjiInfo": {
      "type": "object",
      "required": ["char", "meanings", "on", "kun", "strokes", "vocab"],
      "properties": {
        "char": { "type": "string", "minLength": 1, "maxLength": 1 },
        "meanings": { "type": "array", "items": { "type": "string" } },
        "on": { "type": "array", "items": { "type": "string" } },
        "kun": { "type": "array", "items": { "type": "string" } },
        "strokes": { "type": "integer", "minimum": 1 },
        "vocab": {
          "type": "object",
          "required": ["on", "kun"],
          "properties": {
            "on": { "type": "array", "items": { "$ref": "#/definitions/vocab" } },
            "kun": { "type": "array", "items": { "$ref": "#/definitions/vocab" } }
          }
        }
      }
    },
    "vocab": {
      "type": "object",
      "required": ["word", "reading", "gloss"],
      "properties": {
        "word": { "type": "string" },
        "reading": { "type": "string" },
        "gloss": { "type": "string" }
      }
    }
  }
}
```

- [ ] **Step 2: Write the fixture `tests/python/fixtures/kanjidic2_min.xml`**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<kanjidic2>
  <character>
    <literal>生</literal>
    <misc><stroke_count>5</stroke_count></misc>
    <reading_meaning>
      <rmgroup>
        <reading r_type="ja_on">セイ</reading>
        <reading r_type="ja_on">ショウ</reading>
        <reading r_type="ja_kun">い.きる</reading>
        <reading r_type="ja_kun">う.まれる</reading>
        <reading r_type="pinyin">sheng1</reading>
        <meaning>life</meaning>
        <meaning>genuine</meaning>
        <meaning m_lang="fr">vie</meaning>
      </rmgroup>
    </reading_meaning>
  </character>
  <character>
    <literal>一</literal>
    <misc><stroke_count>1</stroke_count></misc>
    <reading_meaning>
      <rmgroup>
        <reading r_type="ja_on">イチ</reading>
        <reading r_type="ja_kun">ひと.つ</reading>
        <meaning>one</meaning>
      </rmgroup>
    </reading_meaning>
  </character>
</kanjidic2>
```

- [ ] **Step 3: Write the failing test**

`tests/python/test_parse_kanjidic.py`:
```python
from pathlib import Path
from scripts import parse_kanjidic

FIX = Path(__file__).parent / "fixtures" / "kanjidic2_min.xml"

def test_parses_readings_meanings_strokes():
    out = parse_kanjidic.parse(FIX, wanted={"生"})
    assert set(out) == {"生"}
    k = out["生"]
    assert k["on"] == ["セイ", "ショウ"]
    assert k["kun"] == ["い.きる", "う.まれる"]
    assert k["meanings"] == ["life", "genuine"]   # French meaning excluded
    assert k["strokes"] == 5

def test_filters_to_wanted_only():
    out = parse_kanjidic.parse(FIX, wanted={"一"})
    assert set(out) == {"一"}
```

- [ ] **Step 4: Run test to verify it fails**

Run: `pytest tests/python/test_parse_kanjidic.py -v`
Expected: FAIL with `ModuleNotFoundError: scripts.parse_kanjidic`.

- [ ] **Step 5: Write `scripts/parse_kanjidic.py`**

```python
from pathlib import Path
from lxml import etree


def parse(path: Path, wanted: set[str]) -> dict[str, dict]:
    result: dict[str, dict] = {}
    context = etree.iterparse(str(path), tag="character")
    for _, char_el in context:
        literal = char_el.findtext("literal")
        if literal in wanted:
            result[literal] = _extract(char_el, literal)
        char_el.clear()
        while char_el.getprevious() is not None:
            del char_el.getparent()[0]
    return result


def _extract(char_el, literal: str) -> dict:
    strokes = int(char_el.findtext("misc/stroke_count") or 0)
    on, kun, meanings = [], [], []
    rmgroup = char_el.find("reading_meaning/rmgroup")
    if rmgroup is not None:
        for r in rmgroup.findall("reading"):
            t = r.get("r_type")
            if t == "ja_on":
                on.append(r.text)
            elif t == "ja_kun":
                kun.append(r.text)
        for m in rmgroup.findall("meaning"):
            if m.get("m_lang") is None:  # English only
                meanings.append(m.text)
    return {
        "char": literal,
        "meanings": meanings,
        "on": on,
        "kun": kun,
        "strokes": strokes,
    }
```

- [ ] **Step 6: Run test to verify it passes**

Run: `pytest tests/python/test_parse_kanjidic.py -v`
Expected: PASS (2 tests).

- [ ] **Step 7: Commit**

```bash
git add data/schema.json scripts/parse_kanjidic.py tests/python/fixtures/kanjidic2_min.xml tests/python/test_parse_kanjidic.py
git commit -m "feat: level JSON schema and KANJIDIC2 parser"
```

---

## Task 4: JMdict parser + on/kun vocabulary selection

**Files:**
- Create: `scripts/parse_jmdict.py`
- Create: `tests/python/fixtures/jmdict_min.xml`
- Test: `tests/python/test_parse_jmdict.py`

**Interfaces:**
- Consumes: per-kanji `on`/`kun` reading lists from Task 3.
- Produces: `parse_jmdict.build_index(path, wanted: set[str]) -> VocabIndex`. `VocabIndex.select(char, on, kun, limit=2) -> {"on":[v], "kun":[v]}` where each `v` is `{"word","reading","gloss"}`. Selection rule: a word is an **on** example if its kana reading contains the hiragana form of any of the kanji's on-readings; a **kun** example if it contains the hiragana stem (text before `.`) of any kun-reading. Within each bucket, prefer words carrying a priority tag (`news1/ichi1/spec1/spec2/gai1`), then shorter words. Cap at `limit` each.

- [ ] **Step 1: Write the fixture `tests/python/fixtures/jmdict_min.xml`**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<JMdict>
  <entry>
    <k_ele><keb>生活</keb><ke_pri>news1</ke_pri></k_ele>
    <r_ele><reb>せいかつ</reb><re_pri>news1</re_pri></r_ele>
    <sense><gloss>life</gloss><gloss>living</gloss></sense>
  </entry>
  <entry>
    <k_ele><keb>生きる</keb><ke_pri>ichi1</ke_pri></k_ele>
    <r_ele><reb>いきる</reb><re_pri>ichi1</re_pri></r_ele>
    <sense><gloss>to live</gloss></sense>
  </entry>
  <entry>
    <k_ele><keb>一生</keb></k_ele>
    <r_ele><reb>いっしょう</reb></r_ele>
    <sense><gloss>whole life</gloss></sense>
  </entry>
  <entry>
    <k_ele><keb>犬</keb><ke_pri>ichi1</ke_pri></k_ele>
    <r_ele><reb>いぬ</reb><re_pri>ichi1</re_pri></r_ele>
    <sense><gloss>dog</gloss></sense>
  </entry>
</JMdict>
```

- [ ] **Step 2: Write the failing test**

`tests/python/test_parse_jmdict.py`:
```python
from pathlib import Path
from scripts import parse_jmdict

FIX = Path(__file__).parent / "fixtures" / "jmdict_min.xml"

def test_selects_on_and_kun_examples():
    idx = parse_jmdict.build_index(FIX, wanted={"生"})
    picks = idx.select("生", on=["セイ", "ショウ"], kun=["い.きる", "う.まれる"], limit=2)
    on_words = {v["word"] for v in picks["on"]}
    kun_words = {v["word"] for v in picks["kun"]}
    assert "生活" in on_words          # reading せいかつ contains せい
    assert "生きる" in kun_words        # reading いきる contains stem い... matches kun い.きる
    # gloss carried through
    assert picks["on"][0]["gloss"] == "life"

def test_katakana_on_reading_is_matched_as_hiragana():
    idx = parse_jmdict.build_index(FIX, wanted={"生"})
    picks = idx.select("生", on=["セイ"], kun=[], limit=2)
    assert any(v["reading"] == "せいかつ" for v in picks["on"])
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/python/test_parse_jmdict.py -v`
Expected: FAIL with `ModuleNotFoundError: scripts.parse_jmdict`.

- [ ] **Step 4: Write `scripts/parse_jmdict.py`**

```python
from pathlib import Path
from lxml import etree

_PRI_TAGS = {"news1", "ichi1", "spec1", "spec2", "gai1"}

# Katakana block U+30A1–U+30F6 maps to hiragana by subtracting 0x60.
def kata_to_hira(s: str) -> str:
    out = []
    for ch in s:
        code = ord(ch)
        if 0x30A1 <= code <= 0x30F6:
            out.append(chr(code - 0x60))
        else:
            out.append(ch)
    return "".join(out)


def _on_keys(on: list[str]) -> list[str]:
    # セイ -> せい ; drop length marker handling kept simple
    return [kata_to_hira(r).replace("ー", "") for r in on if r]


def _kun_keys(kun: list[str]) -> list[str]:
    # い.きる -> stem before the dot: い ; う.まれる -> う ; 表-prefixed '-' markers stripped
    keys = []
    for r in kun:
        if not r:
            continue
        stem = r.split(".")[0].replace("-", "")
        if stem:
            keys.append(stem)
    return keys


class VocabIndex:
    def __init__(self, by_char: dict[str, list[dict]]):
        self._by_char = by_char

    def select(self, char: str, on: list[str], kun: list[str], limit: int = 2) -> dict:
        entries = self._by_char.get(char, [])
        on_keys = _on_keys(on)
        kun_keys = _kun_keys(kun)

        def matches(reading: str, keys: list[str]) -> bool:
            return any(k and k in reading for k in keys)

        def rank(e: dict):
            return (0 if e["pri"] else 1, len(e["word"]))

        on_hits = sorted((e for e in entries if matches(e["reading"], on_keys)), key=rank)
        kun_hits = sorted((e for e in entries if matches(e["reading"], kun_keys)), key=rank)

        def fmt(e):
            return {"word": e["word"], "reading": e["reading"], "gloss": e["gloss"]}

        return {
            "on": [fmt(e) for e in on_hits[:limit]],
            "kun": [fmt(e) for e in kun_hits[:limit]],
        }


def build_index(path: Path, wanted: set[str]) -> VocabIndex:
    by_char: dict[str, list[dict]] = {c: [] for c in wanted}
    context = etree.iterparse(str(path), tag="entry", resolve_entities=False)
    for _, entry in context:
        kebs = entry.findall("k_ele")
        reb = entry.findtext("r_ele/reb")
        gloss = entry.findtext("sense/gloss")
        if reb and gloss:
            for k in kebs:
                keb = k.findtext("keb")
                if not keb:
                    continue
                pri = any(p.text in _PRI_TAGS for p in k.findall("ke_pri"))
                record = {"word": keb, "reading": reb, "gloss": gloss, "pri": pri}
                for ch in set(keb) & wanted:
                    by_char[ch].append(record)
        entry.clear()
        while entry.getprevious() is not None:
            del entry.getparent()[0]
    return VocabIndex(by_char)
```

> **Note on DTD entities:** JMdict uses entity refs in `<pos>` etc. We never read `<pos>`, and `resolve_entities=False` avoids needing the DTD. If lxml still raises on undefined entities, add `load_dtd=False, no_network=True` to `iterparse`.

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/python/test_parse_jmdict.py -v`
Expected: PASS (2 tests).

- [ ] **Step 6: Commit**

```bash
git add scripts/parse_jmdict.py tests/python/fixtures/jmdict_min.xml tests/python/test_parse_jmdict.py
git commit -m "feat: JMdict parser with on/kun vocab selection"
```

---

## Task 5: N4 tree (transcribed from source images)

**Files:**
- Create: `scripts/trees_n4.py`
- Test: `tests/python/test_trees_n4.py`

**Interfaces:**
- Produces: `trees_n4.ROOTS: list[Root]` where `Root = {"id":str, "root":str, "label":str, "children":[Node]}` and `Node = {"char":str, "label":str, "children":[Node]}`. `trees_n4.placed_kanji() -> set[str]` returns every `char` appearing in any node (not roots, which may be non-JLPT components).

- [ ] **Step 1: Write the failing test**

`tests/python/test_trees_n4.py`:
```python
from scripts import trees_n4

def test_roots_have_required_shape():
    assert trees_n4.ROOTS, "expected at least one root"
    for r in trees_n4.ROOTS:
        assert set(r) >= {"id", "root", "label", "children"}
        assert isinstance(r["children"], list)

def test_placed_kanji_are_single_chars():
    placed = trees_n4.placed_kanji()
    assert placed, "expected placed kanji"
    assert all(len(c) == 1 for c in placed)

def test_known_clusters_present():
    placed = trees_n4.placed_kanji()
    # Spot-check clusters visible in the source screenshots.
    for c in ["生", "売", "声", "会", "海", "妹", "運", "暗"]:
        assert c in placed, f"{c} should be transcribed from the N4 images"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/python/test_trees_n4.py -v`
Expected: FAIL with `ModuleNotFoundError: scripts.trees_n4`.

- [ ] **Step 3: Transcribe the images into `scripts/trees_n4.py`**

Re-read all nine `Screenshot_20260626-*.png` files. Transcribe every tree. Use this exact structure; the seed below is partial — **extend it to cover every cluster in the images**. A helper keeps entries terse.

```python
def n(char, label, *children):
    return {"char": char, "label": label, "children": list(children)}

def root(id, root_char, label, *children):
    return {"id": id, "root": root_char, "label": label, "children": list(children)}

# Seed transcription (extend to ALL clusters across the 9 screenshots).
ROOTS = [
    root("ichi-juu", "十", "One / Ten",
        n("生", "life",
            n("売", "to sell"),
            n("産", "give birth")),
        n("士", "scholar",
            n("売", "to sell"),
            n("仕", "serve")),
        n("声", "voice"),
        n("王", "king",
            n("主", "master",
                n("住", "reside"),
                n("注", "concentrate"))),
        n("赤", "red",
            n("教", "teach")),
        n("者", "someone",
            n("都", "metropolis"),
            n("暑", "hot"),
            n("考", "to think"))),
    root("hito", "人", "Person",
        n("会", "to assemble"),
        n("合", "fit", n("答", "answer")),
        n("進", "advance"),
        n("介", "between", n("界", "world, boundary")),
        n("以", "by means of"),
        n("金", "gold", n("銀", "silver")),
        n("今", "now")),
    root("kuchi", "口", "Mouth",
        n("日", "sun, day",
            n("車", "car"),
            n("軍", "army", n("運", "carry")),
            n("音", "sound", n("暗", "darkness"), n("意", "idea")),
            n("朝", "morning"),
            n("昼", "daytime")),
        n("目", "eye")),
    root("onna", "女", "Woman",
        n("安", "cheap"),
        n("好", "fond, pleasing"),
        n("毎", "every", n("海", "sea, ocean")),
        n("妹", "younger sister"),
        n("母", "mother")),
    # ... CONTINUE: 力, 乙, 也, 几, 又, 厶, 門, 月, 宀, 尸, 八, 尚 clusters (pages 9–12).
]

def _walk(nodes):
    for node in nodes:
        yield node["char"]
        yield from _walk(node["children"])

def placed_kanji() -> set[str]:
    out = set()
    for r in ROOTS:
        out.update(_walk(r["children"]))
    return out
```

> **Completion rule:** transcribe until `test_known_clusters_present` passes AND a manual diff against the official N4 list (available after Task 7) shows the unplaced remainder is only kanji genuinely absent from the images. Those go to auto-grouping in Task 6/7 — do not invent tree relationships.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/python/test_trees_n4.py -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add scripts/trees_n4.py tests/python/test_trees_n4.py
git commit -m "feat: transcribe N4 kanji mind-map trees from source images"
```

---

## Task 6: Radical-based auto-grouping (N5 + N4 fallback)

**Files:**
- Create: `scripts/trees_auto.py`
- Test: `tests/python/test_trees_auto.py`

**Interfaces:**
- Consumes: per-kanji info dicts from Task 3 (uses `char`, `meanings`) and a radical lookup.
- Produces: `trees_auto.build(kanji_infos: dict[str, dict], radicals: dict[str, str]) -> list[Root]`. Groups kanji by their radical char; each group becomes a root `{"id": "auto-<radical>", "root": <radical>, "label": <radical-meaning-or-radical>, "children": [flat list of nodes]}`. Each node's `label` is the kanji's first meaning. Kanji sharing a radical are siblings (one level deep). Radicals with a single kanji are merged into an `"auto-misc"` root.

- [ ] **Step 1: Write the failing test**

`tests/python/test_trees_auto.py`:
```python
from scripts import trees_auto

def test_groups_by_radical():
    infos = {
        "海": {"char": "海", "meanings": ["sea"]},
        "活": {"char": "活", "meanings": ["lively"]},
        "犬": {"char": "犬", "meanings": ["dog"]},
    }
    radicals = {"海": "氵", "活": "氵", "犬": "犬"}
    roots = trees_auto.build(infos, radicals)
    by_id = {r["id"]: r for r in roots}
    water = by_id["auto-氵"]
    chars = {c["char"] for c in water["children"]}
    assert chars == {"海", "活"}
    # singletons collapse into misc
    assert "犬" in {c["char"] for c in by_id["auto-misc"]["children"]}

def test_node_label_is_first_meaning():
    infos = {"海": {"char": "海", "meanings": ["sea", "ocean"]}}
    radicals = {"海": "氵", "活": "氵"}  # second radical member to avoid misc-collapse
    infos["活"] = {"char": "活", "meanings": ["lively"]}
    roots = trees_auto.build(infos, radicals)
    node = next(c for r in roots for c in r["children"] if c["char"] == "海")
    assert node["label"] == "sea"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/python/test_trees_auto.py -v`
Expected: FAIL with `ModuleNotFoundError: scripts.trees_auto`.

- [ ] **Step 3: Write `scripts/trees_auto.py`**

```python
from collections import defaultdict


def build(kanji_infos: dict[str, dict], radicals: dict[str, str]) -> list[dict]:
    groups: dict[str, list[str]] = defaultdict(list)
    for char in kanji_infos:
        rad = radicals.get(char, "?")
        groups[rad].append(char)

    roots = []
    misc_children = []
    for rad, chars in sorted(groups.items()):
        children = [_node(c, kanji_infos[c]) for c in sorted(chars)]
        if len(children) == 1:
            misc_children.extend(children)
        else:
            roots.append({
                "id": f"auto-{rad}",
                "root": rad,
                "label": rad,
                "children": children,
            })
    if misc_children:
        roots.append({
            "id": "auto-misc",
            "root": "他",
            "label": "Other",
            "children": sorted(misc_children, key=lambda n: n["char"]),
        })
    return roots


def _node(char: str, info: dict) -> dict:
    meanings = info.get("meanings") or []
    return {"char": char, "label": meanings[0] if meanings else char, "children": []}
```

> **Radical source:** KANJIDIC2 has `<radical><rad_value rad_type="classical">N</rad_type></radical>` (a Kangxi index number 1–214). Extend `parse_kanjidic._extract` to also capture `radical = int(.../rad_value[@rad_type='classical'])`, and add a static `KANGXI[int] -> char` map (214 entries) in `trees_auto.py`. Build the `radicals: dict[char,str]` in `build_data.py` from these. (Add a one-line test in `test_parse_kanjidic.py` asserting `out["生"]["radical"] == 100` once captured.)

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/python/test_trees_auto.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add scripts/trees_auto.py tests/python/test_trees_auto.py
git commit -m "feat: radical-based auto-grouping for trees"
```

---

## Task 7: Build orchestrator → data/n5.json + data/n4.json

**Files:**
- Modify: `scripts/parse_kanjidic.py` (add `radical` capture per Task 6 note)
- Create: `scripts/build_data.py`
- Test: `tests/python/test_build_data.py`

**Interfaces:**
- Consumes: `parse_kanjidic.parse`, `parse_jmdict.build_index`, `trees_n4.ROOTS`/`placed_kanji`, `trees_auto.build`, `data/schema.json`.
- Produces: `build_data.build_level(level, kanji_chars, kanji_infos, vocab_index, roots) -> dict` (a schema-valid level dict) and `build_data.main()` which writes `data/n5.json` and `data/n4.json`. Level dict shape is exactly Task 3's schema.

- [ ] **Step 1: Write the failing test**

`tests/python/test_build_data.py`:
```python
import json
from pathlib import Path
import jsonschema
from scripts import build_data, parse_jmdict

SCHEMA = json.loads((Path(__file__).parents[2] / "data" / "schema.json").read_text(encoding="utf-8"))
JMFIX = Path(__file__).parent / "fixtures" / "jmdict_min.xml"

def test_build_level_is_schema_valid_and_complete():
    infos = {
        "生": {"char": "生", "meanings": ["life"], "on": ["セイ"], "kun": ["い.きる"], "strokes": 5},
        "犬": {"char": "犬", "meanings": ["dog"], "on": ["ケン"], "kun": ["いぬ"], "strokes": 4},
    }
    idx = parse_jmdict.build_index(JMFIX, wanted={"生", "犬"})
    roots = [{"id": "r1", "root": "口", "label": "Mouth",
              "children": [{"char": "生", "label": "life", "children": []},
                           {"char": "犬", "label": "dog", "children": []}]}]
    level = build_data.build_level("N5", {"生", "犬"}, infos, idx, roots)
    jsonschema.validate(level, SCHEMA)         # raises on any schema violation
    # every kanji placed in a node has a detail entry
    assert set(level["kanji"]) == {"生", "犬"}
    assert level["kanji"]["生"]["vocab"]["on"]   # 生活 picked up
    assert level["level"] == "N5"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/python/test_build_data.py -v`
Expected: FAIL with `ModuleNotFoundError: scripts.build_data`.

- [ ] **Step 3: Write `scripts/build_data.py`**

```python
import json
from datetime import date
from pathlib import Path

import jsonschema

from scripts import parse_kanjidic, parse_jmdict, trees_n4, trees_auto
from scripts.sources import KANJIDIC2_PATH, JMDICT_PATH, JLPT_PATH

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SCHEMA = json.loads((DATA_DIR / "schema.json").read_text(encoding="utf-8"))


def _placed_in(roots: list[dict]) -> set[str]:
    out = set()

    def walk(nodes):
        for node in nodes:
            out.add(node["char"])
            walk(node["children"])

    for r in roots:
        walk(r["children"])
    return out


def build_level(level, kanji_chars, kanji_infos, vocab_index, roots) -> dict:
    placed = _placed_in(roots)
    kanji = {}
    for ch in sorted(placed):
        info = kanji_infos[ch]
        vocab = vocab_index.select(ch, info.get("on", []), info.get("kun", []), limit=2)
        kanji[ch] = {
            "char": ch,
            "meanings": info.get("meanings", []),
            "on": info.get("on", []),
            "kun": info.get("kun", []),
            "strokes": info.get("strokes", 1) or 1,
            "vocab": vocab,
        }
    level_dict = {
        "level": level,
        "generated": date.today().isoformat(),
        "roots": roots,
        "kanji": kanji,
    }
    jsonschema.validate(level_dict, SCHEMA)
    return level_dict


def _jlpt_chars() -> dict[str, set[str]]:
    raw = json.loads(JLPT_PATH.read_text(encoding="utf-8"))
    levels = {"N5": set(), "N4": set()}
    for char, meta in raw.items():
        jl = meta.get("jlpt_new")
        if jl == 5:
            levels["N5"].add(char)
        elif jl == 4:
            levels["N4"].add(char)
    return levels


def main() -> None:
    levels = _jlpt_chars()
    all_wanted = levels["N5"] | levels["N4"]
    kanji_infos = parse_kanjidic.parse(KANJIDIC2_PATH, wanted=all_wanted)
    radicals = {c: trees_auto.kangxi_char(i["radical"]) for c, i in kanji_infos.items()}
    vocab_index = parse_jmdict.build_index(JMDICT_PATH, wanted=all_wanted)

    # N4: transcribed trees + auto-group the remainder.
    n4_chars = levels["N4"]
    n4_placed = trees_n4.placed_kanji() & n4_chars
    n4_remainder = {c: kanji_infos[c] for c in n4_chars - n4_placed}
    n4_roots = trees_n4.ROOTS + trees_auto.build(n4_remainder, radicals)
    n4 = build_level("N4", n4_chars, kanji_infos, vocab_index, n4_roots)

    # N5: fully auto-grouped.
    n5_chars = levels["N5"]
    n5_infos = {c: kanji_infos[c] for c in n5_chars}
    n5_roots = trees_auto.build(n5_infos, radicals)
    n5 = build_level("N5", n5_chars, kanji_infos, vocab_index, n5_roots)

    (DATA_DIR / "n4.json").write_text(json.dumps(n4, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA_DIR / "n5.json").write_text(json.dumps(n5, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote N4 ({len(n4['kanji'])} kanji) and N5 ({len(n5['kanji'])} kanji)")


if __name__ == "__main__":
    main()
```

> Add `kangxi_char(index:int)->str` to `trees_auto.py` backed by the 214-entry `KANGXI` map. Filter `trees_n4.ROOTS` children to N4-only chars inside `placed_kanji()` intersection (already done above) so a stray transcription never injects a non-N4 kanji.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/python/test_build_data.py -v`
Expected: PASS.

- [ ] **Step 5: Run the full build (manual, needs `raw/` from Task 2)**

Run: `.venv/Scripts/python scripts/build_data.py`
Expected: prints kanji counts (~80 for N5, ~170 for N4); `data/n5.json` and `data/n4.json` exist and are valid UTF-8 JSON with non-ASCII kanji preserved.

- [ ] **Step 6: Run the whole Python suite**

Run: `pytest -v`
Expected: all PASS.

- [ ] **Step 7: Commit**

```bash
git add scripts/build_data.py scripts/parse_kanjidic.py scripts/trees_auto.py tests/python/test_build_data.py data/n5.json data/n4.json
git commit -m "feat: build orchestrator producing N5 and N4 level data"
```

---

## Task 8: JS data loader + validator (pure)

**Files:**
- Create: `js/data-loader.js`
- Test: `tests/js/data-loader.test.js`

**Interfaces:**
- Produces: `validateLevelData(data)` returns `{ok:true}` or `{ok:false, error:string}`; throws nothing. `loadLevel(level, fetchFn=fetch)` returns the parsed, validated level object (rejects if invalid). `kanjiCount(data)` returns the number of detail entries.

- [ ] **Step 1: Write the failing test**

`tests/js/data-loader.test.js`:
```javascript
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { validateLevelData, loadLevel, kanjiCount } from '../../js/data-loader.js';

const good = {
  level: 'N5', generated: '2026-06-26',
  roots: [{ id: 'r', root: '口', label: 'Mouth',
            children: [{ char: '生', label: 'life', children: [] }] }],
  kanji: { '生': { char: '生', meanings: ['life'], on: ['セイ'], kun: ['い.きる'],
                   strokes: 5, vocab: { on: [], kun: [] } } },
};

test('valid data passes', () => {
  assert.deepEqual(validateLevelData(good), { ok: true });
});

test('missing kanji entry for a placed node fails', () => {
  const bad = structuredClone(good);
  delete bad.kanji['生'];
  const res = validateLevelData(bad);
  assert.equal(res.ok, false);
  assert.match(res.error, /生/);
});

test('kanjiCount counts entries', () => {
  assert.equal(kanjiCount(good), 1);
});

test('loadLevel fetches and validates', async () => {
  const fakeFetch = async (url) => ({ ok: true, json: async () => good });
  const data = await loadLevel('N5', fakeFetch);
  assert.equal(data.level, 'N5');
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm test`
Expected: FAIL — cannot find `../../js/data-loader.js`.

- [ ] **Step 3: Write `js/data-loader.js`**

```javascript
function walkChars(nodes, out) {
  for (const node of nodes) {
    out.add(node.char);
    walkChars(node.children || [], out);
  }
}

export function validateLevelData(data) {
  if (!data || typeof data !== 'object') return { ok: false, error: 'not an object' };
  for (const key of ['level', 'roots', 'kanji']) {
    if (!(key in data)) return { ok: false, error: `missing ${key}` };
  }
  const placed = new Set();
  for (const root of data.roots) walkChars(root.children || [], placed);
  for (const ch of placed) {
    if (!data.kanji[ch]) return { ok: false, error: `no detail entry for placed kanji ${ch}` };
  }
  return { ok: true };
}

export function kanjiCount(data) {
  return Object.keys(data.kanji || {}).length;
}

export async function loadLevel(level, fetchFn = fetch) {
  const res = await fetchFn(`data/${level.toLowerCase()}.json`);
  if (!res.ok) throw new Error(`failed to load ${level}`);
  const data = await res.json();
  const v = validateLevelData(data);
  if (!v.ok) throw new Error(`invalid ${level} data: ${v.error}`);
  return data;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm test`
Expected: PASS (data-loader tests).

- [ ] **Step 5: Commit**

```bash
git add js/data-loader.js tests/js/data-loader.test.js
git commit -m "feat: JS level data loader and validator"
```

---

## Task 9: Hierarchy transform (pure) + D3 mind-map render

**Files:**
- Create: `js/hierarchy.js`
- Create: `js/mindmap.js`
- Test: `tests/js/hierarchy.test.js`

**Interfaces:**
- Produces (`hierarchy.js`): `toHierarchy(root)` converts a level `root` into `{name, char, label, children}` suitable for `d3.hierarchy`; the synthetic top node uses `root.root` as `char` and `root.label` as `name`. `countNodes(hierarchyRoot)` returns total node count including the root.
- Produces (`mindmap.js`): `renderMindmap(svgEl, root, { onSelect })` draws a horizontal tidy tree (`d3.tree`) for one root cluster; clicking a node calls `onSelect(char)`. Uses global `d3` (loaded via CDN in `index.html`).

- [ ] **Step 1: Write the failing test**

`tests/js/hierarchy.test.js`:
```javascript
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { toHierarchy, countNodes } from '../../js/hierarchy.js';

const root = { id: 'r', root: '口', label: 'Mouth',
  children: [{ char: '日', label: 'sun', children: [
    { char: '車', label: 'car', children: [] },
  ] }] };

test('toHierarchy makes synthetic root from component', () => {
  const h = toHierarchy(root);
  assert.equal(h.char, '口');
  assert.equal(h.name, 'Mouth');
  assert.equal(h.children[0].char, '日');
  assert.equal(h.children[0].children[0].char, '車');
});

test('countNodes counts root + descendants', () => {
  assert.equal(countNodes(toHierarchy(root)), 3); // 口, 日, 車
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm test`
Expected: FAIL — cannot find `../../js/hierarchy.js`.

- [ ] **Step 3: Write `js/hierarchy.js`**

```javascript
function convertNode(node) {
  return {
    char: node.char,
    name: node.label,
    label: node.label,
    children: (node.children || []).map(convertNode),
  };
}

export function toHierarchy(root) {
  return {
    char: root.root,
    name: root.label,
    label: root.label,
    children: (root.children || []).map(convertNode),
  };
}

export function countNodes(h) {
  let n = 1;
  for (const c of h.children || []) n += countNodes(c);
  return n;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm test`
Expected: PASS.

- [ ] **Step 5: Write `js/mindmap.js` (rendering; verified manually in Task 12)**

```javascript
import { toHierarchy } from './hierarchy.js';

const NODE_W = 170, NODE_H = 40;

export function renderMindmap(svgEl, rootData, { onSelect } = {}) {
  const d3 = window.d3;
  svgEl.innerHTML = '';
  const svg = d3.select(svgEl);

  const root = d3.hierarchy(toHierarchy(rootData));
  const depth = root.height + 1;
  const leaves = root.leaves().length;

  const width = depth * NODE_W + 80;
  const height = Math.max(leaves * NODE_H + 40, 120);
  svgEl.setAttribute('viewBox', `0 0 ${width} ${height}`);
  svgEl.setAttribute('width', width);
  svgEl.setAttribute('height', height);

  const layout = d3.tree().size([height - 40, width - NODE_W - 40]);
  layout(root);

  const g = svg.append('g').attr('transform', 'translate(20,20)');

  g.append('g').attr('class', 'links')
    .selectAll('path').data(root.links()).enter().append('path')
    .attr('class', 'link')
    .attr('d', d3.linkHorizontal().x(d => d.y).y(d => d.x));

  const node = g.append('g').attr('class', 'nodes')
    .selectAll('g').data(root.descendants()).enter().append('g')
    .attr('class', d => d.depth === 0 ? 'node node--root' : 'node')
    .attr('transform', d => `translate(${d.y},${d.x})`)
    .style('cursor', d => d.depth === 0 ? 'default' : 'pointer')
    .on('click', (_, d) => { if (d.depth > 0 && onSelect) onSelect(d.data.char); });

  node.append('text').attr('class', 'kanji').attr('dy', '0.32em').text(d => d.data.char);
  node.append('text').attr('class', 'gloss').attr('dx', 22).attr('dy', '0.32em')
    .text(d => d.data.label);
}
```

- [ ] **Step 6: Commit**

```bash
git add js/hierarchy.js js/mindmap.js tests/js/hierarchy.test.js
git commit -m "feat: hierarchy transform and D3 mind-map renderer"
```

---

## Task 10: Detail panel + app shell + styles

**Files:**
- Create: `js/detail.js`
- Create: `js/app.js`
- Create: `index.html`
- Create: `css/styles.css`
- Create: `assets/fonts/` (vendor `NotoSansJP-Regular.woff2`, `NotoSansJP-Bold.woff2`, `OFL.txt`)

**Interfaces:**
- Consumes: `loadLevel` (Task 8), `renderMindmap` (Task 9).
- Produces: `detail.js` `renderDetail(containerEl, kanjiInfo)` renders meanings, on/kun readings, and on/kun vocab lists. `app.js` wires level tabs (N5/N4), renders one mind-map section per root, and opens the detail panel on node click.

- [ ] **Step 1: Vendor the font**

Download Noto Sans JP (OFL) Regular + Bold as `.woff2` into `assets/fonts/`, plus the OFL license as `assets/fonts/OFL.txt`. (Convert from Google Fonts `ttf` with `fonttools` if needed; pin the files in-repo so the site is offline.)

- [ ] **Step 2: Write `index.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Kanji Mind-Map · JLPT N5 / N4</title>
  <link rel="stylesheet" href="css/styles.css" />
  <script src="https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"></script>
</head>
<body>
  <header>
    <h1>Kanji Mind-Map</h1>
    <nav id="levels">
      <button data-level="N5" class="active">N5</button>
      <button data-level="N4">N4</button>
    </nav>
  </header>
  <main>
    <section id="maps" aria-label="Kanji mind maps"></section>
  </main>
  <aside id="detail" hidden></aside>
  <footer>
    Data: KANJIDIC2 &amp; JMdict © EDRDG, CC BY-SA 4.0.
  </footer>
  <script type="module" src="js/app.js"></script>
</body>
</html>
```

- [ ] **Step 3: Write `js/detail.js`**

```javascript
function vocabList(items) {
  if (!items || !items.length) return '<p class="empty">—</p>';
  return '<ul>' + items.map(v =>
    `<li><span class="vw">${v.word}</span>` +
    `<span class="vr">${v.reading}</span>` +
    `<span class="vg">${v.gloss}</span></li>`).join('') + '</ul>';
}

export function renderDetail(el, info) {
  el.hidden = false;
  el.innerHTML = `
    <button class="close" aria-label="Close">×</button>
    <div class="big-kanji">${info.char}</div>
    <p class="meanings">${info.meanings.join(', ')}</p>
    <dl class="readings">
      <dt>On'yomi</dt><dd>${info.on.join('、') || '—'}</dd>
      <dt>Kun'yomi</dt><dd>${info.kun.join('、') || '—'}</dd>
      <dt>Strokes</dt><dd>${info.strokes}</dd>
    </dl>
    <h3>On'yomi vocabulary</h3>${vocabList(info.vocab.on)}
    <h3>Kun'yomi vocabulary</h3>${vocabList(info.vocab.kun)}
  `;
  el.querySelector('.close').onclick = () => { el.hidden = true; };
}
```

- [ ] **Step 4: Write `js/app.js`**

```javascript
import { loadLevel } from './data-loader.js';
import { renderMindmap } from './mindmap.js';
import { renderDetail } from './detail.js';

const mapsEl = document.getElementById('maps');
const detailEl = document.getElementById('detail');

async function showLevel(level) {
  const data = await loadLevel(level);
  mapsEl.innerHTML = '';
  for (const root of data.roots) {
    const section = document.createElement('section');
    section.className = 'cluster';
    const h2 = document.createElement('h2');
    h2.innerHTML = `<span class="root-kanji">${root.root}</span> ${root.label}`;
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    section.append(h2, svg);
    mapsEl.append(section);
    renderMindmap(svg, root, {
      onSelect: (char) => {
        const info = data.kanji[char];
        if (info) renderDetail(detailEl, info);
      },
    });
  }
}

document.getElementById('levels').addEventListener('click', (e) => {
  const btn = e.target.closest('button[data-level]');
  if (!btn) return;
  document.querySelectorAll('#levels button').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  showLevel(btn.dataset.level);
});

showLevel('N5');
```

- [ ] **Step 5: Write `css/styles.css`**

```css
@font-face {
  font-family: 'Noto Sans JP'; font-weight: 400; font-display: swap;
  src: url('../assets/fonts/NotoSansJP-Regular.woff2') format('woff2');
}
@font-face {
  font-family: 'Noto Sans JP'; font-weight: 700; font-display: swap;
  src: url('../assets/fonts/NotoSansJP-Bold.woff2') format('woff2');
}
:root { --ink:#1b2330; --line:#c9d2e0; --accent:#b3331f; --bg:#f7f8fb; }
* { box-sizing: border-box; }
body { margin:0; font-family:'Noto Sans JP',system-ui,sans-serif; color:var(--ink); background:var(--bg); }
header { display:flex; align-items:center; gap:1.5rem; padding:.8rem 1.2rem; border-bottom:2px solid var(--ink); }
header h1 { font-size:1.2rem; margin:0; }
#levels button { font:inherit; padding:.35rem .9rem; border:1px solid var(--ink); background:#fff; cursor:pointer; }
#levels button.active { background:var(--ink); color:#fff; }
main { padding:1rem 1.2rem; }
.cluster { border:1px solid var(--line); border-radius:8px; margin-bottom:1.2rem; padding:.6rem 1rem; background:#fff; }
.cluster h2 { font-size:1rem; margin:.2rem 0 .6rem; }
.root-kanji { font-size:1.5rem; color:var(--accent); }
svg .link { fill:none; stroke:var(--line); stroke-width:1.5; }
svg text.kanji { font-size:20px; fill:var(--accent); }
svg .node--root text.kanji { fill:var(--ink); }
svg text.gloss { font-size:11px; fill:#46506a; }
#detail { position:fixed; top:0; right:0; width:320px; height:100%; background:#fff; border-left:2px solid var(--ink); padding:1rem 1.2rem; overflow:auto; box-shadow:-4px 0 16px rgba(0,0,0,.08); }
#detail .close { float:right; font-size:1.4rem; border:none; background:none; cursor:pointer; }
.big-kanji { font-size:5rem; line-height:1; color:var(--accent); }
.meanings { font-weight:700; }
.readings dt { font-size:.75rem; text-transform:uppercase; color:#6b7689; margin-top:.5rem; }
.readings dd { margin:0; font-size:1.1rem; }
#detail h3 { font-size:.9rem; border-bottom:1px solid var(--line); padding-bottom:.2rem; margin-top:1rem; }
#detail ul { list-style:none; padding:0; margin:.3rem 0; }
#detail li { display:grid; grid-template-columns:auto auto 1fr; gap:.5rem; padding:.15rem 0; align-items:baseline; }
.vw { font-size:1.1rem; } .vr { color:#6b7689; font-size:.85rem; } .vg { font-size:.85rem; }
.empty { color:#9aa4b6; }
footer { padding:1rem 1.2rem; font-size:.75rem; color:#6b7689; border-top:1px solid var(--line); }
@media print { header nav, #detail, footer { display:none; } }
```

- [ ] **Step 6: Manual verification**

Run: `npm run serve`, open `http://localhost:8000`. Confirm: N5 map renders clusters; clicking a kanji opens the panel with readings + on/kun vocab; switching to N4 shows the transcribed clusters (e.g., 口→日→車). Kanji glyphs render in Noto Sans JP.

- [ ] **Step 7: Commit**

```bash
git add index.html js/detail.js js/app.js css/styles.css assets/fonts/
git commit -m "feat: detail panel, app shell, styles, bundled JP font"
```

---

## Task 11: Print view

**Files:**
- Create: `print.html`
- Create: `js/print.js`
- Modify: `css/styles.css` (add `@page` + print-layout rules)

**Interfaces:**
- Consumes: `loadLevel`, `renderMindmap`.
- Produces: `print.html?level=N4` renders all clusters stacked for paper, then a reference table of every kanji (char, on, kun, one on-vocab, one kun-vocab). Sets `window.__renderComplete = true` after rendering (PDF step waits on this).

- [ ] **Step 1: Write `print.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Kanji Mind-Map (print)</title>
  <link rel="stylesheet" href="css/styles.css" />
  <script src="https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"></script>
</head>
<body class="print">
  <h1 id="title">Kanji Mind-Map</h1>
  <section id="maps"></section>
  <h2>Reading reference</h2>
  <table id="ref"><thead><tr>
    <th>Kanji</th><th>On'yomi</th><th>Kun'yomi</th><th>On vocab</th><th>Kun vocab</th>
  </tr></thead><tbody></tbody></table>
  <script type="module" src="js/print.js"></script>
</body>
</html>
```

- [ ] **Step 2: Write `js/print.js`**

```javascript
import { loadLevel } from './data-loader.js';
import { renderMindmap } from './mindmap.js';

function param(name, fallback) {
  return new URLSearchParams(location.search).get(name) || fallback;
}

function vocab1(list) {
  if (!list || !list.length) return '—';
  const v = list[0];
  return `${v.word} (${v.reading}) ${v.gloss}`;
}

async function main() {
  const level = param('level', 'N5');
  const data = await loadLevel(level);
  document.getElementById('title').textContent = `Kanji Mind-Map · JLPT ${level}`;

  const maps = document.getElementById('maps');
  for (const root of data.roots) {
    const sec = document.createElement('section');
    sec.className = 'cluster';
    const h2 = document.createElement('h2');
    h2.innerHTML = `<span class="root-kanji">${root.root}</span> ${root.label}`;
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    sec.append(h2, svg);
    maps.append(sec);
    renderMindmap(svg, root, {});
  }

  const tbody = document.querySelector('#ref tbody');
  for (const ch of Object.keys(data.kanji).sort()) {
    const k = data.kanji[ch];
    const tr = document.createElement('tr');
    tr.innerHTML = `<td class="rk">${ch}</td><td>${k.on.join('、')}</td>` +
      `<td>${k.kun.join('、')}</td><td>${vocab1(k.vocab.on)}</td>` +
      `<td>${vocab1(k.vocab.kun)}</td>`;
    tbody.append(tr);
  }
  window.__renderComplete = true;
}
main();
```

- [ ] **Step 3: Append print rules to `css/styles.css`**

```css
@page { size: A4 portrait; margin: 14mm; }
body.print { background:#fff; }
body.print h1 { font-size:1.4rem; }
body.print .cluster { break-inside: avoid; page-break-inside: avoid; }
#ref { width:100%; border-collapse:collapse; font-size:.8rem; }
#ref th, #ref td { border:1px solid var(--line); padding:.25rem .4rem; text-align:left; }
#ref .rk { font-size:1.2rem; color:var(--accent); }
#ref { page-break-before: always; }
```

- [ ] **Step 4: Manual verification**

Run: serve, open `http://localhost:8000/print.html?level=N5`. Confirm clusters stack vertically, the reference table fills, and the browser Print preview paginates cleanly (clusters not split).

- [ ] **Step 5: Commit**

```bash
git add print.html js/print.js css/styles.css
git commit -m "feat: print view with mind-maps and reading reference table"
```

---

## Task 12: PDF generator (Playwright)

**Files:**
- Create: `pdf/generate_pdf.py`
- Test: `tests/python/test_generate_pdf.py`

**Interfaces:**
- Produces: `generate_pdf.render(level, port) -> Path` prints `print.html?level=<level>` to `pdf/kanji-<level>.pdf` using a Chromium page that waits for `window.__renderComplete`. `generate_pdf.main()` starts a local static server, renders N5 and N4, stops the server.

- [ ] **Step 1: Write the failing test**

`tests/python/test_generate_pdf.py`:
```python
import importlib.util
import pytest

playwright_missing = importlib.util.find_spec("playwright") is None

@pytest.mark.skipif(playwright_missing, reason="playwright not installed")
def test_pdf_path_naming():
    from pdf import generate_pdf
    assert generate_pdf.pdf_path("N4").name == "kanji-N4.pdf"
    assert generate_pdf.pdf_path("N5").parent.name == "pdf"
```

> Add `pdf/__init__.py` (empty) so `from pdf import generate_pdf` works.

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/python/test_generate_pdf.py -v`
Expected: FAIL — `ModuleNotFoundError: pdf.generate_pdf`.

- [ ] **Step 3: Write `pdf/generate_pdf.py`**

```python
import functools
import http.server
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PDF_DIR = ROOT / "pdf"


def pdf_path(level: str) -> Path:
    return PDF_DIR / f"kanji-{level}.pdf"


def _start_server(port: int) -> http.server.ThreadingHTTPServer:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def render(level: str, port: int) -> Path:
    from playwright.sync_api import sync_playwright

    PDF_DIR.mkdir(parents=True, exist_ok=True)
    out = pdf_path(level)
    url = f"http://127.0.0.1:{port}/print.html?level={level}"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_function("window.__renderComplete === true", timeout=30000)
        page.pdf(path=str(out), format="A4", print_background=True,
                 margin={"top": "14mm", "bottom": "14mm", "left": "14mm", "right": "14mm"})
        browser.close()
    print(f"Wrote {out}")
    return out


def main() -> None:
    port = 8123
    httpd = _start_server(port)
    try:
        for level in ("N5", "N4"):
            render(level, port)
    finally:
        httpd.shutdown()


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/python/test_generate_pdf.py -v`
Expected: PASS (or SKIP if playwright not yet installed).

- [ ] **Step 5: Generate PDFs (manual)**

Run: `.venv/Scripts/python -m playwright install chromium` then `.venv/Scripts/python pdf/generate_pdf.py`.
Expected: `pdf/kanji-N5.pdf` and `pdf/kanji-N4.pdf` exist; open them and confirm Japanese glyphs render and clusters are not split across pages.

- [ ] **Step 6: Commit**

```bash
git add pdf/__init__.py pdf/generate_pdf.py tests/python/test_generate_pdf.py
git commit -m "feat: Playwright PDF generation per JLPT level"
```

---

## Task 13: GitHub Actions — Pages deploy + PDF artifact

**Files:**
- Create: `.github/workflows/pages.yml`
- Create: `.github/workflows/pdf.yml`

**Interfaces:**
- Produces: pushing to `main` deploys the static site to GitHub Pages and builds both PDFs as a downloadable artifact. Committed `data/*.json` is served directly (no data rebuild in CI — the datasets are large; rebuild is a local/manual step).

- [ ] **Step 1: Write `.github/workflows/pages.yml`**

```yaml
name: Deploy site to Pages
on:
  push:
    branches: [main]
  workflow_dispatch:
permissions:
  contents: read
  pages: write
  id-token: write
concurrency:
  group: pages
  cancel-in-progress: true
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deploy.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v3
        with:
          path: .
      - id: deploy
        uses: actions/deploy-pages@v4
```

> The repo root is the site root, so `index.html`, `js/`, `css/`, `data/`, `assets/` deploy as-is. `.nojekyll` ensures `assets/`/underscored paths are served. `raw/`, `tests/`, `scripts/` are harmless extra files but can be excluded later with a copy-to-`_site` step if desired.

- [ ] **Step 2: Write `.github/workflows/pdf.yml`**

```yaml
name: Build level PDFs
on:
  workflow_dispatch:
  push:
    branches: [main]
    paths: ['data/**', 'print.html', 'js/**', 'css/**', 'pdf/**']
jobs:
  pdf:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install 'playwright>=1.49'
      - run: python -m playwright install --with-deps chromium
      - run: python pdf/generate_pdf.py
      - uses: actions/upload-artifact@v4
        with:
          name: kanji-pdfs
          path: pdf/*.pdf
```

- [ ] **Step 3: Verify workflow YAML is valid**

Run: `npx --yes js-yaml .github/workflows/pages.yml` and `npx --yes js-yaml .github/workflows/pdf.yml`
Expected: both print parsed YAML with no error.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/pages.yml .github/workflows/pdf.yml
git commit -m "ci: GitHub Pages deploy and PDF artifact workflows"
```

- [ ] **Step 5: Enable Pages + push (manual)**

Push to `main`; in repo Settings → Pages, set Source = "GitHub Actions". Confirm the deployed URL loads the app and the PDF workflow produces `kanji-pdfs`.

---

## Task 14: README finalization + full-suite gate

**Files:**
- Modify: `README.md`
- Test: run everything

**Interfaces:**
- Produces: complete docs (data rebuild steps, deploy notes, attribution, screenshot) and a green full test run.

- [ ] **Step 1: Expand `README.md`**

Add: project description + screenshot, the hybrid tree-data design (N4 transcribed / N5 auto-grouped), exact local-dev commands, "how to add N3–N1 later" (drop a `trees_n3.py` or rely on auto-grouping; add the level to `build_data.main()` and the `#levels` nav), the GitHub Pages URL, and the EDRDG CC BY-SA 4.0 + Noto OFL attributions.

- [ ] **Step 2: Run the complete suites**

Run: `pytest -v`
Expected: all PASS.
Run: `npm test`
Expected: all PASS.

- [ ] **Step 3: Final manual smoke**

Serve, verify N5 + N4 render, detail panel shows on/kun readings and vocab, both PDFs open with correct glyphs.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: finalize README with usage, design, and attribution"
```

---

## Self-Review

**Spec coverage:**
- "Mind-map app for learning kanji by JLPT level" → Tasks 5–10 (trees + D3 render + level tabs). ✓
- "Web app" → Tasks 8–10, deployed via Task 13. ✓
- "Printable PDF by JLPT level" → Tasks 11–12, CI artifact in Task 13. ✓
- "On'yomi and kun'yomi readings" → Task 3 (parse), Task 7 (embed), Task 10 (display), Task 11 (PDF table). ✓
- "Sample vocabulary for on'yomi and kun'yomi per kanji" → Task 4 (select), Task 7 (embed), Task 10/11 (display). ✓
- "Publish via GitHub" → static site + Task 13 Pages workflow. ✓
- "Scan all images / build something similar" → Task 5 transcribes the N4 images; N5 auto-grouped (Task 6) to match the style. ✓
- N5 + N4 scope → `build_data.main()` builds both; nav has both tabs. ✓
- Bundled offline dataset → Tasks 2–4 (KANJIDIC2 + JMdict, no runtime network). ✓

**Placeholder scan:** The only intentionally open-ended item is the N4 transcription body in Task 5 Step 3 (seed + explicit "extend to all clusters" rule) and the 214-entry KANGXI map / pinned SHA — these are data-entry items that must be completed at execution against the real source images/repo, not code placeholders. All code steps contain runnable code.

**Type consistency:** `validateLevelData`, `loadLevel`, `kanjiCount` (Task 8) consistent with usage in `app.js`/`print.js`. `toHierarchy`/`countNodes` (Task 9) match `mindmap.js`. `build_level` signature in Task 7 matches its test. `vocab.select(...)` and `parse(...)`/`build_index(...)` signatures consistent across Tasks 3, 4, 7. Level dict shape matches `data/schema.json` everywhere. ✓

---

## Execution Handoff
