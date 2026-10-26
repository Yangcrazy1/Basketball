'use strict';
const N = require('../../lib/native');
Page({
  data: { count: 8, modes: [8, 16, 24], draft: null, latest: false, people: 0, questions: 0, cards: 0, samples: [] },
  onShow: function () {
    const draft = N.read('draft', null);
    this.setData({
      count: N.read('count', 8), draft: draft && draft.phase === 'quiz' ? { answered: draft.answers.filter(function (x) { return x !== null; }).length, count: draft.count } : null,
      latest: !!N.read('latest', null), people: N.G.people.length,
      questions: N.G.data.questions.filter(function (q) { return q.enabled !== false; }).length,
      cards: N.G.cards.length, samples: N.G.people.slice(0, 3).map(N.person)
    });
  },
  choose: function (e) { const count = Number(e.currentTarget.dataset.count); N.write('count', count); this.setData({ count: count }); },
  start: function () { wx.navigateTo({ url: '/pages/quiz/index?count=' + this.data.count }); },
  resume: function () { wx.navigateTo({ url: '/pages/quiz/index?resume=1' }); },
  result: function () { wx.navigateTo({ url: '/pages/result/index' }); },
  diy: function () { wx.navigateTo({ url: '/pages/diy/index' }); },
  people: function () { wx.navigateTo({ url: '/pages/people/index' }); },
  person: function (e) { wx.navigateTo({ url: '/pages/people/index?pid=' + encodeURIComponent(e.currentTarget.dataset.pid) }); },
  onShareAppMessage: function () { return { title: '换个球场，测测你是哪位整活球星', path: '/pages/home/index' }; }
});
