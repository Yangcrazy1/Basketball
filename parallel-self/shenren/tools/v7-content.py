"""V7 authored fan-style parody cards, semantic links and coherent LoL cases."""
from pathlib import Path
import json,copy
ROOT=Path(__file__).resolve().parents[1];D=json.loads((ROOT/'src/data.json').read_text());D['version']=7
# All card text/icons in V7 are original parody. Rarity describes our frame, not an official game item.
CARDS=[
('table-flip','掀桌',0,'心态','kPrismatic','队友第三次说“这把能赢”时，\n将整张桌子刷新到下一局。','赢不了比赛，就改变比赛用的家具。',[95,35,90,15,35,5],{'chaos':5,'blame':3,'reset':2,'int':1},['pdd','ning'],'chaos'),
('collector-union','第五位收集者',1,'经济','kPrismatic','当四名队友都出收集者时，\n你的商店只剩收集者。','全队伤害可以共享，最后一口绝不共享。',[58,98,65,25,65,25],{'collector':5,'gold':2},['uzi','jackeylove'],'economy'),
('basic-duty','回归基本功',2,'操作','kPrismatic','你的 R 键进入年假。\n每次阵亡，复盘时长翻倍。','技能少了一个，解释多了八百字。',[25,40,35,50,95,80],{'mechanics':5,'explain':3,'plan':1},['dasima','knight','faker'],'basic'),
('square-lecture','正方形讲解',4,'嘴硬','kGold','把打野路线画成正方形。\n每绕一圈，获得一次“我有说法”。','先别急，等我把第四条边讲完。',[35,45,25,50,55,98],{'explain':5,'plan':3,'retreat':1},['dasima','clearlove'],'plan'),
('fountain-owner','泉水股东',7,'摆烂','kPrismatic','挂机期间，泉水算你的房产。\n队友每次路过都得听你点评。','人没出泉水，已经指挥了三个战区。',[75,25,5,5,20,15],{'afk':5,'retreat':1,'blame':1},['pdd','dasima'],'retreat'),
('feeding-license','开送驾驶证',8,'上头','kPrismatic','闪现自动规划最短送达路线。\n复活后可无缝续订下一单。','对面全是五星好评，队友正在申请退款。',[98,20,100,8,35,5],{'int':5,'chaos':1},['ning','jackeylove','theshy'],'chaos'),
('all-aboard','全队上车',13,'开团','kGold','你的雪球新增四个乘客座位。\n按下第二段时，车门自动焊死。','来不来另说，反正倒数已经开始。',[60,35,95,90,55,35],{'engage':5,'protect':1,'control':1},['ming','doinb','ning'],'engage'),
('where-team','队友呢？',3,'上头','kGold','突进后暂时关闭小地图。\n阵亡回放时，自动恢复视野。','刚才说跟我，现在怎么只有我？',[80,45,96,12,65,15],{'int':4,'engage':3,'blame':2},['jackeylove','theshy'],'chaos'),
('spring-heater','春季恒温器',9,'运营','kPrismatic','把日历的十二个月改成春天。\n逆风时，可申请一次室温复核。','不是只会打春天，是我负责定义春天。',[25,50,40,70,65,95],{'plan':5,'control':3,'stack':1},['xiaohu'],'plan'),
('four-stay-alive','你们四个别死',10,'队友','kPrismatic','当队友集体上头时，\n你自动获得四个血压监测窗口。','这队可以没脑子，不能没有售后。',[15,20,50,100,55,75],{'protect':5,'heal':3,'control':1},['letme','meiko','ming'],'protect'),
('economy-brain','经济头脑',5,'经济','kGold','每漏一个兵，\n脑内自动播放余额不足提示音。','团可以等，炮车不能等。',[25,98,25,35,55,85],{'gold':5,'stack':3,'collector':1},['uzi','clearlove'],'economy'),
('borrowed-growth','贷款式发育',5,'经济','kPrismatic','立即购买下一件梦想装备。\n利息从队友的精神状态里扣。','别问经济哪来的，先把高光录下来。',[65,98,75,15,65,20],{'collector':4,'gold':3,'chaos':1},['uzi','pdd'],'economy'),
('blame-master','甩锅宗师',6,'嘴硬','kPrismatic','阵亡后生成一口可转移的锅。\n连续说三次“不是我的”，锅会镀金。','伤害排名第五，责任归属第一。',[85,35,35,3,30,20],{'blame':5,'explain':2,'afk':1},['pdd','dasima'],'blame'),
('not-a-loss','这波不亏',4,'嘴硬','kGold','每次阵亡，自动生成一份收益报告。\n亏得越多，PPT 页数越多。','人头可以掉，逻辑闭环不能掉。',[50,55,35,40,45,90],{'explain':5,'plan':1,'reset':1},['dasima'],'plan'),
('life-reroll','人生重开器',14,'随机','kPrismatic','对当前人生点击一次刷新。\n保留战绩，重新抽取嘴硬理由。','旧的我已经下班，这锅找新的我。',[55,40,60,35,45,15],{'reset':5,'chaos':2,'blame':1},['pdd','doinb'],'reset'),
('clown-self','小丑竟是我',15,'抽象','kPrismatic','进场前播放主角音乐。\n阵亡后，音乐自动改成马戏团。','本想剪燃向混剪，最后成了鬼畜素材。',[85,35,85,20,55,15],{'chaos':5,'int':2,'reset':1},['pdd','ning'],'chaos'),
('fountain-range','泉水射程',12,'拉扯','kGold','把攻击距离延长到安全感以外。\n每后退一步，获得一句“我在输出”。','输出先别急，先保证没人碰到我。',[15,50,5,35,85,75],{'poke':5,'retreat':3,'mechanics':1},['uzi','knight'],'range'),
('ultimate-installment','大招分期付款',2,'操作','kPrismatic','今天先交第一个 R。\n第二个 R 从下一局预支。','大招可以分期，镜头必须全款。',[55,45,75,55,85,35],{'ult':5,'mechanics':1,'engage':1},['xiaohu','faker'],'basic'),
('cosmic-pension','宇宙养老保险',5,'发育','kGold','叠一层，存一笔养老金。\n直到基地爆炸，都在等待强势期。','别催，恐龙退休以后轮到我发力。',[10,85,15,35,45,100],{'stack':5,'gold':2,'plan':1},['clearlove','knight'],'economy'),
('bridge-clinic','桥头医务室',10,'治疗','kPrismatic','队友喊一次“奶我”，挂号一次。\n喊得太响，自动转精神科。','奶量有限，求生欲请自行充值。',[5,15,20,100,65,80],{'heal':5,'protect':2},['meiko','baolan'],'protect'),
('last-last-game','真·最后一把',14,'续杯','kGold','每说一次“最后一把”，\n自动新增一个平行宇宙。','不是不睡，是这个宇宙还没赢过。',[60,40,65,65,40,20],{'reset':5,'chaos':1,'protect':1},['doinb','pdd'],'reset'),
('revive-cinema','复活电影院',7,'观战','kSilver','灰屏时解锁全队第一视角。\n观影结束可发表一条高质量弹幕。','操作没看到，问题已经看明白了。',[50,20,5,20,35,50],{'afk':4,'blame':2,'explain':2,'retreat':1},['dasima','pdd'],'retreat'),
('champion-script','冠军剧本',11,'名场面','kPrismatic','把“当年要是”兑换成一次决胜局。\n这一回，金色的雨由你签收。','历史可以架空，走位必须自己走。',[35,65,70,65,100,65],{'mechanics':5,'ult':2,'plan':1},['uzi','faker'],'basic'),
('snowball-hearse','雪球灵车',13,'开团','kPrismatic','雪球命中后，导航直达对面泉水。\n乘客可在复活后补交车费。','上车前是五排，上车后是五个省略号。',[85,30,100,30,45,5],{'int':4,'engage':3,'chaos':2},['ning','jackeylove'],'chaos')]
CARDS.append(('good-enough','得过且过',7,'摆烂','kSilver','进入本局省电模式。\n队友问你在哪，自动回复“在混了”。','不当最亮的星，先当最稳的在线状态。',[30,35,5,25,30,55],{'afk':3,'retreat':5,'reset':1},['pdd','baolan'],'retreat'))
D['augments']['lol']=[]
for ident,name,icon,category,tier,effect,punchline,vector,weights,people,kind in CARDS:
 D['augments']['lol'].append({'id':ident,'name':name,'icon':icon,'category':category,'rarity':tier,'effect':effect,'punchline':punchline,'line':punchline,'vector':vector,'behaviorWeights':weights,'affinities':people,'kind':kind,'bias':[(v-50)/50 for v in vector],'fanMade':True,'creation':'本作原创恶搞文案与图标，借鉴网友 DIY 天赋卡的表现方式','requires':['afk'] if ident in ['fountain-owner','revive-cinema'] else ['blame'] if ident=='blame-master' else []})
good=next(a for a in D['augments']['lol'] if a['id']=='good-enough');good.update(creation='参考已查看网络 DIY 卡“得过且过”的命名方向，效果与图标由本作重新创作',referenceTitle='金铲铲之战：网友 DIY 彩色海克斯，打破玩家认知！',sourcePage='https://mmbiz.qpic.cn/mmbiz_jpg/eutmxn8eXtLC9Sob7XUfyQj85zBiaBv4wTEXrNogU7ibWVsqjrlu1IxZRicTib7buYjwibhWfXu5h3ENTG8wiczthZ5w/0?wx_fmt=jpeg')
D['augmentData']={'edition':'网友脑洞风 · 本作自制','checkedAt':'2026-10-23','note':'卡名、效果和配图是本作娱乐设定，不是官方游戏强化。参考用户提供的回归基本功恶搞卡及网络 DIY 海克斯合集的卡片表达方式。没有把未读到的网传文案声称为原作。'}
# Replace official rules with connected parody premises; preserve option IDs and authored signals.
replacements={
'hex-basic-0':('“回归基本功”让 R 键放年假，阵亡后的复盘时长翻倍。你接这张恶搞卡吗？',None),
'hex-box-0':('“人生重开器”能把旧天赋洗成三句网友锐评。你按刷新吗？',None),
'hex-gate-0':('恶搞卡“冠军剧本”把对面家门标成领奖入口。你打算怎么签收？',None),
'hex-range-0':('抽到“泉水射程”：打得到全桥，但每出门一步就扣安全感。你会？',None),
'hex-giant-0':('抽到“桥梁承重测试”：体型越大，越像全队移动掩体。你愿意站前面吗？',None),
'hex-missile-0':('“弹幕实体化”让你命中的技能附赠一个问号。问号快递寄给谁？',None),
'hex-heal-0':('四个输出喊“奶我”。你抽到“桥头医务室”，今晚开诊吗？',None),
'hex-clown-0':('“小丑竟是我”给你准备了主角 BGM 和马戏团 BGM。你怎么入场？',None),
'hex-stack-0':('抽到“宇宙养老保险”：层数像存款，队友像催缴员。你准备？',None),
'hex-ult-0':('“大招分期付款”让你预支下一局的 R。这局的镜头怎么拍？',None),
'hex-gate-2':('领奖入口后面的奖励未知，队伍最想要哪种恶搞补给？',None),
'hex-missile-1':('队友把问号飞弹叫成“弹幕自动导航”，你怎么接梗？',None)}
for q in D['questions']:
 if q['id'] in replacements:q['title']=replacements[q['id']][0]
 if q['theme']=='lol':q['importance']=1.25 if q['stage']==0 else 1
# Meaningful title branch for all four answers of the user's key scenario.
next(q for q in D['questions'] if q['id']=='hex-collector-1')['branches']={
'0':'你切到观战席，看到对面五个大汉堵住了桥。你希望接下来怎么演？',
'1':'送礼小剧场结束，复活倒计时还在走；对面五个大汉堵桥。下一波怎么回来？',
'2':'第五把收集者刚掏出来，对面五个大汉堵桥。你准备怎么展示这笔投资？',
'3':'你成了四把枪前唯一的盾，对面五个大汉堵桥。你怎么带队？'}
# Every public figure gets a distinct semantic style, so cards/personas can share actual evidence.
PW={
'uzi':{'mechanics':5,'collector':5,'gold':3,'poke':2},'xiaohu':{'plan':5,'ult':4,'control':3,'stack':1},'dasima':{'explain':5,'plan':4,'reset':2,'retreat':1},'theshy':{'mechanics':5,'engage':4,'int':3},'faker':{'control':5,'mechanics':4,'plan':4,'ult':3},'clearlove':{'plan':5,'stack':4,'gold':3,'retreat':2},'jackeylove':{'int':5,'engage':4,'mechanics':3,'collector':2},'doinb':{'engage':5,'protect':4,'chaos':3,'control':2},'pdd':{'chaos':5,'reset':4,'blame':3,'afk':2},'ming':{'engage':5,'control':4,'protect':4},'meiko':{'heal':5,'protect':5,'plan':2},'letme':{'protect':5,'control':4,'plan':3},'ning':{'int':5,'engage':5,'chaos':3},'knight':{'mechanics':5,'poke':4,'ult':3,'stack':2},'baolan':{'protect':5,'heal':4,'retreat':2,'control':1}}
NAMES={'uzi':'污渍','xiaohu':'销户','dasima':'大司马','faker':'飞科','clearlove':'厂长','jackeylove':'杰克爱','ning':'宁王','knight':'左手','ming':'小明','baolan':'宝蓝'}
for p in D['characters']:
 if p['theme']=='lol':p['behaviorWeights']=PW[p['personId']];p['nickname']=NAMES.get(p['personId'],p['name'])
S={}
for q in D['questions']:
 if q['theme']=='lol':
  for o in q['options']:S[o['behavior']]=copy.deepcopy(o)
for key,v,tags in [('explain',[40,45,20,40,45,95],['theory','plan']),('blame',[88,35,30,5,30,20],['blame','chaos'])]:
 S[key]={'signals':dict(zip([x['id'] for x in D['lolDimensions']],v)),'tags':tags,'behavior':key}
NEW=[
('table','掀桌董事会',[
('第三次能赢','四把收集者已经齐了，队友第三次说“能赢”。你按哪个恶搞按钮？',['掀桌！这局换套家具继续打@chaos','泉水挂机，远程出席董事会@afk','开送，把会议纪要送到对面@int','别急，我把能赢的条件列一下@explain']),
('会议分歧','桌子翻到半空，四位股东都说“我没问题”。导演该给谁特写？',['给锅，锅比人更忙@blame','给小地图，我想知道谁先走散@plan','给我的走位，操作还是要看@mechanics','给血条，先把能救的人接住@heal']),
('家具落地','桌子终于落地，对面却抱团进来了。下一幕怎么拍？',['再掀一轮，连地图一起翻@chaos','我先顶住，四位股东往后走@protect','别打字了，直接雪球发车@engage','退半步，等他们交完技能@retreat']),
('散会总结','给这次董事会写一句结语，你写？',['不是我掀桌，是桌子不配赢@blame','家具可以翻，账本不能乱@explain','四个人能活着，会议就有下次@protect','下次记得换一张能重抽的桌子@reset'])]),
('office','泉水远程办公',[
('居家申请','你抽到“泉水股东”：出泉水算出差。你准备？',['挂机上岗，今天申请全程远程@afk','我不坐办公室，先冲一波@int','先把兵线工资领了@gold','安排谁留谁出，别五个人都不上班@plan']),
('视频会议','队友开团了，灰屏观战席让你发一句会议意见。你说？',['我早说不能这么打@blame','给我十秒，我把这波讲明白@explain','先别吵，复活后一起走@protect','下一波大招好了我来开@ult']),
('出差通知','一辆雪球公交停在泉水门口。你要怎么上班？',['车票退了，我继续挂机参会@afk','第一排，车门焊死我也不下@engage','先问终点，别直接送到对面家@plan','带上奶包，我负责车上急救@heal']),
('绩效表格','本局绩效只允许填一项，你填？',['远程指挥覆盖率百分之百@afk','这波不亏，报告稍后八百字@explain','金币到账，业绩自然会说话@gold','五个人还在群里，下次继续@protect'])]),
('review','这波真不亏',[
('讲解启动','你刚阵亡，复活还有十秒，恶搞卡“这波不亏”亮了。你先？',['开讲，十秒足够起一个标题@explain','找锅，十秒足够确定责任@blame','看回放找走位问题@mechanics','报技能，给还活着的队友信息@protect']),
('收益报告','队友问“你拿人头换到了什么”，你交哪份报告？',['对面用了三个技能，这叫战略投资@explain','他们没跟，不在我的项目范围@blame','换到一个教训，下波不这样进@plan','换到了对面的赏金邀请函，下次还来@int']),
('再次出门','复活门一开，同一个路口又出现一个残血。下一幕？',['先看队友位置，再决定追不追@plan','操作换个细节，这回我能打@mechanics','还冲，刚才只是路线没规划好@int','给队友打标记，大家一起收尾@protect']),
('赛后标题','你给这段回放起名？',['人可以没，逻辑必须闭环@explain','锅从天上来，反正不是我@blame','修正一个动作，就是下一局的进步@mechanics','下集重开，这个宇宙先暂停@reset'])]),
('collector-audit','收集者年终审计',[
('资产清单','你们五个人的收集者比人头还多，审计来了。你先做什么？',['再买一把，资产规模还不够@collector','把账拉平，至少留一笔给前排@plan','我来承压，四位财务先别倒@protect','掀桌，账本跟桌子一起重置@chaos']),
('最后一口税','恶搞规则说最后一口要交税，队伍突然客气起来。你怎么办？',['我交税，我来吃最后一口@collector','给差一点成装的人，把收益最大化@plan','我不抢，先保住队友不被反杀@protect','直接开送，让对面来交所得税@int']),
('金币响了','金币音效响得像收银机，对面却在推基地。镜头选哪边？',['先回防，基地不能被拿去抵押@plan','吃完这波炮车，马上到@gold','雪球回去，今天用身体堵门@engage','我在泉水，主打一个房东在场@afk']),
('年终评语','给自己这一年的峡谷事业留一句评语？',['第五位股东，最后一口负责人@collector','收入有波动，复盘没停过@explain','队友健康，才有下一笔生意@heal','经济自由还没到，至少先开心@reset'])])]
for cid,name,rows in NEW:
 for stage,(scene,title,opts) in enumerate(rows):
  options=[]
  for oid,opt in enumerate(opts):
   text,key=opt.rsplit('@',1);o=copy.deepcopy(S[key]);o.update(id=oid,text=text);o.pop('value',None);options.append(o)
  ident=f'hex-{cid}-{stage}'
  if not any(q['id']==ident for q in D['questions']):D['questions'].append({'id':ident,'theme':'lol','series':'hex','chapter':cid,'chapterName':name,'stage':stage,'scene':scene,'title':title,'options':options,'importance':1.25 if stage==0 else 1})
for s in D['lolSeries']:s['count']=sum(q['theme']=='lol' and q['series']==s['id'] for q in D['questions'])
D['themes'][0].update(name='英雄联盟',description='上 / 野 / 中 / 下 / 辅 · 网友脑洞风恶搞海克斯',slogan='人是你匹配的，锅是全队一起分的。')
D['counts']={'questions':len(D['questions']),'lolQuestions':sum(q['theme']=='lol' for q in D['questions']),'lolChapters':len({(q['series'],q['chapter']) for q in D['questions'] if q['theme']=='lol'}),'people':len({p['personId'] for p in D['characters']}),'parodyCards':len(D['augments']['lol'])}
D['behaviorLabels']={'afk':'泉水远程办公','int':'直线送达','collector':'第五位股东','protect':'队友保命优先','plan':'先把局讲明白','mechanics':'操作必须拉满','engage':'开团先上车','chaos':'节目效果优先','poke':'安全距离营业','stack':'宇宙复利','heal':'桥头医务室','reset':'人生允许重抽','ult':'大招就要连播','gold':'金币不能漏','control':'先控住局面','retreat':'先留一条退路','explain':'复盘比复活快','blame':'锅先找到下家'}
(ROOT/'src/data.json').write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n')
(ROOT/'assets/parody-cards.json').write_text(json.dumps(D['augments']['lol'],ensure_ascii=False,indent=2)+'\n')
print(D['counts'])
