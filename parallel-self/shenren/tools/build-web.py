"""Fast online build; keep the fully embedded HTML as the separate offline download."""
from pathlib import Path
import json,hashlib,re,shutil
R=Path(__file__).resolve().parents[1];O=R/'dist/web';shutil.rmtree(O,ignore_errors=True);O.mkdir(parents=True)
def dump(v):return json.dumps(v,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
def asset(name):
 src=R/'assets'/name;dst=O/'assets'/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);return './assets/'+name
A=json.loads((R/'assets/portrait-atlas.json').read_text());D=json.loads((R/'src/data.json').read_text());perk=json.loads((R/'assets/parody-icon-atlas.json').read_text());perk['url']=asset(perk['asset']);sheets=[dict(s,url=asset(s['asset'])) for s in A['sheets']];icons={s['id']:dict(s,url=asset(s['asset']),sourceURL=s['url']) for s in json.loads((R/'assets/game-icon-sources.json').read_text())};branding={k:asset('branding/'+v) for k,v in {'logo':'logo.webp','cover':'cover.webp','intro':'intro.webp','home':'home-v11.webp','uziEnding':'uzi-ending.webp'}.items()}
values=dict(WORLD_DATA=D,WORLD_LEGACY_DATA=json.loads((R/'src/legacy/data.json').read_text()),WORLD_ATLASES=sheets,WORLD_PORTRAITS=A['portraits'],WORLD_PERK_SHEET=perk,WORLD_SOURCES=json.loads((R/'image-sources.json').read_text()),WORLD_GAME_ICONS=icons,WORLD_BRANDING=branding,WORLD_MEME_BANNER=asset('equipment-meme-banner-v8.webp'))
data=';'.join('window.'+k+'='+dump(v) for k,v in values.items())+';\n'
app=(R/'src/app.js').read_text();app=app.replace("const sourceHTML='<!DOCTYPE html>\\n'+document.documentElement.outerHTML,D=",'const D=')
a=app.index('function downloadHTML(){');b=app.index('\n',a);app=app[:a]+"function downloadHTML(){download('./world-another-me.html','世界上另一个我-V11-离线版.html');notify('正在下载完整离线网页，包含题库和全部插画。');}"+app[b:]
boot="""(function(){'use strict';function stalled(){if(document.documentElement.dataset.appReady)return;var e=document.getElementById('loading');if(e){var p=e.querySelector('p');if(p)p.textContent='页面还没加载完成，请点下方刷新重试。';var a=e.querySelector('a');if(a)a.hidden=false;}}window.addEventListener('error',stalled,true);setTimeout(stalled,12000);})();"""
def script(base,body,ext='js'):
 raw=body.encode();name=base+'-'+hashlib.sha256(raw).hexdigest()[:12]+'.'+ext;(O/name).write_bytes(raw);return name
boot_name=script('boot',boot);css=script('style',(R/'src/style.css').read_text(),'css');names=[script('data',data),script('engine',(R/'src/legacy/engine.js').read_text().replace('root.ShenrenEngine','root.ShenrenLegacyEngine')+'\n'+(R/'src/engine.js').read_text()),script('app',app)]
t=(R/'src/template.html').read_text();t=re.sub('<style>.*?</style>','<link rel="stylesheet" href="./'+css+'">',t,flags=re.S);t=re.sub('<script>.*?</script>','',t,flags=re.S);t=t.replace('</head>','<script src="./'+boot_name+'"></script></head>');t=t.replace('人物头像、恶搞海克斯图标与题库均已打包。','正在加载题库和开场漫画，其余图片会在需要时加载。').replace('</section>\n<header>','<a href="?v=11-preview-retry" hidden>刷新重试 ↗</a></section>\n<header>',1);t=t.replace('</body>',''.join('<script src="./'+n+'"></script>' for n in names)+'</body>');assert not re.search(r'__[A-Z_]+__',t);(O/'index.html').write_text(t)
# Same-origin URL points at this exact self-contained release, never an HTML shell.
shutil.copy2(R/'dist/world-another-me.html',O/'world-another-me.html')
report={'entry_bytes':len(t.encode()),'entry_sha256':hashlib.sha256(t.encode()).hexdigest(),'core_bytes':sum((O/n).stat().st_size for n in [boot_name,css]+names)+len(t.encode()),'offline_html_bytes':(O/'world-another-me.html').stat().st_size,'offline_html_sha256':hashlib.sha256((O/'world-another-me.html').read_bytes()).hexdigest(),'core_files':[boot_name,css]+names,'mode':'split assets; portraits loaded on demand; offline export is a separate self-contained file'}
(R/'dist/web-build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
