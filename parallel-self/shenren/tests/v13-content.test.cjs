// V13 regression: execute the exact schema 12 snapshot, independently of current V14 data.
// Domain checks for the authored supplement; this file never modifies live data.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const E = require('../src/legacy-v12/engine.js');
const root = path.join(__dirname, '..');
const patch = JSON.parse(fs.readFileSync(path.join(root, 'content/v13-roster-additions.json'), 'utf8'));
const evidenceFix = JSON.parse(fs.readFileSync(path.join(root, 'content/v13-evidence-fix.json'), 'utf8'));
// Content is authored in two reviewable deltas. Apply only the explicit second delta in memory.
for (const v of evidenceFix.cards) {
  Object.assign(Object.values(patch.augments).flat().find(c => c.id === v.id), v);
}
for (const v of evidenceFix.questions) {
  const q = patch.questions.find(q => q.id === v.id);
  if (v.title) q.title = v.title;
  for (const o of v.options || []) Object.assign(q.options.find(x => x.id === o.id), o);
}
const base = JSON.parse(fs.readFileSync(path.join(root, 'src/legacy-v12/data.json'), 'utf8'));
const dims = ['social', 'explore', 'empathy', 'action', 'order', 'express'];
const lolDims = ['tilt', 'greed', 'risk', 'team', 'craft', 'plan'];
const expected = ['wuyou','xire','tmac','shaq','doncic','shai','rodman','wilt','yujie','musk','trump','renzhengfei','yuchengdong','jensen','nida','yili','wangsicong'];

function merged() {
  const d = JSON.parse(JSON.stringify(base));
  function upsert(list, incoming, key) {
    for (const value of incoming) {
      const i = list.findIndex(x => x[key] === value[key]);
      if (i < 0) list.push(value); else list[i] = Object.assign({}, list[i], value);
    }
  }
  upsert(d.characters, patch.characters, 'personId');
  upsert(d.questions, patch.questions, 'id');
  for (const theme of Object.keys(patch.augments)) upsert(d.augments[theme], patch.augments[theme], 'id');
  Object.assign(d.behaviorLabels, patch.behaviorLabels);
  return d;
}

test('requested new identities stay distinct and old canonical identity keys are reused', () => {
  assert.deepEqual(patch.characters.map(p => p.personId).sort(), expected.slice().sort());
  assert.equal(new Set(patch.characters.map(p => p.id)).size, 17);
  for (const p of patch.characters) {
    const prior = base.characters.find(x => x.personId === p.personId);
    if (prior) assert.equal(p.id, prior.id, p.personId);
    assert.equal(p.enabled, true);
    assert.equal(p.universe && Object.keys(p.universe).length, 5);
    assert.ok(Object.entries(p.universe).every(([k,s]) => typeof s === 'string' && s.length >= (k === 'title' ? 4 : 12)));
    assert.equal(p.signaturePerks.length, 3);
  }
  assert.notEqual(patch.characters.find(p => p.personId === 'renzhengfei').id,
                  patch.characters.find(p => p.personId === 'yuchengdong').id);
  for (const id of ['nida','yili']) {
    const p = patch.characters.find(x => x.personId === id);
    assert.ok(!p.nickname.includes('金角') && !p.nickname.includes('银角'));
  }
});

test('new non-League situations cover six actual dimensions; the hotdog story stays four ordered scenes', () => {
  assert.equal(patch.questions.length, 100);
  for (const p of patch.characters) {
    const qs = patch.questions.filter(q => q.personContext === p.personId);
    assert.equal(qs.length, p.theme === 'lol' ? 4 : 6);
    if (p.theme !== 'lol') assert.deepEqual(qs.map(q => q.dim), dims);
    for (const q of qs) {
      assert.equal(q.theme, p.theme);
      assert.equal(q.options.length, 4);
      assert.equal(new Set(q.options.map(o => o.text)).size, 4);
      assert.deepEqual(q.options.map(o => o.id), [0,1,2,3]);
      assert.ok(p.answerAffinities[q.id][q.options[0].behavior] === 5);
      for (const o of q.options) {
        assert.ok(base.behaviorLabels[o.behavior] || patch.behaviorLabels[o.behavior], o.behavior);
        if (p.theme !== 'lol') assert.ok(o.value >= 1 && o.value <= 4);
        else {
          assert.deepEqual(Object.keys(o.signals), lolDims);
          assert.ok(Object.values(o.signals).every(n => n >= 0 && n <= 100));
        }
      }
    }
  }
  const hotdog = patch.questions.filter(q => q.theme === 'lol');
  assert.deepEqual(hotdog.map(q => q.stage), [0,1,2,3]);
  assert.ok(hotdog.every(q => q.chapter === 's8-hotdog' && q.series === 'rift'));
  assert.ok(/热狗/.test(hotdog[0].title));
  assert.ok(/导播/.test(hotdog[1].title));
  assert.ok(/还在打/.test(hotdog[2].title));
  assert.ok(/合照/.test(hotdog[3].title));
  assert.equal(patch.characters.find(p => p.personId === 'wangsicong').roleType, 'spectator');
});

test('each new identity owns exactly two evidence-triggered perks and one evidence-free gift', () => {
  const cards = Object.values(patch.augments).flat();
  const atlases = JSON.parse(fs.readFileSync(path.join(root, 'assets/rich-perk-atlases.json'), 'utf8'));
  assert.equal(cards.length, 51);
  assert.equal(new Set(cards.map(c => c.id)).size, 51);
  for (const p of patch.characters) {
    const own = cards.filter(c => c.owner === p.personId);
    assert.deepEqual(own.map(c => c.id), p.signaturePerks);
    assert.equal(own.filter(c => c.activationMode === 'answers').length, 2);
    assert.equal(own.filter(c => c.activationMode === 'identity').length, 1);
    for (const c of own) {
      assert.deepEqual(c.signatureFor, [p.personId]);
      assert.equal(c.exclusive, true);
      assert.equal(c.personOnly, true);
      assert.equal(c.preferClassic, true);
      assert.ok(atlases[c.classicSprite.sheet] && c.classicSprite.cell >= 0 && c.classicSprite.cell < 16);
      if (c.activationMode === 'identity') {
        assert.deepEqual(c.evidenceQuestionIds, []);
        assert.deepEqual(c.requires, []);
      } else {
        assert.ok(c.evidenceQuestionIds.length >= 2 && c.requires.length > 0);
        for (const id of c.evidenceQuestionIds) {
          const q = patch.questions.find(q => q.id === id);
          assert.ok(q && q.personContext === p.personId);
          assert.ok(q.options.some(o => c.requires.includes(o.behavior)), c.id + ':' + id);
        }
      }
    }
  }
  // A foul-line card cannot be justified just by an unrelated dunk/show selection.
  const shaqLesson = cards.find(c => c.id === 'v13-shaq-2');
  assert.deepEqual(shaqLesson.evidenceQuestionIds, ['v13-owner-shaq-0','v13-owner-shaq-4']);
  assert.deepEqual(shaqLesson.requires, ['nba-train','nba-calm']);
  assert.deepEqual(cards.find(c => c.id === 'v13-jensen-2').evidenceQuestionIds, ['v13-owner-jensen-1','v13-owner-jensen-4']);
});

test('perks use real current answer evidence and never treat an identity gift as a played answer', () => {
  const d = merged();
  for (const p of patch.characters.filter(p => p.theme !== 'lol')) {
    const own = patch.questions.filter(q => q.personContext === p.personId);
    const extras = d.questions.filter(q => q.enabled !== false && q.theme === p.theme && q.personContext !== p.personId).slice(0,2);
    const s = E.draw(d, p.theme, 8);
    s.deck = own.concat(extras).map(q => ({id:q.id, order:[0,1,2,3]}));
    s.answers = own.concat(extras).map(() => 0);
    s.phase = 'complete';
    assert.ok(E.valid(s, d, true));
    const actual = E.recommend(s, d, E.score(s,d), p);
    const ownCards = patch.augments[p.theme].filter(c => c.owner === p.personId);
    for (const c of ownCards) {
      if (c.activationMode === 'identity') assert.ok(!actual.some(a => a.id === c.id));
      else {
        const got = actual.find(a => a.id === c.id);
        assert.ok(got, p.personId + ':' + c.id);
        assert.ok(got.evidence.length > 0);
        assert.ok(got.evidence.every(e => c.evidenceQuestionIds.includes(e.id)));
      }
    }
  }
});

test('new stories flag the fictional awards and rumors while keeping the requested public memes searchable', () => {
  const people = id => patch.characters.find(p => p.personId === id);
  assert.ok(people('tmac').tags.includes('最美小腿奖'));
  assert.match(people('tmac').universe.passive, /自设/);
  assert.ok(people('wilt').tags.includes('2000后宫梗'));
  assert.match(people('wilt').universe.arrival, /纸片人后援团/);
  assert.match(people('wilt').universe.passive, /不是现实私生活陈述/);
  assert.match(people('trump').universe.arrival, /平行综艺/);
  assert.match(people('musk').universe.arrival, /架空发布会/);
  assert.ok(people('doncic').nickname.includes('汉堡王'));
  assert.ok(people('shai').nickname.includes('罚'));
});

test('the evidence repair edits question text only and supports two genuine answer scenes per repaired card', () => {
  assert.equal(evidenceFix.cards.length, 6);
  assert.equal(evidenceFix.questions.length, 6);
  for (const q of evidenceFix.questions) {
    assert.ok(Object.keys(q).every(k => ['id','title','options'].includes(k)));
    for (const o of q.options || []) assert.deepEqual(Object.keys(o).sort(), ['id','text']);
  }
  for (const c of evidenceFix.cards) {
    const card = Object.values(patch.augments).flat().find(a => a.id === c.id);
    const real = card.evidenceQuestionIds.filter(id => {
      const q = patch.questions.find(q => q.id === id);
      return q.options.some(o => card.requires.includes(o.behavior) && card.behaviorWeights[o.behavior] > 0);
    });
    assert.ok(real.length >= 2, c.id);
    assert.deepEqual(card.behaviorRules.questionIds, card.evidenceQuestionIds);
  }
});
