"""Real browser behavior; mobile viewport emulation is not native acceptance."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
import hashlib
import json
import threading

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / 'dist/qa'
QA.mkdir(exist_ok=True)
checks, errors, failed = [], [], []


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT)))
threading.Thread(target=server.serve_forever, daemon=True).start()
base = 'http://127.0.0.1:' + str(server.server_port)


def passed(label):
    checks.append(label)
    print('PASS', label, flush=True)


def screenshot(page, name, full=True):
    page.locator('img').evaluate_all("async imgs=>{await Promise.all(imgs.map(async im=>{im.loading='eager';try{await im.decode()}catch(e){}}))}")
    page.screenshot(path=str(QA / name), full_page=full)


def layout(page):
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'), page.viewport_size


def answer_rest(page):
    while page.locator('.question-card .option').count():
        option = page.locator('.question-card .option').first
        old = option.get_attribute('data-question')
        option.click()
        page.wait_for_function('id=>!document.querySelector(".option[data-question=\\\""+id+"\\\"]")', arg=old)
    page.wait_for_selector('.result-page')


def history(page):
    return page.evaluate('NBAPlatform.read("history",[])')


def save_png(page, action, filename):
    page.wait_for_timeout(250)
    page.locator('[data-action=' + action + ']').first.click()
    page.wait_for_selector('#dialog .poster-image')
    with page.expect_download() as download:
        page.locator('#dialog [data-action=save-poster]').click()
    image = Image.open(download.value.path())
    assert image.size == (1080, 1920)
    image.save(QA / filename)
    page.locator('#dialog button[data-action=close-dialog]').first.click()


def story_view(page):
    return page.evaluate('NBAGame.storyView(NBAPlatform.read("story").state)')


def finish_story(page, choice):
    for _ in range(14):
        view = story_view(page)
        assert set(page.locator('[data-trigger-card]').evaluate_all('xs=>xs.map(x=>x.dataset.triggerCard)')) <= set(view['ownedCardIds'])
        if view['isEnding']:
            return view
        page.wait_for_timeout(240)
        if page.locator('[data-action=story-choice]').count():
            page.locator('[data-action=story-choice]').nth(choice).click()
        else:
            page.locator('[data-action=story-next]').click()
        page.wait_for_function('old=>document.querySelector(".story-page").dataset.storyNode!==old', arg=view['node'])
    raise AssertionError('story failed to finish')


with sync_playwright() as w:
    browser = w.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
    context = browser.new_context(viewport={'width': 393, 'height': 852}, accept_downloads=True, reduced_motion='reduce')
    p = context.new_page()
    p.set_default_timeout(12000)
    p.on('pageerror', lambda e: errors.append(str(e)))
    p.on('response', lambda r: failed.append([r.status, r.url]) if r.status >= 400 else None)
    p.goto(base + '/dist/web/', wait_until='networkidle')
    p.wait_for_selector('.home-page')
    assert p.title().startswith('整活NBA')
    assert p.evaluate('NBAGame.people.length') == 21
    assert p.evaluate('NBAGame.data.questions.length') == 132
    assert p.evaluate('NBAGame.cards.length') == 51
    assert p.locator('[data-action=theme]').count() == 0
    assert p.evaluate('getComputedStyle(document.documentElement).getPropertyValue("--bg").trim()') == '#100d1c'
    for width in [320, 360, 393, 430, 1280]:
        p.set_viewport_size({'width': width, 'height': 852})
        layout(p)
    p.set_viewport_size({'width': 393, 'height': 852})
    screenshot(p, 'home.png')
    passed('NBA-only purple/gold home, final content counts and five responsive widths')

    p.locator('[data-count="8"]').click()
    p.locator('#app [data-action=start]').first.click()
    p.wait_for_selector('.question-card')
    first = p.locator('.option').first.get_attribute('data-question')
    p.locator('.option').first.evaluate('(b)=>{b.click();b.click()}')
    p.wait_for_function('id=>document.querySelector(".question-card").dataset.question!==id', arg=first)
    draft = p.evaluate('NBAPlatform.read("draft")')
    assert draft['index'] == 1 and sum(x is not None for x in draft['answers']) == 1
    p.locator('[data-action=previous]').click()
    assert p.locator('.question-card').get_attribute('data-question') == first
    p.locator('.option').nth(1).click()
    p.wait_for_function('id=>document.querySelector(".question-card").dataset.question!==id', arg=first)
    p.locator('[data-action=leave-quiz]').click()
    p.reload(wait_until='networkidle')
    p.locator('[data-action=resume]').click()
    p.wait_for_selector('.question-card')
    assert p.evaluate('NBAPlatform.read("draft").index') == 1
    p.screenshot(path=str(QA / 'question.png'))
    answer_rest(p)
    matched = p.locator('.result-page').get_attribute('data-result-person')
    record = history(p)[0]
    assert len(record['session']['deck']) == 8
    assert len(set(p.locator('.team-card').evaluate_all('xs=>xs.map(x=>x.dataset.person)'))) == 5
    screenshot(p, 'result.png')
    passed('real eight-question result, automatic advance, double-tap guard, back-edit and refresh resume')

    original_name = p.locator('[data-team-name]').inner_text()
    p.locator('[data-action=reroll-name]').click()
    assert p.locator('[data-team-name]').inner_text() != original_name
    p.locator('.result-details summary').click()
    p.locator('[data-action=review-answers]').click()
    assert p.locator('#dialog .evidence-item').count() == 8
    p.keyboard.press('Escape')
    p.locator('[data-action=edit-team]').click()
    ids = p.evaluate('NBAGame.people.slice(0,5).map(x=>x.id)')
    for i in range(5):
        p.locator('#team-form select[name=slot' + str(i) + ']').select_option(ids[0])
    p.locator('#team-form button[type=submit]').click()
    assert p.locator('#team-error').inner_text()
    for i in range(5):
        p.locator('#team-form select[name=slot' + str(i) + ']').select_option(ids[i])
    p.locator('#team-form button[type=submit]').click()
    p.wait_for_selector('#dialog', state='hidden')
    assert p.locator('.result-page').get_attribute('data-result-person') == matched
    passed('real answer evidence, distinct random team name and five-person custom team with duplicate rejection')

    result_hash = p.url.split('#', 1)[1]
    p.goto(base + '/dist/web/#diy', wait_until='networkidle')
    p.locator('#diy-form input[name=name]').fill('<b>我</b>')
    p.locator('#diy-form input[name=number]').fill('24')
    p.locator('#diy-form button[type=submit]').click()
    assert p.evaluate('NBAPlatform.read("diy").name') == '<b>我</b>'
    assert p.locator('#diy-preview-name b').count() == 0
    p.locator('#diy-form input[name=name]').fill('篮筐体检主任')
    p.locator('#diy-form input[name=hexName]').fill('打铁也算助攻')
    p.locator('#diy-form textarea[name=hexEffect]').fill('每次打铁都给队友创造篮板机会。')
    p.locator('#diy-form button[type=submit]').click()
    screenshot(p, 'diy.png')
    p.goto(base + '/dist/web/#' + result_hash, wait_until='networkidle')
    p.locator('[data-action=toggle-diy]').click()
    assert p.locator('.team-card[data-person=diy-me]').count() == 1
    assert p.locator('.result-page').get_attribute('data-result-person') == matched
    save_png(p, 'team-poster', 'team-poster.png')
    p.reload(wait_until='networkidle')
    assert p.locator('.team-card[data-person=diy-me]').count() == 1
    assert p.locator('.result-page').get_attribute('data-result-person') == matched
    passed('DIY create/edit, safe literal text, snapshot teammate persistence and real five-person 1080×1920 PNG')

    p.locator('[data-action=story-result]').click()
    p.wait_for_selector('.story-page')
    ending_a = finish_story(p, 0)
    screenshot(p, 'story.png')
    save_png(p, 'story-poster', 'story-poster.png')
    p.locator('[data-action=story-restart]').click()
    p.wait_for_timeout(240)
    ending_b = finish_story(p, 1)
    assert ending_a['text'] != ending_b['text']
    p.reload(wait_until='networkidle')
    assert story_view(p)['text'] == ending_b['text']
    p.wait_for_timeout(240)
    p.locator('[data-action=story-back]').click()
    assert not story_view(p)['isEnding']
    passed('six-scene story branches, actual acquired-card triggers, distinct endings, backtracking and PNG export')

    for count in [16, 24]:
        p.goto(base + '/dist/web/#home', wait_until='networkidle')
        p.locator('[data-count="' + str(count) + '"]').click()
        p.locator('#app [data-action=start]').first.click()
        p.wait_for_selector('.question-card')
        answer_rest(p)
        assert history(p)[0]['session']['count'] == count
        assert p.locator('.team-card').count() == 5
        layout(p)
    passed('complete sixteen- and twenty-four-question flows retain real basketball results and five teammates')

    p.goto(base + '/dist/web/#people', wait_until='networkidle')
    assert p.locator('.person-tile').count() == 21
    p.locator('#people-search').fill('坤坤')
    assert p.locator('.person-tile').count() == 1
    p.goto(base + '/dist/web/#cards', wait_until='networkidle')
    assert p.locator('[data-card]').count() >= 51
    passed('full 21-person catalog, Kun alias search and all 51 actual comic card icons')

    offline = context.new_page()
    offline.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw Error('denied')}})")
    offline.on('pageerror', lambda e: errors.append(str(e)))
    standalone_url = base + '/release/zhenghuo-nba-offline.html'
    offline.route('**/*', lambda route: route.continue_() if route.request.url == standalone_url and route.request.is_navigation_request() else route.abort())
    offline.goto(standalone_url, wait_until='load')
    offline.wait_for_selector('.home-page')
    offline.locator('[data-count="8"]').click()
    offline.locator('#app [data-action=start]').first.click()
    answer_rest(offline)
    assert offline.locator('.team-card').count() == 5
    offline.close()
    passed('standalone HTML completes a quiz with network and persistent storage unavailable')

    native = context.new_page()
    native.on('pageerror', lambda e: errors.append(str(e)))
    native.add_init_script('''window.__nativeCalls=[];window.xhs={miniTool:{getLaunchOptions:async()=>({miniToolEnv:{buildVersion:9490000}}),getStorage:async()=>({data:null}),setStorage:async o=>window.__nativeCalls.push(['set',o.key]),removeStorage:async()=>{},getWindowInfo:async()=>({windowHeight:852,safeArea:{top:24,bottom:818,left:0,right:393},menuButtons:{share:{bottom:64}}}),writeTempFile:async o=>{window.__nativeCalls.push(['temp']);return{filePath:'xhs-local-poster.png'}},saveImageToPhotosAlbum:async o=>window.__nativeCalls.push(['album',o.filePath])}};''')
    native.goto(base + '/dist/xhs/', wait_until='networkidle')
    native.wait_for_selector('.home-page')
    assert native.locator('.brand').bounding_box()['y'] >= 70
    native.locator('[data-count="8"]').click()
    native.locator('#app [data-action=start]').first.click()
    answer_rest(native)
    native.locator('[data-action=team-poster]').click()
    native.wait_for_selector('.poster-image')
    assert not native.evaluate('__nativeCalls.some(x=>x[0]==="album")')
    native.locator('[data-action=save-poster]').click()
    native.wait_for_function('__nativeCalls.some(x=>x[0]==="album")')
    assert native.evaluate('__nativeCalls.filter(x=>x[0]==="temp"||x[0]==="album").map(x=>x[0]).join(",")') == 'temp,album'
    passed('XHS SDK simulation avoids capsule and saves a temporary poster only after explicit user action')
    native.close()
    assert not errors, errors
    assert not failed, failed
    passed('no page exceptions or failed runtime resources')
    browser.close()
server.shutdown()
assert (ROOT / 'web/app.js').read_bytes() == (ROOT / 'dist/web/app.js').read_bytes(), 'Runtime changed after build'
report = {'status': 'passed', 'count': len(checks), 'checks': checks,
          'dataSHA256': hashlib.sha256((ROOT / 'content/data.json').read_bytes()).hexdigest(),
          'appSHA256': hashlib.sha256((ROOT / 'web/app.js').read_bytes()).hexdigest(),
          'device': '393×852 Chromium viewport emulation, not native or physical phone acceptance'}
(ROOT / 'docs/browser-check.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
