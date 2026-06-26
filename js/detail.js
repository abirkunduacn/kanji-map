function vocabList(items) {
  if (!items || !items.length) return '<p class="empty">—</p>';
  return '<ul>' + items.map(v =>
    `<li><span class="vw">${v.word}</span>` +
    `<span class="vr">${v.reading}</span>` +
    `<span class="vg">${v.gloss}</span></li>`).join('') + '</ul>';
}

export function renderDetail(el, info) {
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
  `;
  el.querySelector('.close').onclick = () => { el.hidden = true; };
}
