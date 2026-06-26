from collections import defaultdict


def build(kanji_infos: dict[str, dict], radicals: dict[str, str]) -> list[dict]:
    groups: dict[str, list[str]] = defaultdict(list)
    for char in kanji_infos:
        rad = radicals.get(char, "?")
        groups[rad].append(char)

    roots = []
    misc_children = []
    for rad, chars in sorted(groups.items()):
        children = [_node(c, kanji_infos[c]) for c in sorted(chars)]
        if len(children) == 1:
            misc_children.extend(children)
        else:
            roots.append({
                "id": f"auto-{rad}",
                "root": rad,
                "label": rad,
                "children": children,
            })
    if misc_children:
        roots.append({
            "id": "auto-misc",
            "root": "他",
            "label": "Other",
            "children": sorted(misc_children, key=lambda n: n["char"]),
        })
    return roots


def _node(char: str, info: dict) -> dict:
    meanings = info.get("meanings") or []
    return {"char": char, "label": meanings[0] if meanings else char, "children": []}


# The 214 Kangxi radicals occupy a contiguous, ordered Unicode block
# (U+2F00 = radical 1 … U+2FD5 = radical 214), so radical number N maps to
# chr(0x2EFF + N). This avoids a hand-typed 214-entry table. The glyphs are the
# canonical radical forms (e.g. ⽔ for water) — correct to show as a group root.
def kangxi_char(index: int) -> str:
    if not 1 <= index <= 214:
        return "他"  # fallback bucket char for missing/unknown radical
    return chr(0x2EFF + index)
