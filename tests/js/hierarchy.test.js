import { test } from 'node:test';
import assert from 'node:assert/strict';
import { toHierarchy, countNodes } from '../../js/hierarchy.js';

const root = { id: 'r', root: '口', label: 'Mouth',
  children: [{ char: '日', label: 'sun', children: [
    { char: '車', label: 'car', children: [] },
  ] }] };

test('toHierarchy makes synthetic root from component', () => {
  const h = toHierarchy(root);
  assert.equal(h.char, '口');
  assert.equal(h.name, 'Mouth');
  assert.equal(h.children[0].char, '日');
  assert.equal(h.children[0].children[0].char, '車');
});

test('countNodes counts root + descendants', () => {
  assert.equal(countNodes(toHierarchy(root)), 3); // 口, 日, 車
});
