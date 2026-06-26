import { loadLevel } from './data-loader.js';
import { renderMindmap } from './mindmap.js';
import { renderDetail } from './detail.js';

const mapsEl = document.getElementById('maps');
const detailEl = document.getElementById('detail');

async function showLevel(level) {
  const data = await loadLevel(level);
  mapsEl.innerHTML = '';
  for (const root of data.roots) {
    const section = document.createElement('section');
    section.className = 'cluster';
    const h2 = document.createElement('h2');
    h2.innerHTML = `<span class="root-kanji">${root.root}</span> ${root.label}`;
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    section.append(h2, svg);
    mapsEl.append(section);
    renderMindmap(svg, root, {
      onSelect: (char) => {
        const info = data.kanji[char];
        if (info) renderDetail(detailEl, info);
      },
    });
  }
}

document.getElementById('levels').addEventListener('click', (e) => {
  const btn = e.target.closest('button[data-level]');
  if (!btn) return;
  document.querySelectorAll('#levels button').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  showLevel(btn.dataset.level);
});

showLevel('N5');
