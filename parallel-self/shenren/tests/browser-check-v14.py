"""Actual V14 web flows. Chromium mobile emulation is not XHS/device acceptance."""
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from urllib.request import urlopen
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright
from PIL import Image
import base64, hashlib, json, re, threading

R = Path(__file__).resolve().parents[1]
OUT = R / 'dist/qa/v14'
OUT.mkdir(parents=True, exist_ok=True)
D = json.loads((R / 'src/data.json').read_text())
PEOPLE = [p for p in D['characters'] if p.get('enabled') is not False]
COUNTS = {t: sum(p['theme'] == t for p in PEOPLE) for t in ['lol', 'basket', 'abstract']}
CARDS = {t: sum(a.get('enabled') is not False for a in D['augments'][t]) for t in COUNTS}
NEW_NAMES = {'basket': ['格林', '恶鼠']}
INTRO_KEYS = ['introRealLife', 'introMirror', 'introNewWorld']
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

def story_facts(page):
    facts = page.evaluate('''()=>{const s=JSON.parse(localStorage.getItem('world-otherme.v10.story.v14')),v=ShenrenEngine.storyView(s,WORLD_DATA);return{person:s.personId,node:v.node,owned:v.ownedCardIds,ending:v.isEnding,text:v.text,choices:v.choices.length};}''')
    assert page.locator('.story-top').bounding_box()['y'] >= 0
    assert page.locator('header').bounding_box()['y'] >= 0
    assert sorted(page.locator('.v14-story .story-owned [data-owned-card]').evaluate_all('xs=>xs.map(x=>x.dataset.ownedCard)')) == sorted(facts['owned'])
    triggered = page.locator('.v14-story [data-trigger-card]').evaluate_all('xs=>xs.map(x=>x.dataset.triggerCard)')
    assert set(triggered) <= set(facts['owned']), (triggered, facts)
    return facts

def story_step(page, route=0):
    facts = story_facts(page)
    assert not facts['ending']
    page.wait_for_timeout(250)  # The app locks repeated taps for 220 ms.
    choices = page.locator('.v14-story .story-choice')
    if choices.count():
        choices.nth(min(route, choices.count()-1)).click()
    else:
        page.locator('.v14-story [data-action=story-next]').click()
    page.wait_for_function('id=>document.querySelector(".v14-story").dataset.storyNode!==id', arg=facts['node'])
    return story_facts(page)

def finish_story(page, route=0):
    for _ in range(12):
        facts = story_facts(page)
        if facts['ending']:
            return facts
        story_step(page, route)
    raise AssertionError('story did not reach its ending')

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
    viewport_meta = p.locator('meta[name=viewport]').get_attribute('content')
    assert 'user-scalable=no' not in viewport_meta and 'maximum-scale=1' not in viewport_meta
    for i in [1, 2, 3]:
        assert f'{i}/3' in p.locator('.intro-top').inner_text()
        assert p.locator('.intro-figure img').get_attribute('src') == p.evaluate('key=>WORLD_BRANDING[key]', INTRO_KEYS[i-1])
        p.locator('.intro-figure img').evaluate('img=>img.decode()')
        for width in [360, 390, 430]:
            p.set_viewport_size({'width': width, 'height': 852})
            layout(p)
            button = p.locator('[data-action=intro-next]').bounding_box()
            assert button['y'] >= 0 and button['y'] + button['height'] <= 853, (i, width, button)
        p.set_viewport_size({'width': 393, 'height': 852})
        p.screenshot(path=str(OUT / f'intro-{i}.png'))
        p.locator('[data-action=intro-next]').click()
    assert p.locator('.journey-fold[open]').count() == 0
    assert p.evaluate('WORLD_DATA.version') == 13
    assert p.evaluate('WORLD_DATA.releaseVersion') == 14
    assert (R / 'dist/web/index.html').stat().st_size < 6000
    p.screenshot(path=str(OUT / 'release-home.png'), full_page=True)
    for width in [320, 360, 390, 393, 430, 1280]:
        p.set_viewport_size({'width': width, 'height': 852})
        layout(p)
    passed('intro', 'three new story pages, collapsed replay, small entry and six responsive widths')

    # V14 adds three independent original 4:5 panels; logo/cover may be retained.
    branding = p.evaluate('WORLD_BRANDING')
    intro_hashes = {}
    for name in INTRO_KEYS:
        url = branding[name]
        assert 'v14' in url and url.endswith('.webp'), (name, url)
        body = urlopen(urljoin(base + '/web/', url)).read()
        assert len(body) > 1000
        import io
        image = Image.open(io.BytesIO(body))
        assert abs(image.width / image.height - .8) < .02, (name, image.size)
        intro_hashes[name] = hashlib.sha256(body).hexdigest()
    assert len(set(intro_hashes.values())) == 3
    reveal_hashes = {}
    for theme, key in REVEAL_KEYS.items():
        assert key in branding and branding[key], key
        url = branding[key]
        body = base64.b64decode(url.split(',', 1)[1]) if url.startswith('data:') else urlopen(urljoin(base + '/web/', url)).read()
        assert len(body) > 1000, key
        reveal_hashes[theme] = hashlib.sha256(body).hexdigest()
    assert len(set(reveal_hashes.values())) == 3, 'theme reveal backgrounds must contain different actual images'
    passed('new-art', 'three independently packaged V14 4:5 story illustrations load as distinct actual bitmap assets')

    p.set_viewport_size({'width': 393, 'height': 852})
    assert p.evaluate('document.documentElement.dataset.style') == 'paper'
    p.locator('[data-action=palette]').click()
    assert p.evaluate('document.documentElement.dataset.style') == 'night'
    p.screenshot(path=str(OUT / 'release-home-night.png'), full_page=True)
    p.reload(wait_until='networkidle')
    p.wait_for_selector('.intro-page')
    assert p.evaluate('document.documentElement.dataset.style') == 'night'
    p.locator('[data-action=intro-skip]').click()
    p.locator('header [data-action=intro]').click()
    assert '1/3' in p.locator('.intro-top').inner_text()
    p.locator('[data-action=intro-next]').click()
    assert '2/3' in p.locator('.intro-top').inner_text()
    p.locator('[data-action=intro-prev]').click()
    assert '1/3' in p.locator('.intro-top').inner_text()
    p.locator('[data-action=intro-skip]').click()
    p.locator('.journey-fold summary').click()
    assert p.locator('.journey-thumb').count() == 3
    p.locator('.journey-fold summary').click()
    p.locator('[data-action=palette]').click()
    passed('replay-palette', 'opening can be replayed every visit and from header; collapsed story and palette persistence')

    launch = p.locator('#app [data-action=gallery]').first
    launch.focus()
    p.keyboard.press('Enter')
    p.wait_for_selector('#dialog[open]')
    p.keyboard.press('Tab')
    assert p.evaluate('document.getElementById("dialog").contains(document.activeElement)')
    p.keyboard.press('Escape')
    p.wait_for_selector('#dialog[open]', state='hidden')
    assert p.evaluate('document.activeElement.dataset.action') == 'gallery'
    p.locator('#tabbar [data-action=gallery]').click()
    p.evaluate('window.history.back()')
    p.wait_for_selector('#dialog[open]', state='hidden')
    assert p.locator('.v14-home').count() == 1
    passed('navigation', 'keyboard opening/focus trap/Escape focus return, bottom navigation and browser back close the gallery without leaving the app')

    p.locator('[data-action=card-gallery]').first.click()
    p.locator('[data-action=library-filter][data-theme=all]').click()
    p.locator('.library-card[data-id=collector-union]').click()
    text = p.locator('#dialog-body').inner_text()
    assert re.search(r'四[个名位]?队友.*收集者', text, re.S), text
    assert re.search(r'商店.{0,8}只有收集者', text), text
    assert p.locator('#dialog .perk-art[data-copies="5"]').count() == 1
    p.screenshot(path=str(OUT / 'release-collector.png'))
    p.locator('#close-dialog').click()
    passed('collector', 'Collector effect restores four teammates leading to a Collector-only shop, with five real icon copies')

    p.locator('[data-action=gallery]').first.click()
    assert p.locator('.library-person').count() == COUNTS['lol']
    for theme in ['basket', 'abstract', 'all']:
        p.locator('[data-action=library-filter][data-theme=' + theme + ']').click()
        assert p.locator('.library-person').count() == (len(PEOPLE) if theme == 'all' else COUNTS[theme])
    assert p.locator('#dialog .pending-portrait').count() == 0
    p.locator('[data-search=library]').fill('阿水')
    p.wait_for_timeout(300)
    assert p.locator('.library-person').count() == 1
    p.locator('.library-person').click()
    assert p.locator('#dialog .person-perks button').count() == 2
    p.screenshot(path=str(OUT / 'release-person-detail.png'))
    p.locator('#dialog .person-perks button').first.click()
    p.locator('[data-action=library-back]').click()
    assert p.locator('.library-person-detail').count() == 1
    p.locator('[data-action=library-back]').click()
    assert p.locator('[data-search=library]').input_value() == '阿水'
    p.locator('[data-search=library]').fill('')
    p.wait_for_timeout(300)
    p.locator('[data-action=library-filter][data-theme=lol]').click()
    p.locator('#dialog').evaluate('d=>new Promise(resolve=>requestAnimationFrame(()=>{d.scrollTop=600;requestAnimationFrame(resolve);}))')
    # Choose a completely visible card. A hard-coded offscreen person makes
    # Playwright scroll it into view before the app can capture the real position.
    visible = p.evaluate('''()=>{const d=document.querySelector('#dialog'),r=d.getBoundingClientRect(),head=d.querySelector('.dialog-head').getBoundingClientRect(),search=d.querySelector('.search-label').getBoundingClientRect(),top=Math.max(r.top,head.bottom,search.bottom)+8,bottom=Math.min(r.bottom,innerHeight)-8,card=[...d.querySelectorAll('.library-person')].find(x=>{const b=x.getBoundingClientRect();return b.top>=top&&b.bottom<=bottom;});if(!card)throw Error('no fully visible catalog card');const b=card.getBoundingClientRect();d.addEventListener('pointerdown',e=>{const c=e.target.closest('.library-person');if(c)window.catalogActualClick={id:c.dataset.id,scroll:d.scrollTop};},{once:true});return{id:card.dataset.id,scroll:d.scrollTop,box:{x:b.x,y:b.y,width:b.width,height:b.height}};}''')
    p.locator('.library-person[data-id="' + visible['id'] + '"]').click()
    clicked = p.evaluate('window.catalogActualClick')
    assert clicked == {'id': visible['id'], 'scroll': visible['scroll']}, (visible, clicked)
    p.locator('[data-action=library-back]').click()
    p.wait_for_function('id=>document.activeElement.dataset.id===id', arg=visible['id'])
    returned = p.evaluate('''id=>{const d=document.querySelector('#dialog'),c=d.querySelector('.library-person[data-id="'+id+'"]'),b=c.getBoundingClientRect();return{id:document.activeElement.dataset.id,scroll:d.scrollTop,box:{x:b.x,y:b.y,width:b.width,height:b.height}};}''', visible['id'])
    assert returned['scroll'] == clicked['scroll'], (visible, clicked, returned)
    assert returned['box'] == visible['box'], (visible, returned)
    (OUT / 'catalog-scroll-check.json').write_text(json.dumps({'before': visible, 'atClick': clicked, 'after': returned}, ensure_ascii=False, indent=2) + '\n')
    for width in [320, 360, 390, 393, 430, 1280]:
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
            assert p.locator('#dialog .person-perks button').count() >= 2, name
            assert p.locator('#dialog .pending-portrait').count() == 0, name
            if name in ['格林', '恶鼠']:
                p.screenshot(path=str(OUT / ('release-new-' + ('draymond-green' if name == '格林' else 'ershu') + '.png')))
            p.locator('[data-action=library-back]').click()
        p.locator('[data-search=library]').fill('')
        p.wait_for_timeout(300)
    p.locator('[data-library-group]').select_option('NBA')
    assert p.locator('.library-person [data-avatar="draymond-green"]').count() == 1
    assert p.locator('.library-person [data-avatar="ershu"]').count() == 0
    p.locator('[data-library-group]').select_option('民间篮球')
    assert p.locator('.library-person [data-avatar="draymond-green"]').count() == 0
    assert p.locator('.library-person [data-avatar="ershu"]').count() == 1
    p.locator('[data-search=library]').fill('张梓祎')
    p.wait_for_timeout(300)
    assert p.locator('.library-person').count() == 1
    assert p.locator('.library-person [data-avatar="ershu"]').count() == 1
    p.locator('[data-search=library]').fill('')
    p.wait_for_timeout(300)
    p.locator('[data-library-group]').select_option('')
    assert p.locator('.library-person').count() == COUNTS['basket']
    p.locator('#close-dialog').click()
    passed('new-cast', 'Green/Ershu have portraits, story entries and representative cards; NBA/folk groups stay separate and Zhang Ziyi resolves only to Ershu')

    p.locator('[data-action=card-gallery]').first.click()
    assert p.locator('.library-card').count() == CARDS['lol']
    p.locator('[data-action=library-filter][data-theme=all]').click()
    assert p.locator('.library-card').count() == sum(CARDS.values())
    p.locator('[data-library-owner]').select_option('dailanzi')
    assert p.locator('.library-card').count() == 3
    first_perk = p.evaluate('ShenrenEngine.resolvePerson(WORLD_DATA,"dailanzi").signaturePerks[0]')
    p.locator('.library-card[data-id="' + first_perk + '"]').click()
    assert p.locator('.library-card-detail dd').count() == 3
    p.screenshot(path=str(OUT / 'release-card-detail.png'))
    p.locator('[data-action=library-back]').click()
    assert p.locator('[data-library-owner]').input_value() == 'dailanzi'
    p.locator('#close-dialog').click()
    passed('cards', 'all enabled cards browseable, owner filter and full trigger/effect/punchline details preserved')

    shared = p.evaluate('ShenrenEngine.enabledCards(WORLD_DATA).filter(a=>ShenrenEngine.cardOwners(a).length===2).map(a=>({id:a.id,name:a.name,theme:a.theme,owners:ShenrenEngine.cardOwners(a).map(id=>ShenrenEngine.resolvePerson(WORLD_DATA,id).id)}))')
    assert len(shared) == 6
    for card in shared:
        home(p, card['theme'])
        p.locator('#app [data-action=gallery]').first.click()
        for owner in card['owners']:
            p.locator('.library-person[data-id="' + owner + '"]').click()
            tag = p.locator('.library-person-detail .character-tags [data-id="' + card['id'] + '"]')
            assert tag.inner_text().replace('↗', '').strip() == card['name']
            tag.click()
            assert p.locator('.library-card-detail h2').inner_text() == card['name']
            assert p.locator('.library-card-detail .card-owners button').count() == 2
            p.locator('[data-action=library-back]').click()
            p.locator('[data-action=library-back]').click()
        p.locator('#close-dialog').click()
    passed('shared-cards', 'six shared cards exist once and both owners open the same card through actual character tags')

    home(p, 'lol')
    p.locator('[data-action=mode][data-count="8"]').click()
    p.locator('#app [data-action=start]').click()
    qid = p.locator('.option').first.get_attribute('data-question')
    p.locator('.option').first.evaluate('el=>{el.click();el.click();}')
    p.wait_for_function("id=>!document.querySelector('.option[data-question=\"'+id+'\"]')", arg=qid)
    assert '02' in p.locator('.quiz-meta strong').inner_text()
    p.locator('[data-action=previous]').click()
    assert p.locator('.option').first.get_attribute('data-question') == qid
    p.screenshot(path=str(OUT / 'release-question.png'))
    passed('automatic-advance', 'a real random chapter, automatic advance, stale double-tap protection and back-edit still work')

    # Seed valid seven-answer drafts and finish through the actual last answer button.
    # All V14 identities now use the matched portrait rather than an unrelated championship image.
    for theme in ['lol', 'basket', 'abstract']:
        fixture = p.evaluate('''theme=>{const e=ShenrenEngine,d=WORLD_DATA;for(let k=0;k<80;k++){const s=e.draw(d,theme,8),answers=s.deck.map((x,i)=>d.questions.find(q=>q.id===x.id).options[(i+k)%4].id);s.answers=answers;const r=e.analyze(s,d);s.answers=answers.slice(0,7).concat([null]);s.index=7;s.phase='quiz';if(!e.valid(s,d))throw Error('bad reveal draft');localStorage.setItem('world-otherme.v10.session',JSON.stringify(s));return{last:answers[7],person:r.identity.personId};}throw Error('could not find a legal reveal draft');}''', theme)
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
            assert p.locator('#app [data-squad-name]').count() == 1
            assert p.locator('#app .result-owned [data-owned-card]').count() == 1
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

    # A result story starts with its one actually awarded answer card and records
    # explicit branch rewards in the same record that later supplies the poster.
    result_identity = p.locator('.identity-copy h1').inner_text()
    seed = p.locator('.result-owned [data-owned-card]').evaluate_all('xs=>xs.map(x=>x.dataset.ownedCard)')
    p.locator('[data-action=story-start][data-origin=result]').click()
    assert story_facts(p)['owned'] == seed
    result_story = finish_story(p, 0)
    p.locator('[data-action=story-result]').click()
    assert p.locator('.identity-copy h1').inner_text() == result_identity
    assert sorted(p.locator('.result-owned [data-owned-card]').evaluate_all('xs=>xs.map(x=>x.dataset.ownedCard)')) == sorted(result_story['owned'])

    for width in [320, 360, 390, 393, 430, 1280]:
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
    p.locator('.result-top [data-action=archive]').click()
    p.locator('#app .history-card').first.click()
    assert after == p.locator('#app [data-squad-name]').inner_text()
    png(p, '[data-action=team-poster]', 'team-poster.png')
    passed('posters', 'custom lineup, independent team-name reroll/history persistence and both real 1080×1920 PNG exports')

    with p.expect_download() as dl:
        p.locator('footer [data-action=download-html]').click()
    assert dl.value.suggested_filename.startswith('平行宇宙的另一个我'), dl.value.suggested_filename
    offline = Path(dl.value.path()).read_bytes()
    assert hashlib.sha256(offline).hexdigest() == hashlib.sha256((R / 'dist/world-another-me.html').read_bytes()).hexdigest()
    passed('html-download', 'online HTML download is exactly the full current self-contained artifact')

    tested_stories = ['dailanzi', 'huchenfeng', 'fengge', 'luobenwei', 'xujingyu', 'draymond-green', 'ershu']
    for pid in tested_stories:
        home(p)
        p.locator('[data-action=story-preview]').click()
        p.locator('[data-action=story-start][data-person="' + pid + '"]').click()
        assert p.locator('.v14-story').get_attribute('data-story-person') == pid
        assert story_facts(p)['owned'] == []
        if pid == 'dailanzi':
            story_step(p)
            assert p.locator('.story-choice').count() == 2
            first_choice = story_facts(p)['node']
            after = story_step(p, 0)
            assert after['owned']
            p.reload(wait_until='networkidle')
            p.wait_for_selector('.intro-page')
            p.locator('[data-action=intro-skip]').click()
            p.locator('[data-action=story-resume]').click()
            assert story_facts(p)['owned'] == after['owned']
            p.wait_for_timeout(250)
            p.locator('[data-action=story-back]').click()
            p.wait_for_function('id=>document.querySelector(".v14-story").dataset.storyNode===id', arg=first_choice)
            assert story_facts(p)['owned'] == []
        ending = finish_story(p, 0)
        p.screenshot(path=str(OUT / ('release-story-' + pid + '.png')), full_page=True)
        if pid == 'dailanzi':
            png(p, '[data-action=story-poster]', 'story-poster.png')
            p.locator('[data-action=story-restart]').click()
            assert story_facts(p)['owned'] == []
            other = finish_story(p, 1)
            assert other['text'] != ending['text']
            p.screenshot(path=str(OUT / 'release-story-alternate.png'), full_page=True)
        p.locator('[data-action=story-exit]').click()
    passed('stories', 'five samples plus Green/Ershu run through real choices; acquired-only events, distinct endings, backtracking reward removal, refresh resume, record/card consistency and actual story PNG export work')

    for schema in [10, 11, 12]:
        home(p)
        fixture = p.evaluate('''schema=>{const d=schema===10?WORLD_LEGACY_DATA:schema===11?WORLD_V11_DATA:WORLD_V12_DATA,e=schema===10?ShenrenLegacyEngine:schema===11?ShenrenV11Engine:ShenrenV12Engine,s=e.draw(d,'basket',8);s.answers=s.deck.map((_,i)=>i%4);const r=e.analyze(s,d),ids=r.team.map(p=>p.id),rec={id:'legacy-'+schema,session:s,customTeam:{ids,free:false},teamBrand:{title:'旧宇宙五位嘴硬市民',motto:'旧队名不能被新版重新抽走',ids,theme:'basket'}};localStorage.setItem('world-otherme.v10.history',JSON.stringify([rec]));return{name:r.identity.name,team:ids,brand:rec.teamBrand.title};}''', schema)
        p.locator('#tabbar [data-action=archive]').click()
        assert p.locator('#app .history-card').count() == 1
        p.locator('#app .history-card').click()
        assert p.locator('.identity-copy h1').inner_text() == fixture['name']
        assert p.locator('#app .team-card').evaluate_all('xs=>xs.map(x=>x.dataset.person)') == fixture['team']
        assert p.locator('#app [data-squad-name]').inner_text() == fixture['brand']
        p.screenshot(path=str(OUT / f'release-history-{schema}.png'))
        passed('v10-history' if schema == 10 else 'v11-history' if schema == 11 else 'v12-history', f'old schema {schema} record keeps frozen-engine identity, original custom squad and saved team name')

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

    fallback_ctx = browser.new_context(viewport={'width': 360, 'height': 780})
    fallback_ctx.route('**/intro-real-life-v14.webp', lambda route: route.abort())
    fallback = fallback_ctx.new_page()
    fallback.on('pageerror', lambda e: errors.append(str(e)))
    fallback.goto(base + '/web/', wait_until='networkidle')
    assert '1/3' in fallback.locator('.intro-top').inner_text()
    assert fallback.locator('[data-action=intro-next]').is_enabled()
    fallback.locator('[data-action=intro-next]').click()
    assert '2/3' in fallback.locator('.intro-top').inner_text()
    assert fallback.locator('.intro-copy').inner_text()
    assert fallback.locator('[data-action=intro-next]').is_enabled()
    fallback.locator('[data-action=intro-skip]').click()
    assert fallback.locator('.v14-home').count() == 1
    fallback_ctx.close()
    passed('image-fallback', 'failed first-panel bitmap keeps story text and continue/skip buttons functional at a narrow mobile viewport')

    native = ctx.new_page()
    native.on('pageerror', lambda e: errors.append(str(e)))
    native.goto(base + '/xhs/', wait_until='networkidle')
    native.wait_for_selector('.intro-page')
    native.locator('[data-action=intro-skip]').click()
    native.locator('#app [data-action=gallery]').click()
    assert native.locator('.library-person').count() == COUNTS['lol']
    native.close()
    passed('native-web-fallback', 'staged XHS no-SDK web fallback loads local assets; platform/device acceptance remains pending')

    mock = ctx.new_page()
    mock.on('pageerror', lambda e: errors.append(str(e)))
    mock.add_init_script('''window.nativeCalls=[];window.xhs={launchOptions:{miniToolEnv:{buildVersion:9490001}},miniTool:{getStorage:async()=>({data:null}),setStorage:async()=>({}),removeStorage:async()=>({}),getWindowInfo:async()=>({windowWidth:393,windowHeight:852,safeArea:{left:0,top:20,right:393,bottom:818},menuButtons:{share:{bottom:64}}}),writeTempFile:async({data})=>{nativeCalls.push(['temp',data.slice(0,22)]);return{filePath:'xhs-local-poster.png'};},saveImageToPhotosAlbum:async({filePath})=>{nativeCalls.push(['album',filePath]);return{};}}};''')
    mock.goto(base + '/xhs/', wait_until='networkidle')
    mock.wait_for_selector('.intro-page')
    assert mock.evaluate('getComputedStyle(document.documentElement).getPropertyValue("--safe-area-inset-top").trim()') == '70px'
    assert mock.locator('header .brand').bounding_box()['y'] >= 70
    next_button = mock.locator('[data-action=intro-next]').bounding_box()
    assert next_button['y'] >= 70 and next_button['y'] + next_button['height'] <= 852, next_button
    mock.locator('[data-action=intro-skip]').click()
    mock.locator('#app [data-action=gallery]').first.click()
    assert mock.locator('.library-modal .dialog-head').bounding_box()['y'] >= 70
    mock.locator('#close-dialog').click()
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
    passed('native-contract', 'mock SDK applies a 70px native capsule offset to real header/modal geometry without hiding intro CTA, then saves the team poster via temporary file and explicit album button')
    assert not errors, errors
    assert not failures, failures
    assert not [url for url in requests if not url.startswith(base)], requests
    passed('runtime-clean', 'no page JavaScript exceptions, HTTP failures or external runtime resource requests')
    ctx.close()
    browser.close()

server.shutdown()
atlas = json.loads((R / 'assets/portrait-atlas.json').read_text())
report = {'status': 'passed', 'checks': checks, 'checkIds': [c['id'] for c in checks], 'count': len(checks), 'viewport': '393×852 Chromium mobile viewport; not physical phone or XHS platform acceptance', 'layoutWidths': [320, 360, 390, 393, 430, 1280], 'html_sha256': hashlib.sha256((R / 'dist/world-another-me.html').read_bytes()).hexdigest(), 'enabledPeople': len(PEOPLE), 'byThemePeople': COUNTS, 'cards': sum(CARDS.values()), 'introIllustrationSHA256': intro_hashes, 'revealBackgroundSHA256': reveal_hashes, 'pendingAvatars': [p['personId'] for p in PEOPLE if atlas['portraits'][p['personId']].get('pending')]}
(R / 'docs/browser-check-v14.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(len(checks), 'browser groups passed')
