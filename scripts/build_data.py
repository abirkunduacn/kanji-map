import json
from datetime import date
from pathlib import Path

import jsonschema

from scripts import parse_kanjidic, parse_jmdict, trees_ids
from scripts.sources import KANJIDIC2_PATH, JMDICT_PATH, JLPT_PATH, IDS_PATH
from scripts.words import build_words

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SCHEMA = json.loads((DATA_DIR / "schema.json").read_text(encoding="utf-8"))

LEVEL_ORDER = ["N5", "N4", "N3", "N2"]


def _placed_in(roots: list[dict]) -> set[str]:
    """Every kanji that appears in the trees: each root's own char (when it is a
    real kanji, not the OTHER_ROOT marker) plus every node char in its subtree."""
    out = set()

    def walk(nodes):
        for node in nodes:
            out.add(node["char"])
            walk(node["children"])

    for r in roots:
        if r["root"] != trees_ids.OTHER_ROOT:
            out.add(r["root"])
        walk(r["children"])
    return out


def build_level(level, kanji_chars, kanji_infos, vocab_index, roots, words) -> dict:
    placed = _placed_in(roots)
    kanji = {}
    for ch in sorted(placed):
        info = kanji_infos.get(ch)
        if info is None:
            # A placed char with no readings (e.g. a connector outside our data);
            # skip its detail entry. Real roots/nodes are always in kanji_infos.
            continue
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
        "words": words,
    }
    jsonschema.validate(level_dict, SCHEMA)
    return level_dict


def _jlpt_chars() -> dict[str, set[str]]:
    raw = json.loads(JLPT_PATH.read_text(encoding="utf-8"))
    levels = {lv: set() for lv in LEVEL_ORDER}
    by_num = {5: "N5", 4: "N4", 3: "N3", 2: "N2"}
    for char, meta in raw.items():
        lv = by_num.get(meta.get("jlpt_new"))
        if lv:
            levels[lv].add(char)
    return levels


def main() -> None:
    levels = _jlpt_chars()
    all_wanted = set().union(*levels.values())
    kanji_infos = parse_kanjidic.parse(KANJIDIC2_PATH, wanted=all_wanted)
    vocab_index = parse_jmdict.build_index(JMDICT_PATH, wanted=all_wanted)
    ids = trees_ids.parse_ids(IDS_PATH)

    cumulative: set[str] = set()
    for lv in LEVEL_ORDER:
        cumulative = cumulative | levels[lv]
        roots = trees_ids.build_forest(
            ids, kanji_infos, scope=cumulative, required=levels[lv]
        )
        words = build_words(JMDICT_PATH, known=cumulative, limit=250)
        level_dict = build_level(lv, levels[lv], kanji_infos, vocab_index, roots, words)
        (DATA_DIR / f"{lv.lower()}.json").write_text(
            json.dumps(level_dict, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"Wrote {lv}: {len(level_dict['kanji'])} kanji, "
              f"{len(level_dict['roots'])} clusters, {len(level_dict['words'])} words")


if __name__ == "__main__":
    main()
