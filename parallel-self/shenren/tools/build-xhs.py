"""Resource-based ES2017 Xiaohongshu variant; never uploads to the platform."""
from pathlib import Path
import json,re,shutil,zipfile,hashlib,subprocess
R=Path(__file__).resolve().parents[1];O=R/'dist/xhs';shutil.rmtree(O,ignore_errors=True);O.mkdir(parents=True);(O/'assets').mkdir()
def dump(v):return json.dumps(v,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
def copy(asset):
 src=R/'assets'/asset;dst=O/'assets'/asset;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);return './assets/'+asset
D=json.loads((R/'src/data.json').read_text());A=json.loads((R/'assets/portrait-atlas.json').read_text());sheets=[dict(s,url=copy(s['asset'])) for s in A['sheets']];perk=json.loads((R/'assets/parody-icon-atlas.json').read_text());perk['url']=copy(perk['asset']);icons={s['id']:dict(s,url=copy(s['asset']),sourceURL=s['url']) for s in json.loads((R/'assets/game-icon-sources.json').read_text())};branding={k:copy('branding/'+v) for k,v in {'logo':'logo.webp','cover':'cover.webp','intro':'intro.webp','uziEnding':'uzi-ending.webp'}.items()}
data=';'.join('window.'+k+'='+dump(v) for k,v in dict(WORLD_DATA=D,WORLD_ATLASES=sheets,WORLD_PORTRAITS=A['portraits'],WORLD_PERK_SHEET=perk,WORLD_SOURCES=json.loads((R/'image-sources.json').read_text()),WORLD_GAME_ICONS=icons,WORLD_BRANDING=branding,WORLD_MEME_BANNER=copy('equipment-meme-banner-v8.webp')).items())+';\n';(O/'data.js').write_text(data)
app=(R/'src/app.js').read_text();app=app.replace("(function(){'use strict';", "WORLD_PLATFORM.ready.then(function(){'use strict';").replace("const sourceHTML='<!DOCTYPE html>\\n'+document.documentElement.outerHTML,D=",'const D=')
a=app.index('function read(');b=app.index('function notify(',a);app=app[:a]+"function read(k,f=null){return WORLD_PLATFORM.read(k,f);}\nfunction write(k,v){WORLD_PLATFORM.write(k,v);}\nfunction remove(k){WORLD_PLATFORM.remove(k);}\n"+app[b:]
app=re.sub(r"function download\(url,name\)\{[^\n]+\}\nfunction downloadHTML\(\)\{[^\n]+\}\n",'',app)
app=app.replace("else if(a==='download-html')downloadHTML();",'').replace("else if(a==='poster')poster();", "else if(a==='poster')poster();else if(a==='save-album'){if(b.disabled)return;b.disabled=true;WORLD_PLATFORM.savePoster().then(()=>notify('图片已保存到相册')).catch(e=>notify(e.errMsg||e.message||'保存失败，请检查相册权限')).then(()=>{b.disabled=false;});}")
# Anchors are citations inside the offline tool, never navigation.
app=re.sub(r'<a href="\$\{esc\((.*?)\)\}" target="_blank" rel="noreferrer">',r'<span class="source-citation">参考来源：${esc(\1)}<br>',app)
app=app.replace('</a>','</span>').replace('（需联网）','（离线来源记录）')
app=app.replace('<button class="secondary" data-action="download-html">下载完整离线网页 ↓</button>','')
app=app.replace('长按图片保存，或下载完整 PNG。','点击下方按钮存入手机相册。').replace('<a class="primary download-png" href="${url}" download="世界上另一个我-V10-整活海报.png">下载 PNG 图片 ↓</span>','<button class="primary full-width" data-action="save-album">保存图片到相册 ↓</button>')
app=app.replace("const url=c.toDataURL('image/png');open", "const url=c.toDataURL('image/png');WORLD_PLATFORM.setPoster(url);open")
app=app.replace("function render(html){", "function render(html){persistent=WORLD_PLATFORM.isPersistent();")
app=app.replace("$('#loading').hidden=true;", "$('#loading').hidden=true;WORLD_PLATFORM.afterRender();")
app=app.replace('modal.scrollTop=0;', 'modal.scrollTop=0;WORLD_PLATFORM.afterRender();')
assert app.rstrip().endswith('})();');app=app.rstrip()[:-5]+'});\n'
for name,body in [('engine.js',(R/'src/engine.js').read_text()),('app.js',app),('platform.js',(R/'src/xhs-platform.js').read_text())]:
 assert not re.search(r'\?\.|\?\?|\.flatMap\(|\.flat\(|\{\s*\.\.\.',body),name
 (O/name).write_text(body);subprocess.run(['node','--check',str(O/name)],check=True)
css=(R/'src/style.css').read_text();css=re.sub(r'(?<![-\w])gap:([^;}]+)',r'grid-gap:\1;gap:\1',css)
def rgba(m):
 h=m.group(1);h=''.join(c*2 for c in h) if len(h)==4 else h;return 'rgba(%d,%d,%d,%.4f)'%(int(h[:2],16),int(h[2:4],16),int(h[4:6],16),int(h[6:8],16)/255)
css=re.sub(r'#([0-9a-fA-F]{8}|[0-9a-fA-F]{4})(?![0-9a-fA-F])',rgba,css)
css+='''\n/* Chrome 61 core geometry and native-container safe areas. */
button:focus,a:focus,input:focus{outline:2px solid var(--accent);outline-offset:3px}
header{padding-top:22px;padding-top:calc(22px + var(--safe-area-inset-top, env(safe-area-inset-top, 0px)))}
body{padding-left:0;padding-right:0;padding-left:var(--safe-area-inset-left,env(safe-area-inset-left,0px));padding-right:var(--safe-area-inset-right,env(safe-area-inset-right,0px));-webkit-touch-callout:none}
.result-dock{bottom:9px;bottom:calc(9px + var(--safe-area-inset-bottom,env(safe-area-inset-bottom,0px)))}
.portrait{position:relative;height:auto;aspect-ratio:auto}.portrait:before{content:'';display:block;padding-top:100%}.portrait>svg{position:absolute;top:0;left:0;width:100%;height:100%}
.perk-art{position:relative}.perk-art:before{content:'';display:block;padding-top:100%}.perk-art>svg{position:absolute;top:0;left:0;width:100%;height:100%}
.source-citation{font-size:11px;color:var(--muted);line-height:1.9;word-break:break-all;-webkit-user-select:text;user-select:text}
.source-citation img{width:44px;height:44px}.source-citation small{display:block}.dialog-fallback-open{overflow:hidden}dialog{display:none}dialog[open]{display:block;position:fixed;top:5%;left:5%;margin:0;width:90%;max-height:90%;z-index:50;overflow-y:auto;-webkit-overflow-scrolling:touch}
#dialog-body{overflow-wrap:break-word} .squad-candidates>*{min-width:0}.squad-candidates .portrait{min-height:0}
'''
(O/'style.css').write_text(css)
t=(R/'src/template.html').read_text();t=re.sub('<script>.*?</script>','',t,flags=re.S);t=t.replace('<style>__CSS__</style>','<link rel="stylesheet" href="./style.css">');t=re.sub('<button data-action="download-html">.*?</button>','',t);t=re.sub('<noscript>.*?</noscript>','<noscript>请启用小工具脚本。</noscript>',t,flags=re.S)
t=t.replace('</body>','<script src="./data.js"></script><script src="./engine.js"></script><script src="./platform.js"></script><script src="./app.js"></script></body>');(O/'index.html').write_text(t)
# Deterministic gates in addition to the supplied size audit.
files=list(O.rglob('*'));html=(O/'index.html').read_text();assert len(re.findall(r'<script\b',html))==4 and not re.search(r'<script(?![^>]*src=)',html)
for path in files:
 if not path.is_file():continue
 assert path.suffix in ('.html','.css','.js','.png','.webp','.jpg','.jpeg','.json','.svg','.woff','.woff2','.gif')
 if path.suffix not in ('.js','.html','.css'):continue
 text=path.read_text();assert not re.search(r'\b(?:fetch\s*\(|XMLHttpRequest|WebSocket|EventSource|Worker\s*\(|eval\s*\(|new Function|WebAssembly)|target="_blank"|<a[^>]+download|createObjectURL|sourceHTML|downloadHTML',text),str(path)
 assert not re.search(r'(?:src|href)=[\"\']https?://',text),str(path)
 assert not re.search(r'data:image/[^;]+;base64,[A-Za-z0-9+/=]{1000}',text),str(path)
zip_path=R/'release/world-another-me-v10-xhs.zip'
with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for path in sorted(O.rglob('*')):
  if path.is_file():z.write(path,path.relative_to(O).as_posix())
assert zip_path.stat().st_size<=10*1024*1024
print(json.dumps({'zip':str(zip_path),'bytes':zip_path.stat().st_size,'sha256':hashlib.sha256(zip_path.read_bytes()).hexdigest(),'files':len([p for p in files if p.is_file()]),'entry':'index.html','syntax':'ES2017 authored; Chrome 61/device compatibility NOT physically tested'},ensure_ascii=False,indent=2))
