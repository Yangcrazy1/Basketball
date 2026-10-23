const { test } = require('node:test');
const assert = require('node:assert/strict');
const D = require('../src/data.json');
const E = require('../src/engine.js');
const S = require('../src/storage.cjs');
function selectPoint(q, point) {
  const raw = q.reverse ? 5 - point : point;
  const at = (q.values || [1, 2, 3, 4]).indexOf(raw);
  assert.notEqual(at, -1);
  return at + 1;
}
const encode = (point, mode, data = D) => E.getQuestions(data, mode).map(q => selectPoint(q, point));
const clean = () => JSON.parse(JSON.stringify(D));

test('V4 modes are nested 8/16/24 sets and each covers the six main dimensions', () => {
  assert.equal(D.version, 4);
  assert.deepEqual(D.modes.map(m => m.count), [8, 16, 24]);
  assert.equal(D.questions.length, 24);
  assert.equal(new Set(D.questions.map(q => q.id)).size, 24);
  for (const mode of D.modes) {
    const qs = E.getQuestions(D, mode.id);
    assert.equal(qs.length, mode.count);
    D.dimensions.forEach(d => assert.ok(qs.some(q => q.dim === d.id)));
  }
  assert.deepEqual(E.getQuestions(D, 'deep').slice(0, 16), E.getQuestions(D, 'standard'));
  assert.deepEqual(E.getQuestions(D, 'standard').slice(0, 8), E.getQuestions(D, 'quick'));
});

test('display order is shuffled and every option position has balanced effective primary values', () => {
  for (const q of D.questions) {
    assert.equal(q.options.length, 4);
    assert.deepEqual(q.values.slice().sort(), [1, 2, 3, 4]);
    if (q.secondary) {
      assert.notEqual(q.secondary.dim, q.dim);
      assert.equal(q.secondary.values.length, 4);
      q.secondary.values.forEach(v => assert.ok(Number.isInteger(v) && v >= 1 && v <= 4));
    }
  }
  for (let position = 0; position < 4; position++) {
    const counts = [0, 0, 0, 0];
    D.questions.forEach(q => { const raw = q.values[position]; counts[(q.reverse ? 5 - raw : raw) - 1]++; });
    assert.deepEqual(counts, [6, 6, 6, 6]);
  }
});

test('normalization and reverse scoring reach exact primary-only 0/100 endpoints in every mode', () => {
  const data = clean();
  data.questions.forEach(q => delete q.secondary);
  for (const mode of data.modes) {
    assert.deepEqual(E.score(encode(1, mode.id, data), data, mode.id), [0, 0, 0, 0, 0, 0]);
    assert.deepEqual(E.score(encode(4, mode.id, data), data, mode.id), [100, 100, 100, 100, 100, 100]);
  }
});

test('secondary values have 0.3 weight, their own final direction, and a weighted denominator', () => {
  const a = encode(1, 'quick');
  const result = E.analyze(a, D, 'quick');
  const order = D.dimensions.findIndex(d => d.id === 'order');
  // q5 contributes primary 1; reversed explore q8 contributes secondary order 4.
  // ((1 + .3*4) / 1.3 - 1) / 3 * 100 = 23.0769, rounded to 23.
  assert.equal(result.vector[order], 23);
  assert.equal(result.coverage[order], 1);
  assert.equal(result.weightedCoverage[order], 1.3);
  const without = clean();
  delete without.questions[7].secondary;
  assert.equal(E.score(a, without)[order], 0);
});

test('permuting shown choices with their value maps preserves dimensions, facets and interpretation', () => {
  const data = clean(), original = D.questions.map((q, i) => i % 4 + 1);
  data.questions.forEach(q => {
    q.options.reverse(); q.values.reverse();
    if (q.secondary) q.secondary.values.reverse();
  });
  const remapped = original.map(answer => 5 - answer);
  assert.deepEqual(E.analyze(remapped, data, 'deep'), E.analyze(original, D, 'deep'));
});

test('incomplete, sparse, unsupported lengths, invalid modes and out-of-range answers fail', () => {
  for (const a of [null, [], Array(8), Array(18).fill(2), Array(8).fill(null), Array(8).fill(0), Array(8).fill(5), Array(8).fill(2.5), Array(8).fill('2')]) {
    assert.throws(() => E.analyze(a, D));
  }
  assert.throws(() => E.analyze(Array(8).fill(2), D, 'deep'));
  assert.throws(() => E.getQuestions(D, 'unknown'));
  assert.ok(E.validAnswers(Array(24).fill(null), D, false, 'deep'));
  assert.equal(E.validAnswers(Array(8).fill(2), D, true, 'unknown'), false);
});

test('longer modes may revise the initial family using new actual responses', () => {
  const answers = D.questions.map((q, i) => selectPoint(q, i < 8 ? 1 : 4));
  const quick = E.analyze(answers.slice(0, 8), D, 'quick');
  const standard = E.analyze(answers.slice(0, 16), D, 'standard');
  const deep = E.analyze(answers, D, 'deep');
  assert.equal(quick.subtype, null); assert.equal(quick.branch, null);
  assert.ok(standard.subtype); assert.equal(standard.branch, null);
  assert.ok(deep.subtype); assert.ok(deep.branch);
  assert.notEqual(quick.familyCode, standard.familyCode);
  for (const result of [quick, standard, deep]) {
    const expected = ['social', 'explore', 'empathy'].map(id => result.vector[D.dimensions.findIndex(d => d.id === id)] >= 50 ? '1' : '0').join('');
    assert.equal(result.familyCode, expected);
    assert.equal(result.profile.id, D.familyCodes[expected]);
  }
});

test('subtype reflects all available action/order evidence rather than only the middle block', () => {
  const answers = D.questions.map(q => selectPoint(q, 1));
  // q4 is an action question in the first block; q10 and q16 are the middle action pair.
  const a = answers.slice(0, 16), b = a.slice();
  b[3] = selectPoint(D.questions[3], 4);
  const x = E.analyze(a, D), y = E.analyze(b, D);
  const action = D.dimensions.findIndex(d => d.id === 'action');
  assert.ok(y.vector[action] > x.vector[action]);
  for (const result of [x, y]) {
    const code = ['action', 'order'].map(id => result.vector[D.dimensions.findIndex(d => d.id === id)] >= 50 ? '1' : '0').join('');
    assert.equal(result.subtype.id, D.subtypes[code].id);
  }
});

test('deep facets use value maps and their own reverse direction', () => {
  const answers = D.questions.map(q => selectPoint(q, 2));
  for (let i = 16; i < 24; i++) {
    const q = D.questions[i], desired = q.facet === 'spotlight' ? 4 : 1;
    const raw = q.facetReverse ? 5 - desired : desired;
    answers[i] = q.values.indexOf(raw) + 1;
  }
  const result = E.analyze(answers, D, 'deep');
  assert.deepEqual(result.facets, { spotlight: 100, boundary: 0 });
  assert.equal(result.branch.id, D.branches['10'].id);
});

test('evidence quotes real selections, uses distinct questions and includes no invented certainty', () => {
  const answers = D.questions.map((q, i) => i % 4 + 1), result = E.analyze(answers, D);
  assert.ok(result.evidence.length >= 2 && result.evidence.length <= 4);
  assert.equal(new Set(result.evidence.map(e => e.questionId)).size, result.evidence.length);
  result.evidence.forEach(e => {
    const at = D.questions.findIndex(q => q.id === e.questionId), q = D.questions[at], raw = q.values[answers[at] - 1];
    assert.equal(e.title, q.title); assert.equal(e.option, q.options[answers[at] - 1]);
    assert.equal(e.value, q.reverse ? 5 - raw : raw);
    assert.equal(e.dimension, D.dimensions.find(d => d.id === q.dim).name);
    assert.equal(e.dimensionId, q.dim);
  });
});

test('near-boundary coordinates and context variation are exposed without judging answer quality', () => {
  const answers = D.questions.map(q => selectPoint(q, 2));
  answers[0] = selectPoint(D.questions[0], 1);
  answers[6] = selectPoint(D.questions[6], 4);
  const result = E.analyze(answers, D, 'deep');
  result.boundaryDimensions.forEach(d => { assert.ok(d.value >= 40 && d.value <= 60); assert.equal(d.value, result.vector[D.dimensions.findIndex(dim => dim.id === d.id)]); });
  assert.ok(result.variation.some(v => v.dimensionId === 'social'));
  assert.ok(result.variation.every(v => v.description.includes('不同场景')));
});

test('role data and result rankings are complete, deterministic and sorted by actual distance', () => {
  assert.equal(new Set(D.characters.map(p => p.id)).size, D.characters.length);
  assert.ok(D.featured.length >= 6);
  D.categories.forEach(c => assert.ok(D.characters.some(p => p.category === c.id)));
  [...D.profiles, ...D.characters].forEach(p => { assert.equal(p.vector.length, 6); p.vector.forEach(v => assert.ok(Number.isFinite(v) && v >= 0 && v <= 100)); });
  for (const mode of D.modes) {
    const a = encode(3, mode.id), r = E.analyze(a, D);
    assert.deepEqual(r, E.analyze(a, D));
    for (const c of D.categories) r.categories[c.id].forEach((p, i, items) => { assert.ok(p.similarity >= 0 && p.similarity <= 100); if (i) assert.ok(items[i - 1].distance <= p.distance); });
  }
});

test('distance uses the actual vector dimension count and explanations report real differences', () => {
  assert.equal(E.similarity([0, 0], [0, 0]), 100); assert.equal(E.similarity([0, 0], [100, 100]), 0);
  assert.equal(E.similarity([0, 100], [100, 100]), 50); assert.throws(() => E.similarity([0], [0, 1]));
  const r = E.explain([0, 20, 40, 60, 80, 100], { vector: [0, 20, 35, 50, 60, 10] }, D.dimensions);
  assert.deepEqual(r.close.map(d => d.gap), [0, 0]); assert.equal(r.contrast.gap, 90);
});

test('reused MIT storage round-trips metadata and clears only its own session/result records', () => {
  const api = S.createStorage(), session = { mode: 'quick', answers: [1, null], index: 1 }, result = { mode: 'deep', answers: [1, 2] };
  api.setStorageSync('other-record', 'keep'); S.saveSession(api, session); assert.deepEqual(S.loadSession(api), session);
  S.saveResult(api, result); S.clearSession(api); assert.equal(S.loadSession(api), null); assert.deepEqual(S.loadResult(api), result);
  S.clearAllQuizState(api); assert.equal(S.loadResult(api), null); assert.equal(api.getStorageSync('other-record'), 'keep');
});
