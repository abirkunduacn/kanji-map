"""Build kanji mind-map trees from IDS (Ideographic Description Sequences).

A kanji's parent is the most specific *in-scope* kanji it is structurally built
from, so chains read as a build-up of components, e.g. 一 -> 元 -> 院 and
十 -> 土 -> 主 -> 注.  This replaces the earlier hand-transcribed trees and
radical grouping: every edge here is a real "is built from" relationship, so
mis-groupings like 字 under 月 cannot occur.

Source: cjkvi-ids `ids.txt` (CHISE-derived).  We read only the structural
decomposition and emit factual parent/child relationships.
"""

# Ideographic Description Characters — structural operators, not components.
_IDC = set("⿰⿱⿲⿳⿴⿵⿶⿷⿸⿹⿺⿻")

# Char used for the catch-all cluster that collects kanji with no in-scope
# parent and no children.  Not a JLPT kanji, so it gets no detail entry.
OTHER_ROOT = "他"


def _is_cjk(ch: str) -> bool:
    # BMP CJK only: Unified Ideographs (U+4E00–U+9FFF) + Extension A
    # (U+3400–U+4DBF). Components in Ext B+ (above U+FFFF) are intentionally
    # ignored — they are never in-scope JLPT kanji, so they cannot be parents.
    return ("一" <= ch <= "鿿") or ("㐀" <= ch <= "䶿")


def parse_ids(path) -> dict[str, list[str]]:
    """Return {kanji: [direct component chars]} from an ids.txt file.

    Lines look like:  U+5B8C\t完\t⿱宀元   (tab-separated; col 3 is the IDS).
    Region tags like "[GTKV]" are stripped; IDC operators are dropped so only
    component characters remain.
    """
    direct: dict[str, list[str]] = {}
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        ch = parts[1]
        if len(ch) != 1:
            continue
        ids = parts[2].split("[")[0]
        comps = [c for c in ids if c not in _IDC and _is_cjk(c) and c != ch]
        direct[ch] = comps
    return direct


def _descendants(ch: str, direct: dict[str, list[str]], seen: set[str]) -> set[str]:
    """All structural sub-components of ch, recursively (excludes ch itself)."""
    for c in direct.get(ch, []):
        if c not in seen:
            seen.add(c)
            _descendants(c, direct, seen)
    return seen


def _node(char: str, kanji_infos: dict) -> dict:
    meanings = (kanji_infos.get(char) or {}).get("meanings") or []
    return {"char": char, "label": meanings[0] if meanings else char, "children": []}


def build_forest(direct, kanji_infos, scope, required=None) -> list[dict]:
    """Build a forest of build-from trees over `scope`.

    - parent(k) = the in-scope kanji that is a structural sub-component of k and
      is itself the most specific (greatest stroke count, then codepoint).
    - Kanji with no in-scope parent are roots.
    - If `required` is given, only trees whose nodes include at least one
      `required` kanji are kept (used so the N4 view keeps N5 connector kanji
      but drops trees made purely of other-level kanji).
    - Roots that end up with children become their own cluster (rooted at that
      kanji).  Roots with no children are collected into one OTHER_ROOT cluster.

    Returns a list of root dicts: {id, root, label, children:[node...]}.
    """
    scope = set(scope)
    strokes = {c: (kanji_infos.get(c) or {}).get("strokes", 0) or 0 for c in scope}

    def parent_of(k: str):
        desc = _descendants(k, direct, set())
        cands = [d for d in desc if d in scope and d != k]
        if not cands:
            return None
        return max(cands, key=lambda d: (strokes.get(d, 0), d))

    parent = {k: parent_of(k) for k in scope}

    # children adjacency (only for in-scope parents)
    children: dict[str, list[str]] = {k: [] for k in scope}
    roots: list[str] = []
    for k in scope:
        p = parent.get(k)
        if p is None:
            roots.append(k)
        else:
            children[p].append(k)

    def subtree(k: str) -> dict:
        node = _node(k, kanji_infos)
        node["children"] = [subtree(c) for c in sorted(children[k], key=lambda c: (strokes.get(c, 0), c))]
        return node

    def members(node: dict) -> set[str]:
        out = {node["char"]}
        for c in node["children"]:
            out |= members(c)
        return out

    tree_roots: list[dict] = []
    misc: list[dict] = []
    for r in sorted(roots, key=lambda c: (-strokes.get(c, 0), c)):
        node = subtree(r)
        if required is not None and not (members(node) & set(required)):
            continue  # tree has no required kanji -> belongs to another level's view
        meanings = (kanji_infos.get(r) or {}).get("meanings") or []
        label = meanings[0] if meanings else r
        if node["children"]:
            tree_roots.append({"id": f"k-{r}", "root": r, "label": label, "children": node["children"]})
        else:
            misc.append(node)

    # Safety net: any in-scope kanji not reachable from a root — which could
    # only happen if IDS data ever contained a true A-contains-B-contains-A
    # cycle — would otherwise be silently dropped. Fold such strays in as
    # standalone nodes so completeness never depends on the data being acyclic.
    def _chars(node):
        out = {node["char"]}
        for c in node["children"]:
            out |= _chars(c)
        return out

    emitted = set()
    for tr in tree_roots:
        emitted.add(tr["root"])
        for c in tr["children"]:
            emitted |= _chars(c)
    for m in misc:
        emitted |= _chars(m)
    for stray in sorted(scope - emitted):
        misc.append(_node(stray, kanji_infos))

    if required is not None:
        misc = [m for m in misc if m["char"] in set(required)]

    if misc:
        tree_roots.append({
            "id": "other",
            "root": OTHER_ROOT,
            "label": "Other (standalone)",
            "children": sorted(misc, key=lambda n: n["char"]),
        })
    return tree_roots
