import json
from pathlib import Path
import jsonschema
from scripts import build_data, parse_jmdict, trees_ids

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
    level = build_data.build_level("N5", {"生", "犬"}, infos, idx, roots, words=[])
    jsonschema.validate(level, SCHEMA)         # raises on any schema violation
    # every kanji placed in a node has a detail entry (口 has no readings -> skipped)
    assert set(level["kanji"]) == {"生", "犬"}
    assert level["kanji"]["生"]["vocab"]["on"]   # 生活 picked up
    assert level["level"] == "N5"

def test_build_level_includes_real_root_kanji_in_detail_map():
    # A root that is itself a real kanji (元) must get a detail entry so it is
    # clickable as the top of its chain — not only its descendant 院.
    infos = {
        "元": {"char": "元", "meanings": ["origin"], "on": ["ゲン"], "kun": ["もと"], "strokes": 4},
        "院": {"char": "院", "meanings": ["institution"], "on": ["イン"], "kun": [], "strokes": 10},
    }
    idx = parse_jmdict.build_index(JMFIX, wanted=set())
    roots = [{"id": "k-元", "root": "元", "label": "origin",
              "children": [{"char": "院", "label": "institution", "children": []}]}]
    level = build_data.build_level("N4", {"元", "院"}, infos, idx, roots, words=[])
    assert "元" in level["kanji"]   # the root kanji has its own entry
    assert "院" in level["kanji"]

def test_other_root_marker_gets_no_detail_entry():
    # The OTHER_ROOT marker (他) is not a JLPT kanji and must not get an entry.
    infos = {"犬": {"char": "犬", "meanings": ["dog"], "on": [], "kun": ["いぬ"], "strokes": 4}}
    idx = parse_jmdict.build_index(JMFIX, wanted=set())
    roots = [{"id": "other", "root": trees_ids.OTHER_ROOT, "label": "Other (standalone)",
              "children": [{"char": "犬", "label": "dog", "children": []}]}]
    level = build_data.build_level("N5", {"犬"}, infos, idx, roots, words=[])
    assert set(level["kanji"]) == {"犬"}   # 他 marker excluded

def test_jlpt_chars_has_four_levels(monkeypatch, tmp_path):
    import json as _json
    fake = {
        "一": {"jlpt_new": 5}, "二": {"jlpt_new": 4},
        "三": {"jlpt_new": 3}, "四": {"jlpt_new": 2}, "あ": {"jlpt_new": None},
    }
    p = tmp_path / "kanji.json"
    p.write_text(_json.dumps(fake), encoding="utf-8")
    monkeypatch.setattr(build_data, "JLPT_PATH", p)
    levels = build_data._jlpt_chars()
    assert set(levels) == {"N5", "N4", "N3", "N2"}
    assert levels["N3"] == {"三"} and levels["N2"] == {"四"}
    assert build_data.LEVEL_ORDER == ["N5", "N4", "N3", "N2"]

def test_build_level_includes_words_array():
    infos = {"生": {"char": "生", "meanings": ["life"], "on": [], "kun": [], "strokes": 5}}
    idx = parse_jmdict.build_index(JMFIX, wanted=set())
    roots = [{"id": "k-生", "root": "生", "label": "life", "children": []}]
    w = [{"word": "学生", "reading": "がくせい", "gloss": "student", "kanji": ["学", "生"]}]
    level = build_data.build_level("N5", {"生"}, infos, idx, roots, words=w)
    assert level["words"] == w
