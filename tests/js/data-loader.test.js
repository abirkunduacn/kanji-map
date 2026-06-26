import { test } from 'node:test';
import assert from 'node:assert/strict';
import { validateLevelData, loadLevel, kanjiCount } from '../../js/data-loader.js';

const good = {
  level: 'N5', generated: '2026-06-26',
  roots: [{ id: 'r', root: '口', label: 'Mouth',
            children: [{ char: '生', label: 'life', children: [] }] }],
  kanji: { '生': { char: '生', meanings: ['life'], on: ['セイ'], kun: ['い.きる'],
                   strokes: 5, vocab: { on: [], kun: [] } } },
};

test('valid data passes', () => {
  assert.deepEqual(validateLevelData(good), { ok: true });
});

test('missing kanji entry for a placed node fails', () => {
  const bad = structuredClone(good);
  delete bad.kanji['生'];
  const res = validateLevelData(bad);
  assert.equal(res.ok, false);
  assert.match(res.error, /生/);
});

test('kanjiCount counts entries', () => {
  assert.equal(kanjiCount(good), 1);
});

test('loadLevel fetches and validates', async () => {
  const fakeFetch = async (url) => ({ ok: true, json: async () => good });
  const data = await loadLevel('N5', fakeFetch);
  assert.equal(data.level, 'N5');
});
