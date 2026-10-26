"""Build the basketball entertainment web and local-resource XHS artifacts."""
from pathlib import Path
import base64
import hashlib
import json
import re
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
RELEASE = ROOT / 'release'
DIST.mkdir(exist_ok=True)
RELEASE.mkdir(exist_ok=True)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def dumps(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')


def archive(folder, output):
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for path in sorted(folder.rglob('*')):
            if path.is_file():
                z.write(path, path.relative_to(folder).as_posix())
    return {'bytes': output.stat().st_size, 'sha256': sha(output.read_bytes())}


data = json.loads((ROOT / 'content/data.json').read_text())
portraits = json.loads((ROOT / 'content/portraits.json').read_text())
card_art = json.loads((ROOT / 'content/cards-art.json').read_text())
assert data['name'] == '整活NBA'
assert len(data['characters']) == 21 and len(data['questions']) == 132
payload = 'window.NBA_DATA=' + dumps(data) + ';window.NBA_PORTRAITS=' + dumps(portraits) + ';window.NBA_CARD_ART=' + dumps(card_art) + ';\n'

for mode in ['web', 'xhs']:
    out = DIST / mode
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir()
    shutil.copytree(ROOT / 'assets', out / 'assets')
    for filename in ['index.html', 'style.css', 'app.js']:
        shutil.copy2(ROOT / 'web' / filename, out / filename)
    css_path = out / 'style.css'
    css_text = css_path.read_text()
    def rgba(match):
        value = match.group(1)
        if len(value) == 4:
            value = ''.join(c * 2 for c in value)
        return 'rgba(%d,%d,%d,%.4f)' % (int(value[:2], 16), int(value[2:4], 16), int(value[4:6], 16), int(value[6:8], 16) / 255)
    css_text = re.sub(r'#([0-9a-fA-F]{8}|[0-9a-fA-F]{4})(?![0-9a-fA-F])', rgba, css_text)
    css_path.write_text(css_text)
    shutil.copy2(ROOT / 'content/engine.js', out / 'engine.js')
    shutil.copy2(ROOT / 'shared/game.js', out / 'game.js')
    shutil.copy2(ROOT / 'shared' / ('platform-' + mode + '.js'), out / 'platform.js')
    (out / 'data.js').write_text(payload)
    if mode == 'web':
        entry = (out / 'index.html').read_text()
        for name in ['style.css', 'engine.js', 'data.js', 'game.js', 'platform.js', 'app.js', 'assets/logo.webp']:
            entry = entry.replace('./' + name + '"', './' + name + '?v=' + sha((out / name).read_bytes())[:12] + '"')
        (out / 'index.html').write_text(entry)

# Independent single file for browsers which can execute downloaded HTML.
offline_portraits = json.loads(json.dumps(portraits))
offline_cards = json.loads(json.dumps(card_art))
for mapping in [offline_portraits['portraits'], offline_cards['cards']]:
    for entry in mapping.values():
        raw = (ROOT / entry['src']).read_bytes()
        entry['src'] = 'data:image/webp;base64,' + base64.b64encode(raw).decode()
css = (DIST / 'web/style.css').read_text()
for path in (ROOT / 'assets').glob('*.webp'):
    url = 'data:image/webp;base64,' + base64.b64encode(path.read_bytes()).decode()
    css = re.sub(r'(?:\./)?assets/' + re.escape(path.name), lambda m: url, css)
page = (ROOT / 'web/index.html').read_text()
page = re.sub(r'<link rel="stylesheet" href="(?:\./)?style\.css">', lambda m: '<style>' + css + '</style>', page)
inline_data = 'window.NBA_DATA=' + dumps(data) + ';window.NBA_PORTRAITS=' + dumps(offline_portraits) + ';window.NBA_CARD_ART=' + dumps(offline_cards) + ';'
scripts = {'engine.js': (ROOT / 'content/engine.js').read_text(), 'data.js': inline_data,
           'game.js': (ROOT / 'shared/game.js').read_text(), 'platform.js': (ROOT / 'shared/platform-web.js').read_text(),
           'app.js': (ROOT / 'web/app.js').read_text()}
for name, body in scripts.items():
    page = re.sub(r'<script src="(?:\./)?' + re.escape(name) + r'"></script>', lambda m: '<script>' + body.replace('</script', '<\\/script') + '</script>', page)
for path in (ROOT / 'assets').glob('*.webp'):
    page = re.sub(r'(?:\./)?assets/' + re.escape(path.name), lambda m: 'data:image/webp;base64,' + base64.b64encode(path.read_bytes()).decode(), page)
(RELEASE / 'zhenghuo-nba-offline.html').write_text(page)
web_zip = RELEASE / 'zhenghuo-nba-web.zip'
xhs_zip = RELEASE / 'zhenghuo-nba-xhs.zip'
manifest = {'name': '整活NBA', 'version': 1, 'core': 'entertainment personality quiz',
            'people': 21, 'questions': 132, 'newCourtQuestions': 24, 'cards': 51,
            'dataSHA256': sha((ROOT / 'content/data.json').read_bytes()),
            'engineSHA256': sha((ROOT / 'content/engine.js').read_bytes()),
            'webURL': 'https://yangcrazy1.github.io/Basketball/nba/',
            'wechatAcceptance': 'pending: WeChat Developer Tools, AppID and physical-device validation',
            'xhsAcceptance': 'pending: 创服平台模拟器、Android 与 iOS 真机扫码',
            'artifacts': {web_zip.name: archive(DIST / 'web', web_zip), xhs_zip.name: archive(DIST / 'xhs', xhs_zip)}}
assert manifest['artifacts'][xhs_zip.name]['bytes'] < 10 * 1024 ** 2
raw = (RELEASE / 'zhenghuo-nba-offline.html').read_bytes()
manifest['artifacts']['zhenghuo-nba-offline.html'] = {'bytes': len(raw), 'sha256': sha(raw)}
(DIST / 'build-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(manifest, ensure_ascii=False, indent=2))
