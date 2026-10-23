"""Author V8's connected gameplay episodes and real-icon parody cards.

Run once against V7 data. Re-running updates existing IDs rather than duplicating them.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / 'src/data.json'
d = json.loads(path.read_text())
d['version'] = 8
dims = ['tilt', 'greed', 'risk', 'team', 'craft', 'plan']
signals = {
    'afk': [82,28,8,8,20,15], 'int': [96,22,98,8,45,8],
    'collector': [65,96,68,30,65,30], 'protect': [25,25,50,98,55,75],
    'plan': [15,52,30,72,58,96], 'mechanics': [35,55,65,55,98,60],
    'engage': [60,30,92,75,65,35], 'chaos': [85,35,88,25,55,15],
    'poke': [15,50,12,45,85,75], 'stack': [10,85,15,35,45,100],
    'heal': [5,15,20,100,65,80], 'reset': [50,40,50,45,45,20],
    'ult': [52,62,78,65,85,45], 'gold': [25,98,25,35,55,85],
    'control': [15,30,40,88,70,90], 'retreat': [15,30,8,50,55,85],
    'explain': [50,55,35,40,45,90], 'blame': [85,35,35,3,30,20],
    'laugh': [55,35,60,40,40,20], 'calm': [8,45,25,75,65,95],
    'spin': [65,35,70,45,65,35], 'stasis': [25,35,35,55,85,80],
    'flash': [75,45,95,30,60,12], 'vision': [10,15,25,92,55,95],
}
labels = {'laugh':'二段笑预热','calm':'先别急着庆祝','spin':'逆风陀螺拉扯','stasis':'金身等下一拍','flash':'闪现交个热闹','vision':'先把视野点亮'}
d['behaviorLabels'].update(labels)

def episode(series, chapter, name, rows):
    assert len(rows) == 4
    result = []
    for stage, (scene, title, choices) in enumerate(rows):
        assert len(choices) == 4
        result.append(dict(id=f'{series}-{chapter}-{stage}', theme='lol', series=series,
            chapter=chapter, chapterName=name, stage=stage, scene=scene, title=title,
            options=[dict(id=i, text=text, behavior=b, signals=dict(zip(dims, signals[b])), tags=[b]) for i,(b,text) in enumerate(choices)],
            importance=1.25 if stage == 0 else 1))
    existing = {q['id']:q for q in d['questions']}
    for q in result:
        if q['id'] in existing: existing[q['id']].update(q)
        else: d['questions'].append(q)

# The existing Collector branch remains; every following prompt permits all four reactions.
qmap = {q['id']:q for q in d['questions']}
qmap['hex-collector-2']['options'][1]['text'] = '往前顶，给四个输出留出空间'
qmap['hex-collector-3']['title'] = '这局收集者出了四把起步，推塔却慢了一拍。下局你想改什么？'
qmap['hex-collector-3']['options'][1]['text'] = '先看金币和补刀，塔下局一定拆'

episode('hex','basic','先把技能按明白',[
 ('第一轮选牌','你拿到的三张强化，分别偏普攻、大招、团队保护。英雄没有特殊联动，你先看什么？', [('mechanics','普攻那张，走A才是我的常驻大招'),('ult','大招那张，这把就等一个完美R'),('protect','保护那张，四个队友还缺个兜底的'),('plan','先看技能和阵容，不按稀有度盲选')]),
 ('等级到六','第一场六级团要开了，你想把技能留给谁？',[('mechanics','先用小技能和普攻压血量'),('ult','留R等对方核心进射程'),('control','控住突进，别让后排先倒'),('chaos','技能全亮着，看见人先来一套')]),
 ('技能真空期','刚交完一轮技能，对面前排还在向前走。你怎么接？',[('retreat','先后拉，等下一轮冷却'),('mechanics','边走边A，补上空档伤害'),('protect','挡在后排前面，等队友技能'),('explain','边后拉边解释刚才那套连招')]),
 ('结算复盘','回放里有伤害也有空技能，你最想重看哪一段？',[('mechanics','那次取消后摇，重看十遍'),('ult','R落点差半个身位那次'),('plan','哪一轮技能交早了'),('explain','先暂停，我这波是有思路的')]),
])
episode('hex','box','重掷还是硬玩',[
 ('强化选择','三张强化都没有理想联动，手里还剩一次重掷。你会？',[('reset','重掷，梦想留给下一屏'),('plan','选能稳定触发的，先保证不白板'),('gold','先看能不能早点做出核心装备'),('chaos','选最怪的，这把素材不能少')]),
 ('确认强化','选择已经确认，队友问这张怎么用。你怎么回答？',[('explain','我来讲触发条件，先别乱冲'),('plan','先打一波试强度，再调整站位'),('chaos','别问，问就是开发新套路'),('protect','先看谁缺保护，我来补那块')]),
 ('首次联动','团战开始，你选的强化第一次有机会触发。你先盯什么？',[('mechanics','触发节奏，别把操作打断了'),('ult','等大招窗口一起爆发'),('protect','队友能不能吃到团队收益'),('gold','这波打完能不能合成大件')]),
 ('下一轮选择','下一轮选牌又来了，你会优先补哪块？',[('plan','补当前打法的短板'),('stack','选能继续成长的，越后面越有用'),('reset','不搭就重掷，别硬拧'),('chaos','把怪套路接着往怪里叠')]),
])
episode('hex','gate','赢团以后拆不拆',[
 ('桥头推进','你们刚赢一波，对面还有两个人守塔。下一步怎么打？',[('plan','看兵线和复活时间，能拆就拆'),('engage','叫齐队友，先把守塔的逼退'),('gold','吃完这波兵再跟上'),('chaos','先冲塔下亮表情，气势要到位')]),
 ('塔下换血','守塔的人清掉前排小兵，你们剩下的兵不多。你会？',[('retreat','后拉，别把优势换成团灭'),('mechanics','卡塔攻击间隔，点几下就走'),('protect','挡关键技能，给队友安全撤离'),('int','不等下一波了，我先进去试塔伤')]),
 ('清线之后','一波拉扯结束，新兵线快到了。你最先看哪里？',[('plan','对方复活人数和我们血量'),('poke','守塔人的走位，先消耗再推进'),('heal','队友状态，先把人留在场上'),('collector','有没有能让我补最后一口的残血')]),
 ('推进复盘','同样是赢团，这次推进最该记住什么？',[('plan','团赢不等于塔已经没了'),('protect','活着的人先一起走'),('gold','别把兵线和装备节奏漏掉'),('explain','刚才那次越塔，我能讲出三种解释')]),
])
episode('hex','range','手长也要看身后',[
 ('长手阵容','你拿了远程消耗英雄，队友却是近战居多。你怎么站？',[('poke','站安全位置反复消耗'),('protect','跟紧前排，随时帮他解围'),('mechanics','卡最远射程，走A找角度'),('plan','先观察对面突进技能什么时候交')]),
 ('队友向前','队友想往前压，对面刺客还没露头。你会？',[('vision','先看侧面草丛，别追着一个人看'),('retreat','标记危险，往回收半步'),('protect','技能留一手，跟队友一起退'),('poke','边拉边打，不让对面白追')]),
 ('刺客进场','刺客绕后接近你，前排正在打另一边。你怎么处理？',[('mechanics','躲关键技能，争取反打'),('control','控制留给他，给队友回头时间'),('retreat','拉向队友，不往没人的地方跑'),('chaos','原地反打，看看谁先上集锦')]),
 ('射程结算','看输出统计时，你最想一起对照哪项？',[('poke','伤害转化，消耗有没有帮到团战'),('plan','站位回放，哪次退早或退晚'),('protect','队友活下来后多打了多少'),('explain','先说明，我站远是有理由的')]),
])
episode('hex','giant','四个输出一个前排',[
 ('前排选择','你是队里唯一前排，四个队友都在展示输出装。你先做什么？',[('protect','出抗性装，先让他们有地方站'),('stack','有安全换血就叠心之钢'),('engage','等队友到齐，我来找先手'),('chaos','我也出伤害，五个人都别太安全')]),
 ('桥口站位','五个人挤在桥口，对面法师正在找范围技能。你会？',[('protect','往侧面顶，给后排腾位置'),('control','留控制拦冲脸的'),('plan','标记散开，别五个人吃同一个技能'),('engage','等对面技能交掉再往前压')]),
 ('血量拉扯','你血量不多，队友还在输出，敌方后排也残了。你会？',[('protect','边退边挡，别把队友暴露出去'),('retreat','标记后撤，活着等下一波'),('engage','确认队友能跟，再逼一下后排'),('stack','找安全普攻叠一层，不能白挨打')]),
 ('前排结算','这把最让你有成就感的是？',[('protect','队友能站着把伤害打完'),('stack','心之钢叮了一整局'),('plan','该开的时候开，该退的时候退'),('explain','承伤第一，先听我说两句')]),
])
episode('hex','missile','技能能中就别急',[
 ('消耗回合','你玩远程技能英雄，对面一直躲在兵线后。你会？',[('poke','等补刀停顿，慢慢找命中'),('mechanics','换侧面角度，练预判'),('control','等队友控到再接技能'),('chaos','技能转好就扔，总有一个接得到')]),
 ('技能落空','连续两发空了，队友开始点你的头像。你怎么接？',[('explain','说明我在逼走位，下一发再看'),('calm','先停一下，等对面补刀动作'),('blame','是兵挡住了，不是我没瞄准'),('chaos','再扔，空三发就没人记得前两发')]),
 ('残血诱惑','对方残血在桥尾亮表情，前排挡着。下一步？',[('poke','不穿人墙，等侧面窗口'),('mechanics','找角度打到他再后撤'),('protect','先帮队友处理眼前的人'),('flash','闪现过墙追，表情不能白亮')]),
 ('消耗复盘','回看这局技能命中率，你最想改什么？',[('mechanics','把施法时机卡准一点'),('poke','优先消耗真正能威胁我们的人'),('plan','推线和打人的顺序再排一遍'),('explain','命中率一般，压迫感是满的')]),
])
episode('hex','heal','奶谁都是一门学问',[
 ('辅助开局','你拿到治疗型辅助，四个队友都说自己能C。你怎么准备？',[('heal','治疗和团队装安排上'),('protect','看谁最容易被切，先保他'),('plan','先看伤害结构，别只听谁嗓门大'),('chaos','我也走输出，让他们自己照顾自己')]),
 ('同时掉血','四个人同时喊“奶我”，治疗技能只有一份。你先？',[('heal','救能救下、马上还要吃伤害的人'),('protect','保正在被集火的核心'),('plan','看血量和位置，不按语音音量排序'),('blame','刚才说能C的，先解释为什么又残了')]),
 ('核心走远','核心追残血跑远，后面还有三个人。你会？',[('protect','标记回来，我跟到安全边界'),('heal','先照顾身边受伤的队友'),('engage','确认剩下的人能跟，再向前接应'),('retreat','不跨整座桥送第二个人')]),
 ('治疗结算','治疗量和输出量摆在一起，你最想说什么？',[('heal','看着大家活着，我就挺满意'),('protect','保护不是按完一个键就下班'),('explain','谁说只有输出才算C'),('reset','下局换你奶我，体验一下')]),
])
episode('hex','clown','小丑的进场时机',[
 ('小丑上线','你玩小丑，队友都还在清线，对面后排落单了。你怎么进？',[('plan','先等队友靠近，不把落单演成自投罗网'),('mechanics','计算隐身时间，绕到能脱身的位置'),('chaos','先放表情，节目效果已经到位'),('int','看见人就去，队友可以看回放')]),
 ('隐身绕后','你绕到侧后方，队友还差半座桥。下一步？',[('control','先布盒子，给对面走位压力'),('retreat','先藏住，别急着露脸'),('chaos','提前露脸吓一下，能不能回来再说'),('engage','发进攻信号，等队友进入射程')]),
 ('盒子生效','盒子把对方前排吓退了，后排没跟上。你会？',[('control','把控制链交给靠近队友的人'),('mechanics','打能打到的，别硬追最远的'),('protect','回头帮队友处理突进'),('chaos','追着残血亮表情，这镜头不能丢')]),
 ('小丑回放','回放标题你会选哪个？',[('plan','不是每次隐身都要立刻现身'),('mechanics','操作有了，退路也得有'),('explain','这波有点丑，但我先解释'),('chaos','小丑竟是我，素材先发群里')]),
])
episode('hex','stack','叠层不等于闭关',[
 ('成长英雄','你拿到狗头，Q层数刚起步，队友已经想打架。你怎么安排？',[('stack','先叠安全的兵，不拿命换层数'),('gold','补到关键装备的钱再说'),('protect','跟在后面，至少帮队友挡一下'),('engage','先打起来，Q人也不能没梦想')]),
 ('兵还是团','近处有残血炮车，队友在桥口拉扯。你会？',[('stack','Q掉眼前这只就跟，别再贪下一波'),('protect','先支援，层数不会替队友复活'),('plan','看队友能不能后撤，再决定吃不吃'),('gold','这炮车响了一声，别的先静音')]),
 ('强势期到','装备和层数终于够用，对面却开始后退。你选择？',[('engage','等减速或控制命中，再一起追'),('control','用W逼位，让队友跟上'),('protect','站在中间，让队友安全推进'),('stack','能逼退就继续吃线，别忘记正事')]),
 ('层数结算','基地结算时，你怎么看这把成长？',[('stack','层数很多，但还要看什么时候参团'),('plan','强势期没浪费，比数字更重要'),('gold','这一局发育路线我很满意'),('explain','再给五分钟，故事绝对不一样')]),
])
episode('hex','ult','大招捏到什么时候',[
 ('大招窗口','你玩大招开团英雄，R已经转好，对面五个没站一起。你会？',[('ult','先等能抓住核心的位置'),('engage','找到一个落单的也能开'),('plan','先看队友距离，别开完没人跟'),('chaos','能R到谁算谁，先把键按下去')]),
 ('第一发空了','第一发R没打出效果，技能还在冷却。你怎么接？',[('mechanics','用小技能处理眼前团战'),('retreat','标记大招冷却，先往后拉'),('protect','挡一下突进，别让队友一起倒'),('explain','刚才不是空，是对面临时换了路线')]),
 ('重新等机会','R快好了，对面站得很密，队友还差两个人复活。你会？',[('plan','先清线，等人齐'),('ult','盯着对面核心，但先不按'),('control','用小控制拖住推进节奏'),('int','机会千载难逢，我一个人先上')]),
 ('十秒回放','这局你最想保存的十秒是？',[('ult','终于把R交给正确那个人'),('mechanics','没大招那波也打出了东西'),('protect','替队友争出的一次撤退'),('explain','暂停十秒，我把那次空大解释完')]),
])
episode('hex','table','团灭以后先干什么',[
 ('团灭灰屏','刚被打了一波零换五，复活倒计时还在走。你先？',[('explain','看控制链断在哪儿，不急着下一波'),('blame','先点装备，证明锅不在我'),('calm','先稳住，下波别一起吃大招'),('chaos','回放配个BGM，群里先笑一轮')]),
 ('复活之前','队友说“再来一次就能赢”，但双方装备差了一件。你会？',[('plan','等关键装和技能，不照抄刚才那波'),('protect','我站前面，你们这次别挤一起'),('blame','你先说清楚，刚才为什么不跟'),('explain','把对面交掉的召唤师技能报一遍')]),
 ('重新接团','对面带兵压到塔前，这次你最先看什么？',[('control','谁先交突进，控制留给他'),('mechanics','技能范围和自己退路'),('engage','队友是否在能跟上的位置'),('afk','先在后面等，看看这次谁先倒')]),
 ('结束以后','不管输赢，这局你留给队友哪一句？',[('plan','下次先数人，再数装备'),('explain','来，看这段回放，我只讲一分钟'),('blame','我的操作没问题，其他建议另议'),('reset','下一把，别带着上一把的情绪')]),
])
episode('hex','office','泉水观战有学问',[
 ('阵亡等待','你刚阵亡，队友还在桥中间拉扯，复活还差十秒。你会？',[('afk','切别人镜头，看完再决定想不想动'),('explain','报对面关键技能和复活时间'),('protect','提醒队友退到能接应的位置'),('blame','先打字：刚才怎么没人跟')]),
 ('队友交火','观战时你发现刺客从侧面露头。你怎么提醒？',[('vision','标记刺客位置，不刷屏'),('protect','提醒后排留控制，等我复活'),('blame','被切的人先看自己站位'),('afk','镜头切好了，这段我看得最清楚')]),
 ('复活出门','你复活时队友正往回退，对面还有四个。你会？',[('plan','在塔下接队友，不一个人往前跑'),('protect','挡追击技能，让残血先回来'),('int','直接雪球二段，十秒没操作手痒了'),('afk','先在泉水多看两秒，别催')]),
 ('观战总结','这次灰屏里，你觉得什么最有用？',[('explain','把确实看到的信息说清楚'),('plan','想好复活之后往哪走'),('afk','第一视角轮流看，我已经导播毕业'),('blame','至少我知道该怪谁了')]),
])
episode('hex','review','这波到底亏没亏',[
 ('刚刚阵亡','你阵亡前逼出两个闪现，队友保住了塔。复活还有十秒，你先？',[('explain','报两个闪现时间，强调这波有交换'),('plan','看兵线和下一波技能怎么接'),('blame','先说我已经逼闪了，其他不归我'),('calm','别急着争，先把这波线清完')]),
 ('队友追问','队友问“你拿人头换到了什么”，你怎么回？',[('explain','两个闪现和守塔时间，下波要利用起来'),('plan','收益得看后续，先别宣布赚麻了'),('blame','反正不是我一个人的问题'),('chaos','截图两个闪现空位，当场制作不亏证据')]),
 ('同一路口','复活后，同一个路口又出现残血，旁边敌人没露头。你会？',[('vision','先用技能探草，别重复交学费'),('plan','等队友到，再考虑追不追'),('mechanics','只打安全范围，不越过视野'),('int','上次已经逼闪，这次必须追到底')]),
 ('回放命名','这段回放你会叫什么？',[('explain','这波不亏，但下一波别白给'),('plan','交换资源也得算后续'),('blame','我尽力了，详见聊天记录'),('chaos','人没了，嘴还在输出')]),
])
episode('hex','collector-audit','五把枪缺个前排',[
 ('再次选装备','队伍四个收集者，你的钱也够合成一把，队里没有前排。你选？',[('collector','第五把立刻安排，图标先排整齐'),('protect','换抗性装，总得有人站前面'),('plan','先看我这英雄适不适合，不凑数'),('gold','先算下一件装备的强势时间')]),
 ('五人抢残血','对面前排残血，后排状态还很好。你先打谁？',[('collector','先收眼前这个，击杀音效不能让'),('mechanics','打得到谁打谁，不穿过前排送'),('protect','挡住侧面的刺客，别盯着最后一口'),('control','留控制，防后排趁机追上来')]),
 ('回家防守','对面开始推你们的基地，远处还有一波残血小兵。你会？',[('gold','先把能安全吃的钱收了再回防'),('protect','先回塔前，护住清线队友'),('plan','看回防人数和兵线，别两头都丢'),('collector','只要对面越塔，就轮到我收了')]),
 ('装备结算','装备栏一排收集者，塔伤害却很一般。下局怎么说？',[('collector','枪可以留，拆塔这次也要记得'),('gold','补刀节奏不错，转资源还得练'),('plan','出装按阵容，不按队友复制粘贴'),('protect','总得有人给五把枪挡一下技能')]),
])
episode('rift','spring','小虎的节奏回合',[
 ('中路起手','你玩中单，刚推完一波线，打野想争河道视野。你会？',[('plan','先看边线和对面中路位置'),('control','跟打野一起占口，留控制'),('gold','先补齐关键装备的钱'),('mechanics','卡技能距离，把对面压在塔下')]),
 ('游走窗口','边路有机会，对面中单正在回城。你怎么选？',[('plan','算来回时间，别漏掉整波线'),('engage','跟打野一起走，别分头送'),('control','先从河道逼位置，等对手交技能'),('gold','对面没T，先吃一层镀层也行')]),
 ('关键团战','团战开始，前排已经接触，双方后排都在等。你会？',[('control','把控制留给威胁最大的那个'),('mechanics','找侧面角度，不吃第一轮控制'),('protect','先帮自己核心挡掉突进'),('ult','等对手核心站进R范围')]),
 ('赛后镜头','导播把镜头切到你，队友正笑着聊刚才那团。你会？',[('laugh','先抿嘴，再没忍住笑出第二段'),('calm','笑可以，下一场还得认真打'),('explain','先给那波决策讲个来龙去脉'),('plan','记住这次好窗口，下局继续用')]),
])

# Eight new episodes: all follow one game situation across four stages.
episode('rift','double-laugh','二段笑加载中',[
 ('开局之前','队友看见对面阵容，已经开始笑“这把稳了”。你怎么接？',[('laugh','先憋住，等他一笑我再笑第二段'),('calm','先别开香槟，进游戏再说'),('plan','看看控制和伤害，不按名字判断'),('chaos','表情先亮出来，气势提前进场')]),
 ('领先一点','你们拿到一个人头，对面闪现还在，队友开始连发笑脸。你会？',[('laugh','第一段笑完，补刀间隙再来第二段'),('calm','先回城出装，别把优势笑没了'),('gold','先把这波线吃干净再庆祝'),('protect','提醒位置，别让队友被反抓')]),
 ('对面反扑','对面开始抱团，你的队友仍在说“稳”。你会？',[('calm','收笑容，先看人数和技能'),('control','把控制留给冲进来的人'),('laugh','笑归笑，手先把技能按明白'),('blame','万一没赢，刚才可不是我先笑的')]),
 ('结算之后','结算页终于打开，群里有人要一张表情包。你发？',[('laugh','截两张笑脸，标上第一段和第二段'),('calm','先发结果，赢了再补笑脸'),('explain','顺便讲讲哪次差点笑出事'),('reset','表情发完，下一局重新认真')]),
])
episode('rift','tes-top','滔博陀螺抗压局',[
 ('连续被压','对手连开两波，你们被压在塔前，弹幕刷“陀螺又转起来了”。你会？',[('spin','左右拉扯找空隙，拒绝一直挨打'),('calm','先守线等技能，别急着接第三波'),('protect','站到后排前面，接住第一轮伤害'),('blame','先问刚才是谁让我们接的')]),
 ('传送抉择','边路交火，你的传送能落到后方眼位，但队友血量很低。你会？',[('plan','先看能否撤退，不盲目传送一换五'),('spin','落地先横向拉扯，不站着吃下一套'),('protect','能接应就传，优先帮残血撤走'),('chaos','传都亮了，先让导播别切镜头')]),
 ('对面断档','对面开团技能刚交空一个，你们终于有一点空间。你选？',[('spin','从挨打里转出来，侧移找反打角度'),('control','控制接住最靠前的人'),('calm','先把兵线推回去，不赌一波全有'),('engage','确认队友跟上，一起打回去')]),
 ('赛后梗图','队友发来“滔博陀螺”梗图，你配什么文字？',[('spin','今天先练抗压，下次争取主动转'),('calm','笑完记得复盘，别只记队标'),('explain','这波被压的原因，我能讲清楚'),('reset','这局先存素材，下局换个剧本')]),
])
episode('rift','flash-wall','闪现交个热闹',[
 ('墙边追击','你追到峡谷河道的薄墙边，对面残血刚过去，闪现还在。你会？',[('flash','闪过去再说，手速得比脑子快'),('plan','先确认墙宽、视野和队友位置'),('poke','隔墙能打到就打，没必要硬过'),('protect','不追了，回去保正在吃伤害的队友')]),
 ('闪现以后','有人闪现撞墙，语音突然安静。轮到你接一句？',[('flash','这是贴墙侦察，不是失误'),('calm','没事，技能没了先退'),('explain','先看墙体边缘，这段正好做教学'),('chaos','截图，今晚群头像有了')]),
 ('没有闪现','下一波团你的闪现还在冷却，对面控制却转好了。你怎么站？',[('mechanics','靠走位，不给对面直线出手'),('retreat','站后半步，把退路留出来'),('protect','跟紧能保护我的队友'),('chaos','没闪也能秀，镜头接着录')]),
 ('回放十秒','队友说把撞墙那段删掉，你会？',[('flash','不删，闪现没过墙但能过年'),('explain','留着画一下正确闪现落点'),('calm','私下笑完就好，下一局别提了'),('reset','下局练回来，先重开')]),
])
episode('hex','golden-time','金身两秒半',[
 ('装备抉择','你玩法师，对面刺客盯了你好几次，钱够做金身。你会？',[('stasis','中娅安排上，给队友两秒半回头'),('plan','看伤害和威胁，确认这波确实该补'),('gold','先憋帽子，伤害也是一种保护'),('chaos','金身可以没有，气势不能掉')]),
 ('刺客扑脸','刺客技能快落到你身上，队友就在附近。你怎么按？',[('stasis','卡伤害落点开金身，并标记位置'),('mechanics','能躲先躲，把金身留到躲不了'),('control','先控住他，给队友跟输出'),('flash','闪现向前，试试看能不能反杀')]),
 ('金身结束','金身快结束，队友正与对面交火，脚下还有危险技能。你准备？',[('stasis','看好结束时间，技能和移动接起来'),('mechanics','选能走的角度，别原地读条'),('protect','优先处理贴着队友的刺客'),('explain','一边等一边报：别走，我马上回来')]),
 ('装备结算','这把金身救过你，也有一次没按出来。你怎么评价？',[('stasis','装备买了还得会按，下次练时机'),('plan','看能不能把存活换成赢团'),('explain','没按那次先暂停，我有解释'),('chaos','金色雕像一出，节目效果就值了')]),
])
episode('hex','six-swords','六把无尽的梦想',[
 ('出装争论','队友说“六把无尽，六倍快乐”，让你照着出。你回复？',[('collector','装备栏排得整齐，梦想先拉满'),('plan','先看唯一效果和缺什么，不盲目复制'),('gold','把核心装做完，再想第六格'),('chaos','复制的是装备，笑到的是队友')]),
 ('中期购物','现在你有一个空格，对面前排护甲很高。你会？',[('plan','补适合的穿甲或生存，别只看暴击数字'),('mechanics','看自己能打到谁，再决定输出装'),('collector','想再来一把收集者，图标必须对称'),('protect','队伍没人能扛，先补点生存')]),
 ('被切以后','装备栏很好看，但你刚进场就被切掉了。下一波先改什么？',[('plan','站位和防突进，活着才有输出'),('mechanics','走位躲第一轮，等队友控制'),('collector','我知道缺什么：还差一个最后一口'),('blame','装备没错，错在没人保我')]),
 ('出装复盘','最后你给这套复制出装写一句？',[('plan','重复图标是梗，真实出装看局势'),('gold','钱花得对，才叫装备领先'),('collector','再拍一张，五把枪确实很整齐'),('chaos','数据可能一般，节目效果满装')]),
])
episode('hex','brush','草丛里是不是五个',[
 ('草丛安静','对面五个人都没露头，前方草丛安静得很整齐。你先？',[('vision','用远程技能探一下，不拿脸当扫描'),('plan','先等兵线，别分头往里走'),('protect','站到队友侧前，留控制防突进'),('int','我走过去看看，答案就在草里')]),
 ('技能被挡','探草技能碰到了东西，但不知道有几个人。下一步？',[('vision','标记有人，继续从安全位置确认'),('control','留控制封出口，不直接走进去'),('poke','先消耗露头的，别追进草'),('chaos','亮个表情，看看他们肯不肯出来')]),
 ('敌人冲出','对方前排突然从草里开出来。你会？',[('protect','帮被开的队友挡后续技能'),('control','控住第二个进场的人'),('mechanics','先躲开团，沿有退路的方向拉'),('engage','看队友状态，能反打就一起接')]),
 ('视野回放','这次探草你最认同哪句？',[('vision','草里没人，不代表可以闭眼走'),('plan','信息不全的时候，先留退路'),('explain','刚才那个技能已经告诉我们很多了'),('chaos','草丛要是真能说话，第一句肯定是别来')]),
])
episode('hex','snowball-return','雪球二段先数人',[
 ('雪球命中','雪球中了对面后排，但他身后还有四个人。你按二段吗？',[('plan','先数队友距离，再决定去不去'),('engage','队友在射程内就一起压上去'),('int','命中就是邀请函，我先过去'),('poke','先用技能消耗，不急着进')]),
 ('二段倒计时','雪球标记快结束，队友还在清线，语音有人喊上。你会？',[('plan','不去，这次命中不等于必须飞'),('protect','等队友到齐，先看后排安全'),('engage','发信号，只有跟得上的才开'),('chaos','最后一秒起飞，观众要有悬念')]),
 ('对面反开','对面反而借着空档冲过来了，你的雪球已经没了。你先？',[('control','留控制接冲脸的，不再找后排'),('protect','帮队友拉开位置'),('mechanics','用小技能边拉边打'),('blame','刚才谁喊上的，先把名字留下')]),
 ('司机结算','下次雪球命中后，你希望队友先说什么？',[('plan','人齐了，技能齐了，再上'),('engage','我能跟，等我这一秒'),('protect','后排安全，我来接你'),('chaos','录像开了，司机自由发挥')]),
])
episode('rift','dragon-cheer','抢龙以后别停手',[
 ('争龙之前','龙快进入斩杀线，队友已经在预演抢到后的庆祝。你先？',[('calm','先关庆祝界面，盯好龙血量'),('vision','盯住对面打野位置和进场路线'),('plan','分清谁打龙、谁拦人、谁留控制'),('laugh','先憋一段，抢到了再解锁第二段')]),
 ('龙被拿下','龙的归属确定了，坑里还站着对面三个人。你先做什么？',[('calm','继续操作，结算前不松手'),('protect','先帮拿龙的队友撤出去'),('engage','确认状态能打，再追一个'),('laugh','笑一声就收，键盘还得接着按')]),
 ('撤退路上','后方有人追，前方还有敌方控制，队友想回头。你会？',[('plan','看技能和人数，别把龙换成团灭'),('control','控住追得最近的，留撤退通道'),('protect','让残血先走，我挡一下'),('chaos','回头亮个表情，这趟不能白来')]),
 ('真正庆祝','大家终于安全回城，队友问现在能笑了吗？',[('laugh','可以了，二段笑完整版启动'),('calm','笑完出装，下一条龙还得打'),('explain','先记一下刚才谁拦住了对面打野'),('reset','这段存好，下次争取再来一遍')]),
])

# Remove residual office / staged award language in retained Rift questions.
for q in d['questions']:
    if q['id']=='rift-support-3':
        q['title']='赛后想给辅助一个高光镜头，你最想放哪段？'
        q['options']=[dict(id=i,text=t,behavior=b,signals=dict(zip(dims,signals[b])),tags=[b]) for i,(b,t) in enumerate([
            ('protect','回头保下被切的核心'),('vision','提前点亮龙区，队伍少吃一次埋伏'),('engage','确认人齐以后那次果断开团'),('heal','极限治疗把队友抬回来')])]
    for o in q.get('options',[]):
        if q['theme']=='lol':
            o['text']=o['text'].replace('股东','队友').replace('董事会','队伍').replace('开票','记下')

cards = {a['id']:a for a in d['augments']['lol']}
# Retire the literal table. Keep a stable ID for older authoring tooling, but no table art/text.
a = cards['table-flip']
a.update(name='团灭别急着开', effect='每次零换五后，获得一次冷静读秒。\n队友的“能赢”自动延迟到人齐再播。',punchline='团可以重打，五个人别分五次到。',line='团可以重打，五个人别分五次到。',kind='plan',vector=[20,35,35,80,55,95],behaviorWeights={'plan':5,'calm':4,'control':2},affinities=['xiaohu','clearlove'])
a['bias']=[round((v-50)/50,2) for v in a['vector']]
cards['not-a-loss'].update(effect='阵亡后自动报出逼掉的闪现。\n若下一波没利用，系统追加一句“那还是亏了”。',punchline='嘴可以说不亏，下一波得把资源拿回来。',line='嘴可以说不亏，下一波得把资源拿回来。')
cards['fountain-owner'].update(name='泉水观战席',effect='阵亡时自动切入四位队友视角。\n复活以后，观战权限还想续杯。',punchline='地图看得最全，走出去最晚。',line='地图看得最全，走出去最晚。')
cards['collector-union'].update(effect='获得五把收集者的视觉排面。\n最后一口只有一个，抢的人有五个。',punchline='装备可以复制，击杀不能平均分。',line='装备可以复制，击杀不能平均分。')
cards['blame-master']['effect']='阵亡后解锁全队装备检查。\n每找出一处问题，自己的回放延后十秒。'
cards['basic-duty'].update(effect='关闭“一键甩锅”，开启走A训练。\n每空一个技能，追加一句“先练基本功”。')

visuals = {
 'table-flip':('row',['SummonerHeal','item-3190','item-3075'],'人齐再开'),
 'collector-union':('fan',['item-6676']*5,'收集者 ×5'),
 'basic-duty':('fan',['item-1036']*4,'长剑 ×4'),
 'square-lecture':('square',['item-3364']*4,'四条边都扫过'),
 'fountain-owner':('fan',['item-3363']*3,'远见改造 ×3'),
 'feeding-license':('fan',['SummonerSnowball']*3,'雪球 ×3'),
 'all-aboard':('row',['SummonerSnowball','SummonerFlash','SummonerTeleport'],'三个都能赶路'),
 'where-team':('ring',['item-3363']*4,'四个队友在哪'),
 'spring-heater':('fan',['item-3087']*3,'电刀 ×3'),
 'four-stay-alive':('row',['item-3190','SummonerHeal','item-3075'],'前排售后套餐'),
 'economy-brain':('fan',['item-1083']*4,'萃取 ×4'),
 'borrowed-growth':('fan',['item-6676','item-3031','item-3089'],'梦想先装满'),
 'blame-master':('ring',['item-3364']*3,'复活后开始扫描'),
 'not-a-loss':('row',['SummonerFlash','SummonerFlash','item-1036'],'逼了两个闪现'),
 'life-reroll':('ring',['item-3364','item-3363','item-2055'],'再看一次命运'),
 'clown-self':('fan',['SummonerFlash','SummonerSnowball','SummonerDot'],'主角进场三件套'),
 'fountain-range':('fan',['item-3363']*5,'看得见不等于打得到'),
 'ultimate-installment':('fan',['SummonerDot']*2,'今天先按一次'),
 'cosmic-pension':('fan',['item-3084']*3,'心之钢 ×3'),
 'bridge-clinic':('fan',['SummonerHeal']*4,'治疗术 ×4'),
 'last-last-game':('ring',['item-3006']*4,'再跑最后一趟'),
 'revive-cinema':('row',['item-3363','item-3364','item-3363'],'灰屏导播三机位'),
 'champion-script':('fan',['item-3031']*3,'无尽之刃 ×3'),
 'snowball-hearse':('fan',['SummonerSnowball']*5,'雪球 ×5'),
 'good-enough':('row',['item-3083','item-3111'],'活着也是输出'),
}

def add_card(id,name,category,effect,joke,vector,weights,affinities,kind,visual,requires):
    a=dict(id=id,name=name,category=category,rarity='kPrismatic',effect=effect,punchline=joke,line=joke,vector=vector,behaviorWeights=weights,affinities=affinities,kind=kind,icon=0,fanMade=True,requires=requires)
    a['bias']=[round((v-50)/50,2) for v in vector]
    cards[id]=a
    visuals[id]=visual

add_card('double-laugh','二段笑启动器','名场面','第一次笑获得信心。\n第二次笑之前，强制确认基地还在。','先别把胜利笑出来，把团先打完。',[55,35,60,40,40,20],{'laugh':5,'chaos':1},['xiaohu'],'chaos',('fan',['item-3089']*2,'帽子 ×2，笑两段'),['laugh'])
add_card('tes-top','滔博陀螺','名场面','受到连续开团时，启动抗压旋转。\n转出一次安全站位，才算真正停稳。','这次别只顾着转，找个机会打回去。',[65,35,70,45,65,35],{'spin':5,'engage':1},['jackeylove','knight'],'engage',('ring',['item-3087']*4,'电刀 ×4，环形梗改'),['spin'])
add_card('flash-wall','闪现贴墙检测','操作','闪现撞墙时，获得一次近距离地形考察。\n队友截图速度提高到全队第一。','闪现没过墙，笑话能过年。',[75,45,95,30,60,12],{'flash':5,'chaos':1},['pdd','ning'],'chaos',('fan',['SummonerFlash']*3,'闪现 ×3'),['flash'])
add_card('double-zhonya','两段金身','操作','获得两尊金色雕像的排面。\n队友围观两秒半，你围观队友两秒半。','买的是金身，按的是人情世故。',[25,35,35,55,85,80],{'stasis':5,'mechanics':1},['faker','knight'],'basic',('fan',['item-3157']*2,'中娅沙漏 ×2'),['stasis'])
add_card('six-infinity','六把无尽','装备','装备栏复制六把无尽之刃。\n重复效果不叠，群友的问号可以叠。','这是梗图出装，别真照着买。',[60,90,65,25,60,25],{'collector':4,'chaos':2,'gold':1},['uzi','jackeylove'],'economy',('grid',['item-3031']*6,'无尽之刃 ×6'),['collector'])
add_card('triple-deathcap','帽上加帽','装备','三顶帽子同时上岗。\n法强没有三倍，头围先领先版本。','帽子够高，站位也得够稳。',[50,90,45,30,65,45],{'gold':4,'collector':2},['knight','faker'],'economy',('fan',['item-3089']*3,'灭世者的死亡之帽 ×3'),['gold'])
add_card('calm-before-win','先别开香槟','心态','基地没爆炸前，自动屏蔽“稳了”。\n结算后才解锁完整版笑容。','提前庆祝的手，先放回键盘上。',[8,45,25,75,65,95],{'calm':5,'plan':2},['xiaohu','faker'],'plan',('row',['SummonerBarrier','item-3190','SummonerHeal'],'先把这一波守完'),['calm'])
add_card('brush-five','草里真有五个','视野','探草时额外获得一次“先别走过去”。\n拿脸探草的，自动成为一枚临时眼位。','眼可以排，人别先没了。',[10,15,25,92,55,95],{'vision':5,'control':1},['ming','meiko'],'protect',('fan',['item-2055']*5,'控制守卫 ×5'),['vision'])
add_card('steel-orchestra','心之钢交响乐','成长','每叮一声，全队语音安静零点五秒。\n层数继续涨，耳机音量先投降。','团可以慢一点，叮不能少一下。',[20,85,30,45,50,95],{'stack':5,'protect':1},['letme','theshy'],'protect',('fan',['item-3084']*5,'心之钢 ×5'),['stack'])
add_card('mercury-notice','水银使用须知','拉扯','解除的控制写在装备说明里。\n没按出来的理由写在聊天记录里。','装备先看说明，失误别怪键盘。',[25,35,25,55,90,85],{'mechanics':4,'plan':2},['uzi','faker'],'basic',('fan',['item-3140']*3,'水银饰带 ×3'),['mechanics'])
add_card('five-knives','电刀连锁反应','消耗','第一刀弹向兵线。\n第二刀弹向对手，第三刀弹向队友血压。','弹得很热闹，先看打到了谁。',[25,55,25,45,90,70],{'poke':5,'mechanics':1},['uzi','knight'],'retreat',('fan',['item-3087']*5,'斯塔缇克电刃 ×5'),['poke'])

for a in cards.values():
    layout,icons,label=visuals[a['id']]
    a['visual']=dict(layout=layout,icons=icons,label=label)
    a['creation']='本作自制恶搞效果；配图使用 Riot Data Dragon 16.21.1 真实装备或召唤师技能图标重新排布。重复图标为梗图，不代表可购买数量、效果叠加或出装建议。'
d['augments']['lol']=list(cards.values())
d['memeReferences']=[
 dict(id='double-laugh',title='小虎·二段笑',personId='xiaohu',chapter='double-laugh',series='rift',card='double-laugh',description='参考小虎休息室笑容逐步放大的经典表情梗；这里改编成“笑可以，先打完”的对局情境。',sourcePage='https://www.ji-cloud.cn/news.info.php?id=5764',sourceTitle='极云：二段哭二段笑什么梗（2022-11-01）'),
 dict(id='tes-top',title='滔博·陀螺抗压',personId='jackeylove',chapter='tes-top',series='rift',card='tes-top',description='参考 TES 队标像陀螺、被动挨打的网友二创；这里改编成逆风拉扯。电刀环形图为本作梗改，非原队标。',sourcePage='https://www.ali213.net/news/html/2025-4/921573.html',sourceTitle='游侠网：滔博陀螺是什么梗（2025-04-07）'),
 dict(id='square-lecture',title='大司马·正方形打野',personId='dasima',chapter='review',series='hex',card='square-lecture',description='把“这波不亏”和路线讲解改编成对局复盘题，围绕技能交换、地图信息与下一波决策。',sourcePage='https://zh.moegirl.org.cn/韩金龙',sourceTitle='人物参考：萌娘百科·韩金龙'),
]
for q in d['questions']:
    if q['theme']=='lol':
        q['chapterName']=q['chapterName'].replace('龙坑股东大会','龙坑争夺战')
        q['scene']=q['scene'].replace('会议纪要','龙坑复盘')
for p in d['characters']:
    if p['theme']=='lol' and p['personId']=='xiaohu':p['behaviorWeights'].update(laugh=5,calm=3)
    if p['theme']=='lol' and p['personId']=='jackeylove':p['behaviorWeights'].update(spin=5)
    if p['theme']=='lol' and p['personId']=='knight':p['behaviorWeights'].update(spin=2,stasis=3)
for s in d['lolSeries']:
    s['count']=sum(q['theme']=='lol' and q['series']==s['id'] for q in d['questions'])
d['counts'].update(questions=len(d['questions']),lolQuestions=sum(q['theme']=='lol' for q in d['questions']),lolChapters=len({(q.get('series'),q.get('chapter')) for q in d['questions'] if q['theme']=='lol'}),parodyCards=len(cards))
d['augmentData'].update(edition='真实装备梗改 · 本作自制', note='装备和召唤师技能图标来自 Riot Data Dragon 16.21.1；卡名、夸张效果、重复排布和剧情为本作恶搞创作，不是官方强化。名场面提供参考出处，题目为改编情境。')
path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print(d['counts'])
