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

def test_prune_to_scope_drops_out_of_scope_nodes():
    roots = [{"id": "r", "root": "x", "label": "X", "children": [
        {"char": "生", "label": "life", "children": [
            {"char": "雉", "label": "pheasant", "children": []},  # out of scope
        ]},
        {"char": "雉", "label": "pheasant", "children": []},
    ]}]
    pruned = build_data._prune_to_scope(roots, scope={"生"})
    assert build_data._placed_in(pruned) == {"生"}  # 雉 removed, 生 kept
