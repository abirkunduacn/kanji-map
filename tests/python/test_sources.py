from scripts import sources

def test_source_paths_are_under_raw():
    for p in (sources.KANJIDIC2_PATH, sources.JMDICT_PATH, sources.JLPT_PATH):
        assert sources.RAW_DIR in p.parents

def test_sources_list_is_pinned():
    assert len(sources.SOURCES) == 3
    # JLPT source must be pinned to an exact commit SHA, not a branch
    jlpt = next(s for s in sources.SOURCES if s["name"] == "jlpt")
    assert "/master/" not in jlpt["url"] and "/main/" not in jlpt["url"]
