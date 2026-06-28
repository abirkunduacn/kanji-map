export function wordsUsing(words, char, limit = 8) {
  return (words || []).filter(w => w.kanji && w.kanji.includes(char)).slice(0, limit);
}

function vocabList(items) {
  if (!items || !items.length) return '<p class="empty">—</p>';
  return '<ul>' + items.map(v =>
    `<li><span class="vw">${v.word}</span>` +
    `<span class="vr">${v.reading}</span>` +
    `<span class="vg">${v.gloss}</span></li>`).join('') + '</ul>';
}

function wordsUsingList(words, char, onSelectWord) {
  const items = wordsUsing(words, char);
  if (!items.length) return '';
  const rows = items.map(w =>
    `<li><button class="wlink" data-word="${w.word}">${w.word}</button>` +
    `<span class="vr">${w.reading}</span><span class="vg">${w.gloss}</span></li>`).join('');
  return `<h3>Words using this kanji</h3><ul class="using">${rows}</ul>`;
}

export function renderDetail(el, info, { words = [], onSelectWord } = {}) {
  el.hidden = false;
  el.innerHTML = `
    <button class="close" aria-label="Close">×</button>
    <div class="big-kanji">${info.char}</div>
    <p class="meanings">${info.meanings.join(', ')}</p>
    <dl class="readings">
      <dt>On'yomi</dt><dd>${info.on.join('、') || '—'}</dd>
      <dt>Kun'yomi</dt><dd>${info.kun.join('、') || '—'}</dd>
      <dt>Strokes</dt><dd>${info.strokes}</dd>
    </dl>
    <h3>On'yomi vocabulary</h3>${vocabList(info.vocab.on)}
    <h3>Kun'yomi vocabulary</h3>${vocabList(info.vocab.kun)}
    ${wordsUsingList(words, info.char, onSelectWord)}
  `;
  el.querySelector('.close').onclick = () => { el.hidden = true; };
  if (onSelectWord) {
    el.querySelectorAll('.wlink').forEach(b =>
      b.addEventListener('click', () => onSelectWord(b.dataset.word)));
  }
}
