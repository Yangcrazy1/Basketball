"""Verify the exact /v13/ deployment and real HTTPS quiz/download flows."""
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright
from PIL import Image
import datetime, hashlib, json, re

R = Path(__file__).resolve().parents[1]
base = 'https://yangcrazy1.github.io/Basketball/v13/'
checks, errors, failed = [], [], []

def passed(label):
    checks.append(label)
    print('PASS', label, flush=True)

def digest(body):
    return hashlib.sha256(body).hexdigest()

meta = json.loads(urlopen(base + 'build-info.json', timeout=30).read())
local = json.loads((R / 'docs/v13-build-manifest.json').read_text())
assert meta['version'] == 13 and meta['schemaVersion'] == 12
assert meta['verifiedAvatars'] == meta['enabledPeople'] and meta['pendingAvatars'] == []
assert meta['verifiedAvatarSources'] == meta['enabledPeople']
assert {c['personId'] for c in meta['faceVerificationCaveats']} == {'nida', 'yili'}
assert '不表示每张来源照片的真实面孔均已独立核验' in meta['avatarVerificationMeaning']
assert meta['offline_html_sha256'] == local['offline_html_sha256']
with urlopen(base + 'index.html', timeout=30) as r:
    assert r.status == 200 and digest(r.read()) == meta['entry_sha256']
for filename, expected in [('world-another-me.html', meta['offline_html_sha256'])] + [('downloads/' + name, info['sha256']) for name, info in meta['artifacts'].items() if name.endswith('.zip')]:
    with urlopen(base + filename, timeout=60) as r:
        assert r.status == 200 and digest(r.read()) == expected, filename
for filename in ['review.html', meta['logoDownload'], meta['coverDownload'], 'screenshots/team-poster.png', 'screenshots/intro-1.png', 'screenshots/release-collector.png'] + ['screenshots/release-reveal-' + theme + '.png' for theme in ['lol', 'basket', 'abstract']]:
    with urlopen(urljoin(base, filename), timeout=30) as r:
        assert r.status == 200 and len(r.read()) > 500, filename
for name in ['logo', 'cover']:
    with urlopen(urljoin(base, meta[name + 'Download']), timeout=30) as r:
        assert digest(r.read()) == meta[name + 'DownloadSHA256'], name
passed('published entry, complete HTML, both ZIP hashes, review page, separate logo/cover and actual screenshots resolve')

def answer(page, count):
    for i in range(count):
        old = page.locator('.option').first.get_attribute('data-question')
        page.locator('.option').nth(i % 4).click()
        page.wait_for_function("id=>!document.querySelector('.option[data-question=\"'+id+'\"]')", arg=old)

with sync_playwright() as w:
    browser = w.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
    ctx = browser.new_context(viewport={'width': 393, 'height': 852}, accept_downloads=True, reduced_motion='reduce')
    p = ctx.new_page()
    p.on('pageerror', lambda e: errors.append(str(e)))
    p.on('response', lambda r: failed.append([r.status, r.url]) if r.status >= 400 else None)
    p.goto(base, wait_until='networkidle', timeout=60000)
    p.wait_for_selector('.intro-page')
    assert p.locator('.brand strong').inner_text() == '平行宇宙的另一个我'
    for i in [1, 2, 3]:
        assert f'0{i}' in p.locator('.intro-top').inner_text()
        p.locator('[data-action=intro-next]').click()
    assert p.locator('.home').count() == 1
    assert p.locator('.journey-fold[open]').count() == 0
    assert p.evaluate('WORLD_DATA.version') == 12
    assert p.evaluate('ShenrenEngine.enabledPeople(WORLD_DATA).length') == meta['enabledPeople']
    reveal_hashes = {}
    for theme, key in [('lol', 'revealLol'), ('basket', 'revealBasket'), ('abstract', 'revealAbstract')]:
        asset = p.evaluate('key=>WORLD_BRANDING[key]', key)
        with urlopen(urljoin(base, asset), timeout=30) as r:
            body = r.read()
            assert r.status == 200 and len(body) > 1000, key
            reveal_hashes[theme] = digest(body)
    assert len(set(reveal_hashes.values())) == 3
    p.locator('header [data-action=intro]').click()
    assert '01' in p.locator('.intro-top').inner_text()
    p.locator('[data-action=intro-skip]').click()
    p.locator('[data-action=sample][data-behavior=collector]').click()
    text = p.locator('#dialog-body').inner_text()
    assert re.search(r'四[个名位]?队友.*收集者', text, re.S)
    assert re.search(r'商店.{0,8}只有收集者', text)
    assert p.locator('#dialog .perk-art[data-copies="5"]').count() == 1
    p.locator('#close-dialog').click()
    passed('real HTTPS three-page story/replay and the restored Collector-only shop card with five real icon copies')

    p.locator('[data-action=gallery]').click()
    p.locator('[data-action=library-filter][data-theme=all]').click()
    assert p.locator('.library-person').count() == meta['enabledPeople']
    assert p.locator('#dialog .pending-portrait').count() == 0
    for theme, name in [('basket', '东契奇'), ('abstract', '川普')]:
        p.locator('[data-action=library-filter][data-theme=' + theme + ']').click()
        p.locator('[data-search=library]').fill(name)
        p.wait_for_timeout(300)
        assert p.locator('.library-person').count() >= 1
        p.locator('.library-person').first.click()
        assert p.locator('#dialog .universe-timeline article').count() == 4
        assert p.locator('#dialog .person-perks button').count() == 3
        p.locator('[data-action=library-back]').click()
        p.locator('[data-search=library]').fill('')
        p.wait_for_timeout(300)
    p.locator('#close-dialog').click()
    passed('expanded public catalog has all verified portraits; basketball/abstract new characters expose settings and three cards')

    for theme in ['lol', 'basket', 'abstract']:
        p.locator('.brand').click()
        p.locator('[data-action=theme][data-theme=' + theme + ']').click()
        p.locator('[data-action=mode][data-count="8"]').click()
        p.locator('#app [data-action=start]').click()
        answer(p, 8)
        p.wait_for_selector('.reveal-page')
        scene = p.locator('#app .large-portrait-scene')
        if scene.count():
            illustration = scene.locator('.reveal-illustration')
            illustration.evaluate('img=>img.decode()')
            assert illustration.evaluate('img=>img.complete&&img.naturalWidth>0')
            key = {'lol': 'revealLol', 'basket': 'revealBasket', 'abstract': 'revealAbstract'}[theme]
            assert illustration.get_attribute('src') == p.evaluate('key=>WORLD_BRANDING[key]', key)
            assert scene.locator('.reveal-portrait .portrait svg').count() == 1
            assert scene.locator('.reveal-portrait').bounding_box()['width'] >= scene.bounding_box()['width'] * .6
        p.locator('[data-action=reveal-open]').click()
        assert p.locator('#app .identity-photo .portrait').bounding_box()['width'] >= 120
        assert p.locator('#app .team-card').count() == 5
        assert p.locator('#app .universe-timeline article').count() == 4
        before = p.locator('#app [data-squad-name]').inner_text()
        ids = p.locator('#app .team-card').evaluate_all('xs=>xs.map(x=>x.dataset.person)')
        p.locator('[data-action=team-name]').first.click()
        assert p.locator('#app [data-squad-name]').inner_text() != before
        assert ids == p.locator('#app .team-card').evaluate_all('xs=>xs.map(x=>x.dataset.person)')
        assert '原始匹配' in p.locator('#app .identity-tags').inner_text()
        assert p.evaluate('document.documentElement.scrollWidth<=innerWidth')
        passed('published ' + theme + ' quiz reveals the real-answer result, expanded setting, five-person squad and independent name reroll')

    p.locator('[data-action=team-poster]').first.click()
    p.wait_for_selector('.squad-poster')
    with p.expect_download() as dl:
        p.locator('.download-png').click()
    assert dl.value.suggested_filename.startswith('平行宇宙的另一个我'), dl.value.suggested_filename
    assert Image.open(dl.value.path()).size == (1080, 1920)
    p.locator('#close-dialog').click()
    with p.expect_download() as dl:
        p.locator('footer [data-action=download-html]').click()
    assert dl.value.suggested_filename.startswith('平行宇宙的另一个我'), dl.value.suggested_filename
    assert digest(Path(dl.value.path()).read_bytes()) == meta['offline_html_sha256']
    p.locator('.brand').click()
    p.locator('[data-action=squad-home]').first.click()
    p.locator('[data-action=squad-fill]').click()
    p.locator('[data-action=squad-save]').click()
    assert p.locator('.standalone-squad').count() == 1
    p.locator('[data-action=team-poster]').first.click()
    p.wait_for_selector('.squad-poster')
    with p.expect_download() as dl:
        p.locator('.download-png').click()
    assert dl.value.suggested_filename.startswith('平行宇宙的另一个我'), dl.value.suggested_filename
    assert Image.open(dl.value.path()).size == (1080, 1920)
    passed('real public result/self-selected five-person PNG downloads and exact current offline HTML download')
    assert not errors, errors
    assert not failed, failed
    browser.close()
passed('no public page exceptions or failed HTTP runtime resource requests')
report = {'status': 'passed', 'checks': checks, 'count': len(checks), 'url': base, 'sourceCommit': meta['source_commit'], 'deploymentArtifactSHA256': meta['offline_html_sha256'], 'checkedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'enabledPeople': meta['enabledPeople'], 'revealBackgroundSHA256': reveal_hashes, 'device': '393×852 Chromium mobile viewport; not physical phone or XHS platform acceptance'}
(R / 'docs/public-v13.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
