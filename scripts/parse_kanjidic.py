from pathlib import Path
from lxml import etree


def parse(path: Path, wanted: set[str]) -> dict[str, dict]:
    result: dict[str, dict] = {}
    context = etree.iterparse(str(path), tag="character")
    for _, char_el in context:
        literal = char_el.findtext("literal")
        if literal in wanted:
            result[literal] = _extract(char_el, literal)
        char_el.clear()
        while char_el.getprevious() is not None:
            del char_el.getparent()[0]
    return result


def _extract(char_el, literal: str) -> dict:
    strokes = int(char_el.findtext("misc/stroke_count") or 0)
    on, kun, meanings = [], [], []
    rmgroup = char_el.find("reading_meaning/rmgroup")
    if rmgroup is not None:
        for r in rmgroup.findall("reading"):
            t = r.get("r_type")
            if t == "ja_on":
                on.append(r.text)
            elif t == "ja_kun":
                kun.append(r.text)
        for m in rmgroup.findall("meaning"):
            if m.get("m_lang") is None:  # English only
                meanings.append(m.text)
    return {
        "char": literal,
        "meanings": meanings,
        "on": on,
        "kun": kun,
        "strokes": strokes,
    }
