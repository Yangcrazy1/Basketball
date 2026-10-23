"""V4 standalone UI QA, served from an immutable snapshot on a random local port.

This validates the generated HTML, not a phone attachment-download service or an
Android installation. Run only after build.py has generated the intended version.
"""
from __future__ import annotations
from pathlib import Path
import base64
import hashlib
import http.server
import io
import json
import shutil
import sys
import tempfile
import threading
import time
from playwright.sync_api import sync_playwright
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / 'dist/parallel-self.html'
OUTPUT = ROOT / 'dist/qa-v4'
REPORT_PATH = ROOT / 'docs/v4-browser-check-results.json'
OUTPUT.mkdir(parents=True, exist_ok=True)
HTML_BYTES = HTML_PATH.read_bytes()
HTML = HTML_BYTES.decode('utf-8')
CHECKS: list[str] = []
ERRORS: list[str] = []
EXTERNAL: list[str] = []
CONTEXTS = []
CURRENT_PAGE = None
STARTED = time.time()


def passed(name: str) -> None:
    CHECKS.append(name)
    print('PASS', name, flush=True)


def no_overflow(page) -> None:
    width = page.evaluate('innerWidth')
    actual = page.evaluate('document.documentElement.scrollWidth')
    if actual > width:
        suspects = page.evaluate('''() => [...document.querySelectorAll('body *')]
          .map(e=>({tag:e.tagName,cls:String(e.className||''),right:Math.round(e.getBoundingClientRect().right)}))
          .filter(e=>e.right>innerWidth+1).slice(0,12)''')
        raise AssertionError(f'horizontal overflow {actual}>{width}, candidates={suspects}')


def ready(page) -> None:
    page.wait_for_function("document.documentElement.dataset.appReady === 'true'", timeout=12000)
    assert not page.locator('#startup-status').is_visible(), 'startup status stayed visible after appReady'
    assert page.locator('[data-action="start"]').count() == 1


def open_home(page) -> None:
    if page.locator('#modal').is_visible():
        page.locator('#close-modal').click()
    page.locator('#home-link').click()


def choose_mode(page, mode: str) -> None:
    page.locator(f'[data-action="mode"][data-mode="{mode}"]').click()


def begin(page) -> None:
    page.locator('[data-action="start"]').click()
    if page.locator('#modal').is_visible():
        page.locator('#modal [data-action="new-confirmed"]').click()


def point_answers(data: dict, total: int, point_for_index) -> list[int]:
    out = []
    for i, q in enumerate(data['questions'][:total]):
        point = point_for_index(i)
        raw = 5 - point if q.get('reverse') else point
        out.append(q.get('values', [1,2,3,4]).index(raw) + 1)
    return out


def finish(page, total: int, start: int = 0, choices: list[int] | None = None) -> None:
    for i in range(start, total):
        at = choices[i] - 1 if choices is not None else i % 4
        page.locator('[data-action="answer"]').nth(at).click()
        page.locator('[data-action="next"]').click()
    assert page.locator('.result-hero h1').count() == 1


def latest(page) -> dict:
    return page.evaluate("JSON.parse(localStorage.getItem('elsewhere.v4.sbti_latest_result'))")


def history(page) -> list:
    return page.evaluate("JSON.parse(localStorage.getItem('elsewhere.v4.run_history') || '[]')")


def check_record_against_ui(page) -> dict:
    record = latest(page)
    assert record and record['version'] == 4
    result = page.evaluate('''record=>window.ParallelEngine.analyze(record.answers, window.PARALLEL_DATA, record.mode)''', record)
    assert result['profile']['name'] in page.locator('.result-intro .pills').inner_text()
    assert page.locator('.tier.unlocked').count() == result['mode']['level']
    assert page.locator('.evidence-list article').count() == len(result['evidence'])
    for e in result['evidence']:
        assert e['option'] in page.locator('.evidence-list').inner_text()
    return result


def verify_visible_pixels(locator) -> None:
    pixels = Image.open(io.BytesIO(locator.screenshot())).convert('RGB')
    # A blank pastel placeholder with only rounded edges cannot satisfy this.
    colors = pixels.getcolors(pixels.width * pixels.height)
    assert colors and len(colors) > 160, 'reference image/avatar rendered blank'


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass


def make_page(browser, url: str, *, offline: bool = False, deny_storage: bool = False):
    global CURRENT_PAGE
    ctx = browser.new_context(viewport={'width':390,'height':844}, device_scale_factor=1,
                              reduced_motion='reduce', offline=offline, accept_downloads=True)
    CONTEXTS.append(ctx)
    if deny_storage:
        ctx.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw new Error('QA storage denied')}})")
    page = ctx.new_page()
    CURRENT_PAGE = page
    page.on('pageerror', lambda error: ERRORS.append(str(error)))
    page.on('request', lambda req: EXTERNAL.append(req.url) if not req.url.startswith((url.rsplit('/',1)[0]+'/', 'data:', 'blob:')) and req.url != 'about:blank' else None)
    if offline:
        page.goto('about:blank')
        page.set_content(HTML)
    else:
        page.goto(url)
    ready(page)
    return page


def report(status: str, failure: str | None = None) -> None:
    payload = {
        'version':4, 'status':status, 'html_sha256':hashlib.sha256(HTML_BYTES).hexdigest(),
        'html_bytes':len(HTML_BYTES), 'browser':'system Chromium / Playwright',
        'passed':len(CHECKS), 'failed':0 if status == 'passed' else 1, 'checks':CHECKS,
        'failure':failure, 'javascript_errors':ERRORS, 'external_requests':EXTERNAL,
        'duration_seconds':round(time.time()-STARTED,2),
        'delivery_not_verified':['physical phone installation','ChatGPT attachment export/download route','public HTTPS hosting'],
        'scope':'immutable generated HTML snapshot; random local HTTP port and offline about:blank rendering'
    }
    REPORT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2)+'\n')


def run(browser, url: str) -> None:
    page = make_page(browser, url)
    data = page.evaluate('window.PARALLEL_DATA')
    assert data['version'] == 4
    assert page.locator('.mode-card').count() == 3
    assert page.locator('.intent-picker [data-intent]').count() == 2
    assert page.locator('.mode-card.selected .mode-count').inner_text().replace(' ','') == '16题'
    passed('appReady is set, startup diagnostic hides, and three modes plus two intent views are available')

    for theme in ['lavender', 'mint']:
        page.locator(f'[data-theme-choice="{theme}"]').click()
        assert page.locator('html').get_attribute('data-theme') == theme
        for width in [320,390,430,768,1440]:
            page.set_viewport_size({'width':width,'height':844}); no_overflow(page)
        page.set_viewport_size({'width':390,'height':844})
    page.reload(); ready(page)
    assert page.locator('html').get_attribute('data-theme') == 'mint'
    page.locator('#toast').evaluate('(el)=>el.classList.remove("show")')
    page.screenshot(path=str(OUTPUT/'home-mobile.png'), full_page=True)
    passed('both themes persist and homepage has no overflow at 320/390/430/768/1440px')

    # References are checked for actual visible image pixels and a usable provenance URL.
    sourced = [p for p in data['characters'] if p.get('scene')]
    assert sourced, 'the final build has no sourced scene/portrait records'
    first = sourced[0]
    person_entry = page.locator(f'[data-action="person"][data-person="{first["id"]}"]').first
    if person_entry.count():
        person_entry.click()
    else:
        page.locator(f'[data-action="browse-world"][data-category="{first["category"]}"]').click()
        page.locator(f'#modal [data-action="person"][data-person="{first["id"]}"]').click()
    assert first['name'] in page.locator('#modal-title').inner_text()
    source = page.locator('.scene-provenance a')
    assert source.count() == 1 and source.get_attribute('href') == first['scene']['sourcePage']
    assert source.get_attribute('href').startswith('https://')
    verify_visible_pixels(page.locator('#modal .portrait').first)
    page.locator('#close-modal').click()
    passed('a sourced reference image renders visible pixels and its detail card retains the original source link')

    # All categories are checked against live build data instead of hard-coded old counts.
    for cat in data['categories']:
        page.locator(f'[data-action="browse-world"][data-category="{cat["id"]}"]').click()
        expected = [p for p in data['characters'] if p['category'] == cat['id']]
        assert page.locator('.library-item').count() == len(expected)
        page.locator('#role-search').fill(expected[0]['name'])
        matches = [p for p in expected if expected[0]['name'].lower() in (p['name']+' '+p['sub']).lower()]
        assert page.locator('.library-item').count() == len(matches)
        assert expected[0]['name'] in page.locator('#library-results').inner_text()
        page.locator('#role-search').fill('QA不存在的角色404')
        assert page.locator('.library-item').count() == 0 and page.locator('.empty-hint').count() == 1
        page.locator('#role-search').fill('')
        assert page.locator('.library-item').count() == len(expected)
        page.locator('#close-modal').click()
    passed('all world libraries show correct counts and search handles matches, empty state and clearing')

    favorite_person = data['characters'][next(i for i,p in enumerate(data['characters']) if p['id'] in data['featured'])]
    page.locator(f'[data-action="person"][data-person="{favorite_person["id"]}"]').first.click()
    page.locator('[data-action="favorite"]').click()
    assert '取消收藏' in page.locator('[data-action="favorite"]').inner_text()
    page.locator('#close-modal').click(); page.locator('#archive-link').click()
    assert page.locator(f'.featured-row [data-person="{favorite_person["id"]}"]').count() == 1
    page.reload(); ready(page); page.locator('#archive-link').click()
    page.locator(f'.featured-row [data-person="{favorite_person["id"]}"]').click()
    assert '取消收藏' in page.locator('[data-action="favorite"]').inner_text()
    page.locator('[data-action="favorite"]').click(); page.locator('#close-modal').click()
    assert favorite_person['id'] not in page.evaluate("JSON.parse(localStorage.getItem('elsewhere.v4.favorites')||'[]')")
    open_home(page)
    passed('favorite toggle is retained across reload and appears in the archive')

    choose_mode(page, 'quick'); begin(page)
    assert page.locator('progress').get_attribute('max') == '8'
    assert page.locator('[data-action="next"]').is_disabled()
    quick_choices = point_answers(data, 8, lambda _:1)
    page.locator('[data-action="answer"]').nth(quick_choices[0]-1).click()
    page.locator('[data-action="next"]').click(); page.locator('[data-action="previous"]').click()
    assert page.locator('[data-action="answer"]').nth(quick_choices[0]-1).get_attribute('aria-pressed') == 'true'
    page.reload(); ready(page); page.locator('[data-action="resume"]').click()
    assert page.locator('progress').get_attribute('value') == '1'
    assert page.locator('[data-action="answer"]').nth(quick_choices[0]-1).get_attribute('aria-pressed') == 'true'
    finish(page,8,choices=quick_choices)
    quick_record = latest(page); check_record_against_ui(page)
    assert quick_record['mode'] == 'quick' and quick_record['intent'] == 'self'
    assert page.locator('.tier.unlocked').count() == 1
    assert page.locator('.tier.locked').count() == 2
    passed('8-question self journey enforces completion, supports back/edit and reload resume, and unlocks only the first layer')

    page.locator('[data-action="upgrade"][data-mode="standard"]').click()
    session = page.evaluate("JSON.parse(localStorage.getItem('elsewhere.v4.sbti_test_session'))")
    assert session['answers'][:8] == quick_record['answers'] and session['index'] == 8
    assert session['baseline']['count'] == 8
    assert page.locator('progress').get_attribute('value') == '8'
    upgrade_choices = point_answers(data,16,lambda i:1 if i<8 else 4)
    finish(page,16,8,upgrade_choices)
    standard_record=latest(page); standard_result=check_record_against_ui(page)
    assert standard_record['answers'][:8] == quick_record['answers']
    assert page.locator('.upgrade-note').is_visible()
    assert '答案已保留' in page.locator('.upgrade-note').inner_text()
    assert page.locator('.tier.unlocked').count() == 2
    # A changed family is allowed and expected for this deliberate contradictory path.
    quick_result = page.evaluate('r=>ParallelEngine.analyze(r.answers,PARALLEL_DATA,r.mode)', quick_record)
    if quick_result['profile']['id'] != standard_result['profile']['id']:
        note=page.locator('.upgrade-note').inner_text()
        assert quick_result['profile']['name'] in note and standard_result['profile']['name'] in note
    passed('8→16 upgrade keeps actual answers and recalculates the family/subtype with an explicit update note')

    page.locator('[data-action="upgrade"][data-mode="deep"]').click()
    session = page.evaluate("JSON.parse(localStorage.getItem('elsewhere.v4.sbti_test_session'))")
    assert session['answers'][:16] == standard_record['answers'] and session['index'] == 16
    deep_choices=point_answers(data,24,lambda i:1 if i<8 else 4)
    finish(page,24,16,deep_choices)
    deep_record=latest(page); deep_result=check_record_against_ui(page)
    assert deep_record['answers'][:16] == standard_record['answers']
    assert page.locator('.tier.unlocked').count() == 3 and page.locator('.tier.locked').count() == 0
    assert page.locator('.role-trio .trio-card').count() == 2
    passed('16→24 upgrade adds the final branch and displays explainable evidence, contrast character and companion')

    for cat in data['categories']:
        page.locator('#tab-'+cat['id']).click()
        total=sum(p['category']==cat['id'] for p in data['characters'])
        assert page.locator('.match-item').count()==min(total,3)
        page.locator('summary').first.click(); assert '差异相对较大' in page.locator('details').first.inner_text()
        page.locator('[data-action="expand-matches"]').click()
        assert page.locator('.match-item').count()==total
        numbers=[int(v) for v in page.locator('.match-score b').all_text_contents()]
        assert numbers==sorted(numbers,reverse=True)
        page.locator('[data-action="expand-matches"]').click()
    last=data['categories'][-1]['id']; page.locator('#tab-'+last).press('Home')
    assert page.locator('#tab-'+data['categories'][0]['id']).get_attribute('aria-selected')=='true'
    passed('all result worlds support Top 3/full ranked lists, evidence and keyboard tab switching')

    before=latest(page); edit_at=3; old_value=before['answers'][edit_at]
    page.locator('[data-action="review"]').click()
    assert page.locator('.answer-review li').count()==24
    assert data['questions'][edit_at]['options'][old_value-1] in page.locator('.answer-review li').nth(edit_at).inner_text()
    page.locator(f'[data-action="edit-answer"][data-index="{edit_at}"]').click()
    assert page.locator('#question-title').inner_text()==data['questions'][edit_at]['title']
    new_value=old_value%4+1
    page.locator('[data-action="answer"]').nth(new_value-1).click()
    assert '更新' in page.locator('[data-action="next"]').inner_text()
    page.locator('[data-action="next"]').click()
    after=latest(page); changed=[i for i,(a,b) in enumerate(zip(before['answers'],after['answers'])) if a!=b]
    assert changed==[edit_at] and after['answers'][edit_at]==new_value
    check_record_against_ui(page)
    passed('review quotes actual choices and editing one question recomputes a full result without answering the rest again')

    for theme in ['lavender','mint']:
        page.locator(f'[data-theme-choice="{theme}"]').click()
        for width in [320,390,430,768,1440]:
            page.set_viewport_size({'width':width,'height':844}); no_overflow(page)
        page.set_viewport_size({'width':390,'height':844})
    page.locator('#toast').evaluate('(el)=>el.classList.remove("show")')
    page.screenshot(path=str(OUTPUT/'result-mobile.png'),full_page=True)
    passed('deep results fit both themes at 320/390/430/768/1440px without horizontal overflow')

    post_urls=[]
    for theme in ['mint','lavender']:
        page.locator(f'[data-theme-choice="{theme}"]').click(); page.locator('[data-action="poster"]').click()
        img=page.locator('.poster-img'); img.wait_for(timeout=20000)
        assert img.evaluate('(i)=>i.complete && i.naturalWidth===1080 && i.naturalHeight>=1600')
        src=img.get_attribute('src'); assert src.startswith('data:image/png;base64,');post_urls.append(src)
        (OUTPUT/f'identity-{theme}.png').write_bytes(base64.b64decode(src.split(',')[1]))
        if theme=='mint':
            with page.expect_download() as downloaded: page.locator('a[download]').click()
            downloaded.value.save_as(str(OUTPUT/'downloaded-identity.png'))
            image=Image.open(OUTPUT/'downloaded-identity.png')
            assert image.size[0]==1080 and image.size[1]>=1600
            assert len(set(image.convert('RGB').resize((150,200)).getdata()))>500
            page.locator('[data-action="share-poster"]').click()
            assert page.locator('#toast').is_visible()
        page.locator('#close-modal').click()
    assert post_urls[0]!=post_urls[1]
    passed('both themes generate distinct full PNG identity cards and an actual downloaded PNG opens successfully')

    # A sample remains separate from the stored run/history.
    before_last=latest(page);before_history=history(page)
    open_home(page);page.locator('[data-action="sample"]').click()
    assert page.locator('.sample-banner').is_visible()
    assert latest(page)==before_last and history(page)==before_history
    passed('sample results do not overwrite the latest result or append fake history')

    # Direct standard and deep entry validate both boundaries independently of upgrade.
    for mode,total,levels in [('standard',16,2),('deep',24,3)]:
        direct=make_page(browser,url)
        choose_mode(direct,mode);begin(direct)
        finish(direct,total)
        r=latest(direct); assert r['mode']==mode and len(r['answers'])==total
        check_record_against_ui(direct)
        assert direct.locator('.tier.unlocked').count()==levels
    passed('direct 16- and 24-question journeys finish at their own boundaries, independently of upgrades')

    # Ideal persona is another explicit intent; it must not be mislabeled as self.
    open_home(page);page.locator('[data-action="intent"][data-intent="ideal"]').click()
    choose_mode(page,'quick');begin(page);finish(page,8)
    assert latest(page)['intent']=='ideal'
    assert '理想人设' in page.locator('.result-topline').inner_text()
    page.locator('#archive-link').click()
    records=history(page)
    assert any(r['intent']=='self' for r in records) and any(r['intent']=='ideal' for r in records)
    assert page.locator('.history-card').count()==len(records)
    assert '理想人设' in page.locator('.history-list').inner_text() and '真实反应' in page.locator('.history-list').inner_text()
    page.locator('.history-card').first.click();assert '理想人设' in page.locator('.result-topline').inner_text()
    passed('self and ideal runs are saved and labeled separately in history and can be reopened')

    # Reloaded history and saved runs are independent of a currently displayed example.
    page.reload();ready(page);page.locator('#archive-link').click()
    assert page.locator('.history-card').count()>=4
    page.locator('.history-card').first.click();check_record_against_ui(page)
    passed('multiple recent records persist across a reload and reopen with engine-consistent results')

    corrupt=make_page(browser,url)
    for raw in ['[null,{},"bad"]', '{not-valid-json']:
        corrupt.evaluate("value=>localStorage.setItem('elsewhere.v4.run_history',value)", raw)
        corrupt.reload();ready(corrupt);corrupt.locator('#archive-link').click()
        assert corrupt.locator('.history-card').count()==0
        assert '还没有' in corrupt.locator('.archive-view').inner_text()
        open_home(corrupt);choose_mode(corrupt,'quick');begin(corrupt);finish(corrupt,8)
        assert len(history(corrupt))==1 and latest(corrupt)['mode']=='quick'
    passed('null/invalid history entries and malformed JSON are ignored without crashing, and a new run can still be saved')

    offline=make_page(browser,url,offline=True,deny_storage=True)
    assert offline.locator('.storage-warning').is_visible()
    sourced_id=sourced[0]['id']
    # At least one embedded source scene is visible offline; don't infer it from a URL alone.
    offline.locator(f'[data-action="person"][data-person="{sourced_id}"]').first.click()
    verify_visible_pixels(offline.locator('#modal .portrait').first)
    offline.locator('#close-modal').click()
    choose_mode(offline,'quick');begin(offline);finish(offline,8)
    offline.locator('[data-action="poster"]').click();offline.locator('.poster-img').wait_for(timeout=20000)
    assert offline.locator('.poster-img').evaluate('(i)=>i.complete && i.naturalWidth===1080')
    with offline.expect_download() as downloaded:offline.locator('a[download]').click()
    downloaded.value.save_as(str(OUTPUT/'offline-identity.png'))
    assert (OUTPUT/'offline-identity.png').read_bytes()[:8]==b'\x89PNG\r\n\x1a\n'
    passed('offline HTML with denied storage displays reference images, completes eight questions and downloads a real PNG')

    assert not ERRORS,ERRORS
    assert not EXTERNAL,EXTERNAL
    passed('all tested workflows complete without JavaScript errors or external HTTP dependencies')


def main() -> int:
    server=None
    try:
        with tempfile.TemporaryDirectory(prefix='parallel-v4-qa-') as directory:
            Path(directory,'index.html').write_bytes(HTML_BYTES)
            handler=lambda *args,**kwargs:QuietHandler(*args,directory=directory,**kwargs)
            server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler)
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            url=f'http://127.0.0.1:{server.server_address[1]}/index.html'
            print(f'Testing immutable V4 HTML ({len(HTML_BYTES):,} bytes, SHA256 {hashlib.sha256(HTML_BYTES).hexdigest()[:16]})',flush=True)
            with sync_playwright() as p:
                browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
                try:
                    run(browser,url)
                except Exception as error:
                    if CURRENT_PAGE is not None:
                        try:CURRENT_PAGE.screenshot(path=str(OUTPUT/'failure.png'),full_page=True)
                        except Exception:pass
                    report('failed',f'{type(error).__name__}: {error}')
                    raise
                finally:
                    browser.close()
        report('passed')
        print(f'{len(CHECKS)} V4 UI checks passed; report: {REPORT_PATH}',flush=True)
        return 0
    except Exception as error:
        print(f'FAIL {type(error).__name__}: {error}',file=sys.stderr,flush=True)
        return 1
    finally:
        if server:
            server.shutdown();server.server_close()

if __name__=='__main__':
    raise SystemExit(main())
