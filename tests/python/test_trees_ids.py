from pathlib import Path
from scripts import trees_ids


def _write_ids(tmp_path, lines):
    p = tmp_path / "ids.txt"
    p.write_text("\n".join(lines), encoding="utf-8")
    return p


def test_parse_ids_extracts_components_dropping_idc_operators(tmp_path):
    p = _write_ids(tmp_path, [
        "# comment line",
        "U+5B8C\t完\t⿱宀元",
        "U+9662\t院\t⿰阝完",
    ])
    direct = trees_ids.parse_ids(p)
    assert direct["完"] == ["宀", "元"]   # ⿱ operator dropped
    assert direct["院"] == ["阝", "完"]


def test_build_forest_makes_built_from_chain(tmp_path):
    # 一 ⊂ 元 ⊂ 完 ⊂ 院  -> chain 一 -> 元 -> 完 -> 院
    p = _write_ids(tmp_path, [
        "U+5143\t元\t⿱一兀",
        "U+5B8C\t完\t⿱宀元",
        "U+9662\t院\t⿰阝完",
    ])
    direct = trees_ids.parse_ids(p)
    infos = {c: {"char": c, "meanings": [c], "strokes": s}
             for c, s in {"一": 1, "元": 4, "完": 7, "院": 10}.items()}
    roots = trees_ids.build_forest(direct, infos, scope={"一", "元", "完", "院"})
    # one real-kanji root (一) with a single deepening chain
    real = [r for r in roots if r["root"] != trees_ids.OTHER_ROOT]
    assert len(real) == 1
    r = real[0]
    assert r["root"] == "一"
    el = r["children"][0]          # 元
    assert el["char"] == "元"
    assert el["children"][0]["char"] == "完"
    assert el["children"][0]["children"][0]["char"] == "院"


def test_childless_roots_collected_into_other_cluster(tmp_path):
    # 木 and 山 share no components -> both childless roots -> one "Other" cluster
    p = _write_ids(tmp_path, [
        "U+6728\t木\t木",
        "U+5C71\t山\t山",
    ])
    direct = trees_ids.parse_ids(p)
    infos = {c: {"char": c, "meanings": [c], "strokes": 3} for c in ("木", "山")}
    roots = trees_ids.build_forest(direct, infos, scope={"木", "山"})
    assert len(roots) == 1
    assert roots[0]["root"] == trees_ids.OTHER_ROOT
    chars = {n["char"] for n in roots[0]["children"]}
    assert chars == {"木", "山"}


def test_required_filter_keeps_only_trees_touching_required(tmp_path):
    # scope has an N5-only tree (一->元) and an N4 tree (子->字). required=N4.
    p = _write_ids(tmp_path, [
        "U+5143\t元\t⿱一兀",
        "U+5B57\t字\t⿱宀子",
    ])
    direct = trees_ids.parse_ids(p)
    infos = {c: {"char": c, "meanings": [c], "strokes": s}
             for c, s in {"一": 1, "元": 4, "子": 3, "字": 6}.items()}
    roots = trees_ids.build_forest(
        direct, infos, scope={"一", "元", "子", "字"}, required={"字"}
    )
    placed = set()
    for r in roots:
        if r["root"] != trees_ids.OTHER_ROOT:
            placed.add(r["root"])
        for n in r["children"]:
            placed.add(n["char"])
    assert "字" in placed and "子" in placed   # the 字 tree is kept (子 -> 字)
    assert "元" not in placed                   # the pure-N5 一->元 tree is dropped
