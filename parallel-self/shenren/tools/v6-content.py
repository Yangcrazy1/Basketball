"""Author the coherent V6 question bank and pinned, sourced ARAM reference cards."""
from pathlib import Path
import json, urllib.request, hashlib, re, html
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[1];R=Path('/workspace/scratch/v6-research');D=json.loads((ROOT/'src/data.json').read_text())
D['version']=6
D['lolDimensions']=[{'id':k,'name':n} for k,n in zip(['tilt','greed','risk','team','craft','plan'],['上头浓度','经济执念','开团胆量','队友牵引','操作信仰','运营耐心'])]
D['themes'][0]['dims']=[x['name'] for x in D['lolDimensions']]
D['themes'][0]['description']='上 / 野 / 中 / 下 / 辅 · 真实海克斯匹配'
# Every response has an authored multi-axis signal. AFK and inting are intentionally distinct.
S={
'afk':([82,28,8,8,20,15],['retreat','reset']),
'int':([96,22,98,8,45,8],['chaos','engage']),
'collector':([65,96,68,30,65,30],['collector','gold']),
'protect':([25,25,50,98,55,75],['protect','team']),
'plan':([15,52,30,72,58,96],['plan','control']),
'mechanics':([45,60,65,45,98,52],['mechanics','basic']),
'engage':([62,40,96,78,65,38],['engage','team']),
'chaos':([80,48,88,40,55,15],['chaos','reroll']),
'poke':([20,55,25,55,85,70],['range','spell']),
'stack':([20,88,30,45,60,95],['stack','gold']),
'heal':([12,20,30,98,70,80],['heal','protect']),
'reset':([50,45,45,58,60,62],['reset','reroll']),
'ult':([52,62,78,65,85,45],['ultimate','spell']),
'gold':([35,98,42,40,55,70],['gold','collector']),
'control':([25,35,58,80,75,88],['control','team']),
'retreat':([18,40,10,55,50,82],['retreat','plan'])}
# Format: chapter, title, then four sequential scenes with four semantically tagged choices.
CH=[
('hex','collector','四把收集者',[
('装备商店','队友四个人都出了收集者。第五个人的你怎么办？',['挂机，键盘进入节能模式@afk','开送，第五个收集者负责送礼@int','我也补一把，凑齐收集者家族@collector','补个前排：你们四个先别倒@protect']),
('桥上分歧','镜头切回桥上：对面五个大汉排成一堵墙。下一幕你想看什么？',['先刮三分钟，看看墙掉不掉漆@poke','雪球开车，试试墙结不结实@engage','先把残血小兵全部承包@gold','等对面越塔，再把墙关进塔里@control']),
('最后一口','对面只剩一丝血，四位收集者同时亮起。你的反应是？',['平A练到极致，最后一口自己争取@mechanics','往前顶，给四位股东留输出空间@protect','先退一步：五个人不能都上头@retreat','闪现进场，今晚总得有人上集锦@chaos']),
('赛后结算','结算页弹出“五位收集者，一座没拆的塔”。你给下局留什么？',['下局先看阵容，再讨论梦想@plan','把金币截图，塔可以下局再拆@gold','再来一局，收集者家族不能散@collector','我买救赎，你们四个负责活着@heal'])]),
('hex','basic','没有R的未来',[
('天赋抉择','“回归基本功”亮了：基础技能更强，但大招被封印。你怎么选？',['选，R键今天带薪休假@mechanics','我的英雄离开R就像火锅没锅，拒绝@ult','先看队伍缺输出还是控制@plan','重掷，命运不能限制我的键盘@reset']),
('队友提问','队友问“你大招呢”，镜头给到你的键盘。你怎么回答？',['把QWE按成一段爵士乐@mechanics','先标记冷却，再打字解释规则@plan','让队友先开，我负责接第二拍@protect','假装R键还在，靠气势把人吓退@chaos']),
('决胜团战','团战即将开始，对面都在等一个大招镜头。你想怎么打？',['普攻穿插技能，用细节打满@mechanics','等对手交完控制再进@plan','雪球先上，把场面打开@engage','站远一点，用技能慢慢拆血条@poke']),
('节目标题','导演给这场比赛起标题，你投哪一票？',['没有R，也有自己的三连击@mechanics','等关键技能，比等外卖更耐心@plan','这波技能不多，但够救队友@heal','重拍一次，我想换条时间线@reset'])]),
('hex','box','潘朵拉开箱',[
('天赋开箱','拿到“潘朵拉的盒子”，旧天赋要全部重抽。你的第一反应？',['开！旧人生需要一键刷新@reset','先算现有联动值不值这个风险@plan','现在顺风就不换，先稳住@retreat','我就是来录开箱视频的，直接开@chaos']),
('随机命运','抽完以后全队沉默三秒。弹幕问“有说法吗”，你怎么办？',['逐条找联动，临时写份使用说明@plan','先打一波，实践负责解释@engage','换种出装，让金币给天赋让路@gold','先保住核心，别让全队一起试错@protect']),
('桥上实验','这套新组合第一次打团，你最在意哪一幕？',['技能能不能衔接到没有空档@mechanics','能不能从远处不断刮出飞弹@poke','能不能一次开到三个人@engage','能不能平安带队回去补状态@heal']),
('开箱总结','赛后有人要你写开箱评语，你写什么？',['未知不是坏事，重抽才有续集@reset','记录收益和代价，下局再优化@plan','金币虽然没了，节目有了@chaos','下局优先给队友留条退路@protect'])]),
('hex','gate','对面家门打卡',[
('离谱导航','“尊我为王”让对方传送门看起来像领奖入口。你心动吗？',['心动，地图终点就是我的景点@engage','先看兵线和复活时间，别空跑@plan','全队先掩护一个人去领奖@protect','不去，远处输出比较适合我@poke']),
('门口保安','敌方五个人堵在入口。镜头里的突破方案是？',['雪球闪现，路线越短越好@chaos','等对面交完控制再进场@mechanics','从兵线节奏里找一段空窗@plan','正面吸引火力，把队友送过去@protect']),
('进门之后','门后的奖励未知，队伍现在最想要什么？',['能反复放大招的快乐@ult','一整面护盾，把人全带回来@heal','一件让血条突然消失的装备@collector','无所谓，随机人生比较有戏@reset']),
('旅游评价','回看这次敌方家门之旅，你打几句话？',['旅行可以失败，路线一定要帅@chaos','记下开门时间，下次不走弯路@plan','人齐才算旅行，少一个都回头@protect','奖励先结账，我的金币还在路上@gold'])]),
('hex','range','射程租赁公司',[
('长手邀请','三层瞄准镜像望远镜一样亮起，你会？',['接下，在泉水里给桥上点名@poke','不如给我雪球，我想面对面聊@engage','先看攻击方式能不能吃到收益@plan','把射程换金币，我想先成装@gold']),
('距离争议','队友喊“你站那么远怎么保护我”，你怎么应对？',['跟着队友的边缘移动，不脱节@protect','靠走A找极限安全输出点@mechanics','把自己当炮台，控制技能留给突进@control','再退两步，今天主打远程办公@retreat']),
('贴脸快递','一个刺客突然贴到后排，接下来怎么办？',['拉扯一步，普攻和位移交替@mechanics','闪现离开，活着才有下一轮@retreat','喊队友回头，先一起处理刺客@protect','直接对拼，看谁先到结算页@int']),
('射程总结','结算时你最想展示哪条数据？',['安全距离里打满的伤害@poke','关键一秒的走位慢镜头@mechanics','帮队友留下来的护盾量@heal','成装时间比闹钟还准@gold'])]),
('hex','giant','桥上出现巨人',[
('体型膨胀','“歌利亚巨人”摆在眼前，模型大到能给队友遮太阳。你选吗？',['选，我当全队移动掩体@protect','选，桥上终于有我的停车位@engage','再看看，体型大也更难躲技能@plan','我更想要射程，让巨人替我挡@poke']),
('挤桥事件','五个人挤在桥口，对面法师已经蓄力。你会？',['站侧面吸引技能，给队友让路@protect','倒数三秒一起进，不各自冲@plan','雪球命中就发车，车门焊死@engage','先刮血线，别把桥当升降梯@poke']),
('血条艺术','巨人残血了，但对面也只剩两个。怎么拍下一幕？',['继续顶，让后排把收尾做完@protect','先撤回治疗点，不给对面人头@retreat','一脚踩进去，体型就是胆量@int','算好控制和普攻，打极限反杀@mechanics']),
('赛后体检','队友说“你这把像一堵会动的墙”。你回复？',['墙也需要奶妈，请把治疗跟上@heal','下局我还能把先手开得更整齐@engage','体型只是表象，站位才是功课@plan','把墙租出去，每分钟收金币@gold'])]),
('hex','missile','飞弹售后服务',[
('技能快递','“魔法飞弹”亮了。你想让技能去哪里上班？',['越远越好，远程配送有加成@poke','先配技能急速，把快递班次加密@plan','站前面甩，追求每一发都中@mechanics','给我两个大招，我开一条快递专线@ult']),
('弹幕误会','队友把飞弹叫成“自动导航外挂”，你怎么接梗？',['这是售后，技能命中才发货@mechanics','先别聊，远处有人没收快递@poke','我去控制住人，方便全队签收@control','先给队友送口奶，再说伤害@heal']),
('残血诱惑','对方残血在桥尾跳舞，前排还挡着。下一步？',['等技能角度，不为一口血冒进@poke','雪球越过前排，今天必须签收@chaos','切换目标，先处理面前的人@plan','把人头让给成装差一点的队友@protect']),
('售后评价','赛后你的快递公司口号是？',['远一点，安全一点，弹也多一点@poke','技能精准，拒绝空包@mechanics','全队都能签收才算送达@protect','付款金币到账，评价稍后再说@gold'])]),
('hex','heal','全队唯一奶站',[
('队伍成分','四个输出喊“来个会奶的”。你看到“全心为你”会？',['收下，今晚我是桥头医务室@heal','能保人也能打，先看英雄再决定@plan','我去开，奶量交给下个宇宙@engage','我也出收集者，医务室改金店@collector']),
('治疗排队','四个人同时喊“奶我”，每个都说自己能C。你怎么办？',['优先救最可能活下来的那位@heal','按战局给关键位置，别按音量@plan','往前打控制，让对面先停手@control','群体治疗开出来，谁都别插队@protect']),
('队友迷路','核心追着残血跑远，后面还有三个人。你的镜头是？',['保住身边三个，别全队排队白给@plan','跟上护盾，把他接回家@heal','先手控住追兵，帮全队转身@control','一起冲，医务室今天出外勤@chaos']),
('赛后表彰','系统只显示输出排行，你想补哪一个奖？',['全队健康码常绿奖@heal','关键保护最后一秒奖@protect','冷静分配资源奖@plan','奶妈也要拿收集者奖@collector'])]),
('hex','clown','小丑学院开学',[
('录取通知','“小丑学院”给你发了通知书，你准备怎么入学？',['先背刺再隐身，课程直接实践@chaos','研究技能说明，先搞懂再搞事@mechanics','不入学，我想把队友保毕业@heal','先攒一件装备，学费不能贷款@gold']),
('隐身作业','隐身后能走到对面身旁，但队友还隔着半座桥。你会？',['先标记，等队友再一起露面@plan','现在就背刺，学分不能等@int','绕后封退路，不一定自己先打@control','侦察完就回，把信息交给队友@protect']),
('盒子事件','一个盒子把对方阵型搅乱了，下一镜头你选？',['借混乱拆掉后排，动作要细@mechanics','继续加料，整座桥开毕业典礼@chaos','先让队友安全穿过桥口@protect','不追，吃完这波兵再评估@stack']),
('毕业答辩','校长问“你在学院学到了什么”，你答？',['随机应变，比随机送强一点@reset','背刺角度也是一门几何@mechanics','混乱里记得带上队友@protect','毕业证先不拿，奖金拿一下@gold'])]),
('hex','stack','叠层永动机',[
('成长曲线','拿到“叠角龙”，每一层都像宇宙存款。你准备？',['先攒层数，后半场再长成恐龙@stack','我现在就要打，未来由拳头决定@engage','边叠边保队友，不让他们掉队@protect','先看英雄有没有能叠的能力@plan']),
('团战邀请','队友狂点进攻，你离下一档层数只差一点。你会？',['过去参团，层数可以边打边补@protect','先沟通等我一波，再一起打@plan','继续叠，我在为宇宙养老@stack','瞬间上头，层数不要了直接冲@int']),
('兑现时刻','成长终于成型，敌人却开始后退。你选择？',['卡住桥口，把优势换成地图推进@control','追着点，检验基本功作业@mechanics','雪球追上去，恐龙今天学跑步@engage','继续存，宇宙存折永不封顶@stack']),
('财务报告','本局结束，你的成长报告写什么？',['复利没有声音，结算很响@stack','每一波兑现都要有人接应@protect','强势期到了就该推进@plan','层数不够抽象，下局重开箱@reset'])]),
('hex','ult','大招再来一遍',[
('重播按钮','“终极刷新”出现。你脑中的第一张画面是？',['两个大招连着来，导演别切镜头@ult','先算好控制链，再决定怎么连@control','救人大招能再来一次，赚到@heal','基础技能手感更重要，我再看看@mechanics']),
('空大现场','第一个大招空了，刷新机会还在。队伍安静了。你怎么办？',['第二次等到必中窗口再按@plan','第二次立刻按，气势不能停@ult','先用小技能逼走位再补大@mechanics','往后拉，别把两个机会一起交掉@retreat']),
('名场面前夜','对面五人站得很整齐，队友却还在复活。下一步？',['记下位置，等队友到场@plan','双大先手，单人申请五人镜头@chaos','远处消耗，给队友争取时间@poke','守复活路线，确保下一波人齐@protect']),
('导演收工','回放只够保存十秒，你保存什么？',['第二次大招扭转局势的瞬间@ult','一整套没有断掉的控制@control','全队被拉回血线的那一秒@heal','空大后的沉默，配上喜剧音乐@reset'])]),
('hex','snowball','雪球驾驶学校',[
('驾校报名','雪球成了这座桥的通勤工具。你属于哪类司机？',['看见人就发车，乘客请抓紧@engage','先看后排距离，再按第二段@plan','只用于调整位置，拒绝急刹@mechanics','不用开车，我负责照看乘客@heal']),
('超载提示','雪球中了，但四位队友都没跟上。你下一秒会？',['取消进场，等下一班车@retreat','进！先下车的人负责热场@int','标记集火，让队友慢慢靠近@control','改成侦察，把对面技能骗出来@plan']),
('冰面追逐','对面交闪现逃跑，雪球还在冷却。你的计划？',['等下一轮技能，先整理阵型@plan','靠走位追击，技能普攻一起算@mechanics','停下救队友，不追单人纪录@protect','卖鞋买金币梦想，先把装备补满@gold']),
('毕业评价','教练给你的驾照备注会是？',['起步果断，车上最好有人@engage','安全驾驶，把全队送到下一波@protect','路线规划，桥上最稳导航@plan','特技表演，保险请另购@chaos'])]),
('rift','draft','五楼选人的艺术',[
('最后一选','队伍四个脆皮，五楼的你被问“能补个前排吗”？',['锁个能扛的，先让阵容成形@protect','锁刺客，脆皮也能冲出未来@chaos','先问大家擅长什么，再决定@plan','锁ADC，第五位股东也要吃兵@collector']),
('一级分歧','辅助喊一级团，打野却在给野怪发问候。你支持？',['全队统一口令，人齐再走@plan','走，一级团也是一种开场白@engage','站路口守着，别让人被偷@protect','先补兵，经济不会自己长腿@gold']),
('第一波交锋','对面漏出一个机会，你希望怎么接？',['先手控制，把机会交给全队@control','细节操作，自己把缺口撕开@mechanics','远处试探，别把阵容打散@poke','我来抗第一下，队友跟上@protect']),
('选人复盘','赛后回看这次阵容，你想改什么？',['少一点重复定位，多一点配合@plan','保住输出的人也该被看见@heal','再放飞一点，未知才有节目@reset','不改，我的兵线账户很满意@gold'])]),
('rift','gank','打野经过你家门口',[
('求救信号','你被压在塔下，打野从门口路过，你打什么字？',['哥，来一眼，眼不是白带的@protect','不打字，我自己找操作机会@mechanics','先报闪现和兵线，再约下一波@plan','开送一次，试试打野会不会回头@int']),
('路线争议','打野标记要反野，中路却被推线。镜头选哪条路？',['先帮中路清线，再一起进野区@plan','直接进，对面营地也有我的梦想@engage','守住河道，防止队友被包@protect','去刷自己的野，经济不能断@stack']),
('河道遭遇','河道碰到三个人，队友离你两屏。下一步？',['后撤，把位置和人数报清楚@retreat','交控制拖时间，不硬拼@control','操作一下，试试这局手热不热@mechanics','冲，三个人够剪一期视频@chaos']),
('打野报告','你给这位打野留一句评语？',['路线能沟通，比路线像迷宫强@plan','保护做得好，下一局还找你@protect','河道打得精彩，镜头记住了@engage','刷得漂亮，我也想承包野区@gold'])]),
('rift','dragon','龙坑股东大会',[
('资源决策','龙刷新了，队友还差一笔钱做装备。你决定？',['先等装备，少一条龙别少四个人@plan','直接开，装备以后可以分期@gold','埋伏入口，先把对手拦住@control','我来开第一波，队友自由发挥@engage']),
('坑口拉扯','对面假装走远，辅助说“肯定没走”。你怎么安排？',['用技能探路，不拿脸签快递@poke','排好视野再进入@plan','让坦克先站位，后排跟紧@protect','脸探一波，悬念需要主角@chaos']),
('惩戒前夜','龙只剩一点血，对方打野准备进场。你盯哪里？',['盯对方打野，控制留给他@control','盯龙血线，技能和普攻压一起@mechanics','盯队友血线，先保住关键人@heal','盯人头，龙坑也能出收集者@collector']),
('会议纪要','抢完龙之后你最想说什么？',['资源是团队项目，别各写各的@plan','龙没那么重要，人要一起活着@protect','操作这一秒，值得回放三遍@mechanics','奖金先结算，装备更新了@gold'])]),
('rift','galio','加里奥又来了',[
('平行S8','平行S8决胜局，对面的飞科又锁了加里奥。你接什么剧本？',['我是污渍，这次把输出打满@mechanics','先规划转线，不让加里奥到处飞@plan','补保护，谁也别把下路单独丢下@protect','先上头再说，结局需要一次冲锋@engage']),
('全球支援','边线一打起来，加里奥的圈就亮了。你的反应？',['立刻拉开，等落地再反打@retreat','掐好落地点，把控制接上@control','保住核心输出位不被碰到@protect','趁他不在正面，换资源@gold']),
('冠军团战','最后一波团战，人群里出现一条输出缝隙。你会？',['侧身躲技能，普攻一下一下打@mechanics','把保护技能全部留给输出核@heal','果断开团，帮全队打开角度@engage','再等一个关键控制的冷却@plan']),
('金色的雨','这个架空宇宙终于下起金雨，你先做什么？',['抬头看奖杯，再看一起撑过来的队友@protect','保存走位回放，给未来的自己看@mechanics','把战术板收好，下一年继续@plan','先点收集者，冠军也有金币@collector'])]),
('rift','split','上单开了单人宇宙',[
('边线选择','上单说“你们四个守，我能带穿”。你回复？',['报对面位置，给他稳定信息@plan','跟着一起带，单人宇宙升级双人@engage','保住正面，给边线争时间@protect','我也去吃边线，这局按人头收费@gold']),
('五人包夹','小地图上五个人都去抓边线了。下一镜头？',['换龙或推塔，把时间变资源@plan','开车去救，不能让兄弟独自谢幕@protect','让他操作，我们先看回放@mechanics','一起传过去，边线办总决赛@chaos']),
('拆家倒计时','对面基地露出破绽，回城光柱也亮起来。你选？',['控制住回城的人，给拆家争秒数@control','直接拆，普通攻击也是艺术@mechanics','回防自家核心，别换家换亏@retreat','技能全开，今天大招也打建筑@ult']),
('分带评价','这局单带战术最后怎么命名？',['地图不是一条线，信息才是路线@plan','四个人守住，才有一个人自由@protect','我独自上路，但没忘全队@mechanics','塔归你，兵线利息归我@gold'])]),
('rift','support','辅助申请上桌',[
('辅助宣言','辅助出了输出装，说“今天轮到我C”。你反应？',['可以，我把控制和保护补上@protect','给你视野，先保证能打到人@plan','我也出输出，五个人轮流C@collector','那我玩奶妈，全队经营奶站@heal']),
('视野学问','眼位刚插下就被排了，辅助看着你。你怎么接？',['一起走，别让一个人去探黑@protect','记下对面动向，眼没白消失@plan','用技能探草，把风险降下来@poke','直接进草，镜头已经给我了@chaos']),
('保护对象','团战里两个队友同时残血，你救谁？',['先救能活下来的，再找第二个@heal','用控制打断对面追击@control','保住输出核，按胜利条件走@plan','冲进对面，让他们没空追人@engage']),
('赛后座位','赛后饭局只剩一个主位，你给谁？',['给辅助，全队能动起来靠他@protect','给最关键的操作，谁都能坐@mechanics','给战术指挥，今天安排得明白@plan','我先坐下，再给大家倒杯奶@heal'])]),
('rift','pause','逆风语音聊天室',[
('落后五千','逆风五千，语音有人开始算锅的大小。你怎么办？',['挂机，给语音留出安静空间@afk','开送，让节目先到高潮@int','拆成下一波能做的事，慢慢说@plan','给队友一句肯定，先把人留住@protect']),
('翻盘提示','对方核心带着赏金走进河道。镜头怎么继续？',['等队友齐了再包，别单独兑奖@plan','控制先手，把赏金交给全队@control','极限操作一下，机会靠自己抓@mechanics','全员冲过去，赏金就是集合哨@engage']),
('守家时刻','门牙塔只剩一座，超级兵已经进门。你优先？',['清兵保塔，先让游戏继续@plan','给清线的人加血加盾@heal','找机会开到后排，搏一波@engage','继续叠成长，相信下一页存折@stack']),
('逆风结算','无论这局输赢，你最想带走什么？',['下次能执行得更好的翻盘路线@plan','没散掉的五人语音@protect','那一秒真的敢操作的自己@mechanics','这个结局不够离谱，再开一把@reset'])]),
('rift','rematch','赛后再来一把',[
('再战邀请','输赢刚结算，队友说“最后一把”。你相信吗？',['相信，这是循环里的最后一把@reset','先复盘一个问题，别原样再来@plan','人还齐就开，我喜欢这支队伍@protect','开，下一把我一定要拿输出核@collector']),
('位置交换','队友突然想跟你换位置，理由是“风水不好”。你会？',['换，队伍舒服比我位置固定重要@protect','先看熟练度，别把风水换成天气@plan','换个需要操作的位置，正好练手@mechanics','直接玩个没试过的，给风水换宇宙@chaos']),
('最后一团','这真的是今晚最后一团，你希望镜头停在哪里？',['全队一起进，一起退@protect','走位和技能严丝合缝的瞬间@mechanics','大招连成一条银河@ult','对方残血被我当场收集@collector']),
('晚安留言','关掉游戏前，你留给五人群什么？',['下次还这五个，一个别少@protect','发一张关键时间点复盘图@plan','把操作回放剪成十秒@mechanics','发“下把必C”，然后再点一次开始@reset'])])]
CH.append(('rift','spring','春季保温箱',[
('季节预报','平行世界的日历全写着春天，销户问你想先练哪项？',['先算边线与支援的时间差@plan','训练走位，春天也需要基本功@mechanics','练保护，让队伍一起过春天@protect','练开团，春天不能只等花开@engage']),
('温度骤降','对面把节奏拖进深夜，赛场恒温器开始报警。下一步？',['稳定补刀，先把装备攒出来@stack','组织一波先手，把场面打热@engage','留好控制，不让后排吹冷风@control','先回家，买件装备当保暖内衣@gold']),
('最后一波','队友说再赢这一团就能入春，你想怎么打？',['先等对面失误，再接完整控制链@control','大招全开，这次让桥上开花@ult','跟紧输出，护盾不能晚到@heal','练过的连招自己按出来@mechanics']),
('春日结算','奖杯旁多了一台恒温器，你写一句使用说明。',['先安排节奏，再决定今天几度@plan','五个人一起热起来才算春天@protect','把关键操作练到四季通用@mechanics','温度随机，人生允许重抽@reset'])]))

qs=[]
for series,cid,name,rows in CH:
 for stage,(scene,title,opts) in enumerate(rows):
  options=[]
  for oid,item in enumerate(opts):
   text,key=item.rsplit('@',1);v,tags=S[key];options.append({'id':oid,'text':text,'signals':dict(zip([d['id'] for d in D['lolDimensions']],v)),'tags':tags,'behavior':key})
  qs.append({'id':f'{series}-{cid}-{stage}','theme':'lol','series':series,'chapter':cid,'chapterName':name,'stage':stage,'scene':scene,'title':title,'options':options})
D['questions']=qs+[q for q in D['questions'] if q['theme']!='lol']
vecs={'uzi':[65,82,65,60,90,55],'xiaohu':[32,55,45,70,72,90],'dasima':[35,55,32,58,64,95],'theshy':[60,65,92,42,96,35],'faker':[22,55,58,75,92,88],'clearlove':[18,65,35,70,62,98],'jackeylove':[75,75,95,58,85,30],'doinb':[60,45,78,90,65,75],'pdd':[75,65,82,62,58,40],'ming':[35,25,82,97,68,65],'meiko':[15,30,45,98,70,88],'letme':[20,30,42,90,55,92],'ning':[70,65,92,65,80,38],'knight':[25,68,52,55,98,75],'baolan':[35,28,60,92,60,72]}
for p in D['characters']:
 if p['theme']=='lol':p['vector']=vecs[p['personId']]
# Pin actual KIWI pool, do not infer ARAM effects or rarity from Arena data.
raw=json.loads((R/'cherry-augments.json').read_text());lists=json.loads((R/'augment-lists.json').read_text());pool=next(x for x in lists if x['modeName']=='KIWI')
ids={x.rsplit('/',1)[-1] for x in pool['augmentList']};wiki='https://wiki.leagueoflegends.com/en-us/ARAM:_Mayhem/Augments'
A=[
('ARAM_BacktoBasics','强化基础技能的伤害、治疗与护盾，并提供技能急速；无法施放大招。',[25,45,50,50,98,75],['basic','mechanics'],'你愿意把胜负交给小技能和基本功，连R键都可以放假。'),
('ARAM_Upgrade_Collector','升级收集者的处决能力；参与击杀可提升处决阈值至上限，并提供额外金币收益。',[65,98,70,25,65,30],['collector','gold'],'你看见的不只是残血，还有闪着金光的下一件装备。'),
('ARAM_ClownCollege','获得萨科式的背刺和欺诈玩法；阵亡时还会留下爆炸与恐惧盒子。',[90,35,90,20,65,15],['chaos'],'你会把一局普通对战拍成悬疑喜剧，背后总还有下一幕。'),
('ARAM_PandorasBox','获得一个随机棱彩强化，并将已有强化转换为同数量的随机棱彩强化。',[60,40,60,45,50,25],['reroll','reset'],'你愿意改写已经成形的剧本，重抽一次也是一种人生选择。'),
('ARAM_Goliath','获得额外生命值和自适应之力，并显著增大体型。',[45,35,85,80,50,45],['engage','team'],'你更像往前站的那个人，把自己变成队伍的移动掩体。'),
('ARAM_MagicMissile','技能命中敌方英雄后发射飞弹；飞弹造成基于目标生命值的真实伤害，距离会影响效果。',[25,55,30,50,85,65],['range','spell'],'你偏爱隔着半座桥把每一发技能送到，距离就是发挥空间。'),
('ARAM_AllForYou','提升你对友方英雄施加的治疗与护盾效果。',[15,20,35,98,65,80],['heal','protect'],'比起独占镜头，你更在意让五个人一起走到下一波。'),
('ARAM_FirstAidKit','获得治疗与护盾强度加成。',[20,25,25,90,60,80],['heal'],'你会先看谁需要被接住，桥头医务室已经为队友开门。'),
('ARAM_JeweledGauntlet','技能可以产生暴击，并获得暴击几率加成。',[55,70,65,40,95,40],['mechanics','spell'],'你相信准确落下的技能值得一个更响亮的结算。'),
('ARAM_ScopedWeapons','增加普通攻击射程，近战与远程英雄的收益不同。',[15,55,20,50,80,75],['range','retreat'],'你会先找安全位置，再把稳定输出打成自己的名场面。'),
('ARAM_StackosaurusRex','增加从技能获取的永久层数。',[15,90,25,45,55,98],['stack','plan'],'你愿意等成长兑现，层数像存款一样一笔笔积累。'),
('ARAM_UltimateRevolution','施放大招后可触发一次大招冷却重置；该效果自身有冷却。',[60,50,80,60,85,40],['ultimate'],'你希望关键镜头再来一遍，第二次按下大招才是高潮。'),
('ARAM_IceCold','你的减速效果会额外降低目标的移动速度。',[20,35,40,80,75,90],['control','plan'],'你习惯先让场面慢下来，再替队伍把节奏接好。'),
('EscapePlan','生命值较低时提供会衰减的护盾与移速，并缩小体型；效果有冷却。',[35,30,10,35,50,55],['retreat','reset'],'你总留着离场按钮，活到下一幕也能写出新结局。'),
('KingMe','首次进入敌方基地附近的传送入口或发射装置，可获得随机棱彩强化并升级一件装备。',[75,55,98,45,65,20],['engage','chaos'],'对方家门在你眼里像领奖入口，越离谱的路线越想试。'),
('Goldrend','攻击或技能伤害敌方英雄可触发额外伤害，并给予金币与移速；有触发冷却。',[35,95,45,35,60,65],['gold'],'你会把每次试探都变成收入，金币到账的声音最好听。')]
def fetch(row):
 key,effect,vec,tags,reason=row;a=next(x for x in raw if x['augmentNameId']==key);assert key in ids
 english=['Back to Basics','Upgrade Collector','Clown College',"Pandora's Box",'Goliath','Magic Missile','All For You','First-Aid Kit','Jeweled Gauntlet','Scoped Weapons','Stackosaurus Rex','Ultimate Revolution','Ice Cold','Escape Plan','King Me','Goldrend'][[x[0] for x in A].index(key)]
 page=html.unescape((R/'lolwiki.html').read_text())
 tag=next(t for t in re.findall('<img[^>]+>',page) if 'alt="An icon for the ARAM: Mayhem augment '+english+'"' in t)
 src=re.search('src="([^\"]+)"',tag)[1];src=re.sub(r'/thumb/([^/]+)/[^/?]+',r'/\1',src)
 url='https://wiki.leagueoflegends.com'+src
 cached=ROOT/'assets'/'augments'/(key+'.png')
 b=cached.read_bytes() if cached.exists() else urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=25).read()
 asset='augments/'+key+'.png';(ROOT/'assets'/asset).write_bytes(b)
 return {'id':key,'clientId':a['id'],'name':a['nameTRA'],'rarity':a['rarity'],'effect':effect,'line':reason,'vector':vec,'tags':tags,'bias':[(v-50)/50 for v in vec],'asset':asset,'iconSource':url,'sha256':hashlib.sha256(b).hexdigest(),'sourcePage':wiki,'pool':'KIWI','patch':'16.21','officialReference':True}
with ThreadPoolExecutor(max_workers=8) as ex:D['augments']['lol']=list(ex.map(fetch,A))
D['augmentData']={'patch':'16.21','checkedAt':'2026-10-23','clientVersion':'16.21.8298620','clientSource':'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/zh_cn/v1/cherry-augments.json','poolSource':'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/zh_cn/v1/augment-lists.json','effectSource':wiki,'note':'名称、稀有度与图标取自16.21端游KIWI池；效果为Wiki机制简述，省略易变数值。人格解读为本作原创，不代表实战英雄强度推荐。'}
(ROOT/'src/data.json').write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n')
(ROOT/'assets/augment-sources.json').write_text(json.dumps(D['augments']['lol'],ensure_ascii=False,indent=2)+'\n')
print(len(qs),'new LoL questions;',len(D['augments']['lol']),'verified reference augments')
