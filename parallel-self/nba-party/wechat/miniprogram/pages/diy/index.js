'use strict';
const N = require('../../lib/native');
function formFrom(saved) {
  saved = saved || N.G.diyDefaults();
  return Object.assign({}, saved, { hexName: saved.hexName || (saved.signature && saved.signature.name) || '', hexEffect: saved.hexEffect || (saved.signature && saved.signature.effect) || '' });
}
Page({
  data: { form: {}, dimensions: [], exists: false, colors: ['#634b8a', '#94455e', '#315c7b', '#8a6335'] },
  onLoad: function () { const saved = N.read('diy', null); this.setData({ form: formFrom(saved), dimensions: N.G.dims, exists: !!saved }); },
  input: function (e) { const key = e.currentTarget.dataset.key; const update = {}; update['form.' + key] = e.detail.value; this.setData(update); },
  vector: function (e) { const value = this.data.form.vector.slice(); value[Number(e.currentTarget.dataset.index)] = Number(e.detail.value); this.setData({ 'form.vector': value }); },
  color: function (e) { this.setData({ 'form.avatarColor': e.currentTarget.dataset.color }); },
  save: function () {
    try { const diy = N.G.makeDIY(this.data.form); N.write('diy', diy); this.setData({ exists: true }); N.toast('你的整活球星已存到本机'); }
    catch (e) { N.toast(e.message || '请检查人物设定'); }
  },
  remove: function () {
    wx.showModal({ title: '删除这位DIY球星？', content: '不会删除测试身份。下次可重新创建。', success: (res) => { if (res.confirm) { N.remove('diy'); const latest = N.read('latest', null); if (latest) { latest.diyIncluded = false; N.write('latest', latest); } this.setData({ form: N.G.diyDefaults(), exists: false }); N.toast('DIY球星已删除'); } } });
  },
  back: function () { wx.navigateBack(); }
});
