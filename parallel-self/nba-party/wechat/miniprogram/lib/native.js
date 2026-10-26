'use strict';
const G = require('./game');
const prefix = 'zhenghuoNBA.v1.';
const memory = {};
function read(key, fallback) {
  try {
    const value = wx.getStorageSync(prefix + key);
    if (value !== '' && value !== undefined && value !== null) return value;
  } catch (_) {}
  return Object.prototype.hasOwnProperty.call(memory, key) ? memory[key] : fallback;
}
function write(key, value) {
  memory[key] = value;
  try { wx.setStorageSync(prefix + key, value); } catch (_) {}
}
function remove(key) {
  delete memory[key];
  try { wx.removeStorageSync(prefix + key); } catch (_) {}
}
function path(value) { return value && value.charAt(0) === '/' ? value : value ? '/' + value : ''; }
function person(p) {
  const id = p.personId || p.pid;
  const portrait = G.portraits[id];
  return Object.assign({}, p, {
    personId: id, avatar: portrait ? path(portrait.src) : '',
    displayName: p.nickname || p.name,
    displayLine: p.teamLine || p.line || p.sub || '',
    isDIY: !!p.custom && id === 'diy-me'
  });
}
function card(a) {
  if (!a) return null;
  const art = G.cardArt && G.cardArt[a.id];
  return Object.assign({}, a, { image: art ? path(art.src) : '', displayEffect: a.effect || a.line || '' });
}
function loadResult() {
  const record = read('latest', null);
  if (!record || !record.session) return null;
  let result = G.result(record.session);
  if (record.customIds) result = G.customTeam(result, record.customIds);
  const diy = read('diy', null);
  if (record.diyIncluded && diy) result = G.withDIY(result, diy);
  if (record.teamName) result.teamName = record.teamName;
  return { record: record, result: result, diy: diy };
}
function toast(message) { wx.showToast({ title: String(message).slice(0, 30), icon: 'none', duration: 2400 }); }
module.exports = { G: G, read: read, write: write, remove: remove, path: path, person: person, card: card, loadResult: loadResult, toast: toast };
