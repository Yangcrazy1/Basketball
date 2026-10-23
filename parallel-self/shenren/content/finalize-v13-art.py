"""Install the V13 original perk art and narrowly merge final editorial patches."""
from pathlib import Path
import hashlib
import json
from PIL import Image

R = Path(__file__).resolve().parents[1]
read = lambda p: json.loads((R / p).read_text())
def write(p, value):
    (R / p).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

data = read('src/data.json')
data['name'] = '平行宇宙的另一个我'
atlases = read('assets/rich-perk-atlases.json')
sources = [
    ('basket', 'exec-cad4cd80-da4c-4e2e-8452-696e5894a00f.png'),
    ('memes', 'exec-f6cee1ae-b4d8-4109-96fa-509222a1c4bc.png'),
]
sheet_ids = {}
for kind, original in sources:
    name = 'parody-icons-v13-' + kind + '.webp'
    source = Path('/workspace/generated_images') / original
    image = Image.open(source).convert('RGB')
    image.thumbnail((1254, 1254), Image.Resampling.LANCZOS)
    target = R / 'assets' / name
    image.save(target, 'WEBP', quality=90, method=6)
    meta = {'asset': name, 'width': image.width, 'height': image.height,
            'columns': 4, 'rows': 4, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
            'kind': '本作原创AI棱彩漫画图标', 'generatedOriginalName': original}
    index = next((i for i, row in enumerate(atlases) if row['asset'] == name), None)
    if index is None:
        index = len(atlases)
        atlases.append(meta)
    else:
        atlases[index] = meta
    sheet_ids[kind] = index

# Three cards per person: two answer effects and one explicitly identified gift.
mapping = {
    'wuyou': ('basket', [0, 1, 0]), 'xire': ('basket', [2, 3, 2]),
    'tmac': ('basket', [4, 5, 4]), 'shaq': ('basket', [6, 7, 6]),
    'doncic': ('basket', [8, 9, 8]), 'shai': ('basket', [10, 11, 10]),
    'rodman': ('basket', [12, 13, 12]), 'wilt': ('basket', [14, 15, 14]),
    'yujie': ('memes', [0, 12, 0]), 'musk': ('memes', [1, 13, 13]),
    'trump': ('memes', [2, 14, 2]), 'renzhengfei': ('memes', [3, 3, 3]),
    'yuchengdong': ('memes', [4, 4, 4]), 'jensen': ('memes', [5, 15, 5]),
    'nida': ('memes', [6, 7, 6]), 'yili': ('memes', [7, 7, 10]),
    'wangsicong': ('memes', [8, 9, 10]),
}
cards = {a['id']: a for rows in data['augments'].values() for a in rows}
# The roster author sharpened new punchlines after the initial merge.
for rows in read('content/v13-roster-additions.json')['augments'].values():
    for patch in rows:
        if patch['id'] == 'v13-wilt-2':
            continue  # Preserve the explicit fictional collectible-card setting.
        for key in ('punchline', 'line'):
            if key in patch:
                cards[patch['id']][key] = patch[key]
for person, (kind, cells) in mapping.items():
    for num, cell in enumerate(cells, 1):
        a = cards['v13-' + person + '-' + str(num)]
        a['classicSprite'] = {'sheet': sheet_ids[kind], 'cell': cell}
        a['preferClassic'] = True
        a.pop('visual', None)
        a['creation'] = '本作原创恶搞效果与AI棱彩漫画图标；不代表真实人物观点或游戏官方效果。'
wash = cards['v11-uzi-3']
wash.pop('visual', None)
wash['classicSprite'] = {'sheet': sheet_ids['memes'], 'cell': 11}
wash['preferClassic'] = True
wash['creation'] = '本作原创恶搞效果与AI漫画洗澡冷却器图标；架空整活设定。'

fix = read('content/v13-evidence-fix.json')
for patch in fix['cards']:
    cards[patch['id']].update(patch)
questions = {q['id']: q for q in data['questions']}
for patch in fix['questions']:
    q = questions[patch['id']]
    for key, value in patch.items():
        if key not in ('id', 'options'):
            q[key] = value
    options = {a['id']: a for a in q['options']}
    for option in patch.get('options', []):
        options[option['id']]['text'] = option['text']

write('src/data.json', data)
write('assets/rich-perk-atlases.json', atlases)
write('assets/v13-perk-art.json', {'sheets': sources, 'sheetIds': sheet_ids,
      'people': mapping, 'uziShower': wash['classicSprite'],
      'collector': '保留五把真实装备图标；未被原创漫画图标覆盖。'})
print(json.dumps({'sheets': sheet_ids, 'newCardsMapped': 51, 'evidenceCardsFixed': len(fix['cards'])}, ensure_ascii=False))
