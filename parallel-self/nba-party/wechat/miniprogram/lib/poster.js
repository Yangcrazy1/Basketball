'use strict';
const N = require('./native');
function wrap(ctx, text, x, y, maxWidth, lineHeight, maxLines) {
  const chars = Array.from(String(text || '')); let line = '', rows = 0;
  for (let i = 0; i < chars.length; i++) {
    if (ctx.measureText(line + chars[i]).width > maxWidth && line) {
      ctx.fillText(line, x, y); y += lineHeight; rows++;
      if (rows >= maxLines) return y;
      line = chars[i];
    } else line += chars[i];
  }
  if (line && rows < maxLines) { ctx.fillText(line, x, y); y += lineHeight; }
  return y;
}
function font(ctx, size, color) { ctx.setFontSize(size); ctx.setFillStyle(color); }
function imageInfo(src) {
  if (!src) return Promise.resolve(null);
  return new Promise(function (resolve) { wx.getImageInfo({ src: src, success: resolve, fail: function () { resolve(null); } }); });
}
function draw(page, result) {
  const team = result.team.map(N.person), augment = N.card(result.augment);
  return Promise.all(team.map(function (p) { return imageInfo(p.avatar); }).concat([imageInfo(augment.image)])).then(function (images) {
    const ctx = wx.createCanvasContext('posterCanvas', page);
    ctx.setFillStyle('#151024'); ctx.fillRect(0, 0, 540, 960);
    ctx.setStrokeStyle('#c7a0f0'); ctx.setLineWidth(2); ctx.strokeRect(13, 13, 514, 934);
    ctx.save(); ctx.translate(430, 110); ctx.rotate(-0.2); ctx.scale(1, 0.24);
    ctx.setStrokeStyle('#f7ce87'); ctx.setLineWidth(7); ctx.beginPath(); ctx.arc(0, 0, 115, 0, Math.PI * 2); ctx.stroke(); ctx.restore();
    ctx.setFillStyle('#080610'); ctx.beginPath(); ctx.arc(430, 110, 49, 0, Math.PI * 2); ctx.fill();
    ctx.setStrokeStyle('#9771d4'); ctx.setLineWidth(3); ctx.stroke();
    font(ctx, 17, '#d4b5f3'); ctx.fillText('整活NBA / 平行球场五人合照', 32, 47);
    font(ctx, 31, '#ffe1a4'); wrap(ctx, result.teamName.title, 32, 101, 365, 40, 2);
    font(ctx, 13, '#b4a3c8'); ctx.fillText('本轮匹配身份：' + result.identity.name + ' · 原始匹配 ' + result.identity.match + '%', 32, 167);
    const spots = [{ x: 39, y: 199, w: 208 }, { x: 293, y: 199, w: 208 }, { x: 28, y: 474, w: 145 }, { x: 198, y: 474, w: 145 }, { x: 368, y: 474, w: 145 }];
    team.forEach(function (p, i) {
      const s = spots[i], size = s.w - 14;
      ctx.setFillStyle('#2a203a'); ctx.fillRect(s.x - 5, s.y - 5, s.w + 10, s.w + 67);
      ctx.setStrokeStyle(p.isYou ? '#ffdc93' : '#a481cb'); ctx.setLineWidth(p.isYou ? 3 : 1); ctx.strokeRect(s.x - 5, s.y - 5, s.w + 10, s.w + 67);
      if (images[i]) ctx.drawImage(images[i].path, s.x + 7, s.y + 7, size, size);
      else {
        ctx.setFillStyle(p.avatarColor || '#634b8a'); ctx.fillRect(s.x + 7, s.y + 7, size, size);
        ctx.setTextAlign('center'); font(ctx, i < 2 ? 66 : 48, '#fff1ce'); ctx.fillText(p.number || '★', s.x + s.w / 2, s.y + size * 0.65); ctx.setTextAlign('left');
      }
      font(ctx, i < 2 ? 20 : 16, '#fff0dc'); wrap(ctx, p.displayName, s.x + 4, s.y + s.w + 23, s.w - 6, 20, 1);
      font(ctx, 11, '#c7addc'); ctx.fillText((N.G.roles[i] || '自由整活') + (p.isDIY ? ' / DIY' : p.isYou ? ' / 就是我' : ''), s.x + 4, s.y + s.w + 48);
    });
    font(ctx, 18, '#ffe1a4'); wrap(ctx, result.teamName.motto, 32, 729, 475, 26, 2);
    if (images[5]) ctx.drawImage(images[5].path, 32, 784, 68, 68);
    font(ctx, 16, '#dec5f5'); ctx.fillText('本命海克斯 · ' + augment.name, 114, 803);
    font(ctx, 12, '#c1afce'); wrap(ctx, augment.displayEffect, 114, 829, 392, 20, 2);
    font(ctx, 11, '#af99c1'); ctx.fillText('娱乐二创 / 自选队友与DIY不改变原始匹配身份', 32, 899);
    ctx.fillText('换个球场，看看另一个自己。', 32, 920);
    return new Promise(function (resolve, reject) {
      ctx.draw(false, function () {
        wx.canvasToTempFilePath({ canvasId: 'posterCanvas', x: 0, y: 0, width: 540, height: 960, destWidth: 1080, destHeight: 1920, fileType: 'png', success: function (r) { resolve(r.tempFilePath); }, fail: reject }, page);
      });
    });
  });
}
module.exports = { draw: draw };
