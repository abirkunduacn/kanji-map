import { loadLevel } from './data-loader.js';
import { renderMindmap } from './mindmap.js';
import { renderWords } from './words.js';
import { renderDetail } from './detail.js';

const contentEl = document.getElementById('content');
const detailEl = document.getElementById('detail');
const state = { level: 'N5', view: 'trees' };
let current = null;

function openDetail(char) {
  const info = current && current.kanji[char];
  if (info) {
    renderDetail(detailEl, info, {
      words: current.words,
      onSelectWord: () => setView('words'),
    });
  }
}

function renderTrees() {
  contentEl.innerHTML = '';
  for (const root of current.roots) {
    const section = document.createElement('section');
    section.className = 'cluster';
    const h2 = document.createElement('h2');
    h2.innerHTML = `<span class="root-kanji">${root.root}</span> ${root.label}`;
    const scroll = document.createElement('div');
    scroll.className = 'cluster-scroll';
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    scroll.append(svg);
    section.append(h2, scroll);
    contentEl.append(section);
    renderMindmap(svg, root, { onSelect: openDetail });
  }
}

async function render() {
  current = await loadLevel(state.level);
  if (state.view === 'trees') renderTrees();
  else renderWords(contentEl, current, { onSelectKanji: openDetail });
}

function setActive(containerId, attr, value) {
  document.querySelectorAll(`#${containerId} button`).forEach(b =>
    b.classList.toggle('active', b.dataset[attr] === value));
}
function setLevel(level) { state.level = level; setActive('levels', 'level', level); render(); }
function setView(view) { state.view = view; setActive('views', 'view', view); render(); }

document.getElementById('levels').addEventListener('click', e => {
  const b = e.target.closest('button[data-level]'); if (b) setLevel(b.dataset.level);
});
document.getElementById('views').addEventListener('click', e => {
  const b = e.target.closest('button[data-view]'); if (b) setView(b.dataset.view);
});

render();
