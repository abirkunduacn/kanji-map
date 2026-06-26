from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "raw"

KANJIDIC2_PATH = RAW_DIR / "kanjidic2.xml"
JMDICT_PATH = RAW_DIR / "JMdict_e.xml"
JLPT_PATH = RAW_DIR / "kanji-data.json"
IDS_PATH = RAW_DIR / "ids.txt"

# Pinned commits for reproducibility. Update SHAs deliberately, never to a branch.
_KANJI_DATA_SHA = "7ada8ddbfe7359286f4db4e766d1242b9e6f7969"
# cjkvi-ids Ideographic Description Sequences (structural kanji decomposition).
# Source data is GPLv2 (CHISE-derived); it is downloaded at BUILD time only and
# never redistributed. We extract factual "kanji-X-is-built-from-kanji-Y"
# relationships into data/*.json (facts, not the source text). Attributed in README.
_CJKVI_IDS_SHA = "86b4d16159f0079437870408f0ca186e529015db"

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
    {
        "name": "ids",
        "url": f"https://raw.githubusercontent.com/cjkvi/cjkvi-ids/{_CJKVI_IDS_SHA}/ids.txt",
        "dest": IDS_PATH,
        "gzip": False,
    },
]
