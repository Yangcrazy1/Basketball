window.NBAPlatform = (function () {
  'use strict';
  var memory = {}, prefix = 'zhenghuo-nba.v1.';
  function read(key, fallback) {
    try { var raw = localStorage.getItem(prefix + key); return raw === null ? fallback : JSON.parse(raw); }
    catch (e) { return Object.prototype.hasOwnProperty.call(memory, key) ? memory[key] : fallback; }
  }
  return { kind: 'web', ready: Promise.resolve(), read: read,
    write: function (key, value) { memory[key] = value; try { localStorage.setItem(prefix + key, JSON.stringify(value)); } catch (e) {} },
    remove: function (key) { delete memory[key]; try { localStorage.removeItem(prefix + key); } catch (e) {} },
    saveImage: function (dataURL) {
      return new Promise(function (resolve, reject) {
        if (!/^data:image\/png;base64,/.test(dataURL)) { reject(new Error('请先生成海报')); return; }
        var a = document.createElement('a'); a.href = dataURL; a.download = '整活NBA-我的五人整活团.png';
        document.body.appendChild(a); a.click(); a.remove(); resolve();
      });
    }
  };
})();
