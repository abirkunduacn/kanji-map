function walkChars(nodes, out) {
  for (const node of nodes) {
    out.add(node.char);
    walkChars(node.children || [], out);
  }
}

export function validateLevelData(data) {
  if (!data || typeof data !== 'object') return { ok: false, error: 'not an object' };
  for (const key of ['level', 'roots', 'kanji']) {
    if (!(key in data)) return { ok: false, error: `missing ${key}` };
  }
  const placed = new Set();
  for (const root of data.roots) walkChars(root.children || [], placed);
  for (const ch of placed) {
    if (!data.kanji[ch]) return { ok: false, error: `no detail entry for placed kanji ${ch}` };
  }
  return { ok: true };
}

export function kanjiCount(data) {
  return Object.keys(data.kanji || {}).length;
}

export async function loadLevel(level, fetchFn = fetch) {
  const res = await fetchFn(`data/${level.toLowerCase()}.json`);
  if (!res.ok) throw new Error(`failed to load ${level}`);
  const data = await res.json();
  const v = validateLevelData(data);
  if (!v.ok) throw new Error(`invalid ${level} data: ${v.error}`);
  return data;
}
