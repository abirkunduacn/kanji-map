from pathlib import Path
from scripts import parse_kanjidic

FIX = Path(__file__).parent / "fixtures" / "kanjidic2_min.xml"

def test_parses_readings_meanings_strokes():
    out = parse_kanjidic.parse(FIX, wanted={"生"})
    assert set(out) == {"生"}
    k = out["生"]
    assert k["on"] == ["セイ", "ショウ"]
    assert k["kun"] == ["い.きる", "う.まれる"]
    assert k["meanings"] == ["life", "genuine"]   # French meaning excluded
    assert k["strokes"] == 5
    assert k["radical"] == 100

def test_filters_to_wanted_only():
    out = parse_kanjidic.parse(FIX, wanted={"一"})
    assert set(out) == {"一"}
