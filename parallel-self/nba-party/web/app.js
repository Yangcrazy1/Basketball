(function () {
  'use strict';
  var G = window.NBAGame, P = window.NBAPlatform;
  var app = document.getElementById('app'), dialog = document.getElementById('dialog');
  var roles = ['控卫', '分卫', '小前锋', '大前锋', '中锋'];
  var state = { count: 8, session: null, record: null, story: null, storyRecord: null, query: '', busy: false, timer: null, toastTimer: null, posterURL: null, focusReturn: null };
  var colors = ['#9d7cff', '#c76642', '#4967a7', '#a54b72', '#567d69', '#a17a35'];
  function esc(value) { return String(value === null || value === undefined ? '' : value).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function copy(value) { return JSON.parse(JSON.stringify(value)); }
  function read(key, fallback) { try { return P.read(key, fallback); } catch (_) { return fallback; } }
  function write(key, value) { try { P.write(key, value); } catch (_) { toast('本次内容仍可体验，当前环境未保存到本机。'); } }
  function remove(key) { try { P.remove(key); } catch (_) {} }
  function historyRows() { var rows = read('history', []); return Array.isArray(rows) ? rows.slice(0, 12) : []; }
  function people() { return G.people || []; }
  function person(value) { return G.person ? G.person(value) : people().find(function (p) { return p.id === value || p.personId === value; }); }
  function card(id) { return (G.cards || []).find(function (c) { return c.id === id; }); }
  function personName(p) { return p.nickname || p.name; }
  function toast(text) { var node = document.getElementById('toast'); node.textContent = text; node.classList.add('visible'); clearTimeout(state.toastTimer); state.toastTimer = setTimeout(function () { node.classList.remove('visible'); }, 3000); }
  function saveRecord(record) { write('history', [record].concat(historyRows().filter(function (r) { return r.id !== record.id; })).slice(0, 12)); }
  function route(view) { closeDialog(); clearTimeout(state.timer); state.busy = false; var hash = '#' + view; if (location.hash === hash) renderRoute(); else location.hash = hash; }
  function render(html, active) {
    clearTimeout(state.timer); state.busy = false; closeDialog(); app.innerHTML = html;
    document.querySelectorAll('[data-nav]').forEach(function (b) { b.setAttribute('aria-current', b.dataset.nav === active ? 'page' : 'false'); });
    document.body.classList.toggle('quiz-mode', active === 'quiz');
    document.documentElement.dataset.appReady = 'true';
    window.scrollTo(0, 0);
  }
  function portrait(p, extra) {
    if (p.personId === 'diy-me') return '<span class="portrait diy-jersey ' + esc(extra || '') + '" data-avatar="diy-me" role="img" aria-label="DIY球星球衣头像" style="background:' + esc(colors.includes(p.avatarColor) ? p.avatarColor : colors[0]) + '"><span class="jersey-number">' + esc(p.number === undefined ? '00' : p.number) + '</span></span>';
    var meta = G.portraits && G.portraits[p.personId], src = meta && meta.src;
    return '<span class="portrait ' + esc(extra || '') + '" data-avatar="' + esc(p.personId) + '"><span class="fallback-initial" aria-hidden="true">' + esc(p.name.slice(0, 2)) + '</span>' + (src ? '<img src="' + esc(src) + '" alt="' + esc(p.name) + '漫画头像" loading="lazy">' : '') + '</span>';
  }
  function art(c) { var image = G.cardArt && G.cardArt[c.id]; return '<div class="hex-art"><span aria-hidden="true">✦</span>' + (image && image.src ? '<img src="' + esc(image.src) + '" alt="' + esc(c.name) + '漫画图标" loading="lazy">' : '') + '</div>'; }
  function hex(c, compact) {
    return '<article class="hex-card ' + (compact ? 'compact' : '') + '" data-card="' + esc(c.id) + '"><small>' + (compact ? '宇宙整活补给' : '你的本命整活海克斯') + '</small>' + art(c) + '<h2>' + esc(c.name) + '</h2><div class="hex-divider" aria-hidden="true">— ✦ —</div><p class="hex-effect">' + esc(c.effect || c.line || '').replace(/\n/g, '<br>') + '</p><p class="hex-punchline">' + esc(c.punchline || c.line || '') + '</p></article>';
  }
  function begin() {
    var old = read('previousFirst', null);
    state.session = G.start(state.count, old); write('previousFirst', state.session.deck[0].id); write('draft', state.session); route('quiz');
  }
  function home() {
    var draft = read('draft', null), hasDraft = draft && draft.phase === 'quiz' && Array.isArray(draft.answers), diy = read('diy', null);
    var featured = ['lebron', 'curry', 'xujingyu', 'caixukun'].map(person).filter(Boolean);
    if (featured.length < 4) featured = people().slice(0, 4);
    var headline = person('lebron') || people()[0];
    render('<section class="page home-page"><div class="home-topline"><span><i class="live-dot"></i>平行球场信号已接通</span><span>娱乐测试 / 本地保存</span></div><div class="hero"><div class="hero-copy"><span class="eyebrow">ANOTHER YOU · ANOTHER COURT</span><h1>换个宇宙，<em>你是哪位球星？</em></h1><p>球场上有大腿，也有节目效果。<br>凭第一反应接几个梗，看看你的另一种人生。</p><div class="hero-tags"><span class="pill">' + people().length + ' 位平行身份</span><span class="pill">随机球场情境</span><span class="pill gold">五人整活梦之队</span></div><section class="test-console" aria-label="选择测试长度"><div class="console-heading"><h2>这次，测多细？</h2><small>没有标准答案</small></div><div class="mode-picker" role="group" aria-label="选择题量">' + [8, 16, 24].map(function (n, i) { return '<button data-action="mode" data-count="' + n + '" aria-pressed="' + (state.count === n) + '"><b>' + n + '<small>题</small></b><span>' + ['先整一把', '多点细节', '深度整活'][i] + '</span></button>'; }).join('') + '</div><button class="primary start-cta" data-action="start">开始我的平行球场 <span aria-hidden="true">→</span></button><p class="console-note">点选即下一题 · 每局随机 · 随时返回改选</p>' + (hasDraft ? '<button class="resume-button" data-action="resume">继续上次测试 · 已答 ' + draft.answers.filter(function (a) { return a !== null; }).length + '/' + draft.count + ' →</button>' : '') + '</section></div><div class="cosmic-frame"><img src="./assets/cosmic-court.webp" alt="穿过紫金宇宙隧道，走进另一座篮球场"><div class="floating-card">' + portrait(headline) + '<b>下一位登场的，也许是你。</b></div><div class="cosmic-caption"><strong>另一个宇宙，<br>剧本由你接着写。</strong><small>球星身份 × 专属海克斯 × 五人合照</small></div></div></div><ol class="home-steps"><li><i>01</i>接几个球场梗</li><li><i>02</i>解锁你的身份</li><li><i>03</i>组个离谱五人团</li></ol><div class="section-top"><h2>这座球馆，可能遇见</h2><button class="text-button" data-action="people">全部人物 ↗</button></div><div class="home-portraits">' + featured.map(function (p) { return '<button class="polaroid" data-action="person" data-person="' + esc(p.personId) + '">' + portrait(p) + '<strong>' + esc(personName(p)) + '</strong><small>' + esc((p.tags || []).slice(0, 2).join(' / ') || p.sub) + '</small></button>'; }).join('') + '</div><div class="home-sidecards"><button data-action="diy"><span class="side-icon" aria-hidden="true">✦</span><strong>' + (diy ? '我的DIY球星' : '我也能捏一个球星') + '</strong><small>' + (diy ? esc(diy.name) + '，随时换个人设。' : '名字、球衣、离谱能力，自己安排。') + '</small></button><button data-action="cards"><span class="side-icon" aria-hidden="true">◈</span><strong>海克斯补给站</strong><small>' + (G.cards || []).length + ' 张整活能力，看看谁和你最配。</small></button></div><p class="tiny center">本作是篮球热梗与平行人生的娱乐二创，不代表人物本人言论或背书。<br>答案与DIY资料只保存在本机，无登录、无上传。</p></section>', 'home');
  }
  function quiz() {
    var s = state.session || read('draft', null);
    if (!s || s.phase !== 'quiz') { route('home'); return; }
    state.session = s;
    var q;
    try { q = G.question(s); } catch (_) { remove('draft'); toast('上次的草稿不适用于当前题库，请重新开始。'); route('home'); return; }
    if (!q) { route('home'); return; }
    render('<section class="page question-page"><div class="quiz-top"><button class="back-link" data-action="leave-quiz">← 先存一下</button><span>球场信号 ' + (s.index + 1) + ' / ' + s.count + '</span></div><progress class="quiz-progress" max="' + s.count + '" value="' + s.answers.filter(function (a) { return a !== null; }).length + '" aria-label="已完成题数"></progress><article class="question-card" data-question="' + esc(q.id) + '"><div class="scene-number"><span>' + esc(q.scene || '球场日常') + '</span><b>SCENE / ' + String(s.index + 1).padStart(2, '0') + '</b></div><h1>' + esc(q.title) + '</h1><div class="options">' + q.options.map(function (o, i) { return '<button class="option" data-action="answer" data-question="' + esc(q.id) + '" data-id="' + o.id + '" aria-pressed="' + (s.answers[s.index] === o.id) + '"><i aria-hidden="true">' + 'ABCD'[i] + '</i><span>' + esc(o.text) + '</span></button>'; }).join('') + '</div><p class="question-status" id="answer-status" aria-live="polite">按你的第一反应选，选中后自动进入下一题。</p></article><div class="quiz-bottom"><button class="back-link" data-action="previous" ' + (s.index === 0 ? 'disabled' : '') + '>← 上一题</button><span class="micro">你不必懂战术板，<br>只要知道自己会怎么做。</span></div></section>', 'quiz');
  }
  function answer(button) {
    if (state.busy || !state.session) return;
    var step;
    try { step = G.answer(state.session, button.dataset.question, Number(button.dataset.id)); } catch (e) { toast(e.message || '这题已经切换，请重新选择。'); return; }
    state.busy = true; state.session = step.session; write('draft', state.session);
    app.querySelectorAll('.option').forEach(function (b) { b.disabled = true; b.setAttribute('aria-pressed', String(b === button)); });
    var prev = app.querySelector('[data-action=previous]'); if (prev) prev.disabled = true;
    document.getElementById('answer-status').textContent = step.complete ? '信号已集齐，正在揭晓你的平行身份…' : '已接梗，进入下一题…';
    state.timer = setTimeout(function () {
      state.busy = false;
      if (step.complete) finish(); else quiz();
    }, 220);
  }
  function finish() {
    var result;
    try { result = G.result(state.session); } catch (e) { toast(e.message || '这局未能完成，请返回继续作答。'); quiz(); return; }
    var record = { id: Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 7), date: new Date().toISOString(), session: copy(state.session), teamName: copy(result.teamName) };
    saveRecord(record); remove('draft'); state.record = record;
    route('result/' + record.id);
  }
  function resultFor(record) {
    var r = G.result(record.session);
    if (record.customIds) r = G.customTeam(r, record.customIds);
    if (record.diySnapshot) r = G.withDIY(r, record.diySnapshot);
    if (record.teamName) r.teamName = copy(record.teamName);
    if (record.storyState) {
      try { var view = G.storyView(record.storyState); r.obtainedCards = view.ownedCardIds.map(card).filter(Boolean); if (view.isEnding) r.story = [view.title, view.text, '这一条时间线由你的选择完成。']; } catch (_) {}
    }
    return r;
  }
  function resultPage(id) {
    var record = historyRows().find(function (r) { return r.id === id; });
    if (!record) { toast('这条本机记录已不存在。'); route('archive'); return; }
    state.record = record;
    var r;
    try { r = resultFor(record); } catch (_) { toast('这条记录不适用于当前版本，请开启一局新测试。'); route('archive'); return; }
    var p = r.identity, a = r.augment, own = r.obtainedCards || [a], name = r.teamName || { title: '今天五个人都很会整活', motto: '比赛有输赢，节目不能停。' };
    var story = r.story || [], raw = p.rawMatch === undefined ? p.match : p.rawMatch;
    render('<section class="page result-page" data-result-person="' + esc(p.personId) + '"><div class="result-top"><span>穿越完成 / ' + record.session.count + ' 个真实反应</span><button class="text-button" data-action="archive">我的宇宙 ↗</button></div><article class="identity-card"><div class="identity-copy"><span class="eyebrow">在这个宇宙，你成为了</span><h1>' + esc(personName(p)) + '</h1><p class="identity-line">' + esc(p.sub || p.line) + '</p><div class="identity-tags"><span class="pill gold">原始匹配 ' + raw + '%</span><span class="pill">' + esc(r.profile && r.profile.name || '平行球场主角') + '</span>' + (p.tags || []).slice(0, 3).map(function (s) { return '<span class="pill">' + esc(s) + '</span>'; }).join('') + '</div><button class="text-button" data-action="person" data-person="' + esc(p.personId) + '">查看这位主角的设定 ↗</button></div><div class="identity-photo">' + portrait(p) + '<small>PARALLEL IDENTITY / 就是你</small></div></article><p class="result-summary">' + esc(p.line || p.universe && p.universe.passive || '') + '</p><div class="result-two-cols">' + hex(a, false) + '<section class="story-preview"><span class="eyebrow">我的平行人生 / 架空剧情</span><h2>' + esc(story[0] || p.name + '，这次由你上场。') + '</h2><p>' + esc(story[1] || p.universe && p.universe.arrival || '') + '</p><button class="primary" data-action="story-result">' + (record.storyState ? '继续我的平行人生' : '走进六幕平行人生') + ' →</button><p class="micro">你的选择会改变后续故事。只有真正获得的卡，才会在故事中发动。</p></section></div><div class="section-top"><h2>五个人，各有各的离谱。</h2><span>' + (record.customIds || record.diySnapshot ? '自选阵容' : '你 ＋ 四名匹配队友') + '</span></div><section class="team-brand"><small>PARALLEL FIVE / 临时队名也是队名</small><h3 data-team-name>' + esc(name.title) + '</h3><p>' + esc(name.motto) + '</p><button class="text-button" data-action="reroll-name">这名字还不够离谱，换一个 ↻</button></section><div class="button-row"><button class="secondary" data-action="edit-team">自选这五个人 ↗</button>' + (record.customIds ? '<button class="text-button" data-action="reset-team">恢复匹配阵容</button>' : '') + '<button class="text-button" data-action="toggle-diy">' + (record.diySnapshot ? '移出DIY队友' : read('diy', null) ? '让我的DIY球星入队 ＋' : '去DIY一个队友 ＋') + '</button></div>' + (record.diySnapshot ? '<p class="diy-team-note">自选队友「' + esc(record.diySnapshot.name) + '」已入队。测试匹配到的身份、分数和答案没有改变。</p>' : '') + '<div class="team-grid">' + r.team.map(function (m, i) { return '<article class="team-card ' + (m.isYou ? 'is-you' : '') + '" data-person="' + esc(m.personId) + '"><small>' + roles[i] + ' / ' + (m.isYou ? '就是你' : m.personId === 'diy-me' ? 'DIY整活' : 'TEAM ' + (i + 1)) + '</small>' + portrait(m) + '<h4>' + esc(personName(m)) + '</h4><p>' + esc(m.line || m.teamLine || '') + '</p></article>'; }).join('') + '</div><details class="result-details"><summary>展开六维面板与真实答题依据 ＋</summary><div class="dimensions">' + (G.dims || []).map(function (name, i) { return '<div class="dimension"><span>' + esc(name) + '</span><i><b style="width:' + Math.max(0, Math.min(100, r.vector[i])) + '%"></b></i><strong>' + r.vector[i] + '</strong></div>'; }).join('') + '</div><p class="micro">本轮反应的娱乐刻度，不是心理诊断，也不是对现实球星的客观评分。原始匹配分按实际答案计算。</p><div class="evidence-list">' + (r.evidence || []).slice(0, 6).map(function (e) { return '<article class="evidence-item"><small>' + esc(e.scene || e.title) + '</small><p>你选了「' + esc(e.choice) + '」</p></article>'; }).join('') + '</div><button class="text-button" data-action="review-answers">回看这一局的全部答案 →</button></details><section class="panel"><span class="eyebrow">我的本局能力背包</span><div class="person-tags">' + own.map(function (c) { return '<button class="pill" data-action="card" data-card="' + esc(c.id) + '" data-owned-card="' + esc(c.id) + '">' + esc(c.name) + ' ↗</button>'; }).join('') + '</div><p class="micro">图鉴里看到的卡不等于已获得。这里仅记录本轮匹配和故事明确奖励的能力。</p></section><div class="result-actions"><button class="primary" data-action="team-poster">生成五人合照海报 ↗</button><button class="secondary" data-action="start">再整一局</button></div><p class="tiny center">人物、能力和剧情为本作娱乐二创，不代表本人发言或背书。</p></section>', 'home');
  }
  function rerenderResult() { if (state.record) resultPage(state.record.id); }
  function setTeam() {
    if (!state.record) return;
    var r = G.result(state.record.session);
    if (state.record.customIds) r = G.customTeam(r, state.record.customIds);
    openDialog('五个位置，你来安排', '<p class="micro">自由整活可以跨位置，五个人不能重复。保存后使用这五位官方人物；DIY队友可随后再邀请入队。测试身份和分数不变。</p><form id="team-form"><div class="team-selects">' + roles.map(function (role, i) { return '<label>' + esc(role) + '<select name="slot' + i + '" aria-label="选择' + esc(role) + '">' + people().map(function (p) { return '<option value="' + esc(p.id) + '" ' + (r.team[i].id === p.id ? 'selected' : '') + '>' + esc(p.name) + '</option>'; }).join('') + '</select></label>'; }).join('') + '</div><p class="form-error" id="team-error" role="alert"></p><button class="primary full" type="submit">这五个人，到齐了</button></form>');
  }
  function saveTeam(form) {
    var ids = roles.map(function (_, i) { return form.elements['slot' + i].value; });
    try { G.customTeam(G.result(state.record.session), ids); state.record.customIds = ids; delete state.record.diySnapshot; saveRecord(state.record); closeDialog(); rerenderResult(); toast('阵容已保存，原始匹配身份不变。'); }
    catch (e) { document.getElementById('team-error').textContent = e.message || '请选齐五位不同的球星。'; }
  }
  function toggleDIY() {
    if (!state.record) return;
    if (state.record.diySnapshot) { delete state.record.diySnapshot; saveRecord(state.record); rerenderResult(); toast('已恢复这名匹配队友。'); return; }
    var diy = read('diy', null); if (!diy) { route('diy'); return; }
    try { state.record.diySnapshot = G.makeDIY(diy); saveRecord(state.record); rerenderResult(); toast('DIY球星已加入自选阵容，测试身份不变。'); }
    catch (_) { route('diy'); }
  }
  function diyForm() {
    var stored = read('diy', null), value = stored || G.diyDefaults(), sig = value.signature || { name: value.hexName || '', effect: value.hexEffect || '' };
    var vector = value.vector || [50, 50, 50, 50, 50, 50];
    render('<section class="page diy-page"><button class="back-link" data-action="home">← 回到宇宙大厅</button><span class="eyebrow full">DIY PLAYER LAB / 自建整活球星</span><h1 class="page-title">现实没这号人？<br>那就自己捏一个。</h1><p class="page-subtitle">给自己一个球场人设，再带进五人合照。<br>DIY是自选队友，不会混进默认测试身份池。</p><div class="diy-layout"><aside class="diy-preview"><span class="portrait diy-jersey" id="diy-preview-avatar" style="background:' + esc(colors.includes(value.avatarColor) ? value.avatarColor : colors[0]) + '"><span class="jersey-number" id="diy-preview-number">' + esc(value.number === undefined ? '00' : value.number) + '</span></span><h2 id="diy-preview-name">' + esc(value.name || '宇宙第六人') + '</h2><p id="diy-preview-line">' + esc(value.line || '球可以不进，姿势必须像样。') + '</p><p class="tiny">原创自建球星 / 不是官方人物</p></aside><form class="diy-form" id="diy-form"><div class="field-row"><label class="field"><span>球星名字</span><input name="name" maxlength="12" required value="' + esc(value.name || '') + '" placeholder="例：篮筐体检主任"><small>1–12个字，别让队友念不完。</small></label><label class="field"><span>球衣号码</span><input name="number" type="number" min="0" max="99" inputmode="numeric" required value="' + esc(value.number === undefined ? 6 : value.number) + '"><small>0–99号</small></label></div><label class="field"><span>出场口头禅</span><input name="line" maxlength="40" value="' + esc(value.line || '') + '" placeholder="球可以不进，姿势必须像样。"><small>最多40个字，会印在你的球星卡上。</small></label><div class="field"><span>球衣主色</span><div class="color-picker">' + colors.map(function (c, i) { return '<label><input type="radio" name="avatarColor" value="' + c + '" ' + (c === value.avatarColor || !value.avatarColor && i === 0 ? 'checked' : '') + ' aria-label="球衣配色' + (i + 1) + '"><span style="background:' + c + '"></span></label>'; }).join('') + '</div></div><label class="field"><span>专属海克斯名字</span><input name="hexName" maxlength="12" value="' + esc(sig.name || '') + '" placeholder="例：篮板自助取号"><small>最多12个字，原创整活能力。</small></label><label class="field"><span>这张海克斯会发生什么？</span><textarea name="hexEffect" maxlength="60" placeholder="例：篮板还没落地，你的庆祝动作已经准备完毕。">' + esc(sig.effect || '') + '</textarea><small>最多60个字，只在DIY球星卡和合照显示。</small></label><div class="section-top"><h2>六维人设，自己安排</h2><span>不是专业能力评分</span></div>' + (G.dims || []).map(function (dim, i) { return '<label class="range-field"><span>' + esc(dim) + '</span><input type="range" name="dim' + i + '" min="0" max="100" step="1" value="' + vector[i] + '"><output data-range="dim' + i + '">' + vector[i] + '</output></label>'; }).join('') + '<p class="form-error" id="diy-error" role="alert"></p><button class="primary full" type="submit">' + (stored ? '更新我的DIY球星' : '这位整活球星，正式出道') + ' →</button><div class="button-row"><button class="text-button" type="button" data-action="random-diy">给我一个离谱灵感 ↻</button>' + (stored ? '<button class="text-button" type="button" data-action="delete-diy">删除本机DIY球星</button>' : '') + '</div></form></div><p class="tiny center">资料只在本机保存，不上传照片、姓名或其他个人信息。<br>修改DIY不会自动改写已保存合照的队友快照。</p></section>', 'diy');
  }
  function diyInput(form) {
    var out = { name: form.elements.name.value, number: form.elements.number.value, line: form.elements.line.value, hexName: form.elements.hexName.value, hexEffect: form.elements.hexEffect.value, avatarColor: form.elements.avatarColor.value, vector: [] };
    for (var i = 0; i < 6; i++) out.vector.push(Number(form.elements['dim' + i].value));
    return out;
  }
  function saveDIY(form) {
    try { var value = G.makeDIY(diyInput(form)); write('diy', value); diyForm(); toast('DIY球星已保存，可以在测试结果里邀请入队。'); }
    catch (e) { document.getElementById('diy-error').textContent = e.message || '请检查球星名字和能力设置。'; }
  }
  function randomDIY() {
    var form = document.getElementById('diy-form');
    var names = ['篮筐体检主任', '停车场投篮员', '全场暂停申请人', '篮板临时保管员', '第五节嘴硬王', '回防导航失灵'];
    var lines = ['球可以不进，镜头必须给到。', '传球不是甩锅，是共享项目。', '刚才那球，主要怪宇宙风太大。', '我先庆祝，篮筐稍后确认。'];
    form.elements.name.value = names[Math.floor(Math.random() * names.length)]; form.elements.number.value = Math.floor(Math.random() * 100);
    form.elements.line.value = lines[Math.floor(Math.random() * lines.length)]; form.elements.hexName.value = '自带赛后发布会'; form.elements.hexEffect.value = '每次打铁后，自动把队友拉进一分钟的技术复盘。';
    form.elements.avatarColor.value = colors[Math.floor(Math.random() * colors.length)];
    for (var i = 0; i < 6; i++) { form.elements['dim' + i].value = Math.floor(Math.random() * 21) * 5; }
    updateDIYPreview(form); toast('灵感到了，再按你的口味改一改。');
  }
  function updateDIYPreview(form) {
    var value = diyInput(form);
    document.getElementById('diy-preview-name').textContent = value.name || '宇宙第六人'; document.getElementById('diy-preview-line').textContent = value.line || '球可以不进，姿势必须像样。'; document.getElementById('diy-preview-number').textContent = value.number || '0'; document.getElementById('diy-preview-avatar').style.background = colors.includes(value.avatarColor) ? value.avatarColor : colors[0];
    for (var i = 0; i < 6; i++) { var output = form.querySelector('[data-range=dim' + i + ']'); if (output) output.textContent = value.vector[i]; }
  }
  function gallery() {
    render('<section class="page library-page"><span class="eyebrow">PARALLEL ROSTER / 这里全是另一种人生</span><h1 class="page-title">球星与节目效果，<br>都已到场。</h1><p class="page-subtitle">球员、解说和跨界整活各有自己的设定。<br>人物故事为架空二创，不代表真实赛史或本人言论。</p><input class="library-search" id="people-search" type="search" placeholder="搜名字、别名或熟悉的梗" aria-label="搜索球星"><p class="micro" id="people-count"></p><div class="people-grid" id="people-grid"></div></section>', 'people');
    var search = document.getElementById('people-search'); search.value = state.query; filterPeople();
  }
  function filterPeople() {
    var query = state.query.trim().toLowerCase();
    var list = people().filter(function (p) { return [p.name, p.nickname, p.sub].concat(p.tags || [], p.aliases || []).join(' ').toLowerCase().includes(query); });
    document.getElementById('people-count').textContent = '找到 ' + list.length + ' 位 / 全部 ' + people().length + ' 位';
    document.getElementById('people-grid').innerHTML = list.map(function (p) { return '<button class="person-tile" data-action="person" data-person="' + esc(p.personId) + '">' + portrait(p) + '<strong>' + esc(personName(p)) + '</strong><small>' + esc(p.sub || (p.tags || []).slice(0, 2).join(' / ')) + '</small></button>'; }).join('') || '<p class="micro">还没搜到这位，换个名字试试。</p>';
  }
  function personPage(pid) {
    var p = person(pid); if (!p) { route('people'); return; }
    var cards = (p.signaturePerks || []).map(card).filter(Boolean), u = p.universe;
    render('<section class="page narrow person-page" data-person="' + esc(p.personId) + '"><button class="back-link" data-action="people">← 回到球星图鉴</button><article class="person-hero">' + portrait(p) + '<div><span class="eyebrow">PARALLEL PLAYER / 本作架空人设</span><h1>' + esc(personName(p)) + '</h1><p>' + esc(p.sub || '') + '</p><div class="person-tags">' + (p.tags || []).slice(0, 6).map(function (t) { return '<span class="pill">' + esc(t) + '</span>'; }).join('') + '</div></div></article>' + (u ? '<section class="person-setting"><h3>' + esc(u.title || '另一种平行人生') + '</h3><p>' + esc(u.arrival || '') + '</p><p>' + esc(u.mission || '') + '</p><p>' + esc(u.passive || '') + '</p></section>' : '') + '<div class="section-top"><h2>属于TA的整活能力</h2><span>图鉴展示 / 尚未获得</span></div><div class="cards-grid">' + cards.map(function (c) { return '<button class="card-open" data-action="card" data-card="' + esc(c.id) + '" aria-label="查看' + esc(c.name) + '">' + hex(c, true) + '</button>'; }).join('') + '</div><button class="secondary full" data-action="story-preview" data-person="' + esc(p.personId) + '">先看TA的六幕平行人生 →</button><p class="tiny center">预览故事从零张卡开始，不会冒充你的测试结果。</p></section>', 'people');
  }
  function cardsPage() {
    render('<section class="page cards-page"><button class="back-link" data-action="home">← 回到宇宙大厅</button><span class="eyebrow full">HEX SUPPLY / 宇宙补给站</span><h1 class="page-title">这能力，<br>不能说没有用。</h1><p class="page-subtitle">' + G.cards.length + ' 张原创整活海克斯。实际获得哪张，由整局答案决定。</p><div class="cards-grid">' + G.cards.map(function (c) { return '<button class="card-open" data-action="card" data-card="' + esc(c.id) + '" aria-label="查看' + esc(c.name) + '">' + hex(c, true) + '</button>'; }).join('') + '</div></section>', 'people');
  }
  function archive() {
    var rows = historyRows(), shown = [];
    rows.forEach(function (record) { try { var r = resultFor(record); shown.push({ record: record, result: r }); } catch (_) {} });
    render('<section class="page narrow archive-page"><span class="eyebrow">MY PARALLEL UNIVERSES / 我的宇宙</span><h1 class="page-title">你上过场的宇宙，<br>这里都记得。</h1><p class="page-subtitle">只在本机保留最近12次测试。每局身份、答案和自选阵容分别保存。</p>' + (shown.length ? '<div class="history-list">' + shown.map(function (row) { var p = row.result.identity, date; try { date = new Date(row.record.date).toLocaleDateString('zh-CN'); } catch (_) { date = '本机记录'; } return '<button class="history-card" data-action="history" data-record="' + esc(row.record.id) + '">' + portrait(p) + '<span><strong>' + esc(personName(p)) + '</strong><small>' + esc(date) + ' · ' + row.record.session.count + '题<br>' + esc(row.record.teamName && row.record.teamName.title || '五个人已到场') + '</small></span><i class="arrow" aria-hidden="true">↗</i></button>'; }).join('') + '</div>' : '<section class="empty-state"><span class="empty-icon" aria-hidden="true">◌</span><h2>平行球场，还在等你。</h2><p>先接几个梗，第一条时间线马上出现。</p><button class="primary" data-action="start">开始一局娱乐测试 →</button></section>') + '<div class="button-row"><button class="secondary" data-action="diy">看看我的DIY球星</button>' + (shown.length ? '<button class="text-button" data-action="clear-history">清除本机测试记录</button>' : '') + '</div></section>', 'home');
  }
  function storyBegin(pid, record) {
    try {
      state.storyRecord = record || null;
      state.story = record && record.storyState ? copy(record.storyState) : G.storyStart(pid, record ? [resultFor(record).augment.id] : []);
      persistStory(); route('story');
    } catch (e) { toast(e.message || '这位主角的故事暂时无法打开。'); }
  }
  function persistStory() {
    write('story', { state: state.story, recordId: state.storyRecord && state.storyRecord.id || null });
    if (state.storyRecord) { state.storyRecord.storyState = copy(state.story); saveRecord(state.storyRecord); }
  }
  function storyPage() {
    if (!state.story) {
      var saved = read('story', null);
      if (saved && saved.state) { state.story = saved.state; state.storyRecord = saved.recordId && historyRows().find(function (r) { return r.id === saved.recordId; }) || null; }
    }
    var v;
    try { v = G.storyView(state.story); } catch (_) { remove('story'); route('home'); return; }
    var p = person(state.story.personId); if (!p) { route('home'); return; }
    render('<section class="page story-page" data-story-person="' + esc(p.personId) + '" data-story-node="' + esc(v.node) + '"><div class="story-top"><button class="back-link" data-action="story-exit">← ' + (state.storyRecord ? '返回我的身份' : '返回球星图鉴') + '</button><span>' + v.progress.current + ' / ' + v.progress.total + ' 幕</span></div><div class="story-identity">' + portrait(p) + '<div><small>' + esc(p.name) + '的平行人生</small><h2>' + esc(v.storyTitle || p.universe && p.universe.title || '另一种球场结局') + '</h2></div></div><div class="story-steps" aria-label="故事进度">' + Array.from({ length: v.progress.total }, function (_, i) { return '<i class="' + (i < v.progress.current ? 'on' : '') + '"></i>'; }).join('') + '</div><article class="story-sheet"><span class="eyebrow">' + (v.isEnding ? '这条时间线的结局' : '第 ' + v.progress.current + ' 幕') + '</span><h1>' + esc(v.title) + '</h1><p class="story-text">' + esc(v.text) + '</p>' + (v.cardEvents || []).map(function (event) { return event.owned ? '<aside class="story-event" data-trigger-card="' + esc(event.cardId) + '"><small>' + esc(card(event.cardId) && card(event.cardId).name || '已获能力') + ' / 发动</small><p>' + esc(event.text) + '</p></aside>' : '<p class="micro">' + esc(event.text) + '</p>'; }).join('') + '<div class="story-choices">' + (v.choices || []).map(function (choice) { return '<button class="story-choice" data-action="story-choice" data-node="' + esc(v.node) + '" data-choice="' + esc(choice.id) + '"><span>' + esc(choice.text) + '</span><b aria-hidden="true">→</b></button>'; }).join('') + '</div>' + (v.isEnding ? '<div class="button-row"><button class="primary full" data-action="story-poster">把这条人生存成海报 ↗</button><button class="secondary full" data-action="story-restart">换个选择，再走一次</button></div>' : !(v.choices || []).length ? '<button class="primary full story-next" data-action="story-next">继续这条人生 →</button>' : '') + '</article><div class="story-bottom"><button class="back-link" data-action="story-back" ' + (v.canBack ? '' : 'disabled') + '>← 上一幕，改个选择</button><small class="tiny">进度已保存</small></div><section class="story-bag"><h3>我真正获得的能力 · ' + v.ownedCardIds.length + ' 张</h3>' + v.ownedCardIds.map(function (id) { var c = card(id); return '<button class="pill" data-action="card" data-card="' + esc(id) + '" data-owned-card="' + esc(id) + '">' + esc(c && c.name || id) + ' ↗</button>'; }).join('') + (!v.ownedCardIds.length ? '<p class="micro">暂时没有卡，接下来的选择可能带来新能力。</p>' : '') + '</section><p class="tiny center">故事与对白为架空二创。未获得的卡不会发动，返回改选会撤销后续奖励。</p></section>', 'home');
  }
  function storyMove(action, button) {
    if (state.busy || !state.story) return;
    state.busy = true;
    try {
      if (action === 'story-choice') state.story = G.storyChoice(state.story, button.dataset.node, button.dataset.choice);
      if (action === 'story-next') state.story = G.storyNext(state.story);
      if (action === 'story-back') state.story = G.storyBack(state.story);
      if (action === 'story-restart') state.story = G.storyStart(state.story.personId, state.story.seedCards || []);
      persistStory(); storyPage(); state.busy = true;
      state.timer = setTimeout(function () { state.busy = false; }, 220);
    } catch (e) { state.busy = false; toast(e.message || '请重新选择这一幕。'); }
  }
  function openDialog(title, html) {
    state.focusReturn = document.activeElement; document.getElementById('dialog-title').textContent = title; document.getElementById('dialog-content').innerHTML = html; dialog.hidden = false; document.body.classList.add('modal-open');
    var first = dialog.querySelector('button,input,select,textarea'); if (first) first.focus();
  }
  function closeDialog() {
    if (dialog.hidden) return;
    dialog.hidden = true; document.body.classList.remove('modal-open');
    if (state.focusReturn && document.contains(state.focusReturn)) state.focusReturn.focus();
    state.focusReturn = null;
  }
  function cardDialog(id) { var c = card(id); if (!c) return; openDialog(c.name + ' / 原创整活海克斯', hex(c, false) + '<p class="micro">本作娱乐二创能力，不是现实篮球规则或官方游戏天赋。人物图鉴中的展示不代表本局已获得。</p>'); }
  function reviewAnswers() {
    if (!state.record) return;
    var s = state.record.session;
    openDialog('这局真实选过的答案', '<div class="evidence-list">' + s.deck.map(function (item, i) { var q = G.data.questions.find(function (q) { return q.id === item.id; }); var o = q && q.options.find(function (o) { return o.id === s.answers[i]; }); return '<article class="evidence-item"><small>' + (i + 1) + ' / ' + esc(q && q.scene || '') + '</small><p>' + esc(q && q.title || '') + '</p><p>你选了「' + esc(o && o.text || '') + '」</p></article>'; }).join('') + '</div>');
  }
  function rounded(ctx, x, y, w, h, radius) { ctx.beginPath(); ctx.moveTo(x + radius, y); ctx.lineTo(x + w - radius, y); ctx.quadraticCurveTo(x + w, y, x + w, y + radius); ctx.lineTo(x + w, y + h - radius); ctx.quadraticCurveTo(x + w, y + h, x + w - radius, y + h); ctx.lineTo(x + radius, y + h); ctx.quadraticCurveTo(x, y + h, x, y + h - radius); ctx.lineTo(x, y + radius); ctx.quadraticCurveTo(x, y, x + radius, y); ctx.closePath(); }
  function wrap(ctx, text, x, y, width, lineHeight, maxLines) {
    var chars = Array.from(String(text || '')), line = '', lines = [], i;
    for (i = 0; i < chars.length; i++) { if (ctx.measureText(line + chars[i]).width > width && line) { lines.push(line); line = chars[i]; } else line += chars[i]; }
    if (line) lines.push(line); if (maxLines && lines.length > maxLines) { lines = lines.slice(0, maxLines); var tail = lines[lines.length - 1]; while (tail && ctx.measureText(tail + '…').width > width) tail = tail.slice(0, -1); lines[lines.length - 1] = tail + '…'; }
    lines.forEach(function (t, index) { ctx.fillText(t, x, y + index * lineHeight); }); return y + lines.length * lineHeight;
  }
  function image(src) { return new Promise(function (resolve) { var im = new Image(); im.onload = function () { resolve(im); }; im.onerror = function () { resolve(null); }; im.src = src; }); }
  async function paintPortrait(ctx, p, x, y, size) {
    ctx.save(); rounded(ctx, x, y, size, size, 15); ctx.clip();
    var custom = p.personId === 'diy-me', meta = G.portraits[p.personId], im = !custom && meta ? await image(meta.src) : null;
    if (im) ctx.drawImage(im, x, y, size, size);
    else { ctx.fillStyle = custom && colors.includes(p.avatarColor) ? p.avatarColor : '#56376d'; ctx.fillRect(x, y, size, size); ctx.fillStyle = '#fff1cf'; ctx.textAlign = 'center'; ctx.font = 'bold ' + Math.round(size * .38) + 'px sans-serif'; ctx.fillText(custom ? String(p.number) : p.name.slice(0, 2), x + size / 2, y + size * .64); ctx.textAlign = 'left'; }
    ctx.restore();
  }
  function posterBackground(ctx, title) {
    var gradient = ctx.createLinearGradient(0, 0, 1080, 1920); gradient.addColorStop(0, '#2c1646'); gradient.addColorStop(.48, '#14162c'); gradient.addColorStop(1, '#0d0918'); ctx.fillStyle = gradient; ctx.fillRect(0, 0, 1080, 1920);
    ctx.strokeStyle = '#c4a5ef'; ctx.lineWidth = 4; rounded(ctx, 28, 28, 1024, 1864, 28); ctx.stroke();
    ctx.strokeStyle = '#f2c784'; ctx.lineWidth = 3; ctx.beginPath(); ctx.ellipse(540, 590, 450, 160, -.3, 0, Math.PI * 2); ctx.stroke();
    ctx.fillStyle = '#d8c0f6'; ctx.font = 'bold 31px sans-serif'; ctx.fillText('整活NBA / ' + title, 65, 99);
    ctx.fillStyle = '#ad96c5'; ctx.font = '20px sans-serif'; ctx.fillText('平行宇宙娱乐二创 · 按真实作答生成', 65, 1840);
  }
  async function teamPoster() {
    if (state.busy || !state.record) return;
    state.busy = true; toast('五位队友正在集合，合照马上洗出来…');
    try {
      var record = copy(state.record), r = resultFor(record), canvas = document.createElement('canvas'); canvas.width = 1080; canvas.height = 1920; var ctx = canvas.getContext('2d'); posterBackground(ctx, '五个人，各有各的离谱');
      ctx.fillStyle = '#f5d398'; ctx.font = 'bold 52px sans-serif'; wrap(ctx, r.teamName.title, 65, 195, 950, 67, 2);
      ctx.fillStyle = '#d9c6ec'; ctx.font = '27px sans-serif'; wrap(ctx, r.teamName.motto, 65, 360, 950, 42, 2);
      var slots = [{ x: 65, y: 500 }, { x: 410, y: 500 }, { x: 755, y: 500 }, { x: 238, y: 970 }, { x: 582, y: 970 }];
      for (var i = 0; i < r.team.length; i++) {
        var p = r.team[i], slot = slots[i], size = 260; ctx.fillStyle = '#20132f'; rounded(ctx, slot.x - 9, slot.y - 9, size + 18, size + 150, 17); ctx.fill(); ctx.strokeStyle = p.isYou ? '#f1cd86' : '#9d7bc5'; ctx.lineWidth = p.isYou ? 4 : 2; ctx.stroke(); await paintPortrait(ctx, p, slot.x, slot.y, size);
        ctx.fillStyle = p.isYou ? '#f8d897' : '#f8eafc'; ctx.font = 'bold 31px sans-serif'; wrap(ctx, personName(p), slot.x + 5, slot.y + 310, 252, 39, 1); ctx.fillStyle = '#bca0d3'; ctx.font = '21px sans-serif'; ctx.fillText(roles[i] + (p.isYou ? ' / 就是我' : p.personId === 'diy-me' ? ' / DIY自选' : ' / 队友'), slot.x + 5, slot.y + 354); ctx.font = '18px sans-serif'; wrap(ctx, (p.tags || []).slice(0, 1).join('') || p.line || '', slot.x + 5, slot.y + 391, 252, 27, 1);
      }
      ctx.fillStyle = '#f6d49a'; ctx.font = 'bold 30px sans-serif'; ctx.fillText('我的本命海克斯：' + r.augment.name, 65, 1570); ctx.fillStyle = '#c9b4e0'; ctx.font = '25px sans-serif'; wrap(ctx, r.augment.effect || r.augment.line, 65, 1625, 950, 43, 2);
      if (record.diySnapshot) { var sig = record.diySnapshot.signature || {}; ctx.fillStyle = '#d4b5ef'; ctx.font = '21px sans-serif'; wrap(ctx, 'DIY专属：' + (sig.name || '') + ' / ' + (sig.effect || ''), 65, 1745, 950, 31, 2); }
      showPoster(canvas.toDataURL('image/png'), '我的五人整活合照');
    } catch (e) { toast('合照还没洗出来，请再试一次。'); }
    finally { state.busy = false; }
  }
  async function storyPoster() {
    if (state.busy || !state.story) return;
    state.busy = true;
    try {
      var v = G.storyView(state.story), p = person(state.story.personId), canvas = document.createElement('canvas'); canvas.width = 1080; canvas.height = 1920; var ctx = canvas.getContext('2d'); posterBackground(ctx, '我的另一种球场人生');
      await paintPortrait(ctx, p, 240, 170, 600); ctx.fillStyle = '#f4d296'; ctx.font = 'bold 65px sans-serif'; wrap(ctx, personName(p), 65, 890, 950, 78, 1); ctx.font = 'bold 40px sans-serif'; var y = wrap(ctx, v.title, 65, 1000, 950, 58, 2); ctx.fillStyle = '#d8c4e9'; ctx.font = '28px sans-serif'; wrap(ctx, v.text, 65, y + 35, 950, 50, 9); ctx.fillStyle = '#efcb8d'; ctx.font = 'bold 28px sans-serif'; ctx.fillText('这条时间线，我真正获得的能力', 65, 1610); ctx.fillStyle = '#cdb4e2'; ctx.font = '25px sans-serif'; wrap(ctx, v.ownedCardIds.map(function (id) { return card(id).name; }).join(' / ') || '还在旅途中', 65, 1680, 950, 42, 2);
      showPoster(canvas.toDataURL('image/png'), '我的平行人生海报');
    } catch (_) { toast('海报未完成，请重试。'); }
    finally { state.busy = false; }
  }
  function showPoster(url, title) { state.posterURL = url; openDialog(title, '<img class="poster-image" src="' + url + '" alt="' + esc(title) + '"><button class="primary full" data-action="save-poster">' + (P.kind === 'xhs' ? '保存图片到相册' : '保存完整PNG海报') + ' ↓</button><p class="poster-status" id="poster-status" aria-live="polite"></p><p class="tiny center">海报使用这局实际的身份、阵容与能力，不生成虚构匹配结果。</p>'); }
  async function savePoster(button) { if (!state.posterURL || button.disabled) return; button.disabled = true; var status = document.getElementById('poster-status'); try { await P.saveImage(state.posterURL); status.textContent = P.kind === 'xhs' ? '图片已保存到相册。' : 'PNG海报已交给浏览器保存。'; } catch (e) { status.textContent = e.errMsg || e.message || '未能保存，请检查相册权限或重试。'; } finally { button.disabled = false; } }
  function about() { openDialog('整活NBA，怎么玩？', '<p class="micro">选8、16或24题，按第一反应回答球场日常与篮球热梗。每局随机抽题并打乱选项，选择后自动进入下一题。</p><p class="micro">身份与海克斯按整局真实答案计算；结果里的原始匹配分不会被DIY或自选阵容改写。进入故事后，只有真正获得的能力才会触发。</p><p class="micro">DIY球星是你自己写的人设，只用于自选队友与海报，不进入默认人物匹配池。资料只在当前设备保存，无账号、无上传。</p><p class="micro">本作是娱乐二创，不是心理诊断、专业篮球能力测评或人物本人背书。球队和剧情都是平行宇宙设定。</p>'); }
  function renderRoute() {
    var hash = location.hash.slice(1), parts = hash.split('/');
    if (parts[0] === 'quiz') { quiz(); return; }
    if (parts[0] === 'result' && parts[1]) { resultPage(parts[1]); return; }
    if (parts[0] === 'diy') { diyForm(); return; }
    if (parts[0] === 'people') { gallery(); return; }
    if (parts[0] === 'person' && parts[1]) { personPage(parts[1]); return; }
    if (parts[0] === 'cards') { cardsPage(); return; }
    if (parts[0] === 'archive') { archive(); return; }
    if (parts[0] === 'story') { storyPage(); return; }
    if (hash && hash !== 'home') { location.replace('#home'); return; }
    home();
  }
  function action(event) {
    var b = event.target.closest('[data-action]'); if (!b || b.disabled) return;
    var a = b.dataset.action;
    if (state.busy && a !== 'close-dialog') return;
    if (a === 'close-dialog') { closeDialog(); return; }
    if (a === 'home' || a === 'people' || a === 'diy' || a === 'cards' || a === 'archive') { route(a); return; }
    if (a === 'about') { about(); return; }
    if (a === 'mode') { state.count = Number(b.dataset.count); write('count', state.count); document.querySelectorAll('[data-action=mode]').forEach(function (el) { el.setAttribute('aria-pressed', String(Number(el.dataset.count) === state.count)); }); return; }
    if (a === 'start') { begin(); return; }
    if (a === 'resume') { state.session = read('draft', null); route('quiz'); return; }
    if (a === 'leave-quiz') { route('home'); return; }
    if (a === 'answer') { answer(b); return; }
    if (a === 'previous') { if (!state.busy && state.session) { state.session = G.previous(state.session); write('draft', state.session); quiz(); } return; }
    if (a === 'history') { route('result/' + b.dataset.record); return; }
    if (a === 'person') { route('person/' + b.dataset.person); return; }
    if (a === 'card') { cardDialog(b.dataset.card); return; }
    if (a === 'edit-team') { setTeam(); return; }
    if (a === 'reset-team') { delete state.record.customIds; delete state.record.diySnapshot; saveRecord(state.record); rerenderResult(); return; }
    if (a === 'toggle-diy') { toggleDIY(); return; }
    if (a === 'reroll-name') { var r = resultFor(state.record); state.record.teamName = G.rerollName(r); saveRecord(state.record); rerenderResult(); return; }
    if (a === 'team-poster') { teamPoster(); return; }
    if (a === 'save-poster') { savePoster(b); return; }
    if (a === 'review-answers') { reviewAnswers(); return; }
    if (a === 'random-diy') { randomDIY(); return; }
    if (a === 'delete-diy') { openDialog('删除本机DIY球星？', '<p class="micro">只删除当前DIY人设。已保存测试中的队友快照会继续保留。</p><button class="danger full" data-action="confirm-delete-diy">删除当前DIY球星</button>'); return; }
    if (a === 'confirm-delete-diy') { remove('diy'); closeDialog(); diyForm(); toast('DIY球星已删除。'); return; }
    if (a === 'clear-history') { openDialog('清除本机测试记录？', '<p class="micro">将删除最近测试、答题草稿和故事进度，DIY球星单独保留。</p><button class="danger full" data-action="confirm-clear-history">清除本机测试记录</button>'); return; }
    if (a === 'confirm-clear-history') { remove('history'); remove('draft'); remove('story'); state.session = null; state.record = null; state.story = null; closeDialog(); archive(); return; }
    if (a === 'story-result') { storyBegin(resultFor(state.record).identity.personId, state.record); return; }
    if (a === 'story-preview') { storyBegin(b.dataset.person, null); return; }
    if (a === 'story-exit') { if (state.storyRecord) route('result/' + state.storyRecord.id); else route('person/' + state.story.personId); return; }
    if (a === 'story-poster') { storyPoster(); return; }
    if (a === 'story-choice' || a === 'story-next' || a === 'story-back' || a === 'story-restart') { storyMove(a, b); }
  }
  document.addEventListener('click', action);
  document.addEventListener('submit', function (e) { if (e.target.id === 'diy-form') { e.preventDefault(); saveDIY(e.target); } if (e.target.id === 'team-form') { e.preventDefault(); saveTeam(e.target); } });
  document.addEventListener('input', function (e) { if (e.target.closest('#diy-form')) updateDIYPreview(document.getElementById('diy-form')); if (e.target.id === 'people-search') { state.query = e.target.value; filterPeople(); } });
  document.addEventListener('error', function (e) { var image = e.target; if (image && image.tagName === 'IMG' && image.parentNode) image.parentNode.classList.add('failed'); }, true);
  document.addEventListener('keydown', function (e) {
    if (dialog.hidden) return;
    if (e.key === 'Escape') { e.preventDefault(); closeDialog(); return; }
    if (e.key !== 'Tab') return;
    var items = Array.from(dialog.querySelectorAll('button:not([disabled]),input,select,textarea,[tabindex="0"]')).filter(function (n) { return n.offsetParent !== null; }); if (!items.length) return;
    var first = items[0], last = items[items.length - 1]; if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); } else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  });
  window.addEventListener('hashchange', renderRoute);
  Promise.resolve(P.ready).then(function () { var count = Number(read('count', 8)); state.count = [8, 16, 24].includes(count) ? count : 8; renderRoute(); }).catch(function () { app.innerHTML = '<section class="page"><h1 class="page-title">球场信号暂未接通。</h1><p>请刷新页面重试。</p><button class="primary" data-action="home">返回首页</button></section>'; });
})();
