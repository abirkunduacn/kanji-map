import { test } from 'node:test';
import assert from 'node:assert/strict';
import { wordsView } from '../../js/words.js';

test('wordsView sorts by kanji count then length', () => {
  const data = { words: [
    { word: '生活', reading: 'せいかつ', gloss: 'life', kanji: ['生', '活'] },
    { word: '小学生', reading: 'しょうがくせい', gloss: 'pupil', kanji: ['小', '学', '生'] },
    { word: '学生', reading: 'がくせい', gloss: 'student', kanji: ['学', '生'] },
  ] };
  const out = wordsView(data).map(w => w.word);
  assert.deepEqual(out, ['学生', '生活', '小学生']); // 2-kanji (len2) before 2-kanji... then 3-kanji last
});

test('wordsView tolerates missing words', () => {
  assert.deepEqual(wordsView({}), []);
});
