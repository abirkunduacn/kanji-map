import { toHierarchy } from './hierarchy.js';

const NODE_W = 170, NODE_H = 40;

export function renderMindmap(svgEl, rootData, { onSelect } = {}) {
  const d3 = window.d3;
  svgEl.innerHTML = '';
  const svg = d3.select(svgEl);

  const root = d3.hierarchy(toHierarchy(rootData));
  const depth = root.height + 1;
  const leaves = root.leaves().length;

  const width = depth * NODE_W + 80;
  const height = Math.max(leaves * NODE_H + 40, 120);
  svgEl.setAttribute('viewBox', `0 0 ${width} ${height}`);
  svgEl.setAttribute('width', width);
  svgEl.setAttribute('height', height);

  const layout = d3.tree().size([height - 40, width - NODE_W - 40]);
  layout(root);

  const g = svg.append('g').attr('transform', 'translate(20,20)');

  g.append('g').attr('class', 'links')
    .selectAll('path').data(root.links()).enter().append('path')
    .attr('class', 'link')
    .attr('d', d3.linkHorizontal().x(d => d.y).y(d => d.x));

  const node = g.append('g').attr('class', 'nodes')
    .selectAll('g').data(root.descendants()).enter().append('g')
    .attr('class', d => d.depth === 0 ? 'node node--root' : 'node')
    .attr('transform', d => `translate(${d.y},${d.x})`)
    .style('cursor', d => d.depth === 0 ? 'default' : 'pointer')
    .on('click', (_, d) => { if (d.depth > 0 && onSelect) onSelect(d.data.char); });

  node.append('text').attr('class', 'kanji').attr('dy', '0.32em').text(d => d.data.char);
  node.append('text').attr('class', 'gloss').attr('dx', 22).attr('dy', '0.32em')
    .text(d => d.data.label);
}
