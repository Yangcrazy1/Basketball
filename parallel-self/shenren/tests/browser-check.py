from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
import threading,tempfile,json,hashlib,time
from playwright.sync_api import sync_playwright
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];HTML=(ROOT/'dist/world-another-me.html').read_bytes();OUT=ROOT/'dist/qa';OUT.mkdir(exist_ok=True);checks=[];errors=[];requests=[];started=time.time();PREFIX='world-otherme.v7.'
def passed(s):checks.append(s);print('PASS',s,flush=True)
def overflow(p):assert p.evaluate('document.documentElement.scrollWidth<=innerWidth'),f'overflow at {p.viewport_size}'
def close(p):
 if p.locator('#dialog').is_visible():p.locator('#close-dialog').click()
def home(p):close(p);p.locator('.brand').click()
def stored(p):return p.evaluate("JSON.parse(localStorage.getItem('world-otherme.v7.session'))")
def choose(p,theme='lol',series='hex',count=8):
 home(p);p.locator(f'[data-action=theme][data-theme={theme}]').click()
 if theme=='lol':p.locator(f'[data-action=series][data-id={series}]').click()
 p.locator(f'[data-action=mode][data-count="{count}"]').click();p.locator('#app [data-action=start]').click()
def verify_result(p):
 p.wait_for_selector('.identity-card');assert p.locator('.team-card').count()==5;assert p.locator('.team-card.is-you').count()==1;assert p.locator('.hex-card.fan-made').count()==1;assert p.locator('canvas').count()==0
 assert '本作自制' in p.locator('.hex-card').inner_text();assert p.locator('.hex-icon svg use').get_attribute('href')=='#perk-sheet'
 data=p.evaluate('WORLD_DATA');ids=[]
 for el in p.locator('.team-card').all():
  char=next(c for c in data['characters'] if c['id']==el.get_attribute('data-person'));assert int(el.get_attribute('data-role')) in char['roles'];ids.append(char['personId']);assert el.locator('p').inner_text()
 assert len(set(ids))==5
 assert p.locator('.result-dock').is_visible()
def finish(p,n,start=0,pref=None):
 for i in range(start,n):
  if pref:
   oid=p.evaluate('''pref=>{const s=JSON.parse(localStorage.getItem('world-otherme.v7.session')),q=WORLD_DATA.questions.find(q=>q.id===s.deck[s.index].id);return pref.map(b=>q.options.find(o=>o.behavior===b)).find(Boolean)?.id??0;}''',pref);p.locator(f'.option[data-id="{oid}"]').click()
  else:p.locator('.option').nth(i%4).click()
  p.locator('[data-action=next]').click()
 verify_result(p)
def fixture(p,chapters):
 home(p);p.evaluate('''chapters=>{let s=ShenrenEngine.draw(WORLD_DATA,'lol',8,null,undefined,'hex');s.deck=chapters.flatMap(c=>WORLD_DATA.questions.filter(q=>q.theme==='lol'&&q.series==='hex'&&q.chapter===c).sort((a,b)=>a.stage-b.stage)).map(q=>({id:q.id,order:ShenrenEngine.shuffle([0,1,2,3])}));s.answers=Array(8).fill(null);s.index=0;localStorage.setItem('world-otherme.v7.session',JSON.stringify(s));}''',chapters);p.reload();p.locator('[data-action=resume]').click()
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
with tempfile.TemporaryDirectory() as temp:
 Path(temp,'index.html').write_bytes(HTML);server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=temp));threading.Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}/index.html'
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);ctx=browser.new_context(viewport={'width':390,'height':844},accept_downloads=True,reduced_motion='reduce');p=ctx.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.on('request',lambda r:requests.append(r.url) if not r.url.startswith(('http://127.0.0.1:','data:','blob:')) else None)
  try:
   p.goto(url);p.wait_for_function("document.documentElement.dataset.appReady==='true'");assert p.evaluate('WORLD_DATA.version')==7;assert 'VOL.07' in p.locator('.edition').inner_text();assert p.locator('[data-action=series][data-id=hex]').get_attribute('aria-pressed')=='true';assert p.locator('#app [data-action=start]').bounding_box()['y']+p.locator('#app [data-action=start]').bounding_box()['height']<844
   passed('V7 boots with Hex default and the main start button visible within a 390x844 first screen')
   for style in ['night','paper']:
    if p.locator('html').get_attribute('data-style')!=style:p.locator('[data-action=palette]').click()
    for w in [320,390,430,768,1440]:p.set_viewport_size({'width':w,'height':844});overflow(p)
    p.set_viewport_size({'width':390,'height':844});p.screenshot(path=str(OUT/('v7-home-'+style+'.png')),full_page=True)
   passed('both redesigned palettes fit 320/390/430/768/1440px with no horizontal overflow')
   dims=p.evaluate('''async()=>{const im=new Image();im.src=WORLD_PERK_SHEET.url;await im.decode();return [im.width,im.height];}''');assert dims==[1254,1254]
   variants={};expected={'afk':'fountain-owner','int':'feeding-license','collector':'collector-union','protect':'four-stay-alive'}
   for b,card in expected.items():
    p.locator(f'[data-action=sample][data-behavior={b}]').click();assert p.locator('#dialog .hex-card').get_attribute('data-augment')==card;assert '单题示例' in p.locator('#dialog-body').inner_text();variants[b]=p.locator('#dialog .hex-icon').screenshot();close(p)
   assert len(set(variants.values()))==4;assert p.evaluate("localStorage.getItem('world-otherme.v7.history')") is None
   p.locator('[data-action=card-gallery]').click();assert p.locator('.card-gallery button').count()==25;p.locator('#dialog [data-action=peek][data-id=table-flip]').click();assert p.locator('#dialog .hex-card h2').inner_text()=='掀桌';assert '桌子' in p.locator('#dialog .hex-effect').inner_text();close(p)
   passed('four Collector sample reactions reveal four distinct illustrated parody cards; all 25 cards can be browsed')
   p.locator('[data-action=story-preview]').click();assert all(w in p.locator('.story-preview').inner_text() for w in ['S8','架空','飞科','加里奥','GOAT']);close(p)
   fixture(p,['collector','office']);assert p.locator('[data-action=next]').is_disabled();p.locator('.option[data-id="0"]').click();p.locator('[data-action=next]').click();assert '观战席' in p.locator('.question h1').inner_text();assert '挂机' in p.locator('.previous-choice').inner_text();p.locator('[data-action=previous]').click();p.locator('.option[data-id="1"]').click();p.locator('[data-action=next]').click();assert '复活倒计时' in p.locator('.question h1').inner_text();p.locator('[data-action=previous]').click();p.locator('.option[data-id="0"]').click();p.locator('[data-action=next]').click();saved=stored(p);p.screenshot(path=str(OUT/'v7-question-branch.png'),full_page=True);p.reload();p.locator('[data-action=resume]').click();resumed=stored(p);assert resumed['deck']==saved['deck'] and resumed['answers']==saved['answers'] and resumed['index']==1
   passed('Collector follow-up question actually branches for AFK versus inting, follows edits, and resumes the same shuffled run')
   finish(p,8,start=1,pref=['afk','retreat','blame']);assert p.locator('.hex-card').get_attribute('data-augment')=='fountain-owner';assert p.locator('.identity-card h1').inner_text()=='PDD';assert p.locator('.chain-row').count()>0;assert any(term in p.locator('.team-grid').inner_text() for term in ['安全员','先看地图','安全感'])
   p.screenshot(path=str(OUT/'v7-result-fountain.png'),full_page=True)
   old=p.locator('.identity-card h1').inner_text();p.locator('[data-action=alternatives]').click();assert p.locator('#dialog .hex-card').count()==2;close(p);assert p.locator('.identity-card h1').inner_text()==old;p.locator('[data-action=card-note]').click();assert '恶搞' in p.locator('#dialog-body').inner_text();assert '官方游戏数值' in p.locator('#dialog-body').inner_text();close(p)
   passed('full AFK-oriented answers reveal PDD plus Fountain Owner with actual evidence, parody notes and stable alternatives')
   fixture(p,['collector','collector-audit']);finish(p,8,pref=['collector','gold','plan']);assert p.locator('.hex-card').get_attribute('data-augment')=='collector-union';assert '污渍' in p.locator('.identity-card h1').inner_text();p.locator('.story-ending summary').click();assert all(w in p.locator('.story-card').inner_text() for w in ['S8','架空','飞科','加里奥','GOAT']);assert '股东' in p.locator('.team-grid').inner_text() or '最后一口' in p.locator('.team-grid').inner_text();p.screenshot(path=str(OUT/'v7-result-collector.png'),full_page=True)
   passed('economy-focused full answers reveal Uzi/Fifth Collector, the alternate S8 ending and card-specific teammate duties')
   for style in ['night','paper']:
    if p.locator('html').get_attribute('data-style')!=style:p.locator('[data-action=palette]').click()
    for w in [320,390,430,768,1440]:p.set_viewport_size({'width':w,'height':844});overflow(p);box=p.locator('.result-dock').bounding_box();assert box['x']>=0 and box['x']+box['width']<=w+1
   p.set_viewport_size({'width':390,'height':844});p.locator('.result-fold summary').click();p.locator('[data-action=review]').click();assert p.locator('.review-list article').count()==8;close(p)
   passed('result, floating share controls and expandable six-axis/answer detail fit both palettes at every tested viewport')
   p.locator('[data-action=poster]').click();p.wait_for_selector('.poster')
   with p.expect_download() as d:p.locator('.download-png').click()
   im=Image.open(d.value.path());assert im.size==(1080,1920);im.save(OUT/'v7-exported-poster.png');close(p)
   passed('new Uzi plus original parody-card/five-member PNG actually downloads and decodes at 1080x1920')
   before=stored(p)
   for ser in ['hex','rift']:
    for n in [8,16,24]:
     choose(p,series=ser,count=n);s=stored(p);assert all(next(q for q in p.evaluate('WORLD_DATA.questions') if q['id']==d['id'])['series']==ser for d in s['deck']);finish(p,n)
   for t in ['basket','abstract']:choose(p,theme=t);finish(p,8)
   passed('all 8/16/24 modes finish in Hex and Rift with five legal roles; secondary themes retain parody results')
   home(p);p.locator('header [data-action=archive]').click();assert p.locator('.history-card').count()>=9;first=p.locator('.history-card').first.inner_text();p.reload();p.locator('header [data-action=archive]').click();assert p.locator('.history-card').first.inner_text()==first;p.locator('.history-card').first.click();verify_result(p)
   passed('V7 identity/card/team history reproduces after reload while older-version storage remains separate')
   with p.expect_download() as d:p.locator('footer [data-action=download-html]').click()
   downloaded=Path(d.value.path()).read_text();assert 'WORLD_PERK_SHEET' in downloaded and 'WORLD_AUGMENTS' not in downloaded and 'Toy3D' not in downloaded
   offline=browser.new_context(viewport={'width':390,'height':844},offline=True,accept_downloads=True,reduced_motion='reduce');offline.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw Error('QA denied storage')}})");op=offline.new_page();op.on('pageerror',lambda e:errors.append(str(e)));op.goto('about:blank');op.set_content(downloaded);op.wait_for_function("document.documentElement.dataset.appReady==='true'");op.locator('[data-action=mode][data-count="8"]').click();op.locator('#app [data-action=start]').click();finish(op,8);assert op.locator('.local-note').is_visible();op.locator('[data-action=poster]').click();op.wait_for_selector('.poster');offline.close()
   passed('downloaded single HTML works offline with denied storage, original card art, a complete run and its poster')
   home(p);p.evaluate("localStorage.setItem('world-otherme.v7.history',JSON.stringify([null,{},'bad',{session:null}]));localStorage.setItem('world-otherme.v7.session','broken-json')");p.reload();p.locator('header [data-action=archive]').click();assert p.locator('.empty').is_visible();assert not errors,errors;assert not requests,requests
   passed('malformed records are ignored and all tested flows make zero external asset requests with no JavaScript errors')
   status='passed';failure=None
  except Exception as e:
   status='failed';failure=str(e);p.screenshot(path=str(OUT/'v7-failure.png'),full_page=True);raise
  finally:
   report={'status':locals().get('status','failed'),'checks':checks,'passed':len(checks),'failure':locals().get('failure'),'html_sha256':hashlib.sha256(HTML).hexdigest(),'html_bytes':len(HTML),'javascript_errors':errors,'external_requests':requests,'duration_seconds':round(time.time()-started,2),'scope':'Chromium responsive viewport, exact semantic answer cases, actual PNG/HTML downloads and offline execution; no physical phone test'};(ROOT/'docs/browser-check-v7.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');browser.close();server.shutdown()
print(len(checks),'V7 browser checks passed',flush=True)
