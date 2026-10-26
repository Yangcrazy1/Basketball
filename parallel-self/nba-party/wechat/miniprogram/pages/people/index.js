'use strict';
const N = require('../../lib/native');
Page({
  data: { people: [], cards: [], selected: null, selectedCards: [], query: '', mode: 'people' },
  onLoad: function (options) { this.refresh(''); if (options.pid) this.openPerson(options.pid); },
  refresh: function (query) {
    const q = query.trim().toLowerCase();
    this.setData({ people: N.G.people.filter(function (p) { return [p.name, p.nickname].concat(p.aliases || [], p.tags || []).join(' ').toLowerCase().indexOf(q) >= 0; }).map(N.person), cards: N.G.cards.filter(function (a) { return [a.name, a.effect, a.line].join(' ').toLowerCase().indexOf(q) >= 0; }).map(N.card) });
  },
  search: function (e) { this.setData({ query: e.detail.value }); this.refresh(e.detail.value); },
  mode: function (e) { this.setData({ mode: e.currentTarget.dataset.mode, selected: null }); },
  person: function (e) { this.openPerson(e.currentTarget.dataset.pid); },
  openPerson: function (pid) {
    const person = N.G.people.find(function (p) { return p.personId === pid; }); if (!person) return;
    const cards = (person.signaturePerks || []).map(function (id) { return N.G.cards.find(function (a) { return a.id === id; }); }).filter(Boolean).map(N.card);
    this.setData({ selected: N.person(person), selectedCards: cards }); wx.pageScrollTo({ scrollTop: 0, duration: 0 });
  },
  back: function () { this.setData({ selected: null }); },
  story: function () { wx.navigateTo({ url: '/pages/story/index?pid=' + encodeURIComponent(this.data.selected.personId) }); }
});
