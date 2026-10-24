"""Compile the supplied V14 editorial spec. No runtime writes without --assemble.

The frozen schema-12 data is the migration source; the document owns the active
roster, representative names and effects. Sources are indexed, never marked watched.
"""
from pathlib import Path
import argparse, copy, hashlib, json, re

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / 'docs/v14-user-spec.md'
OUT = ROOT / 'content/v14-catalog.json'
THEMES = ['lol', 'basket', 'abstract']
DIMS = ['social', 'explore', 'empathy', 'action', 'order', 'express']
LOL_DIMS = ['tilt', 'greed', 'risk', 'team', 'craft', 'plan']
# Reuse only cards whose previous effect already implements the same meme mechanic.
REUSE = {'这波不亏': 'not-a-loss', '二段笑': 'double-laugh',
         '向前闪现': 'v11-jackeylove-1', '切屏狂魔': 'v11-faker-3',
         '琴女空大': 'v11-xiaoxiao-1', '全体起立': 'v11-luobenwei-3',
         '后撤步': 'stepback-route', '汉堡王': 'v13-doncic-1',
         'Are You OK': 'personal-leijun', '对视艺术': 'v11-yaoshuige-1'}
SHARED = {'抗韩中年人', '快推啊', '好果汁', '东北往事', '金角银角', '双角出征'}
NEW_PEOPLE = {
 'draymond-green': dict(name='德雷蒙德·格林', nickname='格林', aliases=['德雷蒙德·格林','格林','追梦','Draymond Green','draymond-green'],
   theme='basket', roles=[3,4], vector=[88,65,63,87,75,95], number='DG',
   behaviorWeights={'nba-show':5,'nba-team':4,'nba-emotion':4,'nba-plan':3},
   sub='公式、边线与播客 / 平行宇宙二创', line='暂停牌举得快，播客麦也没关。'),
 'ershu': dict(name='恶鼠', nickname='恶鼠', aliases=['恶鼠','张梓祎','Ershu','ershu'],
   theme='basket', roles=[0,1,2], vector=[86,86,65,93,63,91], number='ES',
   behaviorWeights={'nba-show':5,'nba-drive':4,'nba-plan':3,'nba-team':3},
   sub='跨规则挑战 / 平行宇宙二创', line='先把这局规则写清楚，再问哪个场子见。'),
}

def read_json(path):
    return json.loads(path.read_text())

def base_data():
    frozen = ROOT / 'src/legacy-v12/data.json'
    return read_json(frozen if frozen.exists() else ROOT / 'src/data.json')

def catalog():
    text = SPEC.read_text()
    active = text.split('## 4.',1)[1].split('## 5.',1)[0]
    people, cards, by_name = [], [], {}
    theme = None
    current = None
    for line in active.splitlines():
        if line.startswith('### 联盟'): theme = 'lol'
        elif line.startswith('### 篮球'): theme = 'basket'
        elif line.startswith('### 抽象'): theme = 'abstract'
        m = re.match(r'#### (.+)（([^）]+)）', line)
        if m:
            current = {'personId':m[2], 'displayName':m[1], 'theme':theme,
                       'representativeCardIds':[], 'representativeCardNames':[]}
            people.append(current)
        m = re.match(r'- \*\*(.+)〔([梗改创])〕\*\*：(.+)', line)
        if m:
            assert current and theme, line
            name, kind, effect = m.groups()
            if name not in by_name:
                card_id = REUSE.get(name, 'v14-perk-' + hashlib.sha1(name.encode()).hexdigest()[:10])
                c = dict(id=card_id, name=name, theme=theme, owners=[], effect=effect,
                         sourceMeme=name, adaptation={'梗':'meme','改':'adaptation','创':'original'}[kind],
                         enabled=True, editorialStatus='selected', fanMade=True,
                         sourceStatus='pending', sources=[], originalVideoWatched=False)
                if name in REUSE: c['reusedFromV13'] = card_id
                cards.append(c); by_name[name] = c
            c = by_name[name]
            assert c['theme'] == theme and c['effect'] == effect, name
            c['owners'].append(current['personId'])
            current['representativeCardIds'].append(c['id'])
            current['representativeCardNames'].append(name)
        if line.startswith('**故事方向：**'):
            current['storyOutline'] = line.split('**故事方向：**',1)[1].strip()
    sources = text.split('## 附录B.',1)[1]
    for line in sources.splitlines():
        if not line.startswith('| '): continue
        columns = [x.strip() for x in line.strip('|').split('|')]
        if len(columns) < 2: continue
        name = columns[0].split('／')[-1]
        if name not in by_name: continue
        c = by_name[name]
        for url in re.findall(r'\]\((https?://[^)]+)\)', columns[1]):
            if not any(s['url'] == url for s in c['sources']):
                c['sources'].append({'url':url,'status':'indexed','originalVideoWatched':False})
    for c in cards:
        c['sourceStatus'] = 'indexed' if c['sources'] else 'original_fan_creation' if c['adaptation']=='original' else 'pending'
        c['selected'] = True
    by_display = {p['displayName']:p['personId'] for p in people}
    candidates = []
    inactive = text.split('## 5.',1)[1].split('## 6.',1)[0]
    for line in inactive.splitlines():
        if not line.startswith('| '): continue
        col = [x.strip() for x in line.strip('|').split('|')]
        if len(col)!=3 or col[0] not in by_display: continue
        pid,name,reason = by_display[col[0]],col[1],col[2]
        existing = next((c for c in candidates if c['name']==name),None)
        if existing: existing['owners'].append(pid); continue
        candidates.append(dict(id='v14-candidate-'+hashlib.sha1(name.encode()).hexdigest()[:10],name=name,
            owners=[pid],theme=next(p['theme'] for p in people if p['personId']==pid),
            enabled=False,selected=False,editorialStatus='not_selected',sourceStatus='pending',reason=reason,fanMade=True))
    assert len(people)==58 and len(cards)==137, (len(people),len(cards))
    assert sum(len(c['owners']) for c in cards)==143
    assert {c['name'] for c in cards if len(c['owners'])>1} == SHARED
    assert [sum(p['theme']==t for p in people) for t in THEMES]==[21,20,17]
    return dict(schemaVersion=13,releaseVersion=14,spec='docs/v14-user-spec.md',
        counts={'people':58,'representativeCards':137,'representativeAssociations':143,'sharedCards':6,
                'candidateCards':len(candidates)},people=people,representatives=cards,candidates=candidates,
        provenanceNotice='附录B公开链接仅编入索引，未自动认定观看原片或确认原话；卡片效果与故事均为本作二创。')


def compile_story(raw, by_name, active):
    story=copy.deepcopy(raw)
    assert story['personId'] in active
    assert len(story['nodes'])==6, story['id']
    own=story['personId']
    node_ids={n['id'] for n in story['nodes']}
    assert len(node_ids)==6 and story['entry'] in node_ids
    def card_ids(names):
        ids=[]
        for name in names:
            assert name in by_name, (story['id'],name)
            assert own in by_name[name]['owners'], (story['id'],'foreign representative reward',name)
            ids.append(by_name[name]['id'])
        return ids
    story['cardIds']=card_ids(story.get('cardNames',[]))
    for n in story['nodes']:
        n.setdefault('type','choice' if n.get('choices') else 'ending' if n['id']=='ending' else 'scene')
        if n.get('next'): assert n['next'] in node_ids
        for c in n.get('choices',[]):
            c['grantCardIds']=card_ids(c.get('grantCardNames',[]))
            assert c['next'] in node_ids
        for event in n.get('cardEvents',[]):
            event['cardId']=card_ids([event['cardName']])[0]
            assert isinstance(event['owned'],str) and isinstance(event['unowned'],str)
    story['status']='authored';story['fanMade']=True
    return story


def assemble(cat, allow_partial=False):
    data=copy.deepcopy(base_data())
    active={p['personId']:p for p in cat['people']}
    old_people={p['personId']:p for p in data['characters']}
    old_cards={c['id']:c for arr in data['augments'].values() for c in arr}
    old_questions=data['questions']
    art={v['id']:v for v in read_json(ROOT/'content/v14-art-map.json')['cards']}
    sheet_count=len(read_json(ROOT/'assets/rich-perk-atlases.json'))
    characters=[]
    for index,spec in enumerate(cat['people']):
        pid=spec['personId']; p=copy.deepcopy(old_people.get(pid,NEW_PEOPLE.get(pid)))
        assert p, pid
        p.update(id=spec['theme']+'-'+pid,personId=pid,theme=spec['theme'],enabled=True,
            signaturePerks=spec['representativeCardIds'],tags=spec['representativeCardNames'],
            rosterOrder=index,answerAffinities={},optionAffinities={},storyOutline=spec['storyOutline'],
            editorialStatus='selected',sourceStatus='indexed',
            universe={'title':spec['representativeCardNames'][0]+'宇宙','arrival':spec['storyOutline'],
                'mission':'把这场普通日常亲自演到结局。','passive':'代表海克斯仅在真实获得后触发。',
                'teamHook':'本作平行宇宙娱乐角色，不以阵容虚构现实履历。'},
            parallelStory=[(p.get('nickname') or p['name'])+'，你已穿过镜面。',spec['storyOutline'],'在「我的穿越故事」里选一条路线，让下一幕真正改变。'])
        p.setdefault('nickname',p['name']); p.setdefault('aliases',[p['name']]);p.setdefault('tier','normal')
        p.setdefault('exposureWeight',4);p.setdefault('spotlight',False)
        # Search aliases are identity-only; obsolete card labels must not leak back as tags.
        old_labels={c['name'] for c in old_cards.values() if pid in c.get('signatureFor',[]) or c.get('owner')==pid}
        p['aliases']=[a for a in p['aliases'] if a not in old_labels]
        p['aliases']=list(dict.fromkeys([p['name'],p['nickname']]+p['aliases']))
        characters.append(p)
    persons={p['personId']:p for p in characters}
    cards=[];by_name={}
    for spec in cat['representatives']:
        c=copy.deepcopy(spec); owners=c['owners']
        c.update(owner=owners[0] if len(owners)==1 else None,signatureFor=owners[:],affinities=owners[:],
                 exclusive=True,personOnly=True,activationMode='answers',category='人物代表',
                 kind='chaos' if c['theme']=='lol' else 'team',rarity='kPrismatic',icon=0,
                 triggerScene='答题时选择了直接关联「'+c['name']+'」的行动，或故事中明确获得该卡。',
                 creation='人物核心梗为公开线索索引；以上效果、虚构台词及故事由本作重新创作，不是本人原话。',
                 punchline=c['effect'].split('。')[-2]+'。' if '。' in c['effect'] else c['effect'],
                 preferClassic=True,classicSprite=art[c['id']]['proposedSprite'] if art[c['id']].get('proposedSprite',{}).get('sheet',999)<sheet_count else art[c['id']]['classicSprite'],
                 artReason=art[c['id']]['reason'],behaviorWeights={},requires=[],evidenceQuestionIds=[],answerEvidence=[])
        c['line']=c['punchline']
        c['vector']=[round(sum(persons[owner]['vector'][i] for owner in owners)/len(owners)) for i in range(6)]
        c['bias']=[round((v-50)/50,2) for v in c['vector']]
        cards.append(c);by_name[c['name']]=c
    # Only the audited V13 common cards survive. Collector is intentionally a common
    # recurring scene despite its old owner metadata; its five real icons and text stay exact.
    common=[]
    for c in old_cards.values():
        if c.get('enabled') is False: continue
        if (not c.get('owner') and not c.get('exclusive')) or c['id']=='collector-union':
            item=copy.deepcopy(c)
            item.update(enabled=True,selected=True,editorialStatus='preserved_common',sourceStatus='legacy_preserved')
            item['owners']=[]
            if item['id']=='collector-union':
                item.update(owner=None,personOnly=False,exclusive=False,signatureFor=[],category='通用整活')
            item['affinities']=[pid for pid in item.get('affinities',[]) if pid in active]
            item['signatureFor']=[pid for pid in item.get('signatureFor',[]) if pid in active]
            common.append(item)
    # Broader V13 behavior IDs now share semantically matching common backup cards.
    expansions={'shot-retry':['nba-spin','nba-free'], 'court-replay':['nba-color','nba-snack','nba-record'],
        'street-pass':['nba-call'], 'camera-day':['web-cook','web-launch','web-pitch','web-build','web-compute'],
        'route-friend':['web-duo-nida','web-duo-yili'],'meme-share':['web-win']}
    for c in common:
        for b in expansions.get(c['id'],[]): c.setdefault('behaviorWeights',{})[b]=4
    # Keep simple, reviewed game/day-to-day common chapters; new personal chapters
    # replace all previous personal question sets. Do not splice stages of a chapter.
    approved_chapters={'collector','collector-audit','table','office','review','netcafe','mic','boss',
        'golden-time','six-swords','brush','snowball-return','worlds-party','lane-basics','look-map',
        'skin-vote','collector-pact','rematch','noodles','clip','duo','jungle-date'}
    generic=[copy.deepcopy(q) for q in old_questions if q.get('enabled',True) and q['theme']=='lol' and q.get('chapter') in approved_chapters]
    for theme in ['basket','abstract']:
        for dim in DIMS:
            bank=[q for q in old_questions if q.get('enabled',True) and q['theme']==theme and q.get('dim')==dim and re.match(r'^(basket|abstract)-[a-z]+-[0-9]+$',q['id'])]
            generic.extend(copy.deepcopy(bank[:4]))
    for q in generic:
        q['review']={'status':'retained_common','reason':'保留经过审核的通用情境；旧人物专属题已归档。'}
    stories=[];new_questions=[];seen_stories=set()
    for theme in THEMES:
        f=ROOT/f'content/v14-stories-{theme}.json'
        if not f.exists(): continue
        authored=read_json(f)
        for raw in authored['stories']:
            assert raw['personId'] not in seen_stories
            stories.append(compile_story(raw,by_name,active));seen_stories.add(raw['personId'])
        for raw in authored['questions']:
            q=copy.deepcopy(raw); pid=q['personId']; assert pid in active
            q.update(enabled=True,personContext=pid,importance=1.25,
                editorialCategory='life',review={'status':'v14_authored','reason':'按人物核心梗创作日常行动，显式记录每个选项与代表卡的关系。'})
            if theme=='lol':
                order=next(i for i,p in enumerate(cat['people']) if p['personId']==pid)
                q.update(series='hex' if order%2 else 'rift',chapter='v14-'+pid,
                    chapterName='网吧日常 · '+next(item.get('scene','镜面来客') for item in authored['questions'] if item['personId']==pid and item.get('stage')==0))
                q.setdefault('tip','本作架空日常，不考职业术语；按你当下会做的动作选择。')
            else:
                assert q['dim'] in DIMS
            assert len(q['options'])==4 and len({o['id'] for o in q['options']})==4
            for o in q['options']:
                if theme=='lol': assert set(o['signals'])==set(LOL_DIMS)
                else: assert 1<=o['value']<=4
                o['tags']=[o['behavior']]
                names=o.get('cardNames',[])
                pfit=0
                for name in names:
                    assert name in by_name,(q['id'],name)
                    c=by_name[name]
                    assert c['theme']==theme
                    c['behaviorWeights'][o['behavior']]=5
                    c['evidenceQuestionIds'].append(q['id'])
                    c['answerEvidence'].append({'questionId':q['id'],'optionId':o['id'],'behavior':o['behavior']})
                    for owner in c['owners']:
                        persons[owner]['optionAffinities'].setdefault(q['id'],{})[str(o['id'])]=5
                        persons[owner]['answerAffinities'].setdefault(q['id'],{})[o['behavior']]=5
                    if pid in c['owners']: pfit=5
                persons[pid]['answerAffinities'].setdefault(q['id'],{}).setdefault(o['behavior'],pfit)
                if o['behavior'] not in data['behaviorLabels']:
                    data['behaviorLabels'][o['behavior']]=o['behavior']
            new_questions.append(q)
    pending=[pid for pid in active if pid not in seen_stories]
    if not allow_partial:
        assert not pending, ('missing stories',pending)
        assert len(new_questions)==232, len(new_questions)
        assert all(sum(q['personId']==pid for q in new_questions)==4 for pid in active)
    for c in cards:
        c['evidenceQuestionIds']=list(dict.fromkeys(c['evidenceQuestionIds']))
        c['requires']=list(c['behaviorWeights'])
        c['behaviorRules']={'mode':'answers','behaviors':c['requires'],'questionIds':c['evidenceQuestionIds'],
            'owners':c['owners'],
            'note':'只有明确关联该卡的本题选项可作证据；同一行为在无关题不算。故事奖励另记。'}
        c['storyRewardIds']=list(dict.fromkeys(s['id'] for s in stories if any(c['id'] in choice.get('grantCardIds',[]) for n in s['nodes'] for choice in n.get('choices',[]))))
    if not allow_partial:
        assert all(c['answerEvidence'] or c['storyRewardIds'] for c in cards), 'Representative card without a real trigger'
    questions=generic+new_questions
    assert len({q['id'] for q in questions})==len(questions)
    for c in common:
        if c.get('evidenceQuestionIds'):
            ids=[id for id in c['evidenceQuestionIds'] if any(q['id']==id for q in questions)]
            c['evidenceQuestionIds']=ids
            if c.get('behaviorRules'):c['behaviorRules']['questionIds']=ids
    # Original common cards predate the explicit theme field.
    runtime_cards={t:[c for c in cards if c['theme']==t]+[dict(c,theme=t) for c in common if c['id'] in {x['id'] for x in data['augments'][t]}] for t in THEMES}
    archived={'questions':[dict(q,enabled=False) for q in old_questions if q['id'] not in {x['id'] for x in generic}],
        'cards':[dict(c,enabled=False,editorialStatus='archived_v13') for c in old_cards.values() if c['id'] not in {x['id'] for x in cards+common}]}
    (ROOT/'content/v14-archived-review.json').write_text(json.dumps(archived,ensure_ascii=False,indent=2)+'\n')
    data.update(version=13,releaseVersion=14,edition='V14 · 核心梗与分支故事',
        releaseNote='58人 / 137代表海克斯 / 三主题可回溯分支故事；旧存档冻结保留。',
        characters=characters,questions=questions,augments=runtime_cards,branchStories=stories,
        representativeCatalog=[{'id':c['id'],'name':c['name'],'owners':c['owners']} for c in cards],reviewCatalog={'candidates':cat['candidates']},
        archivedContent={'reviewArchive':'content/v14-archived-review.json','questionCount':len(archived['questions']),'cardCount':len(archived['cards'])},
        migration={'legacySchema':12,'nativeSchema':13,'release':14,'pendingStoryPersonIds':pending,
                   'sourceStatusNotice':cat['provenanceNotice']})
    data['themes'][1]['description']='NBA / 中国篮球 / 街球 / 解说名场面'
    data['themes'][2]['description']='带篮子 / 刀哥 / 峰哥 / 科技名人 / 网络整活'
    data['augmentData'].update(representativeCards=137,representativeAssociations=143)
    data['counts']={'questions':len(questions),'lolQuestions':sum(q['theme']=='lol' for q in questions),
        'lolChapters':len({q['chapter'] for q in questions if q['theme']=='lol'}),'people':58,
        'parodyCards':len(cards)+len(common),'representativeCards':137,'representativeAssociations':143,
        'exclusiveCards':sum(c.get('exclusive',False) for c in cards+common),
        'lolParodyCards':len(runtime_cards['lol']),'stories':len(stories),
        'byTheme':{t:{'questions':sum(q['theme']==t for q in questions),'people':sum(p['theme']==t for p in characters),
            'cards':len(runtime_cards[t]),'exclusiveCards':sum(c.get('exclusive',False) for c in runtime_cards[t])} for t in THEMES}}
    return data


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--assemble',action='store_true',help='Explicitly replace src/data.json after all story workers finish')
    parser.add_argument('--allow-partial',action='store_true',help='Temporary UI integration only; final release forbids missing stories')
    args=parser.parse_args()
    cat=catalog(); OUT.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n')
    if args.assemble:
        data=assemble(cat,args.allow_partial)
        (ROOT/'src/data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(cat['counts'],ensure_ascii=False))

if __name__=='__main__': main()
