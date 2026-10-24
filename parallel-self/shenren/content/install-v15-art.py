"""Append V15 art while preserving every published historical atlas cell."""
from pathlib import Path
import json
R = Path(__file__).resolve().parents[1]
def read(path): return json.loads((R/path).read_text())
def write(path, value): (R/path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
branding=read('assets/branding/branding-v14.json')
branding.update(read('content/v15-branding-patch.json'))
write('assets/branding/branding-v15.json',branding)
atlas=read('assets/portrait-atlas.json')
sources=read('image-sources.json')
for filename in ['content/v15-portrait-patch.json','content/v15-369-portrait-patch.json']:
    patch=read(filename)
    offset={}
    for i,sheet in enumerate(patch['sheets']):
        index=next((j for j,s in enumerate(atlas['sheets']) if s['asset']==sheet['asset']),None)
        if index is None:
            index=len(atlas['sheets']);atlas['sheets'].append(sheet)
        offset[i]=index
    for pid,m in patch['portraits'].items():
        atlas['portraits'][pid]=dict(m,sheet=offset[m['sheet']])
    for ref in patch['references']:
        sources=[old for old in sources if old['id']!=ref['id']]+[ref]
write('assets/portrait-atlas.json',atlas)
write('image-sources.json',sources)
perk_patch=R/'content/v15-perk-art-patch.json'
if perk_patch.exists():
    patch=read('content/v15-perk-art-patch.json')
    sheets=read('assets/rich-perk-atlases.json')
    additions=patch.get('sheets',[]) if isinstance(patch,dict) else patch
    for sheet in additions:
        if not any(s['asset']==sheet['asset'] for s in sheets): sheets.append(sheet)
    write('assets/rich-perk-atlases.json',sheets)
print('V15 logo, cover and two new portrait source mappings installed.')
