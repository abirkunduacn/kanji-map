import { loadLevel } from './data-loader.js';
import { renderMindmap } from './mindmap.js';

function param(name, fallback) {
  return new URLSearchParams(location.search).get(name) || fallback;
}

function vocab1(list) {
  if (!list || !list.length) return '—';
  const v = list[0];
  return `${v.word} (${v.reading}) ${v.gloss}`;
}

async function main() {
  const level = param('level', 'N5');
  const data = await loadLevel(level);
  document.getElementById('title').textContent = `Kanji Mind-Map · JLPT ${level}`;

  const maps = document.getElementById('maps');
  for (const root of data.roots) {
    const sec = document.createElement('section');
    sec.className = 'cluster';
    const h2 = document.createElement('h2');
    h2.innerHTML = `<span class="root-kanji">${root.root}</span> ${root.label}`;
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    sec.append(h2, svg);
    maps.append(sec);
    renderMindmap(svg, root, {});
  }

  const tbody = document.querySelector('#ref tbody');
  for (const ch of Object.keys(data.kanji).sort()) {
    const k = data.kanji[ch];
    const tr = document.createElement('tr');
    tr.innerHTML = `<td class="rk">${ch}</td><td>${k.on.join('、')}</td>` +
      `<td>${k.kun.join('、')}</td><td>${vocab1(k.vocab.on)}</td>` +
      `<td>${vocab1(k.vocab.kun)}</td>`;
    tbody.append(tr);
  }
  window.__renderComplete = true;
}
main();
