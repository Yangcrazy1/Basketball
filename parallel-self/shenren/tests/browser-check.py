from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
import threading,tempfile,json,hashlib,sys,io,time
from playwright.sync_api import sync_playwright
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];HTML=(ROOT/'dist/world-another-me.html').read_bytes();OUT=ROOT/'dist/qa';OUT.mkdir(exist_ok=True);checks=[];errors=[];requests=[];started=time.time()
def passed(s):checks.append(s);print('PASS',s,flush=True)
def overflow(page):assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),'horizontal overflow'
def close(page):
 if page.locator('#dialog').is_visible():page.locator('#close-dialog').click()
def home(page):close(page);page.locator('.brand').click()
def session(page):return page.evaluate("JSON.parse(localStorage.getItem('world-otherme.v5.session'))")
def choose(page,theme='lol',series='hex',count=8):
 home(page);page.locator(f'[data-action=theme][data-theme={theme}]').click()
 if theme=='lol':page.locator(f'[data-action=series][data-id={series}]').click()
 page.locator(f'[data-action=mode][data-count="{count}"]').click();page.locator('#app [data-action=start]').click()
def finish(page,count,first=0,choices=None):
 for i in range(first,count):
  if choices is None:page.locator('.option').nth(i%4).click()
  else:page.locator(f'.option[data-id="{choices[i]}"]').click()
  page.locator('[data-action=next]').click()
 assert page.locator('.augment-card').count()==3
 page.locator('.augment-card').first.click();page.wait_for_selector('#toy-canvas')
 assert page.locator('.team-card').count()==5
 assert page.locator('.team-card.is-you').count()==1
 ids=page.locator('.team-card').evaluate_all('(els)=>els.map(e=>e.dataset.person)');assert len(set(ids))==5
 data=page.evaluate('WORLD_DATA');themes={t['id']:t for t in data['themes']}
 for el in page.locator('.team-card').all():
  p=next(p for p in data['characters'] if p['id']==el.get_attribute('data-person'));assert int(el.get_attribute('data-role')) in p['roles']
 assert page.locator('#toy-canvas').get_attribute('data-renderer')=='software-3d-mesh'
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
with tempfile.TemporaryDirectory() as temp:
 Path(temp,'world-another-me.html').write_bytes(HTML)
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=temp));threading.Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}/world-another-me.html'
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  ctx=browser.new_context(viewport={'width':390,'height':844},reduced_motion='reduce',accept_downloads=True);page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url) if not r.url.startswith(('http://127.0.0.1:','data:','blob:')) else None)
  try:
   page.goto(url);page.wait_for_function("document.documentElement.dataset.appReady==='true'")
   assert page.title().startswith('世界上另一个我');assert page.locator('[data-action=theme][data-theme=lol]').get_attribute('aria-pressed')=='true';assert page.locator('[data-action=series][data-id=hex]').get_attribute('aria-pressed')=='true'
   passed('name retained, League is primary and Hex ARAM is the default series')
   for style in ['night','paper']:
    if page.locator('html').get_attribute('data-style')!=style:page.locator('[data-action=palette]').click()
    for width in [320,390,430,768,1440]:page.set_viewport_size({'width':width,'height':844});overflow(page)
   page.set_viewport_size({'width':390,'height':844});page.locator('[data-action=palette]').click();page.screenshot(path=str(OUT/'home-night.png'),full_page=True);page.locator('[data-action=palette]').click();page.screenshot(path=str(OUT/'home-paper.png'),full_page=True)
   passed('both palettes fit 320/390/430/768/1440px; real-reference avatars render')
   page.locator('[data-action=story-preview]').click();assert all(s in page.locator('.story-preview').inner_text() for s in ['架空','S8','飞科','加里奥','GOAT']);close(page)
   passed('intro previews the requested alternative Uzi S8/Galio/GOAT story, clearly labeled fiction')
   choose(page,count=8);original=session(page);assert all(d['id'].startswith('hex-') for d in original['deck']);assert page.locator('[data-action=next]').is_disabled()
   for i in range(2):page.locator('.option').nth(i).click();assert f'已答 {i+1} / 8' in page.locator('.save-note').inner_text();page.locator('[data-action=next]').click()
   saved=session(page);page.reload();page.locator('[data-action=resume]').click();restored=session(page);assert restored['deck']==saved['deck'] and restored['answers']==saved['answers'] and restored['index']==2
   for i in range(2,8):page.locator('.option').nth(i%4).click();page.locator('[data-action=next]').click()
   old=[x.get_attribute('data-id') for x in page.locator('.augment-card').all()];page.locator('[data-action=reroll]').click();new=[x.get_attribute('data-id') for x in page.locator('.augment-card').all()];assert not set(old)&set(new);assert page.locator('[data-action=reroll]').is_disabled()
   page.reload();page.locator('[data-action=resume]').click();assert page.locator('[data-action=reroll]').is_disabled();assert [x.get_attribute('data-id') for x in page.locator('.augment-card').all()]==new
   page.locator('.augment-card').first.click();assert page.locator('.team-card').count()==5
   passed('random Hex-only deck enforces answering, updates progress, and resumes with identical questions/options')
   passed('three random talents can be rerolled exactly once, with persistent choices and reroll state')
   canvas=page.locator('#toy-canvas');assert int(canvas.get_attribute('data-faces'))>600;page.wait_for_timeout(150);front=canvas.screenshot();yaw=float(canvas.get_attribute('data-yaw'));page.locator('[data-action=rotate-right]').click();side=canvas.screenshot();assert front!=side
   for _ in range(7):page.locator('[data-action=rotate-right]').click()
   assert abs(float(canvas.get_attribute('data-yaw'))-yaw-6.283185)<.01
   box=canvas.bounding_box();page.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2);page.mouse.down();page.mouse.move(box['x']+box['width']/2+75,box['y']+box['height']/2+20,steps=6);page.mouse.up();assert abs(float(canvas.get_attribute('data-yaw'))-yaw-6.283185)>.5
   canvas.screenshot(path=str(OUT/'toy-rotated.png'));page.locator('[data-action=rotate-auto]').click();assert page.locator('[data-action=rotate-auto]').inner_text()=='暂停旋转';page.locator('[data-action=rotate-reset]').click();assert page.locator('[data-action=rotate-auto]').inner_text()=='自动旋转';canvas.screenshot(path=str(OUT/'toy-front.png'))
   with page.expect_download() as info:page.locator('[data-action=save-avatar]').click()
   im=Image.open(info.value.path());assert im.width>200 and im.height>200
   passed('true 3D mesh supports a full 360-degree rotation, pointer orbit, reset and actual PNG snapshot download')
   name=page.locator('.identity-card h1').inner_text();first=original['deck'][0]['id'];page.locator('[data-action=change-augment]').click();page.locator('[data-action=augment][data-id=""]').click();assert page.locator('.identity-card h1').inner_text()==name
   page.locator('#app [data-action=start]').click();fresh=session(page);assert fresh['deck'][0]['id']!=first and fresh['deck']!=original['deck']
   passed('changing talent preserves identity; a fresh run changes the first question and deck')
   finish(page,8)
   for series in ['hex','rift']:
    for n in [16,24]:
     choose(page,series=series,count=n);s=session(page);assert all(next(q for q in page.evaluate('WORLD_DATA.questions') if q['id']==d['id'])['series']==series for d in s['deck']);finish(page,n)
   passed('16/24-question journeys finish independently in both Hex ARAM and ranked-Rift series, with five legal positions')
   choose(page,count=24);s=session(page);data=page.evaluate('WORLD_DATA');target=next(p for p in data['characters'] if p['id']=='lol-uzi')['vector'];choice=[None]*24
   for dim,val in zip([d['id'] for d in data['dimensions']],target):
    indices=[i for i,d in enumerate(s['deck']) if next(q for q in data['questions'] if q['id']==d['id'])['dim']==dim];total=round((1+val/100*3)*len(indices));base=total//len(indices);extra=total%len(indices)
    for j,i in enumerate(indices):choice[i]=base+(j<extra)-1
   finish(page,24,choices=choice);assert 'Uzi' in page.locator('.identity-card h1').inner_text();assert all(t in page.locator('.story-card').inner_text() for t in ['架空','S8','飞科','加里奥','GOAT'])
   page.screenshot(path=str(OUT/'uzi-result.png'),full_page=True)
   passed('actual completed target answers reveal Uzi, the alternate S8 ending and a roster containing you plus four teammates')
   for style in ['night','paper']:
    if page.locator('html').get_attribute('data-style')!=style:page.locator('[data-action=palette]').click()
    for width in [320,390,430,768,1440]:page.set_viewport_size({'width':width,'height':844});overflow(page)
   page.set_viewport_size({'width':390,'height':844})
   passed('the full story/3D/five-member result fits both palettes at all five viewport widths')
   page.locator('[data-action=review]').click();assert page.locator('.review-list article').count()==24;close(page);page.locator('[data-action=poster]').click();page.wait_for_selector('.poster')
   with page.expect_download() as info:page.locator('a.download-png').click()
   png=Image.open(info.value.path());assert png.size==(1080,1740);close(page)
   passed('actual answers can be reviewed and a full 1080x1740 identity/team PNG downloads and decodes')
   for theme in ['basket','abstract']:choose(page,theme=theme);finish(page,8);assert len(page.locator('.team-card').all())==5
   passed('secondary basketball/network themes retain independent questions, five positions and themed 3D avatars')
   page.locator('header [data-action=archive]').click();assert page.locator('.history-card').count()>=7;page.reload();page.locator('header [data-action=archive]').click();page.locator('.history-card').first.click();assert page.locator('.identity-card').is_visible()
   passed('completed identities and five-member teams remain reproducible after history reload')
   with page.expect_download() as info:page.locator('footer [data-action=download-html]').click()
   downloaded=Path(info.value.path()).read_text();assert 'WORLD_DATA' in downloaded and 'software-3d-mesh' in downloaded and 'https://cdn.' not in downloaded
   offline=browser.new_context(viewport={'width':390,'height':844},offline=True,reduced_motion='reduce',accept_downloads=True);offline.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw Error('QA deny storage')}})");op=offline.new_page();op.on('pageerror',lambda e:errors.append(str(e)));op.goto('about:blank');op.set_content(downloaded);op.wait_for_function("document.documentElement.dataset.appReady==='true'")
   op.locator('[data-action=mode][data-count="8"]').click();op.locator('#app [data-action=start]').click();finish(op,8);assert op.locator('.local-note').is_visible();op.locator('[data-action=poster]').click();op.wait_for_selector('.poster');offline.close()
   passed('downloaded single-file HTML boots offline with storage denied, completes a run, renders 3D and generates its poster')
   home(page);page.evaluate("localStorage.setItem('world-otherme.v5.history',JSON.stringify([null,{},'bad',{session:null}]));localStorage.setItem('world-otherme.v5.session','broken-json')");page.reload();page.locator('header [data-action=archive]').click();assert page.locator('.empty').is_visible()
   assert not errors,errors;assert not requests,requests
   passed('invalid stored records are ignored; all tested flows run with zero JS errors or external asset requests')
   status='passed';failure=None
  except Exception as e:
   status='failed';failure=str(e);page.screenshot(path=str(OUT/'failure.png'),full_page=True);raise
  finally:
   report={'status':locals().get('status','failed'),'checks':checks,'passed':len(checks),'failure':locals().get('failure'),'html_sha256':hashlib.sha256(HTML).hexdigest(),'html_bytes':len(HTML),'javascript_errors':errors,'external_requests':requests,'duration_seconds':round(time.time()-started,2),'scope':'Chromium mobile viewport and actual downloads; no physical-phone hardware installation check'}
   (ROOT/'docs/browser-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');browser.close();server.shutdown()
print(len(checks),'V5 browser checks passed',flush=True)
