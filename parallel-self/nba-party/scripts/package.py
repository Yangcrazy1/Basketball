"""Publishable downloads for the tested NBA-only entertainment release."""
from pathlib import Path
import hashlib
import html
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / 'dist/web'
RELEASE = ROOT / 'release'
manifest = json.loads((ROOT / 'dist/build-manifest.json').read_text())
browser = json.loads((ROOT / 'docs/browser-check.json').read_text())
assert browser['status'] == 'passed'
assert browser['dataSHA256'] == manifest['dataSHA256']
downloads = WEB / 'downloads'
downloads.mkdir(exist_ok=True)
names = ['zhenghuo-nba-wechat.zip', 'zhenghuo-nba-xhs.zip', 'zhenghuo-nba-web.zip', 'zhenghuo-nba-offline.html']
for name in names:
    source = RELEASE / name
    raw = source.read_bytes()
    manifest['artifacts'][name] = {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
    shutil.copy2(source, downloads / name)
manifest['runtimeFiles'] = {name: hashlib.sha256((WEB / name).read_bytes()).hexdigest() for name in ['index.html','style.css','app.js','engine.js','game.js','platform.js','data.js']}
assert manifest['runtimeFiles']['app.js'] == browser['appSHA256']
manifest['browserChecks'] = browser['count']
manifest['nativeWeChatVerified'] = False
manifest['nativeXhsVerified'] = False
manifest['screenshots'] = []
shots = ROOT / 'dist/qa'
if shots.exists():
    (WEB / 'screenshots').mkdir(exist_ok=True)
    for path in sorted(shots.glob('*.png')):
        shutil.copy2(path, WEB / 'screenshots' / path.name)
        manifest['screenshots'].append(path.name)
(ROOT / 'docs/build-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
buttons = ''
labels = {'zhenghuo-nba-wechat.zip': '微信原生小程序工程 ZIP', 'zhenghuo-nba-xhs.zip': '整活NBA小红书 ZIP',
          'zhenghuo-nba-web.zip': '网页部署 ZIP', 'zhenghuo-nba-offline.html': '完整离线网页 HTML'}
for name in names:
    info = manifest['artifacts'][name]
    buttons += '<article><a class="button" href="./downloads/' + name + '?v=' + info['sha256'][:12] + '" download>' + labels[name] + ' ↓</a><p>' + str(round(info['bytes'] / 1024)) + ' KiB</p><code>SHA256 ' + info['sha256'] + '</code></article>'
branding_buttons = ''
for name, label in [('logo','透明黑洞 Logo PNG'), ('cover','整活NBA宇宙封面 PNG')]:
    source = ROOT / 'branding' / (name + '.png')
    if source.exists():
        shutil.copy2(source, downloads / source.name)
        manifest[name + 'Download'] = './downloads/' + source.name
        manifest[name + 'SHA256'] = hashlib.sha256(source.read_bytes()).hexdigest()
        branding_buttons += '<a class="button secondary" href="./downloads/' + source.name + '" download>' + label + ' ↓</a>'
(ROOT / 'docs/build-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
gallery = ''.join('<figure><img src="./screenshots/' + html.escape(name) + '" alt="' + html.escape(name) + ' 手机视口实际截图"></figure>' for name in manifest['screenshots'] if name in ['home.png', 'result.png', 'diy.png', 'story.png'])
page = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>整活NBA · 下载与验证</title><style>
:root{color-scheme:dark;font-family:system-ui,-apple-system,'PingFang SC',sans-serif;background:#100d1c;color:#faf0e4}*{box-sizing:border-box}body{margin:0}main{max-width:1040px;padding:36px 22px 70px;margin:auto}h1{font-size:38px;color:#f6cf87}p{line-height:1.9;color:#c8bbda}.button{display:inline-block;padding:15px 20px;background:#f6cf87;color:#24162f;border-radius:12px;text-decoration:none;font-weight:700;min-height:48px;margin:8px 8px 8px 0}.secondary{background:#30213e;color:#ecdafa;border:1px solid #8c6bad}article{padding:20px;border:1px solid #5d4479;border-radius:16px;margin:20px 0;background:#1c172a}code{display:block;overflow-wrap:anywhere;color:#b8a2ce;font-size:11px}.gallery{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));grid-gap:18px}figure{margin:0}img{max-width:100%;border-radius:14px}@media(max-width:650px){.gallery{grid-template-columns:1fr}h1{font-size:32px}}
</style></head><body><main><p>V13 紫金漫画风 · 篮球独立娱乐测试</p><h1>整活NBA</h1><p>回答球场日常问题，看看你是哪位平行球星；获得整活海克斯，组出五人团，还能DIY自己的球星。21 位人物、132 道题、51 张海克斯；新增24道球场题。</p><a class="button" href="./">手机直接开始玩 ↗</a><a class="button secondary" href="https://yangcrazy1.github.io/Basketball/v13/downloads/world-another-me-v13-xhs.zip">V13 原版小红书包 ↓</a>
<p>微信包是原生 WXML／WXSS／JS 工程，解压后用微信开发者工具导入 project.config.json 所在目录。它不是微信聊天中点击安装的文件，正式预览需配置自己的 AppID。</p>__DOWNLOADS__
<article><h2>实测与待验证</h2><p>__COUNT__ 组普通浏览器流程已通过，截图为手机视口模拟。微信开发者工具编译、正式AppID、Android/iOS微信真机与平台审核仍待验证。小红书ZIP须上传创服平台，先做平台模拟器完整验证，再分别用Android和iOS真机扫码同一ZIP；普通浏览器或SDK模拟不等于原生验收。Chrome61 CSS与实机性能未实测。</p><p>全部答案、DIY球星和阵容保存在本机。DIY球星作为自选队友，不篡改答题匹配身份；娱乐创作，不代表球星真实经历或本人发言。</p></article><div class="gallery">__GALLERY__</div></main></body></html>'''
page = page.replace('__DOWNLOADS__', buttons + branding_buttons).replace('__COUNT__', str(browser['count'])).replace('__GALLERY__', gallery)
(WEB / 'download.html').write_text(page)
print(json.dumps(manifest['artifacts'], ensure_ascii=False, indent=2))
