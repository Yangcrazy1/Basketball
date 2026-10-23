"""Fast online entry: measure first requests and preserve the true offline download."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
from PIL import Image
import threading,json,hashlib,time
R=Path(__file__).resolve().parents[1];O=R/'dist/web';checks=[];errors=[];requests=[];sizes=[]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
def passed(s):checks.append(s);print('PASS',s,flush=True)
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(O)));threading.Thread(target=server.serve_forever,daemon=True).start();base='http://127.0.0.1:'+str(server.server_port)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);ctx=b.new_context(viewport={'width':390,'height':844},accept_downloads=True,reduced_motion='reduce');p=ctx.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.on('request',lambda r:requests.append(r.url));p.on('response',lambda r:sizes.append((r.url,int(r.headers.get('content-length',0)))))
 try:
  p.goto(base,wait_until='networkidle');p.wait_for_selector('.intro-page');initial_bytes=sum(n for _,n in sizes);assert initial_bytes<1600000,(initial_bytes,sizes);assert not any('portraits-' in u for u in requests);assert len((O/'index.html').read_bytes())<3000
  passed('2 KB online entry renders the comic with less than 1.6 MB of initial resources and no portrait-atlas requests')
  for i in range(3):p.locator('[data-action=intro-next]').click()
  for theme in ['lol','basket','abstract']:
   p.locator('.brand').click();p.locator('[data-action=theme][data-theme='+theme+']').click();p.locator('[data-action=mode][data-count="8"]').click();p.locator('#app [data-action=start]').click()
   for i in range(8):
    old=p.locator('.option').first.get_attribute('data-question');p.locator('.option').nth(i%4).click();p.wait_for_function("id=>!document.querySelector('.option[data-question=\"'+id+'\"]')",arg=old)
   p.wait_for_selector('.reveal-page');p.locator('[data-action=reveal-open]').click();assert p.locator('.team-card').count()==5;assert p.evaluate('document.documentElement.scrollWidth<=innerWidth')
  passed('all three themes load their local portraits on demand and complete quiz, reveal and five-person team flows')
  p.locator('[data-action=squad]').click();p.locator('[data-action=squad-free]').click();p.locator('[data-action=squad-save]').click();assert '自选阵容' in p.locator('.team-heading').inner_text()
  p.locator('[data-action=poster]').click();p.wait_for_selector('.poster')
  with p.expect_download() as dl:p.locator('.download-png').click()
  assert Image.open(dl.value.path()).size==(1080,1920);p.locator('#close-dialog').click()
  passed('resource-backed avatars remain exportable to an actual PNG after selecting a custom squad')
  with p.expect_download() as dl:p.locator('footer [data-action=download-html]').click()
  offline=Path(dl.value.path()).read_bytes();assert hashlib.sha256(offline).hexdigest()==hashlib.sha256((R/'release/world-another-me.html').read_bytes()).hexdigest();assert b'data:image/webp;base64,' in offline
  passed('Download offline HTML saves the complete 10.6 MB standalone app rather than the small online shell')
  bad=ctx.new_page();bad.route('**/data-*.js',lambda route:route.abort());bad.goto(base,wait_until='networkidle');bad.wait_for_selector('#loading a:not([hidden])');assert '还没加载完成' in bad.locator('#loading').inner_text();bad.close()
  passed('a blocked data script leaves a visible retry explanation instead of an inert blank page')
  assert not errors,errors;assert not [u for u in requests if not u.startswith(base)],requests
  passed('online build has no external resource dependencies and no application JavaScript errors')
  status='passed'
 finally:
  report={'status':locals().get('status','failed'),'checks':checks,'passed':len(checks),'entry_sha256':hashlib.sha256((O/'index.html').read_bytes()).hexdigest(),'initial_resource_bytes':locals().get('initial_bytes'),'javascript_errors':errors,'scope':'Chromium mobile viewport and local HTTP; user network reachability remains to be confirmed'};(R/'docs/online-entry-check-v10.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');b.close();server.shutdown()
