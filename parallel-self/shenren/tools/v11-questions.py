"""Reviewed edits are explicit per chapter/question; archived IDs remain readable."""
from pathlib import Path
import json,copy,collections
R=Path(__file__).resolve().parents[1];D=json.loads((R/'src/data.json').read_text());old=json.loads((R/'src/legacy/data.json').read_text());before={q['id']:q for q in old['questions']};reviews=[]
# Each scene is four sequential moments. Each option keeps a semantic behavior, not a good/bad rank.
chapters=[
('netcafe','今晚五黑，网费先别停',[
('五个人终于坐成一排。开机第一件事，你会？','mechanics|先调鼠标灵敏度，今天手感必须像个高手。','protect|问一圈吃啥，五个人先把泡面阵容配齐。','engage|戴上耳机宣布：这把我C，你们随便。','gold|看一眼余额：够打一把，还是够嘴硬一晚上？'),
('喊了半天“跟我冲”，发现麦克风没开。你接下来？','engage|开麦再喊一遍，刚才不算正式演出。','chaos|假装在指挥隔壁桌：我说你们了吗？','vision|疯狂打信号，让鼠标替我说话。','explain|默默回来，解释这是一次免费的地形考察。'),
('战绩0/5，队友问你还行不行。你先说？','explain|先别看数字，我给你讲讲对面为什么亏。','blame|这耳机漏音，刚才操作都漏出去了。','protect|外卖到哪了？先把线下发育补起来。','mechanics|再给我一次，下一波就是翻身局。'),
('大家都说“最后一把”，网管来问还续不续。你会？','reset|续，刚才那把只算热身。','calm|我先把面吃完，给我留个位置。','explain|截张战绩，明天在群里继续复盘。','chaos|口头说不续，手已经点了再来一局。')]),
('noodles','泡面先别泡开了',[
('排队进游戏时泡面刚好。你把碗放哪儿？','plan|鼠标够不着的地方，先保住这一桌。','protect|给队友也递个叉，整齐开饭。','gold|泡面加肠，游戏里的经济另算。','chaos|键盘旁边，红烧牛肉负责提供压迫感。'),
('刚吃一口，队友突然喊救命。你怎么接？','engage|叉子一放，我来了！','explain|嘴没空说话，手上的信号先到。','protect|先替他挡一下，面还能再泡会儿。','calm|等我咽完，这波不能连人带面送。'),
('队友看你碗里还剩半碗，说你发育太慢。你回？','gold|我这叫囤资源，后期有面。','chaos|你游戏0/3，就别点评我的饭量了。','laugh|先笑，等他面坨了再笑一遍。','explain|面条也讲节奏，给你展开说说。'),
('结算赢了，面也凉了。你先？','reset|换碗热的，再续一局。','protect|五个人碰个可乐，面冷了也值。','plan|下把开前吃完，优化一下流程。','chaos|拍张图：冠军套餐，赛后限定。')]),
('mic','宿舍麦克风试营业',[
('舍友都上线了，就差一句开场白。你来？','engage|人齐了，今晚听我发车。','calm|先打个招呼，手热了再聊。','chaos|喂喂喂，今天的语音质量由我担保。','protect|谁还没来？给他留位置。'),
('说了十分钟才发现一直在和系统提示音聊天。你会？','explain|先确认：你们刚才不是被我震住了？','laugh|自己笑完，再让全队补听一遍。','plan|调好麦，下一句说重点。','blame|这耳机，错过了一场精彩指挥。'),
('舍友说你声音太大，隔壁都知道你0/4了。你回？','chaos|隔壁可以来观摩翻盘。','calm|把音量拧小，战绩还得继续打。','explain|0/4只是这段演讲的背景。','protect|给室友道个晚安，改用信号交流。'),
('夜深了，语音终于安静。你最后补一句？','reset|最后一把，音量真不再加了。','plan|明天同一时间，麦提前测好。','protect|睡前记得喝水，兄弟们散会。','chaos|这场直播没有观众，但节目挺满。')]),
('clip','先别删我的高光',[
('朋友要录你这一局。你先提哪个要求？','mechanics|等我操作，镜头跟紧。','chaos|只拍进场，不拍复活时间。','plan|完整录，回头一起看。','protect|五个人都拍进去，别只盯我。'),
('你闪现撞墙，朋友的录制灯还亮着。你会？','flash|再试一次，墙也有适应期。','explain|我在测试这面墙的碰撞体积。','laugh|先笑一遍，自己给视频配音。','calm|留着吧，明天当提醒。'),
('剪出来只剩你灰屏的镜头。你怎么选？','blame|素材偏差，摄像师也有责任。','chaos|标题写“对手集锦友情出演”。','mechanics|下一局补一段，我还没交作业。','protect|加上队友救我的那次，完整一点。'),
('视频发到群里，大家问还拍不拍。你答？','reset|拍，续集里我一定活久点。','explain|先播导演解说版。','plan|下次每人留一个镜头。','laugh|把笑声也留着，比伤害还高。')]),
('boss','网吧老板先别走',[
('五黑只剩最后一台连座机，谁坐单独那台？','protect|我去，语音在就算坐一排。','engage|我过去，当这队的外勤。','plan|问问能不能一起挪一下。','chaos|给我挂个包间牌，气势不能输。'),
('老板路过，问今天能不能打出个名场面。你回？','mechanics|等这波，我手里还有活。','gold|先记账，双斧今天争取回款。','chaos|名场面有，方向可能不太一样。','calm|老板坐会儿，快乐是稳定产出。'),
('刚说完就连着失误两次，老板还在。你会？','explain|刚才展示错误示范，正片马上来。','reset|再开一把，样本量还不够。','blame|这位置离空调太近，手有点僵。','laugh|请老板先笑，我再补第二段。'),
('离店前老板问要不要保留老位置。你说？','plan|周五七点，留五台。','protect|兄弟们都来再定，不落单。','gold|先结账，战绩下次还。','chaos|留，椅子比我更懂这套操作。')]),
('duo','双人相声不下播',[
('队友说了个冷笑话，语音突然安静。你会？','chaos|补一句，让冷场自己下班。','explain|给他铺个背景，包袱重新抖。','laugh|先笑，笑声负责带路。','calm|留半秒，他可能还有后半句。'),
('你俩同时开口，把关键提醒讲成了双声道。你会？','plan|你讲这波，我补下一句。','chaos|左右耳各一个，立体声福利。','protect|先停，听队友说救命。','explain|重播一次，这次按顺序来。'),
('有人提起老IG合照，整队开始翻相册。你先？','explain|讲一段当年的开黑故事。','protect|点个名，老队友一个别落。','laugh|找那张所有人都没看镜头的。','mechanics|回忆归回忆，这波手还在操作。'),
('打完朋友催下播，你还剩一句。你说？','chaos|下一句说完就下，真就一句。','plan|最后报个时间，明天继续。','protect|谢过搭档，五人合照再走。','laugh|笑一下再关，别卡在严肃画面。')]),
('jungle-date','七点准时发车',[
('约好七点五黑，六点五十九分你在？','plan|群里点名，人齐准时发车。','mechanics|训练模式里热手。','chaos|打字说马上到，耳机正在找。','protect|给还没下班的队友留个位置。'),
('打野把路线画得像个正方形。你怎么看？','explain|听完，第四条边还没讲到。','engage|先跟他走一段，看看去哪。','gold|走到哪吃到哪，不能空手回。','plan|问清集合点，别绕回出发地。'),
('说好一起上，队友却走错了岔路。你先？','vision|报个位置，先让大家找到彼此。','chaos|熟人局，导航也要有点个性。','engage|我去接他，临时改个集合点。','explain|这路线有意思，等复活了慢慢讲。'),
('散场时问明天几点，你答？','plan|还是七点，路线今晚画好。','reset|明天再说，今晚还有最后一把。','protect|按大家方便的时间，别催下班。','chaos|随叫随到，前提是我还醒着。')]),
('top-alone','上路在另一个宇宙',[
('队友问你上路怎么没声音，你回？','mechanics|别吵，我在和对面聊天，用鼠标。','calm|信号收到，我这儿还挺安静。','engage|抓我？那我再多待会儿。','protect|你们需要我就喊，我能回来。'),
('对面来了三个人，四个队友正在看你。你会？','mechanics|试试操作，这镜头不能白给。','vision|先报人数，别处可以轻松一点。','retreat|留个退路，观众还想看下一段。','chaos|问一句：抓我就能赢吗？'),
('你刚秀完，发现队友已经去别的地方。你先？','blame|我队友呢？先确认一下宇宙坐标。','laugh|自己笑一下，这段独播。','plan|问集合地点，下波一起。','gold|先把眼前这波吃完再过去。'),
('回到五人合照里，你站哪儿？','mechanics|边上，保持一点上路空间。','protect|挨着队友，今天终于同框。','chaos|拿手比个传送圈，表示刚赶到。','explain|中间，先讲讲刚才怎么活下来的。')]),
('clinic','中路急诊室夜班',[
('开局两个队友都喊“来救”。你先？','protect|问谁更急，先把能接住的接住。','plan|报集合位置，别一个个跑散。','mechanics|给我十秒，先处理眼前这位。','explain|先叫号，院长一次看一边。'),
('队友夸你像院长，你怎么接？','protect|先坐，别又把血条打没。','chaos|加班可以，挂号费用可乐结。','calm|这波配合不错，不全是我的。','mechanics|先别夸，手上这波还没完。'),
('刚稳住一个，另一个又喊你名字。你会？','engage|听到了，马上到下一站。','plan|安排大家先退一步，我在路上。','explain|这不是查房，这是全地图巡诊。','protect|先让刚救好的帮忙，别再落单。'),
('赢了以后队友问你想要什么。你选？','calm|准点下班，今天真打够了。','protect|全队一张合照，没人躺着。','chaos|一张免加班卡，最好能叠。','reset|下一局换你们救我。')]),
('ad-insurance','下路售后服务台',[
('朋友说他这把想体验当主角。你选？','protect|我来陪你，保修范围到基地。','heal|你冲，先留在我的治疗范围。','engage|我先找机会，你等我信号。','gold|两个人轮流吃，别把钱包饿着。'),
('主角冲太快，喊你怎么还没到。你回？','protect|慢点，接送车还在路上。','vision|发个位置，别让我靠猜。','explain|售后不含跨地图瞬移。','chaos|你这速度，保险要加急。'),
('你刚救回朋友，他又想冲。你会？','control|先拉住，让他把水喝一口。','heal|补满状态，再问他确定不。','engage|这次一起，提前说清楚。','laugh|先笑他一秒，再继续接人。'),
('朋友问下次还能找你双排吗。你回？','protect|行，老客户继续包接送。','plan|约好时间，别临时喊救命。','chaos|可以，先给售后服务打五星。','reset|换你保我一次，也体验一下。')]),
('keyboards','稳健先缓一缓',[
('朋友夸你今天特别稳健。你第一反应？','calm|先打完，夸早了容易出事。','chaos|把稳健存起来，待会儿取。','engage|正好，下一波我试个大的。','plan|今天按计划走，问题不大。'),
('你刚想解释，队友也在解释，语音挤爆了。你会？','blame|等一下，先让我把前因讲完。','plan|一个个来，先说下一步。','chaos|开两倍速，争取把话塞完。','calm|先听，手上别停。'),
('朋友把你的“稳健”剪成失误合集。你回？','chaos|稳健暂时离线，稍后重连。','explain|每一帧都有背景，我能解释。','mechanics|今晚补段好的，封面换一换。','laugh|置顶，承认这段确实好笑。'),
('到你给视频配最后一句。你选？','explain|轮到我解释了，先别关。','calm|今天这样，明天再稳。','reset|重开，片名还是《稳健》。','chaos|这不是失误，是留给剪辑的工作量。')]),
('watchparty','二路观赛小客厅',[
('朋友看S赛，给你留了一个解说位。你先？','explain|先把前情讲清楚，零食递过来。','laugh|等一个镜头，全队一起笑。','plan|把声音调好，正片别错过。','protect|谁第一次看？我给你解释简单点。'),
('暂停五分钟，朋友问聊什么。你会？','explain|从赛前集合讲起，时间够用。','chaos|把刚才那个表情现场演一遍。','plan|猜猜回来谁先动，别搞太专业。','calm|吃两口，回来继续看。'),
('你猜的全错，朋友准备截你表情。你先？','blame|预测是娱乐，截图要标明上下文。','laugh|别停，我自己也想存。','explain|我换个角度，重新解释一次。','protect|错得整齐，大家都能笑。'),
('比赛完了，四个朋友还等你的总结。你说？','explain|给我一分钟，故事刚到高潮。','chaos|今晚最佳：那袋没被吃完的薯片。','plan|冠军合照先看，接下来约明年。','protect|不管支持谁，今天人齐就挺好。')]),
('water','水温检测站',[
('朋友问今天哥哥敢不敢向前。你回答？','engage|敢，先说好你们跟不跟。','mechanics|先把手热起来，再给镜头。','calm|水温先测，热了再下。','chaos|先订个高光位，结算再付款。'),
('你向前一步，朋友们却同时后退。你先？','flash|再多走半步，先找个出口。','blame|你们怎么倒车？','explain|这波是测大家的跟车距离。','plan|回来对一下口令，下次一起。'),
('结算前朋友说今天你节目挺满。你回？','chaos|暴毙也有节目，门票不退。','mechanics|有好的也有坏的，好的别漏剪。','laugh|我先笑，防止你们笑得太孤单。','calm|记下这波，下次留半步。'),
('下次开黑的群公告怎么写？','engage|向前请报数，五个人一起。','protect|一个人冲了，另外四个要接。','chaos|水温异常，仍在营业。','plan|热身五分钟，冲动少一点。')]),
('salary','冠军展柜又满了',[
('朋友送你一个小奖杯，表扬你今天没掉线。你会？','calm|摆好，这也是稳定发挥。','chaos|腾个柜子，下一座安排上。','mechanics|奖杯先放，手上还有一波。','protect|全队合个影，五个人都有份。'),
('你发现闪现还在，朋友问是不是忘了按。你解释？','plan|存着，等一个真要用的地方。','mechanics|用不用都得活着把操作做完。','chaos|这是传家宝，谨慎出库。','explain|看回放，我给你讲那半秒。'),
('朋友发现你一直切其他人镜头。你会？','vision|查个岗，看看谁需要帮忙。','protect|关心一下队友，不是监工。','chaos|五个屏幕，一张网费。','calm|有信息才安心，顺手看两眼。'),
('散场收奖杯时，你最后带走什么？','plan|下一局的约定，时间记好。','mechanics|那段顺手的操作，回去再看。','protect|四个人的联系方式，一个别丢。','chaos|展柜尺寸，下次买大点。')]),
('review-home','战绩只是聊天背景',[
('你刚进语音，就被问昨天为什么没赢。你先？','explain|先听我从登录界面讲起。','blame|先统一一下，昨天谁说稳了？','laugh|别问了，我已经笑出第二段。','calm|昨天存档，今天再打。'),
('朋友翻出一张你吹牛的截图。你怎么接？','chaos|过期宣传，活动解释权归本人。','explain|我当时的说法有特定语境。','mechanics|今晚补场表现，截图先别删。','protect|也翻翻我救你的那张，凑一对。'),
('你一边解释一边被队友叫走。你会？','engage|课后再说，先去接人。','explain|手先过去，嘴把最后一句讲完。','plan|一句话总结，等打完再放回放。','laugh|暂停公开课，开始实操考试。'),
('今晚结束，朋友问明天还吹吗。你说？','chaos|吹，控制一下虚假广告长度。','mechanics|明天用操作说话。','protect|只要还一起玩，谁吹都行。','reset|明天？今晚先再来一把。')])]
# Existing chapters retained for their own meme; not transferred to unrelated people.
life_old={'office','review','table'}
meme={'collector','double-laugh','tes-top','spring','galio','worlds-party','ig-memory','deyunse','bro-flash'}
game={'range','heal','lane-basics'}
for q in D['questions']:
 q['enabled']=True
 if q['theme']=='lol':
  q['enabled']=q['chapter'] in life_old|meme|game;q['editorialCategory']='life' if q['chapter'] in life_old else 'meme' if q['chapter'] in meme else 'gameplay'
  status='保留' if q['enabled'] else '退出默认池';reason='保持连贯章节与好梗' if q['enabled'] else '本轮减少专业判断或重复情境，旧ID保留'
 else:
  # These scenes name people outside the 40-person cast; do not swap names mechanically.
  retired=['奥尼尔','邓肯','约老师','罗德曼','加内特','文班','华子','保罗','卡特','麦迪','孙悦','郭艾伦','王猛','苏群','张卫平','于嘉','字母哥','李子柒','郭德纲','孙越','马斯克','黄仁勋','罗翔','郭有才','闻会军','李佳琦','葛优','papi','白客','王老菊']
  q['enabled']=not any(n in q['title'] for n in retired)
  status='保留' if q['enabled'] else '退出默认池';reason='保留普通人能回答的日常' if q['enabled'] else '人物不在40人版；不强换其他人物'
 q['review']={'status':status,'reason':reason};reviews.append({'id':q['id'],'theme':q['theme'],'status':status,'reason':reason,'before':before[q['id']]['title'],'after':q['title'] if q['enabled'] else None})
# Tweak awkward, previously expanded jargon; same IDs and option semantics.
fixes={'打掉最后一下拿金币':'补最后一下','回家买装备出装':'回家出装','连续控制技能':'控制技能','冲到脸上':'近身','回家买装备更新装备':'回家更新装备'}
for q in D['questions']:
 if not q['enabled']:continue
 changed=False
 for target in [q]+q['options']:
  for key in ['title','text','tip']:
   if key in target:
    text=target[key]
    for a,b in fixes.items():text=text.replace(a,b)
    if text!=target[key]:target[key]=text;changed=True
 if changed:q['review']={'status':'微调','reason':'修复拗口的术语展开，保留原行为语义'};row=next(r for r in reviews if r['id']==q['id']);row.update(status='微调',reason=q['review']['reason'],after=q['title'])
# Signals use the existing behavior's authored median, so random option order never changes scoring.
prototypes={}
for b in D['behaviorLabels']:
 opts=[o for q in old['questions'] if q['theme']=='lol' for o in q['options'] if o['behavior']==b]
 if opts:prototypes[b]={d:round(sum(o['signals'][d] for o in opts)/len(opts)) for d in opts[0]['signals']}
for i,(cid,name,rows) in enumerate(chapters):
 for stage,row in enumerate(rows):
  q=dict(id='v11-'+cid+'-'+str(stage),theme='lol',series='hex' if i%2==0 else 'rift',chapter=cid,chapterName=name,stage=stage,scene=['开机与集合','语音接梗','朋友拆台','散场与下一局'][stage],title=row[0],options=[],importance=1,tip='',enabled=True,editorialCategory='life',review={'status':'新增','reason':'网吧与朋友四幕日常'})
  for j,s in enumerate(row[1:]):
   b,text=s.split('|',1);q['options'].append(dict(id=j,text=text,behavior=b,tags=[b],signals=copy.deepcopy(prototypes[b])))
  D['questions'].append(q)
# Non-League samples, preserving independent six-dimension coverage.
samples=[
('basket','action','打铁这天', '今天投篮一直打铁，下一回合你准备？',['nba-train|再试一球，手感不能靠想象找回来。','nba-three|往远处退两步，说不定是站太近了。','nba-team|先给队友传，最后一球再喊我的名字。','nba-rebound|去篮下抢板，今天换个方式交作业。']),
('basket','express','赛后复盘','朋友问刚才输在哪儿，你会？',['nba-plan|摆出战术板的架势，从第一球开始说。','nba-emotion|我立个观点，这球得单独聊半小时。','nba-calm|先喝口水，打下一场的时候再试一试。','nba-show|拿出视频：先确认摄像师有没有把我拍帅。']),
('basket','order','边线暗号','边线发球前，队友跑得像在捉迷藏。你先？',['nba-team|喊个名字，先确认他真在看我。','nba-show|举球假动作，把这次发球当一次表演。','nba-safe|等队友跑到能接的位置，手先稳住。','nba-plan|申请暂停：人都找不着，球先别着急。']),
('basket','social','场边解说','场边朋友比场上人还激动，你会？',['nba-plan|请他继续解说，这场正缺一个旁白。','nba-clutch|球传过去：老师下来示范一下。','nba-team|让他负责录像，精彩镜头别漏。','nba-show|指着自己：先给我一个赛后评分。']),
('abstract','action','吃饱喝足','吃饱喝足，朋友问下一站去哪。你会？',['web-meme|去网吧，今晚先把气势打满。','web-watch|回宿舍，先躺五分钟再谈梦想。','web-live|找个机位，宣布饭后发布会开始。','web-plan|先看钱包：胃已六神装，余额还在出门装。']),
('abstract','express','学士帽Plus','开黑群突然开始聊学校，你怎么接？',['web-punchline|报学校之前，先报一下昨晚战绩。','web-edit|把群名改成“学士帽全球采购中心”。','web-meme|一人发一顶帽子，今天全员大学士。','web-care|发张食堂照片：先研究一下今晚吃啥。']),
('abstract','order','饭点补给图','到一个陌生地方，离饭点还有十分钟。你先？',['web-plan|找附近吃饭的位置，路线安排明白再逛。','web-care|问朋友有没有本地推荐，先组一队。','web-watch|记录一下菜单，今天的补给地图更新了。','web-live|对镜头宣布：生活观察栏目，现在开讲。']),
('abstract','explore','价格观察员','朋友说这家店贵得离谱，你会？',['web-watch|把菜单拿过来，先看份量和价格。','web-craft|找三家店对一下，今天把价格研究明白。','web-care|点最想吃的，吃完再给朋友写评语。','web-live|掏出手机：这个话题值得拍一期。'])]
for i,(t,dim,scene,title,opts) in enumerate(samples):
 D['questions'].append(dict(id='v11-sample-'+str(i+5),theme=t,dim=dim,scene=scene,title=title,enabled=True,review={'status':'新增','reason':'用户V11试读样例'},options=[dict(id=j,text=z.split('|',1)[1],behavior=z.split('|',1)[0],tags=[z.split('|',1)[0]],value=j+1) for j,z in enumerate(opts)]))
# Explicit V10 chapter rewrites: same IDs and four stages, less professional language.
rewrites={
'hex-table-0':('刚输了一波，五个人一起看着灰屏。你先？',['plan|先想想下回一起怎么上。','blame|先看装备，不能只怪我。','protect|别急，水先喝一口。','chaos|给灰屏配个音乐，群里先笑一轮。']),
'hex-table-1':('朋友说“再来一次肯定行”，你接什么？',['plan|先说好集合点，别又走散。','protect|这次我前面站，你们跟紧。','blame|行，但先回答刚才怎么没跟。','vision|等一下，看看谁还没复活。']),
'hex-table-2':('对面快到门口了，你先看？',['control|谁冲最快，先让他慢一点。','retreat|自己怎么走能活。','protect|队友站哪儿，别再落一个。','calm|先等半拍，看清了再动。']),
'hex-table-3':('结算页出来了，你给朋友留哪句话？',['plan|下次先数人，再讲梦想。','explain|回放给我，我只讲一分钟。','blame|操作没问题，其他建议另议。','reset|上一把存档，下一把继续。'])}
for q in D['questions']:
 if q['id'] in rewrites:
  title,opts=rewrites[q['id']];q['title']=title;q['options']=[dict(id=j,text=z.split('|',1)[1],behavior=z.split('|',1)[0],tags=[z.split('|',1)[0]],signals=copy.deepcopy(prototypes[z.split('|',1)[0]])) for j,z in enumerate(opts)];q['review']={'status':'重写','reason':'保留团灭四幕ID，改为朋友口语与互相拆台'};next(r for r in reviews if r['id']==q['id']).update(status='重写',after=title,reason=q['review']['reason'])
# Correct new character behaviors to the shared vocabulary, without inventing unused codes.
for p in D['characters']:
 if p['personId']=='us-lecturer':p['behaviorWeights']={'web-plan':5,'web-watch':4,'web-care':3,'web-travel':2}
 if p['personId']=='yaoshuige':p['behaviorWeights']={'web-watch':5,'web-meme':4,'web-live':3,'web-punchline':2}
active=[q for q in D['questions'] if q['enabled']]
D['counts'].update(questions=len(active),lolQuestions=sum(q['theme']=='lol' for q in active),lolChapters=len({q['chapter'] for q in active if q['theme']=='lol'}))
for t in D['themes']:D['counts']['byTheme'][t['id']]['questions']=sum(q['theme']==t['id'] for q in active)
for s in D['lolSeries']:s['count']=sum(q['theme']=='lol' and q['series']==s['id'] for q in active)
(R/'src/data.json').write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n');(R/'docs/v11-question-review.json').write_text(json.dumps(reviews,ensure_ascii=False,indent=2)+'\n')
summary={'oldQuestions':len(reviews),'decisions':dict(collections.Counter(r['status'] for r in reviews)),'activeCounts':D['counts']['byTheme'],'leagueCategories':dict(collections.Counter(q['editorialCategory'] for q in active if q['theme']=='lol')),'newQuestions':len([q for q in active if q['id'] not in before])}
(R/'docs/v11-question-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary,ensure_ascii=False,indent=2))
