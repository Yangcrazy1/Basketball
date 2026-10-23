"""Build the complete offline web app using only the Python standard library."""
from pathlib import Path
import json,base64
root=Path(__file__).resolve().parent
sources=json.loads((root/'image-sources.json').read_text())
images={}
for item in sources:
 p=root/'assets'/item['asset'];mime='image/png' if p.suffix.lower()=='.png' else 'image/jpeg'
 images[item['id']]='data:'+mime+';base64,'+base64.b64encode(p.read_bytes()).decode()
def js(value):return json.dumps(value,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
values={'__CSS__':(root/'src/style.css').read_text(),'__ENGINE__':(root/'src/engine.js').read_text(),'__TOY__':(root/'src/toy3d.js').read_text(),'__APP__':(root/'src/app.js').read_text(),'__DATA__':js(json.loads((root/'src/data.json').read_text())),'__IMAGES__':js(images),'__SOURCES__':js(sources),'__SHEET__':js('data:image/webp;base64,'+base64.b64encode((root/'assets/portraits-v5.webp').read_bytes()).decode())}
html=(root/'src/template.html').read_text()
for token,value in values.items():html=html.replace(token,value)
(root/'dist').mkdir(exist_ok=True)
p=root/'dist/world-another-me.html';p.write_text(html);print(f'{p}: {p.stat().st_size:,} bytes')
