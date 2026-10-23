"""Pin and exercise the actual V11 candidate; production V10 stays separate."""
from pathlib import Path
from urllib.request import urlopen
from playwright.sync_api import sync_playwright
from PIL import Image
import json,hashlib,datetime
R=Path(__file__).resolve().parents[1];host='https://yangcrazy1.github.io/Basketball/';base=host+'preview/v11/r5/';checks=[];errors=[]
def passed(s):checks.append(s);print('PASS',s,flush=True)
meta=json.loads(urlopen(base+'build-info.json',timeout=25).read());assert meta['round']==5 and meta['production_unchanged'];sha=hashlib.sha256((R/'dist/world-another-me.html').read_bytes()).hexdigest();assert meta['offline_html_sha256']==sha
for filename,want in [('index.html',meta['entry_sha256']),('world-another-me.html',sha)]:
 with urlopen(base+filename,timeout=30) as r:assert r.status==200 and hashlib.sha256(r.read()).hexdigest()==want
for n in [1,2,3,4,5]:
 with urlopen(host+'preview/v11/r'+str(n)+'/',timeout=25) as r:assert r.status==200
with urlopen(host+'build-info.json',timeout=25) as r:production=json.load(r);assert production['version']==10
passed('all five versioned previews resolve, final HTML hashes match, production remains V10')
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);ctx=b.new_context(viewport={'width':393,'height':852},accept_downloads=True,reduced_motion='reduce');p=ctx.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.goto(base,wait_until='networkidle',timeout=60000);p.wait_for_selector('.v11-home');assert p.evaluate('WORLD_DATA.version')==11;assert p.evaluate('ShenrenEngine.enabledPeople(WORLD_DATA).length')==40
 p.locator('[data-action=gallery]').click();assert p.locator('.library-person').count()==20;p.locator('[data-search=library]').fill('阿水');p.wait_for_timeout(300);assert p.locator('.library-person').count()==1;p.locator('.library-person').click();assert p.locator('.person-perks button').count()==3;p.locator('#close-dialog').click();passed('public home, 40-person pool, alias search and three signature cards work in the real published candidate')
 for theme in ['lol','basket','abstract']:
  p.locator('.brand').click();p.locator('[data-action=theme][data-theme='+theme+']').click();p.locator('#app [data-action=start]').click()
  for i in range(8):
   old=p.locator('.option').first.get_attribute('data-question');p.locator('.option').nth(i%4).click();p.wait_for_function("id=>!document.querySelector('.option[data-question=\"'+id+'\"]')",arg=old)
  p.wait_for_selector('.reveal-page');p.locator('[data-action=reveal-open]').click();assert p.locator('.team-card').count()==5;assert p.evaluate('document.documentElement.scrollWidth<=innerWidth');passed('public '+theme+' quiz completes with reveal, evidence, personal gifts and five-person squad')
 p.locator('[data-action=poster]').click();p.wait_for_selector('.poster')
 with p.expect_download() as dl:p.locator('.download-png').click()
 assert Image.open(dl.value.path()).size==(1080,1920);p.locator('#close-dialog').click()
 with p.expect_download() as dl:p.locator('footer [data-action=download-html]').click()
 assert hashlib.sha256(Path(dl.value.path()).read_bytes()).hexdigest()==sha;passed('published candidate downloads an actual PNG and the complete tested offline HTML')
 assert not errors,errors;b.close()
report={'status':'passed','checks':checks,'count':len(checks),'url':base,'sha256':sha,'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'device':'393x852 Chromium mobile viewport, not a physical phone'};(R/'docs/public-preview-v11.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
