"""Verify the exact /v14/ deployment and real HTTPS quiz/download flows."""
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright
from PIL import Image
import datetime, hashlib, json, re

R = Path(__file__).resolve().parents[1]
base = 'https://yangcrazy1.github.io/Basketball/v14/'
checks, errors, failed = [], [], []

def passed(label):
    checks.append(label)
    print('PASS', label, flush=True)

def digest(body):
    return hashlib.sha256(body).hexdigest()

meta = json.loads(urlopen(base + 'build-info.json', timeout=30).read())
local = json.loads((R / 'docs/v14-build-manifest.json').read_text())
assert meta['version'] == 14 and meta['schemaVersion'] == 13
assert meta['verifiedAvatars'] == meta['enabledPeople'] and meta['pendingAvatars'] == []
assert meta['verifiedAvatarSources'] == meta['enabledPeople']
assert {'nida', 'yili'} <= {c['personId'] for c in meta['faceVerificationCaveats']}
assert meta['faceVerificationCaveats'] == local['faceVerificationCaveats']
assert (meta['enabledPeople'], meta['representativeCards'], meta['representativeAssociations']) == (58, 137, 143)
assert meta['historicalSchemas'] == [10, 11, 12]
assert meta['disabledReviewCandidates'] == 26
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
for name in ['logo', 'cover', 'introRealLife', 'introMirror', 'introNewWorld']:
    with urlopen(urljoin(base, meta[name + 'Download']), timeout=30) as r:
        assert digest(r.read()) == meta[name + 'DownloadSHA256'], name
passed('published entry, complete HTML, both ZIP hashes, review page, separate logo/cover and actual screenshots resolve')

def answer(page, count):
    for i in range(count):
        old = page.locator('.option').first.get_attribute('data-question')
        page.locator('.option').nth(i % 4).click()
        page.wait_for_function("id=>!document.querySelector('.option[data-question=\"'+id+'\"]')", arg=old)

def story_facts(page):
    value = page.evaluate('''()=>{const s=JSON.parse(localStorage.getItem('world-otherme.v10.story.v14'));return ShenrenEngine.storyView(s,WORLD_DATA);}''')
    assert sorted(page.locator('.v14-story [data-owned-card]').evaluate_all('xs=>xs.map(x=>x.dataset.ownedCard)')) == sorted(value['ownedCardIds'])
    assert set(page.locator('.v14-story [data-trigger-card]').evaluate_all('xs=>xs.map(x=>x.dataset.triggerCard)')) <= set(value['ownedCardIds'])
    return value

def finish_story(page, route=0):
    for _ in range(12):
        value = story_facts(page)
        if value['isEnding']:
            return value
        page.wait_for_timeout(250)
        choices = page.locator('.v14-story .story-choice')
        if choices.count():
            choices.nth(min(route, choices.count()-1)).click()
        else:
            page.locator('[data-action=story-next]').click()
        page.wait_for_function('id=>document.querySelector(".v14-story").dataset.storyNode!==id', arg=value['node'])
    raise AssertionError('public story did not reach an ending')

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
        assert f'{i}/3' in p.locator('.intro-top').inner_text()
        key = ['introRealLife', 'introMirror', 'introNewWorld'][i-1]
        assert p.locator('.intro-figure img').get_attribute('src') == p.evaluate('key=>WORLD_BRANDING[key]', key)
        p.locator('.intro-figure img').evaluate('img=>img.decode()')
        p.locator('[data-action=intro-next]').click()
    assert p.locator('.home').count() == 1
    assert p.locator('.journey-fold[open]').count() == 0
    assert p.evaluate('WORLD_DATA.version') == 13
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
    assert '1/3' in p.locator('.intro-top').inner_text()
    p.locator('[data-action=intro-skip]').click()
    p.locator('[data-action=card-gallery]').first.click()
    p.locator('[data-action=library-filter][data-theme=all]').click()
    p.locator('.library-card[data-id=collector-union]').click()
    text = p.locator('#dialog-body').inner_text()
    assert re.search(r'四[个名位]?队友.*收集者', text, re.S)
    assert re.search(r'商店.{0,8}只有收集者', text)
    assert p.locator('#dialog .perk-art[data-copies="5"]').count() == 1
    p.locator('#close-dialog').click()
    passed('real HTTPS three-page story/replay and the restored Collector-only shop card with five real icon copies')

    p.locator('[data-action=gallery]').first.click()
    p.locator('[data-action=library-filter][data-theme=all]').click()
    assert p.locator('.library-person').count() == meta['enabledPeople']
    assert p.locator('#dialog .pending-portrait').count() == 0
    for theme, name in [('basket', '格林'), ('basket', '恶鼠'), ('abstract', '带篮子')]:
        p.locator('[data-action=library-filter][data-theme=' + theme + ']').click()
        p.locator('[data-search=library]').fill(name)
        p.wait_for_timeout(300)
        assert p.locator('.library-person').count() >= 1
        p.locator('.library-person').first.click()
        assert p.locator('#dialog .person-perks button').count() >= 2
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

    for pid in ['draymond-green', 'ershu']:
        p.goto(base + '?story=' + pid, wait_until='networkidle')
        p.wait_for_selector('.v14-story[data-story-person="' + pid + '"]')
        assert story_facts(p)['ownedCardIds'] == []
        assert p.locator('.story-top').bounding_box()['y'] >= 0
        if pid == 'draymond-green':
            entry = story_facts(p)['node']
            p.locator('[data-action=story-next]').click()
            p.wait_for_function('id=>document.querySelector(".v14-story").dataset.storyNode!==id', arg=entry)
            p.wait_for_timeout(250)
            choice_node = story_facts(p)['node']
            p.locator('.story-choice').first.click()
            p.wait_for_function('id=>document.querySelector(".v14-story").dataset.storyNode!==id', arg=choice_node)
            before_reload = story_facts(p)
            assert before_reload['ownedCardIds']
            p.reload(wait_until='networkidle')
            p.wait_for_selector('.v14-story[data-story-person="' + pid + '"]')
            after_reload = story_facts(p)
            assert after_reload['node'] == before_reload['node']
            assert after_reload['ownedCardIds'] == before_reload['ownedCardIds']
        first = finish_story(p, 0)
        p.locator('[data-action=story-poster]').click()
        p.wait_for_selector('.story-poster')
        with p.expect_download() as dl:
            p.locator('.download-png').click()
        assert Image.open(dl.value.path()).size == (1080, 1920)
        p.locator('#close-dialog').click()
        p.locator('[data-action=story-restart]').click()
        assert story_facts(p)['ownedCardIds'] == []
        second = finish_story(p, 1)
        assert first['text'] != second['text']
    passed('public Green/Ershu direct story links start card-free, earn only explicit rewards, reach distinct endings and export real story PNGs')

    p.goto(urljoin(base, 'review.html'), wait_until='networkidle')
    p.wait_for_selector('.review-person')
    assert p.locator('.review-person').count() == 7
    for pid in ['draymond-green', 'ershu']:
        assert p.locator('a[href="./?story=' + pid + '"]').count() == 1
    p.locator('[data-review-mode=active]').click()
    assert p.locator('.review-person').count() == meta['enabledPeople']
    assert p.locator('.review-person[data-review-person=renzhengfei]').count() == 0
    p.locator('#review-search').fill('阿水')
    p.wait_for_timeout(220)
    assert p.locator('.review-person').count() == 1
    p.locator('.review-person').click()
    assert p.locator('#review-detail').is_visible()
    assert p.locator('#review-detail .review-card').count() >= 2
    assert p.locator('#review-detail .story-choice').count() >= 4
    assert p.locator('#review-detail .story-node').count() >= 6
    p.locator('[data-review-back]').first.click()
    assert p.locator('#review-search').input_value() == '阿水'
    p.locator('#review-search').fill('')
    p.wait_for_timeout(220)
    p.locator('#review-theme').select_option('basket')
    assert p.locator('.review-person').count() == meta['byTheme']['basket']['people']
    p.locator('#review-theme').select_option('all')
    p.locator('[data-review-mode=disabled]').click()
    candidates = p.evaluate('WORLD_DATA.reviewCatalog.candidates')
    assert len(candidates) == len({c['id'] for c in candidates}) == 26
    assert all(c['enabled'] is False and c['reason'] for c in candidates)
    candidate_owners = sorted({owner for c in candidates for owner in c['owners']})
    assert p.locator('.review-person').count() == len(candidate_owners)
    seen_candidates = set()
    for owner in candidate_owners:
        p.locator('.review-person[data-review-person="' + owner + '"]').click()
        expected = [c for c in candidates if owner in c['owners']]
        assert p.locator('#review-detail .review-card').count() == len(expected)
        for c in expected:
            item = p.locator('#review-detail [data-card="' + c['id'] + '"]')
            assert c['name'] in item.locator('h3').inner_text()
            assert c['reason'] in item.inner_text()
            assert '不进入随机池、结果、故事奖励和默认标签' in item.inner_text()
            assert item.locator('.card-art').count() == 0
            seen_candidates.add(c['id'])
        p.locator('[data-review-back]').first.click()
    assert seen_candidates == {c['id'] for c in candidates}
    p.locator('[data-review-mode=pending]').click()
    assert p.locator('#review-count').inner_text()
    p.locator('[data-review-mode=common]').click()
    common_ids = p.evaluate('''()=>[].concat(...Object.values(WORLD_DATA.augments)).filter(a=>a.enabled!==false&&(a.owners||a.signatureFor||(a.owner?[a.owner]:[])).length===0).map(a=>a.id)''')
    assert len(common_ids) == 37
    assert p.locator('#review-grid .review-card').count() == len(common_ids)
    assert sorted(p.locator('#review-grid .review-card').evaluate_all('xs=>xs.map(x=>x.dataset.card)')) == sorted(common_ids)
    assert p.evaluate('document.documentElement.scrollWidth<=innerWidth')
    passed('live-data review defaults to five samples plus Green/Ershu, shows all 58, preserves alias search and exposes real cards/branches/filters')
    assert not errors, errors
    assert not failed, failed
    browser.close()
passed('no public page exceptions or failed HTTP runtime resource requests')
report = {'status': 'passed', 'checks': checks, 'count': len(checks), 'url': base, 'sourceCommit': meta['source_commit'], 'deploymentArtifactSHA256': meta['offline_html_sha256'], 'checkedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'enabledPeople': meta['enabledPeople'], 'revealBackgroundSHA256': reveal_hashes, 'device': '393×852 Chromium mobile viewport; not physical phone or XHS platform acceptance'}
(R / 'docs/public-v14.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
