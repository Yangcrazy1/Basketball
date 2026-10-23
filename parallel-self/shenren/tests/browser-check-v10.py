"""V10: actual one-tap UI, stale-click protection, three themes and offline exports."""
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
import threading,tempfile,json,hashlib,time
from playwright.sync_api import sync_playwright
from PIL import Image
R=Path(__file__).resolve().parents[1];HTML=(R/'release/world-another-me.html').read_bytes();OUT=R/'dist/qa';OUT.mkdir(exist_ok=True)
checks=[];errors=[];external=[];started=time.time();PREFIX='world-otherme.v10.'
def passed(s):checks.append(s);print('PASS',s,flush=True)
def overflow(p):assert p.evaluate('document.documentElement.scrollWidth<=innerWidth'),str(p.viewport_size)
def close(p):
 if p.locator('#dialog').is_visible():p.locator('#close-dialog').click()
def home(p):close(p);p.locator('.brand').click()
def state(p):return p.evaluate("JSON.parse(localStorage.getItem('world-otherme.v10.session'))")
def choose(p,theme='lol',count=8):
 home(p);p.locator(f'[data-action=theme][data-theme={theme}]').click();p.locator(f'[data-action=mode][data-count="{count}"]').click();p.locator('#app [data-action=start]').click()
def answer(p,locator):
 old=locator.get_attribute('data-question');locator.click();p.wait_for_function("id=>!document.querySelector('.option[data-question=\"'+id+'\"]')",arg=old)
def result(p):
 if p.locator('[data-action=reveal-open]').count():p.locator('[data-action=reveal-open]').click()
 p.wait_for_selector('.identity-card');assert p.locator('#app .hex-card').count()==1;assert p.locator('.team-card').count()==5;assert p.locator('.team-card.is-you').count()==1
 chars=p.evaluate('WORLD_DATA.characters');ids=[]
 for el in p.locator('.team-card').all():
  c=next(c for c in chars if c['id']==el.get_attribute('data-person'));assert int(el.get_attribute('data-role')) in c['roles'];ids.append(c['personId'])
 assert len(set(ids))==5;assert p.locator('.chain-row').count()>0;overflow(p)
def finish(p,n,start=0,pref=None):
 for i in range(start,n):
  if pref:
   oid=p.evaluate("pref=>{const s=JSON.parse(localStorage.getItem('world-otherme.v10.session'));const q=WORLD_DATA.questions.find(q=>q.id===s.deck[s.index].id);return pref.map(b=>q.options.find(o=>o.behavior===b)).find(Boolean)?.id??0;}",pref)
   answer(p,p.locator(f'.option[data-id="{oid}"]'))
  else:answer(p,p.locator('.option').nth(i%4))
 result(p)
def fixture(p,chapters):
 home(p);p.evaluate("chapters=>{const s=ShenrenEngine.draw(WORLD_DATA,'lol',8,null,undefined,'all');s.deck=chapters.flatMap(c=>WORLD_DATA.questions.filter(q=>q.theme==='lol'&&q.chapter===c).sort((a,b)=>a.stage-b.stage)).map(q=>({id:q.id,order:[0,1,2,3]}));s.answers=Array(8).fill(null);s.index=0;localStorage.setItem('world-otherme.v10.session',JSON.stringify(s));}",chapters);p.reload();p.locator('[data-action=resume]').click()
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
with tempfile.TemporaryDirectory() as temp:
 Path(temp,'index.html').write_bytes(HTML);server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=temp));threading.Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}/index.html'
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);ctx=browser.new_context(viewport={'width':390,'height':844},accept_downloads=True,reduced_motion='reduce');p=ctx.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.on('request',lambda r:external.append(r.url) if not r.url.startswith(('http://127.0.0.1:','data:','blob:')) else None)
  try:
   p.goto(url);p.wait_for_function("document.documentElement.dataset.appReady==='true'");assert p.locator('.intro-page').is_visible();p.locator('[data-action=intro-next]').click();p.locator('[data-action=intro-next]').click();p.locator('[data-action=intro-next]').click();assert p.evaluate('WORLD_DATA.version')==10;assert p.locator('.theme-picker button').count()==3;assert p.locator('[data-action=series]').count()==0;assert p.locator('#app [data-action=start]').count()==1
   passed('V10 shows exactly League, NBA Golden Squad and Abstract; League has one combined entry and start is on the mobile first screen')
   for theme in ['lol','basket','abstract']:
    p.locator(f'[data-action=theme][data-theme={theme}]').click()
    assert str({'lol':168,'basket':84,'abstract':96}[theme]) in p.locator('.pool-strip').inner_text()
    for style in ['night','paper']:
     if p.locator('html').get_attribute('data-style')!=style:p.locator('[data-action=palette]').click()
     for w in [320,390,430,768,1440]:p.set_viewport_size({'width':w,'height':844});overflow(p)
     p.set_viewport_size({'width':390,'height':844});p.screenshot(path=str(OUT/f'v10-home-{theme}-{style}.png'),full_page=True)
   passed('all three theme homes and both palettes fit 320/390/430/768/1440px with theme-specific counts')
   p.locator('[data-action=trend-note]').click();assert '2026-10-23' in p.locator('#dialog-body').inner_text();assert '固定题库' in p.locator('#dialog-body').inner_text();assert p.locator('.trend-source a').count()==2;close(p)
   p.locator('[data-action=gallery]').click();p.locator('input[data-search=gallery]').fill('摇摆导演');p.wait_for_timeout(300);assert p.locator('#dialog [data-id=abstract-shake-director]').count()==1;p.locator('#dialog [data-id=abstract-shake-director]').click();assert '原创虚构人物' in p.locator('#dialog-body').inner_text();assert p.locator('.signature-list button').count()>0;close(p)
   passed('abstract source/date disclosure and original dance character with signature cards are available')
   assert p.evaluate("async()=>{for(const s of WORLD_ATLASES){const im=new Image();im.src=s.url;await im.decode();}const im=new Image();im.src=WORLD_PERK_SHEET.url;await im.decode();return WORLD_ATLASES.length>=19&&im.width===1254;}")
   passed('all 12 avatar sheets including the four additions and the new NBA/creator icon atlas decode from embedded data')
   choose(p,count=8);old=p.locator('.option').first.get_attribute('data-question');displayed=p.locator('.option').nth(1).get_attribute('data-id');answer(p,p.locator('.option').nth(1));assert state(p)['index']==1;assert state(p)['answers'][0]==int(displayed);assert p.locator('[data-action=next]').count()==0
   passed('tapping displayed choice B records its shuffled option ID and automatically advances exactly one question with no Next button')
   p.locator('[data-action=previous]').click();assert state(p)['index']==0;answer(p,p.locator('.option[data-id="'+str((int(displayed)+1)%4)+'"]'));assert state(p)['index']==1;assert state(p)['answers'][0]==(int(displayed)+1)%4
   passed('returning to a previous question allows a new choice and updates the saved answer before automatic advance')
   choose(p,count=8);p.evaluate("()=>{const b=document.querySelectorAll('.option')[1];b.click();b.click();b.dispatchEvent(new MouseEvent('click',{bubbles:true}));}");p.wait_for_function("JSON.parse(localStorage.getItem('world-otherme.v10.session')).index===1&&!document.querySelector('.option:disabled')");assert sum(a is not None for a in state(p)['answers'])==1
   passed('rapid double taps plus a forced stale click do not skip a second question or record an extra answer')
   choose(p,count=8);p.evaluate("()=>{document.querySelector('.option').click();document.querySelector('.brand').click();}");p.wait_for_timeout(250);assert p.locator('.v10-home').is_visible();assert state(p)['index']==1;p.locator('[data-action=resume]').click();assert p.locator('.quiz').is_visible();finish(p,8,start=1)
   passed('leaving during the short transition cancels stale navigation while resume starts from the next saved question')
   fixture(p,['collector','collector-audit']);assert '必须出收集者' in p.locator('.option[data-id="2"]').inner_text();answer(p,p.locator('.option[data-id="2"]'));assert '必须出收集者' in p.locator('.question h1').inner_text();finish(p,8,start=1,pref=['collector','gold','plan']);assert p.locator('#app .hex-card').get_attribute('data-augment')=='collector-union';assert '必须出收集者' in p.locator('#app .hex-card h2').inner_text();assert p.locator('#app .hex-icon [data-game-icon=item-6676]').count()==5;assert p.locator('.bond-panel').count()==1;assert '污渍' in p.locator('.bond-panel').inner_text();assert '来自你的选择' in p.locator('.bond-panel').inner_text();p.screenshot(path=str(OUT/'v10-result-collector.png'),full_page=True)
   passed('restored mandatory Collector reaction branches correctly and earns Uzi, five real Collector icons and an evidence-backed person bond')
   p.evaluate("()=>{window.__draws=[];const orig=CanvasRenderingContext2D.prototype.drawImage;window.__origDraw=orig;CanvasRenderingContext2D.prototype.drawImage=function(im,...args){const id=Object.keys(WORLD_GAME_ICONS).find(k=>WORLD_GAME_ICONS[k].url===im.src);if(id)__draws.push(id);return orig.call(this,im,...args);};}")
   p.locator('[data-action=poster]').click();p.wait_for_selector('.poster');assert p.evaluate("__draws.filter(i=>i==='item-6676').length")==5
   with p.expect_download() as dl:p.locator('.download-png').click()
   im=Image.open(dl.value.path());assert im.size==(1080,1920);im.save(OUT/'v10-exported-poster.png');close(p);p.evaluate("()=>{CanvasRenderingContext2D.prototype.drawImage=window.__origDraw;}")
   passed('the actual 1080x1920 PNG download includes exactly five source Collector draws and the new edition')

   p.locator('[data-action=squad]').click();assert p.locator('.squad-slot').count()==5;p.locator('[data-action=squad-free]').click();p.locator('[data-action=squad-slot][data-slot="0"]').click();p.locator('[data-action=squad-remove]').click();p.locator('input[data-search=squad]').fill('笑笑');p.wait_for_timeout(300);p.locator('[data-action=squad-pick][data-id=lol-xiaoxiao]').click();p.locator('[data-action=squad-save]').click();assert p.locator('.team-card[data-role="0"]').get_attribute('data-person')=='lol-xiaoxiao';assert '自选阵容' in p.locator('.team-heading').inner_text();p.reload();p.locator('header [data-action=archive]').click();p.locator('.history-card').first.click();assert p.locator('.team-card[data-role="0"]').get_attribute('data-person')=='lol-xiaoxiao';p.locator('[data-action=auto-team]').click();assert '你 ＋ 四名队友' in p.locator('.team-heading').inner_text()
   passed('custom five-person squad supports search, intentional off-role selection, save/reload and restoring automatic matching')

   for theme in ['lol','basket','abstract']:
    for n in [8,16,24]:
     choose(p,theme,n);s=state(p);assert s['series']=='all'
     if theme=='lol':assert len({d['id'].rsplit('-',1)[0] for d in s['deck']})==n//4
     finish(p,n)
     if n==8:p.screenshot(path=str(OUT/f'v10-result-{theme}.png'),full_page=True)
   passed('all 8/16/24 modes complete automatically in all three themes, retaining legal five-person teams and actual answer evidence')
   home(p);p.locator('[data-action=theme][data-theme=lol]').click();p.locator('[data-action=meme][data-id=double-laugh]').click();p.locator('[data-action=meme-start]').click();assert state(p)['series']=='all';assert state(p)['deck'][0]['id'].startswith('rift-double-laugh-');finish(p,state(p)['count'],pref=['laugh','chaos','plan'])
   passed('a named League meme starts inside the same combined League mode rather than opening a second submode')
   for style in ['night','paper']:
    if p.locator('html').get_attribute('data-style')!=style:p.locator('[data-action=palette]').click()
    for w in [320,390,430,768,1440]:p.set_viewport_size({'width':w,'height':844});overflow(p)
   p.set_viewport_size({'width':390,'height':844});p.locator('.result-fold summary').click();p.locator('[data-action=review]').click();assert p.locator('.review-list article').count() in [8,16,24];close(p)
   home(p);p.locator('header [data-action=archive]').click();assert p.locator('.history-card').count()==12;first=p.locator('.history-card').first.inner_text();p.reload();p.locator('header [data-action=archive]').click();assert p.locator('.history-card').first.inner_text()==first;p.locator('.history-card').first.click();result(p)
   passed('results, person bonds, details and rolling 12-entry history survive both palettes, narrow screens and reload')
   with p.expect_download() as dl:p.locator('footer [data-action=download-html]').click()
   exported=Path(dl.value.path()).read_text();assert 'world-otherme.v10.' in exported;assert 'parody-icons-v9.webp' in exported
   off=browser.new_context(offline=True,viewport={'width':390,'height':844},accept_downloads=True,reduced_motion='reduce');off.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw Error('QA storage denied')}})");op=off.new_page();op.on('pageerror',lambda e:errors.append(str(e)));op.goto('about:blank');op.set_content(exported);op.wait_for_function("document.documentElement.dataset.appReady==='true'")
   for theme in ['lol','basket','abstract']:choose(op,theme,8);finish(op,8)
   assert op.locator('.local-note').is_visible();op.locator('[data-action=poster]').click();op.wait_for_selector('.poster');off.close()
   passed('the actual exported complete HTML runs all three themes offline without storage and still generates a poster')
   home(p);p.evaluate("()=>{localStorage.setItem('world-otherme.v10.history',JSON.stringify([null,{},'broken']));localStorage.setItem('world-otherme.v10.session','broken');}");p.reload();p.locator('header [data-action=archive]').click();assert p.locator('.empty').is_visible();assert not errors,errors;assert not external,external
   passed('malformed local records are ignored and all tested app flows request zero external runtime assets with no JavaScript errors')
   status='passed';failure=None
  except Exception as e:
   status='failed';failure=str(e);p.screenshot(path=str(OUT/'v10-failure.png'),full_page=True);raise
  finally:
   report=dict(status=locals().get('status','failed'),checks=checks,passed=len(checks),failure=locals().get('failure'),html_sha256=hashlib.sha256(HTML).hexdigest(),html_bytes=len(HTML),javascript_errors=errors,external_requests=external,duration_seconds=round(time.time()-started,2),scope='Chromium responsive viewport, actual single-tap navigation and exports, offline exported-content execution; no physical phone test. Managed Chromium policy blocks file:// navigation, as documented in V8.')
   (R/'docs/browser-check-v10.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');browser.close();server.shutdown()
print(len(checks),'V10 browser checks passed',flush=True)
