"""V10: authored character cards, personal augments and coherent extra scenes."""
from pathlib import Path
import json,collections
R=Path(__file__).resolve().parents[1];D=json.loads((R/'src/data.json').read_text());assert D['version']==9
D['version']=10
D=json.loads(json.dumps(D,ensure_ascii=False).replace('金闪闪队','篮球梦之队').replace('金闪闪首发','梦之队首发'))
# Keep each person in their relevant universe once.
D['characters']=[p for p in D['characters'] if p['id'] not in ('abstract-dasima','abstract-yaoming')]
for p in D['characters']:
 if p['personId'] in ('luobenwei','zhouyi'):
  p.update(theme='lol',id='lol-'+p['personId'],roles=[2,1] if p['personId']=='luobenwei' else [4,2],vector=[70,45,65,60,45,40],behaviorWeights={'chaos':5,'explain':4,'laugh':3,'engage':3},signaturePerks=[])
for t in D['themes']:
 if t['id']=='basket':t.update(name='篮球梦之队',label='篮球梦之队',description='NBA / 中国篮球 / 解说名场面 / 现役与经典')
 if t['id']=='abstract':t['description']='带篮子 / 刀哥 / 峰哥 / 相声 / 科技名人 / 网络整活'
# id, name, identity, roles, six dimensions, behaviors, tags, personal card, effect, punchline
rows=[
('xiaoxiao','笑笑','德云色 · 孙亚龙 · 辅助出身',[4],[65,40,60,70,55,60],{'explain':5,'laugh':5,'engage':3},'德云色,秃头披风,辅助视角,激情复盘,老搭档,先笑后讲','德云色双声道','一人负责把对局讲清楚，另一声道负责让你笑出声。','笑笑刚开讲，西卡的接话已经在排队。'),
('xika','西卡','德云色 · 李浩宇 · 解说搭档',[4,2],[45,45,45,78,60,75],{'explain':5,'calm':4,'plan':3},'德云色,接话高手,双人解说,临场补刀,搭档默契,看图说话','西卡接话器','搭档讲到一半时，自动补上那句最想听的吐槽。','双声道开启，复盘和笑声都不丢。'),
('369','369','骰子选手 · 上路摇号员',[0],[50,50,65,65,70,60],{'spin':5,'mechanics':4,'protect':3},'骰子,三六九,上路抗压,状态切换,队友掩护,反打','骰子保底九','每次摇到三，先保住这一波；下一次的九留给关键团。','骰子可以随机，回防不能随机。'),
('tian','Tian','小天 · 打野节奏位',[1],[40,48,60,78,80,80],{'plan':5,'vision':4,'engage':3},'小天,冠军打野,冷静路线,关键开团,队伍节奏,绕后','天选绕后路线','先看见队友在哪，再从对手没注意的方向进场。','镜头没拍到你的路，结算会记得。'),
('bin','Bin','阿 Bin · 上路敢打位',[0],[65,60,95,48,95,40],{'mechanics':5,'engage':5,'chaos':2},'五杀剑姬,上路自信,敢打敢拼,正面操作,边线,绝不手软','Bin式自信额度','有操作空间就敢接，但先确认四个队友能听见你喊。','自信可以拉满，队友也得跟满。'),
('rookie','Rookie','肉鸡 · 宋义进 · 中路守门员',[2],[35,55,55,85,92,80],{'mechanics':5,'protect':4,'calm':4,'control':3},'肉鸡,S8冠军,中路院长,操作细腻,团队兜底,稳定输出,老IG,关键先生','中路急诊室','队友血压刚升高，中路已经替全队续上一口气。','院长不只看病，也看小地图。'),
('showmaker','ShowMaker','许秀 · 中路表情管理员',[2],[60,48,65,68,88,72],{'explain':5,'mechanics':4,'calm':3},'许秀,圣经,表情管理,中路操作,冠军宣言,名场面','许秀表情管理','表情包素材自动存档，操作窗口继续由你亲手找。','脸上有一部剧，手里有一场比赛。'),
('chovy','Chovy','超威 · 中路补兵收藏家',[2],[25,95,45,58,92,90],{'gold':5,'stack':5,'mechanics':3},'超威,补兵,细节,稳定发育,中路压制,资源规划','一刀都不能少','漏掉的小兵会变成梦里的弹幕，补到的不会替你推家。','先收好兵，再收好胜利。'),
('deft','Deft','戴先生 · 逆风续集作者',[3],[30,60,52,85,85,92],{'calm':5,'plan':4,'mechanics':4},'羊驼,最后一舞,坚持,逆风,下路,老将','最后一舞加更','每当大家准备散场，给自己和队友留一局认真的续集。','最后一舞，先别放谢幕音乐。'),
('beryl','BeryL','原神哥 · 辅助奇思妙想',[4],[25,40,62,95,68,85],{'plan':5,'control':5,'protect':4},'原神哥,辅助脑洞,冠军辅助,战术,奇招,冷静','辅助外置大脑','把五个人的想法接成一条线，奇怪选角也能讲出理由。','游戏外在想别的，游戏里该看图还得看图。'),
('otto','电棍','侯国玉 · 直播接梗中单',[2],[85,45,78,38,65,30],{'chaos':5,'blame':4,'explain':4},'电棍,稳健棍,直播切片,高能语气,临场反应,中路','稳健先缓一缓','每次准备口头加速，先让小地图替你补一句提醒。','声音先到，支援请跟上。'),
('zztai','姿态','刘志豪 · 联盟直播气氛位',[0,2],[65,50,65,68,65,50],{'laugh':5,'chaos':4,'explain':3},'姿态,老IG,直播整活,互动,笑场,边看边讲','直播间笑场险','高能操作前自动提醒录屏；笑场之后还得把团打完。','节目别断，兵线也别断。'),
('kryst4l','水晶哥','杨藩 · 下路复盘观察员',[3],[60,50,65,62,78,58],{'explain':5,'mechanics':4,'retreat':3},'水晶哥,刚子,下路,直播复盘,细节观察,老蛇队','刚子逐帧回放','发现一个细节，立刻把直播间带回那一帧。','先别快进，这里真有东西。'),
('godv','韦神','韦朕 · 跨项目脑洞位',[2],[50,50,85,55,85,55],{'mechanics':5,'chaos':4,'poke':3},'韦神,反向箭,跨界,脑洞操作,中路,大胆尝试','反向也有镜头','大胆尝试会留下镜头，下次出手前记得核对方向。','箭有方向，节目没有尽头。'),
('karsa','Karsa','洪浩轩 · 雷达打野',[1],[30,45,48,85,72,95],{'vision':5,'plan':5,'protect':3},'雷达哥,读图,打野,支援,路线,观察','雷达提前三秒','队友还在喊人，你已经从地图上看见了问题。','雷达不是透视，是多看一眼。'),
('xujingyu','徐静雨','雨说体育 · 篮球评论员',[0,2],[90,68,45,85,60,98],{'nba-show':5,'nba-three':5,'nba-plan':3},'鲸鱼,雨说体育,库里,老1.5,立棍单打,激情解说,弹幕互动,长篇输出','立棍单打复读机','每次有人拿球不传，解说席自动生成一段超长回放。','球可以停一下，鲸鱼的语速停不了。'),
('yangyi','杨毅','篮球评论员 · 赛场故事位',[0,4],[85,55,62,60,92,85],{'nba-plan':5,'nba-show':4,'nba-team':3},'解说,杨毅侃球,故事感,战术点评,临场判断,篮球媒体','解说席故事会','一个回合的停顿里，也能讲完一段球队往事。','比赛还剩两分钟，故事刚到第一章。'),
('zhouqi','周琦','中国篮球 · 内线护框位',[4],[35,42,62,65,62,35],{'nba-rebound':5,'nba-safe':4,'nba-team':3},'大魔王,长臂,护框,边线球,国家队,内线','边线球先对暗号','每次边线发球前，先确认接球的人和你在同一部剧。','梗归梗，这次球要发到队友手里。'),
('sunyue-player','孙悦','篮球运动员 · 后卫防守位',[0,1],[55,60,60,75,72,45],{'nba-safe':5,'nba-team':4,'nba-rebound':3},'篮球孙悦,冠军后卫,长臂防守,盖帽,北京,传球','后卫盖帽通行证','对手以为过了你，下一拍你的长臂还在加班。','这是篮球孙悦，今晚负责防守。'),
('zhangweiping','张卫平','篮球解说 · 合理指导',[0,4],[68,40,65,55,98,70],{'nba-plan':5,'nba-calm':4,'nba-clutch':3},'合理,张指导,这球合理,解说,科比,战术讲解','这球真合理','投进先说合理，没进就认真看看下一个更好的选择。','合理不是口头禅，是先把人站明白。'),
('suqun','苏群','篮球评论员 · 稳住分析位',[0,4],[55,45,70,45,98,45],{'nba-plan':5,'nba-calm':5,'nba-team':3},'篮球记者,战术分析,冷静解说,资深,阵容观察,复盘','暂停板上见','把热闹留给看台，把下一回合写清楚给队友。','别只看谁得分，也看谁把空间拉开。'),
('yujia','于嘉','央视篮球解说 · 关键回合见证人',[0,2],[75,48,72,68,90,78],{'nba-clutch':5,'nba-plan':4,'nba-emotion':3},'央视解说,关键球,声音记忆,比赛节奏,现场,见证','关键球旁白','比分越接近，越能给这一球配上准确的一句话。','球没落网，先把呼吸留住。'),
('wangmeng','王猛','篮球评论员 · 激情解说位',[0,3],[95,60,55,82,65,98],{'nba-show':5,'nba-emotion':5,'nba-dunk':3},'篮球解说,激情,声音上扬,临场接话,高光,热场','解说分贝翻倍','每个干净暴扣都配一段上扬声线，回防时音量自动归位。','人还在空中，声音先到篮板上沿。'),
('yijianlian','易建联','中国篮球 · 沉稳内线',[3,4],[25,35,72,65,90,25],{'nba-train':5,'nba-calm':4,'nba-team':4},'阿联,沉稳,加练,内线,中国篮球,队友信任','沉默加练卡','少说一句漂亮话，多完成一组该练的动作。','镜头看不见的那一组，也算数。'),
('wangzhizhi','王治郅','中国篮球 · 内线技术流',[3,4],[35,62,65,50,95,35],{'nba-plan':5,'nba-calm':4,'nba-safe':3},'大郅,脚步,内线技术,中国篮球,柔和手感,老将','篮下脚步说明书','不靠音量制造空间，靠一个脚步让对手先动。','动作不多，位置刚好。'),
('guoailun','郭艾伦','中国篮球 · 突破欢乐位',[0,1],[82,85,70,92,50,88],{'nba-drive':5,'nba-show':4,'nba-team':3},'大侄子,突破,辽宁,喜剧人,后卫,运球','大侄子变向包','球场上变向，采访时也能把话题晃出半步。','过人有节奏，接梗也一样。'),
('giannis','字母哥','扬尼斯 · 长步冲框位',[3,4],[62,60,65,98,65,65],{'nba-drive':5,'nba-dunk':5,'nba-rebound':3},'字母哥,长步,雄鹿,冲框,力量,笑话','两步到你家篮下','别人还在跑战术，你已经用长步抵达篮筐附近。','步子很长，回防也得长。'),
('kyrie','欧文','凯里 · 运球艺术位',[0,1],[45,95,55,80,60,72],{'nba-drive':5,'nba-show':5,'nba-clutch':3},'德鲁大叔,运球,拉杆,技巧,关键球,街球感','地板舞步许可','把防守重心晃出一个空位，舞步最后记得落在得分上。','花活是过程，进球是落点。'),
('chrispaul','保罗','CP3 · 控场调度员',[0],[70,50,65,50,100,45],{'nba-plan':5,'nba-team':5,'nba-safe':3},'控卫之神,中距离,控场,传球,细节,老将','控卫遥控器','把五个人调到舒服的位置，电池是你的耐心。','暂停键不用按，节奏交给我。'),
('carter','文斯·卡特','UFO · 扣篮收藏家',[1,2],[60,90,55,95,55,85],{'nba-dunk':5,'nba-show':5,'nba-train':3},'UFO,扣篮,飞人,长青,弹跳,全明星','篮筐上方停机坪','高光起飞前先检查落点，掌声抵达后马上回防。','UFO可以起飞，膝盖需要安全着陆。'),
('tmac','麦迪','T-Mac · 末节追分位',[1,2],[50,85,50,90,60,70],{'nba-clutch':5,'nba-three':4,'nba-show':3},'麦迪,35秒13分,干拔,追分,一号球衣,飘逸','三十五秒加时券','时间越少越认真找出手机会，记得把队友算进奇迹。','秒表别关，最后一攻还没签收。'),
('musk','马斯克','科技名人 · 火星脑洞位',[1,2],[85,100,30,98,40,90],{'web-original':5,'web-live':4,'web-meme':3},'火星,火箭,X,产品发布,跨界,脑洞','火星先开群','项目还没离开地球，五人火星群已经取好了名字。','先把今天这一小步落地。'),
('jensen','黄仁勋','科技名人 · 皮衣发布位',[0,2],[80,85,45,82,88,90],{'web-plan':5,'web-live':4,'web-craft':3},'皮衣,显卡,AI,发布会,技术讲解,招牌笑容','皮衣算力加成','穿上招牌皮衣，普通介绍也像在发布一张新显卡。','算力可以堆，内容还得自己做。'),
('trump','川普','公众人物 · 手势热场位',[0,3],[98,65,30,88,40,100],{'web-punchline':5,'web-live':5,'web-dance':3},'标志手势,金发,舞步,公众演说,热场,夸张表达','手势先替我说','话还没说完，手势已经完成了全场同步。','平行舞台梗，现场节奏由你接。'),
('jackma','马云','商业名人 · 金句开场位',[0,2],[95,85,55,75,75,90],{'web-punchline':5,'web-plan':4,'web-live':3},'金句,演讲,商业故事,梦想,开场,互联网','开场先讲个梦想','一句话把普通聚会讲成创业发布会，最后记得回到今天。','梦想先上墙，事情慢慢做。'),
('leijun','雷军','科技名人 · 发布会气氛位',[0,2],[85,85,70,85,88,80],{'web-live':5,'web-craft':4,'web-punchline':4},'Are you OK,小米,发布会,交个朋友,产品,米粉','Are you OK开场音','刚举起麦克风，脑内前奏已经自动播放。','开场有梗，产品介绍也要讲明白。'),
('zhouhongyi','周鸿祎','科技名人 · 红衣开麦位',[0,1],[90,80,35,90,55,95],{'web-live':5,'web-meme':4,'web-original':3},'红衣,科技访谈,跨界,现场提问,互联网,整活','红衣现场追问','大家准备收场时，自动加一轮“我再问一个”。','问题够直接，答案别靠猜。'),
('liguoqing','李国庆','自媒体名人 · 直球表达位',[0,1],[95,65,35,95,35,95],{'web-live':5,'web-punchline':4,'web-meme':3},'直球,直播,商业,现场表达,强烈语气,自媒体','直球不打草稿','脑内草稿刚写一半，话筒已经开始营业。','表达可以直，事实要说准。'),
('luoyonghao','罗永浩','老罗 · 演讲接梗位',[0,2],[85,85,55,78,82,90],{'web-punchline':5,'web-live':4,'web-craft':4},'交个朋友,脱口秀,理想主义,发布会,段子,自嘲','交个队友','原本只想解释一句，最后把四个人讲成了新朋友。','先交朋友，再把片子拍完。'),
('dongyuhui','董宇辉','主播 · 诗词叙事位',[0,2],[78,72,90,55,85,80],{'web-cover':4,'web-care':5,'web-live':4},'诗词,文化直播,叙事,共情,读书,讲故事','购物车里有散文','普通日用品经过你的介绍，先多了一段诗意的背景。','把故事讲好，也把信息讲清楚。'),
('yuminhong','俞敏洪','教育名人 · 长线规划位',[0,2],[72,60,78,62,95,62],{'web-plan':5,'web-care':4,'web-travel':3},'教育,长线,讲述,成长,旅行,经验','人生复盘笔记','走过的弯路先记下来，下一次出发多带一条建议。','经验可以分享，路线仍由自己选。'),
('luoxiang','罗翔','法学老师 · 张三宇宙讲述者',[0,2],[65,90,85,45,98,72],{'web-punchline':5,'web-plan':5,'web-care':3},'张三,法学,举例,幽默,边界,认真解释','张三来举例','每当问题太抽象，张三自动进入例子但不会替你做决定。','笑过以后，边界也讲明白了。'),
('guoyoucai','郭有才','音乐主播 · 诺言开麦位',[0,3],[85,65,78,80,45,90],{'web-cover':5,'web-live':4,'web-meme':3},'诺言,翻唱,菏泽,复古,直播,沙哑声线','诺言循环播放','一段前奏就能把普通路口唱成平行宇宙演唱会。','嗓音负责入戏，节奏还得跟上。'),
('wenhuijun','闻会军','闻神 · 日夜三种状态',[1,3],[80,82,65,90,40,98],{'web-dance':5,'web-meme':4,'web-live':3},'早中晚三态,驾校,舞蹈,伤感文案,闻神,反差','早中晚人格切换','早上认真办事，中午跟着节拍，晚上给月亮写一句话。','一天三种状态，都是同一个你。'),
('fengtimo','冯提莫','音乐主播 · 翻唱开麦位',[0,3],[82,65,78,72,65,88],{'web-cover':5,'web-live':4,'web-care':3},'翻唱,直播,歌声,互动,旋律,舞台','副歌自动返场','唱到熟悉副歌时，四位队友自动切成合唱声部。','先对好调，再把麦递出去。'),
('lijiaqi','李佳琦','主播 · 直播节奏位',[0,4],[98,60,55,90,88,100],{'web-live':5,'web-edit':4,'web-plan':3},'直播,语速,展示,口播,倒计时,节奏','口播倍速档','讲解进入高速档，关键信息仍然得让每个人听清。','三二一，先别急着点。'),
('sunyue-comic','孙越','相声演员 · 德云社捧哏',[3,4],[75,65,90,45,85,78],{'web-punchline':5,'web-care':5,'web-live':3},'相声孙越,捧哏,德云社,岳云鹏搭档,接话,稳住场面','捧哏稳场结界','队友越讲越离谱，你用一句接话把观众留在同一段里。','这位孙越负责捧哏，不负责投三分。'),
('guodegang','郭德纲','相声演员 · 德云社',[0,4],[95,85,60,65,95,95],{'web-punchline':5,'web-live':5,'web-plan':3},'相声,德云社,包袱,返场,现挂,台上节奏','返场再加一段','观众刚以为结束，你已经把下一段包袱接上了。','这不是最后一段，是下段的开场。'),
('dailanzi','带篮子','网络主播 · 带文学观察位',[0,3],[88,82,45,75,48,95],{'web-punchline':5,'web-meme':5,'web-watch':4,'web-live':4},'带文学,东北语气,互联网观察,反向鼓励,弹幕接梗,现场反应,自媒体,一秒换台','带文学弹幕翻译','群里突然沉默时，把一条普通消息翻译成全员都接得住的梗。','嘴上绕一圈，队友还在同一边。'),
]
league=set(x['id'] for x in json.loads((R/'tools/v10-roster.json').read_text()) if x['theme']=='lol')
basket=set(x['id'] for x in json.loads((R/'tools/v10-roster.json').read_text()) if x['theme']=='basket')
for idx,(pid,name,sub,roles,vec,weights,tags,title,effect,punch) in enumerate(rows):
 theme='lol' if pid in league else 'basket' if pid in basket else 'abstract';cid='personal-'+pid
 p=dict(id=theme+'-'+pid,personId=pid,theme=theme,name=name,nickname=name,sub=sub,roles=roles,vector=vec,behaviorWeights=weights,tags=tags.split(','),line=punch,number=str(idx+47),signaturePerks=[cid]);D['characters'].append(p)
 a=dict(id=cid,name=title,effect=effect,punchline=punch,line=punch,bias=[round((v-50)/50,2) for v in vec],vector=vec,behaviorWeights=weights,affinities=[pid],signatureFor=[pid],requires=list(weights),icon=idx%16,fanMade=True,rarity='kPrismatic' if idx%3==0 else 'kGold',category='人物专属',kind='plan' if 'plan' in weights else 'basic' if 'mechanics' in weights else 'chaos',creation='本作原创人物联动梗卡；效果为娱乐设定，不是官方天赋或本人言论。',personOnly=True)
 if theme=='lol':
  icons=['item-3089','item-3157'] if 2 in roles else ['item-3190','SummonerHeal'] if 4 in roles else ['item-3031','item-6676'];a['visual']=dict(layout='row',icons=icons,label=title[:7])
 D['augments'][theme].append(a)
central={
'uzi':('污渍','污渍,小狗,世界级ADC,金色的雨,S8改写,收集者,下路操作,极限走位,输出担当'),
'xiaohu':('销户','销户,春之虎帝,二段笑,春天恒温器,中路运营,大招时机,冠军梗,稳住再笑'),
'jackeylove':('哥哥','哥哥,阿水,接Q,向前闪现,敢打输出,大心脏,滔博陀螺,S8冠军,下路'),
'rookie':('肉鸡','肉鸡,S8冠军,中路院长,老IG,团队兜底,操作细腻,中路急诊室,稳定输出'),
'fengge':('峰哥亡命天涯','亡命天涯,猎奇旅行,街头访谈,说走就走,生活观察,故事采集,社交破冰,镜头外的生活,旅途同行'),
'daoge':('刀哥','好果汁,东北往事,街头整活,气氛担当,接梗快,场面人,有事真上,热闹优先,现场反应'),
'huge':('东北虎哥','东北往事,好果汁,开机音效,热场,街头,兄弟局,节目效果,说干就干'),
'dailanzi':('带篮子','带文学,东北语气,互联网观察,反向鼓励,弹幕接梗,现场反应,自媒体,一秒换台,观察后开麦'),
'dasima':('大司马','金牌讲师,正方形打野,回归基本功,芜湖,理论先行,下饭,复盘,教学素材'),
}
central['theshy']=('TheShy','晒老师,上路独立宇宙,敢抓敢送,操作上限,一打多,边线牵制,S8冠军,名场面,大胆尝试')
for p in D['characters']:
 if p['personId']=='xiaohu':p['sceneBonds']={'double-laugh':['laugh'],'dragon-cheer':['laugh'],'spring':['plan','calm']}
 if p['personId'] in central and central[p['personId']]:p['nickname'],tags=central[p['personId']];p['tags']=tags.split(',');p['spotlight']=True
 if not p.get('tags'):p['tags']=[p.get('nickname',p['name']),*p['sub'].split(' · '),*[D['behaviorLabels'].get(b,b) for b in list(p.get('behaviorWeights',{}))[:3]]][:6]
# Re-home signature relationships for the two League streamers.
for pid in ('luobenwei','zhouyi'):
 p=next(p for p in D['characters'] if p['personId']==pid); p['signaturePerks']=['personal-'+pid]
 a=dict(D['augments']['lol'][-1]);a.update(id='personal-'+pid,name='最后一把续订' if pid=='luobenwei' else '直播间先别笑',effect='说好的最后一把又有了续集，下一局先把队友叫齐。' if pid=='luobenwei' else '笑声负责节目效果，下一波仍然要看队友位置。',punchline='先接梗，再把这局认真打完。',line='先接梗，再把这局认真打完。',vector=p['vector'],bias=[round((v-50)/50,2) for v in p['vector']],behaviorWeights=p['behaviorWeights'],affinities=[pid],signatureFor=[pid],requires=list(p['behaviorWeights']),visual={'layout':'row','icons':['item-3157','SummonerFlash'],'label':'直播续订'})
 D['augments']['lol'].append(a)
# Old abstract cards must only link to residents in this theme.
for theme,cards in D['augments'].items():
 pool={p['personId'] for p in D['characters'] if p['theme']==theme}
 for a in cards:
  a['signatureFor']=[x for x in a.get('signatureFor',[]) if x in pool];a['affinities']=[x for x in a.get('affinities',[]) if x in pool]
  if not a['signatureFor'] and theme=='abstract':
   target='dailanzi' if a['id']=='commentator' else 'geyou';a['signatureFor']=[target];a['affinities']=[target];next(p for p in D['characters'] if p['personId']==target)['signaturePerks'].append(a['id'])
# Additional headliner-only cards preserve older behavior-driven general cards.
for pid,title,effect,punch,beh in [
 ('fengge','路边采访通行证','新地图刚打开，你已经和路边的人聊出了下一段故事。','不是每个人都想出镜，先问一句再开拍。','web-travel'),
 ('fengge','宇宙路费已到账','把目的地改成问号，背包里多放一点观察力。','先把同行的人数清点好，再出发。','web-original'),
 ('daoge','好果汁五人装','一箱五瓶，最后一瓶必须等没到场的队友。','整活可以超前，队友一个别落。','web-meme'),
 ('daoge','街头场面维护员','现场越离谱，越先把五个人叫回同一镜头。','先集合，再给宇宙整个活。','web-live'),
 ('dailanzi','弹幕先替我拐个弯','不急着抢第一句，等到最适合接梗的那一秒。','先看看，再给它换个说法。','web-watch'),
 ('rookie','院长今日值班','队友需要输出，你先把中路这一口气续上。','别急，院长还在线。','mechanics')]:
 p=next(x for x in D['characters'] if x['personId']==pid);theme=p['theme'];cid='extra-'+pid+'-'+str(len(p['signaturePerks']));a=dict(id=cid,name=title,effect=effect,punchline=punch,line=punch,bias=[round((v-50)/50,2) for v in p['vector']],vector=p['vector'],behaviorWeights={beh:5},affinities=[pid],signatureFor=[pid],requires=[beh],icon=14 if pid=='daoge' else 10,fanMade=True,rarity='kPrismatic',category='主角联动',kind='basic' if theme=='lol' else 'chaos',creation='本作原创人物联动，架空娱乐效果。',personOnly=True)
 if theme=='lol':a['visual']={'layout':'row','icons':['item-3089','item-3190'],'label':'中路值班'}
 D['augments'][theme].append(a);p['signaturePerks'].append(cid)
# New non-League scenarios: four per dimension for abstract and two for basketball.
extra={
'abstract':[
('social','带文学开场','五人群里没人说话，带篮子式接梗机会来了，你会？',['先围观，看看大家在聊什么','给熟人发一个能接住的表情','改写群公告，逗四个队友出来','开麦招呼全员：这场面不能冷'],['web-watch','web-meme','web-punchline','web-live']),
('social','刀哥的第五瓶','刀哥带了五瓶好果汁，最后一位队友迟到，你会？',['先把自己的放旁边','问问迟到的人到哪了','替他留着，大家先聊','拉全队录一句：就等你了'],['web-watch','web-care','web-care','web-meme']),
('social','孙越接话','郭德纲说了个夸张包袱，你坐在捧哏的位置上，会？',['先听完整，不抢话','接一句短的，给搭档留口气','顺着他的设定再问一句','一个现挂把五个人一起逗笑'],['web-watch','web-care','web-punchline','web-punchline']),
('social','发布会彩排','雷军式开场前，队友问“Are you OK”，你会？',['点头，在台下帮忙','小声跟一句','拉队友一起练开场','麦克风给我，前奏也给我'],['web-watch','web-care','web-punchline','web-live']),
('explore','峰哥的岔路','旅行途中遇见不在攻略里的小镇，峰哥式好奇心上线，你会？',['先按原路线走','路口看看再决定','问问当地人这里有什么故事','确认安全和时间后，带队进去转转'],['web-plan','web-watch','web-travel','web-travel']),
('explore','火星五人群','马斯克式脑洞：你们的五人群突然改名“火星先遣队”，你会？',['先看今天的计划','给群换一张星空封面','把行李清单写成段子','先拍一段纸箱火箭出征片'],['web-plan','web-edit','web-punchline','web-original']),
('explore','张三的例子','朋友的问题越来越抽象，你想起罗翔式举例，会？',['先把问题说清楚','找个生活里的小例子','让张三登场，把逻辑讲顺','给五位队友各写一个平行身份'],['web-plan','web-care','web-punchline','web-original']),
('explore','皮衣发布会','黄仁勋式发布会借你五分钟，但你只有旧电脑，会？',['介绍它能完成的事','给真实体验拍一段','用纸板做个夸张显卡道具','把普通电脑讲成宇宙飞船驾驶台'],['web-craft','web-live','web-original','web-original']),
('empathy','街头访谈边界','峰哥式街头访谈里，对方说不想出镜，你会？',['立刻停拍，道谢离开','问能否只聊不拍','听完故事，也替他保留匿名','剪掉所有可识别片段，再确认能否用'],['web-care','web-care','web-travel','web-edit']),
('empathy','带梗要有分寸','带篮子式吐槽把朋友说沉默了，你会？',['先停一下','私下问问是不是不舒服','解释是玩梗，认真把话说回来','当场换成自嘲，让朋友轻松下台'],['web-watch','web-care','web-care','web-punchline']),
('empathy','捧哏接住','搭档第一次上台忘词，你负责孙越式捧哏，会？',['留半秒让他想起','用原话帮他接下一句','问个简单问题把话题接住','变成一段默契笑场，再回到正题'],['web-watch','web-care','web-care','web-punchline']),
('empathy','董宇辉式介绍','你要介绍一碗普通面，但朋友今天很累，你会？',['让他先吃，别挡着','只说这碗热乎','讲一小段家乡记忆','把他爱吃的细节讲成温柔旁白'],['web-watch','web-care','web-cover','web-care']),
('action','闻神的中午','上午认真办事的闻会军到了中午开始跳舞，你呢？',['坐着看一遍','先学一个动作','拉队友练一小段','找好场地就开拍，拍完继续办事'],['web-watch','web-dance','web-dance','web-dance']),
('action','刀哥喊集合','刀哥在群里说“来，整个五人合照”，你会？',['发个表情先占位','问清时间地点','带上饮料和手机支架','到场先把四个队友招呼齐'],['web-meme','web-plan','web-care','web-live']),
('action','带篮子录开场','你想到一句带文学式开场，手机已经架好了，你会？',['先看看上次拍的','记下来，等状态好了拍','试一遍，不行再改','直接拍一条自然的，保留笑场'],['web-watch','web-plan','web-punchline','web-live']),
('action','老罗的重录','罗永浩式发布会段子讲岔了，你会？',['暂停，重新整理','剪掉重复的部分','自嘲一句，把逻辑接回来','留住笑场，现场再完整讲一遍'],['web-plan','web-edit','web-punchline','web-live']),
('order','峰哥旅行清单','五人说走就走前，谁来收拾这趟旅程？',['背上包再说','先查路线和返程','把住宿、预算、同行人数写好','路线留弹性，先把安全与联系办法讲清'],['web-travel','web-plan','web-plan','web-care']),
('order','诺言翻唱排练','郭有才式沙哑翻唱要开录，五个人谁也不在一个拍上，你会？',['先自由唱一遍','找出同一段伴奏','分清主唱、和声和拍摄','先对调、对拍，再完整录一次'],['web-cover','web-cover','web-plan','web-craft']),
('order','口播倒计时','李佳琦式三二一口播，重要信息快被语速吃掉了，你会？',['减慢一点先试试','删掉重复形容词','把关键信息列在旁边','分段讲清，确认队友都听懂再加速'],['web-live','web-edit','web-plan','web-care']),
('order','五人返场','郭德纲式返场喊到第三轮，大家明天还要早起，你会？',['再笑一会儿','提醒一下时间','约好最后一段，讲完收工','收好道具，给每个人安排回程'],['web-punchline','web-care','web-plan','web-care']),
('express','带文学评论区','视频发出后，评论问你为何这么抽象，你会？',['点个赞就好','回个表情包','把普通回复绕成一个新梗','置顶一段自嘲，让评论区继续接'],['web-watch','web-meme','web-punchline','web-punchline']),
('express','川普式舞台','聚会音乐响起，有人开始摆标志性的手势舞，你会？',['先在旁边笑','跟两个动作','叫队友一起摆手','站中间带一段，再把位置让给朋友'],['web-watch','web-dance','web-dance','web-live']),
('express','峰哥回程旁白','一趟旅程回来，你准备怎么讲给大家听？',['发一张照片就好','说一个最难忘的细节','把遇见的人剪成小故事','对着镜头讲完这一路的笑场和收获'],['web-watch','web-travel','web-edit','web-live']),
('express','好果汁谢幕','五人整活视频拍完，刀哥把最后一瓶果汁递给你，你会？',['举瓶点头','和拍摄的人碰一下','一句“人齐了，片也齐了”','让五个人一起入镜，留住最后的笑'],['web-care','web-care','web-punchline','web-live'])],
'basket':[
('social','鲸鱼解说席','徐静雨式解说已经讲了两分钟，球还在同一个人手里，你会？',['先看防守站位','提醒该传球了','接一句“立棍单打”缓和气氛','边讲边招呼队友跑出空位'],['nba-safe','nba-team','nba-show','nba-plan']),
('social','合理指导上线','张卫平指导说“这球合理”，队友立刻都想投，你会？',['先观察防守','把球交给空位的人','笑着说一次只投一个','喊出这次配合，让五个人都参与'],['nba-safe','nba-team','nba-show','nba-plan']),
('explore','字母长步','字母哥式大步冲框，前面却已经站了两个人，你会？',['先停下护好球','传给旁边空位','换个角度再试突破','敢打也要找空隙，别往人堆里冲'],['nba-safe','nba-team','nba-drive','nba-drive']),
('explore','欧文运球教学','欧文式花活还没练会，朋友就要录高光，你会？',['先练最稳的动作','把成功那一次记录下来','尝试一个新变向','做一段花活与失误都保留的搞笑集锦'],['nba-train','nba-plan','nba-drive','nba-show']),
('empathy','孙悦封盖之后','篮球孙悦式追帽完成，传球的队友没人看见，你会？',['先回防','回头跟他击掌','主动说这球靠他的提醒','庆祝时把他拉到镜头中间'],['nba-safe','nba-team','nba-care','nba-team']),
('empathy','周琦边线球','队友边线球失误，场边开始玩老梗，你会？',['先回防，别继续丢分','告诉他下一次先对眼神','叫个简单接应配合帮他找回感觉','挡掉嘲讽，五个人再认真发一次'],['nba-safe','nba-team','nba-plan','nba-care']),
('action','大侄子突破','郭艾伦式第一步晃出了位置，协防又补来，你会？',['稳住别丢球','传给空位队友','找节奏继续突破','假动作加变向，但保留传球路线'],['nba-safe','nba-team','nba-drive','nba-drive']),
('action','麦迪时间','时间只剩35秒，比分落后，你会？',['先完成眼前一防','布置一个简单配合','空位来了果断三分','每个回合认真抢，奇迹也得一球球投'],['nba-safe','nba-plan','nba-three','nba-clutch']),
('order','保罗遥控器','五个人都想当主攻，保罗式控场的你会？',['先护住球','确认谁手感最好','安排传切和掩护','让五人都知道这一回合的第一选择'],['nba-safe','nba-team','nba-plan','nba-plan']),
('order','解说席三人组','杨毅讲故事、苏群画战术、王猛等暴扣，你最先接哪一个？',['先听当前回合','问清楚战术站位','补一个比赛背景','卡准高光再把情绪喊出来'],['nba-calm','nba-plan','nba-plan','nba-show']),
('express','UFO落地','卡特式暴扣点燃球场，你会？',['落地先站稳','和队友击掌回防','给一个经典庆祝','喊一句再追上下一回合'],['nba-safe','nba-team','nba-show','nba-dunk']),
('express','于嘉末节旁白','最后一球进了，轮到你给这场球配一句话，你会？',['好球，先握手','这球大家配合得好','稳住呼吸，说完最后一攻','跟王猛一起把声音抬到篮筐那么高'],['nba-calm','nba-team','nba-clutch','nba-show'])]}
for theme,questions in extra.items():
 for n,(dim,scene,title,texts,bs) in enumerate(questions):D['questions'].append(dict(id=f'v10-{theme}-{n}',theme=theme,dim=dim,scene=scene,title=title,options=[dict(id=i,text=t,value=i+1,behavior=b,tags=[b]) for i,(t,b) in enumerate(zip(texts,bs))]))
# Three additional connected League chapters, everyday wording and useful tips.
chapters=[('deyunse','德云色双声道',[
('双人解说','笑笑和西卡同时开麦，队友说听不清谁在指挥，你会？',[('先停一秒，让一个人说','calm'),('把下一步说成一句短话','plan'),('接个梗再问队友去哪','laugh'),('两个声道一起上，先把气氛拉满','chaos')]),
('场上接话','你刚说完下一步，队友已经笑场，怎么把话接回来？',[('确认人齐再走','protect'),('把笑点留录屏，先报位置','vision'),('自己也笑一段，再认真打','laugh'),('这波我来操作，大家看我','mechanics')]),
('被对面抓到','复活倒计时里，双人解说突然变成全队复盘，你先做什么？',[('只说一个能改的点','explain'),('把下一波路线标好','plan'),('先问刚才谁没跟上','blame'),('回放先别关，这里太好笑了','laugh')]),
('双声道收尾','最后一波打完，搭档把麦递给你，你会？',[('赢了再笑，先确认基地倒了','calm'),('讲讲这局五人怎么配合','explain'),('两个人一起模仿开场的笑声','laugh'),('让全队一人接一句，录成片尾','chaos')])]),
('rookie-clinic','中路今日值班',[
('中路急诊室','Rookie式中路值班：上下两路同时喊难打，你先怎么办？',[('先清眼前小兵，再看哪边能帮','plan'),('给危险的那路报一下敌人位置','vision'),('找一个能打的机会给队友减压','mechanics'),('把保护技能留给被追的人','protect')]),
('队友终于到了','队友来中路了，你刚好打出一次机会，接下来？',[('等队友控制接上再打','control'),('先报一句，我准备往前','engage'),('有空隙就把伤害打够','mechanics'),('血量不多的人先回去','protect')]),
('这波没打赢','队友说“院长救我”，但你也在复活，你会？',[('先稳住，下一波一起到','calm'),('把刚才哪个技能没接上讲清楚','explain'),('把进场时间再对一遍','plan'),('练的就是这种局，下一波继续操作','mechanics')]),
('值班结束','五人一起推到最后，你怎么结束这班？',[('先拆完，庆祝不抢跑','calm'),('最后一个兵也得吃明白','gold'),('把队友留在身边一起点基地','protect'),('有机会就打完最后一段操作','mechanics')])]),
('bro-flash','哥哥向前一步',[
('下路镜头','哥哥式名场面：你有闪现，队友刚说“别急”，你会？',[('先看对面控制有没有交','plan'),('找安全位置持续输出','poke'),('确认能赢这一下，再向前闪','flash'),('五个人都在，开这波','engage')]),
('镜头突然变灰','向前之后屏幕灰了，弹幕已经打出“接Q”，你会？',[('复活先把走位做好','mechanics'),('先问下一波在哪里集合','plan'),('把这一幕笑着收进素材','laugh'),('刚才是谁说能跟的','blame')]),
('陀螺要转了','队伍连续被打退，朋友说滔博陀螺启动，你怎么接？',[('先绕开最挤的位置','spin'),('等对面的关键技能交完','control'),('让输出的人先活下来','protect'),('下一次我要找机会反打','engage')]),
('最后一个机会','最终决胜局剩一个空位，你会？',[('站稳输出，别为镜头多走一步','mechanics'),('确认队友准备好了再打','plan'),('对面技能交了，这次向前','flash'),('先把金色的雨表情备好，基地倒了再发','calm')])])]
base={b:next(o['signals'] for q in D['questions'] if q['theme']=='lol' for o in q['options'] if o['behavior']==b) for b in ['calm','plan','laugh','chaos','protect','vision','mechanics','explain','blame','control','engage','gold','poke','flash','spin']}
for chapter,name,scenes in chapters:
 for stage,(scene,title,opts) in enumerate(scenes):D['questions'].append(dict(id=f'rift-{chapter}-{stage}',theme='lol',series='rift',chapter=chapter,chapterName=name,stage=stage,scene=scene,title=title,importance=1,tip='先看小地图、队友位置和对面关键技能，再决定向前；复活期间可以简单沟通下一步。',options=[dict(id=i,text=t,behavior=b,tags=[b],signals=base[b]) for i,(t,b) in enumerate(opts)]))
D['counts']=dict(questions=len(D['questions']),lolQuestions=sum(q['theme']=='lol' for q in D['questions']),lolChapters=len({q.get('series','')+':'+q.get('chapter','') for q in D['questions'] if q['theme']=='lol'}),people=len({p['personId'] for p in D['characters']}),parodyCards=sum(len(a) for a in D['augments'].values()),lolParodyCards=len(D['augments']['lol']),byTheme={t['id']:dict(questions=sum(q['theme']==t['id'] for q in D['questions']),people=sum(p['theme']==t['id'] for p in D['characters']),cards=len(D['augments'][t['id']])) for t in D['themes']})
for s in D['lolSeries']:s['count']=sum(q['theme']=='lol' and q['series']==s['id'] for q in D['questions'])
D['editorial']['checkedAt']='2026-10-23';D['editorial']['note']='经典公开名场面与本作原创情境的固定快照；不声称实时热榜排名。人物标签描述本作梗角色，不是本人性格结论。'
(R/'src/data.json').write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n');(R/'assets/parody-cards.json').write_text(json.dumps(D['augments'],ensure_ascii=False,indent=2)+'\n');print(D['counts'])
