"""Build one self-contained HTML. No third-party runtime, CDN or backend required."""
from pathlib import Path
import json,base64,hashlib
root=Path(__file__).resolve().parent
def js(v):return json.dumps(v,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
def data_url(asset,mime):return 'data:'+mime+';base64,'+base64.b64encode((root/'assets'/asset).read_bytes()).decode()
sources=json.loads((root/'image-sources.json').read_text());atlas=json.loads((root/'assets/portrait-atlas.json').read_text());data=json.loads((root/'src/data.json').read_text())
sheets=[dict(s,url=data_url(s['asset'],'image/webp')) for s in atlas['sheets']]
perk=json.loads((root/'assets/parody-icon-atlas.json').read_text());perk['url']=data_url(perk['asset'],'image/webp')
icons=json.loads((root/'assets/game-icon-sources.json').read_text())
game_icons={s['id']:dict(s,url=data_url(s['asset'],'image/png'),sourceURL=s['url']) for s in icons}
for a in data['augments']['lol']:
    if a.get('visual'):assert all(i in game_icons for i in a['visual']['icons'])
branding={name:data_url('branding/'+file,'image/webp') for name,file in {'logo':'logo.webp','cover':'cover.webp','intro':'intro.webp','home':'home-v11.webp','uziEnding':'uzi-ending.webp'}.items()}
card_art={a['id']:data_url(a['artAsset'],'image/webp') for arr in data['augments'].values() for a in arr if a.get('enabled') and a.get('artAsset')}
values={'__CARD_ART__':js(card_art),'__BRANDING__':js(branding),'__CSS__':(root/'src/style.css').read_text(),'__ENGINE__':(root/'src/legacy/engine.js').read_text().replace('root.ShenrenEngine','root.ShenrenLegacyEngine')+'\n'+(root/'src/engine.js').read_text(),'__APP__':(root/'src/app.js').read_text(),'__LEGACY_DATA__':js(json.loads((root/'src/legacy/data.json').read_text())),'__DATA__':js(data),'__ATLASES__':js(sheets),'__PORTRAITS__':js(atlas['portraits']),'__PERKS__':js(perk),'__SOURCES__':js(sources),'__GAME_ICONS__':js(game_icons),'__MEME_BANNER__':js(data_url('equipment-meme-banner-v8.webp','image/webp'))}
html=(root/'src/template.html').read_text()
for k,v in values.items():html=html.replace(k,v)
assert 'WORLD_AUGMENTS' not in html
assert '__TOY__' not in html and 'Toy3D' not in html and 'toy-canvas' not in html
for p in data['characters']:assert p['personId'] in atlas['portraits']
(root/'dist').mkdir(exist_ok=True);p=root/'dist/world-another-me.html';p.write_text(html);print(f'{p}: {p.stat().st_size:,} bytes; sha256 {hashlib.sha256(p.read_bytes()).hexdigest()}')
