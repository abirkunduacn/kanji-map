from pathlib import Path
from lxml import etree

_PRI_TAGS = {"news1", "ichi1", "spec1", "spec2", "gai1"}

# Katakana block U+30A1–U+30F6 maps to hiragana by subtracting 0x60.
def kata_to_hira(s: str) -> str:
    out = []
    for ch in s:
        code = ord(ch)
        if 0x30A1 <= code <= 0x30F6:
            out.append(chr(code - 0x60))
        else:
            out.append(ch)
    return "".join(out)


def _on_keys(on: list[str]) -> list[str]:
    # セイ -> せい ; drop length marker handling kept simple
    return [kata_to_hira(r).replace("ー", "") for r in on if r]


def _kun_keys(kun: list[str]) -> list[str]:
    # Full kun reading with the okurigana separator removed, used as a
    # START-OF-READING key: い.きる -> いきる ; う.まれる -> うまれる ; みず -> みず.
    # Matching the full reading at the start (not a bare-stem substring) keeps a
    # short stem from spuriously matching inside an unrelated on-reading word.
    keys = []
    for r in kun:
        if not r:
            continue
        full = r.replace(".", "").replace("-", "")
        if full:
            keys.append(full)
    return keys


class VocabIndex:
    def __init__(self, by_char: dict[str, list[dict]]):
        self._by_char = by_char

    def select(self, char: str, on: list[str], kun: list[str], limit: int = 2) -> dict:
        entries = self._by_char.get(char, [])
        on_keys = _on_keys(on)
        kun_keys = _kun_keys(kun)

        def contains(reading: str, keys: list[str]) -> bool:
            return any(k and k in reading for k in keys)

        def prefix(reading: str, keys: list[str]) -> bool:
            return any(k and reading.startswith(k) for k in keys)

        def rank(e: dict):
            return (0 if e["pri"] else 1, len(e["word"]))

        # on: reading may carry the syllable anywhere (学生 がくせい). kun: anchor at
        # the start so a short stem can't match inside an on-reading word.
        on_hits = sorted((e for e in entries if contains(e["reading"], on_keys)), key=rank)
        kun_hits = sorted((e for e in entries if prefix(e["reading"], kun_keys)), key=rank)

        def fmt(e):
            return {"word": e["word"], "reading": e["reading"], "gloss": e["gloss"]}

        return {
            "on": [fmt(e) for e in on_hits[:limit]],
            "kun": [fmt(e) for e in kun_hits[:limit]],
        }


def build_index(path: Path, wanted: set[str]) -> VocabIndex:
    by_char: dict[str, list[dict]] = {c: [] for c in wanted}
    context = etree.iterparse(str(path), tag="entry", resolve_entities=False)
    for _, entry in context:
        kebs = entry.findall("k_ele")
        reb = entry.findtext("r_ele/reb")
        gloss = entry.findtext("sense/gloss")
        if reb and gloss:
            for k in kebs:
                keb = k.findtext("keb")
                if not keb:
                    continue
                pri = any(p.text in _PRI_TAGS for p in k.findall("ke_pri"))
                record = {"word": keb, "reading": reb, "gloss": gloss, "pri": pri}
                for ch in set(keb) & wanted:
                    by_char[ch].append(record)
        entry.clear()
        while entry.getprevious() is not None:
            del entry.getparent()[0]
    return VocabIndex(by_char)
