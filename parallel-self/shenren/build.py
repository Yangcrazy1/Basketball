"""Build one self-contained HTML. No third-party runtime, CDN or backend required."""
from pathlib import Path
import json,base64,hashlib
root=Path(__file__).resolve().parent
def js(v):return json.dumps(v,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
def data_url(asset,mime):return 'data:'+mime+';base64,'+base64.b64encode((root/'assets'/asset).read_bytes()).decode()
sources=json.loads((root/'image-sources.json').read_text());atlas=json.loads((root/'assets/portrait-atlas.json').read_text());data=json.loads((root/'src/data.json').read_text())
sheets=[dict(s,url=data_url(s['asset'],'image/webp')) for s in atlas['sheets']]
icons={a['id']:data_url(a['asset'],'image/png') for a in data['augments']['lol']}
values={'__CSS__':(root/'src/style.css').read_text(),'__ENGINE__':(root/'src/engine.js').read_text(),'__APP__':(root/'src/app.js').read_text(),'__DATA__':js(data),'__ATLASES__':js(sheets),'__PORTRAITS__':js(atlas['portraits']),'__AUGMENTS__':js(icons),'__SOURCES__':js(sources)}
html=(root/'src/template.html').read_text()
for k,v in values.items():html=html.replace(k,v)
assert '__TOY__' not in html and 'Toy3D' not in html and 'toy-canvas' not in html
for p in data['characters']:assert p['personId'] in atlas['portraits']
(root/'dist').mkdir(exist_ok=True);p=root/'dist/world-another-me.html';p.write_text(html);print(f'{p}: {p.stat().st_size:,} bytes; sha256 {hashlib.sha256(p.read_bytes()).hexdigest()}')
