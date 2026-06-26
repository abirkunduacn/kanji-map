from scripts import sources

def test_source_paths_are_under_raw():
    for p in (sources.KANJIDIC2_PATH, sources.JMDICT_PATH, sources.JLPT_PATH, sources.IDS_PATH):
        assert sources.RAW_DIR in p.parents

def test_sources_list_is_pinned():
    assert len(sources.SOURCES) == 4
    # GitHub-hosted sources must be pinned to an exact commit SHA, not a branch
    for name in ("jlpt", "ids"):
        src = next(s for s in sources.SOURCES if s["name"] == name)
        assert "/master/" not in src["url"] and "/main/" not in src["url"]
