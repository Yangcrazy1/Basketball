"""Three approachable meme universes, updated as an offline editorial snapshot."""
import json,re
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'src/data.json';d=json.loads(p.read_text());d['version']=9
d['themes'][0].update(name='英雄联盟',label='英雄联盟',description='S赛热梗 / 对线小技巧 / 大乱斗，全都一起玩',slogan='不背术语，照着你的第一反应选。',dims=['容易上头','金币执念','敢不敢冲','照顾队友','操作热情','稳住耐心'])
d['themes'][1].update(name='金闪闪队 · NBA',label='NBA 金闪闪队',description='老大 / 勒邦詹氏 / 裤衩子 / 现役与经典名场面',slogan='冠军先别争，五个人的节目先排满。')
d['themes'][2].update(name='抽象热梗',label='抽象热梗',description='摇一摇 / 翻唱 / 峰哥 / 自媒体 / 本期网络热梗',slogan='人还没上镜，前奏已经启动了。')
d['quizGuide']='点一个选项就自动下一题；选错可返回修改。'
d['editorial']={'checkedAt':'2026-10-23','label':'本期热梗 · 2026.10','note':'按公开来源整理的本期快照，含经典梗回归。离线版不自动抓取热榜。','sources':[{'title':'数英：2026上半年网络热词TOP30','date':'2026-08-21','url':'https://www.digitaling.com/articles/1561293.html','topics':['摇一摇舞蹈二创','豆包型人格','做完你的做你的','进城办事','不讲不讲']},{'title':'悟空中文：2025—2026中文网络热梗','url':'https://www.wukongsch.com/blog/zh/chinese-popular-internet-slangs-post-59740/','topics':['活人感','预制内容','爱你老己','邪修','丝瓜汤文学']}]}

# Preserve the meaning and scoring of existing League choices, explain their language.
terms=[('控制链','连续控制技能'),('斩杀线','能一套打掉的血量'),('技能真空期','技能还没好'),('取消后摇','让普攻动作更顺'),('走A','边走边普攻'),('线权','谁先清完兵'),('镀层','防御塔的额外金币'),('强势期','装备够用的时候'),('补刀','打掉最后一下拿金币'),('回城','回家买装备'),('核心装','最重要的装备'),('拉扯','边退边打'),('控图','看住地图上的资源'),('视野','地图信息'),('突进','冲到脸上'),('先手','先出手'),('真空期','等待时间'),('AP','法术伤害'),('ADC','下路射手'),('CD','冷却时间')]
def plain(s):
    for a,b in terms:s=s.replace(a,b)
    s=re.sub(r'(?<![A-Za-z])R(?![A-Za-z])','大招',s)
    s=re.sub(r'(?<![A-Za-z])Q(?![A-Za-z])','一技能',s)
    s=re.sub(r'(?<![A-Za-z])W(?![A-Za-z])','减速技能',s)
    return s
for q in d['questions']:
    if q['theme']=='lol':
        for k in ['title','scene','chapterName']:q[k]=plain(q[k])
        for o in q['options']:o['text']=plain(o['text'])
        if q.get('branches'):q['branches']={k:plain(v) for k,v in q['branches'].items()}
        q['tip']= {'collector':'收集者是一件输出装备。队伍还需要有人挡伤害，题里的“必须出”是玩梗。','double-laugh':'二段笑是小虎的经典表情梗。没看过原图，也按自己的反应选就好。','tes-top':'滔博陀螺源于队标与被动挨打的网友二创，这里把你放进逆风现场。','flash-wall':'闪现能快速挪一小段。追人前先看墙和队友，别把自己闪进包围圈。','golden-time':'金身能让角色短暂无法被攻击；结束后仍要继续走位。'}.get(q['chapter'],'')
for q in d['questions']:
    if q['id']=='hex-collector-0':q['options'][2]['text']='必须出收集者！四个队友都出了，我能不出？'
    if q['id']=='hex-collector-audit-0':q['options'][0]['text']='必须出收集者，五个人就是要整整齐齐'
    if q['id']=='hex-collector-1':q['branches']['2']='你喊完“必须出收集者”，五把枪齐了，对面五个人却一起压过来。你怎么办？'

# New League chapters mix familiar Worlds knowledge, jokes and easy laning habits.
sig={o['behavior']:o['signals'] for q in d['questions'] if q['theme']=='lol' for o in q['options']}
def episode(chapter,name,tip,rows):
    for i,(title,choices) in enumerate(rows):
        q=dict(id=f'rift-{chapter}-{i}',theme='lol',series='rift',chapter=chapter,chapterName=name,stage=i,scene=['开场','接梗','临场','收尾'][i],title=title,tip=tip,importance=1.25 if i==0 else 1,options=[dict(id=j,text=t,behavior=b,signals=sig[b],tags=[b]) for j,(b,t) in enumerate(choices)])
        old=next((x for x in d['questions'] if x['id']==q['id']),None)
        if old:old.update(q)
        else:d['questions'].append(q)
episode('worlds-party','S赛客厅总决赛','S赛就是英雄联盟全球总决赛。题目问你怎么接梗，不考年份。',[
 ('朋友第一次看S赛，问“为什么大家都等金色的雨”，你会？',[('explain','先讲夺冠庆祝，再补两张表情包'),('laugh','先发二段笑，让他感受一下气氛'),('protect','陪他看，没看懂就慢慢解释'),('chaos','先把家里灯开成金色，仪式必须到位')]),
 ('比赛领先一点，朋友已经拿起香槟。你怎么接？',[('calm','基地还没倒，先坐下'),('laugh','先笑第一段，第二段等结算'),('plan','看看队友装备，再说这波稳不稳'),('chaos','香槟先别开，录像先开')]),
 ('决胜局开始，弹幕一半“稳了”一半“别急”。你会？',[('calm','先看比赛，不被弹幕带着跑'),('mechanics','盯着选手怎么躲技能'),('protect','给紧张的朋友递杯水'),('explain','暂停一下，我讲讲刚才为什么没追')]),
 ('冠军举杯那一刻，群里让你配一句。你选？',[('mechanics','这波操作，值得重播一整晚'),('laugh','现在二段笑可以完整播放了'),('protect','五个人都在，才有这场金雨'),('reset','截图存好，明年还一起看')]),
])
episode('lane-basics','对线先别急','对线就是在同一条路上与对手交手。先少挨打，再想着打赢。',[
 ('对手血量比你多，还追着你点表情。你先做什么？',[('calm','不被表情带走，先躲掉他的技能'),('gold','先拿眼前小兵的金币'),('engage','等队友靠近，再找机会打回去'),('chaos','表情回一个，气势可以先赢')]),
 ('对方刚把最危险的技能打空了，你会？',[('mechanics','趁他还没恢复，打一下就退'),('gold','趁这会儿把小兵的钱拿稳'),('plan','先看他旁边有没有帮手'),('chaos','这一秒感觉我能打十个')]),
 ('你只剩一点血，队友说“再吃一波兵就走”。你会？',[('retreat','先回家，别把这点钱换成复活倒计时'),('gold','站远一点，只拿安全的钱'),('protect','告诉队友我先走，他也别硬上'),('int','都说再一波了，不打不是人')]),
 ('这一局结束，你最想留下哪个小习惯？',[('plan','对方技能没了，再找机会打'),('mechanics','尽量躲技能，少站着硬吃'),('gold','拿到钱还得活着花'),('explain','先别急，我这把真的学到了一点')]),
])
episode('look-map','小地图救我一命','小地图在屏幕角落。看见对手不见了，先往安全的地方退。',[
 ('你正追着对手打，突然发现别的敌人都没露面。你会？',[('vision','先瞟一眼小地图'),('retreat','往自己防御塔退一点'),('protect','提醒旁边的队友也小心'),('chaos','追都追到这里了，镜头别停')]),
 ('队友发了危险信号，你还差一下就拿到击杀。你会？',[('calm','先听一次劝，不赌草里没人'),('mechanics','只在安全距离打，不继续往里追'),('collector','最后一下很重要，但命也挺贵'),('int','今天必须收下这个人头')]),
 ('草里果然出来两个人，你的队友也在往这边赶。你会？',[('control','留能拦人的技能，等队友接应'),('retreat','先跑向队友，不往更黑的地方钻'),('protect','把危险位置标出来'),('chaos','边跑边亮表情，至少看起来不慌')]),
 ('朋友问你怎么突然稳了，你会说？',[('vision','因为我终于想起小地图不是装饰'),('plan','能活着拿到的钱，才是真的钱'),('explain','来，我给你指一下刚才两个人从哪出来'),('reset','下局你提醒我，我提醒你')]),
])
episode('ig-memory','冠军合照与青春','IG在2018年的S8夺冠。这里从共同记忆出发，选你自己的反应。',[
 ('群里有人发出IG夺冠合照，问“那年的你在哪”。你会？',[('explain','讲一段自己当时看比赛的故事'),('laugh','先发一句“我的青春回来了”'),('protect','把当年一起看的人都叫出来'),('chaos','立刻把合照做成群头像候选')]),
 ('大家争论最想重看哪一种镜头，你选？',[('mechanics','极限躲技能之后打回去的操作'),('engage','五个人一起往前冲的那一波'),('protect','有人回头救队友的那一秒'),('plan','不乱打，等到好机会才出手')]),
 ('朋友说“我上我也行”，还真打开了游戏。你会？',[('calm','先打一把人机，嘴和手慢慢同步'),('mechanics','一起练两个简单动作'),('protect','陪他打，别上来就催他'),('chaos','录像开了，今晚素材靠你了')]),
 ('重新打完一局，你给青春续哪一句？',[('plan','记忆可以热血，操作还得认真'),('laugh','笑归笑，能一起玩就挺好'),('protect','当年一起看，现在一起排'),('reset','下一局继续，青春还有续杯')]),
])
episode('skin-vote','冠军皮肤选哪位','冠军皮肤是夺冠纪念。这里玩的是“要是你夺冠了”的平行宇宙。',[
 ('平行宇宙的你拿了S赛冠军，终于轮到你选纪念皮肤。你会？',[('mechanics','选最能代表我操作的那个英雄'),('protect','选陪队友一起赢到最后的那个'),('laugh','选能配上二段笑的，仪式感拉满'),('chaos','选完再问能不能带个搞笑回城动作')]),
 ('设计师问“你想加什么个人彩蛋”，你会？',[('explain','加一句我说了很多年的口头禅'),('collector','偷偷放五把收集者，懂的都懂'),('protect','把四个队友也藏进小细节'),('chaos','回家时跳个谁都模仿不了的舞')]),
 ('朋友想照着你的冠军打法玩，但第一次不太顺。你会？',[('calm','冠军是一步步练出来的，先别急'),('mechanics','先教一个最实用的小动作'),('protect','我陪你试，先把快乐找回来'),('explain','先看回放，不急着抄完整套')]),
 ('皮肤终于上线，群里让你发宣传词。你写？',[('mechanics','操作自己练，冠军梦可以一起做'),('collector','必须出收集者，必须把纪念收齐'),('protect','这一次，把五个人的名字留住'),('laugh','现在可以放心笑第二段了')]),
])
episode('collector-pact','必须出收集者','“队友出了我也出”是团伙出装梗。按你真实会做的反应选。',[
 ('四个队友亮出了收集者，还齐声问你“差你这一把，出不出”。你会？',[('collector','必须出收集者！一家人就是要整整齐齐'),('protect','你们四个负责收，我负责挡一下'),('plan','先看看我这角色适不适合，再说出不出'),('chaos','先截图，五把枪的节目不能白整')]),
 ('五个人开始抢最后一下，你的第一反应是？',[('collector','自己的收集者，自己争取那一口'),('protect','先看谁快倒了，不让他白挨打'),('mechanics','打得到谁打谁，不穿人群追残血'),('laugh','语音先笑一下，再记得按技能')]),
 ('对面一起压过来，五把枪看起来都很贵。你会？',[('plan','先退到能一起守的位置'),('protect','我挡第一轮，你们往后站'),('collector','能安全收一个就收，别白给'),('int','装备这么整齐，这波必须冲')]),
 ('赛后群聊里，这套出装你想怎么命名？',[('collector','必须出收集者·五人限定版'),('plan','复制梗可以，赢法还得自己想'),('protect','四把枪一个盾，谁用谁知道'),('chaos','伤害另议，节目效果满分')]),
])

# Non-League themes use independent six-axis scales with semantic behavior tags.
d['questions']=[q for q in d['questions'] if q['theme']=='lol']
def questions(theme,dim,rows):
    assert len(rows)==12,(theme,dim,len(rows))
    for n,(scene,title,choices) in enumerate(rows,1):
        assert len(choices)==4
        d['questions'].append(dict(id=f'{theme}-{dim}-{n}',theme=theme,dim=dim,scene=scene,title=title,options=[dict(id=i,text=t,value=i+1,behavior=b,tags=[b]) for i,(b,t) in enumerate(choices)]))

questions('basket','social',[
 ('球场摇人','球场四缺一，群里只回了一个“在”。你会？',[('nba-safe','等一会儿，不主动喊'),('nba-team','问两个熟人'),('nba-team','开始拉人凑局'),('nba-show','连隔壁场的都招呼过来')]),
 ('老大开练','朋友说“老大叫你凌晨四点练球”，你第一反应？',[('nba-calm','我先睡醒再练'),('nba-train','自己早一点到场'),('nba-train','叫个熟人一起练'),('nba-train','把五个人都喊来，嘴硬也得出勤')]),
 ('金闪闪首发','你当金闪闪队临时队长，怎么介绍队友？',[('nba-calm','报个名字就行'),('nba-plan','先讲清每个人的位置'),('nba-team','夸夸大家各自擅长的'),('nba-show','给五个人都配上场音乐')]),
 ('勒邦詹氏上线','群里有人把你备注成“勒邦詹氏”，你会？',[('nba-calm','默默接受'),('nba-show','回一个表情'),('nba-team','顺手给队友也取外号'),('nba-show','直接做一张五人首发海报')]),
 ('裤衩子来局','朋友说“裤衩子来了，今晚三分管够”。你会？',[('nba-calm','我先在场边看看'),('nba-three','拿球自己试两个'),('nba-team','叫大家给射手传传球'),('nba-show','当场宣布停车场进入射程')]),
 ('赛后合照','刚赢一场野球，大家准备合照。你站哪？',[('nba-calm','边上就挺好'),('nba-safe','站熟人旁边'),('nba-team','先把没入镜的拉进来'),('nba-show','中间摆个全队最离谱的姿势')]),
 ('约老师下班','赢球后有人说“约老师要回去看马了”。你会？',[('nba-calm','点头，大家各回各家'),('nba-plan','先问下次几点'),('nba-team','约一顿饭再散'),('nba-show','办一场只有一分钟的颁奖典礼')]),
 ('乔丹争论','饭桌上开始争“历史第一”，你怎么加入？',[('nba-calm','先听他们聊'),('nba-plan','有印象的再说，不乱编数据'),('nba-team','把各自喜欢的点聊明白'),('nba-show','先问今天谁是本桌气氛第一')]),
 ('华子来扣篮','第一次跟特别能跳的球友同队，你会？',[('nba-safe','先适应一下他的节奏'),('nba-dunk','给他一个好传球'),('nba-team','介绍给队友认识'),('nba-show','起个“本小区华子”的外号')]),
 ('邓肯式笑容','队友面无表情打完一场好球，你会？',[('nba-calm','懂他，不催他营业'),('nba-team','拍一下肩就够'),('nba-team','拉他来合照'),('nba-show','我替他笑，把表情包承包了')]),
 ('一代看一代','长辈喜欢乔丹，你朋友喜欢现役球员。你会？',[('nba-calm','各看各的也不错'),('nba-plan','交换一段代表回放'),('nba-team','拉大家一起看一场'),('nba-show','做一张跨时代金闪闪队阵容表')]),
 ('球场新朋友','一个新球友一直不太敢要球，你会？',[('nba-safe','先让他慢慢适应'),('nba-team','给他传一个简单球'),('nba-team','主动叫他一起跑一段'),('nba-show','给他第一球安排全队欢呼')]),
])
questions('basket','explore',[
 ('停车场射程','朋友说库里在停车场也敢投，你想怎么试？',[('nba-safe','先从近处投稳'),('nba-three','往三分线外试一步'),('nba-three','挑一个没投过的远点'),('nba-show','先找停车位，再找篮筐方向')]),
 ('文班的手','看完文班亚马长臂封盖，你最想模仿什么？',[('nba-plan','先学他的站位'),('nba-safe','试着判断球飞哪'),('nba-alien','用自己的臂展去干扰'),('nba-alien','幻想把篮筐装进伸缩臂服务区')]),
 ('大鲨鱼罚球','朋友请你给奥尼尔式罚球想个新招。你会？',[('nba-train','先把同一个动作练熟'),('nba-plan','改一个最明显的小问题'),('nba-dunk','试个自己舒服的新节奏'),('nba-show','进不进另说，仪式必须整齐')]),
 ('约老师传球','看见约基奇的奇怪角度传球，你会？',[('nba-safe','先传最稳的那条路线'),('nba-plan','看懂他为什么那样传'),('nba-team','叫队友一起试一次'),('nba-show','脑子会了，球先替脑子去探路')]),
 ('华子起飞','你看到爱德华兹的扣篮回放，最想尝试？',[('nba-train','先把起跳动作练明白'),('nba-dunk','试个小一点的上篮变化'),('nba-dunk','找合适高度练一段扣篮动作'),('nba-show','先把我的起飞BGM选好')]),
 ('哈登后撤步','你准备学一个后撤步动作，怎么开始？',[('nba-train','先把脚步站稳'),('nba-plan','慢动作拆开看'),('nba-three','试一下拉开距离出手'),('nba-show','先后退三步，气势比距离更远')]),
 ('跨时代合体','能借一位球星的一项本领，你选？',[('nba-plan','邓肯一样稳定的基本动作'),('nba-train','科比那种反复练球的劲'),('nba-three','库里式超远手感'),('nba-alien','文班式伸手就像开了大地图')]),
 ('罗德曼抢板','你看篮板高手只盯落点，最想研究？',[('nba-plan','他为什么站在那里'),('nba-rebound','球碰框以后会往哪跳'),('nba-rebound','怎么给队友卡出空间'),('nba-show','能不能给每个篮板配吸尘音效')]),
 ('没有标准动作','朋友投篮姿势很怪，但总能进。你会？',[('nba-safe','先把自己的动作投稳'),('nba-plan','看看他稳定在哪'),('nba-train','试一试其中适合我的细节'),('nba-show','动作不重要，进球后得有表情')]),
 ('球衣号码','金闪闪队让你挑号码，你会？',[('nba-calm','挑一个自己喜欢的'),('nba-train','选24，提醒自己去练球'),('nba-three','选30，给三分加点信仰'),('nba-show','号码可以普通，入场必须特别')]),
 ('训练新花样','教练允许你给训练加一点花样，你会？',[('nba-train','先练原来的基本项目'),('nba-plan','换个更容易坚持的小节奏'),('nba-team','设计一个双人配合小游戏'),('nba-show','把训练剪成金闪闪队预告')]),
 ('总决赛脑洞','平行总决赛让你设计一项额外节目，你选？',[('nba-plan','看一段经典回放'),('nba-train','球星带大家练一个动作'),('nba-team','现役和退役球员混合组队'),('nba-show','球员用自己的表情包介绍自己')]),
])
questions('basket','empathy',[
 ('勒邦跪地','朋友模仿勒邦詹氏跪地抱怨漏判，大家笑完以后你会？',[('nba-plan','先把刚才那球说清楚'),('nba-calm','示意先回到比赛'),('nba-team','拉他起来继续打'),('nba-emotion','先接住他的委屈，再一起笑')]),
 ('关键球投丢','队友投丢最后一球，一个人坐着。你会？',[('nba-plan','一起看出手选择'),('nba-calm','给他一点安静时间'),('nba-team','说下次我们还传给你'),('nba-care','先坐旁边，听他说完')]),
 ('老大训练日','朋友练了一晚没练好，说自己太菜。你会？',[('nba-train','帮他挑一个能改的小动作'),('nba-plan','说明谁也不是一天练会'),('nba-team','陪他投到约好的时间'),('nba-care','先说今天这份坚持我看见了')]),
 ('裤衩子失准','平时最准的人今天三分一直不进，你会？',[('nba-plan','建议他先换近一点的位置'),('nba-calm','告诉他不用急着证明'),('nba-team','给他一次舒服的接球机会'),('nba-care','先问是不是状态不太好')]),
 ('篮板没人夸','有人抢了好多篮板，赛后却没人提他。你会？',[('nba-plan','把篮板数据记下来'),('nba-rebound','告诉大家这些回合从哪来的'),('nba-team','主动把他拉到合照中间'),('nba-care','当面谢谢他那些没镜头的活')]),
 ('姚明式笑脸','朋友被做成表情包，笑着说没关系。你会？',[('nba-plan','先确认照片不会被误用'),('nba-calm','不再往外扩散'),('nba-team','私下问他介不介意'),('nba-care','认真听他真实的感受')]),
 ('新手被断球','新队友刚上场就连丢两个球。你会？',[('nba-plan','教他一个护球的小办法'),('nba-safe','让他先做最简单的事'),('nba-team','下一回合照样给他传球'),('nba-care','先说别怕，大家都这样过')]),
 ('板凳席等待','朋友整场没怎么拿到球，赛后有点闷。你会？',[('nba-plan','想想下场怎么分配回合'),('nba-calm','先让他缓一会儿'),('nba-team','下次专门给他安排一次配合'),('nba-care','先问今天哪一段最难受')]),
 ('裁判争议','两队因为一声哨子吵起来，你会？',[('nba-plan','复述刚才实际发生的动作'),('nba-calm','先把音量降下来'),('nba-team','提议用大家都接受的方式继续'),('nba-care','先让最激动的人把话说完')]),
 ('冠军与配角','有人说“只有拿分的人才有用”。你会？',[('nba-plan','举一个配合创造机会的例子'),('nba-rebound','聊聊挡人和抢板'),('nba-team','让大家说说今天谁帮过自己'),('nba-care','先照顾被这句话刺到的人')]),
 ('华子失误','年轻队友想扣篮却没成功，你会？',[('nba-train','帮他看起跳和落点'),('nba-safe','先确认有没有受伤'),('nba-team','告诉他下次有好机会还传'),('nba-care','先把人扶稳，其他等会儿说')]),
 ('输球群聊','输了以后群里有人只怪自己，你会？',[('nba-plan','把能改和不能改的分开'),('nba-calm','提醒一场球不是全部'),('nba-team','说我们一起赢也一起输'),('nba-care','先私聊陪他说会儿话')]),
])
questions('basket','action',[
 ('最后一攻','最后一攻到了，你面前有一点空位。你会？',[('nba-plan','先看队友有没有更好机会'),('nba-safe','确认脚步站稳再动'),('nba-drive','抓住空当就往里走'),('nba-clutch','机会到手就出手，赛后再解释')]),
 ('凌晨四点闹钟','“老大训练闹钟”响了，你会？',[('nba-calm','先规划今天什么时候练'),('nba-train','洗漱好再去'),('nba-train','拿球就到楼下'),('nba-train','人到球场了，脑子还在开机')]),
 ('三分有空','传球到了，面前没人防，你会？',[('nba-plan','再看一眼整体位置'),('nba-three','站好投一个'),('nba-three','手感在就直接投'),('nba-three','投完才想起刚才站得挺远')]),
 ('快攻来球','队友把球传到你面前，你会？',[('nba-plan','先看追防和篮筐距离'),('nba-safe','稳稳接住再走'),('nba-drive','加速冲向篮下'),('nba-dunk','能完成就上，脑内先放华子回放')]),
 ('篮板机会','球弹到你附近，你会？',[('nba-plan','先找最有利的位置'),('nba-rebound','卡住位置再伸手'),('nba-rebound','往落点再抢一步'),('nba-rebound','球还没落地，我已经过去了')]),
 ('突破还是传','你面前有缝，旁边队友也在要球，你会？',[('nba-plan','看清防守再做选择'),('nba-team','先给队友一个机会'),('nba-drive','先突破一步把人吸引过来'),('nba-clutch','这一球我来，机会过了就没了')]),
 ('暂停结束','暂停刚结束，队友还没完全回神，你会？',[('nba-plan','再确认一次打法'),('nba-team','提醒大家站好位置'),('nba-drive','先带着队伍跑起来'),('nba-show','边上场边喊，全队进入大戏模式')]),
 ('关键防守','对面最后一攻往你这边来，你会？',[('nba-plan','先看他想往哪走'),('nba-safe','站稳，不轻易跳'),('nba-team','提醒身后队友补一下'),('nba-alien','时机一到就伸手，挑战文班服务区')]),
 ('老将来了','一位老球友邀你一起练基本动作，你会？',[('nba-plan','先问练什么、练多久'),('nba-train','准备好再开始'),('nba-train','先练一轮找感觉'),('nba-train','来都来了，练完再说累')]),
 ('球快出界','球就要滚出边线，你会？',[('nba-safe','先看有没有安全救球空间'),('nba-plan','判断救回来会给到谁'),('nba-team','喊队友接一下'),('nba-drive','安全能救就冲，脚先迈出去')]),
 ('华子挑战','朋友问“这球你敢不敢试”，你会？',[('nba-plan','先看自己确实能做什么'),('nba-safe','选稳一点的做法'),('nba-dunk','降低难度试一次'),('nba-dunk','能安全完成就来，先把勇气拉满')]),
 ('夺冠合影','金闪闪队赢了，摄影师倒数三秒，你会？',[('nba-calm','站好就行'),('nba-team','把队友都拉进画面'),('nba-show','立刻摆个招牌动作'),('nba-show','三秒内完成三种表情')]),
])
questions('basket','order',[
 ('赛前排位置','金闪闪队第一次凑齐，你会？',[('nba-show','先打起来再认识'),('nba-team','大概说一下谁做什么'),('nba-plan','把常用配合讲清楚'),('nba-plan','连换人和最后一攻也安排好')]),
 ('训练计划','你准备学科比的认真劲，怎么排训练？',[('nba-show','有空就去投几个'),('nba-train','每天先练一点'),('nba-train','固定几项基本训练'),('nba-train','把投篮、脚步和休息都安排好')]),
 ('总决赛观赛','朋友来你家看NBA总决赛，你会？',[('nba-show','来了再说'),('nba-team','买点喝的就行'),('nba-plan','提前调好画面和座位'),('nba-plan','时间、零食、回放和散场都准备好')]),
 ('约老师传球课','你想练一套传球配合，怎么开始？',[('nba-show','凭感觉跑起来'),('nba-team','先试最简单的一种'),('nba-plan','约好手势和跑位'),('nba-plan','连对手不配合时怎么改也想好')]),
 ('篮板分工','队伍总是五个人一起盯着球落地，你会？',[('nba-show','谁近谁抢吧'),('nba-rebound','先提醒大家动起来'),('nba-plan','分清谁卡人谁拿球'),('nba-plan','拿到球后传给谁也一起说清')]),
 ('关键球准备','你想提高最后一球的把握，你会？',[('nba-show','到时看手感'),('nba-train','多投几个熟悉的位置'),('nba-clutch','固定练几种常用出手'),('nba-plan','把时间、脚步和传球路线一起练')]),
 ('外号登记','大家外号越取越多，群里快认不清人了，你会？',[('nba-show','越乱越好玩'),('nba-team','叫得顺口就行'),('nba-plan','在群公告放一张阵容表'),('nba-plan','号码、位置、外号一次写明白')]),
 ('球衣装备','出门打球前你怎么收包？',[('nba-show','拿到什么带什么'),('nba-safe','球鞋和水先带上'),('nba-plan','衣服、球、护具分好'),('nba-plan','连换洗和回程都一起准备')]),
 ('邓肯基本功','朋友嫌基本动作太无聊，你怎么劝？',[('nba-show','那先玩会儿再说'),('nba-team','一人陪他练十分钟'),('nba-train','选两个最实用的反复练'),('nba-plan','做个能坚持的计划，稳一点也能赢')]),
 ('赛后复盘','比赛结束后，你怎么记住问题？',[('nba-show','快乐就行，不记了'),('nba-calm','只留一个最有印象的'),('nba-plan','写下两三个能改的点'),('nba-plan','下次练什么、怎么检验都排好')]),
 ('退役球星梦之队','组一支跨时代五人队，你最先考虑？',[('nba-show','五个都要最有节目效果'),('nba-team','先把喜欢的人凑齐'),('nba-plan','位置别全挤一块'),('nba-plan','出手、传球、防守和替补想完整')]),
 ('现役观察表','今年准备多看几位年轻球员，你怎么选？',[('nba-show','谁回放好看就看谁'),('nba-dunk','先挑一位有冲劲的'),('nba-plan','不同位置各挑一个'),('nba-plan','看一段时间，记下进步再下结论')]),
])
questions('basket','express',[
 ('裤衩子庆祝','三分进了，你怎么庆祝？',[('nba-calm','转身回防就行'),('nba-three','轻轻做个晚安手势'),('nba-show','给队友一个明显回应'),('nba-show','球刚进，全套表情已经开播')]),
 ('勒邦情绪','争议哨响了，你怎么表达？',[('nba-calm','先忍住，继续打'),('nba-plan','找机会把这一球说清楚'),('nba-emotion','表情写满“我不理解”'),('nba-emotion','膝盖先软一下，站起来还得回防')]),
 ('老大回放','群里发了科比经典回放，你会？',[('nba-calm','看完自己记住'),('nba-train','回一句，明天练这个'),('nba-clutch','讲讲最后一球为什么难'),('nba-show','当场开麦，热血解说拉满')]),
 ('虎扑式评分','让你给本场自己打分，你会？',[('nba-calm','心里有数就行'),('nba-plan','说一个亮点一个问题'),('nba-show','认真写一句赛后评语'),('nba-show','满分给节目，失误另开一页')]),
 ('文班长臂','有人夸你防守范围大，你会？',[('nba-calm','笑一笑就过了'),('nba-team','说队友补得也好'),('nba-alien','做个长臂展开的手势'),('nba-show','宣布这一小块归外星人管理')]),
 ('华子起飞后','完成一次漂亮上篮，队友都在看你，你会？',[('nba-calm','赶紧回防'),('nba-team','跟传球的人击个掌'),('nba-dunk','做个小小的起飞动作'),('nba-show','眼神先巡视全场，再假装没庆祝')]),
 ('约老师领奖','拿到一张最佳队友贴纸，你会？',[('nba-calm','收好，继续收包'),('nba-team','谢谢大家就行'),('nba-show','拍照发群里'),('nba-show','先问颁奖能不能快点，我还有马要看')]),
 ('邓肯被夸','朋友说你今天特别稳，你会？',[('nba-calm','面无表情地点个头'),('nba-team','微笑说大家也不错'),('nba-plan','聊两句今天做对的选择'),('nba-show','我替面无表情的自己配一段欢呼')]),
 ('乔丹式定格','要给一个进球选封面，你会？',[('nba-calm','留着自己看'),('nba-train','挑动作最清楚的'),('nba-clutch','挑最后出手那一刻'),('nba-show','挑最像海报主角的那个表情')]),
 ('奥尼尔节目','赛后让你和朋友拍搞笑短片，你会？',[('nba-calm','我在旁边笑就行'),('nba-team','配合出个镜'),('nba-show','主动接一段台词'),('nba-show','人还没开拍，我已经演完第一集')]),
 ('姚明表情包','你的笑脸被队友截成表情包，你会？',[('nba-calm','自己保存一张'),('nba-team','只在熟人群用用'),('nba-show','配一句我今天的心情'),('nba-show','亲自做成金闪闪队表情包系列')]),
 ('冠军宣言','平行NBA总冠军让你讲一句话，你说？',[('nba-calm','谢谢，能一起打球就很好'),('nba-team','这一队谁都不能少'),('nba-clutch','下一场关键球，我还敢接'),('nba-show','戒指先戴，段子我们边走边讲')]),
])

# Abstract questions are actual content-making / social situations, not random talking furniture.
questions('abstract','social',[
 ('前奏一响','刷到“摇一摇”舞蹈，朋友问要不要一起拍，你会？',[('web-watch','我先看你跳'),('web-dance','只跟熟人扭两下'),('web-dance','拉两个人一起练'),('web-dance','五人站好，群舞导演上线')]),
 ('翻唱起局','朋友开了翻唱房，麦克风递过来了，你会？',[('web-watch','先听大家唱'),('web-cover','跟熟人合一句'),('web-cover','唱一小段给大家听'),('web-live','直接把今晚唱成个人小专场')]),
 ('峰哥出门','峰哥式旅行群临时说“走不走”，你会？',[('web-watch','先看他们去哪'),('web-travel','问问一个熟人'),('web-travel','主动一起约时间'),('web-live','把出发讲成连续更新的第一集')]),
 ('自媒体搭子','准备拍一个短视频，还缺四个队友，你会？',[('web-watch','先自己试着拍'),('web-plan','约两个熟悉的人'),('web-live','主动凑齐分工'),('web-live','导演摄影演员气氛组一口气全喊齐')]),
 ('好果汁聚会','虎刀梗把群里人都逗乐了，你会？',[('web-watch','默默保存表情包'),('web-meme','只回一句熟悉的梗'),('web-punchline','接一段自己的吐槽'),('web-live','现场给大家演个特别版')]),
 ('不讲不讲','大家玩“不讲不讲”的问答梗，你会？',[('web-watch','先听几轮'),('web-meme','跟熟人接一句'),('web-punchline','换个自己的问题'),('web-live','把整群问成一档魔性访谈')]),
 ('进城办事','朋友约你拍“进城办事”风格日常，你会？',[('web-watch','看看成片就好'),('web-travel','和熟人走一小段'),('web-travel','主动约路线和地点'),('web-live','把五个人拍成临时出差小队')]),
 ('活人感群聊','群聊安静太久，你想发点什么？',[('web-watch','不强行找话'),('web-original','发一件今天真实的小事'),('web-care','问问朋友最近怎么样'),('web-punchline','用自己的翻车现场重新点亮全群')]),
 ('豆包型搭子','朋友说“你情绪真稳，适合当我的搭子”，你会？',[('web-watch','先安静听完'),('web-care','陪他把这件事聊完'),('web-care','有空就一起把小问题解决'),('web-live','当场给五个人都安排一个轻松开场')]),
 ('合拍邀请','陌生创作者想和你合拍舞蹈，你会？',[('web-watch','先看看对方内容'),('web-plan','了解怎么拍再决定'),('web-dance','试拍一小段找默契'),('web-live','把简单合拍做成一期跨界联动')]),
 ('评论区认亲','有人留言“同款抽象人格，交个朋友”，你会？',[('web-watch','点个赞就好'),('web-meme','回个只有同频的人懂的梗'),('web-care','聊两句他为什么有共鸣'),('web-live','拉他进下一期节目，观众变队友')]),
 ('线下相见','平时只在群里玩梗的人终于见面，你会？',[('web-watch','先听大家说'),('web-meme','拿一个熟悉的老梗开场'),('web-care','照顾一下还没放开的朋友'),('web-live','正式宣布网络人终于加载到现实')]),
])
questions('abstract','explore',[
 ('摇一摇二创','同一段舞蹈已经看了十个版本，你想做？',[('web-watch','先把喜欢的收藏好'),('web-dance','学最容易的一小段'),('web-edit','剪一个不同节奏的版本'),('web-original','用自己的角色和动作重新玩一次')]),
 ('翻唱改编','一首热门歌听熟了，朋友让你翻唱，你会？',[('web-cover','先按原来的舒服调唱'),('web-cover','换个适合自己的音调'),('web-edit','试一个新的伴奏感觉'),('web-original','用自己的表达改编，不照抄别人的成片')]),
 ('邪修拍法','看到一个特别省事的“邪修拍摄法”，你会？',[('web-watch','先看完整过程'),('web-plan','确认不会影响成片再试'),('web-edit','拿旧素材做一个小实验'),('web-original','用身边的普通道具另整一套')]),
 ('李子柒式镜头','一段安静手作视频特别耐看，你想学什么？',[('web-watch','先看懂它在做什么'),('web-craft','学一个小小的手工步骤'),('web-edit','试着拍出过程和细节'),('web-craft','从准备材料到完成，全程自己做一次')]),
 ('城巴佬发现','刷到“城巴佬”梗，你发现自己也不认得某种菜，你会？',[('web-watch','先认真查清楚'),('web-travel','下次去菜场看看'),('web-original','拍一段真实的学习记录'),('web-live','做一期从认菜到做饭的特别节目')]),
 ('预制感太重','别人说你的视频像模板生产线，你会？',[('web-plan','先保留已经清楚的结构'),('web-original','加一段自己的真实经历'),('web-edit','改掉统一配音和重复镜头'),('web-original','重写一版有自己口气的内容')]),
 ('峰哥路线','出门拍旅行日常，你想选哪里？',[('web-watch','先走熟悉的那条路'),('web-travel','去附近没逛过的小店'),('web-travel','挑一个完全陌生的街区'),('web-original','不追景点，去找只有当地人才知道的小故事')]),
 ('旧梗回锅','一个老梗突然又火了，你会？',[('web-watch','先看看这次为什么火'),('web-meme','用一次刚好合适的场景'),('web-edit','给老梗换一个新剪辑节奏'),('web-original','只借一个点，写成自己的新故事')]),
 ('不拍完美','相机里有一段意外笑场，你会？',[('web-plan','先放进备选'),('web-original','留一点真实反应'),('web-edit','试着把笑场剪成转场'),('web-live','干脆用笑场开启整期节目')]),
 ('声音也能整活','一个普通提示音忽然很洗脑，你会？',[('web-watch','听两次就算了'),('web-cover','跟着哼两下'),('web-edit','拿它配一段自己的动作'),('web-original','做个有反转的小作品，笑点自己写')]),
 ('豆包风旁白','大家都在用同一种语气配旁白，你会？',[('web-watch','先看它适不适合这条'),('web-plan','只用一句当调味'),('web-edit','和真实声音混着剪'),('web-original','换成自己的说话方式，让人记住我')]),
 ('全职研究','看到“我将全职研究这个视频”的夸张评论，你会？',[('web-watch','再看一遍找笑点'),('web-plan','记下值得学的一个地方'),('web-edit','拆一下镜头怎么安排'),('web-original','研究完就去做一条自己的')]),
])
questions('abstract','empathy',[
 ('爱你老己','忙完一天，朋友说“爱你老己，辛苦了”，你会？',[('web-plan','先帮他把明天最急的事减下来'),('web-care','提醒他今晚早点休息'),('web-care','陪他做一件轻松的小事'),('web-care','先认真听他今天到底有多累')]),
 ('舞蹈没跟上','朋友跳舞慢半拍，被自己逗笑了，你会？',[('web-plan','把动作放慢再拆开看'),('web-dance','陪他练最容易的一段'),('web-care','告诉他跳得开心也很好看'),('web-care','先确认他真的在笑，而不是勉强撑着')]),
 ('翻唱跑调','朋友翻唱走音，被评论点出来后有点难受，你会？',[('web-cover','帮他换个更舒服的调'),('web-plan','把有用建议和起哄分开'),('web-care','陪他重新录一小段'),('web-care','先让他把难过说出来')]),
 ('丝瓜汤文学','朋友遇到烦心事，你怎么“安慰到点子上”？',[('web-plan','先想清能具体帮什么'),('web-care','不急着说大道理'),('web-care','陪他解决眼前一件小事'),('web-care','先承认这件事确实不好受')]),
 ('做完你的做你的','朋友同时被三个人催更新，你会？',[('web-plan','帮他排一下先后顺序'),('web-care','先替他回一句别急'),('web-care','接走一个力所能及的小活'),('web-care','先给他喘口气，不把梗变成新的催促')]),
 ('评论被误读','一段自嘲被人当成认真发言，你会？',[('web-plan','把上下文补清楚'),('web-original','平静说明自己的本意'),('web-care','先照顾被误会的朋友'),('web-care','听他说清楚为什么这句评论让他难受')]),
 ('热梗用过头','你发的梗让朋友不舒服，你会？',[('web-plan','弄明白边界在哪'),('web-care','先停下来不再发'),('web-care','认真道歉，不拿玩笑当挡箭牌'),('web-care','先听他的感受，再说自己的本意')]),
 ('自媒体低谷','朋友认真做的视频没什么人看，你会？',[('web-plan','一起找一个能改的具体点'),('web-edit','帮他改一个更清楚的开头'),('web-care','陪他把下一条做完'),('web-care','先肯定这份认真，不用播放量定义他')]),
 ('不想出镜','拍群舞时有人说今天不想露脸，你会？',[('web-plan','调整站位和拍法'),('web-edit','安排只拍手或背影的镜头'),('web-care','明确告诉他不拍也没关系'),('web-care','先问他愿不愿意留在现场玩')]),
 ('峰哥旅途累了','一起旅行的朋友突然不想再拍了，你会？',[('web-plan','把剩下安排简化'),('web-travel','改成不赶路的短行程'),('web-care','关掉相机陪他走走'),('web-care','先听他说累在哪里')]),
 ('不是预制的人','有人说自己总怕表现得不够有趣，你会？',[('web-plan','帮他找到一个轻松的表达方式'),('web-original','告诉他真实小事也值得说'),('web-care','陪他拍一条不用演的日常'),('web-care','先让他知道，不整活也可以被喜欢')]),
 ('热闹散场','活动结束后，最会搞气氛的人突然安静了，你会？',[('web-plan','确认他有没有落下东西'),('web-care','让他先安静休息'),('web-care','陪他慢慢收拾'),('web-care','问一句，现在还好吗')]),
])
questions('abstract','action',[
 ('前奏启动','熟悉的舞蹈前奏响了，你会？',[('web-watch','先把动作看清楚'),('web-plan','找个合适的位置'),('web-dance','先跟着扭两下'),('web-dance','人已经开始摇，相机还没打开')]),
 ('翻唱录音键','伴奏放好了，轮到你录第一遍，你会？',[('web-cover','先再熟悉一遍旋律'),('web-plan','试好音量再开始'),('web-cover','先录一小段找状态'),('web-cover','直接开唱，唱错再来一次')]),
 ('灵感来了','想到一个自媒体选题，你会？',[('web-plan','先放进选题清单'),('web-plan','想清最关键的开头'),('web-original','写三句话试试'),('web-live','相机已经开了，先说一遍')]),
 ('峰哥临时出发','朋友说附近有个值得逛的小地方，你会？',[('web-plan','先查清路怎么走'),('web-travel','收拾好必要东西'),('web-travel','拿上手机出门'),('web-live','人到楼下了，开场白边走边想')]),
 ('热梗时效','一个新梗刚刷到第二次，你会？',[('web-watch','先搞懂来龙去脉'),('web-plan','看看它适不适合我'),('web-meme','在合适地方试着用一句'),('web-edit','立刻做一小段自己的二创')]),
 ('群舞开拍','导演倒数三二一，你会？',[('web-plan','先确认从哪个动作开始'),('web-dance','找好节拍再动'),('web-dance','跟着队友先跳起来'),('web-dance','还没数到一，我的前奏已经进身体')]),
 ('手作第一步','准备拍一个李子柒式小手作，你会？',[('web-plan','先看清材料和步骤'),('web-craft','把最必要的材料备好'),('web-craft','先做一个小样'),('web-craft','先动手，做好再补镜头')]),
 ('翻车补救','拍摄到一半，最关键的镜头没录上，你会？',[('web-plan','先想清哪里必须补'),('web-edit','找能用的镜头接起来'),('web-original','换个更容易完成的新讲法'),('web-live','把没录上这件事本身讲成开场')]),
 ('不讲不讲接梗','朋友突然把麦克风递给你，让你接下一句，你会？',[('web-watch','先等别人接'),('web-meme','接一句最熟悉的'),('web-punchline','临时换个自己的包袱'),('web-live','直接把整段接成现场小短剧')]),
 ('剪辑最后一刀','视频差一个结尾就能完成，你会？',[('web-plan','再想想结尾该表达什么'),('web-edit','选最清楚的一种'),('web-edit','先做一个短版试着看'),('web-original','先把有自己味道的版本做完')]),
 ('创作者联动','一个很合适的合作想法出现了，你会？',[('web-plan','先把想法整理清楚'),('web-plan','写好关键内容再联系'),('web-live','先跟熟悉的人试拍一段'),('web-live','立刻约个最小版本，先把事做出来')]),
 ('老己下班','今天该做的事已经完成，下一步你选？',[('web-plan','先想清明天最轻松的安排'),('web-care','把手机放下缓一会儿'),('web-care','去做一件自己喜欢的小事'),('web-care','说走就走，先奖励今天的自己')]),
])
questions('abstract','order',[
 ('群舞分工','五个人要拍“摇一摇”二创，你会？',[('web-dance','先跳，队形边扭边找'),('web-dance','先约好从哪开始'),('web-plan','排好站位和动作顺序'),('web-plan','镜头、音乐、站位、收尾一起排清楚')]),
 ('自媒体周更','准备每周更新一条内容，你会？',[('web-live','有灵感就发'),('web-original','先保证每次都有自己的东西'),('web-plan','留出固定的制作时间'),('web-plan','选题、拍摄、剪辑和休息都安排好')]),
 ('做完你的做你的','大家同时催你交片，你会？',[('web-live','先做顺手的'),('web-care','先安抚最着急的人'),('web-plan','按先后顺序排好'),('web-plan','说明时间和边界，做完一个再做下一个')]),
 ('翻唱拍摄','一首歌准备录正式版，你会？',[('web-cover','唱着找感觉'),('web-cover','先记住最容易错的几句'),('web-plan','把音调、伴奏、收音调好'),('web-plan','连试听、补录和文件备份都安排好')]),
 ('峰哥路线表','旅行日常准备怎么拍？',[('web-travel','走到哪里拍到哪里'),('web-travel','只定一个最想去的地方'),('web-plan','把路线和休息点排好'),('web-plan','连天气变化和返程都留个备选')]),
 ('热梗存档','收藏夹里的梗越来越多，你会？',[('web-meme','能找到就好'),('web-watch','只留下真正喜欢的'),('web-plan','按舞蹈、翻唱、日常分一分'),('web-plan','出处和适用场景一起记好，避免乱用')]),
 ('李子柒式慢工','要拍一件需要耐心的小手作，你会？',[('web-craft','边做边看下一步'),('web-craft','先做最容易开始的部分'),('web-plan','把材料、步骤和等待时间排好'),('web-craft','从制作到镜头都认真留好过程')]),
 ('预制模板改造','拿到一份很常见的短视频模板，你会？',[('web-live','先拍出来再说'),('web-original','换掉最像别人的那一句'),('web-edit','重排内容，让节奏适合自己'),('web-plan','先写自己的结构，再看模板能帮哪一段')]),
 ('评论区回复','评论越来越多，怎么回比较舒服？',[('web-live','看到哪条回哪条'),('web-care','先回认真交流的那几条'),('web-plan','集中一段时间慢慢回'),('web-plan','把问题整理好，不让回复占满一整天')]),
 ('旧素材整理','相册里堆满了没剪过的视频，你会？',[('web-live','随缘翻到哪段算哪段'),('web-watch','先删重复的'),('web-edit','按主题分成几组'),('web-plan','挑能做的列进计划，其他安心存档')]),
 ('拍摄前一晚','明天要拍五人联动，你今晚会？',[('web-live','明天见面再说'),('web-plan','确认时间和地点'),('web-plan','把道具和大致流程写清楚'),('web-plan','连不想出镜的人怎么参与也安排好')]),
 ('休息也排进去','计划越做越满，你会怎么改？',[('web-care','先把自己不想做的划掉'),('web-original','只留下真正想表达的东西'),('web-plan','缩小一轮的目标'),('web-plan','把休息写进计划，别只给更新留位置')]),
])
questions('abstract','express',[
 ('群舞封面','拍完舞蹈，选哪张当封面？',[('web-watch','不公开，自己留着看'),('web-dance','选大家动作最齐的'),('web-original','选最像我们日常的'),('web-live','选笑得最离谱的，封面就先开演')]),
 ('翻唱发布','你第一次录好翻唱，准备怎么分享？',[('web-cover','先留给自己听'),('web-cover','发给一个熟人'),('web-cover','配上自己的感受发出来'),('web-live','连开场和幕后花絮一起安排')]),
 ('峰哥日记','今天出门发现一间有趣的小店，你会？',[('web-watch','自己记住就好'),('web-travel','发张照片给熟人'),('web-original','写一段自己的观察'),('web-live','剪成一集有开头有结尾的旅行日常')]),
 ('活人感开场','视频开头你更想说什么？',[('web-watch','不说话，先把画面给清楚'),('web-original','说一句今天真实发生的事'),('web-punchline','讲一个自己的小失误'),('web-live','镜头一开，今天整段故事都想讲出来')]),
 ('不讲不讲配文','普通日常想配一句有趣文案，你会？',[('web-watch','不配，画面够了'),('web-meme','点到为止地用一句梗'),('web-punchline','写个自己的反转句'),('web-live','把评论区也预演成下集节目')]),
 ('豆包型回复','朋友问“今天怎么样”，你会？',[('web-watch','回一句还行'),('web-care','说一件让自己舒服的小事'),('web-original','认真讲讲真实感受'),('web-punchline','用一段很稳的语气讲最离谱的日常')]),
 ('手作完成','辛苦做好的小东西终于完成了，你会？',[('web-craft','留着自己慢慢看'),('web-craft','拍个成品照给熟人'),('web-original','分享做的过程和心得'),('web-live','拍成一条有细节、有笑场的完整视频')]),
 ('我将全职研究','你刷到一个百看不厌的视频，怎么评论？',[('web-watch','点个赞就结束'),('web-meme','轻轻接一句熟悉的梗'),('web-punchline','说清到底哪一秒戳中我'),('web-live','现场讲一段“我为什么又看了十遍”')]),
 ('爱你老己收尾','一天结束，朋友圈只留一句，你会？',[('web-watch','不发，自己知道就行'),('web-care','今天辛苦了，早点休息'),('web-original','记下一件我认真做到的小事'),('web-punchline','给今天的自己颁一个离谱但真诚的小奖')]),
 ('幕后笑场','观众想看你录制翻车的幕后，你会？',[('web-watch','不一定想公开'),('web-edit','剪一小段自己能接受的'),('web-original','配上当时真实的想法'),('web-live','正片十秒，笑场能剪三分钟')]),
 ('自媒体简介','给自己的新账号写一句介绍，你会？',[('web-watch','先放个名字'),('web-original','说一句我平时真的在做的事'),('web-punchline','用一个自己的小故事介绍'),('web-live','简介字数不够，想直接拍一期')]),
 ('平行宇宙首播','另一个你终于开始第一场直播，你会？',[('web-watch','先和少数熟人聊聊'),('web-care','安静听大家今天过得怎样'),('web-original','讲自己为什么想做这件事'),('web-live','音乐一响，自己的节目正式开播')]),
])

def new_person(id,name,nickname,theme,vector,roles,sub,line,number):
    c=dict(id=theme+'-'+id,personId=id,name=name,nickname=nickname,theme=theme,vector=vector,roles=roles,sub=sub,line=line,number=number)
    if not any(x['id']==c['id'] for x in d['characters']):d['characters'].append(c)
new_person('edwards','安东尼·爱德华兹','华子','basket',[85,85,55,90,65,90],[1,2],'年轻冲劲与起飞服务','能安全起飞就试一次，回防也别忘。','ANT')
new_person('wemby','文班亚马','文班亚马','basket',[55,80,75,80,85,55],[4,3],'长臂展开，篮下进入服务区','胳膊可以长，站位还得认真。','ALIEN')
new_person('liziqi','李子柒','李子柒','abstract',[35,75,90,60,95,40],[2,4],'把普通日常拍成耐看的故事','慢慢做，细节会替你说话。','LZQ')
new_person('shake-director','摇摆导演','摇摆导演','abstract',[95,95,65,95,55,100],[3,1],'本作原创角色 · 舞蹈与镜头一起启动','一听前奏就上线，跳完才想起开相机。','SHAKE')
nick={'kobe':'老大 · 科比','lebron':'勒邦詹氏','curry':'裤衩子 · 库里','jokic':'约老师','shaq':'大鲨鱼','duncan':'石佛 · 邓肯','edwards':'华子','wemby':'文班亚马'}
weights={
 'kobe':{'nba-train':5,'nba-clutch':5,'nba-plan':2},'lebron':{'nba-emotion':5,'nba-drive':4,'nba-team':3},'curry':{'nba-three':5,'nba-show':3},'jordan':{'nba-clutch':5,'nba-train':3,'nba-plan':2},'durant':{'nba-three':4,'nba-clutch':4,'nba-calm':3},'jokic':{'nba-plan':5,'nba-team':5,'nba-calm':4},'westbrook':{'nba-drive':5,'nba-show':4,'nba-emotion':2},'harden':{'nba-three':4,'nba-plan':4,'nba-drive':3},'yaoming':{'nba-team':5,'nba-care':4,'nba-plan':3},'shaq':{'nba-dunk':5,'nba-show':4,'nba-rebound':3},'duncan':{'nba-calm':5,'nba-plan':5,'nba-safe':3},'garnett':{'nba-emotion':4,'nba-rebound':5,'nba-team':3},'doncic':{'nba-plan':5,'nba-three':4,'nba-show':2},'butler':{'nba-clutch':5,'nba-train':4,'nba-team':2},'rodman':{'nba-rebound':5,'nba-show':4},'edwards':{'nba-dunk':5,'nba-drive':4,'nba-show':4},'wemby':{'nba-alien':5,'nba-rebound':3,'nba-plan':2},
 'fengge':{'web-travel':5,'web-original':3,'web-live':3},'huchenfeng':{'web-plan':5,'web-original':3},'huge':{'web-live':5,'web-meme':4,'web-dance':2},'daoge':{'web-meme':5,'web-live':4,'web-punchline':3},'dasima':{'web-plan':5,'web-punchline':3},'sunxiaochuan':{'web-punchline':5,'web-meme':4},'geyou':{'web-watch':5,'web-care':3},'jackie':{'web-dance':4,'web-original':4},'wanglaoju':{'web-original':5,'web-edit':4},'luobenwei':{'web-live':5,'web-dance':3},'zhouyi':{'web-live':5,'web-cover':3,'web-punchline':3},'papi':{'web-punchline':5,'web-original':4,'web-edit':3},'baike':{'web-punchline':4,'web-watch':4,'web-care':2},'liziqi':{'web-craft':5,'web-original':4,'web-plan':3},'shake-director':{'web-dance':5,'web-edit':4,'web-live':3},
}
for c in d['characters']:
    if c['theme']=='basket':c['nickname']=nick.get(c['personId'],c['name'])
    if c['theme']!='lol':c['behaviorWeights']=weights[c['personId']]

labels={'nba-safe':'稳一点再动','nba-calm':'表情很稳','nba-plan':'先看怎么打','nba-train':'老大式加练','nba-clutch':'关键球敢接','nba-three':'三分想象力','nba-show':'赛后节目担当','nba-drive':'先往篮下冲','nba-team':'把队友带上','nba-emotion':'情绪写在脸上','nba-rebound':'篮板不能丢','nba-dunk':'有机会就起飞','nba-alien':'长臂封盖服务','nba-care':'先照顾队友的心情','web-dance':'前奏自动启动','web-cover':'翻唱开麦','web-edit':'剪辑二创','web-travel':'出门找故事','web-care':'先照顾感受','web-punchline':'原创吐槽','web-meme':'接住热梗','web-plan':'把更新排明白','web-original':'拒绝预制感','web-watch':'安静观察','web-live':'镜头一开就营业','web-craft':'耐心做细节'}
d['behaviorLabels'].update(labels)

def card(theme,id,name,effect,joke,vector,weights,people,icon,requires=None,visual=None):
    a=dict(id=id,name=name,effect=effect,punchline=joke,line=joke,vector=vector,bias=[round((v-50)/50,2) for v in vector],behaviorWeights=weights,affinities=people,signatureFor=people,icon=icon,requires=requires or [],fanMade=True,rarity='kPrismatic',category='人物联动',kind='basic',creation='本作原创恶搞设定；人物联动是平行宇宙娱乐创作，不是本人发言。')
    if visual:a['visual']=visual
    old=next((x for x in d['augments'][theme] if x['id']==id),None)
    if old:old.update(a)
    else:d['augments'][theme].append(a)
    return a

# Six new League bonds; the restored Collector remains the five-real-PNG card.
a=next(a for a in d['augments']['lol'] if a['id']=='collector-union');a.update(name='必须出收集者',signatureFor=['uzi'],punchline='队友四把都出了，第五把必须有我的名字。',line='队友四把都出了，第五把必须有我的名字。')
for id,people in {'double-laugh':['xiaohu'],'tes-top':['jackeylove'],'square-lecture':['dasima'],'four-stay-alive':['meiko','ming','baolan'],'champion-script':['uzi','faker']}.items():next(a for a in d['augments']['lol'] if a['id']==id)['signatureFor']=people
lolcards=[('gold-rain','金雨先寄存','领先时暂存你的庆祝。\n基地倒下后，笑容一次性全款到账。','香槟先放下，金雨不会因为你少笑一秒就迟到。',[20,45,35,75,65,90],{'calm':5,'laugh':3,'plan':2},['xiaohu','faker'],['SummonerBarrier','SummonerHeal']),('mini-map','小地图终于开机','每次追人前，小地图轻轻闪一下。\n原来屏幕角落一直能救命。','地图不是装修，队友不在隔壁宇宙。',[10,25,25,85,55,95],{'vision':5,'plan':2},['clearlove','ming'],['item-3363','item-2055']),('one-more-hit','别贪这一下','残血时自动计算“再吃一波”的学费。\n活着离开，奖励一次下波再来的底气。','钱要活着花，嘴硬不包复活。',[10,40,10,65,60,85],{'retreat':5,'calm':2},['letme','baolan'],['item-3111','SummonerHeal']),('lane-umbrella','对线小雨伞','先躲掉对面的危险技能，\n再让你的勇气从伞下探出头。','少挨一套，比多说一句有用。',[25,50,40,55,95,65],{'mechanics':5,'plan':2},['theshy','knight'],['SummonerFlash','SummonerBarrier']),('five-names','五个人的冠军皮肤','每次回头照顾队友，\n纪念皮肤就多藏进一个名字。','冠军合照里，谁也不能少。',[15,25,45,100,65,80],{'protect':5,'heal':2},['meiko','ming'],['item-3190','SummonerHeal']),('s8-rewrite','S8平行宇宙通行证','把“当年如果”兑换成一场架空决胜局。\n这次金色的雨，轮到你来签收。','故事可以重写，操作得自己练。',[35,65,65,65,95,70],{'mechanics':5,'engage':2,'plan':2},['uzi','faker'],['item-3031','item-6676'])]
for id,name,effect,joke,v,w,people,icons in lolcards:card('lol',id,name,effect,joke,v,w,people,0,list(w),dict(layout='row',icons=icons,label='人物联动 · 真实图标梗改'))

existing_basket={'kneel':('nba-emotion',['lebron'],5),'logo':('nba-three',['curry'],2),'board':('nba-rebound',['rodman','garnett'],7),'coffee':('nba-clutch',['jordan','butler'],1),'meme':('nba-show',['shaq','westbrook'],6),'team':('nba-team',['yaoming','jokic'],0)}
for a in d['augments']['basket'][:6]:
    behavior,people,icon=existing_basket[a['id']];a.update(behaviorWeights={behavior:5},affinities=people,signatureFor=people,requires=[behavior],icon=icon)
card('basket','mamba-clock','凌晨四点自动打卡','闹钟一响，嘴硬暂停。\n今晚说过的“我也行”，明早全部折算成加练。','学的是认真劲，睡眠也别欠账。',[45,55,45,95,95,60],{'nba-train':5,'nba-clutch':2},['kobe'],1,['nba-train'])
card('basket','goodnight-three','晚安三分服务','三分进球后，自动给观众盖小被子。\n投丢时，被子先还给自己。','停车场有射程，回防还得自己跑。',[85,95,65,85,65,90],{'nba-three':5,'nba-show':1},['curry'],2,['nba-three'])
card('basket','ant-takeoff','华子起飞许可证','合适机会出现时，勇气提前一步到篮下。\n落地后自动提醒：回防也算高光。','先把动作练好，再给起飞配音乐。',[85,85,50,95,65,90],{'nba-dunk':5,'nba-drive':3},['edwards'],3,['nba-dunk'])
card('basket','alien-arms','文班长臂服务区','展开双臂，篮下进入延长营业。\n对手还在找角度，你已经够到下一帧。','长臂不是借口，站位才是说明书。',[55,80,75,80,85,55],{'nba-alien':5,'nba-rebound':2},['wemby'],4,['nba-alien'])
card('basket','stone-face','邓肯表情省电器','全场情绪波动时，面部保持低功耗。\n该得分该回防，一件没少做。','表情可以下班，基本功一直在线。',[25,35,80,55,95,20],{'nba-calm':5,'nba-plan':2},['duncan'],0,['nba-calm'])
card('basket','horse-shift','约老师准点下班','传球把队友安排明白，\n领奖时只剩一个问题：还赶得上看马吗？','球场都看明白了，下班也得认真。',[45,85,85,65,95,40],{'nba-plan':5,'nba-team':3,'nba-calm':1},['jokic'],7,['nba-plan'])

existing_web={'juice':('web-meme',['huge','daoge'],14),'commentator':('web-plan',['dasima'],10),'portal':('web-travel',['fengge'],15),'sofa':('web-watch',['geyou','baike'],13),'micro':('web-live',['zhouyi','luobenwei'],9),'clipboard':('web-plan',['huchenfeng'],12)}
for a in d['augments']['abstract'][:6]:
    b,people,icon=existing_web[a['id']];a.update(behaviorWeights={b:5},affinities=people,signatureFor=people,requires=[b],icon=icon)
card('abstract','auto-dance','前奏一响自动摇','检测到熟悉前奏，自动加载身体记忆。\n相机没开也能先完成一次全员启动。','人还没进画面，动作已经更新完了。',[95,90,65,95,50,100],{'web-dance':5,'web-edit':2},['shake-director','luobenwei'],8,['web-dance'])
card('abstract','cover-key','翻唱舒适调','把“硬上高音”兑换成适合自己的音调。\n唱错也能变成下一遍更稳的开头。','调可以降，自己的味道不用降。',[65,85,75,80,65,90],{'web-cover':5,'web-original':2},['zhouyi','shake-director'],9,['web-cover'])
card('abstract','no-precut','活人感保鲜膜','移除三句模板台词，\n自动保留一个只有你会有的小细节。','不必演得很完美，先让人认出是你。',[65,95,80,65,80,90],{'web-original':5,'web-edit':3,'web-punchline':1},['papi','wanglaoju'],10,['web-original'])
card('abstract','love-yourself','爱你老己充电站','每次认真照顾自己，回复一点心情电量。\n今日没爆款，也照样准许下班。','更新很重要，你本人也很重要。',[35,50,100,45,65,50],{'web-care':5},['geyou','baike'],13,['web-care'])
card('abstract','one-at-time','做完你的做你的','同时出现三条催更时，\n自动生成一句稳稳的“一个一个来”。','更新可以排队，情绪不用跟着排雷。',[55,65,75,65,100,75],{'web-plan':5,'web-care':2},['huchenfeng','dasima'],12,['web-plan'])
card('abstract','slow-craft','把日常拍成风景','耐心完成一个小步骤，\n普通材料也能拥有自己的主角镜头。','慢一点没关系，细节会自己发光。',[35,75,90,60,95,40],{'web-craft':5,'web-original':2,'web-plan':1},['liziqi'],11,['web-craft'])

for a in d['augments']['lol']:a.setdefault('signatureFor',a.get('affinities',[]))
for a in d['augments']['basket']:
    if a['id']=='team':a['affinities']=a['signatureFor']=['yaoming','jokic','lebron']
    if a['id']=='coffee':a['affinities']=a['signatureFor']=['jordan','butler','durant']
    if a['id']=='logo':a['affinities']=a['signatureFor']=['curry','durant']
    if a['id']=='mamba-clock':a['requires']=['nba-train','nba-clutch']
    if a['id']=='meme':a['behaviorWeights']['nba-drive']=2;a['requires']=['nba-show','nba-drive']
for a in d['augments']['abstract']:
    if a['id']=='slow-craft':a['requires']=['web-craft','web-original']
    if a['id']=='auto-dance':a['affinities']=a['signatureFor']=['shake-director','luobenwei','jackie']
    if a['id']=='love-yourself':a['affinities']=a['signatureFor']=['geyou','baike','yaoming']
    if a['id']=='micro':a['affinities']=a['signatureFor']=['zhouyi','luobenwei','huge']
card('basket','stepback-route','后撤步脑内导航','先退一步，不是退出比赛。\n给出手留空间，也给队友留一条传球路线。','球在手上，下一拍在脑子里。',[60,80,55,65,80,70],{'nba-three':4,'nba-plan':3,'nba-drive':2},['harden','doncic'],0,['nba-three','nba-plan','nba-drive'])
card('abstract','punchline-shield','吐槽弹幕保护罩','把模板吐槽筛掉一层，\n留下只有你会说的那一句。','先看懂场合，再让笑点落地。',[65,80,55,60,65,85],{'web-punchline':5,'web-meme':2},['sunxiaochuan','baike','papi'],14,['web-punchline','web-meme'])
for c in d['characters']:
    c['signaturePerks']=[a['id'] for a in d['augments'][c['theme']] if c['personId'] in a.get('signatureFor',[])]
for x in d['lolSeries']:x['count']=sum(q.get('series')==x['id'] for q in d['questions'] if q['theme']=='lol')
d['counts'].update(questions=len(d['questions']),lolQuestions=sum(q['theme']=='lol' for q in d['questions']),lolChapters=len({(q['series'],q['chapter']) for q in d['questions'] if q['theme']=='lol'}),people=len({c['personId'] for c in d['characters']}),parodyCards=sum(map(len,d['augments'].values())),lolParodyCards=len(d['augments']['lol']))
d['counts']['byTheme']={t:dict(questions=sum(q['theme']==t for q in d['questions']),people=sum(c['theme']==t for c in d['characters']),cards=len(d['augments'][t])) for t in ['lol','basket','abstract']}
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');(R/'assets/parody-cards.json').write_text(json.dumps(d['augments'],ensure_ascii=False,indent=2)+'\n')
print(d['counts'])
