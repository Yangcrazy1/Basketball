"""Collect an already tested V15 release; never claim platform/device acceptance."""
from pathlib import Path
import hashlib, html, json, shutil, zipfile

R = Path(__file__).resolve().parents[1]
W = R / 'dist/web'
D = json.loads((R / 'src/data.json').read_text())
A = json.loads((R / 'assets/portrait-atlas.json').read_text())
sources = {r['id']: r for r in json.loads((R / 'image-sources.json').read_text())}
browser = json.loads((R / 'docs/browser-check-v15.json').read_text())
required = {'intro', 'new-art', 'collector', 'catalog', 'new-cast', 'cards', 'reveal-portraits', 'quiz', 'posters', 'v10-history', 'v11-history', 'v12-history', 'v13-history', 'new-evidence', 'stories', 'shared-cards', 'standalone-squad', 'offline', 'native-contract', 'runtime-clean'}
assert browser['status'] == 'passed' and required <= set(browser['checkIds'])
assert browser['pendingAvatars'] == []
meta_path = R / 'docs/v15-build-manifest.json'
meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
meta.update(json.loads((R / 'dist/web-build.json').read_text()))
assert browser['html_sha256'] == meta['offline_html_sha256']
assert hashlib.sha256((W / 'world-another-me.html').read_bytes()).hexdigest() == meta['offline_html_sha256']
people = [p for p in D['characters'] if p.get('enabled') is not False]
cards = [a for arr in D['augments'].values() for a in arr if a.get('enabled') is not False]
pending = [p['personId'] for p in people if not A['portraits'].get(p['personId']) or A['portraits'][p['personId']].get('pending')]
assert not pending, pending
assert all(sources.get(p['personId'], {}).get('verifiedReference') is True for p in people)
face_caveats = [{'personId': p['personId'], 'name': p['name'], 'sourceNote': sources[p['personId']].get('note', ''), 'meaning': '已核对公开账号头像来源；不宣称真实面孔已独立核验。'} for p in people if sources[p['personId']].get('faceVerified') is False]
counts = {t: {'people': sum(p['theme'] == t for p in people), 'questions': sum(q.get('enabled') is not False and q['theme'] == t for q in D['questions']), 'cards': sum(a.get('enabled') is not False for a in D['augments'][t])} for t in ['lol', 'basket', 'abstract']}
meta.update(version=15, edition=D.get('edition', '镜面平行宇宙版'), schemaVersion=D['version'], enabledPeople=len(people), verifiedAvatars=len(people), pendingAvatars=[], activeQuestions=sum(c['questions'] for c in counts.values()), cards=len(cards), exclusiveCards=sum(bool(a.get('exclusive')) for a in cards), byTheme=counts, webURL='https://yangcrazy1.github.io/Basketball/v15/', browserGroups=browser['count'], browserDevice=browser['viewport'], historicalSchemas=[10, 11, 12, 13], nativeAcceptance='pending: 创服平台模拟器、Android 真机扫码、iOS 真机扫码')
meta.update(verifiedAvatarSources=len(people), avatarVerificationMeaning='verifiedAvatarSources（旧字段 verifiedAvatars 同义）表示漫画头像均有已核对的公开原型来源与非占位绘图；不表示每张来源照片的真实面孔均已独立核验，也不表示取得商业授权。', faceVerificationCaveats=face_caveats)
meta['appName'] = D['name']
meta['appDescription'] = D.get('description', '')
assert isinstance(meta['appDescription'],str) and len(meta['appDescription']) >= 20
assert D['version'] == 14 and D['releaseVersion'] == 15
assert [counts[t]['people'] for t in ['lol','basket','abstract']] == [22,21,17]
assert sum(c['questions'] for c in counts.values()) == 340 and len(cards) == 180
representative_ids = {card_id for p in people for card_id in p.get('signaturePerks', [])}
assert all(len(p.get('signaturePerks', [])) >= 2 for p in people)
assert representative_ids <= {a['id'] for a in cards}
meta.update(representativeCards=len(representative_ids), representativeAssociations=sum(len(p.get('signaturePerks', [])) for p in people))
assert (len(people), meta['representativeCards'], meta['representativeAssociations']) == (60, 143, 149)
assert not any(p['personId'] == 'renzhengfei' for p in people)
stories = D.get('branchStories', D.get('stories', []))
assert isinstance(stories, list) and len(stories) == len(people)
assert {s['personId'] for s in stories} == {p['personId'] for p in people}
meta['branchStories'] = len(stories)
candidates = D.get('reviewCatalog', {}).get('candidates', [])
assert len(candidates) == len({c['id'] for c in candidates}) == 26
assert all(c.get('enabled') is False and c.get('reason') for c in candidates)
meta['disabledReviewCandidates'] = len(candidates)
meta['frozenHistorySources'] = {str(schema): {name: hashlib.sha256((R / 'src' / directory / name).read_bytes()).hexdigest() for name in ['data.json', 'engine.js']} for schema, directory in [(10, 'legacy'), (11, 'legacy-v11'), (12, 'legacy-v12'), (13, 'legacy-v13')]}
meta.setdefault('artifacts', {})
release = R / 'release'
release.mkdir(exist_ok=True)
shutil.copy2(R / 'dist/world-another-me.html', release / 'world-another-me-v15.html')
downloads = W / 'downloads'
downloads.mkdir(exist_ok=True)
web_zip = release / 'world-another-me-v15-web.zip'
with zipfile.ZipFile(web_zip, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for p in sorted(W.rglob('*')):
        if p.is_file() and p.relative_to(W).parts[0] not in ('downloads', 'screenshots') and p.name not in ('review.html', 'build-info.json') and not p.name.startswith('review-v15-'):
            z.write(p, p.relative_to(W).as_posix())
with zipfile.ZipFile(web_zip) as z:
    assert 'index.html' in z.namelist() and 'world-another-me.html' in z.namelist()
    assert all(n in z.namelist() for n in meta['core_files'])
xhs_zip = release / 'world-another-me-v15-xhs.zip'
assert xhs_zip.stat().st_size <= 10 * 1024 ** 2
with zipfile.ZipFile(xhs_zip) as z:
    assert 'index.html' in z.namelist()
    assert not any(n.startswith(('.git/', 'node_modules/')) or n.endswith(('.map', '.DS_Store')) for n in z.namelist())
    assert not any('review.html' in n or n.startswith('screenshots/') or n.endswith('-v15.png') for n in z.namelist())
    meta['xhsFiles'] = len(z.namelist())
for name in ['world-another-me-v15.html', 'world-another-me-v15-web.zip', 'world-another-me-v15-xhs.zip']:
    p = release / name
    meta['artifacts'][name] = {'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
    if name.endswith('.zip'):
        shutil.copy2(p, downloads / name)

# V15 adds a new logo and cover while retaining the three independent story illustrations.
branding_meta = R / 'assets/branding/branding-v15.json'
branding_files = json.loads(branding_meta.read_text()) if branding_meta.exists() else {}
for name in ['logo', 'cover', 'introRealLife', 'introMirror', 'introNewWorld']:
    configured = branding_files.get(name)
    if isinstance(configured, dict):
        configured = configured.get('png') or configured.get('asset')
    candidates = [R / 'assets' / configured] if isinstance(configured, str) else []
    candidates += [R / 'assets/branding' / (name + '-v15.png'), R / 'assets/branding' / (name + '.png')]
    source = next(p for p in candidates if p.is_file())
    source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
    if name in ['logo', 'cover']:
        old=json.loads((R/'assets/branding/branding-v14.json').read_text())[name]
        assert source_sha != hashlib.sha256((R/'assets'/old['png']).read_bytes()).hexdigest(), name+' still uses V14 PNG artwork'
        assert '-v15.' in source.name, name+' must use the versioned V15 original'
    shutil.copy2(source, downloads / (name + source.suffix))
    meta[name + 'Download'] = './downloads/' + name + source.suffix
    meta[name + 'DownloadSHA256'] = source_sha

# Keep the publication name/description directly selectable and independently
# downloadable, without adding clipboard or network capabilities to the app.
launch_text = '名称：' + D['name'] + '\n\n介绍：' + meta['appDescription'] + '\n'
launch_txt = downloads / 'launch-copy-v15.txt'
launch_txt.write_text(launch_text)
launch_md = downloads / 'launch-copy-v15.md'
shutil.copy2(R / 'content/v15-launch-copy.md', launch_md)
meta['launchCopyDownload'] = './downloads/' + launch_txt.name
meta['launchCopyDownloadSHA256'] = hashlib.sha256(launch_txt.read_bytes()).hexdigest()
meta['launchMarkdownDownload'] = './downloads/' + launch_md.name
meta['launchMarkdownDownloadSHA256'] = hashlib.sha256(launch_md.read_bytes()).hexdigest()

screens = W / 'screenshots'
screens.mkdir(exist_ok=True)
screen_names = ['intro-1.png', 'intro-2.png', 'intro-3.png', 'release-home.png', 'release-home-night.png', 'release-person-detail.png', 'release-card-detail.png', 'release-collector.png', 'release-question.png', 'release-new-draymond-green.png', 'release-new-ershu.png', 'release-new-caixukun.png', 'release-new-369.png', 'release-result-caixukun.png', 'release-result-369.png', 'release-reveal-lol.png', 'release-reveal-basket.png', 'release-reveal-abstract.png', 'release-result-lol.png', 'release-result-basket.png', 'release-result-abstract.png', 'release-team.png', 'team-poster.png', 'standalone-team-poster.png', 'story-poster.png', 'release-story-alternate.png'] + ['release-story-' + pid + '.png' for pid in ['dailanzi', 'huchenfeng', 'fengge', 'luobenwei', 'xujingyu', 'draymond-green', 'ershu', 'caixukun', '369']]
for name in screen_names:
    shutil.copy2(R / 'dist/qa/v15' / name, screens / name)
meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')

# The review reads the exact deployed data bundle: no second handwritten content copy.
data_scripts = [name for name in meta['core_files'] if name.startswith('data-') and name.endswith('.js')]
assert len(data_scripts) == 1
review_js = r'''(function(){'use strict';
var d=window.WORLD_DATA,allCards=[].concat.apply([],Object.values(d.augments)).concat(d.reviewCatalog&&d.reviewCatalog.candidates||[]),people=d.characters,
samples=['dailanzi','huchenfeng','fengge','luobenwei','xujingyu'],featured=samples.concat(['draymond-green','ershu','caixukun','369']),
state={mode:'samples',theme:'all',query:'',person:null},grid=document.getElementById('review-grid'),detail=document.getElementById('review-detail'),returnFocus=null;
function esc(s){return String(s===null||s===undefined?'':s).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
function owners(a){return a.owners||a.signatureFor||(a.owner?[a.owner]:[]);}
function cardsFor(p,enabledOnly){return allCards.filter(function(a){return (!enabledOnly||a.enabled!==false)&&(owners(a).indexOf(p.personId)>=0||(p.signaturePerks||[]).indexOf(a.id)>=0);});}
function stories(){var s=d.branchStories||d.stories||[];return Array.isArray(s)?s:Object.values(s);}
function storyFor(p){return stories().find(function(s){return s.personId===p.personId;});}
function status(a){return a.sourceStatus||a.sourceVerification||'未记录';}
function pending(a){return /pending|partial|unverified|待核|未核|需核/i.test(status(a))||(/indexed/.test(status(a))&&a.originalVideoWatched===false);}
function changed(p){return p.releaseVersion===15||p.modifiedIn==='v15'||cardsFor(p,false).some(function(a){return /^v15[-:]/.test(a.id)||a.editorialStatus==='selected_for_implementation';})||(storyFor(p)&&/^v15[-:]/.test(storyFor(p).id));}
function portrait(p){var m=window.WORLD_PORTRAITS[p.personId];if(!m||m.pending)return '<span class="portrait missing">'+esc(p.name)+'<small>头像待补</small></span>';var s=window.WORLD_ATLASES[m.sheet],w=s.width/2,h=s.height/2;return '<span class="portrait" data-avatar="'+esc(p.personId)+'"><svg viewBox="'+[m.cell%2*w,Math.floor(m.cell/2)*h,w,h].join(' ')+'" role="img" aria-label="'+esc(p.name)+'漫画头像"><image width="'+s.width+'" height="'+s.height+'" href="'+esc(s.url)+'" xlink:href="'+esc(s.url)+'" /></svg></span>';}
function art(a){if(a.enabled===false&&!a.visual&&!a.classicSprite&&!a.artAsset)return '';if(a.visual)return '<div class="card-art equipment">'+a.visual.icons.map(function(id){var x=window.WORLD_GAME_ICONS[id];return x?'<img src="'+esc(x.url)+'" alt="'+esc(x.name||id)+'">':'';}).join('')+'</div>';var m=a.classicSprite||{sheet:0,cell:a.icon||0},s=(window.WORLD_PERK_SHEETS||[window.WORLD_PERK_SHEET])[m.sheet];if(!s)return '';var w=s.width/4,h=s.height/4;return '<div class="card-art"><svg viewBox="'+[m.cell%4*w,Math.floor(m.cell/4)*h,w,h].join(' ')+'" role="img" aria-label="'+esc(a.name)+'漫画图标"><image width="'+s.width+'" height="'+s.height+'" href="'+esc(s.url)+'" xlink:href="'+esc(s.url)+'" /></svg></div>';}
function sources(a){var values=a.sources||a.sourceRecords||a.sourceLinks||a.sourceURLs||a.sourceUrls||[];if(!Array.isArray(values))values=[values];if(a.sourceURL)values.push(a.sourceURL);return values.map(function(s){var url=typeof s==='string'?s:s.url||s.sourcePage||s.sourceURL||s.sourceUrl||'',label=typeof s==='string'?s:s.label||s.title||url;if(!/^https?:\/\//.test(url))return '<span>'+esc(label||JSON.stringify(s))+'</span>';return '<a href="'+esc(url)+'" target="_blank" rel="noopener noreferrer">'+esc(label)+'</a>'+(typeof s==='object'&&s.note?'<br><small>'+esc(s.note)+'</small>':'');}).join('<br>')||'<span>见来源说明与梗线索；未声称完整观看原片。</span>';}
function avatarReference(p){var r=(window.WORLD_SOURCES||[]).find(function(r){return r.id===p.personId;});if(!r)return '<p>未记录头像来源。</p>';return '<details><summary>头像来源与核验边界</summary>'+block('公开来源',r.sourcePage)+block('来源核对',r.verifiedReference?'已核对公开参考来源':'待核')+block('面容说明',r.faceVerified===false?'未独立核验完整真实面容；按公开账号头像姿态绘制。':'来源核对不等于取得商业许可或本人背书。')+block('记录',r.note)+block('权利',r.rights)+'</details>';}
function block(label,value){return value?'<p><b>'+esc(label)+'：</b>'+esc(typeof value==='string'?value:JSON.stringify(value))+'</p>':'';}
function card(a){var names=owners(a).map(function(id){var p=people.find(function(p){return p.personId===id;});return p?p.name:id;});return '<article class="review-card '+(a.enabled===false&&!a.visual&&!a.classicSprite&&!a.artAsset?'no-art':'')+'" data-card="'+esc(a.id)+'">'+art(a)+'<div><h3>'+esc(a.name)+' <small>'+(a.enabled!==false?'启用':'禁用')+'</small></h3>'+block('适用人物',names.join('、')||'共通卡')+block('卡片 ID',a.id)+block('未实施原因',a.reason)+block('本轮状态',a.enabled===false?'未实施；不进入随机池、结果、故事奖励和默认标签。':'当前启用')+block('效果',a.effect)+block('触发场景',a.triggerScene||a.trigger)+block('笑点回收',a.punchline)+block('原梗',a.sourceMeme||a.creation)+block('来源状态',status(a))+block('来源核验说明',a.sourceVerificationNote||a.sourceNote)+block('原片完整观看',a.originalVideoWatched===true?'已完整观看':a.originalVideoWatched===false?'未完整观看；记录仅为公开传播线索':'未记录，不声称已观看')+block('编辑选择',a.editorialStatus)+block('二创',a.fanMade?'卡片效果与故事为本作二创':'见实际来源说明')+block('题目证据',a.evidenceQuestionIds||[])+block('精确选项证据',a.answerEvidence||[])+block('触发规则',a.behaviorRules||a.requires)+'<details><summary>来源记录</summary><div class="source-links">'+sources(a)+'</div></details></div></article>';}
function node(n){return '<details class="story-node"><summary>'+esc(n.id)+' · '+esc(n.title||'剧情节点')+'</summary>'+block('正文',n.text)+block('下一节点',n.next)+(n.variants||[]).map(function(v){return '<blockquote>'+block('条件',v.when)+block('标题',v.title)+block('分支正文',v.text)+'</blockquote>';}).join('')+(n.cardEvents||[]).map(function(e){return '<div class="card-event">'+block('卡片',e.cardId||e.cardName)+block('已获得时',e.owned)+block('未获得时',e.unowned)+'</div>';}).join('')+(n.choices||[]).map(function(c){return '<div class="story-choice">'+block('选项 '+c.id,c.text)+block('具体后果',c.effect)+block('跳转',c.next)+block('获得卡片',c.grantCards||c.grantCardIds||c.grantCardNames)+block('标记',c.flags)+'</div>';}).join('')+'</details>';}
function personPanel(p){var story=storyFor(p),cards=cardsFor(p,false).filter(function(a){return state.mode==='disabled'&&p.enabled!==false?a.enabled===false:state.mode==='pending'?pending(a):true;}),questionIds=new Set([].concat.apply([],cards.map(function(a){return a.evidenceQuestionIds||[];})).concat(Object.keys(p.answerAffinities||{}),Object.keys(p.optionAffinities||{}))),questions=d.questions.filter(function(q){return q.personId===p.personId||q.personContext===p.personId||questionIds.has(q.id);});return '<button class="secondary" data-review-back>← 返回名单与原滚动位置</button><div class="person-heading">'+portrait(p)+'<div><small>'+esc(p.theme)+' / '+esc(p.personId)+' / '+(p.enabled!==false?'启用':'禁用')+'</small><h2>'+esc(p.name)+'</h2>'+block('别名',(p.aliases||[]).join('、'))+block('简介',p.line||p.teamLine||p.universe&&p.universe.arrival)+'<a class="button" href="./?story='+encodeURIComponent(p.personId)+'">直接试玩这条穿越故事 ↗</a></div></div><h2>代表卡片与共享关联</h2>'+cards.map(card).join('')+'<h2>实际故事节点、选择与结局</h2>'+(story?'<p>'+esc(story.title)+' · 入口 '+esc(story.entry)+' · 二创架空剧情</p>'+story.nodes.map(node).join(''):'<p>未找到故事，此项应在发布前修复。</p>')+'<details class="question-review"><summary>相关题目与四个实际选项（'+questions.length+'）</summary>'+questions.map(function(q){return '<article><h3>'+esc(q.title||q.text)+'</h3>'+block('题目 ID',q.id)+block('场景',q.scene)+(q.options||[]).map(function(o){return block('选项 '+o.id,o.text)+block('对应卡片',o.cardIds||o.cardNames||[]);}).join('')+'</article>';}).join('')+'</details><button class="secondary" data-review-back>← 返回名单</button>';}
function draw(){state.person=null;detail.hidden=true;grid.hidden=false;document.getElementById('review-controls').hidden=false;grid.classList.toggle('common-list',state.mode==='common');if(state.mode==='common'){var common=allCards.filter(function(a){return a.enabled!==false&&owners(a).length===0&&(state.theme==='all'||a.theme===state.theme)&&(!state.query||(a.name+' '+a.effect).toLowerCase().indexOf(state.query.toLowerCase())>=0);});document.getElementById('review-count').textContent='当前显示 '+common.length+' 张启用共通海克斯。';grid.innerHTML=common.map(card).join('')||'<p>没有符合条件的共通卡。</p>';document.querySelectorAll('[data-review-mode]').forEach(function(b){b.setAttribute('aria-pressed',String(b.dataset.reviewMode===state.mode));});return;}var shown=people.filter(function(p){if(state.theme!=='all'&&p.theme!==state.theme)return false;var cs=cardsFor(p,false);if(state.mode==='samples'&&featured.indexOf(p.personId)<0)return false;if(state.mode==='active'&&p.enabled===false)return false;if(state.mode==='disabled'&&p.enabled!==false&&!cs.some(function(a){return a.enabled===false;}))return false;if(state.mode==='pending'&&!cs.some(pending))return false;if(state.mode==='changed'&&!changed(p))return false;var text=[p.name,p.nickname,p.personId].concat(p.aliases||[],cs.map(function(a){return a.name;})).join(' ').toLowerCase();return !state.query||text.indexOf(state.query.toLowerCase())>=0;});if(state.mode==='samples')shown.sort(function(a,b){return featured.indexOf(a.personId)-featured.indexOf(b.personId);});document.getElementById('review-count').textContent='当前显示 '+shown.length+' 位人物；活动 '+people.filter(function(p){return p.enabled!==false;}).length+' 位。';grid.innerHTML=shown.map(function(p){var cards=state.mode==='disabled'?cardsFor(p,false).filter(function(a){return a.enabled===false;}):state.mode==='pending'?cardsFor(p,false).filter(pending):cardsFor(p,true);return '<button class="review-person" data-review-person="'+esc(p.personId)+'">'+portrait(p)+'<strong>'+esc(p.name)+'</strong><small>'+esc((p.aliases||[]).slice(0,3).join(' / '))+'</small><span>'+cards.length+(state.mode==='disabled'?' 张未启用候补':state.mode==='pending'?' 张来源待核项目':' 张启用代表卡')+' · '+(p.enabled!==false?'启用':'禁用')+'</span><p>'+esc(cards.map(function(a){return a.name;}).join(' · '))+'</p></button>';}).join('')||'<p>没有符合条件的项目。</p>';document.querySelectorAll('[data-review-mode]').forEach(function(b){b.setAttribute('aria-pressed',String(b.dataset.reviewMode===state.mode));});}
var savedScroll=0;
function showPerson(id){var p=people.find(function(p){return p.personId===id;});if(!p)return;savedScroll=window.pageYOffset;returnFocus=document.activeElement;state.person=id;detail.innerHTML=personPanel(p);grid.hidden=true;document.getElementById('review-controls').hidden=true;detail.hidden=false;detail.focus();window.scrollTo(0,0);}
function back(){var id=state.person;draw();window.scrollTo(0,savedScroll);if(returnFocus&&document.contains(returnFocus))returnFocus.focus();else{var b=document.querySelector('[data-review-person="'+id+'"]');if(b)b.focus();}}
document.addEventListener('click',function(e){var b=e.target.closest('[data-review-mode],[data-review-person],[data-review-back]');if(!b)return;if(b.hasAttribute('data-review-back'))back();else if(b.dataset.reviewMode){state.mode=b.dataset.reviewMode;draw();}else showPerson(b.dataset.reviewPerson);});
document.getElementById('review-theme').addEventListener('change',function(e){state.theme=e.target.value;draw();});var timer;document.getElementById('review-search').addEventListener('input',function(e){clearTimeout(timer);var q=e.target.value;timer=setTimeout(function(){state.query=q;draw();},150);});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&state.person){e.preventDefault();back();}});document.addEventListener('error',function(e){if(e.target&&e.target.tagName==='IMG'){e.target.alt='图片暂不可用；正文和操作仍可使用。';}},true);
draw();var query=new URLSearchParams(window.location.search).get('person');if(query)showPerson(query);
})();'''
review_name = 'review-v15-' + hashlib.sha256(review_js.encode()).hexdigest()[:12] + '.js'
(W / review_name).write_text(review_js)

def pic(name, alt):
    return '<a href="./screenshots/' + name + '"><img loading="lazy" src="./screenshots/' + name + '" alt="' + html.escape(alt, quote=True) + '"></a>'

screens_html = ''.join(pic(f'intro-{i}.png', f'V15简约绘本开场第{i}幕') for i in [1, 2, 3])
downloads_html = ''.join('<a class="button secondary" href="' + html.escape(meta[name + 'Download'], quote=True) + '" download>' + label + ' ↓</a>' for name, label in [('logo', '简约 Logo'), ('cover', '镜面封面'), ('introRealLife', '第一幕原稿'), ('introMirror', '第二幕原稿'), ('introNewWorld', '第三幕原稿')])
downloads_html += '<a class="button secondary" href="' + meta['launchCopyDownload'] + '" download>名称与介绍 TXT ↓</a><a class="button secondary" href="' + meta['launchMarkdownDownload'] + '" download>发布资料 Markdown ↓</a>'
avatar_caveats = '全部活动人物均有核对过的公开头像原型；来源核对不等于独立核验真实面孔或取得商业授权。' + ('其中 ' + '、'.join(c['name'] for c in face_caveats) + ' 按公开账号头像绘制，不宣称已独立核验完整面容。' if face_caveats else '')
summary = f"{len(people)} 位活动人物 · {meta['representativeCards']} 张去重代表卡 · {meta['representativeAssociations']} 个人物关联 · {meta['cards']} 张全部启用卡 · {meta['activeQuestions']} 道情境题"
page = r'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>平行宇宙的另一个我 V15 · 实际内容审阅与下载</title><style>
*{box-sizing:border-box}body{margin:0;background:#faf7ef;color:#302e2a;font:16px -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;line-height:1.75}main{max-width:1120px;margin:auto;padding:28px 24px 80px}h1{font-size:34px;line-height:1.4}h2{font-size:24px;margin:26px 0 15px}h3{margin:0 0 10px;font-size:19px}p{margin:9px 0;overflow-wrap:break-word}a{color:#476052}button,input,select{font:inherit}button,a{touch-action:manipulation}button{cursor:pointer}button:focus,a:focus,input:focus,select:focus{outline:3px solid #648c78;outline-offset:3px}[hidden]{display:none!important}.button,.secondary,.filters button{display:inline-flex;align-items:center;justify-content:center;min-height:45px;margin:7px 8px 7px 0;padding:10px 16px;background:#537562;color:white;border:1px solid #537562;border-radius:12px;text-decoration:none;font-weight:650}.secondary,.filters button{background:#fffdf7;color:#476052}.filters button[aria-pressed=true]{background:#537562;color:white}.summary{color:#66675d}.note,small{font-size:13px;color:#6f746d}.progress{height:8px;width:100%;accent-color:#648c78}article.panel{padding:24px;border:1px solid #d4d8c9;border-radius:18px;background:#fffdf8;margin:25px 0}.gallery{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));grid-gap:15px}.gallery img{width:100%;border-radius:10px}.controls{position:relative;margin:25px 0}.fields{display:flex;flex-wrap:wrap;margin:12px -5px}.fields label{display:flex;flex-direction:column;flex:1;min-width:200px;margin:5px}input,select{width:100%;min-height:46px;padding:10px 12px;border:1px solid #b9c7b7;border-radius:10px;background:white}.review-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));grid-gap:16px}.review-person{display:flex;flex-direction:column;align-items:stretch;background:#fffdf8;color:inherit;text-align:left;border:1px solid #d4d8c9;border-radius:16px;padding:12px;min-width:0}.review-person strong{font-size:18px;margin:10px 0 5px}.review-person p{font-size:12px;color:#5d6f5d}.review-person span:not(.portrait){font-size:12px}.portrait{display:block;position:relative;width:100%;overflow:hidden;border-radius:12px;background:#edeade}.portrait:before{content:'';display:block;padding-top:100%}.portrait>svg{position:absolute;left:0;top:0;width:100%;height:100%}.missing{padding:30px;min-height:100px}.person-heading{display:grid;grid-template-columns:240px 1fr;grid-gap:28px;margin:20px 0}.review-card{display:grid;grid-template-columns:130px 1fr;grid-gap:22px;padding:20px 0;border-top:1px solid #d4d8c9}.card-art{width:100%;position:relative}.card-art:before{content:'';display:block;padding-top:100%}.card-art>svg{position:absolute;top:0;left:0;width:100%;height:100%}.equipment{display:flex;flex-wrap:wrap;align-items:flex-start}.equipment:before{display:none}.equipment img{width:45%;margin:2%;height:auto}.review-grid.common-list{display:block}.review-card>div{min-width:0}.review-card.no-art{grid-template-columns:1fr}.review-card p{font-size:14px}.source-links{word-break:break-all;font-size:12px}.story-node,.question-review{padding:14px 18px;border:1px solid #d4d8c9;border-radius:12px;margin:12px 0;background:#fffdf8}summary{cursor:pointer;min-height:34px;font-weight:650}blockquote,.story-choice,.card-event{margin:15px 0;padding:10px 18px;border-left:3px solid #a5b8a1;background:#f1f4e9}.question-review article{border-top:1px solid #d4d8c9;padding:18px 0}.sample-links a{display:inline-block;padding:10px;margin:4px 5px 4px 0;border:1px solid #a6b9a3;border-radius:8px}.download-area{margin-top:45px}code{font-size:11px;overflow-wrap:anywhere}@media(max-width:760px){main{padding:20px 16px 60px}.review-grid{grid-template-columns:repeat(2,minmax(0,1fr));grid-gap:12px}.person-heading{grid-template-columns:150px 1fr;grid-gap:16px}.review-card{grid-template-columns:100px 1fr;grid-gap:15px}h1{font-size:28px}.gallery{grid-template-columns:1fr}.gallery img{display:block;max-width:393px;margin:auto}}@media(max-width:430px){.person-heading{grid-template-columns:1fr}.person-heading>.portrait{max-width:260px}.review-card{grid-template-columns:1fr}.review-card>.card-art{max-width:130px}.fields label{min-width:100%}.review-person strong{font-size:16px}}@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}
</style></head><body><main><small>平行宇宙的另一个我 / V15 · 实际内容审阅</small><h1>同一套人物、海克斯和故事，<br>在这里逐条看清楚。</h1><p class="summary">__SUMMARY__</p><p>__DESCRIPTION__</p><progress class="progress" max="100" value="100" aria-label="本轮网页开发和记录的浏览器检查已完成"></progress><p><a class="button" href="./">手机直接打开玩 ↗</a><a class="button secondary" href="./world-another-me.html" download="平行宇宙的另一个我-V15-离线版.html">完整离线网页 ↓</a></p><p class="note">本页直接读取本次玩家入口的数据包，不把旧版卡名或手写摘要冒充当前内容。梗来源仅表示公开传播线索，全部卡片效果和剧情均为本作架空二创；未声称完整观看受限原片。</p><section class="sample-links"><h2>先试玩五组样板与新朋友</h2>__SAMPLE_LINKS__</section><section id="review-controls" class="controls"><div class="filters" role="group" aria-label="内容审阅筛选"><button data-review-mode="samples" aria-pressed="true">五组样板与新增</button><button data-review-mode="active">全部活动人物</button><button data-review-mode="common">共通海克斯</button><button data-review-mode="changed">只看本轮修改</button><button data-review-mode="disabled">只看禁用项</button><button data-review-mode="pending">只看来源待核</button><button data-review-mode="all">全部记录</button></div><div class="fields"><label>主题<select id="review-theme"><option value="all">全部宇宙</option value="lol">英雄联盟</option><option value="basket">篮球梦之队</option><option value="abstract">抽象热梗</option></select></label><label>人物别名与卡名<input id="review-search" type="search" placeholder="试试阿水、本升专、八角笼见"></label></div><p id="review-count" aria-live="polite"></p></section><section id="review-grid" class="review-grid" aria-label="实际人物名单"></section><section id="review-detail" tabindex="-1" hidden aria-label="实际人物与剧情详情"></section>
<section class="download-area"><article class="panel"><h2>三张独立绘本开场</h2><div class="gallery">__INTRO__</div><p class="note">以上为本次 393×852 Chromium 手机视口实际截图，非实体手机拍摄。运行图使用三张独立 WebP，标题、正文和操作由前端排版。</p></article><article class="panel"><h2>单独下载与部署产物</h2>__DOWNLOADS__<a class="button secondary" href="./downloads/world-another-me-v15-web.zip" download>网页部署 ZIP ↓</a><a class="button secondary" href="./downloads/world-another-me-v15-xhs.zip" download>小红书待上传 ZIP ↓</a><p class="note">离线 HTML 约 __OFFLINE__ MiB；小红书 ZIP 约 __XHS__ MiB。手机直接体验可用顶部网页入口。小红书包内只有运行资源，不含本审阅页与原始 PNG。</p></article><details class="panel"><summary>实际校验结果与待验证项目</summary><p>__BROWSER__ 组浏览器检查通过，覆盖三主题题量、故事选择与卡片记录、共享卡、全量图鉴、旧 schema10／11／12／13 重放、真实 PNG／HTML 导出和无网络运行。普通 Chromium 和 SDK 模拟检查不能替代小红书容器验收。</p><p>平台模拟器、Android 真机扫码和 iOS 真机扫码仍待用户验证，使用同一 ZIP。Chrome61 CSS 兼容性、旧设备性能与实际安全区没有实机结果。ZIP 小于10 MiB硬上限；超过2 MiB推荐值与大文本风险已保留在审计报告，不以高压缩率当性能证明。</p><p>__AVATAR_CAVEATS__</p><p>离线 HTML SHA-256：<code>__SHA__</code></p></details></section></main><script src="./__DATA_SCRIPT__"></script><script src="./__REVIEW_SCRIPT__"></script></body></html>'''
sample_links = ''.join('<a href="./?story=' + p['personId'] + '">' + html.escape(p['name']) + ' ↗</a>' for pid in ['dailanzi', 'huchenfeng', 'fengge', 'luobenwei', 'xujingyu', 'draymond-green', 'ershu', 'caixukun', '369'] for p in people if p['personId'] == pid)
for key, value in {'__SUMMARY__': html.escape(summary), '__DESCRIPTION__':html.escape(meta['appDescription']), '__SAMPLE_LINKS__': sample_links, '__INTRO__': screens_html, '__DOWNLOADS__': downloads_html, '__OFFLINE__': f"{meta['offline_html_bytes']/1024**2:.1f}", '__XHS__': f"{meta['artifacts']['world-another-me-v15-xhs.zip']['bytes']/1024**2:.2f}", '__BROWSER__': str(browser['count']), '__AVATAR_CAVEATS__': html.escape(avatar_caveats), '__SHA__': meta['offline_html_sha256'], '__DATA_SCRIPT__': data_scripts[0], '__REVIEW_SCRIPT__': review_name}.items():
    page = page.replace(key, value)
assert '__SUMMARY__' not in page
(R / 'docs/v15-review.html').write_text(page)
(W / 'review.html').write_text(page)
# The hosted review offers release ZIPs. Its archive copy contains the same
# content and image downloads without a recursive link to its own ZIP.
archive_page = page
for name, label in [('world-another-me-v15-web.zip', '网页部署 ZIP'), ('world-another-me-v15-xhs.zip', '小红书待上传 ZIP')]:
    archive_page = archive_page.replace('<a class="button secondary" href="./downloads/' + name + '" download>' + label + ' ↓</a>', '')
with zipfile.ZipFile(web_zip, 'a', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    z.writestr('review.html', archive_page)
    z.writestr(review_name, review_js)
    for name in ['logo', 'cover', 'introRealLife', 'introMirror', 'introNewWorld']:
        filename = meta[name + 'Download'].removeprefix('./')
        z.write(W / filename, filename)
    for i in [1, 2, 3]:
        z.write(screens / f'intro-{i}.png', f'screenshots/intro-{i}.png')
    for source in [launch_txt, launch_md]:
        z.write(source, 'downloads/' + source.name)
meta['artifacts'][web_zip.name] = {'bytes': web_zip.stat().st_size, 'sha256': hashlib.sha256(web_zip.read_bytes()).hexdigest()}
shutil.copy2(web_zip, downloads / web_zip.name)
meta['reviewScript'] = review_name
meta['reviewDataScript'] = data_scripts[0]
meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'review': str(W / 'review.html'), 'people': len(people), 'representativeCards': len(representative_ids), 'artifacts': meta['artifacts']}, ensure_ascii=False, indent=2))
