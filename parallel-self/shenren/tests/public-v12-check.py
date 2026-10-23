"""Exercise the exact published /v12/ release and its downloads in Chromium."""
from pathlib import Path
from urllib.request import urlopen
from playwright.sync_api import sync_playwright
from PIL import Image
import json, hashlib, datetime

R = Path(__file__).resolve().parents[1]
base = 'https://yangcrazy1.github.io/Basketball/v12/'
checks, errors, failed = [], [], []
def passed(label):
    checks.append(label)
    print('PASS', label, flush=True)
def digest(body):
    return hashlib.sha256(body).hexdigest()
meta = json.loads(urlopen(base + 'build-info.json', timeout=30).read())
local = json.loads((R / 'docs/v12-build-manifest.json').read_text())
assert meta['version'] == 12 and meta['verifiedAvatars'] == 40 and meta['pendingAvatars'] == []
assert meta['offline_html_sha256'] == local['offline_html_sha256']
with urlopen(base + 'index.html', timeout=30) as r:
    assert r.status == 200 and digest(r.read()) == meta['entry_sha256']
for filename, expected in [('world-another-me.html', meta['offline_html_sha256'])] + [('downloads/' + n, a['sha256']) for n, a in meta['artifacts'].items() if n.endswith('.zip')]:
    with urlopen(base + filename, timeout=60) as r:
        assert r.status == 200 and digest(r.read()) == expected, filename
for filename in ['review.html', 'downloads/logo.png', 'downloads/cover.png', 'screenshots/team-poster.png', 'screenshots/intro-1.png']:
    with urlopen(base + filename, timeout=30) as r:
        assert r.status == 200 and len(r.read()) > 500, filename
passed('published entry, full offline HTML, web/XHS ZIP SHA-256 hashes, review, cover, logo and screenshots resolve')
with sync_playwright() as w:
    b = w.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
    ctx = b.new_context(viewport={'width': 393, 'height': 852}, accept_downloads=True, reduced_motion='reduce')
    p = ctx.new_page()
    p.on('pageerror', lambda e: errors.append(str(e)))
    p.on('response', lambda r: failed.append([r.status, r.url]) if r.status >= 400 else None)
    p.goto(base, wait_until='networkidle', timeout=60000)
    p.wait_for_selector('.intro-page')
    for i in [1, 2, 3]:
        assert f'0{i}' in p.locator('.intro-top').inner_text()
        p.locator('[data-action=intro-next]').click()
    assert p.locator('.v12-home').count() == 1
    assert p.locator('.journey-fold[open]').count() == 0
    assert p.evaluate('ShenrenEngine.enabledPeople(WORLD_DATA).length') == 40
    p.locator('header [data-action=intro]').click()
    assert '01' in p.locator('.intro-top').inner_text()
    p.locator('[data-action=intro-skip]').click()
    p.locator('[data-action=gallery]').click()
    p.locator('[data-action=library-filter][data-theme=all]').click()
    assert p.locator('.library-person').count() == 40
    assert p.locator('.pending-portrait').count() == 0
    p.locator('[data-search=library]').fill('杨毅')
    p.wait_for_timeout(300)
    p.locator('.library-person').click()
    assert p.locator('.universe-timeline article').count() == 4
    assert p.locator('.person-perks button').count() == 3
    p.locator('#close-dialog').click()
    passed('real HTTPS three-page story/replay, collapsed home story, all 40 portraits and Yang Yi detail work')
    for theme in ['lol', 'basket', 'abstract']:
        p.locator('.brand').click()
        p.locator('[data-action=theme][data-theme=' + theme + ']').click()
        p.locator('[data-action=mode][data-count="8"]').click()
        p.locator('#app [data-action=start]').click()
        for i in range(8):
            old = p.locator('.option').first.get_attribute('data-question')
            p.locator('.option').nth(i % 4).click()
            p.wait_for_function("id=>!document.querySelector('.option[data-question=\"'+id+'\"]')", arg=old)
        p.wait_for_selector('.reveal-page')
        p.locator('[data-action=reveal-open]').click()
        assert p.locator('.team-card').count() == 5
        assert p.locator('.universe-timeline article').count() == 4
        before = p.locator('[data-squad-name]').inner_text()
        ids = p.locator('.team-card').evaluate_all('xs=>xs.map(x=>x.dataset.person)')
        p.locator('[data-action=team-name]').first.click()
        assert p.locator('[data-squad-name]').inner_text() != before
        assert ids == p.locator('.team-card').evaluate_all('xs=>xs.map(x=>x.dataset.person)')
        assert p.evaluate('document.documentElement.scrollWidth<=innerWidth')
        passed('published ' + theme + ' quiz, reveal, rich dossier, five-person squad and independent name reroll')
    p.locator('[data-action=team-poster]').first.click()
    p.wait_for_selector('.squad-poster')
    with p.expect_download() as dl:
        p.locator('.download-png').click()
    assert Image.open(dl.value.path()).size == (1080, 1920)
    p.locator('#close-dialog').click()
    with p.expect_download() as dl:
        p.locator('footer [data-action=download-html]').click()
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
    assert Image.open(dl.value.path()).size == (1080, 1920)
    passed('real public PNG downloads for result/standalone squads and exact current offline HTML download')
    assert not errors, errors
    assert not failed, failed
    b.close()
passed('no public page exceptions or failed HTTP resource requests')
report = dict(status='passed', checks=checks, count=len(checks), url=base, sourceCommit=meta['source_commit'], deploymentArtifactSHA256=meta['offline_html_sha256'], checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(), device='393×852 Chromium mobile viewport; not physical phone or XHS platform acceptance')
(R / 'docs/public-v12.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
