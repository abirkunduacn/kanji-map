export function wordsView(levelData) {
  const words = (levelData && levelData.words) || [];
  return [...words].sort((a, b) =>
    a.kanji.length - b.kanji.length ||
    a.word.length - b.word.length ||
    a.word.localeCompare(b.word));
}

export function renderWords(el, levelData, { onSelectKanji } = {}) {
  el.innerHTML = '';
  const grid = document.createElement('div');
  grid.className = 'words-grid';
  const items = wordsView(levelData);
  if (!items.length) {
    el.innerHTML = '<p class="empty">No multi-kanji words yet for this level.</p>';
    return;
  }
  for (const w of items) {
    const card = document.createElement('article');
    card.className = 'word-card';
    const chips = w.kanji
      .map(c => `<button class="chip" data-char="${c}" aria-label="Open ${c}">${c}</button>`)
      .join('');
    card.innerHTML =
      `<div class="word">${w.word}</div>` +
      `<div class="word-reading">${w.reading}</div>` +
      `<div class="word-gloss">${w.gloss}</div>` +
      `<div class="chips">${chips}</div>`;
    grid.append(card);
  }
  el.append(grid);
  if (onSelectKanji) {
    el.addEventListener('click', e => {
      const b = e.target.closest('.chip');
      if (b) onSelectKanji(b.dataset.char);
    });
  }
}
