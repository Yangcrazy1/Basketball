"""Build a standalone offline HTML file, with no third-party build dependencies."""
from pathlib import Path
import json
import base64

root = Path(__file__).resolve().parent
template = (root / 'src/template.html').read_text()
data = json.dumps(json.loads((root / 'src/data.json').read_text()), ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
portrait = root / 'src/assets/topic-cartoons.webp'
portrait_mime = 'image/webp'
if not portrait.exists():
    portrait = root / 'src/assets/topic-cartoons.png'
    portrait_mime = 'image/png'
values = {
    '__PORTRAIT_IMAGE__': 'data:' + portrait_mime + ';base64,' + base64.b64encode(portrait.read_bytes()).decode('ascii'),
    '__CSS__': (root / 'src/style.css').read_text(),
    '__ENGINE__': (root / 'src/engine.js').read_text(),
    '__STORAGE__': (root / 'src/storage.cjs').read_text(),
    '__DATA__': data,
    '__APP__': (root / 'src/app.js').read_text(),
    '__NOTICES__': (root / 'THIRD_PARTY_NOTICES.txt').read_text().replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'),
}
references = {}
for person in json.loads((root / 'src/data.json').read_text())['characters']:
    asset = person.get('scene', {}).get('asset')
    if asset:
        image = root / 'src/assets' / asset
        mime = 'image/png' if image.suffix.lower() == '.png' else 'image/jpeg'
        references[person['id']] = 'data:' + mime + ';base64,' + base64.b64encode(image.read_bytes()).decode('ascii')
values['__REFERENCE_IMAGES__'] = json.dumps(references, separators=(',', ':'))
for token, value in values.items():
    template = template.replace(token, value)
(root / 'dist').mkdir(exist_ok=True)
target = root / 'dist/parallel-self.html'
target.write_text(template)
print(f'{target}: {target.stat().st_size:,} bytes')
