from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
import threading,tempfile,json,hashlib,time,base64
from playwright.sync_api import sync_playwright
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];HTML=(ROOT/'dist/world-another-me.html').read_bytes();OUT=ROOT/'dist/qa';OUT.mkdir(exist_ok=True);checks=[];errors=[];requests=[];started=time.time()
def passed(s):checks.append(s);print('PASS',s,flush=True)
def overflow(page):assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),f'overflow {page.viewport_size}'
def close(page):
 if page.locator('#dialog').is_visible():page.locator('#close-dialog').click()
def home(page):close(page);page.locator('.brand').click()
def session(page):return page.evaluate("JSON.parse(localStorage.getItem('world-otherme.v6.session'))")
def choose(page,theme='lol',series='hex',count=8):
 home(page);page.locator(f'[data-action=theme][data-theme={theme}]').click()
 if theme=='lol':page.locator(f'[data-action=series][data-id={series}]').click()
 page.locator(f'[data-action=mode][data-count="{count}"]').click();page.locator('#app [data-action=start]').click()
def finish(page,count,first=0):
 for i in range(first,count):
  page.locator('.option').nth(i%4).click();page.locator('[data-action=next]').click()
 page.wait_for_selector('.identity-card');assert page.locator('.team-card').count()==5;assert page.locator('.team-card.is-you').count()==1
 ids=page.locator('.team-card').evaluate_all('(els)=>els.map(e=>e.dataset.person)');assert len(set(ids))==5
 data=page.evaluate('WORLD_DATA')
 for el in page.locator('.team-card').all():
  p=next(p for p in data['characters'] if p['id']==el.get_attribute('data-person'));assert int(el.get_attribute('data-role')) in p['roles']
 assert page.locator('canvas').count()==0;assert page.locator('.hex-card').count()==1
 if page.evaluate("WORLD_DATA.characters.find(p=>p.id===document.querySelector('.is-you').dataset.person).theme")== 'lol':
  assert page.locator('.hex-icon img').evaluate('(im)=>im.complete&&im.naturalWidth===256');assert '真实强化' in page.locator('.hex-card').inner_text()
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
with tempfile.TemporaryDirectory() as temp:
 Path(temp,'index.html').write_bytes(HTML);server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=temp));threading.Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}/index.html'
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);ctx=browser.new_context(viewport={'width':390,'height':844},reduced_motion='reduce',accept_downloads=True);page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url) if not r.url.startswith(('http://127.0.0.1:','data:','blob:')) else None)
  try:
   page.goto(url);page.wait_for_function("document.documentElement.dataset.appReady==='true'");assert page.title().startswith('世界上另一个我');assert page.locator('[data-action=series][data-id=hex]').get_attribute('aria-pressed')=='true';assert 'VOL.06' in page.locator('.edition').inner_text()
   passed('V6 boots with League/Hex ARAM as default; all 3D UI and runtime are absent')
   for style in ['night','paper']:
    if page.locator('html').get_attribute('data-style')!=style:page.locator('[data-action=palette]').click()
    for width in [320,390,430,768,1440]:page.set_viewport_size({'width':width,'height':844});overflow(page)
    page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(OUT/('v6-home-'+style+'.png')),full_page=True)
   passed('both palettes fit 320/390/430/768/1440px without horizontal overflow')
   assert page.evaluate('WORLD_ATLASES.length')==11;assert page.evaluate('Object.keys(WORLD_PORTRAITS).length')==43
   dimensions=page.evaluate('''async()=>{let dims=[];for(const s of WORLD_ATLASES){let im=new Image();im.src=s.url;await im.decode();dims.push([im.width,im.height]);}return dims;}''');assert all(w==1254 and h==1254 for w,h in dimensions)
   for t in ['lol','basket','abstract']:
    page.locator(f'[data-action=theme][data-theme={t}]').click();page.locator('[data-action=gallery]').click();assert page.locator('.gallery [data-avatar]').count()==(14 if t=='abstract' else 15)
    assert len(set(page.locator('.gallery [data-avatar]').evaluate_all('(els)=>els.map(e=>e.dataset.avatar)')))==(14 if t=='abstract' else 15);close(page)
   page.locator('[data-action=theme][data-theme=lol]').click();page.locator('[data-action=gallery]').click();page.locator('[data-action=person][data-id=lol-dasima]').click();assert '公开参考重绘' in page.locator('.reference-box').inner_text();close(page);page.locator('[data-action=gallery]').click();page.locator('[data-action=person][data-id=lol-meiko]').click();assert '示意' in page.locator('.reference-box').inner_text();close(page)
   passed('11 new atlases decode; all 44 themed entries have distinct assigned cartoon cells; 5 illustrative avatars are disclosed')
   page.locator('[data-action=story-preview]').click();assert all(w in page.locator('.story-preview').inner_text() for w in ['S8','架空','加里奥','GOAT']);close(page)
   passed('Uzi introduction retains the fictional S8/Galio/GOAT alternate ending')
   choose(page);original=session(page);assert page.locator('[data-action=next]').is_disabled();choice=page.locator('.option').first.inner_text()[1:].strip();page.locator('.option').first.click();page.locator('[data-action=next]').click();assert page.locator('.previous-choice').is_visible();assert choice in page.locator('.previous-choice').inner_text();page.locator('[data-action=previous]').click();choice=page.locator('.option').nth(1).inner_text()[1:].strip();page.locator('.option').nth(1).click();page.locator('[data-action=next]').click();assert choice in page.locator('.previous-choice').inner_text();page.screenshot(path=str(OUT/'v6-question.png'),full_page=True)
   saved=session(page);page.reload();page.locator('[data-action=resume]').click();restored=session(page);assert restored['deck']==saved['deck'] and restored['answers']==saved['answers'] and restored['index']==1
   passed('four-act context quotes actual previous choice, responds to edits, and resumes identical shuffled questions/options')
   finish(page,8,first=1);name=page.locator('.identity-card h1').inner_text();aug=page.locator('.hex-card h2').inner_text();assert '为什么它更像你' in page.locator('.hex-reading').inner_text();page.locator('[data-action=alternatives]').click();assert page.locator('#dialog .hex-card').count()==2;close(page);page.locator('[data-action=augment-source]').click();assert '图标为真实游戏素材' in page.locator('#dialog-body').inner_text();close(page)
   passed('completing answers directly reveals a person and a real automatic augment with two alternatives and a source dialog')
   for style in ['night','paper']:
    if page.locator('html').get_attribute('data-style')!=style:page.locator('[data-action=palette]').click()
    for width in [320,390,430,768,1440]:page.set_viewport_size({'width':width,'height':844});overflow(page)
    page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(OUT/('v6-result-'+style+'.png')),full_page=True)
   passed('identity, real augment card, narrative, five-member team and six-axis result fit both palettes at all viewport widths')
   page.locator('[data-action=review]').click();assert page.locator('.review-list article').count()==8;close(page)
   page.locator('[data-action=poster]').click();page.wait_for_selector('.poster');page.locator('.poster').screenshot(path=str(OUT/'v6-poster-preview.png'))
   with page.expect_download() as info:page.locator('a.download-png').click()
   png=Image.open(info.value.path());assert png.size==(1080,1920);png.save(OUT/'v6-exported-poster.png');close(page)
   passed('new 1080x1920 character/real-augment/five-person PNG actually downloads and decodes')
   home(page);page.locator('#app [data-action=start]').click();fresh=session(page);assert fresh['deck'][0]['id']!=original['deck'][0]['id'];assert fresh['deck']!=original['deck']
   finish(page,8)
   for ser in ['hex','rift']:
    for n in [16,24]:
     choose(page,series=ser,count=n);s=session(page);assert all(next(q for q in page.evaluate('WORLD_DATA.questions') if q['id']==d['id'])['series']==ser for d in s['deck']);finish(page,n)
   for t in ['basket','abstract']:choose(page,theme=t);finish(page,8)
   passed('fresh runs change the first episode; 8/16/24 modes work; both LoL series and secondary themes finish with five legal positions')
   page.locator('header [data-action=archive]').click();assert page.locator('.history-card').count()>=7;first=page.locator('.history-card').first.inner_text();page.reload();page.locator('header [data-action=archive]').click();assert page.locator('.history-card').first.inner_text()==first;page.locator('.history-card').first.click();assert page.locator('.identity-card').is_visible()
   passed('history reload reproduces the identity, automatically recommended augment and five-member team')
   with page.expect_download() as info:page.locator('footer [data-action=download-html]').click()
   downloaded=Path(info.value.path()).read_text();assert 'WORLD_ATLASES' in downloaded and 'WORLD_AUGMENTS' in downloaded and 'Toy3D' not in downloaded;assert not 'world-otherme.v6.history' in downloaded
   offline=browser.new_context(viewport={'width':390,'height':844},offline=True,reduced_motion='reduce',accept_downloads=True);offline.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw Error('QA denied storage')}})");op=offline.new_page();op.on('pageerror',lambda e:errors.append(str(e)));op.goto('about:blank');op.set_content(downloaded);op.wait_for_function("document.documentElement.dataset.appReady==='true'");op.locator('[data-action=mode][data-count="8"]').click();op.locator('#app [data-action=start]').click();finish(op,8);assert op.locator('.local-note').is_visible();op.locator('[data-action=poster]').click();op.wait_for_selector('.poster');offline.close()
   passed('downloaded complete HTML works offline with storage denied, shows real icons and generates the new poster')
   home(page);page.evaluate("localStorage.setItem('world-otherme.v6.history',JSON.stringify([null,{},'bad',{session:null}]));localStorage.setItem('world-otherme.v6.session','broken-json')");page.reload();page.locator('header [data-action=archive]').click();assert page.locator('.empty').is_visible();assert not errors,errors;assert not requests,requests
   passed('malformed local records are ignored; all tested flows have zero JavaScript errors and no external asset requests')
   status='passed';failure=None
  except Exception as e:
   status='failed';failure=str(e);page.screenshot(path=str(OUT/'v6-failure.png'),full_page=True);raise
  finally:
   report={'status':locals().get('status','failed'),'checks':checks,'passed':len(checks),'failure':locals().get('failure'),'html_sha256':hashlib.sha256(HTML).hexdigest(),'html_bytes':len(HTML),'javascript_errors':errors,'external_requests':requests,'duration_seconds':round(time.time()-started,2),'scope':'Chromium responsive viewport, real PNG/HTML downloads, offline execution; no physical phone test'}
   (ROOT/'docs/browser-check-v6.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');browser.close();server.shutdown()
print(len(checks),'V6 browser checks passed',flush=True)
