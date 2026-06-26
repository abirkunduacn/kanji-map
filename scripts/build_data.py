import json
from datetime import date
from pathlib import Path

import jsonschema

from scripts import parse_kanjidic, parse_jmdict, trees_ids
from scripts.sources import KANJIDIC2_PATH, JMDICT_PATH, JLPT_PATH, IDS_PATH

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SCHEMA = json.loads((DATA_DIR / "schema.json").read_text(encoding="utf-8"))


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


def build_level(level, kanji_chars, kanji_infos, vocab_index, roots) -> dict:
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
    vocab_index = parse_jmdict.build_index(JMDICT_PATH, wanted=all_wanted)
    ids = trees_ids.parse_ids(IDS_PATH)

    n5_chars = levels["N5"]
    n4_chars = levels["N4"]

    # N5: build-from forest over N5 kanji only (parents restricted to N5).
    n5_roots = trees_ids.build_forest(ids, kanji_infos, scope=n5_chars)
    n5 = build_level("N5", n5_chars, kanji_infos, vocab_index, n5_roots)

    # N4: forest over N5 ∪ N4 so N5 building blocks connect the N4 kanji into
    # deep chains; only trees that include at least one N4 kanji are kept.
    n4_roots = trees_ids.build_forest(
        ids, kanji_infos, scope=n5_chars | n4_chars, required=n4_chars
    )
    n4 = build_level("N4", n4_chars, kanji_infos, vocab_index, n4_roots)

    (DATA_DIR / "n4.json").write_text(json.dumps(n4, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA_DIR / "n5.json").write_text(json.dumps(n5, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote N4 ({len(n4['kanji'])} kanji) and N5 ({len(n5['kanji'])} kanji)")


if __name__ == "__main__":
    main()
