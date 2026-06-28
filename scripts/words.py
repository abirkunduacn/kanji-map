from pathlib import Path
from lxml import etree

from scripts.parse_jmdict import _PRI_TAGS


def _kanji_chars(s: str) -> list[str]:
    """Distinct CJK ideographs in s, in first-seen order."""
    out = []
    for c in s:
        if "一" <= c <= "鿿" and c not in out:
            out.append(c)
    return out


def build_words(path: Path, known: set[str], limit: int = 250) -> list[dict]:
    known = set(known)
    rows = []
    context = etree.iterparse(str(path), tag="entry", resolve_entities=False)
    for _, entry in context:
        reb = entry.findtext("r_ele/reb")
        gloss = entry.findtext("sense/gloss")
        if reb and gloss:
            for k in entry.findall("k_ele"):
                keb = k.findtext("keb")
                if not keb:
                    continue
                kanji = _kanji_chars(keb)
                if len(kanji) >= 2 and all(c in known for c in kanji):
                    pri = any(p.text in _PRI_TAGS for p in k.findall("ke_pri"))
                    rows.append({
                        "word": keb, "reading": reb, "gloss": gloss,
                        "kanji": kanji, "pri": pri,
                    })
        entry.clear()
        while entry.getprevious() is not None:
            del entry.getparent()[0]
    rows.sort(key=lambda e: (0 if e["pri"] else 1, len(e["word"]), e["word"]))
    return [
        {"word": e["word"], "reading": e["reading"], "gloss": e["gloss"], "kanji": e["kanji"]}
        for e in rows[:limit]
    ]
