"""Verify the exact published NBA release and real HTTPS download/quiz flows."""
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright
from PIL import Image
import datetime
import hashlib
import io
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://yangcrazy1.github.io/Basketball/nba/'
checks, errors, failed = [], [], []


def read(url):
    with urlopen(url, timeout=40) as response:
        assert response.status == 200
        return response.read()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def passed(label):
    checks.append(label)
    print('PASS', label, flush=True)


deployment = json.loads((ROOT / 'docs/deployment.json').read_text())
meta = json.loads(read(BASE + 'build-info.json?source=' + deployment['sourceCommit']))
assert meta['sourceCommit'] == deployment['sourceCommit']
assert meta['name'] == '整活NBA' and (meta['people'], meta['questions'], meta['cards']) == (21, 132, 51)
for name, digest in meta['runtimeFiles'].items():
    assert sha(read(BASE + name)) == digest, name
for name, info in meta['artifacts'].items():
    raw = read(BASE + 'downloads/' + name + '?v=' + info['sha256'][:12])
    assert len(raw) == info['bytes'] and sha(raw) == info['sha256'], name
    if name.endswith('-wechat.zip'):
        z = zipfile.ZipFile(io.BytesIO(raw))
        app = json.loads(z.read('miniprogram/app.json'))
        assert len(app['pages']) == 6
        assert sum(i.file_size for i in z.infolist() if i.filename.startswith('miniprogram/')) < 2 * 1024 ** 2
        assert not any(b'<web-view' in z.read(n) for n in z.namelist() if n.endswith('.wxml'))
download_page = read(BASE + 'download.html?source=' + deployment['sourceCommit'])
assert b'zhenghuo-nba-wechat.zip' in download_page
assert meta['artifacts']['zhenghuo-nba-wechat.zip']['sha256'][:12].encode() in download_page
passed('exact HTTPS runtime and all four downloadable artifact hashes, including a real six-page native WeChat project')

for name in ['logo', 'cover']:
    if name + 'Download' in meta:
        raw = read(urljoin(BASE, meta[name + 'Download']))
        assert sha(raw) == meta[name + 'SHA256']
        image = Image.open(io.BytesIO(raw))
        if name == 'logo':
            assert image.mode == 'RGBA' and image.getchannel('A').getextrema()[0] < 255
        else:
            assert abs(image.width / image.height - .75) < .015
passed('separate original brand artwork downloads match final source images')
original = read('https://yangcrazy1.github.io/Basketball/v13/downloads/world-another-me-v13-xhs.zip')
assert sha(original) == '54929e09e98f85c7c16ed167676cca817e928243084c882edd6613ff1dd648a9'
passed('original V13 XHS download remains accessible with its unchanged historical hash')

with sync_playwright() as w:
    browser = w.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
    context = browser.new_context(viewport={'width': 393, 'height': 852}, accept_downloads=True)
    p = context.new_page()
    p.on('pageerror', lambda e: errors.append(str(e)))
    p.on('response', lambda r: failed.append([r.status, r.url]) if r.status >= 400 else None)
    p.goto(BASE + '?source=' + deployment['sourceCommit'], wait_until='networkidle')
    p.wait_for_selector('.home-page')
    assert p.locator('.brand strong').inner_text() == '整活NBA'
    p.locator('[data-count="8"]').click()
    p.locator('#app [data-action=start]').first.click()
    p.wait_for_selector('.question-card')
    for _ in range(8):
        option = p.locator('.option').first
        qid = option.get_attribute('data-question')
        option.click()
        p.wait_for_function('id=>!document.querySelector(".option[data-question=\\\""+id+"\\\"]")', arg=qid)
    p.wait_for_selector('.result-page')
    record = p.evaluate('NBAPlatform.read("history")[0]')
    actual = p.evaluate('r=>NBAGame.result(r.session).identity.personId', record)
    assert p.locator('.result-page').get_attribute('data-result-person') == actual
    assert p.locator('.team-card').count() == 5
    assert p.evaluate('document.documentElement.scrollWidth<=innerWidth')
    passed('real public eight-question quiz automatically reveals its actual matched identity, card and five-person team')

    p.goto(BASE + '#diy', wait_until='networkidle')
    p.locator('#diy-form input[name=name]').fill('篮筐体检主任')
    p.locator('#diy-form button[type=submit]').click()
    p.goto(BASE + '#result/' + record['id'], wait_until='networkidle')
    p.locator('[data-action=toggle-diy]').click()
    assert p.locator('.team-card[data-person=diy-me]').count() == 1
    assert p.locator('.result-page').get_attribute('data-result-person') == actual
    p.locator('[data-action=team-poster]').click()
    p.wait_for_selector('.poster-image')
    with p.expect_download() as download:
        p.locator('[data-action=save-poster]').click()
    assert Image.open(download.value.path()).size == (1080, 1920)
    p.reload(wait_until='networkidle')
    assert p.locator('.team-card[data-person=diy-me]').count() == 1
    assert p.locator('.result-page').get_attribute('data-result-person') == actual
    passed('live DIY teammate, original match preservation, real PNG export and persisted team reload')
    assert not errors, errors
    assert not failed, failed
    browser.close()
passed('no public page exceptions or failed runtime resource responses')
report = {'status': 'passed', 'count': len(checks), 'checks': checks, 'url': BASE,
          'sourceCommit': meta['sourceCommit'], 'checkedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'device': 'Chromium 393×852 mobile viewport simulation; not physical phone or native platform acceptance'}
(ROOT / 'docs/public-check.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
