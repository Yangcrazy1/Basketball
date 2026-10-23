"""Collect an already tested V13 release; never claim platform/device acceptance."""
from pathlib import Path
import hashlib, html, json, shutil, zipfile

R = Path(__file__).resolve().parents[1]
W = R / 'dist/web'
D = json.loads((R / 'src/data.json').read_text())
A = json.loads((R / 'assets/portrait-atlas.json').read_text())
sources = {r['id']: r for r in json.loads((R / 'image-sources.json').read_text())}
browser = json.loads((R / 'docs/browser-check-v13.json').read_text())
required = {'intro', 'new-art', 'collector', 'catalog', 'new-cast', 'cards', 'reveal-portraits', 'quiz', 'posters', 'v10-history', 'v11-history', 'standalone-squad', 'offline', 'native-contract', 'runtime-clean'}
assert browser['status'] == 'passed' and required <= set(browser['checkIds'])
assert browser['pendingAvatars'] == []
meta_path = R / 'docs/v13-build-manifest.json'
meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
meta.update(json.loads((R / 'dist/web-build.json').read_text()))
assert browser['html_sha256'] == meta['offline_html_sha256']
assert hashlib.sha256((W / 'world-another-me.html').read_bytes()).hexdigest() == meta['offline_html_sha256']
people = [p for p in D['characters'] if p.get('enabled') is not False]
cards = [a for arr in D['augments'].values() for a in arr if a.get('enabled') is not False]
pending = [p['personId'] for p in people if not A['portraits'].get(p['personId']) or A['portraits'][p['personId']].get('pending')]
assert not pending, pending
assert all(sources.get(p['personId'], {}).get('verifiedReference') is True for p in people)
face_caveats = [{'personId': p['personId'], 'name': p['name'], 'sourceNote': sources[p['personId']].get('note', ''), 'meaning': '已核对公开账号头像来源；不宣称真实面孔已独立核验。'} for p in people if sources[p['personId']].get('faceVerified') is False]
counts = {t: {'people': sum(p['theme'] == t for p in people), 'questions': sum(q.get('enabled') is not False and q['theme'] == t for q in D['questions']), 'cards': sum(a.get('enabled') is not False for a in D['augments'][t])} for t in ['lol', 'basket', 'abstract']}
meta.update(version=13, edition=D.get('edition', '镜面平行宇宙版'), schemaVersion=D['version'], enabledPeople=len(people), verifiedAvatars=len(people), pendingAvatars=[], activeQuestions=sum(c['questions'] for c in counts.values()), cards=len(cards), exclusiveCards=sum(bool(a.get('exclusive')) for a in cards), byTheme=counts, webURL='https://yangcrazy1.github.io/Basketball/v13/', browserGroups=browser['count'], browserDevice=browser['viewport'], nativeAcceptance='pending: 创服平台模拟器、Android 真机扫码、iOS 真机扫码')
meta.update(verifiedAvatarSources=len(people), avatarVerificationMeaning='verifiedAvatarSources（旧字段 verifiedAvatars 同义）表示漫画头像均有已核对的公开原型来源与非占位绘图；不表示每张来源照片的真实面孔均已独立核验，也不表示取得商业授权。', faceVerificationCaveats=face_caveats)
meta['appName'] = D['name']
meta.setdefault('artifacts', {})
release = R / 'release'
release.mkdir(exist_ok=True)
shutil.copy2(R / 'dist/world-another-me.html', release / 'world-another-me-v13.html')
downloads = W / 'downloads'
downloads.mkdir(exist_ok=True)
web_zip = release / 'world-another-me-v13-web.zip'
with zipfile.ZipFile(web_zip, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for p in sorted(W.rglob('*')):
        if p.is_file() and p.relative_to(W).parts[0] not in ('downloads', 'screenshots') and p.name not in ('review.html', 'build-info.json'):
            z.write(p, p.relative_to(W).as_posix())
with zipfile.ZipFile(web_zip) as z:
    assert 'index.html' in z.namelist() and 'world-another-me.html' in z.namelist()
    assert all(n in z.namelist() for n in meta['core_files'])
xhs_zip = release / 'world-another-me-v13-xhs.zip'
assert xhs_zip.stat().st_size <= 10 * 1024 ** 2
with zipfile.ZipFile(xhs_zip) as z:
    assert 'index.html' in z.namelist()
    assert not any(n.startswith(('.git/', 'node_modules/')) or n.endswith(('.map', '.DS_Store')) for n in z.namelist())
    meta['xhsFiles'] = len(z.namelist())
for name in ['world-another-me-v13.html', 'world-another-me-v13-web.zip', 'world-another-me-v13-xhs.zip']:
    p = release / name
    meta['artifacts'][name] = {'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
    if name.endswith('.zip'):
        shutil.copy2(p, downloads / name)

# New artwork may live in versioned files; follow branding-metadata.json when supplied.
branding_meta = R / 'assets/branding/branding-v13.json'
branding_files = json.loads(branding_meta.read_text()) if branding_meta.exists() else {}
old_png = {'logo': '2a593dde04ef0fb3d3bc368459609378c743cd2617515f378a11df9209cb68dc', 'cover': '812b9bd2982eb4d826e922089442e922560a0912920a959366b10ebf66534a20'}
for name in ['logo', 'cover']:
    configured = branding_files.get(name)
    if isinstance(configured, dict):
        configured = configured.get('png') or configured.get('asset')
    candidates = [R / 'assets' / configured] if isinstance(configured, str) else []
    candidates += [R / 'assets/branding' / (name + '-v13.png'), R / 'assets/branding' / (name + '.png')]
    source = next(p for p in candidates if p.is_file())
    source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
    assert source_sha != old_png[name], name + ' download would still deliver the old V12 PNG; point branding-v13.json at the new original'
    shutil.copy2(source, downloads / (name + source.suffix))
    meta[name + 'Download'] = './downloads/' + name + source.suffix
    meta[name + 'DownloadSHA256'] = source_sha

screens = W / 'screenshots'
screens.mkdir(exist_ok=True)
screen_names = ['intro-1.png', 'intro-2.png', 'intro-3.png', 'release-home.png', 'release-home-cream.png', 'release-person-detail.png', 'release-card-detail.png', 'release-collector.png', 'release-question.png', 'release-new-basket.png', 'release-new-abstract.png', 'release-reveal-lol.png', 'release-reveal-basket.png', 'release-reveal-abstract.png', 'release-result-lol.png', 'release-result-basket.png', 'release-result-abstract.png', 'release-team.png', 'team-poster.png', 'standalone-team-poster.png']
for name in screen_names:
    shutil.copy2(R / 'dist/qa/v13' / name, screens / name)
meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')

def pic(name, alt):
    return '<a href="./screenshots/' + name + '"><img loading="lazy" src="./screenshots/' + name + '" alt="' + html.escape(alt, quote=True) + '"></a>'

engine_tests = str(meta['engineAndStorageTests']) + ' 项逻辑／存储测试、' if isinstance(meta.get('engineAndStorageTests'), int) else ''
xhs_mib = meta['artifacts']['world-another-me-v13-xhs.zip']['bytes'] / 1024 ** 2
offline_mib = meta['offline_html_bytes'] / 1024 ** 2
snapshot = ' · '.join(f'{c["people"]} 人' for c in counts.values())
page = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>平行宇宙的另一个我 · 镜面平行宇宙版下载</title><style>
*{box-sizing:border-box}body{margin:0;background:#121321;color:#f7eedf;font:16px -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;line-height:1.8}main{max-width:940px;margin:auto;padding:30px 20px 70px}h1{font-size:34px;line-height:1.4}h2{font-size:24px;line-height:1.5}small{color:#b8accb}a{color:#d5bcff}progress{display:block;width:100%;height:9px;accent-color:#b99bff;margin:24px 0}article{border:1px solid #574a6e;background:linear-gradient(145deg,#282039,#181a2c);border-radius:22px;padding:24px;margin:26px 0}.button{display:inline-flex;align-items:center;min-height:48px;text-decoration:none;border:1px solid #ad91dd;border-radius:12px;padding:10px 17px;margin:7px 7px 7px 0;background:#c6b0ed;color:#211932;font-weight:700}.secondary{background:transparent;color:#e1cef9}.gallery{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}.gallery a{min-width:0}.gallery img{width:100%;border-radius:10px;border:1px solid #574a6e}.phone{display:block;width:393px;max-width:100%;margin:20px auto;border-radius:12px}.note{color:#c1b4cb;font-size:13px}li{margin:9px 0}summary{min-height:44px;cursor:pointer}code{overflow-wrap:anywhere;font-size:12px}@media(max-width:540px){article{padding:20px 16px}.gallery{grid-template-columns:1fr}.gallery img{max-width:393px;display:block;margin:auto}h1{font-size:29px}}
</style><main><small>平行宇宙的另一个我 / V13 镜面平行宇宙</small><h1>镜子另一边，<br>这个宇宙由你来接梗。</h1><progress value="100" max="100" aria-label="网页开发与本轮浏览器检查完成"></progress><p>__PEOPLE__ 位漫画人物 · __QUESTIONS__ 道情境题 · __CARDS__ 张恶搞海克斯<br>英雄联盟／篮球梦之队／抽象热梗：__SNAPSHOT__</p><a class="button" href="./">手机直接打开玩 ↗</a><a class="button secondary" href="./world-another-me.html" download="平行宇宙的另一个我-V13-离线版.html">下载完整离线 HTML ↓</a>
<article><h2>这次换了什么？</h2><ul><li>恢复收集者规则：当你四个队友都出了收集者，你的商店里只有收集者；保留五把真实装备图标。</li><li>篮球新增吴悠、西热力江、麦迪、奥尼尔、东契奇、亚历山大、罗德曼、张伯伦，并有各自专属海克斯与情境题。</li><li>抽象宇宙加入雨姐、马斯克、川普、任正非、余承东、黄仁勋等人物。人物标签与剧情为架空娱乐创作。</li><li>热门人物有更高出场优先级，仍由真实答题决定候选范围；原始匹配分和作答证据继续展示。</li><li>三幕开场漫画、简约 Logo、镜面双宇宙封面重新创作；两套配色、故事折叠重看、五人自选与随机队名海报继续保留。</li></ul></article>
<article><h2>三页讲清这场穿越</h2><div class="gallery">__INTRO__</div><p class="note">下方是本次产物实际运行的 393×852 Chromium 手机视口截图，不是实体手机拍摄。</p></article>
<article><h2>揭晓时，另一个你站到画面中央。</h2><div class="gallery">__REVEAL__</div><p class="note">三个宇宙各有镜门背景，匹配人物以大头像揭晓；污渍保留专属冠军漫画结局。</p></article>
<article><h2>收集者与新朋友</h2><div class="gallery">__DETAILS__</div><p class="note">__AVATAR_CAVEATS__</p></article>
<article><h2>五人合照，队名继续离谱。</h2><a href="./screenshots/team-poster.png"><img class="phone" loading="lazy" src="./screenshots/team-poster.png" alt="实际导出的五人战队PNG海报"></a><a class="button secondary" href="./screenshots/team-poster.png" download="我的平行宇宙五人团.png">下载示例合照 ↓</a></article>
<article><h2>单独下载</h2><a class="button secondary" href="__LOGO__" download>简约 Logo ↓</a><a class="button secondary" href="__COVER__" download>镜面平行宇宙封面 ↓</a><a class="button secondary" href="./downloads/world-another-me-v13-web.zip" download>网页部署 ZIP ↓</a><a class="button secondary" href="./downloads/world-another-me-v13-xhs.zip" download>小红书待上传 ZIP ↓</a><p class="note">完整离线 HTML 约 __OFFLINE__ MiB，图片和题库均在文件内；手机直接体验请点顶部“打开玩”。网页部署 ZIP 解压后可静态托管。小红书 ZIP 约 __XHS__ MiB，供创服平台上传。</p></article>
<details><summary>校验摘要与待验证项目</summary><p>__TESTS____BROWSER__ 组实际浏览器检查通过，覆盖三主题 × 8／16／24 题、全名单与新人物搜索、收集者文案、热门匹配边界、两套配色、三页故事重看、五人自选、队名保存、实际 PNG／HTML 下载与离线运行。旧 schema 10／11 档案用冻结引擎重放，身份、阵容和已保存队名保留。</p><p>网页宽度检查：320／360／393／430／1280px。小红书 ZIP 根目录为 index.html，全部运行资源随包提供，低于 10 MiB 硬上限；若超过 2 MiB 建议值，仍需在目标设备观察加载与内存表现。</p><p>待用户验证：创服平台模拟器完整功能 → Android 真机扫码 → iOS 真机扫码，三者使用同一 ZIP。Chrome 61 CSS 与实际设备性能尚未实测；浏览器与 SDK 模拟不能替代小红书容器验收。</p><p>人物与剧情为本作架空娱乐创作。公开照片用于漫画原型核对，不代表已获得照片商用许可或本人背书。</p><p>离线 HTML SHA-256：<code>__SHA__</code></p></details></main></html>'''
avatar_caveats = '全部漫画头像均有已核对的公开原型来源；来源核对不等于真实面孔的独立核验。' + ('其中 ' + '、'.join(c['name'] for c in face_caveats) + ' 按公开账号头像绘制，保留来源中可见的姿态与特征，不宣称已独立核验完整面容。' if face_caveats else '')
values = {'__PEOPLE__': str(len(people)), '__QUESTIONS__': str(meta['activeQuestions']), '__CARDS__': str(len(cards)), '__SNAPSHOT__': snapshot, '__AVATAR_CAVEATS__': html.escape(avatar_caveats), '__INTRO__': ''.join(pic(f'intro-{i}.png', f'穿越故事第{i}幕') for i in [1, 2, 3]), '__REVEAL__': ''.join(pic('release-reveal-' + t + '.png', a) for t, a in [('lol', '英雄联盟身份大头像揭晓'), ('basket', '篮球梦之队身份大头像揭晓'), ('abstract', '抽象宇宙身份大头像揭晓')]), '__DETAILS__': ''.join(pic(n, a) for n, a in [('release-collector.png', '恢复后的收集者卡'), ('release-new-basket.png', '新增篮球人物'), ('release-new-abstract.png', '新增抽象人物')]), '__LOGO__': meta['logoDownload'], '__COVER__': meta['coverDownload'], '__OFFLINE__': f'{offline_mib:.1f}', '__XHS__': f'{xhs_mib:.2f}', '__TESTS__': engine_tests, '__BROWSER__': str(browser['count']), '__SHA__': meta['offline_html_sha256']}
for key, value in values.items():
    page = page.replace(key, value)
(R / 'docs/v13-review.html').write_text(page)
(W / 'review.html').write_text(page)
print(json.dumps({'review': str(W / 'review.html'), 'people': len(people), 'cards': len(cards), 'artifacts': meta['artifacts']}, ensure_ascii=False, indent=2))
