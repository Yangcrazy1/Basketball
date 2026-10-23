"""Apply V8 renderer changes to the V7 UI, keeping its responsive layout."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'src/app.js'
s=p.read_text()
if "world-otherme.v8." in s:
    raise SystemExit('V8 interface is already applied')
s=s.replace('world-otherme.v7.','world-otherme.v8.').replace('V7','V8').replace('VOL.07','VOL.08')
def replace_function(name,body):
    global s
    start=s.index('function '+name+'(')
    end=s.find('\n',start)
    assert end!=-1
    s=s[:start]+body+s[end:]

replace_function('perkIcon', '''function perkIcon(a){if(a.visual){return `<span class="perk-art equipment-mix" role="img" aria-label="${esc(a.visual.label)}，真实游戏图标梗改" data-layout="${a.visual.layout}" data-copies="${a.visual.icons.length}">${E.artLayout(a).map((p,i)=>`<img class="game-item" data-game-icon="${p.icon}" data-copy="${i+1}" src="${window.WORLD_GAME_ICONS[p.icon].url}" alt="" style="--ix:${p.x*100}%;--iy:${p.y*100}%;--is:${p.size*100}%;--ir:${p.rotation}deg">`).join('')}</span>`;}const w=window.WORLD_PERK_SHEET.width/4,h=window.WORLD_PERK_SHEET.height/4,i=a.icon||0;return `<span class="perk-art" role="img" aria-label="${esc(a.name)}原创恶搞图标"><svg viewBox="${i%4*w} ${Math.floor(i/4)*h} ${w} ${h}" aria-hidden="true"><use href="#perk-sheet"/></svg></span>`;}''')
s=s.replace("['table-flip','collector-union','basic-duty']", "['collector-union','double-laugh','tes-top']")
s=s.replace('VOL.08 / 网友脑洞风','VOL.08 / 装备梗宇宙')
s=s.replace('可能有点<em>不正常。</em>','可能笑得<em>有两段。</em>')
s=s.replace('从“四个队友出了收集者”开始，<br>测出你的平行身份和本命恶搞海克斯。','五把收集者，装不下一个前排。<br>二段笑、陀螺局，测出你的神人身份。')
s=s.replace('<h2>你的海克斯，离谱但合理。</h2>','<h2>装备是真的，效果是整的。</h2>')
s=s.replace('本作自制恶搞卡，借鉴网友 DIY 天赋卡的表达方式。人物与剧情是娱乐设定，头像说明见人物卡。','真实装备与技能图标重新排布；恶搞效果不代表实际游戏机制。人物与剧情为娱乐设定。')
needle='<div class="pool-strip">'
s=s.replace(needle, '${theme===\'lol\'?memeScenes():\'\'}'+needle,1)
s=s.replace('<section class="sample-case"><div>', '<section class="sample-case"><div class="sample-real-icons">${perkIcon(findCard(\'collector-union\'))}</div><div>',1)
s=s.replace('<div class="hex-icon">${perkIcon(a)}</div><h2>', '<div class="hex-icon">${perkIcon(a)}</div>${a.visual?`<span class="real-art-label">${esc(a.visual.label)} · 图标梗改</span>`:\'\'}<h2>')
s=s.replace('同一场对局，继续接梗','同一场景，继续接梗')
s=s.replace('<h1>${esc(q.title)}</h1><p class="micro">','${questionArt(q)}<h1>${esc(q.title)}</h1><p class="micro">')
replace_function('start', '''function start(chapter=null,forceSeries=null){close();if(forceSeries){theme='lol';series=forceSeries;write('series',series);}const k='first.'+theme+'.'+series;session=E.draw(D,theme,count,read(k),undefined,theme==='lol'?series:'all');if(chapter){const chosen=D.questions.filter(q=>q.theme==='lol'&&q.series===series&&q.chapter===chapter).sort((a,b)=>a.stage-b.stage);if(chosen.length===4){const ids=new Set(chosen.map(q=>q.id));session.deck=[...chosen.map(q=>({id:q.id,order:E.shuffle(q.options.map(o=>o.id))})),...session.deck.filter(d=>!ids.has(d.id))].slice(0,count);}}write(k,session.deck[0].id);write('theme',theme);write('count',count);save();quiz();}''')
replace_function('cardNote', '''function cardNote(id){const a=findCard(id);if(!a)return;const icons=[...new Set(a.visual?.icons||[])];open(a.name+' · 图标与梗设定',`${augmentCard(a,true)}<div class="about"><p>${esc(a.creation||'本作原创恶搞设定。')}</p>${icons.length?`<div class="icon-sources">${icons.map(id=>{const g=window.WORLD_GAME_ICONS[id];return `<a href="${esc(g.sourceURL)}" target="_blank" rel="noreferrer"><img src="${g.url}" alt=""><span>${esc(g.name)} ×${a.visual.icons.filter(i=>i===id).length}<small>Riot Data Dragon ${g.version} ↗</small></span></a>`;}).join('')}</div>`:''}<p>卡牌依据实际作答匹配。重复装备图标只是梗图，卡面效果为自制恶搞，不是官方强化或出装建议。</p>${a.sourcePage?`<p><a href="${esc(a.sourcePage)}" target="_blank" rel="noreferrer">查看参考来源 ↗</a></p>`:''}</div>`);}''')
replace_function('cardGallery', '''function cardGallery(){open(themed().name+' · 整活海克斯图鉴',`<p class="micro">${D.augments[theme].length} 张自制恶搞卡。${theme==='lol'?'真实装备和技能图标重新排布，效果负责一本正经地离谱。':'点开看它怎么整。'}</p><div class="card-gallery">${D.augments[theme].map(a=>`<button data-action="peek" data-id="${a.id}">${perkIcon(a)}<strong>${esc(a.name)}</strong><small>${esc(a.visual?.label||a.category||'整活')}</small></button>`).join('')}</div>`);}''')
replace_function('about', '''function about(){open('装备梗宇宙 · V8',`<div class="about"><p>收集者×5、无尽×6、帽子×3、金身×2，这次使用 Riot Data Dragon 16.21.1 真实装备与召唤师技能图标重新组合。卡牌效果是本作恶搞；重复图标是梗图，不是装备叠加说明。</p><p>${D.counts.questions} 道情境题，其中联盟 ${D.counts.lolQuestions} 道、${D.counts.lolChapters} 个连续小剧场。8 / 16 / 24 题随机抽取 2 / 4 / 6 个剧场，剧情顺序连贯，选项打乱；新局首题改变，续答保持本轮。</p><p>新增小虎二段笑、滔博陀螺、闪现撞墙、金身时机、雪球二段、重复出装、探草与抢龙庆祝。名场面有出处，题目是改编情境；没有把二创梗当作真实游戏机制。</p><p>人物匹配、恶搞卡、五人分位都参考本轮真实选择。四个队友出收集者时，挂机、开送、跟着出、补前排分别计分。带特定前提的梗卡必须出现相应反应才会匹配。</p><p>42 位人物、44 个主题条目；37 位有公开参考，5 位示意头像在人物卡里单独说明。故事为架空剧情，不是人物评价或心理诊断。</p><p>全部运行资源已内置，无需账号与后台。首页装备横幅是参考真实图标生成的插画，卡牌与海报里的装备使用原始 PNG 图标。答案只留本机。</p><button class="secondary" data-action="download-html">下载完整离线网页 ↓</button></div>`);}''')
# Replace the whole one-line async function without altering the following poster function.
start=s.index('async function paintPerk(');end=s.index('\n',start)
s=s[:start]+'''async function paintPerk(ctx,a,x,y,size){if(a.visual){ctx.save();ctx.fillStyle='#111d31';ctx.beginPath();ctx.roundRect(x,y,size,size,size*.15);ctx.fill();for(const p of E.artLayout(a)){const im=imageFor(window.WORLD_GAME_ICONS[p.icon].url);await im.decode();const n=p.size*size;ctx.save();ctx.translate(x+(p.x+p.size/2)*size,y+(p.y+p.size/2)*size);ctx.rotate(p.rotation*Math.PI/180);ctx.shadowColor='#020718';ctx.shadowBlur=size*.04;ctx.strokeStyle='#d0b4ff';ctx.lineWidth=Math.max(1,size*.006);ctx.drawImage(im,-n/2,-n/2,n,n);ctx.strokeRect(-n/2,-n/2,n,n);ctx.restore();}ctx.restore();return;}const s=window.WORLD_PERK_SHEET,im=imageFor(s.url),w=s.width/4,h=s.height/4,i=a.icon||0;await im.decode();ctx.drawImage(im,i%4*w,Math.floor(i/4)*h,w,h,x,y,size,size);}'''+s[end:]
s=s.replace('神人档案 / VOL.08 / 网友脑洞风 · 本作自制','神人档案 / VOL.08 / 真实装备梗改 · 本作自制')
s=s.replace("ctx.fillText((a.category||'主题')+'强化 / 本作自制恶搞',350,707)","ctx.fillText(a.visual?a.visual.label+' / 真实图标梗改':(a.category||'主题')+'强化 / 本作自制恶搞',350,707)")
s=s.replace('自制恶搞卡 / 平行宇宙架空剧情 / 人物为本作娱乐设定','真实图标梗改 · 效果自制 / 平行剧情 · 非真实赛史')
insert='''
function questionArt(q){if(q.theme!=='lol')return '';const map={'collector':'collector-union','collector-audit':'collector-union','double-laugh':'double-laugh','tes-top':'tes-top','flash-wall':'flash-wall','golden-time':'double-zhonya','six-swords':'six-infinity','brush':'brush-five','snowball-return':'snowball-hearse'};const a=findCard(map[q.chapter]);return a?`<div class="question-equipment">${perkIcon(a)}<span>${esc(a.visual.label)}<small>场景配图 / 恶搞效果另算</small></span></div>`:'';}
function memeScenes(){return `<section class="meme-scene-section"><img class="meme-banner" src="${window.WORLD_MEME_BANNER}" alt="参考收集者、无尽、帽子和金身图标重绘的装备梗插画"><div class="section-head"><h2>名场面，换你来接。</h2><span>梗有出处 / 情境改编</span></div><div class="meme-scenes">${D.memeReferences.map(m=>`<button data-action="meme" data-id="${m.id}">${portrait(person('lol-'+m.personId))}<strong>${esc(m.title)}</strong><small>${m.series==='rift'?'峡谷排位':'海克斯大乱斗'} · 四幕情境 ↗</small></button>`).join('')}</div></section>`;}
function showMeme(id){const m=D.memeReferences.find(m=>m.id===id);if(!m)return;open(m.title+' · 名场面改编',`<div class="meme-note">${perkIcon(findCard(m.card))}<p>${esc(m.description)}</p><p class="micro">参考：${esc(m.sourceTitle)}。人物反应和卡牌效果是本作娱乐创作。</p><a href="${esc(m.sourcePage)}" target="_blank" rel="noreferrer">查看梗出处（需联网） ↗</a><button class="primary full-width" data-action="meme-start" data-id="${m.id}">这次换我来接梗 · ${count} 题 →</button><p class="tiny">先体验这四幕，再随机加入其他剧场。正式计分。</p></div>`);}
'''
s=s.replace('\nfunction action(e)',insert+'\nfunction action(e)')
s=s.replace("else if(a==='person')", "else if(a==='meme')showMeme(b.dataset.id);else if(a==='meme-start'){const m=D.memeReferences.find(m=>m.id===b.dataset.id);if(m)start(m.chapter,m.series);}else if(a==='person')")
p.write_text(s)
print('V8 renderer applied')
