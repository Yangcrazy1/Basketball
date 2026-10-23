from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];f=R/'src/data.json';D=json.loads(f.read_text())
# New questions are scored by option meaning, never by their displayed or authored position.
values={
'basket':{
'social':{'nba-safe':1,'nba-calm':1,'nba-plan':2,'nba-train':2,'nba-clutch':3,'nba-three':3,'nba-show':4,'nba-drive':3,'nba-team':4,'nba-emotion':4,'nba-rebound':2,'nba-dunk':4,'nba-alien':2,'nba-care':3},
'explore':{'nba-safe':1,'nba-calm':1,'nba-plan':3,'nba-train':2,'nba-clutch':3,'nba-three':4,'nba-show':4,'nba-drive':3,'nba-team':2,'nba-emotion':3,'nba-rebound':2,'nba-dunk':4,'nba-alien':3,'nba-care':2},
'empathy':{'nba-safe':2,'nba-calm':3,'nba-plan':2,'nba-train':1,'nba-clutch':1,'nba-three':1,'nba-show':2,'nba-drive':1,'nba-team':4,'nba-emotion':2,'nba-rebound':3,'nba-dunk':1,'nba-alien':2,'nba-care':4},
'action':{'nba-safe':1,'nba-calm':1,'nba-plan':2,'nba-train':3,'nba-clutch':4,'nba-three':3,'nba-show':4,'nba-drive':4,'nba-team':3,'nba-emotion':3,'nba-rebound':4,'nba-dunk':4,'nba-alien':3,'nba-care':2},
'order':{'nba-safe':4,'nba-calm':3,'nba-plan':4,'nba-train':4,'nba-clutch':2,'nba-three':2,'nba-show':1,'nba-drive':2,'nba-team':3,'nba-emotion':1,'nba-rebound':3,'nba-dunk':1,'nba-alien':2,'nba-care':3},
'express':{'nba-safe':1,'nba-calm':1,'nba-plan':3,'nba-train':2,'nba-clutch':3,'nba-three':3,'nba-show':4,'nba-drive':2,'nba-team':2,'nba-emotion':4,'nba-rebound':1,'nba-dunk':3,'nba-alien':2,'nba-care':2}},
'abstract':{
'social':{'web-watch':1,'web-craft':1,'web-plan':2,'web-edit':2,'web-original':2,'web-care':3,'web-travel':3,'web-punchline':4,'web-live':4,'web-meme':4,'web-cover':3,'web-dance':4},
'explore':{'web-watch':2,'web-craft':3,'web-plan':2,'web-edit':4,'web-original':4,'web-care':2,'web-travel':4,'web-punchline':3,'web-live':3,'web-meme':3,'web-cover':3,'web-dance':3},
'empathy':{'web-watch':3,'web-craft':2,'web-plan':2,'web-edit':1,'web-original':2,'web-care':4,'web-travel':2,'web-punchline':2,'web-live':2,'web-meme':1,'web-cover':2,'web-dance':1},
'action':{'web-watch':1,'web-craft':3,'web-plan':2,'web-edit':3,'web-original':3,'web-care':2,'web-travel':4,'web-punchline':3,'web-live':4,'web-meme':4,'web-cover':3,'web-dance':4},
'order':{'web-watch':3,'web-craft':4,'web-plan':4,'web-edit':3,'web-original':2,'web-care':3,'web-travel':2,'web-punchline':1,'web-live':1,'web-meme':1,'web-cover':2,'web-dance':1},
'express':{'web-watch':1,'web-craft':2,'web-plan':2,'web-edit':3,'web-original':3,'web-care':2,'web-travel':3,'web-punchline':4,'web-live':4,'web-meme':4,'web-cover':4,'web-dance':4}}}
for q in D['questions']:
 if q['id'].startswith('v11-') and q['theme']!='lol':
  for o in q['options']:o['value']=values[q['theme']][q['dim']][o['behavior']]
# Every scene affinity has an explicit question + behavioral basis in the editorial data.
for p in D['characters']:
 if not p['enabled']:continue
 rules={}
 for a in D['augments'][p['theme']]:
  if a.get('exclusive') and a.get('owner')==p['personId'] and a['activationMode']=='answers':
   for id in a['evidenceQuestionIds']:
    rules.setdefault(id,{})
    for b,w in a['behaviorWeights'].items():rules[id][b]=max(rules[id].get(b,0),w)
 p['answerAffinities']=rules
# Derive current counters rather than maintaining separate front-end constants.
for t in D['themes']:
 ts=D['counts']['byTheme'][t['id']];ts.update(people=sum(p['enabled'] and p['theme']==t['id'] for p in D['characters']),questions=sum(q['enabled'] and q['theme']==t['id'] for q in D['questions']),cards=sum(a['enabled'] for a in D['augments'][t['id']]))
f.write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n')
p=R/'src/engine.js';s=p.read_text();a=s.index('function rankPeople(');b=s.index('\nfunction recommend',a)
s=s[:a]+'''function rankPeople(s,data,vector){const rows=selections(s,data);return applyExposure(enabledPeople(data,s.theme).map(p=>{const v=similarity(vector,p.vector),b=behaviorFit(rows,p.behaviorWeights),scene=100*rows.reduce((sum,{q,o})=>sum+((p.answerAffinities&&p.answerAffinities[q.id]&&p.answerAffinities[q.id][o.behavior])||0),0)/(5*rows.length);return Object.assign({},p,{rawMatch:Math.round(.4*v+.35*b+.25*scene),matchBreakdown:{vector:v,behavior:b,scene}});}),data.rosterPolicy);}
''' +s[b:];p.write_text(s)
p=R/'src/app.js';s=p.read_text();s=s.replace("if(record.customTeam&&!E.squadError(record.customTeam.ids,theme,D,record.customTeam.free)){result.team=E.customSquad(record.customTeam.ids,theme,D", "if(record.customTeam&&!recordEngine(record).squadError(record.customTeam.ids,theme,recordData(record),record.customTeam.free)){result.team=recordEngine(record).customSquad(record.customTeam.ids,theme,recordData(record)")
s=s.replace("function inherentPanel(r){return", "function inherentPanel(r){const cards=r.inherentCards||(r.identity.signaturePerks||[]).map(id=>[].concat(...Object.values(recordData(currentRecord).augments)).find(a=>a.id===id)).filter(Boolean);return").replace('随身份附赠的 3 张专属卡','随身份附赠的 ${cards.length} 张专属卡').replace('${(r.inherentCards||[]).map(a=>','${cards.map(a=>')
# Keep only runtime version labels fresh; storage prefix stays v10 for migration/history.
s=s.replace('VOL.10','VOL.11').replace('V10-整活海报','V11-整活海报').replace('V10-离线版','V11-离线版').replace(' · V10',' · V11').replace('清除 V10','清除本机').replace('V10 进度','本机进度').replace(' ·  V10',' ·  V11')
s=s.replace('篮球梦之队 包含老大科比、勒邦詹氏、裤衩子库里、乔丹、邓肯、约老师与年轻球员；抽象热梗围绕跳舞、翻唱、旅行和自媒体日常。','篮球梦之队围绕球场日常、球星与解说梗；抽象热梗围绕带文学、旅行、饭点和互联网嘴替。')
s=s.replace('人物、海克斯和联动卡均使用真实作答证据；专属梗卡有对应行为才能激活。','作答触发卡需要相关题中的实际选择；人物自带赠卡单独展示，不生成作答证据。')
p.write_text(s)
