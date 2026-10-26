'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const cp = require('node:child_process');
const root = path.resolve(__dirname, '..');
const mini = path.join(root, 'wechat/miniprogram');
const app = JSON.parse(fs.readFileSync(path.join(mini, 'app.json')));
const read = p => fs.readFileSync(p, 'utf8');
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

test('importable native project has six complete routes, local art and no web-view wrapper', () => {
  const project = JSON.parse(read(path.join(root, 'wechat/project.config.json')));
  assert.equal(project.miniprogramRoot, 'miniprogram/');
  assert.equal(project.appid, 'touristappid');
  assert.equal(app.pages.length, 6);
  const expected = new Set(['home', 'quiz', 'result', 'diy', 'people', 'story']);
  for (const route of app.pages) {
    assert(expected.has(route.split('/')[1]));
    for (const ext of ['js', 'json', 'wxml']) assert(fs.existsSync(path.join(mini, route + '.' + ext)), route + '.' + ext);
    const js = read(path.join(mini, route + '.js'));
    const wxml = read(path.join(mini, route + '.wxml'));
    cp.execFileSync(process.execPath, ['--check', path.join(mini, route + '.js')]);
    assert(!/<web-view|<rich-text|https?:\/\//i.test(wxml));
    let page;
    vm.runInNewContext(js, { require: () => ({}), Page: value => { page = value; }, setTimeout, clearTimeout });
    assert(page && page.data);
    const handlers = [...wxml.matchAll(/(?:bind|catch)(?:tap|input|change)="([\w]+)"/g)].map(x => x[1]);
    for (const handler of handlers) assert.equal(typeof page[handler], 'function', route + ' handler ' + handler);
  }
  const manifest = JSON.parse(read(path.join(root, 'wechat/build-manifest.json')));
  assert(manifest.mainPackageUncompressedBytes <= 2 * 1024 ** 2);
  assert.equal(manifest.enabledPeople, 21);
  assert.equal(manifest.activeQuestions, 132);
  assert.equal(manifest.activeCards, 51);
  assert.equal(manifest.pending.length, 4);
  for (const file of ['portraits.json', 'cards-art.json']) {
    const record = JSON.parse(read(path.join(mini, 'lib', file)));
    for (const art of Object.values(record.portraits || record.cards)) {
      assert(!/https?:/.test(art.src));
      assert(fs.existsSync(path.join(mini, art.src)), art.src);
      assert.equal(path.extname(art.src), '.jpg');
    }
  }
  assert(!read(path.join(mini, 'app.json')).includes('requiredPrivateInfos'));
});

function mockWX() {
  const store = {}, calls = [];
  const wx = {
    getStorageSync: key => store[key] === undefined ? '' : JSON.parse(JSON.stringify(store[key])),
    setStorageSync: (key, value) => { store[key] = JSON.parse(JSON.stringify(value)); },
    removeStorageSync: key => { delete store[key]; },
    showToast: value => calls.push(['toast', value.title]),
    navigateTo: value => calls.push(['navigate', value.url]),
    navigateBack: () => calls.push(['back']),
    redirectTo: value => calls.push(['redirect', value.url]),
    reLaunch: value => calls.push(['relaunch', value.url]),
    pageScrollTo: value => calls.push(['scroll', value]),
    showLoading: value => calls.push(['loading', value.title]),
    hideLoading: () => calls.push(['hide-loading']),
    showModal: value => { calls.push(['modal', value.title]); value.success({ confirm: true }); },
    previewImage: value => calls.push(['preview', value]),
    getImageInfo: value => { calls.push(['image', value.src]); value.success({ path: value.src }); },
    canvasToTempFilePath: value => { calls.push(['canvas-export', value.destWidth, value.destHeight, value.fileType]); value.success({ tempFilePath: 'wxfile://test-poster.png' }); },
    saveImageToPhotosAlbum: value => { calls.push(['album', value.filePath]); if (value.success) value.success(); },
    createCanvasContext: id => {
      calls.push(['canvas', id]);
      return new Proxy({}, { get: (_, key) => {
        if (key === 'measureText') return text => ({ width: Array.from(String(text)).length * 9 });
        if (key === 'draw') return (keep, callback) => { calls.push(['draw', keep]); callback(); };
        return () => {};
      } });
    }
  };
  return { wx, store, calls };
}

function loadPage(name) {
  let page;
  const file = path.join(mini, 'pages', name, 'index.js');
  global.Page = value => { page = value; };
  delete require.cache[require.resolve(file)];
  require(file);
  page.data = JSON.parse(JSON.stringify(page.data));
  page.setData = function (values) {
    for (const [key, value] of Object.entries(values)) {
      const names = key.split('.'); let target = this.data;
      for (let i = 0; i < names.length - 1; i++) { if (!target[names[i]]) target[names[i]] = {}; target = target[names[i]]; }
      target[names[names.length - 1]] = value;
    }
  };
  return page;
}

test('native quiz rejects stale double taps, resumes/back-edits and keeps identity through self-selected/DIY teams', async () => {
  const env = mockWX(); global.wx = env.wx;
  const N = require(path.join(mini, 'lib/native.js'));
  const game = N.G;
  const home = loadPage('home'); home.onShow();
  assert.equal(home.data.people, 21); assert.equal(home.data.questions, 132);
  const quiz = loadPage('quiz'); quiz.onLoad({ count: '8' });
  const first = quiz.data.question;
  const event = { currentTarget: { dataset: { question: first.id, option: first.options[0].id } } };
  quiz.answer(event); quiz.answer(event);
  assert.equal(quiz.session.answers.filter(x => x !== null).length, 1);
  assert.equal(quiz.session.index, 1);
  await sleep(200);
  const resumed = loadPage('quiz'); resumed.onLoad({ resume: '1' });
  assert.equal(resumed.session.index, 1);
  resumed.previous(); assert.equal(resumed.session.index, 0);
  assert.equal(resumed.data.question.id, first.id);
  while (resumed.session.phase === 'quiz') {
    const q = resumed.data.question;
    resumed.answer({ currentTarget: { dataset: { question: q.id, option: q.options[1].id } } });
    await sleep(195);
  }
  assert(env.calls.some(x => x[0] === 'redirect' && x[1] === '/pages/result/index'));
  assert.equal(N.read('draft', null), null);
  const record = N.read('latest', null);
  assert.equal(record.session.answers.filter(x => x !== null).length, 8);
  assert.equal(N.read('history', []).length, 1);
  const result = loadPage('result'); result.onShow();
  assert.equal(result.data.ready, true);
  const identity = result.result.identity.personId;
  const score = result.result.identity.match;
  assert.equal(new Set(result.result.team.map(p => p.personId)).size, 5);
  result.setData({ teamSelection: [0, 0, 0, 0, 0] }); result.saveTeam();
  assert.equal(N.read('latest', {}).customIds, undefined);
  assert(env.calls.some(x => x[0] === 'toast' && /重复/.test(x[1])));
  result.setData({ teamSelection: [0, 1, 2, 3, 4] }); result.saveTeam();
  assert.deepEqual(result.result.team.map(p => p.id), game.people.slice(0, 5).map(p => p.id));
  const diy = loadPage('diy'); diy.onLoad();
  diy.setData({ 'form.name': '小区终结者', 'form.number': '77', 'form.hexName': '全场热身', 'form.hexEffect': '先绕球场三圈，再宣布手感来了。' });
  diy.save(); assert.equal(N.read('diy', {}).name, '小区终结者');
  result.onShow(); result.toggleDIY();
  assert.equal(result.result.team.length, 5);
  assert.equal(result.result.team.filter(p => p.personId === 'diy-me').length, 1);
  assert.equal(result.result.identity.personId, identity);
  assert.equal(result.result.identity.match, score);
  assert.equal(new Set(result.result.team.map(p => p.personId)).size, 5);
  assert(!game.people.some(p => p.personId === 'diy-me'));
  assert.equal(env.calls.filter(x => x[0] === 'album').length, 0);
  result.poster(); await sleep(15);
  assert.equal(result.data.posterPath, 'wxfile://test-poster.png');
  assert(env.calls.some(x => x[0] === 'canvas-export' && x[1] === 1080 && x[2] === 1920 && x[3] === 'png'));
  assert.equal(env.calls.filter(x => x[0] === 'album').length, 0);
  result.savePoster(); assert.equal(env.calls.filter(x => x[0] === 'album').length, 1);
  env.wx.saveImageToPhotosAlbum = value => { env.calls.push(['album-denied']); value.fail({ errMsg: 'auth denied' }); };
  result.savePoster(); assert(env.calls.some(x => x[0] === 'toast' && /未保存/.test(x[1])));
  const story = loadPage('story'); story.onLoad({ from: 'result' });
  assert(story.data.view.ownedCardIds.includes(result.result.augment.id));
  for (let i = 0; !story.data.view.isEnding && i < 12; i++) {
    if (story.data.view.choices.length) story.choice({ currentTarget: { dataset: { choice: story.data.view.choices[0].id } } }); else story.next();
    await sleep(230);
  }
  assert.equal(story.data.view.isEnding, true);
  const savedStory = N.read('story', null);
  assert(savedStory && savedStory.origin === record.session.date);
  const storyResume = loadPage('story'); storyResume.onLoad({ from: 'result' });
  assert.equal(storyResume.data.view.text, story.data.view.text);
  diy.remove(); assert.equal(N.read('diy', null), null);
  result.onShow(); assert.equal(result.result.team.some(p => p.personId === 'diy-me'), false);
  assert.equal(result.result.identity.personId, identity);
  assert.equal(result.result.identity.match, score);
});
