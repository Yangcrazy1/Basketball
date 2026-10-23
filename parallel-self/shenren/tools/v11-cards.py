from pathlib import Path
import json,copy,collections
R=Path(__file__).resolve().parents[1];D=json.loads((R/'src/data.json').read_text());P={p['personId']:p for p in D['characters']};cards=[a for arr in D['augments'].values() for a in arr];byname={a['name']:a for a in cards};byid={a['id']:a for a in cards}
renames={'这波不亏计算器':'not-a-loss','最后一把永动机':'personal-luobenwei','院长加班通知':'extra-rookie-1','带文学翻译机':'personal-dailanzi','晚安提前预约':'goodnight-three','更衣室群主':'team','闪现还在':'ultimate-installment','上路独立宇宙':'lane-umbrella','我队友呢':'where-team','反向冲分计划':'life-reroll','兵线独立账户':'economy-brain'}
scopes={'uzi':['collector','bro-flash','water','review-home'],'xiaohu':['spring','double-laugh','watchparty'],'jackeylove':['bro-flash','water','clip'],'theshy':['top-alone','range','ig-memory'],'vincent':['boss','netcafe','clip'],'rookie':['clinic','netcafe','review-home'],'faker':['salary','galio','worlds-party'],'xiaoxiao':['duo','deyunse','watchparty'],'xika':['duo','deyunse','watchparty'],'pdd':['boss','clip','netcafe'],'dasima':['jungle-date','review','review-home','office'],'clearlove':['jungle-date','office','netcafe'],'ning':['jungle-date','mic','netcafe'],'kid':['jungle-date','duo','ig-memory'],'luobenwei':['netcafe','review-home','mic'],'baolan':['ad-insurance','heal','office'],'otto':['keyboards','review-home','mic'],'zztai':['watchparty','duo','clip'],'doinb':['mic','jungle-date','ad-insurance'],'ming':['ad-insurance','heal','collector']}
# Dedicated everyday scenes: each answer-triggered non-League representative has two relevant evidence questions.
# Other two cards are innate identity gifts and never claim the player selected their story.
scenes={
'lebron': [('action','朋友对刚才的判罚摊手，你先怎么回应？','nba-emotion|我也摊手，先把表情同步。','nba-team|拉他回来，下一球还等着。','nba-calm|喝口水，先缓半分钟。','nba-show|给个表情，录像别漏这段。'),('express','回放里你的表情比进球还抢镜，你会？','nba-show|留着，这场总得有张封面。','nba-emotion|把当时的心情再讲一遍。','nba-team|配上队友拉我回防的那段。','nba-calm|笑一下，下次记得先回去。')],
'durant':[('action','球传到你手里，朋友喊“就这个位置”，你会？','nba-clutch|接住就试一球，脚步站稳。','nba-three|再退一点，看看今天手感。','nba-safe|先看空位，不急着拔。','nba-team|让队友也摸到球，下一次还我。'),('explore','同一个位置连着进了两球，下一回合？','nba-clutch|就在这儿，再试一次。','nba-three|稍微远一点，别一次退太多。','nba-plan|留着这招，等机会再用。','nba-show|对镜头点头，熟悉的位置。')],
'jordan':[('action','野球场最后一投，朋友把球递给你，你会？','nba-clutch|我来，先把呼吸稳住。','nba-drive|试着往里走，看看能不能更近。','nba-team|问问谁手热，一起选。','nba-safe|看清时间，别乱扔。'),('express','朋友说你刚才那一球“没压力”，你回？','nba-clutch|球给我，下回再接一次。','nba-train|那是平时练过，别跳过这句。','nba-show|先喝口咖啡，再给你配解说。','nba-calm|手心都湿了，赢了才说轻松。')],
'kobe':[('action','今天打铁比进球多，散场前你准备？','nba-train|留十分钟，把动作练顺。','nba-clutch|再认真试最后几球。','nba-team|找个队友互相传，谁都不闲着。','nba-calm|先歇会儿，动作别练乱。'),('order','明天朋友又约球，你今晚怎么安排？','nba-train|鞋放门口，早点起练一下。','nba-plan|定个自己能完成的小目标。','nba-care|问问朋友要不要一起热身。','nba-show|先把闹钟截图发群里，求监督。')],
'yangyi':[('express','比赛暂停，朋友问刚才那球怎么来的，你会？','nba-plan|从前一个回合讲起才清楚。','nba-show|先配一句旁白，画面感得有。','nba-calm|简单说两句，等他们回来。','nba-team|听听传球的人怎么想。'),('social','朋友只问一句背景，你发现自己讲了三分钟。你会？','nba-show|故事到一半，给我再半分钟。','nba-plan|先讲关键那句，细节赛后补。','nba-emotion|这段我有印象，得讲明白。','nba-care|问问大家听懂没，再往下说。')],
'xujingyu':[('express','朋友对同一球给了相反评分，你会？','nba-emotion|我先立个观点，听我说完。','nba-plan|回放拉过来，一帧帧看。','nba-calm|各留一个看法，别急着吵。','nba-show|今晚解说席开加时。'),('social','场边快没人了，你们还在聊那一球。你先？','nba-emotion|再讲一句，这个点还没说透。','nba-plan|总结两条，改天接着聊。','nba-care|先问他回家远不远。','nba-show|拿个水瓶当话筒，正式收尾。')],
'zhouqi':[('order','边线发球，朋友跑来跑去却不看你，你先？','nba-team|喊名字，先把眼神对上。','nba-safe|球拿稳，等能传的机会。','nba-plan|约个手势，别只靠猜。','nba-show|举球问一句：谁来签收？'),('empathy','刚才发球没接住，朋友也有点尴尬，你会？','nba-team|一起对个暗号，下回用。','nba-safe|慢一点，先找稳的接法。','nba-care|拍拍肩，这球就过去了。','nba-calm|先回到位置，再聊原因。')],
'yaoming':[('express','朋友拍到你一个夸张表情，问能不能发群里，你会？','nba-show|发，今天表情包素材够了。','nba-emotion|给我也一份，我来配字。','nba-care|其他人也同意再发合照。','nba-calm|先看看，别把朋友裁丢。'),('social','队友用你的表情做了聊天贴图，你回？','nba-show|再摆个新的，更新第二套。','nba-emotion|用原图表情回他一个。','nba-team|全队每人来一张，凑齐。','nba-calm|默默收藏，以后用。')],
'curry':[('explore','朋友开玩笑说停车场也算三分线，你会？','nba-three|想象一下就好，找安全球场再试远投。','nba-show|拍个借位镜头，球先别真扔。','nba-safe|先看清场地，别让大家捡危险球。','nba-team|先把这场打完，再聊射程。'),('action','今天远投进了两球，朋友问你要不要再远一点，你会？','nba-three|稍微退一点，动作别散。','nba-show|先摆个晚安，回去还得防守。','nba-train|在这个位置多练几次。','nba-team|球先给队友，轮着来。')],
'harden':[('action','朋友贴得很近，你想怎么找出手位置？','nba-clutch|试个自己练过的后撤步。','nba-plan|先看脚下，别退到界外。','nba-team|传一下，换个角度再接。','nba-safe|先稳住球，不急。'),('explore','回放里后退动作很帅，但球没进，你准备？','nba-plan|看清脚步，找找哪儿不顺。','nba-clutch|再练两次，别光留造型。','nba-show|镜头先留，进球版以后补。','nba-calm|承认这次没进，下一次再来。')],
'dailanzi':[('social','朋友说吃饱喝足去网吧，还差一个开场白，你会？','web-meme|胃已六神装，键盘准备开工。','web-live|我先录一句，今晚气势管够。','web-care|先问谁没吃，给他留一份。','web-plan|查查余额，热血不能抵网费。'),('explore','吃完大餐，钱包只够打一小会儿，你准备？','web-meme|先打出气势，操作按分钟结。','web-live|拍个饭后开场，内容先到账。','web-plan|算好回程钱，剩下再安排。','web-watch|坐会儿消食，看朋友先玩。')],
'fengge':[('explore','路边遇见一个有趣摊主，你想聊两句。先说？','web-travel|你好，方便聊一下这里的故事吗？','web-care|问清能不能拍，不愿意就收手机。','web-watch|先看看他忙不忙。','web-plan|留意时间，别耽误人家做生意。'),('empathy','路边聊天很投缘，对方不想出镜。你会？','web-care|收起相机，聊天照样开心。','web-travel|只记下这条路，下次还来逛。','web-watch|好好听完，不急着做内容。','web-plan|记个匿名笔记，发布前再确认。')],
'daoge':[('social','五人合照迟迟开不了场，你先？','web-live|音乐给我，先做个开场。','web-meme|气势借我三秒，马上还。','web-care|先看谁还没准备好。','web-plan|支架放稳，数三个数一起。'),('express','朋友说你出场太有气势，正片呢？','web-meme|前奏包满意，正片一起想。','web-live|镜头接着开，我再来一句。','web-punchline|气势已交，内容分期。','web-care|把麦递过去，轮到你出场。')],
'huge':[('social','整活拍了一小时，大家嗓子都干了。你先？','web-care|一人递一瓶果汁，喝完再来。','web-meme|补给到了，气势别急着耗完。','web-plan|先休息五分钟，把下一段说清。','web-watch|坐下听听大家还想不想拍。'),('empathy','迟到的朋友来了，最后一瓶果汁还在你手里，你会？','web-care|递过去，先喝两口。','web-meme|举瓶欢迎：补给刚给你留好。','web-live|五个人一起碰一下，再开机。','web-watch|放他旁边，等他自己拿。')],
'huchenfeng':[('explore','同一份饭三家店差价很大，你会？','web-watch|先看每家份量和配菜。','web-craft|拍下菜单，回头仔细比较。','web-care|问问朋友更想吃哪家。','web-plan|预算先定，再决定。'),('order','朋友说贵就是好，你拿着菜单怎么接？','web-watch|先看清价格，别只看封面。','web-craft|把重量和做法也问一问。','web-punchline|钱包先投个反对票。','web-care|各按自己预算选，也能坐一起。')],
'us-lecturer':[('order','陌生街区快到饭点，朋友还想随便逛。你先？','web-plan|找好能吃饭的地方，再绕路。','web-watch|看清营业时间，别到门口才扑空。','web-care|问问谁饿了，先安排一顿。','web-live|今天补给地图，由我带路。'),('action','朋友问午饭去哪儿，你手机里已经打开什么？','web-plan|路线和时间，走过去刚刚好。','web-watch|菜单照片，先知道有没有想吃的。','web-care|大家的口味清单，别只顾自己。','web-travel|附近地图，吃完还能逛一段。')],
'sunxiaochuan':[('empathy','群里一句吐槽让朋友不舒服，你会？','web-care|先停下来，问他愿不愿意聊。','web-punchline|把梗收回，改成自嘲也别追着说。','web-watch|看清前情，不跟着刷。','web-plan|删掉不合适的那条，边界说清。'),('express','评论区玩梗开始给人乱扣锅，你先？','web-punchline|提醒一句：包袱能接，锅别乱甩。','web-care|照顾被提到的人，先停火。','web-watch|翻清上下文，再决定怎么回。','web-live|说明这是创作，不拿梗当事实。')],
'yaoshuige':[('social','朋友突然盯着你不说话，你会？','web-watch|也看着他，等一个人先笑。','web-meme|保持表情，挑战已经开始。','web-punchline|问一句：你也在等加载吗？','web-care|先问是不是想说点什么。'),('express','十秒对视谁都没开口，镜头还亮着。你先？','web-watch|再等半拍，看看谁先动。','web-meme|举个暂停手势，下一轮继续。','web-original|留着这段，空白也挺真实。','web-punchline|宣布：本段台词已全部完成。')],
'leijun':[('social','朋友要办个小发布会，开场让你说Are you OK，你会？','web-live|麦给我，先和大家打招呼。','web-meme|带着四个人一起接一句。','web-plan|先对好节拍，不用背太多。','web-care|给紧张的朋友留一句简单的。'),('express','开场第一句意外很洗脑，朋友想再来一遍，你会？','web-meme|再接一次，全队副歌安排上。','web-live|顺手录下来，留个幕后。','web-edit|剪成开场提示音，别抢过正片。','web-watch|先看一遍，笑完再录。')],
'luoyonghao':[('social','新朋友想和你合拍，但不知道怎么分工，你先？','web-care|问问他喜欢做哪一部分。','web-live|一起试十秒，边做边熟。','web-plan|把最小的一版先说清。','web-punchline|交个队友，先别谈宇宙级合作。'),('empathy','搭档第一次忘词很尴尬，你怎么接？','web-care|留半拍，别急着催。','web-live|自嘲一句，再一起录一遍。','web-punchline|这次当彩排，下一次才开卖。','web-watch|先看他愿不愿意保留笑场。')]
}
for pid,rows in scenes.items():
 p=P[pid]
 for j,row in enumerate(rows):
  dim,title,*opts=row;id='v11-owner-'+pid+'-'+str(j)
  if any(q['id']==id for q in D['questions']):continue
  D['questions'].append(dict(id=id,theme=p['theme'],dim=dim,scene=p.get('nickname',p['name'])+' / 日常整活',title=title,enabled=True,personContext=pid,review={'status':'新增','reason':'人物代表卡的相关情境，提供独立证据'},options=[dict(id=n,text=z.split('|',1)[1],behavior=z.split('|',1)[0],tags=[z.split('|',1)[0]],value=n+1) for n,z in enumerate(opts)]))
used=set();pid=None;i=0;coverage=[]
for line in (R/'content/v11-personal-cards.txt').read_text().splitlines():
 if line.startswith('['):pid=line[1:-1];i=0;continue
 if not line:continue
 name,trigger,effect,punch,concept,beh=line.split('|');i+=1;p=P[pid];beh=beh.split(',');oldcard=byname.get(name) or byid.get(renames.get(name))
 a=copy.deepcopy(oldcard) if oldcard else dict(id='v11-'+pid+'-'+str(i),icon=(len(used)%16),rarity=['kPrismatic','kGold','kSilver'][i-1],bias=[(v-50)/50 for v in p['vector']],vector=p['vector'][:],kind='chaos',category='人物专属')
 a.update(name=name,owner=pid,signatureFor=[pid],affinities=[pid],personOnly=True,enabled=True,exclusive=True,fanMade=True,triggerScene=trigger,effect=effect,punchline=punch,line=punch,imageConcept=concept.split(','),creation='本作原创恶搞效果，不是人物原话。',behaviorWeights={b:5-n for n,b in enumerate(beh)},requires=beh,signatureRole=['代表梗','反转整活','日常共鸣'][i-1])
 mode='answers' if p['theme']=='lol' or i==1 else 'identity';a['activationMode']=mode
 bank=[q for q in D['questions'] if q['enabled'] and q['theme']==p['theme'] and (q.get('chapter') in scopes.get(pid,[]) if p['theme']=='lol' else q.get('personContext')==pid) and any(o['behavior'] in beh for o in q['options'])]
 # For Dailanzi the food starter has two food-specific scenes; academic and translation gifts are innate.
 a['evidenceQuestionIds']=[q['id'] for q in bank] if mode=='answers' else []
 if mode=='answers' and len(bank)<2:raise ValueError((pid,name,len(bank)))
 a['behaviorRules']={'mode':mode,'behaviors':beh,'questionIds':a['evidenceQuestionIds'],'identityOwner':pid,'note':'需选择相关题中的对应行为，不能拿其他题的同类行为冒充证据。' if mode=='answers' else '仅作人物自带赠卡，不生成作答证据。'}
 if a['id']=='collector-union':a['visual']={'layout':'fan','icons':['item-6676']*5,'label':'五把收集者 / 集体活动'}
 else:a.pop('visual',None);a['artAsset']='v11-card-art/'+a['id']+'.webp'
 a['icon']=a.get('icon',0)%16;a.setdefault('vector',p['vector'][:]);a.setdefault('bias',[(v-50)/50 for v in p['vector']]);a.setdefault('kind','chaos');a['category']='人物专属'
 arr=D['augments'][p['theme']];idx=next((n for n,x in enumerate(arr) if x['id']==a['id']),None)
 if idx is None:arr.append(a)
 else:arr[idx]=a
 used.add(a['id']);coverage.append(dict(card=a['id'],name=name,person=pid,mode=mode,questions=a['evidenceQuestionIds']))
for arr in D['augments'].values():
 for a in arr:
  if a['id'] not in used:
   # Existing generic/link cards stay separate. Retired exclusive cards stay stored for old IDs.
   a['enabled']=a.get('enabled',True) and len(a.get('signatureFor',[]))!=1;a['exclusive']=False;a['activationMode']='answers';a['owner']=None
for p in D['characters']:
 if p['enabled']:p['signaturePerks']=[a['id'] for a in D['augments'][p['theme']] if a['id'] in used and a['owner']==p['personId']]
active=[q for q in D['questions'] if q['enabled']];D['counts']['questions']=len(active);D['counts']['parodyCards']=sum(a['enabled'] for arr in D['augments'].values() for a in arr);D['counts']['exclusiveCards']=len(used)
for t in D['themes']:
 ts=D['counts']['byTheme'][t['id']];ts['questions']=sum(q['theme']==t['id'] for q in active);ts['cards']=sum(a['enabled'] for a in D['augments'][t['id']]);ts['exclusiveCards']=sum(a['id'] in used for a in D['augments'][t['id']])
(R/'src/data.json').write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n');(R/'docs/v11-card-coverage.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2)+'\n');print('120 exclusive cards;',collections.Counter(a['mode'] for a in coverage));print(D['counts'])
