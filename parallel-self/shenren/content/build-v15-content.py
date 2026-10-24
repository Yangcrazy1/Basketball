"""Add the explicitly requested Kun collaboration to the frozen V14 runtime.

No legacy field, scoring input or story action is re-authored here. Run once the
content author freezes v15-kun-content.json; --assemble opts into the runtime write.
"""
from pathlib import Path
import argparse, copy, json

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'src/legacy-v13/data.json'
SOURCES={'caixukun':ROOT/'content/v15-kun-content.json','369':ROOT/'content/v15-369-content.json'}
DIMS=['social','explore','empathy','action','order','express']
PERSON=dict(id='basket-caixukun',personId='caixukun',theme='basket',name='蔡徐坤',nickname='坤坤',
    aliases=['蔡徐坤','坤坤','KUN','Cai Xukun','caixukun'],number='KUN',roles=[1,0,2],
    roleType='entertainer',basketballGroup='跨界整活',
    sub='唱跳舞台与篮球开场 / 跨界娱乐二创',line='前奏先别循环，五个人的球也得传起来。',
    vector=[88,82,68,90,80,98],
    behaviorWeights={'nba-show':5,'nba-train':5,'nba-three':4,'nba-team':3,'nba-plan':3,'nba-emotion':3},
    tier='normal',exposureWeight=1,spotlight=False,enabled=True,editorialStatus='selected',sourceStatus='indexed',
    universe={'title':'跨界练习生','arrival':'你穿过镜面，落在球馆侧边的排练区。球鞋旁摆着话筒，四个队友都在等这次开场。',
        'mission':'把练习动作排成能与队友接上的一场表演，别让前奏比比赛还长。',
        'passive':'听见节拍先踩准动作，球到了手上仍得抬头找队友。',
        'teamHook':'负责开场和加练的人：唱跳可以有个人镜头，篮球得五个人传。'})
PERSON_369=dict(id='lol-369',personId='369',theme='lol',name='369',nickname='369',
    aliases=['369','白家浩','Bai Jiahao','骰子上单'],number='369',roles=[0],
    roleType='player',sub='上路摇号与拉扯 / 平行宇宙二创',line='手气可以随机，练习和退路先自己安排。',
    vector=[50,50,65,65,70,60],behaviorWeights={'spin':5,'mechanics':4,'protect':3},
    tier='normal',exposureWeight=1,spotlight=False,enabled=True,editorialStatus='selected',sourceStatus='indexed',
    universe={'title':'上路摇号员','arrival':'你穿过镜面，落在网吧上路训练角。桌上的骰子、饮水杯和三脚椅都在等一次校准。',
        'mission':'把手气留给节目效果，把拉扯和练习变成可重复的动作。',
        'passive':'点数落下后先看看退路；再好的手气也替不了一次真正的练习。',
        'teamHook':'独守一路的人，也要记得五个人同在一张地图。'})

ART={
 'v15-caixukun-1':{'classicSprite':{'sheet':6,'cell':0},'artReason':'V15专图：练习闹钟与篮球。'},
 'v15-caixukun-2':{'classicSprite':{'sheet':6,'cell':1},'artReason':'V15专图：麦克风、耳机、运动鞋与篮球，对应四项舞台技能。'},
 'v15-caixukun-3':{'classicSprite':{'sheet':6,'cell':2},'artReason':'V15专图：灰背带裤、篮球和音符，对应出镜造型与循环副歌。'},
 'v15-369-1':{'classicSprite':{'sheet':6,'cell':3},'artReason':'V15专图：三颗分别呈现3、6、9的骰子，直接对应摇点数。'},
 'v15-369-2':{'classicSprite':{'sheet':6,'cell':4},'artReason':'V15专图：电竞椅、充电线与走位箭头，对应进退拉扯。'},
 'v15-369-3':{'classicSprite':{'sheet':6,'cell':5},'artReason':'V15专图：酒桶饮水机与练习书，对应酒桶动作补习。'},
}

def load(path):return json.loads(path.read_text())
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def compile_addition(base,raw,pid='caixukun'):
    p=copy.deepcopy(PERSON if pid=='caixukun' else PERSON_369)
    theme=p['theme']
    # The author tied these values to the actual four question behaviors. Identity,
    # grouping and normal exposure remain explicit migration-owned metadata.
    for key in ['vector','behaviorWeights','line']:
        if key in raw.get('person',{}):p[key]=copy.deepcopy(raw['person'][key])
    p.update(rosterOrder=max(x['rosterOrder'] for x in base['characters'])+1+(1 if pid=='369' else 0),answerAffinities={},optionAffinities={})
    p['parallelStory']=[p['nickname']+'，你已穿过镜面。',p['universe']['arrival'],'这一次的开场，由你和四位队友一起完成。']
    cards=copy.deepcopy(raw['cards']);questions=copy.deepcopy(raw['questions']);story=copy.deepcopy(raw['story'])
    assert len(cards)==3 and {c['id'] for c in cards}=={f'v15-{pid}-{i}' for i in range(1,4)}
    assert len({c['name'] for c in cards})==3
    by_name={c['name']:c for c in cards}
    existing_names={c['name'] for arr in base['augments'].values() for c in arr}
    assert not (set(by_name)&existing_names)
    for c in cards:
        c.update(theme=theme,owners=[pid],owner=pid,signatureFor=[pid],affinities=[pid],
            exclusive=True,personOnly=True,enabled=True,selected=True,editorialStatus='selected',
            activationMode='answers',category='人物代表',fanMade=True,rarity='kPrismatic',kind='chaos' if theme=='lol' else 'team',
            vector=p['vector'][:],bias=[round((v-50)/50,2) for v in p['vector']],
            behaviorWeights={},requires=[],evidenceQuestionIds=[],answerEvidence=[],preferClassic=True)
        c.setdefault('icon',0);c.setdefault('sourceMeme',c['name']);c.setdefault('adaptation','adaptation')
        c.setdefault('sources',[]);c['originalVideoWatched']=False
        c.setdefault('sourceStatus','indexed' if c['sources'] else 'pending')
        for source in c['sources']:
            source.update(status='indexed',originalVideoWatched=False)
        if pid=='369':
            evidence=next(item for item in load(ROOT/'content/v15-369-source-notes.json')['sources'] if item['cardName']==c['name'])
            c['sourceStatus']='partial_context_only' if evidence['status']=='partial_context_only' else 'indexed'
            c['sourceVerificationNote']=evidence['note']
            if evidence['status']=='partial_context_only':
                c['sources']=[{'title':evidence['sourceTitle'],'url':evidence['url'],'status':'partial_context_only',
                    'contextOnly':True,'originalVideoWatched':False,'note':evidence['note']}]
                c['sourceMeme']='公开报道中的999状态称呼背景；摇骰子机制为本作原创，直接原梗出处未确认。'
                c['adaptation']='original'
                c['creation']='依据999状态比喻设计的原创骰子机制；未确认摇骰子直接原出处，不是本人原话。'
            else:
                c['sources']=[dict(item,status='indexed',originalVideoWatched=False) for item in evidence['references']]

        c.setdefault('creation','本作基于公开流行梗创作的虚构效果，不是人物原话或现实职业履历。')
        c.setdefault('line',c['punchline'])
        c.pop('visual',None);c.pop('artAsset',None);c.update(ART[c['id']])
    assert len(questions)==4 and len({q['id'] for q in questions})==4
    if theme!='lol':assert len({q['dim'] for q in questions})==4
    else:assert sorted(q['stage'] for q in questions)==[0,1,2,3]
    known_behaviors=set(base['behaviorLabels'])
    for q in questions:
        assert q.get('personId',pid)==pid
        q.update(theme=theme,personId=pid,personContext=pid,enabled=True,importance=1.25,
            editorialCategory='life',review={'status':'v15_authored','reason':'从具体情境行动触发代表卡，不把人物名当答案。'})
        if theme!='lol':assert q['dim'] in DIMS
        else:q.update(series='rift',chapter='v15-369',chapterName='网吧日常 · '+next(item['scene'] for item in questions if item['stage']==0))
        assert len(q['options'])==4 and {o['id'] for o in q['options']}==set(range(4))
        for o in q['options']:
            assert o['behavior'] in known_behaviors
            if theme!='lol':assert o['behavior'].startswith('nba-') and 1<=o['value']<=4
            else:assert set(o['signals'])=={'tilt','greed','risk','team','craft','plan'}
            o['tags']=[o['behavior']]
            for name in o.get('cardNames',[]):
                assert name in by_name,(q['id'],name)
                c=by_name[name]
                c['behaviorWeights'][o['behavior']]=5;c['evidenceQuestionIds'].append(q['id'])
                c['answerEvidence'].append({'questionId':q['id'],'optionId':o['id'],'behavior':o['behavior']})
                p['optionAffinities'].setdefault(q['id'],{})[str(o['id'])]=5
                p['answerAffinities'].setdefault(q['id'],{})[o['behavior']]=5
    p['signaturePerks']=[c['id'] for c in cards];p['tags']=[c['name'] for c in cards]
    def ids(names):
        assert all(name in by_name for name in names),names
        return [by_name[name]['id'] for name in names]
    story.update(id=f'v15-story-{pid}',personId=pid,theme=theme,status='authored',fanMade=True)
    story['cardIds']=ids(story.get('cardNames',p['tags']))
    assert len(story['nodes'])==6
    node_ids={n['id'] for n in story['nodes']};assert len(node_ids)==6 and story['entry'] in node_ids
    for n in story['nodes']:
        n.setdefault('type','choice' if n.get('choices') else 'ending' if n['id']=='ending' else 'scene')
        if n.get('next'):assert n['next'] in node_ids
        for choice in n.get('choices',[]):
            choice['grantCardIds']=ids(choice.get('grantCardNames',[]));assert choice['next'] in node_ids
        for event in n.get('cardEvents',[]):
            event['cardId']=ids([event['cardName']])[0]
            assert isinstance(event['owned'],str) and isinstance(event['unowned'],str)
    for c in cards:
        c['evidenceQuestionIds']=list(dict.fromkeys(c['evidenceQuestionIds']))
        assert len(c['evidenceQuestionIds'])>=2,c['name']
        c['requires']=list(c['behaviorWeights'])
        c['behaviorRules']={'mode':'answers','behaviors':c['requires'],'questionIds':c['evidenceQuestionIds'],
            'owners':[pid],'note':'只有明确关联该卡的本题选项可作证据；同类行为在无关题不算，故事奖励另记。'}
        c['storyRewardIds']=[story['id']] if any(c['id'] in choice.get('grantCardIds',[]) for n in story['nodes'] for choice in n.get('choices',[])) else []
    return {'release':15,'schema':14,'person':p,'cards':cards,'story':story,'questions':questions,
        'notes':raw.get('notes',[]),'sourceFile':str(SOURCES[pid].relative_to(ROOT))}

def assemble(base,patches):
    data=copy.deepcopy(base)
    assert base['version']==13 and base['releaseVersion']==14
    assert not any(p['personId'] in {'caixukun','369'} for p in base['characters'])
    for index,patch in enumerate(patches):
        patch['person']['rosterOrder']=max(p['rosterOrder'] for p in base['characters'])+index+1
        data['characters'].append(patch['person']);data['questions'].extend(patch['questions'])
        data['augments'][patch['person']['theme']].extend(patch['cards']);data['branchStories'].append(patch['story'])
        data['representativeCatalog'].extend({'id':c['id'],'name':c['name'],'owners':c['owners']} for c in patch['cards'])
    launch=(ROOT/'content/v15-launch-copy.md').read_text()
    description=launch.split('发布介绍：',1)[1].strip().split('\n\n',1)[0]
    assert description and not any(term in description for term in ['V15','60人','340题'])
    data.update(version=14,releaseVersion=15,name='平行宇宙的另一个我',description=description,edition='V15坤坤与369联动',
        releaseNote='篮球梦之队新增跨界娱乐角色蔡徐坤，联盟新增369：各3张代表海克斯、4道新情境题与可回溯穿越故事。')
    data['migration'].update(legacySchema=13,nativeSchema=14,release=15)
    data['augmentData'].update(representativeCards=143,representativeAssociations=149)
    counts=data['counts'];counts.update(questions=340,lolQuestions=140,lolChapters=35,people=60,parodyCards=180,
        representativeCards=143,representativeAssociations=149,exclusiveCards=143,stories=60,lolParodyCards=86)
    counts['byTheme']['basket'].update(questions=108,people=21,cards=51,exclusiveCards=48)
    counts['byTheme']['lol'].update(questions=140,people=22,cards=86,exclusiveCards=55)
    assert len(data['questions'])==340 and len(data['characters'])==60 and len(data['branchStories'])==60
    assert sum(len(c) for c in data['augments'].values())==180
    return data


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--assemble',action='store_true');args=parser.parse_args()
    base=load(BASE);patches=[compile_addition(base,load(source),pid) for pid,source in SOURCES.items()]
    for pid,patch in zip(SOURCES,patches):write(ROOT/f'content/v15-{"kun" if pid=="caixukun" else pid}.json',patch)
    if args.assemble:write(ROOT/'src/data.json',assemble(base,patches))
    print(json.dumps({'people':['caixukun','369'],'cards':6,'questions':8,'stories':2,'runtimeWritten':args.assemble}))

if __name__=='__main__':main()
