window.NBAPlatform = (function () {
  'use strict';
  var values = {}, prefix = 'zhenghuo-nba.v1.', keys = ['draft', 'history', 'diy', 'story', 'count', 'first', 'palette'];
  var mini = window.xhs && window.xhs.miniTool, version = 0, native = false, queue = Promise.resolve();
  function parse(raw, fallback) { try { return raw === null || raw === undefined ? fallback : JSON.parse(raw); } catch (e) { return fallback; } }
  async function initialize() {
    var options = window.xhs && window.xhs.launchOptions;
    if (mini && typeof mini.getLaunchOptions === 'function') { try { options = await mini.getLaunchOptions(); } catch (e) {} }
    version = Math.floor((Number(options && options.miniToolEnv && options.miniToolEnv.buildVersion) || 0) / 1000);
    native = version >= 9460 && mini && typeof mini.getStorage === 'function' && typeof mini.setStorage === 'function';
    for (var i = 0; i < keys.length; i++) {
      if (native) { try { var res = await mini.getStorage({ key: prefix + keys[i] }); values[keys[i]] = parse(res && res.data, null); } catch (e) {} }
    }
    if (version >= 9490 && mini && typeof mini.getWindowInfo === 'function') {
      try {
        var info = await mini.getWindowInfo(), safe = info.safeArea, top = safe ? Math.max(0, safe.top) : 0;
        var buttons = info.menuButtons || {};
        ['back', 'me', 'share'].forEach(function (key) { if (buttons[key]) top = Math.max(top, buttons[key].bottom + 6); });
        document.documentElement.style.setProperty('--safe-area-inset-top', top + 'px');
        if (safe) document.documentElement.style.setProperty('--safe-area-inset-bottom', Math.max(0, info.windowHeight - safe.bottom) + 'px');
      } catch (e) {}
    }
  }
  function enqueue(operation) { queue = queue.then(operation).catch(function () {}); }
  return { kind: 'xhs', ready: initialize(),
    read: function (key, fallback) { var v = values[key]; return v === null || v === undefined ? fallback : v; },
    write: function (key, value) { values[key] = value; if (native) enqueue(function () { return mini.setStorage({ key: prefix + key, data: JSON.stringify(value) }); }); },
    remove: function (key) { delete values[key]; if (native && typeof mini.removeStorage === 'function') enqueue(function () { return mini.removeStorage({ key: prefix + key }); }); },
    saveImage: async function (dataURL) {
      if (!mini || typeof mini.writeTempFile !== 'function' || typeof mini.saveImageToPhotosAlbum !== 'function') throw new Error('请在支持存相册的小红书小工具中保存海报');
      if (!/^data:image\/png;base64,/.test(dataURL)) throw new Error('请先生成海报');
      var file = await mini.writeTempFile({ data: dataURL });
      if (!file || !file.filePath) throw new Error('海报暂存失败，请重试');
      await mini.saveImageToPhotosAlbum({ filePath: file.filePath });
    }
  };
})();
