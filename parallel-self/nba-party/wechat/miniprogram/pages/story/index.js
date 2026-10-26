'use strict';
const N = require('../../lib/native');
Page({
  data: { view: null, person: null, owned: [] },
  onLoad: function (options) {
    try {
      const result = options.from === 'result' ? N.loadResult() : null;
      const pid = result ? result.result.identity.personId : options.pid;
      const person = N.G.people.find(function (p) { return p.personId === pid; }); if (!person) throw Error('这位球星的故事不存在');
      this.origin = result ? result.record.session.date : 'preview:' + pid;
      const saved = N.read('story', null);
      this.state = saved && saved.origin === this.origin ? saved.state : N.G.storyStart(pid, result ? [result.result.augment.id] : []);
      this.setData({ person: N.person(person) }); this.render();
    } catch (e) { N.toast(e.message || '故事未能打开'); }
  },
  render: function () {
    const view = N.G.storyView(this.state);
    this.setData({ view: view, owned: view.ownedCardIds.map(function (id) { return N.G.cards.find(function (a) { return a.id === id; }); }).filter(Boolean) });
    N.write('story', { origin: this.origin, state: this.state });
  },
  act: function (next) {
    if (this.locked) return; this.locked = true;
    try { this.state = next(); this.render(); wx.pageScrollTo({ scrollTop: 0, duration: 0 }); }
    catch (e) { N.toast(e.message || '请重新选择'); }
    setTimeout(() => { this.locked = false; }, 220);
  },
  next: function () { this.act(() => N.G.storyNext(this.state)); },
  choice: function (e) { this.act(() => N.G.storyChoice(this.state, this.data.view.node, e.currentTarget.dataset.choice)); },
  previous: function () { this.act(() => N.G.storyBack(this.state)); },
  restart: function () { this.act(() => N.G.storyStart(this.data.person.personId, this.state.seedCards || [])); }
});
