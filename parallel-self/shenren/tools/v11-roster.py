"""One-time V10 → V11 roster migration. Historical definitions remain immutable."""
from pathlib import Path
import json,shutil
R=Path(__file__).resolve().parents[1]
def save(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
legacy=R/'src/legacy';legacy.mkdir(exist_ok=True)
for name in ['data.json','engine.js']:
    if not (legacy/name).exists(): shutil.copy2(R/'src'/name,legacy/name)
D=json.loads((legacy/'data.json').read_text())
rosters={
 'lol':['uzi','xiaohu','jackeylove','theshy','vincent','rookie','faker','xiaoxiao','xika','pdd','dasima','clearlove','ning','kid','luobenwei','baolan','otto','zztai','doinb','ming'],
 'basket':['lebron','durant','jordan','kobe','yangyi','xujingyu','zhouqi','yaoming','curry','harden'],
 'abstract':['dailanzi','fengge','daoge','huge','huchenfeng','us-lecturer','sunxiaochuan','yaoshuige','leijun','luoyonghao']}
featured=['uzi','xiaohu','jackeylove','theshy','faker','dasima','pdd','luobenwei','lebron','durant','jordan','kobe','curry','yaoming','dailanzi','fengge','daoge','huge','huchenfeng','us-lecturer']
new=[
 ('vincent','文森特','lol',[3],[65,88,90,24,90,40],{'mechanics':5,'gold':4,'collector':4,'engage':3},['德莱文','双斧','网吧','接单'],'双斧一转，网吧老板开始确认余额。'),
 ('kid','Kid','lol',[1,3],[40,55,45,80,60,85],{'plan':5,'protect':4,'reset':3,'vision':4},['小孩游神','老IG','打野','熟人局'],'老队友点个名，回忆录先开一页。'),
 ('us-lecturer','美国讲师','abstract',[2,4],[68,55,78,65,88,76],{'abs-route':5,'abs-observe':4,'abs-care':3},['丁胖子金牌讲师','美国讲师','饭点','补给','路线'],'先把午饭路线讲明白，再研究人生下一站。'),
 ('yaoshuige','药水哥','abstract',[3,4],[48,76,50,55,30,90],{'abs-deadpan':5,'abs-loop':5,'abs-meme':3},['对视','复读','沉默','节目效果'],'你等我开口，我等你先笑。')]
for pid,name,t,roles,vector,beh,tags,line in new:
 D['characters'].append(dict(id=t+'-'+pid,personId=pid,theme=t,name=name,nickname=name,sub='本作娱乐设定 / '+('联盟主播' if t=='lol' else '互联网人物'),roles=roles,vector=vector,behaviorWeights=beh,tags=tags,line=line,signaturePerks=[],number=len(D['characters'])+1))
aliases={'uzi':['污渍','Uzi'],'xiaohu':['销户','小虎'],'jackeylove':['哥哥','阿水','JackeyLove'],'theshy':['Shy','TheShy'],'faker':['飞科','Faker'],'huchenfeng':['户子','户晨风'],'us-lecturer':['美国讲师','丁胖子金牌讲师'],'daoge':['刀哥','东北刀哥'],'huge':['虎哥','东北虎哥'],'lebron':['詹姆斯','勒邦詹氏','乐邦詹士','LeBron'],'curry':['库里','裤衩子','Curry'],'kobe':['科比','老大','Kobe'],'fengge':['峰哥','峰哥亡命天涯'],'rookie':['Rookie','肉鸡'],'kid':['Kid','小孩游神']}
for p in D['characters']:
 pid=p['personId'];p['enabled']=pid in rosters[p['theme']];p['tier']='featured' if pid in featured else 'normal';p['exposureWeight']=4 if pid in featured else 1
 p['aliases']=list(dict.fromkeys(aliases.get(pid,[])+[p['name'],p.get('nickname','')]+p.get('aliases',[])));p['aliases']=[a for a in p['aliases'] if a]
 if pid in aliases:p['nickname']=aliases[pid][0]
 if pid=='lebron':p['name']='詹姆斯'
 if pid in ['yangyi','xujingyu']:p['sub']='篮球解说 / 本作娱乐组队设定';p['roleType']='commentator'
 if p['enabled']:p['rosterOrder']=rosters[p['theme']].index(pid)
for theme,cards in D['augments'].items():
 for a in cards:
  owners=a.get('signatureFor',[]);a['enabled']=not owners or any(pid in rosters[theme] for pid in owners)
D['version']=11;D['rosterPolicy']={'featuredWeight':4,'normalWeight':1,'nearTop':5,'maxBonus':4,'note':'编辑曝光配置，不是实时人气榜'}
D['counts']['people']=sum(p['enabled'] for p in D['characters'])
for t in rosters:D['counts']['byTheme'][t]['people']=len(rosters[t]);D['counts']['byTheme'][t]['cards']=sum(a['enabled'] for a in D['augments'][t])
D['counts']['parodyCards']=sum(a['enabled'] for cards in D['augments'].values() for a in cards)
save(R/'src/data.json',D);save(R/'tools/v11-roster.json',rosters)
A=json.loads((R/'assets/portrait-atlas.json').read_text());S=json.loads((R/'image-sources.json').read_text())
for pid,name,*_ in new:
 A['portraits'][pid]={'pending':True}
 S.append(dict(id=pid,name=name,verifiedReference=False,status='pending',kind='文字占位',note='照片待核对，不用其他人物替代。',rights='未投入照片素材。'))
save(R/'assets/portrait-atlas.json',A);save(R/'image-sources.json',S)
print('40 enabled; old IDs and V10 engine/data archived')
