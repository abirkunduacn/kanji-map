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
