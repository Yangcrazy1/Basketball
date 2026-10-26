"""Build an importable native WeChat project. No login, upload or device claims."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import zipfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'wechat'
MINI = PROJECT / 'miniprogram'
LIB = MINI / 'lib'
LIMIT = 2 * 1024 * 1024


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def put_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n')


def pack_images(filename, key, target):
    raw = json.loads((ROOT / 'content' / filename).read_text())
    images = raw.get(key, raw)
    outputs, provenance = {}, []
    folder = MINI / 'assets' / target
    folder.mkdir(parents=True, exist_ok=True)
    for item_id, meta in images.items():
        source = ROOT / meta['src']
        with Image.open(source) as original:
            image = original.copy()
            image.thumbnail((256, 256) if target == 'portraits' else (160, 160), Image.Resampling.LANCZOS)
            if image.mode == 'RGBA':
                rgb = Image.new('RGB', image.size, (21, 16, 36))
                rgb.paste(image, mask=image.getchannel('A'))
                image = rgb
            else:
                image = image.convert('RGB')
            # JPEG is a conservative native Canvas choice. Only the distributed
            # copy is converted; original generated art and references stay intact.
            output = folder / (item_id + '.jpg')
            image.save(output, 'JPEG', quality=83, optimize=True, progressive=False)
            outputs[item_id] = dict(meta, src=output.relative_to(MINI).as_posix(), width=image.width, height=image.height,
                                    nativeFormat='JPEG', sourceSHA256=digest(source), sha256=digest(output))
        provenance.append({'id': item_id, 'source': meta['src'], 'sourceSHA256': digest(source),
                           'path': output.relative_to(MINI).as_posix(), 'bytes': output.stat().st_size, 'sha256': digest(output)})
    put_json(LIB / filename, {key: outputs})
    return provenance


def main():
    LIB.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(MINI / 'assets', ignore_errors=True)
    for name in ['data.json', 'engine.js']:
        shutil.copy2(ROOT / 'content' / name, LIB / name)
    shutil.copy2(ROOT / 'shared/game.js', LIB / 'game.js')
    portrait_images = pack_images('portraits.json', 'portraits', 'portraits')
    card_images = pack_images('cards-art.json', 'cards', 'cards')
    for source in MINI.rglob('*.js'):
        subprocess.run(['node', '--check', str(source)], check=True)
    app = json.loads((MINI / 'app.json').read_text())
    for page in app['pages']:
        assert all((MINI / (page + suffix)).is_file() for suffix in ['.js', '.json', '.wxml']), page
    files = sorted(p for p in MINI.rglob('*') if p.is_file())
    assert not any(p.suffix in ['.map', '.ts'] for p in files)
    runtime_bytes = sum(p.stat().st_size for p in files)
    if runtime_bytes > LIMIT:
        raise RuntimeError('Native uncompressed main package exceeds 2 MiB: ' + str(runtime_bytes))
    data = json.loads((LIB / 'data.json').read_text())
    manifest = {
        'name': '整活NBA', 'format': 'native WXML/WXSS/JS project; not a web-view wrapper',
        'runtimeFiles': len(files), 'mainPackageUncompressedBytes': runtime_bytes, 'conservativeMainPackageLimitBytes': LIMIT,
        'sourceSchema': data['version'], 'enabledPeople': len([p for p in data['characters'] if p.get('enabled') is not False]),
        'activeQuestions': len([q for q in data['questions'] if q.get('enabled') is not False]),
        'activeCards': sum(len([a for a in arr if a.get('enabled') is not False]) for arr in data['augments'].values()),
        'dataSHA256': digest(LIB / 'data.json'), 'engineSHA256': digest(LIB / 'engine.js'), 'sharedGameSHA256': digest(LIB / 'game.js'),
        'portraitDistribution': portrait_images, 'cardDistribution': card_images,
        'appid': 'touristappid placeholder; replace with the actual WeChat mini-program AppID before platform upload',
        'pending': ['微信开发者工具完整功能验证', 'Android 微信真机验证', 'iOS 微信真机验证', '真实 AppID 配置与平台审核'],
        'acceptance': 'Only Node/static/package checks are available here; no WeChat Developer Tools or physical device result.'
    }
    manifest_file = PROJECT / 'build-manifest.json'
    manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    release = ROOT / 'release'
    release.mkdir(exist_ok=True)
    archive = release / 'zhenghuo-nba-wechat.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for path in sorted(PROJECT.rglob('*')):
            if path.is_file() and path.name != 'project.private.config.json' and '.DS_Store' not in path.parts:
                z.write(path, path.relative_to(PROJECT).as_posix())
    report = dict(manifest, zip=archive.relative_to(ROOT).as_posix(), zipBytes=archive.stat().st_size, zipSHA256=digest(archive))
    (release / 'wechat-build.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({key: report[key] for key in ['zip', 'zipBytes', 'zipSHA256', 'runtimeFiles', 'mainPackageUncompressedBytes', 'enabledPeople', 'activeQuestions', 'activeCards', 'pending']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
