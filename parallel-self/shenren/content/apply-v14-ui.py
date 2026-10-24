"""One-time V13 -> V14 UI migration. Subsequent edits belong in src/app.js."""
from pathlib import Path
import re

P = Path(__file__).resolve().parents[1] / 'src/app.js'
s = P.read_text()
assert 'function storyScreen(' not in s, 'Already migrated; edit app.js directly.'
def fn(name, body):
    global s
    pattern = r'^function ' + name + r'\([^\n]*\n'
    s, n = re.subn(pattern, lambda _: body.strip() + '\n', s, count=1, flags=re.M)
    assert n == 1, name

s = s.replace("document.documentElement.dataset.style=read('style.v12')==='paper'?'paper':'night';", "document.body.classList.add('v14-ui');document.documentElement.dataset.style=read('style.v14','paper');")
s = s.replace("function themed(id=theme){return D.themes.find(t=>t.id===id);}function person(id){return D.characters.find(p=>p.id===id);}", "function themed(id=theme){return D.themes.find(t=>t.id===id);}function person(id){return D.characters.find(p=>p.id===id)||(currentRecord?recordData(currentRecord).characters.find(p=>p.id===id):null);}")
fn('recordData', "function recordData(record){return record&&record.session.version===10?window.WORLD_LEGACY_DATA:record&&record.session.version===11?window.WORLD_V11_DATA:record&&record.session.version===12?window.WORLD_V12_DATA:D;}")
fn('recordEngine', "function recordEngine(record){return record&&record.session.version===10?window.ShenrenLegacyEngine:record&&record.session.version===11?window.ShenrenV11Engine:record&&record.session.version===12?window.ShenrenV12Engine:E;}")
fn('findCard', "function findCard(id){const pools=[D,window.WORLD_V12_DATA,window.WORLD_V11_DATA,window.WORLD_LEGACY_DATA];for(const d of pools){if(!d)continue;const a=[].concat(...Object.values(d.augments)).find(a=>a.id===id);if(a)return a;}return null;}")
fn('analyzeRecord', r'''
function analyzeRecord(record){
 const r=recordEngine(record).analyze(record.session,recordData(record));
 if(record.session.version===D.version){
  const bs=storyFor(r.identity.personId);let view=null;
  if(record.storyState&&record.storyState.originKey===record.id&&E.storyValid(record.storyState,D))view=E.storyView(record.storyState,D);
  r.obtainedCardIds=view?view.ownedCardIds:(r.obtainedCardIds||[r.augment.id]);
  r.obtainedCards=r.obtainedCardIds.map(findCard).filter(Boolean);
  if(bs)r.story=[view&&view.isEnding?view.title:bs.title,view&&view.isEnding?view.text:bs.nodes[0].text,'你的选择会改变后面的场面。'];
 }
 return r;
}
''')
fn('render', r'''
function render(html){
 clearTimeout(answerTimer);answerTimer=null;advancing=false;
 document.body.classList.toggle('is-home',html.includes('v14-home'));
 document.body.classList.toggle('has-dock',html.includes('result-dock'));
 document.body.classList.toggle('focus-mode',/intro-page|reveal-page|class="quiz|v14-story/.test(html));
 app.innerHTML=html+(!persistent?'<p class="local-note">当前环境不保存记录，本次体验和导出仍可使用。</p>':'');
 app.focus({preventScroll:true});scrollTo(0,0);document.documentElement.style.setProperty('--accent',themed().accent);
 document.documentElement.dataset.appReady='true';$('#loading').hidden=true;pruneSheets();
 document.querySelectorAll('#tabbar [data-action]').forEach(b=>b.setAttribute('aria-current',html.includes('v14-home')&&b.dataset.action==='home'?'page':html.includes('archive')&&b.dataset.action==='archive'?'page':'false'));
}
''')
s=s.replace("const journeyTitles=['镜子比你，晚笑了一秒。','另一个你，先活成了传说。','伸出手，选一条人生重开。'];", "const journeyTitles=['普通的一天','镜子慢了半拍','另一种人生'];\nconst introKeys=['introRealLife','introMirror','introNewWorld'];")
fn('journeyFold', r'''
function journeyFold(){return `<details class="journey-fold"><summary><span>我的穿越故事 <small>三幕小故事，随时重看</small></span><b>＋</b></summary><div class="journey-thumbnails">${journeyTitles.map((title,i)=>`<article><img class="journey-thumb" src="${window.WORLD_BRANDING[introKeys[i]]}" alt="${esc(title)}" loading="lazy"><small>${i+1} / 3</small><p>${esc(title)}</p></article>`).join('')}</div><button class="secondary" data-action="intro">从第一幕开始看</button></details>`;}
''')
fn('home', r'''
function home(){
 close();result=null;currentRecord=null;const stats=D.counts.byTheme[theme],draft=pending(),ids=E.exposureSample(D,theme,3),storyDraft=read('story.v14');
 render(`<section class="v14-home home narrow"><div class="home-topline"><span>平行人生实验室</span><small>V14 · ${E.enabledPeople(D).length} 个另一个我</small></div><div class="home-hero"><div><span class="eyebrow">今天，换一条时间线</span><h1>换个世界，<br>你是哪一位？</h1><p>选几个日常场景，看看你会成为谁，<br>又会带着什么离谱能力。</p></div><img class="home-hero-art" src="${window.WORLD_BRANDING.introNewWorld}" alt="镜子另一边的三条人生" loading="lazy"></div><ol class="home-steps"><li>选一个世界</li><li>做几个选择</li><li>获得身份，走进故事</li></ol><section class="home-section"><div class="section-head"><h2>这次，穿越到哪里？</h2><span>01 / 选世界</span></div><div class="world-picker" role="group" aria-label="选择世界">${D.themes.map((t,i)=>`<button class="world-card" data-action="theme" data-theme="${t.id}" aria-pressed="${theme===t.id}"><span class="world-icon" aria-hidden="true">${['⌘','◉','✳'][i]}</span><span><strong>${esc(t.name)}</strong><small>${['网吧开黑 · 对线热梗','街球日常 · 球星解说','出门接梗 · 离谱日常'][i]}</small></span><i>${theme===t.id?'✓':'○'}</i></button>`).join('')}</div></section><section class="home-section"><div class="section-head"><h2>用几个选择认识你</h2><span>02 / 选题量</span></div><div class="mode-picker" role="group" aria-label="选择题量">${D.modes.map((n,i)=>`<button data-action="mode" data-count="${n}" aria-pressed="${count===n}"><b>${n}<small>题</small></b><span>${['轻松试试','多点细节','完整体验'][i]}</span></button>`).join('')}</div><button class="primary home-primaryCTA full-width" data-action="start">开始穿越 <span aria-hidden="true">→</span></button><p class="micro center">点选即下一题 · 随时返回改选 · 每次随机抽题</p>${draft?`<button class="resume-compact" data-action="resume">继续上次答题 · 已答 ${draft.answers.filter(a=>a!==null).length}/${draft.count}</button>`:''}${storyDraft&&E.storyValid(storyDraft,D)?'<button class="resume-compact" data-action="story-resume">继续还没讲完的故事 →</button>':''}</section><div class="home-entry-grid"><button class="secondary" data-action="gallery"><strong>全部人物</strong><small>${E.enabledPeople(D).length} 位，看看有谁</small></button><button class="secondary" data-action="card-gallery"><strong>全部海克斯</strong><small>${E.enabledCards(D).length} 张，能力有点怪</small></button></div><section class="home-section"><div class="section-head"><h2>这个世界，可能遇见</h2><span>${stats.people} 位人物</span></div><div class="home-samples">${ids.map(p=>`<button data-action="person" data-id="${p.id}">${portrait(p)}<strong>${esc(p.name)}</strong><small>${(p.signaturePerks||[]).map(findCard).filter(Boolean).slice(0,1).map(a=>esc(a.name)).join('')}</small></button>`).join('')}</div></section>${journeyFold()}<div class="home-tools"><button class="text" data-action="squad-home">自选一个五人团 →</button><button class="text" data-action="story-preview">先逛五组故事样板 →</button></div><p class="tiny center">${stats.questions} 道本主题情境 · 梗与能力为架空二创<br>这是娱乐匹配，答案只留在本机。</p></section>`);
}
''')
fn('intro', r'''
function intro(n=0){
 close();introStep=Math.max(0,Math.min(2,n));
 const copy=['又是普通的一天。你看着镜子，忽然想知道：如果换个世界，自己会过成什么样？','镜中的人慢了半拍。你伸手过去，镜面竟像水一样轻轻晃动。','门的另一边，三条人生正在等你。先选一个世界，去见见另一个自己。'];
 render(`<section class="intro-page v14-intro narrow"><div class="intro-top"><span>我的穿越故事 · ${introStep+1}/3</span><button class="text" data-action="intro-skip">跳过故事</button></div><figure class="intro-figure"><img src="${window.WORLD_BRANDING[introKeys[introStep]]}" alt="${esc(journeyTitles[introStep])}" fetchpriority="high"><span class="image-fallback" aria-hidden="true">镜子另一边，还有另一种可能。</span></figure><div class="intro-copy"><h1>${journeyTitles[introStep]}</h1><p>${copy[introStep]}</p></div><div class="intro-controls"><div class="intro-progress" role="img" aria-label="第${introStep+1}幕，共3幕">${[0,1,2].map(i=>`<i class="${i===introStep?'on':''}"></i>`).join('')}</div><button class="primary full-width" data-action="intro-next">${introStep===2?'进入平行世界':'继续'} <span aria-hidden="true">→</span></button><button class="text intro-prev" data-action="intro-prev" ${introStep?'':'disabled'}>← 上一幕</button></div></section>`);
 if(introStep<2){const im=new Image();im.src=window.WORLD_BRANDING[introKeys[introStep+1]];im.onload=function(){if(introStep===0){const last=new Image();last.src=window.WORLD_BRANDING.introNewWorld;}};}
}
''')
fn('tags', r'''
function tags(p){const cards=(p.signaturePerks||[]).map(findCard).filter(a=>a&&(p.enabled===false||a.enabled!==false));return `<div class="character-tags">${cards.map(a=>`<button class="pill" data-action="peek" data-id="${a.id}">${esc(a.name)} <span aria-hidden="true">↗</span></button>`).join('')}</div>`;}
''')
fn('storyPreview', r'''
function storyPreview(){open('先看看这七条人生',`<p class="micro">故事试玩不生成测试身份。从零张卡开始，跟随选择获得能力。</p><div class="story-samples">${['dailanzi','huchenfeng','fengge','luobenwei','xujingyu','draymond-green','ershu'].map(pid=>{const p=E.resolvePerson(D,pid),st=storyFor(pid);return p&&st?`<button class="history-card" data-action="story-start" data-person="${pid}">${portrait(p)}<span><strong>${esc(p.name)}</strong><small>${esc(st.title)}</small></span><b>→</b></button>`:'';}).join('')}</div>`);}
''')
fn('showResult', r'''
function showResult(record){
 close();session=JSON.parse(JSON.stringify(record.session));theme=session.theme;count=session.count;series='all';currentRecord=JSON.parse(JSON.stringify(record));result=analyzeRecord(record);
 if(record.customTeam&&!recordEngine(record).squadError(record.customTeam.ids,theme,recordData(record),record.customTeam.free)){result.team=recordEngine(record).customSquad(record.customTeam.ids,theme,recordData(record),result.vector,result.identity,result.augment,record.customTeam.free);result.customTeam=true;}applySquadBrand();
 const r=result,p=r.identity,t=themed(),isNew=session.version===D.version,story=isNew?storyFor(p.personId):null;
 render(`<section class="result v12-result v14-result"><div class="result-top"><span>我的平行身份 · ${session.count} 个选择</span><button class="text" data-action="home">返回首页</button></div><article class="identity-card"><div class="identity-photo">${portrait(p)}</div><div class="identity-copy"><span class="eyebrow">换个世界，你成为了</span><h1>${esc(p.name)}</h1><p class="identity-sub">${esc(p.sub)}</p><div class="identity-tags"><span>原始匹配 ${p.match}%</span><span>${esc(r.profile.name)}</span></div><button class="text" data-action="person" data-id="${p.id}">认识这个人 →</button></div></article>${story?`<article class="story-card story-entry"><span class="eyebrow">身份已就位，故事才刚开始</span><h2>${esc(story.title)}</h2><p>${esc(story.nodes[0].text)}</p><button class="primary full-width" data-action="story-start" data-person="${p.personId}" data-origin="result">${currentRecord.storyState?'继续我的故事':'进入我的平行人生'} →</button><small>每次选择都会改变后续场面和结局</small></article>`:`<article class="story-card"><h2>旧时间线的故事</h2><h3>${esc(r.story[0])}</h3><p>${esc(r.story[1])}</p><details><summary>看看结局</summary><p>${esc(r.story[2])}</p></details></article>`}<div class="section-head"><h2>这次，带着什么能力？</h2><span>${isNew?(r.obtainedCards||[]).length+' 张已获得':'历史能力'}</span></div><section class="augment-result">${augmentCard(r.augment)}</section>${isNew?ownedCardsPanel(r):inherentPanel(r)}<details class="result-fold match-chain"><summary>为什么是这个身份和海克斯？</summary>${(r.augment.evidence||[]).map(e=>`<div class="chain-row"><div><small>${esc(e.scene)}</small><p>你选了「${esc(e.choice)}」</p></div></div>`).join('')}<p>原始匹配分来自你本轮的选择；热门排序优先级不改写这个分数。</p><button class="text" data-action="review">回看全部选择 →</button><button class="text" data-action="alternatives">看看另外两张候选卡 →</button></details><div class="section-head team-heading"><h2>五个人，凑不出一个正常队</h2><span>${r.customTeam?'自选阵容':'你 ＋ 四名队友'}</span></div>${squadBrandPanel(r)}<div class="squad-actions"><button class="secondary" data-action="squad">${r.customTeam?'编辑阵容':'自选我的队友'}</button>${r.customTeam?'<button class="text" data-action="auto-team">恢复匹配阵容</button>':''}</div><div class="team-grid">${r.team.map((m,i)=>`<article class="team-card ${m.isYou?'is-you':''}" data-role="${i}" data-person="${m.id}"><div class="team-role"><span>${t.roles[i]}</span><strong>${m.isYou?'就是你':'队友'}</strong></div><button class="team-portrait" data-action="person" data-id="${m.id}">${portrait(m)}</button><h3>${esc(m.name)}</h3><p>${esc(m.teamLine||m.line)}</p></article>`).join('')}</div><details class="result-fold"><summary>我的六维面板</summary><div class="dimensions">${t.dims.map((name,i)=>`<div><span>${esc(name)}</span><i style="--value:${r.vector[i]}%"></i><b>${r.vector[i]}</b></div>`).join('')}</div><p class="tiny">娱乐反应刻度，不是心理诊断。</p></details><div class="result-dock"><button class="primary" data-action="team-poster">五人合照</button><button class="secondary" data-action="poster">身份海报</button><button class="text" data-action="start">再测一次</button></div></section>`);
}
''')
fn('reveal', r'''
function reveal(record){close();currentRecord=JSON.parse(JSON.stringify(record));session=JSON.parse(JSON.stringify(record.session));theme=session.theme;count=session.count;result=analyzeRecord(record);const p=result.identity,st=storyFor(p.personId);render(`<section class="reveal-page narrow"><span class="eyebrow">穿越成功 · 你的新身份</span><h1>在这个宇宙，<br>你成为了 <em>${esc(p.name)}</em></h1><div class="reveal-scene large-portrait-scene"><img class="reveal-illustration" src="${window.WORLD_BRANDING[theme==='lol'?'revealLol':theme==='basket'?'revealBasket':'revealAbstract']}" alt="你的平行人生背景"><div class="reveal-portrait">${portrait(p)}</div><span class="scene-stamp">平行身份 / 架空创作</span></div><div class="reveal-story"><h2>${esc(st?st.title:result.story[0])}</h2><p>${esc(st?st.nodes[0].text:result.story[1])}</p><button class="primary full-width" data-action="reveal-open">查收身份与海克斯 →</button><p class="micro">匹配来自你的真实选择 · 故事由你接着写</p></div></section>`);}
''')
fn('about', r'''
function about(){open('这场穿越，怎么玩？',`<div class="about"><h3>选世界，答几个日常问题</h3><p>三个世界，8／16／24 题。点选后自动进入下一题，随时可以返回改选。每次重新抽题。</p><h3>获得一个身份和一张能力卡</h3><p>人物由本轮真实选择匹配。代表海克斯是人物的内容库，不会自动全部塞进背包。</p><h3>走进故事，让能力真的起作用</h3><p>每个人都有自己的六幕故事。选择会改变后续事件，明确获得的海克斯才会触发，返回改选也会重算背包。</p><h3>拉起一个离谱五人团</h3><p>自动匹配或自己挑人，换个搞笑队名，生成五人合照。记录只保存在这台设备。</p><p class="tiny">人物、能力与对白均为架空二创；来源线索另在内容审阅页展示。不读取真实机型、收入或学历来评价玩家。</p></div>`);}
''')
# Player detail has the same cards as its labels, and no source-verification block.
s=s.replace("<span>${esc((p.tags||[]).slice(0,2).join(' · '))}</span>","<span>${(p.signaturePerks||[]).length} 张代表海克斯</span>")
s=s.replace("${tags(p)}<p class=\"micro\">人物反应与卡牌效果是本作创作，不是本人发言。</p>${universeDetails(p)}", "${tags(p)}<p class=\"micro\">人物反应与卡牌效果是本作创作，不是本人发言。</p><button class=\"primary full-width\" data-action=\"story-start\" data-person=\"${p.personId}\">走进他的平行故事 →</button>")
s=re.sub(r'<details class="reference-box">.*?</details>', '', s)
s=s.replace("${a.activationMode==='identity'?'人物自带赠卡，不作为本轮作答证据。':'依据真实作答匹配；夸张效果不影响分数。'}", "${a.activationMode==='story'?'在故事中的明确奖励节点获得。':'依据本轮实际选择匹配，也可由故事中的明确奖励获得。'}")
s=s.replace("else if(a==='palette'){const s=document.documentElement.dataset.style==='paper'?'night':'paper';document.documentElement.dataset.style=s;write('style',s);write('style.v12',s);paletteLabel();}", "else if(a==='palette'){const s=document.documentElement.dataset.style==='paper'?'night':'paper';document.documentElement.dataset.style=s;write('style.v14',s);paletteLabel();}")
s=s.replace("function action(e){const b=e.target.closest('[data-action]');if(!b||b.disabled)return;const a=b.dataset.action;", "function action(e){const b=e.target.closest('[data-action]');if(!b||b.disabled)return;const a=b.dataset.action;if(storyAction(a,b))return;")
s=s.replace("document.querySelectorAll('header,footer')", "document.querySelectorAll('header,footer,#tabbar')")
s=s.replace("});intro();", "});bootV14();")
s=s.replace('V13','V14').replace('/v13/','/v14/').replace('V10 REBORN','V14 / 平行人生').replace(' ·  V11',' ·  V14')

fragment = r'''
let storyState=null,storyRecordId=null,storyClickLock=false;
function storyFor(pid){return (D.branchStories||[]).find(st=>st.personId===pid);}
function ownedCardsPanel(r){const cards=r.obtainedCards||[r.augment];return `<section class="story-owned result-owned"><h3>我的本局背包 · ${cards.length} 张</h3><div class="character-tags">${cards.map(a=>`<button class="pill" data-action="peek" data-id="${a.id}" data-owned-card="${a.id}">${esc(a.name)} ↗</button>`).join('')}</div><p class="micro">答题匹配的卡，以及故事中明确获得的卡。人物图鉴里的其他代表卡仍未获得。</p></section>`;}
function storyBegin(pid,fromResult=false){
 const p=E.resolvePerson(D,pid);if(!p||p.enabled===false||!storyFor(pid)){notify('这条故事暂时不可用。');return;}
 const rec=fromResult&&currentRecord&&currentRecord.session.version===D.version?currentRecord:null;
 storyRecordId=rec?rec.id:null;
 if(rec&&rec.storyState&&rec.storyState.originKey===rec.id&&E.storyValid(rec.storyState,D))storyState=rec.storyState;
 else{const seed=rec?[analyzeRecord(rec).augment.id]:[];storyState=E.storyStart(pid,D,seed,rec?rec.id:'preview:'+pid);}
 theme=p.theme;storyPersist();storyScreen();
}
function storyPersist(){
 write('story.v14',storyState);
 if(storyRecordId){const rows=history(),rec=rows.find(r=>r.id===storyRecordId);if(rec){rec.storyState=JSON.parse(JSON.stringify(storyState));write('history',rows);currentRecord=JSON.parse(JSON.stringify(rec));result=analyzeRecord(rec);}}
}
function storyResume(){const st=read('story.v14');if(!E.storyValid(st,D)){notify('没有可继续的故事。');return;}storyState=st;const rec=history().find(r=>r.id===st.originKey&&r.session.version===D.version);storyRecordId=rec?rec.id:null;if(rec)currentRecord=rec;const p=E.resolvePerson(D,st.personId);theme=p.theme;storyScreen();}
function storyScreen(){
 close();const v=E.storyView(storyState,D),p=E.resolvePerson(D,storyState.personId),st=storyFor(p.personId);
 const ledger=v.rewardLedger||[],recent=ledger.filter(x=>x.nodeId===(storyState.history.length?storyState.history[storyState.history.length-1].nodeId:''));
 render(`<section class="v14-story narrow" data-story-person="${p.personId}" data-story-node="${v.node}"><div class="story-top"><button class="text" data-action="story-exit">← ${storyRecordId?'返回身份':'返回首页'}</button><small>${v.progress.current} / ${v.progress.total} 幕</small></div><div class="story-person">${portrait(p)}<div><small>${esc(p.name)}的平行人生</small><h1>${esc(st.title)}</h1></div></div><div class="story-progress" aria-label="故事第${v.progress.current}幕">${Array.from({length:v.progress.total},(_,i)=>`<i class="${i<v.progress.current?'on':''}"></i>`).join('')}</div><article class="story-page"><span class="eyebrow">${v.isEnding?'这一条时间线的结局':'第 '+v.progress.current+' 幕'}</span><h2>${esc(v.title)}</h2><p class="story-node-text">${esc(v.text)}</p>${(v.cardEvents||[]).map(c=>c.owned?`<div class="story-card-event" data-trigger-card="${c.cardId}"><button class="pill" data-action="peek" data-id="${c.cardId}">${esc(findCard(c.cardId).name)} · 发动</button><p>${esc(c.text)}</p></div>`:`<p class="story-node-text plain-event">${esc(c.text)}</p>`).join('')}${recent.length?`<div class="story-rewards" role="status"><small>选择带来的新能力</small>${recent.map(x=>`<button class="pill" data-action="peek" data-id="${x.cardId}">＋ ${esc(findCard(x.cardId).name)}</button>`).join('')}</div>`:''}${v.choices.length?`<div class="story-choices">${v.choices.map(c=>`<button class="story-choice" data-action="story-choice" data-node="${v.node}" data-choice="${c.id}"><span>${esc(c.text)}</span><b>→</b></button>`).join('')}</div>`:v.isEnding?`<div class="story-actions"><button class="primary full-width" data-action="story-poster">把这条人生存成海报</button><button class="secondary full-width" data-action="story-restart">换个选择，再走一次</button>${storyRecordId?'<button class="text" data-action="story-result">回到身份与五人团 →</button>':''}</div>`:'<button class="primary full-width" data-action="story-next">继续故事 →</button>'}</article><div class="story-bottom"><button class="text" data-action="story-back" ${v.canBack?'':'disabled'}>← 上一幕，改个选择</button><small>进度已保存</small></div><section class="story-owned"><h3>我的能力背包 · ${v.ownedCardIds.length}</h3><div class="character-tags">${v.ownedCardIds.map(id=>`<button class="pill" data-action="peek" data-id="${id}" data-owned-card="${id}">${esc(findCard(id).name)} ↗</button>`).join('')||'<p class="micro">暂时还没有卡，接下来的选择会带来能力。</p>'}</div></section><p class="tiny center">故事与对白为本作二创 · 未获得的卡不会发动</p></section>`);
}
function storyAction(a,b){
 if(a==='story-start'){storyBegin(b.dataset.person,b.dataset.origin==='result');return true;}
 if(a==='story-resume'){storyResume();return true;}
 if(a==='story-poster'){storyPoster();return true;}
 if(a==='retry-images'){document.body.classList.remove('image-has-error');document.querySelectorAll('[data-failed-src]').forEach(im=>{im.parentNode.classList.remove('image-failed');if(im.tagName.toLowerCase()==='image'){im.setAttribute('href',im.dataset.failedSrc);im.setAttributeNS('http://www.w3.org/1999/xlink','xlink:href',im.dataset.failedSrc);}else im.src=im.dataset.failedSrc;});return true;}
 if(!a.startsWith('story-'))return false;
 if(a==='story-preview')return false;
 if(a==='story-result'||a==='story-exit'){const rec=storyRecordId&&history().find(r=>r.id===storyRecordId);if(rec)showResult(rec);else home();return true;}
 if(a==='story-restart'){const seed=storyState.seedCards||[];storyState=E.storyStart(storyState.personId,D,seed,storyState.originKey);storyPersist();storyScreen();return true;}
 if(storyClickLock)return true;storyClickLock=true;
 try{if(a==='story-choice')storyState=E.storyChoose(storyState,b.dataset.node,b.dataset.choice,D);else if(a==='story-next')storyState=E.storyAdvance(storyState,D);else if(a==='story-back')storyState=E.storyBack(storyState,D);else return false;storyPersist();storyScreen();}catch(error){notify(error.message||'请重新选择这一幕。');}finally{setTimeout(()=>{storyClickLock=false;},220);}return true;
}
async function storyPoster(){
 if(!storyState||posterBusy)return;posterBusy=true;
 try{const v=E.storyView(storyState,D),p=E.resolvePerson(D,storyState.personId),c=document.createElement('canvas');c.width=1080;c.height=1920;const ctx=c.getContext('2d');ctx.fillStyle='#f7f5ed';ctx.fillRect(0,0,1080,1920);ctx.fillStyle='#42634f';ctx.font='bold 32px sans-serif';ctx.fillText('平行宇宙的另一个我',70,98);await paintPortrait(ctx,p,190,170,700);ctx.fillStyle='#202b25';fit(ctx,p.name,70,940);ctx.fillText(p.name,70,970);ctx.font='bold 40px sans-serif';let y=wrap(ctx,v.title,70,1060,940,56,2);ctx.font='28px sans-serif';ctx.fillStyle='#53635a';y=wrap(ctx,v.text,70,y+30,940,45,5);ctx.fillStyle='#42634f';ctx.font='bold 28px sans-serif';ctx.fillText('这一局，我真正获得的能力',70,1510);ctx.font='26px sans-serif';wrap(ctx,v.ownedCardIds.map(id=>findCard(id).name).join(' / ')||'还在旅途中',70,1575,940,46,3);ctx.font='23px sans-serif';ctx.fillText('不同的选择，会走向另一种结局。',70,1785);ctx.font='18px sans-serif';ctx.fillText('架空故事 / 非本人发言 · yangcrazy1.github.io/Basketball/v14/',70,1850);const url=c.toDataURL('image/png');open('我的平行人生海报',`<p class="micro">海报上的能力来自这条故事的实际获得记录。</p><img class="poster story-poster" src="${url}" alt="${esc(p.name)}的平行故事与已获得能力"><a class="primary download-png" href="${url}" download="平行宇宙的另一个我-V14-故事海报.png">下载故事海报 PNG</a>`);}catch(error){notify('海报未完成，请重试。');console.error(error);}finally{imageCache.clear();posterBusy=false;}
}
function bootV14(){let pid='';try{pid=new URLSearchParams(location.search).get('story')||'';}catch(_){}if(pid&&storyFor(pid))storyBegin(pid);else intro();}
document.addEventListener('error',function(e){const im=e.target;if(!im||!im.tagName||!['img','image'].includes(im.tagName.toLowerCase()))return;im.dataset.failedSrc=im.getAttribute('src')||im.getAttribute('href')||'';if(im.parentNode)im.parentNode.classList.add('image-failed');document.body.classList.add('image-has-error');},true);
'''
s=s.replace('function action(e){',fragment+'\nfunction action(e){')
P.write_text(s)
print('V14 player home, intro, acquired-card story flow, results and exported story poster installed.')
