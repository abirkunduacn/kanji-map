from pathlib import Path
from scripts import parse_jmdict

FIX = Path(__file__).parent / "fixtures" / "jmdict_min.xml"

def test_selects_on_and_kun_examples():
    idx = parse_jmdict.build_index(FIX, wanted={"生"})
    picks = idx.select("生", on=["セイ", "ショウ"], kun=["い.きる", "う.まれる"], limit=2)
    on_words = {v["word"] for v in picks["on"]}
    kun_words = {v["word"] for v in picks["kun"]}
    assert "生活" in on_words          # reading せいかつ contains せい
    assert "生きる" in kun_words        # reading いきる contains stem い... matches kun い.きる
    # gloss carried through
    assert picks["on"][0]["gloss"] == "life"

def test_katakana_on_reading_is_matched_as_hiragana():
    idx = parse_jmdict.build_index(FIX, wanted={"生"})
    picks = idx.select("生", on=["セイ"], kun=[], limit=2)
    assert any(v["reading"] == "せいかつ" for v in picks["on"])
