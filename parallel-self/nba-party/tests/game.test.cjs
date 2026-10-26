const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const context = { module: { exports: {} }, require: name => require(path.join(root, 'content', name)), console };
vm.runInNewContext(fs.readFileSync(path.join(root, 'shared/game.js'), 'utf8'), context);
const G = context.module.exports;
function completed(count, option = 0) {
  let s = G.start(count);
  for (let i = 0; i < count; i++) {
    const q = G.question(s);
    s = G.answer(s, q.id, q.options[option].id).session;
  }
  return s;
}
test('three quiz lengths produce distinct random questions, valid real results and five unique basketball teammates', () => {
  for (const count of [8, 16, 24]) {
    const a = G.start(count), b = G.start(count, a.deck[0].id);
    assert.equal(a.deck.length, count);
    assert.equal(new Set(a.deck.map(x => x.id)).size, count);
    assert.notEqual(a.deck[0].id, b.deck[0].id);
    const s = completed(count), r = G.result(s);
    assert.equal(G.valid(s, true), true);
    assert.equal(r.identity.theme, 'basket');
    assert.equal(r.team.length, 5);
    assert.equal(new Set(r.team.map(p => p.personId)).size, 5);
    assert.ok(G.cards.some(c => c.id === r.augment.id));
    assert.ok(r.teamName.title);
  }
});
test('stale double tap cannot answer a different question and previous editing remains valid', () => {
  const s = G.start(8), q = G.question(s);
  const next = G.answer(s, q.id, q.options[0].id).session;
  assert.throws(() => G.answer(next, q.id, q.options[0].id), /切换/);
  const back = G.previous(next);
  assert.equal(G.question(back).id, q.id);
  assert.equal(G.valid(G.answer(back, q.id, q.options[1].id).session), true);
});
test('DIY and self-selected team never replace the actual matched identity or score', () => {
  const r = G.result(completed(8, 2));
  const diy = G.makeDIY(G.diyDefaults());
  const mixed = G.withDIY(r, diy);
  assert.equal(mixed.identity.personId, r.identity.personId);
  assert.equal(mixed.identity.rawMatch, r.identity.rawMatch);
  assert.equal(mixed.team.filter(p => p.personId === 'diy-me').length, 1);
  assert.equal(mixed.team.filter(p => p.isYou).length, 1);
  assert.equal(G.withDIY(mixed, diy).team.filter(p => p.personId === 'diy-me').length, 1);
  assert.equal(G.people.some(p => p.personId === 'diy-me'), false);
  assert.throws(() => G.customTeam(r, Array(5).fill(G.people[0].id)), /重复/);
  const custom = G.customTeam(r, G.people.slice(0, 5).map(p => p.id));
  assert.equal(custom.identity.personId, r.identity.personId);
  assert.equal(new Set(custom.team.map(p => p.personId)).size, 5);
});
test('DIY validation blocks malformed ability values, invalid jersey numbers and oversized text', () => {
  assert.throws(() => G.makeDIY({ name: 'a'.repeat(13) }), /名字/);
  assert.throws(() => G.makeDIY({ number: '100' }), /号码/);
  assert.throws(() => G.makeDIY({ vector: [0, 0, 0, 0, 0, 101] }), /能力/);
  const d = G.makeDIY({ name: '<b>我</b>', avatarColor: 'url(javascript:1)' });
  assert.equal(d.name, '<b>我</b>');
  assert.equal(d.avatarColor, '#9d7cff');
});
test('all 21 existing branching stories start without invented acquired cards', () => {
  for (const p of G.people) {
    const state = G.storyStart(p.personId), view = G.storyView(state);
    assert.equal(view.ownedCardIds.length, 0);
    assert.ok(view.text);
  }
});
