import { test } from 'node:test';
import assert from 'node:assert/strict';
import { wordsUsing } from '../../js/detail.js';

test('wordsUsing returns words containing the char, capped', () => {
  const words = [
    { word: '学生', reading: 'がくせい', gloss: 'student', kanji: ['学', '生'] },
    { word: '生活', reading: 'せいかつ', gloss: 'life', kanji: ['生', '活'] },
    { word: '学校', reading: 'がっこう', gloss: 'school', kanji: ['学', '校'] },
  ];
  const out = wordsUsing(words, '生').map(w => w.word);
  assert.deepEqual(out, ['学生', '生活']);
  assert.equal(wordsUsing(words, '生', 1).length, 1);
});
