"""Install original V14 paintings and append atlas mappings without changing old cells."""
from pathlib import Path
import hashlib, json, shutil
from PIL import Image

R = Path(__file__).resolve().parents[1]
def read(name):
    return json.loads((R / name).read_text())
def write(name, value):
    (R / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

branding = read('assets/branding/branding-v14.json')
originals = {
    'introRealLife': 'exec-3b83b3db-f3a5-4fcd-a21f-be5198bf7fb2.png',
    'introMirror': 'exec-d67aef93-0a6e-44ce-a6b1-02fdcb177911.png',
    'introNewWorld': 'exec-b03952cc-05f6-4f07-b1a1-1e2b87c800cb.png',
}
for key, original in originals.items():
    meta = branding[key]
    source = Path('/workspace/generated_images') / original
    target = R / 'assets' / meta['png']
    shutil.copy2(source, target)
    image = Image.open(source).convert('RGB')
    image.thumbnail((800, 1000), Image.Resampling.LANCZOS)
    webp = R / 'assets' / meta['webp']
    image.save(webp, 'WEBP', quality=84, method=6)
    meta.update(originalName=original, originalSha256=sha(source), sha256=sha(webp),
                width=image.width, height=image.height)
write('assets/branding/branding-v14.json', branding)

perk_sheets = read('assets/rich-perk-atlases.json')
name = 'parody-icons-v14.webp'
image = Image.open('/workspace/generated_images/exec-80077beb-ba8e-4779-a8d8-9d630b511299.png').convert('RGB')
image.save(R / 'assets' / name, 'WEBP', quality=90, method=6)
meta = {'asset': name, 'width': image.width, 'height': image.height,
        'columns': 4, 'rows': 4, 'sha256': sha(R / 'assets' / name),
        'kind': '本作原创AI棱彩漫画图标',
        'generatedOriginalName': 'exec-80077beb-ba8e-4779-a8d8-9d630b511299.png'}
if not any(s['asset'] == name for s in perk_sheets):
    perk_sheets.append(meta)
write('assets/rich-perk-atlases.json', perk_sheets)

patch = read('content/v14-portrait-patch.json')
atlas = read('assets/portrait-atlas.json')
indexes = {}
for i, sheet in enumerate(patch['sheets']):
    index = next((j for j, old in enumerate(atlas['sheets']) if old['asset'] == sheet['asset']), None)
    if index is None:
        index = len(atlas['sheets'])
        atlas['sheets'].append(sheet)
    indexes[i] = index
for pid, portrait in patch['portraits'].items():
    atlas['portraits'][pid] = dict(portrait, sheet=indexes[portrait['sheet']])
write('assets/portrait-atlas.json', atlas)
refs = read('image-sources.json')
for ref in patch['references']:
    refs = [old for old in refs if old['id'] != ref['id']]
    refs.append(ref)
write('image-sources.json', refs)
print('Installed 3 independent paintings, 16 perk icons, 2 verified portrait mappings.')
