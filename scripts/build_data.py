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


def _prune_to_scope(roots: list[dict], scope: set[str]) -> list[dict]:
    """Drop tree nodes whose kanji is outside `scope` (the kanji we have readings
    for = N5 ∪ N4), along with their subtrees. In-scope descendants of a dropped
    node are NOT lost overall: because they no longer appear in the pruned tree,
    main() puts them in the auto-grouped remainder instead. Roots left with no
    children are dropped entirely. This guarantees every node that survives has a
    detail entry, so schema/JS validation (every placed kanji has a kanji entry)
    holds."""
    def prune_nodes(nodes):
        kept = []
        for node in nodes:
            if node["char"] in scope:
                kept.append({
                    "char": node["char"],
                    "label": node["label"],
                    "children": prune_nodes(node["children"]),
                })
        return kept
    out = []
    for r in roots:
        children = prune_nodes(r["children"])
        if children:
            out.append({"id": r["id"], "root": r["root"], "label": r["label"], "children": children})
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

    # N4: curated trees (pruned to in-scope kanji) + auto-group the remainder.
    # The transcribed trees may contain building-block kanji outside N5∪N4
    # (e.g. rare components); pruning drops those so every surviving node has a
    # detail entry. Any N4 kanji not present in the pruned trees is auto-grouped.
    scope = set(kanji_infos)  # every kanji we parsed readings for (N5 ∪ N4)
    n4_chars = levels["N4"]
    pruned_roots = _prune_to_scope(trees_n4.ROOTS, scope)
    n4_in_trees = _placed_in(pruned_roots) & n4_chars
    n4_remainder = {c: kanji_infos[c] for c in n4_chars - n4_in_trees}
    n4_roots = pruned_roots + trees_auto.build(n4_remainder, radicals)
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
