"""First paint and deliberately broken network dependencies, without repeating quiz regressions."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
import threading,json,hashlib
R=Path(__file__).resolve().parents[1];O=R/'dist/web';sizes=[];requests=[];checks=[]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(O)));threading.Thread(target=s.serve_forever,daemon=True).start();base='http://127.0.0.1:'+str(s.server_port)
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);p=b.new_page(viewport={'width':393,'height':852});p.on('response',lambda r:sizes.append(int(r.headers.get('content-length',0))));p.on('request',lambda r:requests.append(r.url));p.goto(base,wait_until='networkidle');p.wait_for_selector('.v11-home');assert len((O/'index.html').read_bytes())<3000;assert not any('portraits-' in u or 'v11-card-art/' in u for u in requests);total=sum(sizes);assert total<2000000,total;checks.append('first paint needs no portrait/card atlases and less than 2MB uncompressed core resources')
 bad=b.new_page();bad.route('**/data-*.js',lambda r:r.abort());bad.goto(base,wait_until='networkidle');bad.wait_for_selector('#loading a:not([hidden])');assert '还没加载完成' in bad.locator('#loading').inner_text();checks.append('blocked data dependency displays a retry entry instead of an inert blank screen');b.close()
s.shutdown();report=dict(status='passed',entry_bytes=(O/'index.html').stat().st_size,initial_resource_bytes=total,checks=checks,entry_sha256=hashlib.sha256((O/'index.html').read_bytes()).hexdigest());(R/'docs/online-entry-check-v11.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
