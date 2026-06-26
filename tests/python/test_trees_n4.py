from scripts import trees_n4

def test_roots_have_required_shape():
    assert trees_n4.ROOTS, "expected at least one root"
    for r in trees_n4.ROOTS:
        assert set(r) >= {"id", "root", "label", "children"}
        assert isinstance(r["children"], list)

def test_placed_kanji_are_single_chars():
    placed = trees_n4.placed_kanji()
    assert placed, "expected placed kanji"
    assert all(len(c) == 1 for c in placed)

def test_known_clusters_present():
    placed = trees_n4.placed_kanji()
    # Spot-check clusters visible in the source screenshots.
    for c in ["生", "売", "声", "会", "海", "妹", "運", "暗"]:
        assert c in placed, f"{c} should be transcribed from the N4 images"
