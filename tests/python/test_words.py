from pathlib import Path
from scripts import words

FIX = Path(__file__).parent / "fixtures" / "jmdict_min.xml"

def test_selects_only_all_known_multi_kanji_words():
    # jmdict_min.xml has 生活(生,活? no 活), 一生(一,生), 衛生(衛,生), 生きる(1 kanji), 犬(1)
    out = words.build_words(FIX, known={"一", "生", "衛"}, limit=50)
    found = {w["word"] for w in out}
    assert "一生" in found            # 一,生 both known, 2 kanji
    assert "衛生" in found            # 衛,生 both known
    assert "生きる" not in found       # only 1 kanji
    assert "犬" not in found           # only 1 kanji

def test_excludes_word_with_unknown_kanji():
    out = words.build_words(FIX, known={"一", "生"}, limit=50)   # 衛 NOT known
    assert "衛生" not in {w["word"] for w in out}
    assert "一生" in {w["word"] for w in out}

def test_kanji_field_lists_distinct_kanji_in_order():
    out = words.build_words(FIX, known={"一", "生", "衛"}, limit=50)
    isshou = next(w for w in out if w["word"] == "一生")
    assert isshou["kanji"] == ["一", "生"]
    assert isshou["reading"] and isshou["gloss"]
