'use strict';
const N = require('../../lib/native');
const poster = require('../../lib/poster');
Page({
  data: { ready: false, result: null, identity: null, augment: null, team: [], dimensions: [], hasDIY: false, diyIncluded: false, editingTeam: false, peopleNames: [], teamSelection: [], roles: [], posterPath: '', posterBusy: false },
  onShow: function () { this.refresh(); },
  refresh: function () {
    try {
      const loaded = N.loadResult(); if (!loaded) { this.setData({ ready: false }); return; }
      this.result = loaded.result; this.record = loaded.record;
      const auto = N.G.result(loaded.record.session);
      const ids = loaded.record.customIds || auto.team.map(function (p) { return p.id; });
      this.setData({ ready: true, result: loaded.result, identity: N.person(loaded.result.identity), augment: N.card(loaded.result.augment), team: loaded.result.team.map(N.person),
        dimensions: N.G.dims.map(function (label, i) { return { label: label, value: loaded.result.vector[i] }; }),
        hasDIY: !!loaded.diy, diyIncluded: !!loaded.diy && !!loaded.record.diyIncluded,
        peopleNames: N.G.people.map(function (p) { return p.name; }), roles: N.G.roles,
        teamSelection: ids.map(function (id) { return Math.max(0, N.G.people.findIndex(function (p) { return p.id === id; })); })
      });
    } catch (e) { N.toast(e.message || '记录无法重放，请重新测试'); this.setData({ ready: false }); }
  },
  reroll: function () { this.record.teamName = N.G.rerollName(this.result); N.write('latest', this.record); this.refresh(); this.setData({ posterPath: '' }); },
  diy: function () { wx.navigateTo({ url: '/pages/diy/index' }); },
  toggleDIY: function () {
    if (!this.data.hasDIY) { this.diy(); return; }
    this.record.diyIncluded = !this.record.diyIncluded; N.write('latest', this.record); this.refresh(); this.setData({ posterPath: '' });
  },
  editTeam: function () { this.setData({ editingTeam: !this.data.editingTeam }); },
  pickTeam: function (e) { const selected = this.data.teamSelection.slice(); selected[Number(e.currentTarget.dataset.slot)] = Number(e.detail.value); this.setData({ teamSelection: selected }); },
  saveTeam: function () {
    try {
      const ids = this.data.teamSelection.map(function (index) { return N.G.people[index].id; });
      N.G.customTeam(N.G.result(this.record.session), ids);
      this.record.customIds = ids; this.record.diyIncluded = false; N.write('latest', this.record); this.refresh(); this.setData({ editingTeam: false, posterPath: '' }); N.toast('五人阵容已保存');
    } catch (e) { N.toast(e.message || '请选五个不同的人'); }
  },
  resetTeam: function () { delete this.record.customIds; this.record.diyIncluded = false; N.write('latest', this.record); this.refresh(); this.setData({ editingTeam: false, posterPath: '' }); },
  story: function () { wx.navigateTo({ url: '/pages/story/index?from=result' }); },
  restart: function () { wx.navigateTo({ url: '/pages/quiz/index?count=' + this.record.session.count }); },
  home: function () { wx.reLaunch({ url: '/pages/home/index' }); },
  person: function (e) { const pid = e.currentTarget.dataset.pid; if (pid === 'diy-me') this.diy(); else wx.navigateTo({ url: '/pages/people/index?pid=' + encodeURIComponent(pid) }); },
  poster: function () {
    if (this.data.posterBusy || !this.result) return;
    this.setData({ posterBusy: true }); wx.showLoading({ title: '五位队友正在集合' });
    poster.draw(this, this.result).then((path) => { this.setData({ posterPath: path }); wx.pageScrollTo({ selector: '#poster-output', duration: 250 }); }).catch((e) => { N.toast(e.errMsg || e.message || '海报生成失败，请重试'); }).then(() => { wx.hideLoading(); this.setData({ posterBusy: false }); });
  },
  preview: function () { if (this.data.posterPath) wx.previewImage({ urls: [this.data.posterPath], current: this.data.posterPath }); },
  savePoster: function () {
    if (!this.data.posterPath) return;
    wx.saveImageToPhotosAlbum({ filePath: this.data.posterPath, success: function () { N.toast('五人海报已保存到相册'); }, fail: function () { N.toast('图片未保存，可以点预览后手动保存'); } });
  },
  onShareAppMessage: function () { return { title: '整活NBA：来测你的平行球场身份', path: '/pages/home/index' }; }
});
