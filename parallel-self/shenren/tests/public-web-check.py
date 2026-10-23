"""Verify V10 on the actual published HTTPS host and download endpoints."""
from pathlib import Path
from urllib.request import urlopen
import json,hashlib,datetime
from playwright.sync_api import sync_playwright
from PIL import Image
R=Path(__file__).resolve().parents[1];BASE='https://yangcrazy1.github.io/Basketball/';HTML=(R/'release/world-another-me.html').read_bytes();SHA=hashlib.sha256(HTML).hexdigest();checks=[];errors=[]
def passed(s):checks.append(s);print('PASS',s,flush=True)
def answer(p,i):
 b=p.locator('.option').nth(i);qid=b.get_attribute('data-question');b.click();p.wait_for_function("id=>!document.querySelector('.option[data-question=\"'+id+'\"]')",arg=qid)
info=json.loads(urlopen(BASE+'build-info.json?v='+SHA[:12],timeout=30).read());assert info['version']==10 and info['html_sha256']==SHA
for name in ['', 'world-another-me.html']:
 with urlopen(BASE+name+'?v=10-story-'+SHA[:12],timeout=30) as r:assert r.status==200 and hashlib.sha256(r.read()).hexdigest()==SHA
passed('public root and single-file endpoint serve HTTP 200 and exactly the browser-tested release bytes')
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);ctx=browser.new_context(viewport={'width':390,'height':844},accept_downloads=True,reduced_motion='reduce');p=ctx.new_page();p.on('pageerror',lambda e:errors.append(str(e)))
 p.goto(BASE+'?v=10-story',wait_until='networkidle',timeout=60000);p.wait_for_function("document.documentElement.dataset.appReady==='true'");assert p.locator('.intro-page').is_visible();p.locator('[data-action=intro-skip]').click();assert p.evaluate('WORLD_DATA.version')==10;assert p.locator('.theme-picker button').count()==3;assert p.locator('[data-action=series]').count()==0;assert p.evaluate('WORLD_DATA.counts.questions')==348;assert p.evaluate('WORLD_DATA.characters.length')==95
 passed('actual public mobile viewport starts V10 with three boards and only one combined League entry')
 p.locator('[data-action=sample][data-behavior=collector]').click();assert '必须出收集者' in p.locator('#dialog .hex-card h2').inner_text();assert p.locator('#dialog .hex-icon [data-game-icon=item-6676]').count()==5;p.locator('#close-dialog').click()
 passed('public Collector sample restores the mandatory Collector response and five real item copies')
 for theme in ['lol','basket','abstract']:
  p.locator('.brand').click();p.locator(f'[data-action=theme][data-theme={theme}]').click();p.locator('[data-action=mode][data-count="8"]').click();p.locator('#app [data-action=start]').click();assert p.locator('[data-action=next]').count()==0
  for i in range(8):answer(p,i%4)
  p.wait_for_selector('.reveal-page');p.locator('[data-action=reveal-open]').click();p.wait_for_selector('.identity-card');assert p.locator('.team-card').count()==5;assert p.locator('.team-card.is-you').count()==1;assert p.locator('.chain-row').count()>0;assert p.evaluate('document.documentElement.scrollWidth<=innerWidth')
  passed('public '+theme+' eight-question flow auto-advances to its person, themed Hex and five-person team')
 p.locator('[data-action=poster]').click();p.wait_for_selector('.poster')
 with p.expect_download() as dl:p.locator('.download-png').click()
 assert Image.open(dl.value.path()).size==(1080,1920);p.locator('#close-dialog').click()
 with p.expect_download() as dl:p.locator('footer [data-action=download-html]').click()
 text=Path(dl.value.path()).read_text();assert len(text)>3000000 and 'world-otherme.v10.' in text and 'parody-icons-v9.webp' in text and 'Toy3D' not in text
 passed('public app actually downloads a 1080x1920 PNG and the complete V10 offline HTML')
 p.goto(BASE+'download/?v=10-story',wait_until='networkidle')
 with p.expect_download() as dl:p.locator('a.download').click()
 assert hashlib.sha256(Path(dl.value.path()).read_bytes()).hexdigest()==SHA
 passed('public download page actually saves exactly the released self-contained HTML file')
 assert not errors,errors;browser.close()
report=dict(status='passed',url=BASE+'?v=10-story',download_page=BASE+'download/?v=10-story',source_commit=info['source_commit'],html_sha256=SHA,html_bytes=len(HTML),checks=checks,javascript_errors=errors,checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Actual public HTTPS host, Chromium 390px responsive viewport and real downloads; no physical phone hardware test')
(R/'docs/web-verification-v10.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(len(checks),'public HTTPS app checks passed',flush=True)

for remote,local in [('packages/world-another-me-v10-xhs.zip','release/world-another-me-v10-xhs.zip'),('branding/logo.png','assets/branding/logo.png'),('branding/cover.png','assets/branding/cover.png')]:
 data=urlopen(BASE+remote+'?v='+SHA[:12],timeout=45).read();assert hashlib.sha256(data).hexdigest()==hashlib.sha256((R/local).read_bytes()).hexdigest()
passed('public Xiaohongshu ZIP, transparent Logo and cover downloads exactly match the validated artifacts')
report['checks']=checks;(R/'docs/web-verification-v10.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
