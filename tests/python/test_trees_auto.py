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

def test_kangxi_char_maps_number_to_radical_glyph():
    assert ord(trees_auto.kangxi_char(1)) == 0x2F00      # radical 1 (⼀)
    assert ord(trees_auto.kangxi_char(214)) == 0x2FD5    # radical 214
    assert trees_auto.kangxi_char(0) == "他"             # out-of-range fallback
    assert trees_auto.kangxi_char(999) == "他"
