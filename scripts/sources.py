from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "raw"

KANJIDIC2_PATH = RAW_DIR / "kanjidic2.xml"
JMDICT_PATH = RAW_DIR / "JMdict_e.xml"
JLPT_PATH = RAW_DIR / "kanji-data.json"

# Pinned commit for reproducibility. Update the SHA deliberately, never to a branch.
_KANJI_DATA_SHA = "7ada8ddbfe7359286f4db4e766d1242b9e6f7969"

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
