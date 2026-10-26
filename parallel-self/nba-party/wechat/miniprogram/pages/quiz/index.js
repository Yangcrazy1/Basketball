'use strict';
const N = require('../../lib/native');
Page({
  data: { question: null, index: 1, count: 8, percent: 0, busy: false },
  onLoad: function (options) {
    let session = options.resume ? N.read('draft', null) : null;
    try {
      if (!session || session.phase !== 'quiz' || !N.G.question(session)) session = N.G.start(Number(options.count) || 8, N.read('previousFirst', null));
      this.session = session; N.write('previousFirst', session.deck[0].id); N.write('draft', session); this.showQuestion();
    } catch (e) { N.toast(e.message || '测试未能开始'); wx.navigateBack(); }
  },
  showQuestion: function () {
    this.setData({ question: N.G.question(this.session), index: this.session.index + 1, count: this.session.count, percent: Math.round(this.session.index / this.session.count * 100), busy: false });
  },
  answer: function (e) {
    if (this.data.busy) return;
    this.setData({ busy: true });
    try {
      const next = N.G.answer(this.session, e.currentTarget.dataset.question, Number(e.currentTarget.dataset.option));
      this.session = next.session;
      if (next.complete) {
        const result = N.G.result(this.session);
        const record = { session: this.session, teamName: result.teamName, diyIncluded: false, createdAt: Date.now() };
        N.write('latest', record); N.write('history', [record].concat(N.read('history', [])).slice(0, 12)); N.remove('draft');
      } else N.write('draft', this.session);
      this.timer = setTimeout(() => { if (next.complete) wx.redirectTo({ url: '/pages/result/index' }); else this.showQuestion(); }, 180);
    } catch (error) { N.toast(error.message || '请重新点选'); this.setData({ busy: false }); }
  },
  previous: function () {
    if (this.data.busy) return;
    if (!this.session.index) { wx.navigateBack(); return; }
    this.session = N.G.previous(this.session); N.write('draft', this.session); this.showQuestion();
  },
  onUnload: function () { clearTimeout(this.timer); }
});
