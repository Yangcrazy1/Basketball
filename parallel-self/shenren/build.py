"""Build one self-contained HTML. No third-party runtime, CDN or backend required."""
from pathlib import Path
import json,base64,hashlib,html as html_module
root=Path(__file__).resolve().parent
css=(root/'src/style.css').read_text()+('\n'+(root/'src/v14.css').read_text() if (root/'src/v14.css').exists() else '')
def description(d):return d.get('description') or d['name']+'：'+str(sum(p.get('enabled') is not False for p in d['characters']))+'位人物，三个世界，选择日常反应，获得身份和海克斯，走进会因选择改变的平行人生。'
def js(v):return json.dumps(v,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
def data_url(asset,mime):return 'data:'+mime+';base64,'+base64.b64encode((root/'assets'/asset).read_bytes()).decode()
sources=json.loads((root/'image-sources.json').read_text());atlas=json.loads((root/'assets/portrait-atlas.json').read_text());data=json.loads((root/'src/data.json').read_text())
sheets=[dict(s,url=data_url(s['asset'],'image/webp')) for s in atlas['sheets']]
perk=json.loads((root/'assets/parody-icon-atlas.json').read_text());perk['url']=data_url(perk['asset'],'image/webp')
icons=json.loads((root/'assets/game-icon-sources.json').read_text())
game_icons={s['id']:dict(s,url=data_url(s['asset'],'image/png'),sourceURL=s['url']) for s in icons}
for a in data['augments']['lol']:
    if a.get('visual'):assert all(i in game_icons for i in a['visual']['icons'])
branding={name:data_url(meta['webp'],'image/webp') for name,meta in json.loads((root/'assets/branding/branding-v15.json').read_text()).items()}
card_art={a['id']:data_url(a['artAsset'],'image/webp') for arr in data['augments'].values() for a in arr if a.get('enabled') and a.get('artAsset') and not a.get('preferClassic')}
perk_sheets=[dict(a,url=data_url(a['asset'],'image/webp')) for a in json.loads((root/'assets/rich-perk-atlases.json').read_text())]
engines='\n'.join((root/('src/'+directory+'/engine.js')).read_text().replace('root.ShenrenEngine','root.'+name) for directory,name in [('legacy','ShenrenLegacyEngine'),('legacy-v11','ShenrenV11Engine'),('legacy-v12','ShenrenV12Engine'),('legacy-v13','ShenrenV13Engine')])+'\n'+(root/'src/engine.js').read_text()
values={'__APP_NAME__':html_module.escape(data['name'],quote=True),'__APP_DESCRIPTION__':html_module.escape(description(data),quote=True),'__PERK_SHEETS__':js(perk_sheets),'__CARD_ART__':js(card_art),'__BRANDING__':js(branding),'__CSS__':css,'__ENGINE__':engines,'__APP__':(root/'src/app.js').read_text(),'__V13_DATA__':js(json.loads((root/'src/legacy-v13/data.json').read_text())),'__V12_DATA__':js(json.loads((root/'src/legacy-v12/data.json').read_text())),'__V11_DATA__':js(json.loads((root/'src/legacy-v11/data.json').read_text())),'__LEGACY_DATA__':js(json.loads((root/'src/legacy/data.json').read_text())),'__DATA__':js(data),'__ATLASES__':js(sheets),'__PORTRAITS__':js(atlas['portraits']),'__PERKS__':js(perk),'__SOURCES__':js(sources),'__GAME_ICONS__':js(game_icons),'__MEME_BANNER__':js(data_url('equipment-meme-banner-v8.webp','image/webp'))}
html=(root/'src/template.html').read_text()
for k,v in values.items():html=html.replace(k,v)
assert 'WORLD_AUGMENTS' not in html
assert '__TOY__' not in html and 'Toy3D' not in html and 'toy-canvas' not in html
assert 'WORLD_V13_DATA=' in html and 'ShenrenV13Engine' in html
assert all(k in branding for k in ['introRealLife','introMirror','introNewWorld'])
for p in data['characters']:assert p['personId'] in atlas['portraits']
(root/'dist').mkdir(exist_ok=True);p=root/'dist/world-another-me.html';p.write_text(html);print(f'{p}: {p.stat().st_size:,} bytes; sha256 {hashlib.sha256(p.read_bytes()).hexdigest()}')
