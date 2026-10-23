"""Actual V13 web flows. Chromium mobile emulation is not XHS/device acceptance."""
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from urllib.request import urlopen
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright
from PIL import Image
import base64, hashlib, json, re, threading

R = Path(__file__).resolve().parents[1]
OUT = R / 'dist/qa/v13'
OUT.mkdir(parents=True, exist_ok=True)
D = json.loads((R / 'src/data.json').read_text())
PEOPLE = [p for p in D['characters'] if p.get('enabled') is not False]
COUNTS = {t: sum(p['theme'] == t for p in PEOPLE) for t in ['lol', 'basket', 'abstract']}
CARDS = {t: sum(a.get('enabled') is not False for a in D['augments'][t]) for t in COUNTS}
NEW_NAMES = {'lol': ['王思聪'], 'basket': ['吴悠', '西热力江', '麦迪', '奥尼尔', '东契奇', '亚历山大', '罗德曼', '张伯伦'], 'abstract': ['雨姐', '马斯克', '川普', '任正非', '余承东', '黄仁勋', '尼达', '伊利']}
OLD_ART_SHA = {'logo': 'd2262a44084f635164c5e626d934c089d415021289cfaa641195d918f6e7704e', 'cover': '39144e33152baf4ace1643e71948fd5f881f431e0a8cccdbdc98a7c270f10ca9', 'intro': '32956a36f9b55830d859493f5f071612d979f4d7f4750eb9a24e5bf088be17d3'}
REVEAL_KEYS = {'lol': 'revealLol', 'basket': 'revealBasket', 'abstract': 'revealAbstract'}
checks, errors, requests, failures = [], [], [], []

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(R / 'dist')))
threading.Thread(target=server.serve_forever, daemon=True).start()
base = 'http://127.0.0.1:' + str(server.server_port)

def passed(key, text):
    checks.append({'id': key, 'text': text})
    print('PASS', key, text, flush=True)

def layout(page):
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), page.viewport_size

def answer(page, count):
    for i in range(count):
        qid = page.locator('.option').first.get_attribute('data-question')
        page.locator('.option').nth(i % 4).click()
        page.wait_for_function("id=>!document.querySelector('.option[data-question=\"'+id+'\"]')", arg=qid)

def png(page, selector, name):
    page.locator(selector).first.click()
    page.wait_for_selector('#dialog .download-png')
    with page.expect_download() as dl:
        page.locator('#dialog .download-png').click()
    assert dl.value.suggested_filename.startswith('平行宇宙的另一个我'), dl.value.suggested_filename
    im = Image.open(dl.value.path())
    assert im.size == (1080, 1920)
    im.save(OUT / name)
    page.locator('#close-dialog').click()

def home(page, theme=None):
    page.locator('.brand').click()
    if theme:
        page.locator('[data-action=theme][data-theme=' + theme + ']').click()

def assert_large_reveal(page, theme, expected_person=None):
    scene = page.locator('#app .large-portrait-scene')
    assert scene.count() == 1, theme
    page.wait_for_function("()=>{const i=document.querySelector('#app .large-portrait-scene .reveal-illustration');return i&&i.complete&&i.naturalWidth>0;}")
    illustration = scene.locator('.reveal-illustration')
    assert illustration.get_attribute('src') == page.evaluate('key=>WORLD_BRANDING[key]', REVEAL_KEYS[theme])
    avatar = scene.locator('.reveal-portrait')
    portrait = avatar.locator('.portrait')
    assert portrait.count() == 1 and portrait.locator('svg').count() == 1
    assert portrait.locator('.pending-portrait').count() == 0
    if expected_person:
        assert portrait.get_attribute('data-avatar') == expected_person
    for width in [320, 360, 393, 430]:
        page.set_viewport_size({'width': width, 'height': 852})
        box, face = scene.bounding_box(), avatar.bounding_box()
        assert box and face and face['width'] >= box['width'] * .60, (theme, width, box, face)
        layout(page)
    page.set_viewport_size({'width': 393, 'height': 852})

with sync_playwright() as w:
    browser = w.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
    ctx = browser.new_context(viewport={'width': 393, 'height': 852}, accept_downloads=True, reduced_motion='reduce')
    p = ctx.new_page()
    p.on('pageerror', lambda e: errors.append(str(e)))
    p.on('request', lambda r: requests.append(r.url))
    p.on('response', lambda r: failures.append([r.status, r.url]) if r.status >= 400 else None)
    p.goto(base + '/web/', wait_until='networkidle')
    p.wait_for_selector('.intro-page')
    assert p.locator('.brand strong').inner_text() == '平行宇宙的另一个我'
    for i in [1, 2, 3]:
        assert f'0{i}' in p.locator('.intro-top').inner_text()
        p.screenshot(path=str(OUT / f'intro-{i}.png'))
        p.locator('[data-action=intro-next]').click()
    assert p.locator('.journey-fold[open]').count() == 0
    assert p.evaluate('WORLD_DATA.version') == 12
    assert p.evaluate('WORLD_DATA.releaseVersion') == 13
    assert (R / 'dist/web/index.html').stat().st_size < 6000
    p.screenshot(path=str(OUT / 'release-home.png'), full_page=True)
    for width in [320, 360, 393, 430, 1280]:
        p.set_viewport_size({'width': width, 'height': 852})
        layout(p)
    passed('intro', 'three new story pages, collapsed replay, small entry and five responsive widths')

    # Verify a new generation was actually packaged, rather than merely new labels.
    branding = p.evaluate('WORLD_BRANDING')
    for name, old_sha in OLD_ART_SHA.items():
        url = branding[name]
        body = base64.b64decode(url.split(',', 1)[1]) if url.startswith('data:') else urlopen(urljoin(base + '/web/', url)).read()
        assert hashlib.sha256(body).hexdigest() != old_sha, name + ' still uses V12 art'
        assert len(body) > 1000, name
    reveal_hashes = {}
    for theme, key in REVEAL_KEYS.items():
        assert key in branding and branding[key], key
        url = branding[key]
        body = base64.b64decode(url.split(',', 1)[1]) if url.startswith('data:') else urlopen(urljoin(base + '/web/', url)).read()
        assert len(body) > 1000, key
        reveal_hashes[theme] = hashlib.sha256(body).hexdigest()
    assert len(set(reveal_hashes.values())) == 3, 'theme reveal backgrounds must contain different actual images'
    passed('new-art', 'new logo, mirrored-universe cover and opening comic are packaged as actual images')

    p.set_viewport_size({'width': 393, 'height': 852})
    p.locator('[data-action=palette]').click()
    assert p.evaluate('document.documentElement.dataset.style') == 'paper'
    p.screenshot(path=str(OUT / 'release-home-cream.png'), full_page=True)
    p.reload(wait_until='networkidle')
    p.wait_for_selector('.intro-page')
    assert p.evaluate('document.documentElement.dataset.style') == 'paper'
    p.locator('[data-action=intro-skip]').click()
    p.locator('header [data-action=intro]').click()
    assert '01' in p.locator('.intro-top').inner_text()
    p.locator('[data-action=intro-skip]').click()
    p.locator('.journey-fold summary').click()
    assert p.locator('.journey-thumb').count() == 3
    p.locator('.journey-fold summary').click()
    p.locator('[data-action=palette]').click()
    passed('replay-palette', 'opening can be replayed every visit and from header; collapsed story and palette persistence')

    p.locator('[data-action=sample][data-behavior=collector]').click()
    text = p.locator('#dialog-body').inner_text()
    assert re.search(r'四[个名位]?队友.*收集者', text, re.S), text
    assert re.search(r'商店.{0,8}只有收集者', text), text
    assert p.locator('#dialog .perk-art[data-copies="5"]').count() == 1
    p.screenshot(path=str(OUT / 'release-collector.png'))
    p.locator('#close-dialog').click()
    passed('collector', 'Collector effect restores four teammates leading to a Collector-only shop, with five real icon copies')

    p.locator('[data-action=gallery]').click()
    assert p.locator('.library-person').count() == COUNTS['lol']
    for theme in ['basket', 'abstract', 'all']:
        p.locator('[data-action=library-filter][data-theme=' + theme + ']').click()
        assert p.locator('.library-person').count() == (len(PEOPLE) if theme == 'all' else COUNTS[theme])
    assert p.locator('#dialog .pending-portrait').count() == 0
    p.locator('[data-search=library]').fill('阿水')
    p.wait_for_timeout(300)
    assert p.locator('.library-person').count() == 1
    p.locator('.library-person').click()
    assert p.locator('#dialog .person-perks button').count() == 3
    assert p.locator('#dialog .universe-timeline article').count() == 4
    p.screenshot(path=str(OUT / 'release-person-detail.png'), full_page=True)
    p.locator('#dialog .person-perks button').first.click()
    p.locator('[data-action=library-back]').click()
    assert p.locator('.library-person-detail').count() == 1
    p.locator('[data-action=library-back]').click()
    assert p.locator('[data-search=library]').input_value() == '阿水'
    p.locator('[data-search=library]').fill('')
    p.wait_for_timeout(300)
    p.locator('[data-action=library-filter][data-theme=lol]').click()
    p.locator('#dialog').evaluate('e=>e.scrollTop=600')
    saved = p.locator('#dialog').evaluate('e=>e.scrollTop')
    p.locator('[data-id=lol-rookie]').click()
    p.locator('[data-action=library-back]').click()
    p.wait_for_timeout(100)
    assert abs(p.locator('#dialog').evaluate('e=>e.scrollTop') - saved) < 5
    for width in [320, 360, 393, 430, 1280]:
        p.set_viewport_size({'width': width, 'height': 852})
        layout(p)
        assert p.locator('#dialog').evaluate('e=>e.scrollWidth<=e.clientWidth')
    p.set_viewport_size({'width': 393, 'height': 852})
    p.screenshot(path=str(OUT / 'release-people.png'))
    passed('catalog', 'dynamic expanded roster counts, resolved aliases, no placeholder portraits, nested back and restored scroll')

    for theme, names in NEW_NAMES.items():
        p.locator('[data-action=library-filter][data-theme=' + theme + ']').click()
        for name in names:
            p.locator('[data-search=library]').fill(name)
            p.wait_for_timeout(300)
            assert p.locator('.library-person').count() >= 1, (theme, name)
            p.locator('.library-person').first.click()
            assert p.locator('#dialog .person-perks button').count() == 3, name
            assert p.locator('#dialog .universe-timeline article').count() == 4, name
            assert p.locator('#dialog .pending-portrait').count() == 0, name
            if name in ['吴悠', '雨姐']:
                p.screenshot(path=str(OUT / ('release-new-' + theme + '.png')), full_page=True)
            p.locator('[data-action=library-back]').click()
        p.locator('[data-search=library]').fill('')
        p.wait_for_timeout(300)
    p.locator('#close-dialog').click()
    passed('new-cast', 'all requested basketball/abstract additions are searchable in the right theme with portraits, four setting fragments and three exclusive cards')

    p.locator('[data-action=card-gallery]').click()
    assert p.locator('.library-card').count() == CARDS['lol']
    p.locator('[data-action=library-filter][data-theme=all]').click()
    assert p.locator('.library-card').count() == sum(CARDS.values())
    p.locator('[data-library-owner]').select_option('dailanzi')
    assert p.locator('.library-card').count() == 3
    p.locator('[data-id=v11-dailanzi-2]').click()
    assert '不作为本轮作答证据' in p.locator('.library-card-detail').inner_text()
    p.screenshot(path=str(OUT / 'release-card-detail.png'))
    p.locator('[data-action=library-back]').click()
    assert p.locator('[data-library-owner]').input_value() == 'dailanzi'
    p.locator('#close-dialog').click()
    passed('cards', 'all expanded cards browseable, owner filter and innate-gift evidence distinction preserved')

    p.locator('[data-action=readthrough]').click()
    assert p.locator('.v11-readthrough article').count() == 12
    p.locator('[data-action=sample-chapter]').click()
    qid = p.locator('.option').first.get_attribute('data-question')
    p.locator('.option').first.evaluate('el=>{el.click();el.click();}')
    p.wait_for_function("id=>!document.querySelector('.option[data-question=\"'+id+'\"]')", arg=qid)
    assert '02' in p.locator('.quiz-meta strong').inner_text()
    p.locator('[data-action=previous]').click()
    assert p.locator('.option').first.get_attribute('data-question') == qid
    p.screenshot(path=str(OUT / 'release-question.png'))
    passed('automatic-advance', 'sample chapter, automatic advance, stale double-tap protection and back-edit still work')

    # Seed valid seven-answer drafts and finish through the actual last answer button.
    # This deterministically covers the generic League scene even if ordinary draws reveal Uzi.
    for theme in ['lol', 'basket', 'abstract']:
        fixture = p.evaluate('''theme=>{const e=ShenrenEngine,d=WORLD_DATA;for(let k=0;k<80;k++){const s=e.draw(d,theme,8),answers=s.deck.map((x,i)=>d.questions.find(q=>q.id===x.id).options[(i+k)%4].id);s.answers=answers;const r=e.analyze(s,d);if(r.identity.personId==='uzi')continue;s.answers=answers.slice(0,7).concat([null]);s.index=7;s.phase='quiz';if(!e.valid(s,d))throw Error('bad reveal draft');localStorage.setItem('world-otherme.v10.session',JSON.stringify(s));return{last:answers[7],person:r.identity.personId};}throw Error('could not find a legal non-Uzi reveal draft');}''', theme)
        home(p, theme)
        p.locator('[data-action=resume]').click()
        p.locator('.option[data-id="' + str(fixture['last']) + '"]').click()
        p.wait_for_selector('.reveal-page')
        assert_large_reveal(p, theme, fixture['person'])
        p.screenshot(path=str(OUT / ('release-reveal-' + theme + '.png')), full_page=True)
        p.locator('[data-action=reveal-open]').click()
        face = p.locator('#app .identity-photo .portrait').bounding_box()
        assert face and face['width'] >= 120, (theme, face)
    passed('reveal-portraits', 'three distinct loaded theme backgrounds reveal the matched portrait at least 60% of scene width at four mobile widths; result portraits remain enlarged')

    for theme in ['lol', 'basket', 'abstract']:
        for count in [8, 16, 24]:
            home(p, theme)
            p.locator('[data-action=mode][data-count="' + str(count) + '"]').click()
            p.locator('#app [data-action=start]').click()
            answer(p, count)
            p.wait_for_selector('.reveal-page')
            p.locator('[data-action=reveal-open]').click()
            assert p.locator('#app .team-card').count() == 5
            assert p.locator('#app .universe-timeline article').count() == 4
            assert p.locator('#app [data-squad-name]').count() == 1
            assert p.locator('#app .inherent-panel .person-perks button').count() == 3
            # Strongly different answer evidence cannot be erased by popularity priority.
            facts = p.evaluate('''()=>{const h=JSON.parse(localStorage.getItem('world-otherme.v10.history'))[0],r=ShenrenEngine.analyze(h.session,WORLD_DATA),p=r.identity,top=Math.max(...r.ranked.map(x=>x.rawMatch)),policy=WORLD_DATA.rosterPolicy;return{raw:p.rawMatch,match:p.match,gap:top-p.rawMatch,bonus:p.editorialBonus||0,eligible:p.tier==='flagship'?policy.flagshipNearTop:policy.nearTop};}''')
            assert facts['match'] == facts['raw']
            assert facts['gap'] <= facts['bonus'], facts
            if facts['bonus']:
                assert facts['gap'] <= facts['eligible'], facts
            assert '原始匹配' in p.locator('#app .identity-tags').inner_text()
            layout(p)
            if count == 8:
                p.screenshot(path=str(OUT / ('release-result-' + theme + '.png')), full_page=True)
    passed('quiz', 'all nine theme/count flows complete, show raw match evidence, and keep popularity priority within the answer-related score boundary')

    for width in [320, 360, 393, 430, 1280]:
        p.set_viewport_size({'width': width, 'height': 852})
        layout(p)
    p.set_viewport_size({'width': 393, 'height': 852})
    p.locator('[data-action=squad]').click()
    p.locator('[data-action=squad-free]').click()
    p.locator('[data-action=squad-save]').click()
    assert '自选阵容' in p.locator('.team-heading').inner_text()
    png(p, '[data-action=poster]', 'release-exported-poster.png')
    identity = p.locator('.identity-copy h1').inner_text()
    team = p.locator('#app .team-card').evaluate_all('xs=>xs.map(x=>x.dataset.person)')
    before = p.locator('#app [data-squad-name]').inner_text()
    p.locator('[data-action=team-name]').first.click()
    after = p.locator('#app [data-squad-name]').inner_text()
    assert before != after
    assert identity == p.locator('.identity-copy h1').inner_text()
    assert team == p.locator('#app .team-card').evaluate_all('xs=>xs.map(x=>x.dataset.person)')
    p.locator('header [data-action=archive]').click()
    p.locator('.history-card').first.click()
    assert after == p.locator('#app [data-squad-name]').inner_text()
    png(p, '[data-action=team-poster]', 'team-poster.png')
    passed('posters', 'custom lineup, independent team-name reroll/history persistence and both real 1080×1920 PNG exports')

    with p.expect_download() as dl:
        p.locator('footer [data-action=download-html]').click()
    assert dl.value.suggested_filename.startswith('平行宇宙的另一个我'), dl.value.suggested_filename
    offline = Path(dl.value.path()).read_bytes()
    assert hashlib.sha256(offline).hexdigest() == hashlib.sha256((R / 'dist/world-another-me.html').read_bytes()).hexdigest()
    passed('html-download', 'online HTML download is exactly the full current self-contained artifact')

    for schema in [10, 11]:
        fixture = p.evaluate('''schema=>{const d=schema===10?WORLD_LEGACY_DATA:WORLD_V11_DATA,e=schema===10?ShenrenLegacyEngine:ShenrenV11Engine,s=e.draw(d,'basket',8);s.answers=s.deck.map((_,i)=>i%4);const r=e.analyze(s,d),ids=r.team.map(p=>p.id),rec={id:'legacy-'+schema,session:s,customTeam:{ids,free:false},teamBrand:{title:'旧宇宙五位嘴硬市民',motto:'旧队名不能被新版重新抽走',ids,theme:'basket'}};localStorage.setItem('world-otherme.v10.history',JSON.stringify([rec]));return{name:r.identity.nickname||r.identity.name,team:ids,brand:rec.teamBrand.title};}''', schema)
        p.locator('header [data-action=archive]').click()
        assert p.locator('.history-card').count() == 1
        p.locator('.history-card').click()
        assert p.locator('.identity-copy h1').inner_text() == fixture['name']
        assert p.locator('#app .team-card').evaluate_all('xs=>xs.map(x=>x.dataset.person)') == fixture['team']
        assert p.locator('#app [data-squad-name]').inner_text() == fixture['brand']
        p.screenshot(path=str(OUT / f'release-history-{schema}.png'))
        passed('v10-history' if schema == 10 else 'v11-history', f'old schema {schema} record keeps frozen-engine identity, original custom squad and saved team name')

    home(p, 'lol')
    p.locator('[data-action=squad-home]').first.click()
    p.locator('[data-action=squad-fill]').click()
    p.locator('[data-action=squad-save]').click()
    assert p.locator('.standalone-squad').count() == 1
    initial = p.locator('#app [data-squad-name]').inner_text()
    ids = p.locator('#app .team-card').evaluate_all('xs=>xs.map(x=>x.dataset.person)')
    assert len(set(ids)) == 5
    p.locator('[data-action=team-name]').first.click()
    assert initial != p.locator('#app [data-squad-name]').inner_text()
    name = p.locator('#app [data-squad-name]').inner_text()
    p.locator('[data-action=squad-home]').click()
    p.locator('[data-action=squad-save]').click()
    assert name == p.locator('#app [data-squad-name]').inner_text()
    assert ids == p.locator('#app .team-card').evaluate_all('xs=>xs.map(x=>x.dataset.person)')
    png(p, '[data-action=team-poster]', 'standalone-team-poster.png')
    p.screenshot(path=str(OUT / 'release-team.png'), full_page=True)
    passed('standalone-squad', 'self-selected five-person squad saves its distinct members/name and exports PNG without a quiz')

    denied = browser.new_context(viewport={'width': 393, 'height': 852}, offline=True)
    q = denied.new_page()
    q.on('pageerror', lambda e: errors.append(str(e)))
    q.set_content(offline.decode(), wait_until='load')
    q.wait_for_selector('.intro-page')
    q.locator('[data-action=intro-skip]').click()
    q.locator('#app [data-action=start]').click()
    answer(q, 8)
    q.locator('[data-action=reveal-open]').click()
    assert q.locator('#app .team-card').count() == 5
    denied.close()
    passed('offline', 'full standalone HTML runs with network/storage unavailable and completes a real eight-question quiz')

    native = ctx.new_page()
    native.on('pageerror', lambda e: errors.append(str(e)))
    native.goto(base + '/xhs/', wait_until='networkidle')
    native.wait_for_selector('.intro-page')
    native.locator('[data-action=intro-skip]').click()
    native.locator('[data-action=gallery]').click()
    assert native.locator('.library-person').count() == COUNTS['lol']
    native.close()
    passed('native-web-fallback', 'staged XHS no-SDK web fallback loads local assets; platform/device acceptance remains pending')

    mock = ctx.new_page()
    mock.on('pageerror', lambda e: errors.append(str(e)))
    mock.add_init_script('''window.nativeCalls=[];window.xhs={launchOptions:{miniToolEnv:{buildVersion:9490001}},miniTool:{getStorage:async()=>({data:null}),setStorage:async()=>({}),removeStorage:async()=>({}),getWindowInfo:async()=>({windowWidth:393,windowHeight:852,safeArea:{left:0,top:20,right:393,bottom:818},menuButtons:{share:{bottom:64}}}),writeTempFile:async({data})=>{nativeCalls.push(['temp',data.slice(0,22)]);return{filePath:'xhs-local-poster.png'};},saveImageToPhotosAlbum:async({filePath})=>{nativeCalls.push(['album',filePath]);return{};}}};''')
    mock.goto(base + '/xhs/', wait_until='networkidle')
    mock.wait_for_selector('.intro-page')
    mock.locator('[data-action=intro-skip]').click()
    mock.locator('[data-action=squad-home]').first.click()
    mock.locator('[data-action=squad-fill]').click()
    mock.locator('[data-action=squad-save]').click()
    mock.locator('[data-action=team-poster]').first.click()
    mock.wait_for_selector('.squad-poster')
    assert mock.locator('.download-png').count() == 0
    mock.locator('[data-action=save-album]').click()
    mock.wait_for_function("nativeCalls.some(c=>c[0]==='album')")
    assert mock.evaluate('nativeCalls') == [['temp', 'data:image/png;base64,'], ['album', 'xhs-local-poster.png']]
    mock.close()
    passed('native-contract', 'mock SDK integration saves team poster via temporary file then explicit album button, not a browser download')
    assert not errors, errors
    assert not failures, failures
    assert not [url for url in requests if not url.startswith(base)], requests
    passed('runtime-clean', 'no page JavaScript exceptions, HTTP failures or external runtime resource requests')
    ctx.close()
    browser.close()

server.shutdown()
atlas = json.loads((R / 'assets/portrait-atlas.json').read_text())
report = {'status': 'passed', 'checks': checks, 'checkIds': [c['id'] for c in checks], 'count': len(checks), 'viewport': '393×852 Chromium mobile viewport; not physical phone or XHS platform acceptance', 'layoutWidths': [320, 360, 393, 430, 1280], 'html_sha256': hashlib.sha256((R / 'dist/world-another-me.html').read_bytes()).hexdigest(), 'enabledPeople': len(PEOPLE), 'byThemePeople': COUNTS, 'cards': sum(CARDS.values()), 'revealBackgroundSHA256': reveal_hashes, 'pendingAvatars': [p['personId'] for p in PEOPLE if atlas['portraits'][p['personId']].get('pending')]}
(R / 'docs/browser-check-v13.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(len(checks), 'browser groups passed')
