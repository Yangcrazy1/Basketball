"""Verify the published site, not a local preview or a raw-host proxy."""
from pathlib import Path
from urllib.request import urlopen
import json,hashlib,datetime
from playwright.sync_api import sync_playwright
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];BASE='https://yangcrazy1.github.io/Basketball/';HTML=(ROOT/'release/world-another-me.html').read_bytes();SHA=hashlib.sha256(HTML).hexdigest();checks=[];errors=[]
def passed(s):checks.append(s);print('PASS',s,flush=True)
info=json.loads(urlopen(BASE+'build-info.json?v='+SHA[:12],timeout=30).read());assert info['version']==8 and info['html_sha256']==SHA
for path in ['', 'world-another-me.html']:
 with urlopen(BASE+path+'?v=8-memes-'+SHA[:12],timeout=30) as r:
  body=r.read();assert r.status==200 and hashlib.sha256(body).hexdigest()==SHA
passed('public root and single-file URL both return HTTP 200 with exactly the tested HTML bytes')
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);ctx=browser.new_context(viewport={'width':390,'height':844},accept_downloads=True,reduced_motion='reduce');page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
 r=page.goto(BASE+'?v=8-memes',wait_until='networkidle',timeout=60000);assert r.status==200;page.wait_for_function("document.documentElement.dataset.appReady==='true'");assert page.evaluate('WORLD_DATA.version')==8;assert 'VOL.08' in page.locator('.edition').inner_text();assert page.evaluate('WORLD_DATA.characters.length')==44;assert not page.evaluate("WORLD_DATA.characters.some(p=>p.personId==='lecturer')");assert page.locator('canvas').count()==0
 passed('actual public Chromium mobile viewport boots V8 with the removed character/model absent')
 page.locator('[data-action=sample][data-behavior=afk]').click();assert page.locator('#dialog .hex-card').get_attribute('data-augment')=='fountain-owner';page.locator('#close-dialog').click();page.locator('[data-action=sample][data-behavior=int]').click();assert page.locator('#dialog .hex-card').get_attribute('data-augment')=='feeding-license';page.locator('#close-dialog').click()
 page.locator('[data-action=sample][data-behavior=collector]').click();assert page.locator('#dialog .hex-icon [data-game-icon=item-6676]').count()==5;page.locator('#close-dialog').click()
 passed('public Collector sample distinguishes AFK and inting with separate parody cards')
 page.locator('[data-action=mode][data-count="8"]').click();page.locator('#app [data-action=start]').click()
 for i in range(8):page.locator('.option').nth(i%4).click();page.locator('[data-action=next]').click()
 assert page.locator('.identity-card').is_visible();assert page.locator('.team-card').count()==5;assert page.locator('.team-card.is-you').count()==1;assert page.locator('#app .hex-card .perk-art .game-item').count()>0;assert '本作自制' in page.locator('#app .hex-card').inner_text();assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 passed('public eight-question flow reveals a cartoon person, real-icon parody card and five-person team')
 page.locator('[data-action=poster]').click();page.wait_for_selector('.poster')
 with page.expect_download() as d:page.locator('.download-png').click()
 assert Image.open(d.value.path()).size==(1080,1920);page.locator('#close-dialog').click()
 with page.expect_download() as d:page.locator('footer [data-action=download-html]').click()
 exported=Path(d.value.path()).read_text();assert len(exported)>3000000 and 'WORLD_PERK_SHEET' in exported and 'WORLD_AUGMENTS' not in exported and 'Toy3D' not in exported
 passed('public app actually downloads the new PNG and a complete offline HTML file')
 page.goto(BASE+'download/?v=8-memes',wait_until='networkidle');assert page.locator('a.download').get_attribute('download').endswith('.html')
 with page.expect_download() as d:page.locator('a.download').click()
 assert hashlib.sha256(Path(d.value.path()).read_bytes()).hexdigest()==SHA
 passed('public download page downloads exactly the released single-file HTML')
 assert not errors,errors;browser.close()
report={'status':'passed','url':BASE+'?v=8-memes','download_page':BASE+'download/?v=8-memes','source_commit':info['source_commit'],'html_sha256':SHA,'html_bytes':len(HTML),'checks':checks,'javascript_errors':errors,'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Actual public HTTPS site, Chromium 390px responsive viewport and real downloads; no physical phone hardware test'}
(ROOT/'docs/web-verification-v8.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(len(checks),'public HTTPS checks passed',flush=True)
