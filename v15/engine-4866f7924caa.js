(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.ShenrenLegacyEngine=factory();})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const dimIds=['social','explore','empathy','action','order','express'];
const lolDimIds=['tilt','greed','risk','team','craft','plan'];
const dimsFor=theme=>theme==='lol'?lolDimIds:dimIds;
function random(){if(typeof crypto!=='undefined'&&crypto.getRandomValues){const a=new Uint32Array(1);crypto.getRandomValues(a);return a[0]/4294967296;}return Math.random();}
function shuffle(list,rng=random){const a=list.slice();for(let i=a.length-1;i>0;i--){const j=Math.floor(rng()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
// One layout feeds both HTML and exported Canvas: the real icons and copy counts match.
function artLayout(a){
 const icons=a.visual?a.visual.icons:[],n=icons.length,l=a.visual?a.visual.layout:null;
 const points=n===1?[[.19,.19,.62,0]]:l==='grid'?icons.map((_,i)=>[.02+(i%3)*.33,.17+Math.floor(i/3)*.34,.30,0]):l==='square'?[[.07,.07,.36,-8],[.57,.07,.36,8],[.07,.57,.36,8],[.57,.57,.36,-8]]:l==='ring'?icons.map((_,i)=>{const t=-Math.PI/2+i*Math.PI*2/n;return [.33+Math.cos(t)*.28,.33+Math.sin(t)*.28,.34,i*15-15];}):l==='row'?icons.map((_,i)=>[.03+i*(.94-.40)/Math.max(1,n-1),.30+(i%2)*.1,.40,(i-(n-1)/2)*10]):n===2?[[.04,.28,.47,-15],[.49,.19,.47,15]]:n===3?[[.03,.35,.47,-17],[.51,.35,.47,17],[.27,.07,.47,0]]:n===4?[[.05,.14,.4,-15],[.55,.14,.4,15],[.05,.55,.4,-8],[.55,.55,.4,8]]:[[.03,.14,.37,-17],[.23,.04,.37,-8],[.43,.04,.37,8],[.62,.14,.37,17],[.29,.53,.43,0]];
 return icons.map((icon,i)=>({icon,x:points[i][0],y:points[i][1],size:points[i][2],rotation:points[i][3]}));
}
function draw(data,theme,count,previousFirst=null,rng=random,series='all'){
 if(!data.themes.some(t=>t.id===theme)||!data.modes.includes(count))throw Error('不支持的主题或题量');
 if(theme==='lol'&&!['all','hex','rift'].includes(series))throw Error('不支持的联盟系列');
 let chosen=[];
 if(theme==='lol'){
  const bank=data.questions.filter(q=>q.theme===theme&&(series==='all'||q.series===series));
  const chapters=shuffle([...new Set(bank.map(q=>q.series+':'+q.chapter))],rng);
  if(chapters.length<count/4)throw Error('章节题库不足');
  if(bank.some(q=>q.id===previousFirst&&chapters[0]===q.series+':'+q.chapter))[chapters[0],chapters[1]]=[chapters[1],chapters[0]];
  chosen=[].concat(...chapters.slice(0,count/4).map(c=>bank.filter(q=>q.series+':'+q.chapter===c).sort((a,b)=>a.stage-b.stage)));
 }else{
  const extra=new Set(shuffle(dimIds,rng).slice(0,count%6));
  dimIds.forEach(dim=>{const bank=data.questions.filter(q=>q.theme===theme&&q.dim===dim),n=Math.floor(count/6)+(extra.has(dim)?1:0);if(bank.length<n)throw Error('题库不足');chosen.push(...shuffle(bank,rng).slice(0,n));});
  chosen=shuffle(chosen,rng);if(chosen[0].id===previousFirst)[chosen[0],chosen[1]]=[chosen[1],chosen[0]];
 }
 return {version:data.version,theme,series:theme==='lol'?series:'all',count,deck:chosen.map(q=>({id:q.id,order:shuffle(q.options.map(o=>o.id),rng)})),answers:Array(count).fill(null),index:0,phase:'quiz',date:new Date().toISOString()};
}
function valid(s,data,complete=false){
 if(!s||s.version!==data.version||!data.themes.some(t=>t.id===s.theme)||!data.modes.includes(s.count)||!Array.isArray(s.deck)||s.deck.length!==s.count||!Array.isArray(s.answers)||s.answers.length!==s.count||!Number.isInteger(s.index)||s.index<0||s.index>=s.count)return false;
 if(s.theme==='lol'&&!['hex','rift','all'].includes(s.series))return false;
 if(new Set(s.deck.map(d=>d&&d.id)).size!==s.count)return false;
 const questions=s.deck.map(d=>data.questions.find(q=>q.id===(d&&d.id)&&q.theme===s.theme&&(s.theme!=='lol'||s.series==='all'||q.series===s.series)));
 if(questions.some(q=>!q))return false;
 if(s.theme==='lol'){
  for(let i=0;i<questions.length;i+=4){const group=questions.slice(i,i+4);if(group.some((q,j)=>q.chapter!==group[0].chapter||q.series!==group[0].series||q.stage!==j))return false;}
 }else if(!dimIds.every(dim=>questions.some(q=>q.dim===dim)))return false;
 return s.deck.every((d,i)=>Array.isArray(d.order)&&d.order.length===4&&new Set(d.order).size===4&&d.order.every(v=>questions[i].options.some(o=>o.id===v))&&((!complete&&s.answers[i]===null)||questions[i].options.some(o=>o.id===s.answers[i])));
}
// Commit against the question that was actually displayed; stale taps cannot answer another question.
function recordAnswer(s,data,questionId,optionId){
 if(!valid(s,data)||s.phase!=='quiz'||s.deck[s.index].id!==questionId)throw Error('这道题已经切换，请重新选择');
 const q=data.questions.find(q=>q.id===questionId);
 if(!q.options.some(o=>o.id===optionId))throw Error('这个选项不存在');
 const next=Object.assign({},s,{answers:s.answers.slice()});next.answers[s.index]=optionId;
 const complete=s.index===s.count-1;
 if(complete)next.phase='complete';else next.index=s.index+1;
 return {session:next,complete};
}
function selections(s,data){return s.deck.map((d,i)=>{const q=data.questions.find(q=>q.id===d.id);return {q,o:q.options.find(o=>o.id===s.answers[i])};});}
function score(s,data){
 if(!valid(s,data,true))throw Error('请完成本轮全部题目');const rows=selections(s,data);
 return dimsFor(s.theme).map(dim=>{if(s.theme==='lol'){const total=rows.reduce((sum,{o})=>sum+o.signals[dim],0),neutral=rows.reduce((sum,{q})=>sum+q.options.reduce((n,o)=>n+o.signals[dim],0)/4,0),lo=rows.reduce((sum,{q})=>sum+Math.min(...q.options.map(o=>o.signals[dim])),0),hi=rows.reduce((sum,{q})=>sum+Math.max(...q.options.map(o=>o.signals[dim])),0),delta=total-neutral;return Math.max(0,Math.min(100,Math.round(50+50*delta/Math.max(1,delta>=0?hi-neutral:neutral-lo))));}const values=rows.filter(({q})=>q.dim===dim).map(({o})=>o.value);return Math.round((values.reduce((a,b)=>a+b,0)/values.length-1)/3*100);});
}
function similarity(a,b){return Math.round(100*(1-a.reduce((s,v,i)=>s+Math.abs(v-b[i]),0)/600));}
function responseWeight(q){return q.importance||1;}
function behaviorFit(rows,weights={}){const total=rows.reduce((sum,{q})=>sum+responseWeight(q),0);return total?100*rows.reduce((sum,{q,o})=>sum+(weights[o.behavior]||0)*responseWeight(q),0)/(5*total):0;}
function cardEvidence(rows,card){return rows.map(({q,o},index)=>({id:q.id,scene:q.scene,choice:o.text,behavior:o.behavior,strength:((card.behaviorWeights&&card.behaviorWeights[o.behavior])||0)*responseWeight(q),index})).filter(e=>e.strength>0).sort((a,b)=>b.strength-a.strength||a.index-b.index);}
function rankPeople(s,data,vector){const pool=data.characters.filter(p=>p.theme===s.theme),rows=selections(s,data);return pool.map(p=>Object.assign({},p,{match:Math.round(.65*similarity(vector,p.vector)+.35*behaviorFit(rows,p.behaviorWeights)+20*rows.filter(({q,o})=>p.sceneBonds&&p.sceneBonds[q.chapter]&&p.sceneBonds[q.chapter].includes(o.behavior)).length/rows.length)})).sort((a,b)=>b.match-a.match||a.id.localeCompare(b.id));}
function recommend(s,data,vector=score(s,data),identity=null){
 const rows=selections(s,data);if(!identity)identity=rankPeople(s,data,vector)[0];
 return data.augments[s.theme].filter(a=>!a.personOnly||(a.signatureFor||[]).includes(identity.personId)).filter(a=>!(a.requires||[]).length||(a.requires||[]).some(b=>rows.some(({o})=>o.behavior===b))).map(a=>{
  const v=a.vector||a.bias.map(n=>Math.max(0,Math.min(100,50+n*40))),evidence=cardEvidence(rows,a);
  const behavior=behaviorFit(rows,a.behaviorWeights),bonus=(a.affinities||[]).includes(identity.personId)?5:0;
  const match=Math.round(.42*similarity(vector,v)+.53*behavior+bonus);
  return Object.assign({},a,{match,evidence:evidence.slice(0,2),hitCount:evidence.length,personLink:bonus>0});
 }).filter(a=>a.hitCount>0).sort((a,b)=>b.match-a.match||b.hitCount-a.hitCount||a.id.localeCompare(b.id));
}
function questionAt(s,data,index=s.index){const q=data.questions.find(q=>q.id===(s.deck[index]&&s.deck[index].id));if(!q)return null;const prior=index>0?s.answers[index-1]:null;return Object.assign({},q,{title:q.branches&&prior!==null?(q.branches[String(prior)]||q.title):q.title});}
const reactions={afk:'你的镜头切到观战席，接下来由你决定这局怎么演。',int:'上一单已经送达，导播开始等你的下一次发车。',collector:'第五把收集者已在计划里，下一波还得看阵容。',protect:'你把队友留在镜头里，接下来看看这份售后怎么做。',heal:'桥头医务室已经开门，下一波挂号队伍也到了。',explain:'复活倒计时在走，你的讲解刚刚开始。',blame:'锅还在空中，下一幕先看看谁来接。',chaos:'节目效果已到账，故事还有下一幕。',plan:'计划先写在这里，接下来看看现场听不听安排。',engage:'车已经开了，接下来看乘客有没有跟上。',reset:'上一段剧本已翻篇，新的一幕还等你接梗。',laugh:'笑容先记一段，接下来手也要跟上。',calm:'你把庆祝留到了后面，先把眼前的对局打完。',spin:'抗压拉扯已经开始，下一步看看有没有反打空间。',stasis:'金身时机已经记下，结束之后还得接着操作。',flash:'闪现交了，接下来先把走位和退路找回来。',vision:'你先要信息，再决定下一步怎么打。'};
function context(s,data,index=s.index){const q=questionAt(s,data,index);if(q.theme!=='lol'||q.stage===0)return null;const previous=data.questions.find(p=>p.id===s.deck[index-1].id),o=previous.options.find(o=>o.id===s.answers[index-1]);return o?{chapter:q.chapterName,stage:q.stage,previousChoice:o.text,previousScene:previous.scene,reaction:reactions[o.behavior]||'上一个反应已经记下，同一场对局继续往下演。'}:null;}
const teamScripts={
 range:['上路卡位：把对手留在输出射程里。','打野盯人：绕后的人先报位置。','中路消耗：命中一轮再决定进退。','下路拉扯：边走边打，别只顾着后退。','辅助接应：控制留给贴脸的那个人。'],
 blame:['上路复盘：先说线权，再看有没有支援。','打野报点：刷野路线和到场时间说清楚。','中路看图：先确认信息，再问队友在哪。','下路回放：谁先吃控，拉进度条再说。','辅助提醒：复活时间和技能比问号更有用。'],
 economy:['上路承压：先站住，再给四个输出腾空间。','野区控图：该吃资源时吃，该到场时到。','中路游走：推完线再走，别两头都漏。','下路收尾：残血可以收，前排别硬穿。','辅助售后：全队唯一还看血条的人。'],
 chaos:['上路独演：先把边线变成个人舞台。','打野发车：路线直达下一段集锦。','中路配乐：这一波自带主角 BGM。','下路压轴：高光和灰屏只隔一帧。','辅助验票：上车前请签字。'],
 engage:['上路顶门：把第一波技能收下。','打野发车：开之前先数一遍乘客。','中路接戏：控制留给关键那个人。','下路输出：司机说到站再下车。','辅助导航：负责把人齐这件事讲明白。'],
 protect:['上路挡风：四个输出的移动掩体。','打野保安：巡逻到后排就上班。','中路调度：让技能替队友争取时间。','下路患者：请在医务室射程内营业。','辅助主治：这家没你真得关门。'],
 basic:['上路动作指导：细节交给手，不交给嘴。','打野解说：先把路线走成一个几何题。','中路编导：等到技能窗口再拍。','下路主演：金色的雨要自己走位接。','辅助控场：让高光背后有人接应。'],
 plan:['上路带线：看完小地图再过河。','打野路线：第四条边还没讲完。','中路恒温：今天几度由这里决定。','下路输出：等关键装备成型再接硬仗。','辅助复盘：把五个人留在同一张图上。'],
 retreat:['上路安全员：撤退也要留出通道。','打野巡场：先看地图再问队友呢。','中路观察：等对手把按钮按完。','下路远程：在安全感边缘输出。','辅助接人：回来就有口热奶。'],
 reset:['上路续集：这一条线还没演完。','打野刷新：新路线下一局见。','中路转场：重开也要记得带队友。','下路重拍：镜头先别删。','辅助留人：说好最后一把，又齐了。']};
function linkTeam(team,augment,theme){const lines=theme==='basket'?['控卫串联：先让队友都能接到球。','分卫接火：有机会就投，没机会先传。','侧翼跑动：把这一段名场面接起来。','篮下协作：卡好位置，给队友留空间。','中锋护框：篮板和回防都得有人管。']:theme==='abstract'?['发言人开场：把五个人的故事讲清楚。','行动派开拍：先完成最容易的一小段。','军师编排：好点子也要有人把它做出来。','气氛组接梗：前奏一响，全队进入画面。','场控收尾：照顾边界，也别落下任何队友。']:(teamScripts[augment.kind]||teamScripts.chaos);return team.map(p=>Object.assign({},p,{teamLine:lines[p.slot]}));}
function buildTeam(vector,characters,identity,augment){
 let best=null;
 for(const myRole of identity.roles){
  let states=Array(32).fill(null);states[1<<myRole]={value:0,slots:Array(5).fill(null)};states[1<<myRole].slots[myRole]=identity;
  for(const p of characters.filter(p=>p.id!==identity.id)){
   const next=states.slice();for(let mask=0;mask<32;mask++){const prior=states[mask];if(!prior)continue;
    for(let role=0;role<5;role++){if(mask&(1<<role)||!p.roles.includes(role))continue;const match=similarity(vector,p.vector),affinity=p.roles[0]===role?12:p.roles.includes(role)?7:-18;const flavor=augment?augment.bias.reduce((s,w,i)=>s+w*(p.vector[i]-50)/10,0):0;const value=prior.value+match+affinity+flavor;
     const to=mask|(1<<role);if(!next[to]||value>next[to].value){const slots=prior.slots.slice();slots[role]=p;next[to]={value,slots};}}
   }states=next;
  }
  const full=states[31];if(full&&(!best||full.value>best.value))best=full;
 }
 if(!best)throw Error('角色池不足以组成五人队');return best.slots.map((p,i)=>Object.assign({},p,{slot:i,isYou:p.id===identity.id,match:p.match===undefined?similarity(vector,p.vector):p.match,naturalRole:p.roles.includes(i)}));
}

function squadError(ids,theme,data,free=false,partial=false){
 if(!Array.isArray(ids)||ids.length!==5)return '请选择五个位置';
 const chosen=ids.filter(Boolean);if(!partial&&chosen.length!==5)return '还没选满五个人';
 const people=[];for(let i=0;i<5;i++){if(!ids[i])continue;const p=data.characters.find(p=>p.id===ids[i]&&p.theme===theme);if(!p)return '只能选择当前主题的人物';if(people.includes(p.personId))return '同一个人不能重复出场';people.push(p.personId);if(!free&&!p.roles.includes(i))return '这个位置不合适，可开启自由整活';}return '';
}
function fillSquad(ids,theme,data,vector,free=false){
 const err=squadError(ids,theme,data,free,true);if(err)throw Error(err);
 const fixed=ids.map(id=>id?data.characters.find(p=>p.id===id):null),used=fixed.filter(Boolean).map(p=>p.personId);let mask=0;fixed.forEach((p,i)=>{if(p)mask|=1<<i;});
 let states=Array(32).fill(null);states[mask]={value:0,slots:fixed.slice()};
 for(const p of data.characters.filter(p=>p.theme===theme&&!used.includes(p.personId))){const next=states.slice();for(let m=0;m<32;m++){const prev=states[m];if(!prev)continue;for(let i=0;i<5;i++){if((m&(1<<i))||(!free&&!p.roles.includes(i)))continue;const val=prev.value+similarity(vector,p.vector)+(p.roles[0]===i?12:p.roles.includes(i)?7:-15),to=m|(1<<i);if(!next[to]||val>next[to].value){const slots=prev.slots.slice();slots[i]=p;next[to]={value:val,slots};}}}states=next;}
 if(!states[31])throw Error('当前选择无法补齐五个位置；请换人或开启自由整活');return states[31].slots.map(p=>p.id);
}
function customSquad(ids,theme,data,vector,identity,augment,free=false){
 const err=squadError(ids,theme,data,free);if(err)throw Error(err);
 return linkTeam(ids.map((id,slot)=>{const p=data.characters.find(p=>p.id===id);return Object.assign({},p,{slot,isYou:p.personId===identity.personId,match:similarity(vector,p.vector),naturalRole:p.roles.includes(slot),custom:true});}),augment,theme).map(p=>Object.assign({},p,{teamLine:(p.naturalRole?'':'跨位整活 / ')+(p.tags||[]).slice(0,2).join(' · ')+'。'+p.teamLine}));
}

const stories={
 jackeylove:['哥哥，这回向前一步走到了金色的雨。','在这条架空 S8 时间线，你化身阿水。最后一局的闪现没有换来灰屏，而是等到了四名队友同时到场。你找到侧面的空隙，输出、拉开、再次上前，把那个熟悉的“敢打”变成了所有人等着看的结局。','奖杯前大家又喊起哥哥。你笑着把四个人拉进合照：这次镜头里，一个队友都没少。'],
 rookie:['院长，这次把整个宇宙都救回来了。','你化身 Rookie，站进一场架空 S8 决赛。队友在语音里喊你，你把中路守成了全队的落脚点。最后一波控制接上，四个熟悉的身影一起向前，你的输出把最后一座基地打成了金色的雨。','你抱着奖杯，眼泪先于采访回答。观众喊着肉鸡，队友说今天院长终于可以下班了。'],
 dailanzi:['评论区还没开，你的平行宇宙已经有了开场白。','你化身带篮子，带着四位风格完全不同的队友开了一场平行宇宙直播。刀哥带了好果汁，峰哥讲起路上的故事，台下刚有点冷场，你用一句带文学把所有人拉回同一段里。','散场后，最热的一条弹幕不是谁赢了，而是“这五个人怎么凑一起的”。你把它置顶：下一期，还得人齐。'],
 xiaoxiao:['双声道里，终于播到了冠军谢幕。','你化身笑笑，和西卡坐在平行决赛的解说席。开场的笑声被你们接成一句句简明的提醒。最后一波五个人齐了，基地倒下，你们一边笑一边把每个队友的名字喊出来。','这个宇宙的冠军回放有两个声道：一个记住操作，一个记住大家为什么一起笑。'],
 xika:['搭档那句话，被你接成了整个宇宙的片尾。','你化身西卡，和笑笑主持一场平行宇宙冠军之夜。有人讲快了，你补一句；有人漏了细节，你再讲清一遍。最后一波打完，直播间的笑声和现场的金色纸片一起落下。','冠军采访结束，你还在替这局接尾句：先别关，五个人的合照还没拍。'],
 uzi:['平行 S8，轮到你改写结局。','在这条架空时间线，你变成了污渍。决胜局，对面的飞科锁下加里奥，镜头里所有人都以为这又是熟悉的剧本。你却在最后一波侧身躲开控制，和四位队友一起战胜 Faker，把输出打到了结算页面。','金色的雨落下。你抱着奖杯泪流满面，全场高喊“世界第一 ADC”。主持人还在问“历史第一 ADC”，你已经把问题推进到“英雄联盟的 GOAT”。收集者不是决定，敢不敢接下这场比赛才是。'],
 xiaohu:['这个宇宙，没有不属于你的季节。','你变成了销户，赛场的日历被你改成了“春一月”到“春十二月”。总决赛打到最后一局，你把边线、团战与笑容一起拉满。','奖杯旁边多了一块恒温器：全宇宙的春天，今天由中路负责。'],
 dasima:['从讲解席，走到冠军颁奖台。','你变成了大司马。架空决赛里，所有人还在质疑你的路线，你已经画出了第三条“正方形打野”轨迹。最后一波不是嘴上有说法，是地图真的照着你的说法走。','奖杯被你端成一件教学道具。冠军公开课第一句话：先别急，这波我慢慢讲。'],
 theshy:['上路这条线，通向另一个结局。','你化身 TheShy，在架空决赛把一条边线打成了自己的独立宇宙。对手终于凑齐五个人来围你，你的队友刚好把另一边的主场拆完。','赛后大家讨论阵型，你在战术板上画了一条线：这里，也是一种答案。'],
 faker:['这一次，时间站在你这一边。','你化身飞科。平行决赛进入最安静的十秒，你等到所有技能交错的缝隙，再把那个属于自己的窗口按了下去。','第五次、第六次都不再是问题。这个宇宙的传奇，是把每一个小回合认真打完。'],
 lebron:['勒邦詹氏，膝盖先于战术板反应。','平行总决赛最后一攻，你变成了勒邦詹氏。漏判出现，全场进入表情加载页，你用一个跪地默剧把节目效果拉满。随后你站起来，追帽、推进、压哨出手一气呵成。','球进灯亮。这个宇宙的“虎扑式”搞笑评分写着：10 分，建议把膝盖也算进首发。你拿走的是这条时间线的 GOAT 剧本。'],
 curry:['停车场，正式进入你的射程表。','你变成了库里。平行总决赛的三分线被搬到停车场，大家还在找停车位，你已经借掩护转身出手。篮球在空中待得像一趟跨省快递。','球落网，晚安手势安排上。这个宇宙规定：只要你站得稳，想象力就有出手权。'],
 kobe:['凌晨的第一盏灯，由你点亮。','你化身科比。平行总决赛最后一节，你把练过无数遍的动作放进那个最需要答案的回合。全场的声音很大，你听见的只有脚步和球落网。','镜头切到空荡的训练馆：这里，早就为这个结局留过灯。'],
 jokic:['马儿没来，但传球已经到了。','你化身约老师。平行总决赛开打前，大家发现战术板背面是一张木马旋转图。第三节开始，对手才意识到每个人都被你转到了正确的位置。','你拿着奖杯问能不能早点回去。这个宇宙的中锋，把轻描淡写打成了史诗。'],
 fengge:['你去过的地方，地图还没来得及加载。','你变成了峰哥，揣着一张平行宇宙通行证出发。路边一间小卖部卖的是“如果当年”，你没急着买，而是拉老板聊完了另一个人生。','最后你带回来五个人和一大串故事。宇宙没被你讲明白，但你的这一集已经够好看。'],
 huge:['来，整个宇宙先别关。','你变成了虎哥。平行东北的路灯突然集体熄灭，你一抬手，现场五个人自带开机音效。围观群众还没弄清第一幕，第二幕已经顺着街口开过去了。','城市把“节目效果维护员”奖章发给你。你问：奖章能不能再配一瓶好果汁？'],
 daoge:['好果汁，这回送到了银河边上。','你变成了刀哥。一封星际补给单把你带到银河边，你发现全宇宙都在排队等下一段名场面。你把好果汁放上桌，先把五个队友招呼齐。','这场没有既定台词，只有现场反应。你的平行身份，是让离谱故事继续发生的人。'],
 geyou:['你没拯救宇宙，你让它坐下休息了。','你变成了葛优。平行世界不停催进度，所有人都在找下一场大事。你先在沙发上挪出四个位置，把队友一个个招呼坐下。','宇宙最后没爆炸。它只是承认：有些重要的事，要坐稳了才能想明白。']
};
function narrative(identity,theme,profile,series='all',augment=null){
 if(theme==='lol'&&(augment&&augment.id)==='double-laugh')return [`${identity.nickname||identity.name}，把第二段笑留给金色的雨。`,'在这条架空时间线，你在开局前忍住了第一段笑。领先以后，队友已经准备庆祝，你却把手重新放回键盘：这次先把对局打完。决胜团结束，基地终于倒下，导播才切到你的笑脸。','第一段是开心，第二段是终于赢了。这个平行宇宙的表情包，连同奖杯一起由你签收。'];
 if(theme==='lol'&&(augment&&augment.id)==='tes-top')return [`${identity.nickname||identity.name}，这回陀螺转出了反打角度。`,'在这条架空时间线，你们连着两波被压在塔前，弹幕里又飘起陀螺梗。你没有再抢着接第三波，而是和四位队友等到对面的开团技能交空，再从侧面一起打回去。','赛后梗图还在，但这次的结尾多了一段反打集锦。你把图存进群里：能笑，也能把下一波打明白。'];
 if(theme==='lol'&&series==='hex'){
  if(identity.personId==='uzi')return ['平行 S8，嚎哭深渊也能下起金色的雨。','在这条架空时间线，S8 决赛开在海克斯大乱斗的桥上。你变成污渍，对面的飞科又锁下加里奥。全场以为结局早已写好，你却用一波天赋联动和极限走位，把输出打到了结算页。','金色的雨落下。历史第一 ADC 只是起点，这个宇宙的观众把英雄联盟 GOAT 的剧本交给了你。收集者先收好，奖杯也别落下。'];
  if(identity.personId==='dasima')return ['这座桥，终于听懂了你的说法。','你化身大司马，走进一场架空海克斯冠军赛。随机给出的天赋看起来不搭，你边讲边把它连成一套“正方形大乱斗”。全队从一脸疑惑，打到一起点头。','最后一波结束，你端着奖杯继续讲：先别急，这次真的不是失误，是教材。冠军席，被你办成了一间公开课堂。'];
  if(identity.personId==='xiaohu')return ['嚎哭深渊，今天全桥入春。','你化身销户，进入一条只过春天的海克斯时间线。桥上冰雪还没化，天赋组合已经被你运营到舒服的位置。决胜团开打，所有人终于明白谁在掌握季节。','这个宇宙的奖杯旁多了一台恒温器。不是每年春天很强，是今天由你宣布春天。'];
  return [identity.name+'，这一座桥由你改写。','你化身'+identity.name+'，站上平行宇宙的海克斯大乱斗冠军桥。随机天赋没有给你标准答案，你用'+profile.name+'的反应，把一次普通抽签变成了自己的打法。'+(augment?'这一局，'+augment.name+'也写进了你的名场面。':''),'对手记住的也许是连招，队友记住的是这一局有人敢把可能性试出来。奖杯旁边，还有一枚属于这个宇宙的 GOAT 彩蛋。'];
 }
 if(theme==='abstract'&&identity.personId==='shake-director')return ['前奏一响，另一个你已经站到镜头中间。','在这个虚构的平行宇宙，你成了摇摆导演。原本只想拍十秒，四位队友一到场，群舞、翻唱和笑场一起上线。你把最像自己的那一段留下，第一次用自己的节奏被大家记住。','成片不必全程整齐。有人记得舞步，有人记得笑声，这期终于有了你自己的味道。'];
 if(theme==='abstract'&&identity.personId==='liziqi')return ['慢一点，普通日常也有自己的主角镜头。','在这条架空时间线，你化身李子柒，和四位搭档把一件普通手作拍成了温柔的小故事。你没有急着追下一个热点，而是把材料、过程和做完后的笑容都留下。','视频有自己的呼吸，更新也有自己的节奏。这个宇宙的专属海克斯，是认真生活时一点点积累的光。'];
 if(theme==='basket'&&identity.personId==='wemby')return ['文班长臂服务区，今天正式营业。','平行总决赛里，你化身文班亚马。对手还在寻找上篮角度，你已经和四位队友把篮下照顾明白。一次干净封盖之后，你没有忙着庆祝，转身就把球传向跑起来的队友。','外星人梗可以接，位置还得认真站。这个宇宙的冠军合照里，五个人都在你的服务范围。'];
 if(theme==='basket'&&identity.personId==='edwards')return ['华子准备起飞，回防也在飞行计划里。','平行总决赛最后一节，你化身华子。队友传来一个舒服的球，你抓住合适机会完成上篮，笑着和传球的人击掌。镜头想留住你的庆祝，你已经回到防守的位置。','篮球梦之队把高光留给你，也把下一球继续交给你。这场比赛的节目效果，有冲劲，也有靠谱的下一步。'];
 const own=stories[identity.personId];if(own)return own;return theme==='lol'?[`${identity.name}，这次由你接下决胜局。`,`你化身${identity.name}，走进一条结局尚未写下的平行赛道。对手准备好了熟悉的套路，你用${profile.name}的打法把这一局带到了新的节奏。`,'奖杯不是剧本的终点。五个人愿意再开一局，才是这个宇宙最好的彩蛋。']:theme==='basket'?[`${identity.name}，今天的名场面由你签收。`,`你化身${identity.name}。平行总决赛把所有戏剧性都留到了末节，你把熟悉的动作和没试过的选择拼成了自己的答案。`,'这个宇宙的虎扑式搞笑评分给出满分：有人负责数据，有人负责让整场值得重看。']:[`${identity.name}，你在另一个宇宙上线了。`,`你化身${identity.name}。普通的一天被平行宇宙拧开了一个口子，你用${profile.name}的方式，把五个看似不搭的人放进同一段故事。`,'故事没有标准答案。能把自己的那一集过得有声有色，也是一种隐藏天赋。'];}
function analyze(session,data){
 const vector=score(session,data),pool=data.characters.filter(p=>p.theme===session.theme),ranked=rankPeople(session,data,vector);
 const identity=ranked[0],code=[0,1,2].map(i=>vector[i]>=50?'1':'0').join('');let profile=data.profiles.find(p=>p.id===data.familyCodes[code]);
 if(session.theme==='lol'){const hi=vector.indexOf(Math.max(...vector));profile=Object.assign({},profile,{name:['上头编剧','金币合伙人','雪球发车人','全队保护伞','基本功信徒','桥上运营师'][hi]});}
 const recommendations=recommend(session,data,vector,identity),augment=recommendations[0],rows=selections(session,data);
 const evidence=dimsFor(session.theme).map((dim,di)=>{const choices=[].concat(...rows.map(({q,o})=>{if(session.theme!=='lol'&&q.dim!==dim)return [];return [{id:q.id,scene:q.scene,title:q.title,choice:o.text,value:session.theme==='lol'?o.signals[dim]:(o.value-1)/3*100}];}));choices.sort((a,b)=>Math.abs(b.value-50)-Math.abs(a.value-50));return Object.assign({dim,coordinate:vector[di]},choices[0]);});
 const bond=recommendations.find(a=>(a.signatureFor||[]).includes(identity.personId))||null;
 return {vector,identity,ranked,profile,augment,recommendations,bond,team:linkTeam(buildTeam(vector,ranked,identity,augment),augment,session.theme),story:narrative(identity,session.theme,profile,session.series,augment),signature:Object.entries(rows.reduce((sum,{o})=>{sum[o.behavior]=(sum[o.behavior]||0)+1;return sum;},{})).sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0])).slice(0,3).map(([id,count])=>({id,count,label:data.behaviorLabels[id]})),evidence,coverage:dimsFor(session.theme).map(dim=>session.theme==='lol'?session.count:rows.filter(({q})=>q.dim===dim).length)};
}
return {dimIds,lolDimIds,dimsFor,shuffle,draw,valid,score,similarity,analyze,buildTeam,narrative,recommend,context,selections,questionAt,rankPeople,behaviorFit,artLayout,recordAnswer,squadError,fillSquad,customSquad};
});

(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.ShenrenV11Engine=factory();})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const dimIds=['social','explore','empathy','action','order','express'];
const lolDimIds=['tilt','greed','risk','team','craft','plan'];
const dimsFor=theme=>theme==='lol'?lolDimIds:dimIds;
function random(){if(typeof crypto!=='undefined'&&crypto.getRandomValues){const a=new Uint32Array(1);crypto.getRandomValues(a);return a[0]/4294967296;}return Math.random();}
function shuffle(list,rng=random){const a=list.slice();for(let i=a.length-1;i>0;i--){const j=Math.floor(rng()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
// One layout feeds both HTML and exported Canvas: the real icons and copy counts match.
function artLayout(a){
 const icons=a.visual?a.visual.icons:[],n=icons.length,l=a.visual?a.visual.layout:null;
 const points=n===1?[[.19,.19,.62,0]]:l==='grid'?icons.map((_,i)=>[.02+(i%3)*.33,.17+Math.floor(i/3)*.34,.30,0]):l==='square'?[[.07,.07,.36,-8],[.57,.07,.36,8],[.07,.57,.36,8],[.57,.57,.36,-8]]:l==='ring'?icons.map((_,i)=>{const t=-Math.PI/2+i*Math.PI*2/n;return [.33+Math.cos(t)*.28,.33+Math.sin(t)*.28,.34,i*15-15];}):l==='row'?icons.map((_,i)=>[.03+i*(.94-.40)/Math.max(1,n-1),.30+(i%2)*.1,.40,(i-(n-1)/2)*10]):n===2?[[.04,.28,.47,-15],[.49,.19,.47,15]]:n===3?[[.03,.35,.47,-17],[.51,.35,.47,17],[.27,.07,.47,0]]:n===4?[[.05,.14,.4,-15],[.55,.14,.4,15],[.05,.55,.4,-8],[.55,.55,.4,8]]:[[.03,.14,.37,-17],[.23,.04,.37,-8],[.43,.04,.37,8],[.62,.14,.37,17],[.29,.53,.43,0]];
 return icons.map((icon,i)=>({icon,x:points[i][0],y:points[i][1],size:points[i][2],rotation:points[i][3]}));
}
function enabledPeople(data,theme=null){return data.characters.filter(p=>p.enabled!==false&&(!theme||p.theme===theme)).sort((a,b)=>(a.rosterOrder||0)-(b.rosterOrder||0));}
function enabledCards(data,theme=null){return [].concat(...Object.keys(data.augments).filter(t=>!theme||t===theme).map(t=>data.augments[t])).filter(a=>a.enabled!==false);}
function searchPeople(data,theme,query=''){const q=query.trim().toLowerCase();return enabledPeople(data,theme==='all'?null:theme).filter(p=>[p.name,p.nickname].concat(p.aliases||[],p.tags||[]).join(' ').toLowerCase().includes(q));}
function resolvePerson(data,value){const q=String(value).toLowerCase();return data.characters.find(p=>p.id===value||p.personId===value||(p.aliases||[p.name,p.nickname]).some(a=>a&&a.toLowerCase()===q))||null;}
function applyExposure(candidates,policy={}){const top=Math.max(...candidates.map(p=>p.rawMatch)),near=policy.nearTop===undefined?5:Math.min(5,policy.nearTop),max=policy.maxBonus===undefined?4:Math.min(4,Math.max(0,policy.maxBonus));return candidates.map(p=>Object.assign({},p,{match:p.rawMatch,editorialBonus:p.tier==='featured'&&top-p.rawMatch<=near?max:0})).sort((a,b)=>(b.rawMatch+b.editorialBonus)-(a.rawMatch+a.editorialBonus)||b.rawMatch-a.rawMatch||a.id.localeCompare(b.id));}
function exposureSample(data,theme,n=1,rng=random){const pool=enabledPeople(data,theme).slice(),out=[];while(pool.length&&out.length<n){let x=rng()*pool.reduce((sum,p)=>sum+p.exposureWeight,0),i=0;for(;i<pool.length-1;i++){x-=pool[i].exposureWeight;if(x<0)break;}out.push(pool.splice(i,1)[0]);}return out;}
function draw(data,theme,count,previousFirst=null,rng=random,series='all'){
 if(!data.themes.some(t=>t.id===theme)||!data.modes.includes(count))throw Error('不支持的主题或题量');
 if(theme==='lol'&&!['all','hex','rift'].includes(series))throw Error('不支持的联盟系列');
 let chosen=[];
 if(theme==='lol'){
  const bank=data.questions.filter(q=>q.enabled!==false&&q.theme===theme&&(series==='all'||q.series===series));
  const chapters=shuffle([...new Set(bank.map(q=>q.series+':'+q.chapter))],rng);
  if(chapters.length<count/4)throw Error('章节题库不足');
  if(bank.some(q=>q.id===previousFirst&&chapters[0]===q.series+':'+q.chapter))[chapters[0],chapters[1]]=[chapters[1],chapters[0]];
  chosen=[].concat(...chapters.slice(0,count/4).map(c=>bank.filter(q=>q.series+':'+q.chapter===c).sort((a,b)=>a.stage-b.stage)));
 }else{
  const extra=new Set(shuffle(dimIds,rng).slice(0,count%6));
  dimIds.forEach(dim=>{const bank=data.questions.filter(q=>q.enabled!==false&&q.theme===theme&&q.dim===dim),n=Math.floor(count/6)+(extra.has(dim)?1:0);if(bank.length<n)throw Error('题库不足');chosen.push(...shuffle(bank,rng).slice(0,n));});
  chosen=shuffle(chosen,rng);if(chosen[0].id===previousFirst)[chosen[0],chosen[1]]=[chosen[1],chosen[0]];
 }
 return {version:data.version,theme,series:theme==='lol'?series:'all',count,deck:chosen.map(q=>({id:q.id,order:shuffle(q.options.map(o=>o.id),rng)})),answers:Array(count).fill(null),index:0,phase:'quiz',date:new Date().toISOString()};
}
function valid(s,data,complete=false){
 if(!s||s.version!==data.version||!data.themes.some(t=>t.id===s.theme)||!data.modes.includes(s.count)||!Array.isArray(s.deck)||s.deck.length!==s.count||!Array.isArray(s.answers)||s.answers.length!==s.count||!Number.isInteger(s.index)||s.index<0||s.index>=s.count)return false;
 if(s.theme==='lol'&&!['hex','rift','all'].includes(s.series))return false;
 if(new Set(s.deck.map(d=>d&&d.id)).size!==s.count)return false;
 const questions=s.deck.map(d=>data.questions.find(q=>q.id===(d&&d.id)&&q.theme===s.theme&&(s.theme!=='lol'||s.series==='all'||q.series===s.series)));
 if(questions.some(q=>!q))return false;
 if(s.theme==='lol'){
  for(let i=0;i<questions.length;i+=4){const group=questions.slice(i,i+4);if(group.some((q,j)=>q.chapter!==group[0].chapter||q.series!==group[0].series||q.stage!==j))return false;}
 }else if(!dimIds.every(dim=>questions.some(q=>q.dim===dim)))return false;
 return s.deck.every((d,i)=>Array.isArray(d.order)&&d.order.length===4&&new Set(d.order).size===4&&d.order.every(v=>questions[i].options.some(o=>o.id===v))&&((!complete&&s.answers[i]===null)||questions[i].options.some(o=>o.id===s.answers[i])));
}
// Commit against the question that was actually displayed; stale taps cannot answer another question.
function recordAnswer(s,data,questionId,optionId){
 if(!valid(s,data)||s.phase!=='quiz'||s.deck[s.index].id!==questionId)throw Error('这道题已经切换，请重新选择');
 const q=data.questions.find(q=>q.id===questionId);
 if(!q.options.some(o=>o.id===optionId))throw Error('这个选项不存在');
 const next=Object.assign({},s,{answers:s.answers.slice()});next.answers[s.index]=optionId;
 const complete=s.index===s.count-1;
 if(complete)next.phase='complete';else next.index=s.index+1;
 return {session:next,complete};
}
function selections(s,data){return s.deck.map((d,i)=>{const q=data.questions.find(q=>q.id===d.id);return {q,o:q.options.find(o=>o.id===s.answers[i])};});}
function score(s,data){
 if(!valid(s,data,true))throw Error('请完成本轮全部题目');const rows=selections(s,data);
 return dimsFor(s.theme).map(dim=>{if(s.theme==='lol'){const total=rows.reduce((sum,{o})=>sum+o.signals[dim],0),neutral=rows.reduce((sum,{q})=>sum+q.options.reduce((n,o)=>n+o.signals[dim],0)/4,0),lo=rows.reduce((sum,{q})=>sum+Math.min(...q.options.map(o=>o.signals[dim])),0),hi=rows.reduce((sum,{q})=>sum+Math.max(...q.options.map(o=>o.signals[dim])),0),delta=total-neutral;return Math.max(0,Math.min(100,Math.round(50+50*delta/Math.max(1,delta>=0?hi-neutral:neutral-lo))));}const values=rows.filter(({q})=>q.dim===dim).map(({o})=>o.value);return Math.round((values.reduce((a,b)=>a+b,0)/values.length-1)/3*100);});
}
function similarity(a,b){return Math.round(100*(1-a.reduce((s,v,i)=>s+Math.abs(v-b[i]),0)/600));}
function responseWeight(q){return q.importance||1;}
function behaviorFit(rows,weights={}){const total=rows.reduce((sum,{q})=>sum+responseWeight(q),0);return total?100*rows.reduce((sum,{q,o})=>sum+(weights[o.behavior]||0)*responseWeight(q),0)/(5*total):0;}
function cardEvidence(rows,card){return rows.map(({q,o},index)=>({id:q.id,scene:q.scene,choice:o.text,behavior:o.behavior,strength:((card.behaviorWeights&&card.behaviorWeights[o.behavior])||0)*responseWeight(q),index})).filter(e=>e.strength>0&&(!card.evidenceQuestionIds||!card.evidenceQuestionIds.length||card.evidenceQuestionIds.includes(e.id))).sort((a,b)=>b.strength-a.strength||a.index-b.index);}
function rankPeople(s,data,vector){const rows=selections(s,data);return applyExposure(enabledPeople(data,s.theme).map(p=>{const v=similarity(vector,p.vector),b=behaviorFit(rows,p.behaviorWeights),scene=100*rows.reduce((sum,{q,o})=>sum+((p.answerAffinities&&p.answerAffinities[q.id]&&p.answerAffinities[q.id][o.behavior])||0),0)/(5*rows.length);return Object.assign({},p,{rawMatch:Math.round(.4*v+.35*b+.25*scene),matchBreakdown:{vector:v,behavior:b,scene}});}),data.rosterPolicy);}

function recommend(s,data,vector=score(s,data),identity=null){
 const rows=selections(s,data);if(!identity)identity=rankPeople(s,data,vector)[0];
 return enabledCards(data,s.theme).filter(a=>a.activationMode!=='identity').filter(a=>!a.personOnly||(a.signatureFor||[]).includes(identity.personId)).filter(a=>!(a.requires||[]).length||(a.requires||[]).some(b=>rows.some(({o})=>o.behavior===b))).map(a=>{
  const v=a.vector||a.bias.map(n=>Math.max(0,Math.min(100,50+n*40))),evidence=cardEvidence(rows,a);
  const behavior=behaviorFit(rows,a.behaviorWeights),bonus=(a.affinities||[]).includes(identity.personId)?5:0;
  const match=Math.round(.42*similarity(vector,v)+.53*behavior+bonus);
  return Object.assign({},a,{match,evidence:evidence.slice(0,2),hitCount:evidence.length,personLink:bonus>0});
 }).filter(a=>a.hitCount>0).sort((a,b)=>Number(Boolean(b.exclusive&&b.personLink))-Number(Boolean(a.exclusive&&a.personLink))||b.match-a.match||b.hitCount-a.hitCount||a.id.localeCompare(b.id));
}
function questionAt(s,data,index=s.index){const q=data.questions.find(q=>q.id===(s.deck[index]&&s.deck[index].id));if(!q)return null;const prior=index>0?s.answers[index-1]:null;return Object.assign({},q,{title:q.branches&&prior!==null?(q.branches[String(prior)]||q.title):q.title});}
const reactions={afk:'你的镜头切到观战席，接下来由你决定这局怎么演。',int:'上一单已经送达，导播开始等你的下一次发车。',collector:'第五把收集者已在计划里，下一波还得看阵容。',protect:'你把队友留在镜头里，接下来看看这份售后怎么做。',heal:'桥头医务室已经开门，下一波挂号队伍也到了。',explain:'复活倒计时在走，你的讲解刚刚开始。',blame:'锅还在空中，下一幕先看看谁来接。',chaos:'节目效果已到账，故事还有下一幕。',plan:'计划先写在这里，接下来看看现场听不听安排。',engage:'车已经开了，接下来看乘客有没有跟上。',reset:'上一段剧本已翻篇，新的一幕还等你接梗。',laugh:'笑容先记一段，接下来手也要跟上。',calm:'你把庆祝留到了后面，先把眼前的对局打完。',spin:'抗压拉扯已经开始，下一步看看有没有反打空间。',stasis:'金身时机已经记下，结束之后还得接着操作。',flash:'闪现交了，接下来先把走位和退路找回来。',vision:'你先要信息，再决定下一步怎么打。'};
function context(s,data,index=s.index){const q=questionAt(s,data,index);if(q.theme!=='lol'||q.stage===0)return null;const previous=data.questions.find(p=>p.id===s.deck[index-1].id),o=previous.options.find(o=>o.id===s.answers[index-1]);return o?{chapter:q.chapterName,stage:q.stage,previousChoice:o.text,previousScene:previous.scene,reaction:reactions[o.behavior]||'上一个反应已经记下，同一场对局继续往下演。'}:null;}
const teamScripts={
 range:['上路卡位：把对手留在输出射程里。','打野盯人：绕后的人先报位置。','中路消耗：命中一轮再决定进退。','下路拉扯：边走边打，别只顾着后退。','辅助接应：控制留给贴脸的那个人。'],
 blame:['上路复盘：先说线权，再看有没有支援。','打野报点：刷野路线和到场时间说清楚。','中路看图：先确认信息，再问队友在哪。','下路回放：谁先吃控，拉进度条再说。','辅助提醒：复活时间和技能比问号更有用。'],
 economy:['上路承压：先站住，再给四个输出腾空间。','野区控图：该吃资源时吃，该到场时到。','中路游走：推完线再走，别两头都漏。','下路收尾：残血可以收，前排别硬穿。','辅助售后：全队唯一还看血条的人。'],
 chaos:['上路独演：先把边线变成个人舞台。','打野发车：路线直达下一段集锦。','中路配乐：这一波自带主角 BGM。','下路压轴：高光和灰屏只隔一帧。','辅助验票：上车前请签字。'],
 engage:['上路顶门：把第一波技能收下。','打野发车：开之前先数一遍乘客。','中路接戏：控制留给关键那个人。','下路输出：司机说到站再下车。','辅助导航：负责把人齐这件事讲明白。'],
 protect:['上路挡风：四个输出的移动掩体。','打野保安：巡逻到后排就上班。','中路调度：让技能替队友争取时间。','下路患者：请在医务室射程内营业。','辅助主治：这家没你真得关门。'],
 basic:['上路动作指导：细节交给手，不交给嘴。','打野解说：先把路线走成一个几何题。','中路编导：等到技能窗口再拍。','下路主演：金色的雨要自己走位接。','辅助控场：让高光背后有人接应。'],
 plan:['上路带线：看完小地图再过河。','打野路线：第四条边还没讲完。','中路恒温：今天几度由这里决定。','下路输出：等关键装备成型再接硬仗。','辅助复盘：把五个人留在同一张图上。'],
 retreat:['上路安全员：撤退也要留出通道。','打野巡场：先看地图再问队友呢。','中路观察：等对手把按钮按完。','下路远程：在安全感边缘输出。','辅助接人：回来就有口热奶。'],
 reset:['上路续集：这一条线还没演完。','打野刷新：新路线下一局见。','中路转场：重开也要记得带队友。','下路重拍：镜头先别删。','辅助留人：说好最后一把，又齐了。']};
function linkTeam(team,augment,theme){const lines=theme==='basket'?['控卫串联：先让队友都能接到球。','分卫接火：有机会就投，没机会先传。','侧翼跑动：把这一段名场面接起来。','篮下协作：卡好位置，给队友留空间。','中锋护框：篮板和回防都得有人管。']:theme==='abstract'?['发言人开场：把五个人的故事讲清楚。','行动派开拍：先完成最容易的一小段。','军师编排：好点子也要有人把它做出来。','气氛组接梗：前奏一响，全队进入画面。','场控收尾：照顾边界，也别落下任何队友。']:(teamScripts[augment.kind]||teamScripts.chaos);return team.map(p=>Object.assign({},p,{teamLine:lines[p.slot]}));}
function buildTeam(vector,characters,identity,augment){
 let best=null;
 for(const myRole of identity.roles){
  let states=Array(32).fill(null);states[1<<myRole]={value:0,slots:Array(5).fill(null)};states[1<<myRole].slots[myRole]=identity;
  for(const p of characters.filter(p=>p.id!==identity.id)){
   const next=states.slice();for(let mask=0;mask<32;mask++){const prior=states[mask];if(!prior)continue;
    for(let role=0;role<5;role++){if(mask&(1<<role)||!p.roles.includes(role))continue;const match=similarity(vector,p.vector),affinity=p.roles[0]===role?12:p.roles.includes(role)?7:-18;const flavor=augment?augment.bias.reduce((s,w,i)=>s+w*(p.vector[i]-50)/10,0):0;const value=prior.value+match+affinity+flavor;
     const to=mask|(1<<role);if(!next[to]||value>next[to].value){const slots=prior.slots.slice();slots[role]=p;next[to]={value,slots};}}
   }states=next;
  }
  const full=states[31];if(full&&(!best||full.value>best.value))best=full;
 }
 if(!best)throw Error('角色池不足以组成五人队');return best.slots.map((p,i)=>Object.assign({},p,{slot:i,isYou:p.id===identity.id,match:p.match===undefined?similarity(vector,p.vector):p.match,naturalRole:p.roles.includes(i)}));
}

function squadError(ids,theme,data,free=false,partial=false){
 if(!Array.isArray(ids)||ids.length!==5)return '请选择五个位置';
 const chosen=ids.filter(Boolean);if(!partial&&chosen.length!==5)return '还没选满五个人';
 const people=[];for(let i=0;i<5;i++){if(!ids[i])continue;const p=enabledPeople(data,theme).find(p=>p.id===ids[i]);if(!p)return '只能选择当前主题的人物';if(people.includes(p.personId))return '同一个人不能重复出场';people.push(p.personId);if(!free&&!p.roles.includes(i))return '这个位置不合适，可开启自由整活';}return '';
}
function fillSquad(ids,theme,data,vector,free=false){
 const err=squadError(ids,theme,data,free,true);if(err)throw Error(err);
 const fixed=ids.map(id=>id?data.characters.find(p=>p.id===id):null),used=fixed.filter(Boolean).map(p=>p.personId);let mask=0;fixed.forEach((p,i)=>{if(p)mask|=1<<i;});
 let states=Array(32).fill(null);states[mask]={value:0,slots:fixed.slice()};
 for(const p of enabledPeople(data,theme).filter(p=>!used.includes(p.personId))){const next=states.slice();for(let m=0;m<32;m++){const prev=states[m];if(!prev)continue;for(let i=0;i<5;i++){if((m&(1<<i))||(!free&&!p.roles.includes(i)))continue;const val=prev.value+similarity(vector,p.vector)+(p.roles[0]===i?12:p.roles.includes(i)?7:-15),to=m|(1<<i);if(!next[to]||val>next[to].value){const slots=prev.slots.slice();slots[i]=p;next[to]={value:val,slots};}}}states=next;}
 if(!states[31])throw Error('当前选择无法补齐五个位置；请换人或开启自由整活');return states[31].slots.map(p=>p.id);
}
function customSquad(ids,theme,data,vector,identity,augment,free=false){
 const err=squadError(ids,theme,data,free);if(err)throw Error(err);
 return linkTeam(ids.map((id,slot)=>{const p=data.characters.find(p=>p.id===id);return Object.assign({},p,{slot,isYou:p.personId===identity.personId,match:similarity(vector,p.vector),naturalRole:p.roles.includes(slot),custom:true});}),augment,theme).map(p=>Object.assign({},p,{teamLine:(p.naturalRole?'':'跨位整活 / ')+(p.tags||[]).slice(0,2).join(' · ')+'。'+p.teamLine}));
}

const stories={
 jackeylove:['哥哥，这回向前一步走到了金色的雨。','在这条架空 S8 时间线，你化身阿水。最后一局的闪现没有换来灰屏，而是等到了四名队友同时到场。你找到侧面的空隙，输出、拉开、再次上前，把那个熟悉的“敢打”变成了所有人等着看的结局。','奖杯前大家又喊起哥哥。你笑着把四个人拉进合照：这次镜头里，一个队友都没少。'],
 rookie:['院长，这次把整个宇宙都救回来了。','你化身 Rookie，站进一场架空 S8 决赛。队友在语音里喊你，你把中路守成了全队的落脚点。最后一波控制接上，四个熟悉的身影一起向前，你的输出把最后一座基地打成了金色的雨。','你抱着奖杯，眼泪先于采访回答。观众喊着肉鸡，队友说今天院长终于可以下班了。'],
 dailanzi:['评论区还没开，你的平行宇宙已经有了开场白。','你化身带篮子，带着四位风格完全不同的队友开了一场平行宇宙直播。刀哥带了好果汁，峰哥讲起路上的故事，台下刚有点冷场，你用一句带文学把所有人拉回同一段里。','散场后，最热的一条弹幕不是谁赢了，而是“这五个人怎么凑一起的”。你把它置顶：下一期，还得人齐。'],
 xiaoxiao:['双声道里，终于播到了冠军谢幕。','你化身笑笑，和西卡坐在平行决赛的解说席。开场的笑声被你们接成一句句简明的提醒。最后一波五个人齐了，基地倒下，你们一边笑一边把每个队友的名字喊出来。','这个宇宙的冠军回放有两个声道：一个记住操作，一个记住大家为什么一起笑。'],
 xika:['搭档那句话，被你接成了整个宇宙的片尾。','你化身西卡，和笑笑主持一场平行宇宙冠军之夜。有人讲快了，你补一句；有人漏了细节，你再讲清一遍。最后一波打完，直播间的笑声和现场的金色纸片一起落下。','冠军采访结束，你还在替这局接尾句：先别关，五个人的合照还没拍。'],
 uzi:['平行 S8，轮到你改写结局。','在这条架空时间线，你变成了污渍。决胜局，对面的飞科锁下加里奥，镜头里所有人都以为这又是熟悉的剧本。你却在最后一波侧身躲开控制，和四位队友一起战胜 Faker，把输出打到了结算页面。','金色的雨落下。你抱着奖杯泪流满面，全场高喊“世界第一 ADC”。主持人还在问“历史第一 ADC”，你已经把问题推进到“英雄联盟的 GOAT”。收集者不是决定，敢不敢接下这场比赛才是。'],
 xiaohu:['这个宇宙，没有不属于你的季节。','你变成了销户，赛场的日历被你改成了“春一月”到“春十二月”。总决赛打到最后一局，你把边线、团战与笑容一起拉满。','奖杯旁边多了一块恒温器：全宇宙的春天，今天由中路负责。'],
 dasima:['从讲解席，走到冠军颁奖台。','你变成了大司马。架空决赛里，所有人还在质疑你的路线，你已经画出了第三条“正方形打野”轨迹。最后一波不是嘴上有说法，是地图真的照着你的说法走。','奖杯被你端成一件教学道具。冠军公开课第一句话：先别急，这波我慢慢讲。'],
 theshy:['上路这条线，通向另一个结局。','你化身 TheShy，在架空决赛把一条边线打成了自己的独立宇宙。对手终于凑齐五个人来围你，你的队友刚好把另一边的主场拆完。','赛后大家讨论阵型，你在战术板上画了一条线：这里，也是一种答案。'],
 faker:['这一次，时间站在你这一边。','你化身飞科。平行决赛进入最安静的十秒，你等到所有技能交错的缝隙，再把那个属于自己的窗口按了下去。','第五次、第六次都不再是问题。这个宇宙的传奇，是把每一个小回合认真打完。'],
 lebron:['勒邦詹氏，膝盖先于战术板反应。','平行总决赛最后一攻，你变成了勒邦詹氏。漏判出现，全场进入表情加载页，你用一个跪地默剧把节目效果拉满。随后你站起来，追帽、推进、压哨出手一气呵成。','球进灯亮。这个宇宙的“虎扑式”搞笑评分写着：10 分，建议把膝盖也算进首发。你拿走的是这条时间线的 GOAT 剧本。'],
 curry:['停车场，正式进入你的射程表。','你变成了库里。平行总决赛的三分线被搬到停车场，大家还在找停车位，你已经借掩护转身出手。篮球在空中待得像一趟跨省快递。','球落网，晚安手势安排上。这个宇宙规定：只要你站得稳，想象力就有出手权。'],
 kobe:['凌晨的第一盏灯，由你点亮。','你化身科比。平行总决赛最后一节，你把练过无数遍的动作放进那个最需要答案的回合。全场的声音很大，你听见的只有脚步和球落网。','镜头切到空荡的训练馆：这里，早就为这个结局留过灯。'],
 jokic:['马儿没来，但传球已经到了。','你化身约老师。平行总决赛开打前，大家发现战术板背面是一张木马旋转图。第三节开始，对手才意识到每个人都被你转到了正确的位置。','你拿着奖杯问能不能早点回去。这个宇宙的中锋，把轻描淡写打成了史诗。'],
 fengge:['你去过的地方，地图还没来得及加载。','你变成了峰哥，揣着一张平行宇宙通行证出发。路边一间小卖部卖的是“如果当年”，你没急着买，而是拉老板聊完了另一个人生。','最后你带回来五个人和一大串故事。宇宙没被你讲明白，但你的这一集已经够好看。'],
 huge:['来，整个宇宙先别关。','你变成了虎哥。平行东北的路灯突然集体熄灭，你一抬手，现场五个人自带开机音效。围观群众还没弄清第一幕，第二幕已经顺着街口开过去了。','城市把“节目效果维护员”奖章发给你。你问：奖章能不能再配一瓶好果汁？'],
 daoge:['好果汁，这回送到了银河边上。','你变成了刀哥。一封星际补给单把你带到银河边，你发现全宇宙都在排队等下一段名场面。你把好果汁放上桌，先把五个队友招呼齐。','这场没有既定台词，只有现场反应。你的平行身份，是让离谱故事继续发生的人。'],
 geyou:['你没拯救宇宙，你让它坐下休息了。','你变成了葛优。平行世界不停催进度，所有人都在找下一场大事。你先在沙发上挪出四个位置，把队友一个个招呼坐下。','宇宙最后没爆炸。它只是承认：有些重要的事，要坐稳了才能想明白。']
};
function narrative(identity,theme,profile,series='all',augment=null){
 if(theme==='lol'&&(augment&&augment.id)==='double-laugh')return [`${identity.nickname||identity.name}，把第二段笑留给金色的雨。`,'在这条架空时间线，你在开局前忍住了第一段笑。领先以后，队友已经准备庆祝，你却把手重新放回键盘：这次先把对局打完。决胜团结束，基地终于倒下，导播才切到你的笑脸。','第一段是开心，第二段是终于赢了。这个平行宇宙的表情包，连同奖杯一起由你签收。'];
 if(theme==='lol'&&(augment&&augment.id)==='tes-top')return [`${identity.nickname||identity.name}，这回陀螺转出了反打角度。`,'在这条架空时间线，你们连着两波被压在塔前，弹幕里又飘起陀螺梗。你没有再抢着接第三波，而是和四位队友等到对面的开团技能交空，再从侧面一起打回去。','赛后梗图还在，但这次的结尾多了一段反打集锦。你把图存进群里：能笑，也能把下一波打明白。'];
 if(theme==='lol'&&series==='hex'){
  if(identity.personId==='uzi')return ['平行 S8，嚎哭深渊也能下起金色的雨。','在这条架空时间线，S8 决赛开在海克斯大乱斗的桥上。你变成污渍，对面的飞科又锁下加里奥。全场以为结局早已写好，你却用一波天赋联动和极限走位，把输出打到了结算页。','金色的雨落下。历史第一 ADC 只是起点，这个宇宙的观众把英雄联盟 GOAT 的剧本交给了你。收集者先收好，奖杯也别落下。'];
  if(identity.personId==='dasima')return ['这座桥，终于听懂了你的说法。','你化身大司马，走进一场架空海克斯冠军赛。随机给出的天赋看起来不搭，你边讲边把它连成一套“正方形大乱斗”。全队从一脸疑惑，打到一起点头。','最后一波结束，你端着奖杯继续讲：先别急，这次真的不是失误，是教材。冠军席，被你办成了一间公开课堂。'];
  if(identity.personId==='xiaohu')return ['嚎哭深渊，今天全桥入春。','你化身销户，进入一条只过春天的海克斯时间线。桥上冰雪还没化，天赋组合已经被你运营到舒服的位置。决胜团开打，所有人终于明白谁在掌握季节。','这个宇宙的奖杯旁多了一台恒温器。不是每年春天很强，是今天由你宣布春天。'];
  return [identity.name+'，这一座桥由你改写。','你化身'+identity.name+'，站上平行宇宙的海克斯大乱斗冠军桥。随机天赋没有给你标准答案，你用'+profile.name+'的反应，把一次普通抽签变成了自己的打法。'+(augment?'这一局，'+augment.name+'也写进了你的名场面。':''),'对手记住的也许是连招，队友记住的是这一局有人敢把可能性试出来。奖杯旁边，还有一枚属于这个宇宙的 GOAT 彩蛋。'];
 }
 if(theme==='abstract'&&identity.personId==='shake-director')return ['前奏一响，另一个你已经站到镜头中间。','在这个虚构的平行宇宙，你成了摇摆导演。原本只想拍十秒，四位队友一到场，群舞、翻唱和笑场一起上线。你把最像自己的那一段留下，第一次用自己的节奏被大家记住。','成片不必全程整齐。有人记得舞步，有人记得笑声，这期终于有了你自己的味道。'];
 if(theme==='abstract'&&identity.personId==='liziqi')return ['慢一点，普通日常也有自己的主角镜头。','在这条架空时间线，你化身李子柒，和四位搭档把一件普通手作拍成了温柔的小故事。你没有急着追下一个热点，而是把材料、过程和做完后的笑容都留下。','视频有自己的呼吸，更新也有自己的节奏。这个宇宙的专属海克斯，是认真生活时一点点积累的光。'];
 if(theme==='basket'&&identity.personId==='wemby')return ['文班长臂服务区，今天正式营业。','平行总决赛里，你化身文班亚马。对手还在寻找上篮角度，你已经和四位队友把篮下照顾明白。一次干净封盖之后，你没有忙着庆祝，转身就把球传向跑起来的队友。','外星人梗可以接，位置还得认真站。这个宇宙的冠军合照里，五个人都在你的服务范围。'];
 if(theme==='basket'&&identity.personId==='edwards')return ['华子准备起飞，回防也在飞行计划里。','平行总决赛最后一节，你化身华子。队友传来一个舒服的球，你抓住合适机会完成上篮，笑着和传球的人击掌。镜头想留住你的庆祝，你已经回到防守的位置。','篮球梦之队把高光留给你，也把下一球继续交给你。这场比赛的节目效果，有冲劲，也有靠谱的下一步。'];
 if(theme==='basket'&&identity.roleType==='commentator')return [identity.name+'，这场比赛由你来讲。','你化身'+identity.name+'，坐进平行宇宙的解说席。朋友们在场上拼出一个精彩回合，你把前因后果讲成大家都听得懂的故事。暂停时球员喝水，你还在认真接住观众的问题。','五人队采用本作娱乐角色设定；这里的你是解说员，没有虚构球员履历。'];
 const own=stories[identity.personId];if(own)return own;return theme==='lol'?[`${identity.name}，这次由你接下决胜局。`,`你化身${identity.name}，走进一条结局尚未写下的平行赛道。对手准备好了熟悉的套路，你用${profile.name}的打法把这一局带到了新的节奏。`,'奖杯不是剧本的终点。五个人愿意再开一局，才是这个宇宙最好的彩蛋。']:theme==='basket'?[`${identity.name}，今天的名场面由你签收。`,`你化身${identity.name}。平行总决赛把所有戏剧性都留到了末节，你把熟悉的动作和没试过的选择拼成了自己的答案。`,'这个宇宙的虎扑式搞笑评分给出满分：有人负责数据，有人负责让整场值得重看。']:[`${identity.name}，你在另一个宇宙上线了。`,`你化身${identity.name}。普通的一天被平行宇宙拧开了一个口子，你用${profile.name}的方式，把五个看似不搭的人放进同一段故事。`,'故事没有标准答案。能把自己的那一集过得有声有色，也是一种隐藏天赋。'];}
function analyze(session,data){
 const vector=score(session,data),pool=data.characters.filter(p=>p.theme===session.theme),ranked=rankPeople(session,data,vector);
 const identity=ranked[0],code=[0,1,2].map(i=>vector[i]>=50?'1':'0').join('');let profile=data.profiles.find(p=>p.id===data.familyCodes[code]);
 if(session.theme==='lol'){const hi=vector.indexOf(Math.max(...vector));profile=Object.assign({},profile,{name:['上头编剧','金币合伙人','雪球发车人','全队保护伞','基本功信徒','桥上运营师'][hi]});}
 const recommendations=recommend(session,data,vector,identity),augment=recommendations[0],rows=selections(session,data);
 const evidence=dimsFor(session.theme).map((dim,di)=>{const choices=[].concat(...rows.map(({q,o})=>{if(session.theme!=='lol'&&q.dim!==dim)return [];return [{id:q.id,scene:q.scene,title:q.title,choice:o.text,value:session.theme==='lol'?o.signals[dim]:(o.value-1)/3*100}];}));choices.sort((a,b)=>Math.abs(b.value-50)-Math.abs(a.value-50));return Object.assign({dim,coordinate:vector[di]},choices[0]);});
 const bond=recommendations.find(a=>(a.signatureFor||[]).includes(identity.personId))||null;
 return {inherentCards:(identity.signaturePerks||[]).map(id=>data.augments[session.theme].find(a=>a.id===id)).filter(Boolean),triggeredPersonal:recommendations.filter(a=>a.exclusive&&a.personLink),vector,identity,ranked,profile,augment,recommendations,bond,team:linkTeam(buildTeam(vector,ranked,identity,augment),augment,session.theme),story:narrative(identity,session.theme,profile,session.series,augment),signature:Object.entries(rows.reduce((sum,{o})=>{sum[o.behavior]=(sum[o.behavior]||0)+1;return sum;},{})).sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0])).slice(0,3).map(([id,count])=>({id,count,label:data.behaviorLabels[id]})),evidence,coverage:dimsFor(session.theme).map(dim=>session.theme==='lol'?session.count:rows.filter(({q})=>q.dim===dim).length)};
}
function makeSquadName(theme,team,previous='',rng=random){
 if(!Array.isArray(team)||team.length!==5||new Set(team.map(p=>p.personId)).size!==5)throw Error('五位不同的队友到齐后才能起名');
 const heads={lol:['全员收集者','五楼拒绝补位','网费不够但嘴硬','最后一把不散伙','复活期间还在讲课','金色的雨先分期','今天全队都在解释','先别急着说稳了'],basket:['凌晨四点还在打铁','膝盖管理局','最后一投谁都想要','球没进先怪风','篮板全靠缘分','停车场射程施工中','赛后采访没人认输','全队申请暂停'],abstract:['吃饱喝足再上头','全员学士帽Plus','麦克风无人刹车','路费还没凑齐','先别急着解释','饭点比闹钟还准','五个群聊管理员','正片没开始先笑场']};
 const tails={lol:['包夜互助会','峡谷临时夺冠办','五黑售后服务部','没有前排股份公司','不愿透露战绩的五位市民','宇宙级复盘研究所'],basket:['篮球研究所','野球场团建小队','赛后嘴硬中心','夕阳红冠军分部','全员回防倡议会','篮筐维修筹备组'],abstract:['互联网临时工','宇宙级气氛组','节目效果售后部','饭后发布会筹备组','平行宇宙嘴替联盟','未获通知也要返场团']};
 if(!heads[theme])throw Error('不支持的战队主题');let title='',hi=0,ti=0;for(let k=0;k<6;k++){hi=Math.min(heads[theme].length-1,Math.floor(rng()*heads[theme].length));ti=Math.min(tails[theme].length-1,Math.floor(rng()*tails[theme].length));title=heads[theme][hi]+' · '+tails[theme][ti];if(title!==previous)break;}if(title===previous)title=heads[theme][(hi+1)%heads[theme].length]+' · '+tails[theme][ti];
 const motto={lol:'上不上分先不说，今晚五个人必须整整齐齐。',basket:'投进算大家的，打铁就当替篮筐做体检。',abstract:'节目可以随缘，人和饭必须按时到齐。'}[theme];
 return {title,motto,ids:team.map(p=>p.id),theme};
}
return {makeSquadName,enabledPeople,enabledCards,searchPeople,resolvePerson,applyExposure,exposureSample,dimIds,lolDimIds,dimsFor,shuffle,draw,valid,score,similarity,analyze,buildTeam,narrative,recommend,context,selections,questionAt,rankPeople,behaviorFit,artLayout,recordAnswer,squadError,fillSquad,customSquad};
});

(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.ShenrenV12Engine=factory();})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const dimIds=['social','explore','empathy','action','order','express'];
const lolDimIds=['tilt','greed','risk','team','craft','plan'];
const dimsFor=theme=>theme==='lol'?lolDimIds:dimIds;
function random(){if(typeof crypto!=='undefined'&&crypto.getRandomValues){const a=new Uint32Array(1);crypto.getRandomValues(a);return a[0]/4294967296;}return Math.random();}
function shuffle(list,rng=random){const a=list.slice();for(let i=a.length-1;i>0;i--){const j=Math.floor(rng()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
// One layout feeds both HTML and exported Canvas: the real icons and copy counts match.
function artLayout(a){
 const icons=a.visual?a.visual.icons:[],n=icons.length,l=a.visual?a.visual.layout:null;
 const points=n===1?[[.19,.19,.62,0]]:l==='grid'?icons.map((_,i)=>[.02+(i%3)*.33,.17+Math.floor(i/3)*.34,.30,0]):l==='square'?[[.07,.07,.36,-8],[.57,.07,.36,8],[.07,.57,.36,8],[.57,.57,.36,-8]]:l==='ring'?icons.map((_,i)=>{const t=-Math.PI/2+i*Math.PI*2/n;return [.33+Math.cos(t)*.28,.33+Math.sin(t)*.28,.34,i*15-15];}):l==='row'?icons.map((_,i)=>[.03+i*(.94-.40)/Math.max(1,n-1),.30+(i%2)*.1,.40,(i-(n-1)/2)*10]):n===2?[[.04,.28,.47,-15],[.49,.19,.47,15]]:n===3?[[.03,.35,.47,-17],[.51,.35,.47,17],[.27,.07,.47,0]]:n===4?[[.05,.14,.4,-15],[.55,.14,.4,15],[.05,.55,.4,-8],[.55,.55,.4,8]]:[[.03,.14,.37,-17],[.23,.04,.37,-8],[.43,.04,.37,8],[.62,.14,.37,17],[.29,.53,.43,0]];
 return icons.map((icon,i)=>({icon,x:points[i][0],y:points[i][1],size:points[i][2],rotation:points[i][3]}));
}
function enabledPeople(data,theme=null){return data.characters.filter(p=>p.enabled!==false&&(!theme||p.theme===theme)).sort((a,b)=>(a.rosterOrder||0)-(b.rosterOrder||0));}
function enabledCards(data,theme=null){return [].concat(...Object.keys(data.augments).filter(t=>!theme||t===theme).map(t=>data.augments[t])).filter(a=>a.enabled!==false);}
function searchPeople(data,theme,query=''){const q=query.trim().toLowerCase();return enabledPeople(data,theme==='all'?null:theme).filter(p=>[p.name,p.nickname].concat(p.aliases||[],p.tags||[]).join(' ').toLowerCase().includes(q));}
function resolvePerson(data,value){const q=String(value).toLowerCase();return data.characters.find(p=>p.id===value||p.personId===value||(p.aliases||[p.name,p.nickname]).some(a=>a&&a.toLowerCase()===q))||null;}
function applyExposure(candidates,policy={}){
 if(!candidates.length)return [];
 const top=Math.max(...candidates.map(p=>p.rawMatch)),near=Math.max(0,Math.min(8,policy.nearTop===undefined?5:policy.nearTop)),bonus=Math.max(0,Math.min(6,policy.maxBonus===undefined?4:policy.maxBonus)),starNear=Math.max(0,Math.min(15,policy.flagshipNearTop===undefined?12:policy.flagshipNearTop)),starBonus=Math.max(0,Math.min(12,policy.flagshipBonus===undefined?9:policy.flagshipBonus));
 return candidates.map(p=>{const flagship=p.tier==='flagship',featured=p.tier==='featured',gap=top-p.rawMatch,add=flagship&&gap<=starNear?starBonus:featured&&gap<=near?bonus:0;return Object.assign({},p,{match:p.rawMatch,editorialBonus:add});}).sort((a,b)=>(b.rawMatch+b.editorialBonus)-(a.rawMatch+a.editorialBonus)||b.rawMatch-a.rawMatch||a.id.localeCompare(b.id));
}
function exposureSample(data,theme,n=1,rng=random){const pool=enabledPeople(data,theme).slice(),out=[];while(pool.length&&out.length<n){let x=rng()*pool.reduce((sum,p)=>sum+p.exposureWeight,0),i=0;for(;i<pool.length-1;i++){x-=pool[i].exposureWeight;if(x<0)break;}out.push(pool.splice(i,1)[0]);}return out;}
function draw(data,theme,count,previousFirst=null,rng=random,series='all'){
 if(!data.themes.some(t=>t.id===theme)||!data.modes.includes(count))throw Error('不支持的主题或题量');
 if(theme==='lol'&&!['all','hex','rift'].includes(series))throw Error('不支持的联盟系列');
 let chosen=[];
 if(theme==='lol'){
  const bank=data.questions.filter(q=>q.enabled!==false&&q.theme===theme&&(series==='all'||q.series===series));
  const chapters=shuffle([...new Set(bank.map(q=>q.series+':'+q.chapter))],rng);
  if(chapters.length<count/4)throw Error('章节题库不足');
  if(bank.some(q=>q.id===previousFirst&&chapters[0]===q.series+':'+q.chapter))[chapters[0],chapters[1]]=[chapters[1],chapters[0]];
  chosen=[].concat(...chapters.slice(0,count/4).map(c=>bank.filter(q=>q.series+':'+q.chapter===c).sort((a,b)=>a.stage-b.stage)));
 }else{
  const extra=new Set(shuffle(dimIds,rng).slice(0,count%6));
  dimIds.forEach(dim=>{const bank=data.questions.filter(q=>q.enabled!==false&&q.theme===theme&&q.dim===dim),n=Math.floor(count/6)+(extra.has(dim)?1:0);if(bank.length<n)throw Error('题库不足');chosen.push(...shuffle(bank,rng).slice(0,n));});
  chosen=shuffle(chosen,rng);if(chosen[0].id===previousFirst)[chosen[0],chosen[1]]=[chosen[1],chosen[0]];
 }
 return {version:data.version,theme,series:theme==='lol'?series:'all',count,deck:chosen.map(q=>({id:q.id,order:shuffle(q.options.map(o=>o.id),rng)})),answers:Array(count).fill(null),index:0,phase:'quiz',date:new Date().toISOString()};
}
function valid(s,data,complete=false){
 if(!s||s.version!==data.version||!data.themes.some(t=>t.id===s.theme)||!data.modes.includes(s.count)||!Array.isArray(s.deck)||s.deck.length!==s.count||!Array.isArray(s.answers)||s.answers.length!==s.count||!Number.isInteger(s.index)||s.index<0||s.index>=s.count)return false;
 if(s.theme==='lol'&&!['hex','rift','all'].includes(s.series))return false;
 if(new Set(s.deck.map(d=>d&&d.id)).size!==s.count)return false;
 const questions=s.deck.map(d=>data.questions.find(q=>q.id===(d&&d.id)&&q.theme===s.theme&&(s.theme!=='lol'||s.series==='all'||q.series===s.series)));
 if(questions.some(q=>!q))return false;
 if(s.theme==='lol'){
  for(let i=0;i<questions.length;i+=4){const group=questions.slice(i,i+4);if(group.some((q,j)=>q.chapter!==group[0].chapter||q.series!==group[0].series||q.stage!==j))return false;}
 }else if(!dimIds.every(dim=>questions.some(q=>q.dim===dim)))return false;
 return s.deck.every((d,i)=>Array.isArray(d.order)&&d.order.length===4&&new Set(d.order).size===4&&d.order.every(v=>questions[i].options.some(o=>o.id===v))&&((!complete&&s.answers[i]===null)||questions[i].options.some(o=>o.id===s.answers[i])));
}
// Commit against the question that was actually displayed; stale taps cannot answer another question.
function recordAnswer(s,data,questionId,optionId){
 if(!valid(s,data)||s.phase!=='quiz'||s.deck[s.index].id!==questionId)throw Error('这道题已经切换，请重新选择');
 const q=data.questions.find(q=>q.id===questionId);
 if(!q.options.some(o=>o.id===optionId))throw Error('这个选项不存在');
 const next=Object.assign({},s,{answers:s.answers.slice()});next.answers[s.index]=optionId;
 const complete=s.index===s.count-1;
 if(complete)next.phase='complete';else next.index=s.index+1;
 return {session:next,complete};
}
function selections(s,data){return s.deck.map((d,i)=>{const q=data.questions.find(q=>q.id===d.id);return {q,o:q.options.find(o=>o.id===s.answers[i])};});}
function score(s,data){
 if(!valid(s,data,true))throw Error('请完成本轮全部题目');const rows=selections(s,data);
 return dimsFor(s.theme).map(dim=>{if(s.theme==='lol'){const total=rows.reduce((sum,{o})=>sum+o.signals[dim],0),neutral=rows.reduce((sum,{q})=>sum+q.options.reduce((n,o)=>n+o.signals[dim],0)/4,0),lo=rows.reduce((sum,{q})=>sum+Math.min(...q.options.map(o=>o.signals[dim])),0),hi=rows.reduce((sum,{q})=>sum+Math.max(...q.options.map(o=>o.signals[dim])),0),delta=total-neutral;return Math.max(0,Math.min(100,Math.round(50+50*delta/Math.max(1,delta>=0?hi-neutral:neutral-lo))));}const values=rows.filter(({q})=>q.dim===dim).map(({o})=>o.value);return Math.round((values.reduce((a,b)=>a+b,0)/values.length-1)/3*100);});
}
function similarity(a,b){return Math.round(100*(1-a.reduce((s,v,i)=>s+Math.abs(v-b[i]),0)/600));}
function responseWeight(q){return q.importance||1;}
function behaviorFit(rows,weights={}){const total=rows.reduce((sum,{q})=>sum+responseWeight(q),0);return total?100*rows.reduce((sum,{q,o})=>sum+(weights[o.behavior]||0)*responseWeight(q),0)/(5*total):0;}
function cardEvidence(rows,card){return rows.map(({q,o},index)=>({id:q.id,scene:q.scene,choice:o.text,behavior:o.behavior,strength:((card.behaviorWeights&&card.behaviorWeights[o.behavior])||0)*responseWeight(q),index})).filter(e=>e.strength>0&&(!card.evidenceQuestionIds||!card.evidenceQuestionIds.length||card.evidenceQuestionIds.includes(e.id))).sort((a,b)=>b.strength-a.strength||a.index-b.index);}
function rankPeople(s,data,vector){const rows=selections(s,data);return applyExposure(enabledPeople(data,s.theme).map(p=>{const v=similarity(vector,p.vector),b=behaviorFit(rows,p.behaviorWeights),scene=100*rows.reduce((sum,{q,o})=>sum+((p.answerAffinities&&p.answerAffinities[q.id]&&p.answerAffinities[q.id][o.behavior])||0),0)/(5*rows.length);return Object.assign({},p,{rawMatch:Math.round(.4*v+.35*b+.25*scene),matchBreakdown:{vector:v,behavior:b,scene}});}),data.rosterPolicy);}

function recommend(s,data,vector=score(s,data),identity=null){
 const rows=selections(s,data);if(!identity)identity=rankPeople(s,data,vector)[0];
 return enabledCards(data,s.theme).filter(a=>a.activationMode!=='identity').filter(a=>!a.personOnly||(a.signatureFor||[]).includes(identity.personId)).filter(a=>!(a.requires||[]).length||(a.requires||[]).some(b=>rows.some(({o})=>o.behavior===b))).map(a=>{
  const v=a.vector||a.bias.map(n=>Math.max(0,Math.min(100,50+n*40))),evidence=cardEvidence(rows,a);
  const behavior=behaviorFit(rows,a.behaviorWeights),bonus=(a.affinities||[]).includes(identity.personId)?5:0;
  const match=Math.round(.42*similarity(vector,v)+.53*behavior+bonus);
  return Object.assign({},a,{match,evidence:evidence.slice(0,2),hitCount:evidence.length,personLink:bonus>0});
 }).filter(a=>a.hitCount>0).sort((a,b)=>Number(Boolean(b.exclusive&&b.personLink))-Number(Boolean(a.exclusive&&a.personLink))||b.match-a.match||b.hitCount-a.hitCount||a.id.localeCompare(b.id));
}
function questionAt(s,data,index=s.index){const q=data.questions.find(q=>q.id===(s.deck[index]&&s.deck[index].id));if(!q)return null;const prior=index>0?s.answers[index-1]:null;return Object.assign({},q,{title:q.branches&&prior!==null?(q.branches[String(prior)]||q.title):q.title});}
const reactions={afk:'你的镜头切到观战席，接下来由你决定这局怎么演。',int:'上一单已经送达，导播开始等你的下一次发车。',collector:'第五把收集者已在计划里，下一波还得看阵容。',protect:'你把队友留在镜头里，接下来看看这份售后怎么做。',heal:'桥头医务室已经开门，下一波挂号队伍也到了。',explain:'复活倒计时在走，你的讲解刚刚开始。',blame:'锅还在空中，下一幕先看看谁来接。',chaos:'节目效果已到账，故事还有下一幕。',plan:'计划先写在这里，接下来看看现场听不听安排。',engage:'车已经开了，接下来看乘客有没有跟上。',reset:'上一段剧本已翻篇，新的一幕还等你接梗。',laugh:'笑容先记一段，接下来手也要跟上。',calm:'你把庆祝留到了后面，先把眼前的对局打完。',spin:'抗压拉扯已经开始，下一步看看有没有反打空间。',stasis:'金身时机已经记下，结束之后还得接着操作。',flash:'闪现交了，接下来先把走位和退路找回来。',vision:'你先要信息，再决定下一步怎么打。'};
function context(s,data,index=s.index){const q=questionAt(s,data,index);if(q.theme!=='lol'||q.stage===0)return null;const previous=data.questions.find(p=>p.id===s.deck[index-1].id),o=previous.options.find(o=>o.id===s.answers[index-1]);return o?{chapter:q.chapterName,stage:q.stage,previousChoice:o.text,previousScene:previous.scene,reaction:reactions[o.behavior]||'上一个反应已经记下，同一场对局继续往下演。'}:null;}
const teamScripts={
 range:['上路卡位：把对手留在输出射程里。','打野盯人：绕后的人先报位置。','中路消耗：命中一轮再决定进退。','下路拉扯：边走边打，别只顾着后退。','辅助接应：控制留给贴脸的那个人。'],
 blame:['上路复盘：先说线权，再看有没有支援。','打野报点：刷野路线和到场时间说清楚。','中路看图：先确认信息，再问队友在哪。','下路回放：谁先吃控，拉进度条再说。','辅助提醒：复活时间和技能比问号更有用。'],
 economy:['上路承压：先站住，再给四个输出腾空间。','野区控图：该吃资源时吃，该到场时到。','中路游走：推完线再走，别两头都漏。','下路收尾：残血可以收，前排别硬穿。','辅助售后：全队唯一还看血条的人。'],
 chaos:['上路独演：先把边线变成个人舞台。','打野发车：路线直达下一段集锦。','中路配乐：这一波自带主角 BGM。','下路压轴：高光和灰屏只隔一帧。','辅助验票：上车前请签字。'],
 engage:['上路顶门：把第一波技能收下。','打野发车：开之前先数一遍乘客。','中路接戏：控制留给关键那个人。','下路输出：司机说到站再下车。','辅助导航：负责把人齐这件事讲明白。'],
 protect:['上路挡风：四个输出的移动掩体。','打野保安：巡逻到后排就上班。','中路调度：让技能替队友争取时间。','下路患者：请在医务室射程内营业。','辅助主治：这家没你真得关门。'],
 basic:['上路动作指导：细节交给手，不交给嘴。','打野解说：先把路线走成一个几何题。','中路编导：等到技能窗口再拍。','下路主演：金色的雨要自己走位接。','辅助控场：让高光背后有人接应。'],
 plan:['上路带线：看完小地图再过河。','打野路线：第四条边还没讲完。','中路恒温：今天几度由这里决定。','下路输出：等关键装备成型再接硬仗。','辅助复盘：把五个人留在同一张图上。'],
 retreat:['上路安全员：撤退也要留出通道。','打野巡场：先看地图再问队友呢。','中路观察：等对手把按钮按完。','下路远程：在安全感边缘输出。','辅助接人：回来就有口热奶。'],
 reset:['上路续集：这一条线还没演完。','打野刷新：新路线下一局见。','中路转场：重开也要记得带队友。','下路重拍：镜头先别删。','辅助留人：说好最后一把，又齐了。']};
function linkTeam(team,augment,theme){const lines=theme==='basket'?['控卫串联：先让队友都能接到球。','分卫接火：有机会就投，没机会先传。','侧翼跑动：把这一段名场面接起来。','篮下协作：卡好位置，给队友留空间。','中锋护框：篮板和回防都得有人管。']:theme==='abstract'?['发言人开场：把五个人的故事讲清楚。','行动派开拍：先完成最容易的一小段。','军师编排：好点子也要有人把它做出来。','气氛组接梗：前奏一响，全队进入画面。','场控收尾：照顾边界，也别落下任何队友。']:(teamScripts[augment.kind]||teamScripts.chaos);return team.map(p=>Object.assign({},p,{teamLine:lines[p.slot]}));}
function buildTeam(vector,characters,identity,augment){
 let best=null;
 for(const myRole of identity.roles){
  let states=Array(32).fill(null);states[1<<myRole]={value:0,slots:Array(5).fill(null)};states[1<<myRole].slots[myRole]=identity;
  for(const p of characters.filter(p=>p.id!==identity.id)){
   const next=states.slice();for(let mask=0;mask<32;mask++){const prior=states[mask];if(!prior)continue;
    for(let role=0;role<5;role++){if(mask&(1<<role)||!p.roles.includes(role))continue;const match=similarity(vector,p.vector),affinity=p.roles[0]===role?12:p.roles.includes(role)?7:-18;const flavor=augment?augment.bias.reduce((s,w,i)=>s+w*(p.vector[i]-50)/10,0):0;const value=prior.value+match+affinity+flavor;
     const to=mask|(1<<role);if(!next[to]||value>next[to].value){const slots=prior.slots.slice();slots[role]=p;next[to]={value,slots};}}
   }states=next;
  }
  const full=states[31];if(full&&(!best||full.value>best.value))best=full;
 }
 if(!best)throw Error('角色池不足以组成五人队');return best.slots.map((p,i)=>Object.assign({},p,{slot:i,isYou:p.id===identity.id,match:p.match===undefined?similarity(vector,p.vector):p.match,naturalRole:p.roles.includes(i)}));
}

function squadError(ids,theme,data,free=false,partial=false){
 if(!Array.isArray(ids)||ids.length!==5)return '请选择五个位置';
 const chosen=ids.filter(Boolean);if(!partial&&chosen.length!==5)return '还没选满五个人';
 const people=[];for(let i=0;i<5;i++){if(!ids[i])continue;const p=enabledPeople(data,theme).find(p=>p.id===ids[i]);if(!p)return '只能选择当前主题的人物';if(people.includes(p.personId))return '同一个人不能重复出场';people.push(p.personId);if(!free&&!p.roles.includes(i))return '这个位置不合适，可开启自由整活';}return '';
}
function fillSquad(ids,theme,data,vector,free=false){
 const err=squadError(ids,theme,data,free,true);if(err)throw Error(err);
 const fixed=ids.map(id=>id?data.characters.find(p=>p.id===id):null),used=fixed.filter(Boolean).map(p=>p.personId);let mask=0;fixed.forEach((p,i)=>{if(p)mask|=1<<i;});
 let states=Array(32).fill(null);states[mask]={value:0,slots:fixed.slice()};
 for(const p of enabledPeople(data,theme).filter(p=>!used.includes(p.personId))){const next=states.slice();for(let m=0;m<32;m++){const prev=states[m];if(!prev)continue;for(let i=0;i<5;i++){if((m&(1<<i))||(!free&&!p.roles.includes(i)))continue;const val=prev.value+similarity(vector,p.vector)+(p.roles[0]===i?12:p.roles.includes(i)?7:-15),to=m|(1<<i);if(!next[to]||val>next[to].value){const slots=prev.slots.slice();slots[i]=p;next[to]={value:val,slots};}}}states=next;}
 if(!states[31])throw Error('当前选择无法补齐五个位置；请换人或开启自由整活');return states[31].slots.map(p=>p.id);
}
function customSquad(ids,theme,data,vector,identity,augment,free=false){
 const err=squadError(ids,theme,data,free);if(err)throw Error(err);
 return linkTeam(ids.map((id,slot)=>{const p=data.characters.find(p=>p.id===id);return Object.assign({},p,{slot,isYou:p.personId===identity.personId,match:similarity(vector,p.vector),naturalRole:p.roles.includes(slot),custom:true});}),augment,theme).map(p=>Object.assign({},p,{teamLine:(p.naturalRole?'':'跨位整活 / ')+(p.tags||[]).slice(0,2).join(' · ')+'。'+p.teamLine}));
}

const stories={
 jackeylove:['哥哥，这回向前一步走到了金色的雨。','在这条架空 S8 时间线，你化身阿水。最后一局的闪现没有换来灰屏，而是等到了四名队友同时到场。你找到侧面的空隙，输出、拉开、再次上前，把那个熟悉的“敢打”变成了所有人等着看的结局。','奖杯前大家又喊起哥哥。你笑着把四个人拉进合照：这次镜头里，一个队友都没少。'],
 rookie:['院长，这次把整个宇宙都救回来了。','你化身 Rookie，站进一场架空 S8 决赛。队友在语音里喊你，你把中路守成了全队的落脚点。最后一波控制接上，四个熟悉的身影一起向前，你的输出把最后一座基地打成了金色的雨。','你抱着奖杯，眼泪先于采访回答。观众喊着肉鸡，队友说今天院长终于可以下班了。'],
 dailanzi:['评论区还没开，你的平行宇宙已经有了开场白。','你化身带篮子，带着四位风格完全不同的队友开了一场平行宇宙直播。刀哥带了好果汁，峰哥讲起路上的故事，台下刚有点冷场，你用一句带文学把所有人拉回同一段里。','散场后，最热的一条弹幕不是谁赢了，而是“这五个人怎么凑一起的”。你把它置顶：下一期，还得人齐。'],
 xiaoxiao:['双声道里，终于播到了冠军谢幕。','你化身笑笑，和西卡坐在平行决赛的解说席。开场的笑声被你们接成一句句简明的提醒。最后一波五个人齐了，基地倒下，你们一边笑一边把每个队友的名字喊出来。','这个宇宙的冠军回放有两个声道：一个记住操作，一个记住大家为什么一起笑。'],
 xika:['搭档那句话，被你接成了整个宇宙的片尾。','你化身西卡，和笑笑主持一场平行宇宙冠军之夜。有人讲快了，你补一句；有人漏了细节，你再讲清一遍。最后一波打完，直播间的笑声和现场的金色纸片一起落下。','冠军采访结束，你还在替这局接尾句：先别关，五个人的合照还没拍。'],
 uzi:['平行 S8，轮到你改写结局。','在这条架空时间线，你变成了污渍。决胜局，对面的飞科锁下加里奥，镜头里所有人都以为这又是熟悉的剧本。你却在最后一波侧身躲开控制，和四位队友一起战胜 Faker，把输出打到了结算页面。','金色的雨落下。你抱着奖杯泪流满面，全场高喊“世界第一 ADC”。主持人还在问“历史第一 ADC”，你已经把问题推进到“英雄联盟的 GOAT”。收集者不是决定，敢不敢接下这场比赛才是。'],
 xiaohu:['这个宇宙，没有不属于你的季节。','你变成了销户，赛场的日历被你改成了“春一月”到“春十二月”。总决赛打到最后一局，你把边线、团战与笑容一起拉满。','奖杯旁边多了一块恒温器：全宇宙的春天，今天由中路负责。'],
 dasima:['从讲解席，走到冠军颁奖台。','你变成了大司马。架空决赛里，所有人还在质疑你的路线，你已经画出了第三条“正方形打野”轨迹。最后一波不是嘴上有说法，是地图真的照着你的说法走。','奖杯被你端成一件教学道具。冠军公开课第一句话：先别急，这波我慢慢讲。'],
 theshy:['上路这条线，通向另一个结局。','你化身 TheShy，在架空决赛把一条边线打成了自己的独立宇宙。对手终于凑齐五个人来围你，你的队友刚好把另一边的主场拆完。','赛后大家讨论阵型，你在战术板上画了一条线：这里，也是一种答案。'],
 faker:['这一次，时间站在你这一边。','你化身飞科。平行决赛进入最安静的十秒，你等到所有技能交错的缝隙，再把那个属于自己的窗口按了下去。','第五次、第六次都不再是问题。这个宇宙的传奇，是把每一个小回合认真打完。'],
 lebron:['勒邦詹氏，膝盖先于战术板反应。','平行总决赛最后一攻，你变成了勒邦詹氏。漏判出现，全场进入表情加载页，你用一个跪地默剧把节目效果拉满。随后你站起来，追帽、推进、压哨出手一气呵成。','球进灯亮。这个宇宙的“虎扑式”搞笑评分写着：10 分，建议把膝盖也算进首发。你拿走的是这条时间线的 GOAT 剧本。'],
 curry:['停车场，正式进入你的射程表。','你变成了库里。平行总决赛的三分线被搬到停车场，大家还在找停车位，你已经借掩护转身出手。篮球在空中待得像一趟跨省快递。','球落网，晚安手势安排上。这个宇宙规定：只要你站得稳，想象力就有出手权。'],
 kobe:['凌晨的第一盏灯，由你点亮。','你化身科比。平行总决赛最后一节，你把练过无数遍的动作放进那个最需要答案的回合。全场的声音很大，你听见的只有脚步和球落网。','镜头切到空荡的训练馆：这里，早就为这个结局留过灯。'],
 jokic:['马儿没来，但传球已经到了。','你化身约老师。平行总决赛开打前，大家发现战术板背面是一张木马旋转图。第三节开始，对手才意识到每个人都被你转到了正确的位置。','你拿着奖杯问能不能早点回去。这个宇宙的中锋，把轻描淡写打成了史诗。'],
 fengge:['你去过的地方，地图还没来得及加载。','你变成了峰哥，揣着一张平行宇宙通行证出发。路边一间小卖部卖的是“如果当年”，你没急着买，而是拉老板聊完了另一个人生。','最后你带回来五个人和一大串故事。宇宙没被你讲明白，但你的这一集已经够好看。'],
 huge:['来，整个宇宙先别关。','你变成了虎哥。平行东北的路灯突然集体熄灭，你一抬手，现场五个人自带开机音效。围观群众还没弄清第一幕，第二幕已经顺着街口开过去了。','城市把“节目效果维护员”奖章发给你。你问：奖章能不能再配一瓶好果汁？'],
 daoge:['好果汁，这回送到了银河边上。','你变成了刀哥。一封星际补给单把你带到银河边，你发现全宇宙都在排队等下一段名场面。你把好果汁放上桌，先把五个队友招呼齐。','这场没有既定台词，只有现场反应。你的平行身份，是让离谱故事继续发生的人。'],
 geyou:['你没拯救宇宙，你让它坐下休息了。','你变成了葛优。平行世界不停催进度，所有人都在找下一场大事。你先在沙发上挪出四个位置，把队友一个个招呼坐下。','宇宙最后没爆炸。它只是承认：有些重要的事，要坐稳了才能想明白。']
};
function narrative(identity,theme,profile,series='all',augment=null){
 if(Array.isArray(identity.parallelStory)&&identity.parallelStory.length===3)return identity.parallelStory.slice();
 if(theme==='lol'&&(augment&&augment.id)==='double-laugh')return [`${identity.nickname||identity.name}，把第二段笑留给金色的雨。`,'在这条架空时间线，你在开局前忍住了第一段笑。领先以后，队友已经准备庆祝，你却把手重新放回键盘：这次先把对局打完。决胜团结束，基地终于倒下，导播才切到你的笑脸。','第一段是开心，第二段是终于赢了。这个平行宇宙的表情包，连同奖杯一起由你签收。'];
 if(theme==='lol'&&(augment&&augment.id)==='tes-top')return [`${identity.nickname||identity.name}，这回陀螺转出了反打角度。`,'在这条架空时间线，你们连着两波被压在塔前，弹幕里又飘起陀螺梗。你没有再抢着接第三波，而是和四位队友等到对面的开团技能交空，再从侧面一起打回去。','赛后梗图还在，但这次的结尾多了一段反打集锦。你把图存进群里：能笑，也能把下一波打明白。'];
 if(theme==='lol'&&series==='hex'){
  if(identity.personId==='uzi')return ['平行 S8，嚎哭深渊也能下起金色的雨。','在这条架空时间线，S8 决赛开在海克斯大乱斗的桥上。你变成污渍，对面的飞科又锁下加里奥。全场以为结局早已写好，你却用一波天赋联动和极限走位，把输出打到了结算页。','金色的雨落下。历史第一 ADC 只是起点，这个宇宙的观众把英雄联盟 GOAT 的剧本交给了你。收集者先收好，奖杯也别落下。'];
  if(identity.personId==='dasima')return ['这座桥，终于听懂了你的说法。','你化身大司马，走进一场架空海克斯冠军赛。随机给出的天赋看起来不搭，你边讲边把它连成一套“正方形大乱斗”。全队从一脸疑惑，打到一起点头。','最后一波结束，你端着奖杯继续讲：先别急，这次真的不是失误，是教材。冠军席，被你办成了一间公开课堂。'];
  if(identity.personId==='xiaohu')return ['嚎哭深渊，今天全桥入春。','你化身销户，进入一条只过春天的海克斯时间线。桥上冰雪还没化，天赋组合已经被你运营到舒服的位置。决胜团开打，所有人终于明白谁在掌握季节。','这个宇宙的奖杯旁多了一台恒温器。不是每年春天很强，是今天由你宣布春天。'];
  return [identity.name+'，这一座桥由你改写。','你化身'+identity.name+'，站上平行宇宙的海克斯大乱斗冠军桥。随机天赋没有给你标准答案，你用'+profile.name+'的反应，把一次普通抽签变成了自己的打法。'+(augment?'这一局，'+augment.name+'也写进了你的名场面。':''),'对手记住的也许是连招，队友记住的是这一局有人敢把可能性试出来。奖杯旁边，还有一枚属于这个宇宙的 GOAT 彩蛋。'];
 }
 if(theme==='abstract'&&identity.personId==='shake-director')return ['前奏一响，另一个你已经站到镜头中间。','在这个虚构的平行宇宙，你成了摇摆导演。原本只想拍十秒，四位队友一到场，群舞、翻唱和笑场一起上线。你把最像自己的那一段留下，第一次用自己的节奏被大家记住。','成片不必全程整齐。有人记得舞步，有人记得笑声，这期终于有了你自己的味道。'];
 if(theme==='abstract'&&identity.personId==='liziqi')return ['慢一点，普通日常也有自己的主角镜头。','在这条架空时间线，你化身李子柒，和四位搭档把一件普通手作拍成了温柔的小故事。你没有急着追下一个热点，而是把材料、过程和做完后的笑容都留下。','视频有自己的呼吸，更新也有自己的节奏。这个宇宙的专属海克斯，是认真生活时一点点积累的光。'];
 if(theme==='basket'&&identity.personId==='wemby')return ['文班长臂服务区，今天正式营业。','平行总决赛里，你化身文班亚马。对手还在寻找上篮角度，你已经和四位队友把篮下照顾明白。一次干净封盖之后，你没有忙着庆祝，转身就把球传向跑起来的队友。','外星人梗可以接，位置还得认真站。这个宇宙的冠军合照里，五个人都在你的服务范围。'];
 if(theme==='basket'&&identity.personId==='edwards')return ['华子准备起飞，回防也在飞行计划里。','平行总决赛最后一节，你化身华子。队友传来一个舒服的球，你抓住合适机会完成上篮，笑着和传球的人击掌。镜头想留住你的庆祝，你已经回到防守的位置。','篮球梦之队把高光留给你，也把下一球继续交给你。这场比赛的节目效果，有冲劲，也有靠谱的下一步。'];
 if(theme==='basket'&&identity.roleType==='commentator')return [identity.name+'，这场比赛由你来讲。','你化身'+identity.name+'，坐进平行宇宙的解说席。朋友们在场上拼出一个精彩回合，你把前因后果讲成大家都听得懂的故事。暂停时球员喝水，你还在认真接住观众的问题。','五人队采用本作娱乐角色设定；这里的你是解说员，没有虚构球员履历。'];
 const own=stories[identity.personId];if(own)return own;const u=identity.universe;if(u)return [(identity.nickname||identity.name)+'，'+u.title+'正式上岗。',u.arrival+' 这条时间线交给你的任务是：'+u.mission,u.passive+' 队友给你的评价是：'+u.teamHook];return theme==='lol'?[`${identity.name}，这次由你接下决胜局。`,`你化身${identity.name}，走进一条结局尚未写下的平行赛道。对手准备好了熟悉的套路，你用${profile.name}的打法把这一局带到了新的节奏。`,'奖杯不是剧本的终点。五个人愿意再开一局，才是这个宇宙最好的彩蛋。']:theme==='basket'?[`${identity.name}，今天的名场面由你签收。`,`你化身${identity.name}。平行总决赛把所有戏剧性都留到了末节，你把熟悉的动作和没试过的选择拼成了自己的答案。`,'这个宇宙的虎扑式搞笑评分给出满分：有人负责数据，有人负责让整场值得重看。']:[`${identity.name}，你在另一个宇宙上线了。`,`你化身${identity.name}。普通的一天被平行宇宙拧开了一个口子，你用${profile.name}的方式，把五个看似不搭的人放进同一段故事。`,'故事没有标准答案。能把自己的那一集过得有声有色，也是一种隐藏天赋。'];}
function analyze(session,data){
 const vector=score(session,data),pool=data.characters.filter(p=>p.theme===session.theme),ranked=rankPeople(session,data,vector);
 const identity=ranked[0],code=[0,1,2].map(i=>vector[i]>=50?'1':'0').join('');let profile=data.profiles.find(p=>p.id===data.familyCodes[code]);
 if(session.theme==='lol'){const hi=vector.indexOf(Math.max(...vector));profile=Object.assign({},profile,{name:['上头编剧','金币合伙人','雪球发车人','全队保护伞','基本功信徒','桥上运营师'][hi]});}
 const recommendations=recommend(session,data,vector,identity),augment=recommendations[0],rows=selections(session,data);
 const evidence=dimsFor(session.theme).map((dim,di)=>{const choices=[].concat(...rows.map(({q,o})=>{if(session.theme!=='lol'&&q.dim!==dim)return [];return [{id:q.id,scene:q.scene,title:q.title,choice:o.text,value:session.theme==='lol'?o.signals[dim]:(o.value-1)/3*100}];}));choices.sort((a,b)=>Math.abs(b.value-50)-Math.abs(a.value-50));return Object.assign({dim,coordinate:vector[di]},choices[0]);});
 const bond=recommendations.find(a=>(a.signatureFor||[]).includes(identity.personId))||null;
 return {inherentCards:(identity.signaturePerks||[]).map(id=>data.augments[session.theme].find(a=>a.id===id)).filter(Boolean),triggeredPersonal:recommendations.filter(a=>a.exclusive&&a.personLink),vector,identity,ranked,profile,augment,recommendations,bond,team:linkTeam(buildTeam(vector,ranked,identity,augment),augment,session.theme),story:narrative(identity,session.theme,profile,session.series,augment),signature:Object.entries(rows.reduce((sum,{o})=>{sum[o.behavior]=(sum[o.behavior]||0)+1;return sum;},{})).sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0])).slice(0,3).map(([id,count])=>({id,count,label:data.behaviorLabels[id]})),evidence,coverage:dimsFor(session.theme).map(dim=>session.theme==='lol'?session.count:rows.filter(({q})=>q.dim===dim).length)};
}
function makeSquadName(theme,team,previous='',rng=random){
 if(!Array.isArray(team)||team.length!==5||new Set(team.map(p=>p.personId)).size!==5)throw Error('五位不同的队友到齐后才能起名');
 const heads={lol:['全员收集者','五楼拒绝补位','网费不够但嘴硬','最后一把不散伙','复活期间还在讲课','金色的雨先分期','今天全队都在解释','先别急着说稳了'],basket:['凌晨四点还在打铁','膝盖管理局','最后一投谁都想要','球没进先怪风','篮板全靠缘分','停车场射程施工中','赛后采访没人认输','全队申请暂停'],abstract:['吃饱喝足再上头','全员学士帽Plus','麦克风无人刹车','路费还没凑齐','先别急着解释','饭点比闹钟还准','五个群聊管理员','正片没开始先笑场']};
 const tails={lol:['包夜互助会','峡谷临时夺冠办','五黑售后服务部','没有前排股份公司','不愿透露战绩的五位市民','宇宙级复盘研究所'],basket:['篮球研究所','野球场团建小队','赛后嘴硬中心','夕阳红冠军分部','全员回防倡议会','篮筐维修筹备组'],abstract:['互联网临时工','宇宙级气氛组','节目效果售后部','饭后发布会筹备组','平行宇宙嘴替联盟','未获通知也要返场团']};
 if(!heads[theme])throw Error('不支持的战队主题');let title='',hi=0,ti=0;for(let k=0;k<6;k++){hi=Math.min(heads[theme].length-1,Math.floor(rng()*heads[theme].length));ti=Math.min(tails[theme].length-1,Math.floor(rng()*tails[theme].length));title=heads[theme][hi]+' · '+tails[theme][ti];if(title!==previous)break;}if(title===previous)title=heads[theme][(hi+1)%heads[theme].length]+' · '+tails[theme][ti];
 const motto={lol:'上不上分先不说，今晚五个人必须整整齐齐。',basket:'投进算大家的，打铁就当替篮筐做体检。',abstract:'节目可以随缘，人和饭必须按时到齐。'}[theme];
 return {title,motto,ids:team.map(p=>p.id),theme};
}
return {makeSquadName,enabledPeople,enabledCards,searchPeople,resolvePerson,applyExposure,exposureSample,dimIds,lolDimIds,dimsFor,shuffle,draw,valid,score,similarity,analyze,buildTeam,narrative,recommend,context,selections,questionAt,rankPeople,behaviorFit,artLayout,recordAnswer,squadError,fillSquad,customSquad};
});

(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.ShenrenV13Engine=factory();})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const dimIds=['social','explore','empathy','action','order','express'];
const lolDimIds=['tilt','greed','risk','team','craft','plan'];
const dimsFor=theme=>theme==='lol'?lolDimIds:dimIds;
function random(){if(typeof crypto!=='undefined'&&crypto.getRandomValues){const a=new Uint32Array(1);crypto.getRandomValues(a);return a[0]/4294967296;}return Math.random();}
function shuffle(list,rng=random){const a=list.slice();for(let i=a.length-1;i>0;i--){const j=Math.floor(rng()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
// One layout feeds both HTML and exported Canvas: the real icons and copy counts match.
function artLayout(a){
 const icons=a.visual?a.visual.icons:[],n=icons.length,l=a.visual?a.visual.layout:null;
 const points=n===1?[[.19,.19,.62,0]]:l==='grid'?icons.map((_,i)=>[.02+(i%3)*.33,.17+Math.floor(i/3)*.34,.30,0]):l==='square'?[[.07,.07,.36,-8],[.57,.07,.36,8],[.07,.57,.36,8],[.57,.57,.36,-8]]:l==='ring'?icons.map((_,i)=>{const t=-Math.PI/2+i*Math.PI*2/n;return [.33+Math.cos(t)*.28,.33+Math.sin(t)*.28,.34,i*15-15];}):l==='row'?icons.map((_,i)=>[.03+i*(.94-.40)/Math.max(1,n-1),.30+(i%2)*.1,.40,(i-(n-1)/2)*10]):n===2?[[.04,.28,.47,-15],[.49,.19,.47,15]]:n===3?[[.03,.35,.47,-17],[.51,.35,.47,17],[.27,.07,.47,0]]:n===4?[[.05,.14,.4,-15],[.55,.14,.4,15],[.05,.55,.4,-8],[.55,.55,.4,8]]:[[.03,.14,.37,-17],[.23,.04,.37,-8],[.43,.04,.37,8],[.62,.14,.37,17],[.29,.53,.43,0]];
 return icons.map((icon,i)=>({icon,x:points[i][0],y:points[i][1],size:points[i][2],rotation:points[i][3]}));
}
function enabledPeople(data,theme=null){return data.characters.filter(p=>p.enabled!==false&&(!theme||p.theme===theme)).sort((a,b)=>(a.rosterOrder||0)-(b.rosterOrder||0));}
function cardOwners(card){return Array.isArray(card.owners)?card.owners.slice():Array.isArray(card.signatureFor)&&card.signatureFor.length?card.signatureFor.slice():card.owner?[card.owner]:[];}
function enabledCards(data,theme=null){return [].concat(...Object.keys(data.augments).filter(t=>!theme||t===theme).map(t=>data.augments[t])).filter(a=>a.enabled!==false);}
function searchPeople(data,theme,query=''){const q=query.trim().toLowerCase();return enabledPeople(data,theme==='all'?null:theme).filter(p=>[p.name,p.nickname].concat(p.aliases||[],p.tags||[]).join(' ').toLowerCase().includes(q));}
function resolvePerson(data,value){const q=String(value).toLowerCase();return data.characters.find(p=>p.id===value||p.personId===value||(p.aliases||[p.name,p.nickname]).some(a=>a&&a.toLowerCase()===q))||null;}
function applyExposure(candidates,policy={}){
 if(!candidates.length)return [];
 const top=Math.max(...candidates.map(p=>p.rawMatch)),near=Math.max(0,Math.min(8,policy.nearTop===undefined?5:policy.nearTop)),bonus=Math.max(0,Math.min(6,policy.maxBonus===undefined?4:policy.maxBonus)),starNear=Math.max(0,Math.min(15,policy.flagshipNearTop===undefined?12:policy.flagshipNearTop)),starBonus=Math.max(0,Math.min(12,policy.flagshipBonus===undefined?9:policy.flagshipBonus));
 return candidates.map(p=>{const flagship=p.tier==='flagship',featured=p.tier==='featured',gap=top-p.rawMatch,add=flagship&&gap<=starNear?starBonus:featured&&gap<=near?bonus:0;return Object.assign({},p,{match:p.rawMatch,editorialBonus:add});}).sort((a,b)=>(b.rawMatch+b.editorialBonus)-(a.rawMatch+a.editorialBonus)||b.rawMatch-a.rawMatch||a.id.localeCompare(b.id));
}
function exposureSample(data,theme,n=1,rng=random){const pool=enabledPeople(data,theme).slice(),out=[];while(pool.length&&out.length<n){let x=rng()*pool.reduce((sum,p)=>sum+p.exposureWeight,0),i=0;for(;i<pool.length-1;i++){x-=pool[i].exposureWeight;if(x<0)break;}out.push(pool.splice(i,1)[0]);}return out;}
function draw(data,theme,count,previousFirst=null,rng=random,series='all'){
 if(!data.themes.some(t=>t.id===theme)||!data.modes.includes(count))throw Error('不支持的主题或题量');
 if(theme==='lol'&&!['all','hex','rift'].includes(series))throw Error('不支持的联盟系列');
 let chosen=[];
 if(theme==='lol'){
  const bank=data.questions.filter(q=>q.enabled!==false&&q.theme===theme&&(series==='all'||q.series===series));
  const chapters=shuffle([...new Set(bank.map(q=>q.series+':'+q.chapter))],rng);
  if(chapters.length<count/4)throw Error('章节题库不足');
  if(bank.some(q=>q.id===previousFirst&&chapters[0]===q.series+':'+q.chapter))[chapters[0],chapters[1]]=[chapters[1],chapters[0]];
  chosen=[].concat(...chapters.slice(0,count/4).map(c=>bank.filter(q=>q.series+':'+q.chapter===c).sort((a,b)=>a.stage-b.stage)));
 }else{
  const extra=new Set(shuffle(dimIds,rng).slice(0,count%6));
  dimIds.forEach(dim=>{const bank=data.questions.filter(q=>q.enabled!==false&&q.theme===theme&&q.dim===dim),n=Math.floor(count/6)+(extra.has(dim)?1:0);if(bank.length<n)throw Error('题库不足');chosen.push(...shuffle(bank,rng).slice(0,n));});
  chosen=shuffle(chosen,rng);if(chosen[0].id===previousFirst)[chosen[0],chosen[1]]=[chosen[1],chosen[0]];
 }
 return {version:data.version,theme,series:theme==='lol'?series:'all',count,deck:chosen.map(q=>({id:q.id,order:shuffle(q.options.map(o=>o.id),rng)})),answers:Array(count).fill(null),index:0,phase:'quiz',date:new Date().toISOString()};
}
function valid(s,data,complete=false){
 if(!s||s.version!==data.version||!data.themes.some(t=>t.id===s.theme)||!data.modes.includes(s.count)||!Array.isArray(s.deck)||s.deck.length!==s.count||!Array.isArray(s.answers)||s.answers.length!==s.count||!Number.isInteger(s.index)||s.index<0||s.index>=s.count)return false;
 if(s.theme==='lol'&&!['hex','rift','all'].includes(s.series))return false;
 if(new Set(s.deck.map(d=>d&&d.id)).size!==s.count)return false;
 const questions=s.deck.map(d=>data.questions.find(q=>q.id===(d&&d.id)&&q.theme===s.theme&&(s.theme!=='lol'||s.series==='all'||q.series===s.series)));
 if(questions.some(q=>!q))return false;
 if(s.theme==='lol'){
  for(let i=0;i<questions.length;i+=4){const group=questions.slice(i,i+4);if(group.some((q,j)=>q.chapter!==group[0].chapter||q.series!==group[0].series||q.stage!==j))return false;}
 }else if(!dimIds.every(dim=>questions.some(q=>q.dim===dim)))return false;
 return s.deck.every((d,i)=>Array.isArray(d.order)&&d.order.length===4&&new Set(d.order).size===4&&d.order.every(v=>questions[i].options.some(o=>o.id===v))&&((!complete&&s.answers[i]===null)||questions[i].options.some(o=>o.id===s.answers[i])));
}
// Commit against the question that was actually displayed; stale taps cannot answer another question.
function recordAnswer(s,data,questionId,optionId){
 if(!valid(s,data)||s.phase!=='quiz'||s.deck[s.index].id!==questionId)throw Error('这道题已经切换，请重新选择');
 const q=data.questions.find(q=>q.id===questionId);
 if(!q.options.some(o=>o.id===optionId))throw Error('这个选项不存在');
 const next=Object.assign({},s,{answers:s.answers.slice()});next.answers[s.index]=optionId;
 const complete=s.index===s.count-1;
 if(complete)next.phase='complete';else next.index=s.index+1;
 return {session:next,complete};
}
function selections(s,data){return s.deck.map((d,i)=>{const q=data.questions.find(q=>q.id===d.id);return {q,o:q.options.find(o=>o.id===s.answers[i])};});}
function score(s,data){
 if(!valid(s,data,true))throw Error('请完成本轮全部题目');const rows=selections(s,data);
 return dimsFor(s.theme).map(dim=>{if(s.theme==='lol'){const total=rows.reduce((sum,{o})=>sum+o.signals[dim],0),neutral=rows.reduce((sum,{q})=>sum+q.options.reduce((n,o)=>n+o.signals[dim],0)/4,0),lo=rows.reduce((sum,{q})=>sum+Math.min(...q.options.map(o=>o.signals[dim])),0),hi=rows.reduce((sum,{q})=>sum+Math.max(...q.options.map(o=>o.signals[dim])),0),delta=total-neutral;return Math.max(0,Math.min(100,Math.round(50+50*delta/Math.max(1,delta>=0?hi-neutral:neutral-lo))));}const values=rows.filter(({q})=>q.dim===dim).map(({o})=>o.value);return Math.round((values.reduce((a,b)=>a+b,0)/values.length-1)/3*100);});
}
function similarity(a,b){return Math.round(100*(1-a.reduce((s,v,i)=>s+Math.abs(v-b[i]),0)/600));}
function responseWeight(q){return q.importance||1;}
function behaviorFit(rows,weights={}){const total=rows.reduce((sum,{q})=>sum+responseWeight(q),0);return total?100*rows.reduce((sum,{q,o})=>sum+(weights[o.behavior]||0)*responseWeight(q),0)/(5*total):0;}
function cardEvidence(rows,card){return rows.map(({q,o},index)=>({id:q.id,scene:q.scene,choice:o.text,behavior:o.behavior,strength:((card.behaviorWeights&&card.behaviorWeights[o.behavior])||0)*responseWeight(q),index})).filter(e=>e.strength>0&&(!card.evidenceQuestionIds||!card.evidenceQuestionIds.length||card.evidenceQuestionIds.includes(e.id))&&(!Array.isArray(card.answerEvidence)||card.answerEvidence.some(a=>a.questionId===e.id&&a.optionId===rows[e.index].o.id))).sort((a,b)=>b.strength-a.strength||a.index-b.index);}
function rankPeople(s,data,vector){const rows=selections(s,data);return applyExposure(enabledPeople(data,s.theme).map(p=>{const v=similarity(vector,p.vector),b=behaviorFit(rows,p.behaviorWeights),scene=100*rows.reduce((sum,{q,o})=>sum+(p.optionAffinities?((p.optionAffinities[q.id]&&p.optionAffinities[q.id][String(o.id)])||0):((p.answerAffinities&&p.answerAffinities[q.id]&&p.answerAffinities[q.id][o.behavior])||0)),0)/(5*rows.length);return Object.assign({},p,{rawMatch:Math.round(.4*v+.35*b+.25*scene),matchBreakdown:{vector:v,behavior:b,scene}});}),data.rosterPolicy);}

function recommend(s,data,vector=score(s,data),identity=null){
 const rows=selections(s,data);if(!identity)identity=rankPeople(s,data,vector)[0];
 return enabledCards(data,s.theme).filter(a=>a.activationMode!=='identity').filter(a=>!a.personOnly||cardOwners(a).includes(identity.personId)).filter(a=>!(a.requires||[]).length||(a.requires||[]).some(b=>rows.some(({o})=>o.behavior===b))).map(a=>{
  const v=a.vector||a.bias.map(n=>Math.max(0,Math.min(100,50+n*40))),evidence=cardEvidence(rows,a);
  const behavior=behaviorFit(rows,a.behaviorWeights),bonus=(cardOwners(a).includes(identity.personId)||(a.affinities||[]).includes(identity.personId))?5:0;
  const match=Math.round(.42*similarity(vector,v)+.53*behavior+bonus);
  return Object.assign({},a,{match,evidence:evidence.slice(0,2),hitCount:evidence.length,personLink:bonus>0});
 }).filter(a=>a.hitCount>0).sort((a,b)=>Number(Boolean(b.exclusive&&b.personLink))-Number(Boolean(a.exclusive&&a.personLink))||b.match-a.match||b.hitCount-a.hitCount||a.id.localeCompare(b.id));
}
function questionAt(s,data,index=s.index){const q=data.questions.find(q=>q.id===(s.deck[index]&&s.deck[index].id));if(!q)return null;const prior=index>0?s.answers[index-1]:null;return Object.assign({},q,{title:q.branches&&prior!==null?(q.branches[String(prior)]||q.title):q.title});}
const reactions={afk:'你的镜头切到观战席，接下来由你决定这局怎么演。',int:'上一单已经送达，导播开始等你的下一次发车。',collector:'第五把收集者已在计划里，下一波还得看阵容。',protect:'你把队友留在镜头里，接下来看看这份售后怎么做。',heal:'桥头医务室已经开门，下一波挂号队伍也到了。',explain:'复活倒计时在走，你的讲解刚刚开始。',blame:'锅还在空中，下一幕先看看谁来接。',chaos:'节目效果已到账，故事还有下一幕。',plan:'计划先写在这里，接下来看看现场听不听安排。',engage:'车已经开了，接下来看乘客有没有跟上。',reset:'上一段剧本已翻篇，新的一幕还等你接梗。',laugh:'笑容先记一段，接下来手也要跟上。',calm:'你把庆祝留到了后面，先把眼前的对局打完。',spin:'抗压拉扯已经开始，下一步看看有没有反打空间。',stasis:'金身时机已经记下，结束之后还得接着操作。',flash:'闪现交了，接下来先把走位和退路找回来。',vision:'你先要信息，再决定下一步怎么打。'};
function context(s,data,index=s.index){const q=questionAt(s,data,index);if(q.theme!=='lol'||q.stage===0)return null;const previous=data.questions.find(p=>p.id===s.deck[index-1].id),o=previous.options.find(o=>o.id===s.answers[index-1]);return o?{chapter:q.chapterName,stage:q.stage,previousChoice:o.text,previousScene:previous.scene,reaction:reactions[o.behavior]||'上一个反应已经记下，同一场对局继续往下演。'}:null;}
const teamScripts={
 range:['上路卡位：把对手留在输出射程里。','打野盯人：绕后的人先报位置。','中路消耗：命中一轮再决定进退。','下路拉扯：边走边打，别只顾着后退。','辅助接应：控制留给贴脸的那个人。'],
 blame:['上路复盘：先说线权，再看有没有支援。','打野报点：刷野路线和到场时间说清楚。','中路看图：先确认信息，再问队友在哪。','下路回放：谁先吃控，拉进度条再说。','辅助提醒：复活时间和技能比问号更有用。'],
 economy:['上路承压：先站住，再给四个输出腾空间。','野区控图：该吃资源时吃，该到场时到。','中路游走：推完线再走，别两头都漏。','下路收尾：残血可以收，前排别硬穿。','辅助售后：全队唯一还看血条的人。'],
 chaos:['上路独演：先把边线变成个人舞台。','打野发车：路线直达下一段集锦。','中路配乐：这一波自带主角 BGM。','下路压轴：高光和灰屏只隔一帧。','辅助验票：上车前请签字。'],
 engage:['上路顶门：把第一波技能收下。','打野发车：开之前先数一遍乘客。','中路接戏：控制留给关键那个人。','下路输出：司机说到站再下车。','辅助导航：负责把人齐这件事讲明白。'],
 protect:['上路挡风：四个输出的移动掩体。','打野保安：巡逻到后排就上班。','中路调度：让技能替队友争取时间。','下路患者：请在医务室射程内营业。','辅助主治：这家没你真得关门。'],
 basic:['上路动作指导：细节交给手，不交给嘴。','打野解说：先把路线走成一个几何题。','中路编导：等到技能窗口再拍。','下路主演：金色的雨要自己走位接。','辅助控场：让高光背后有人接应。'],
 plan:['上路带线：看完小地图再过河。','打野路线：第四条边还没讲完。','中路恒温：今天几度由这里决定。','下路输出：等关键装备成型再接硬仗。','辅助复盘：把五个人留在同一张图上。'],
 retreat:['上路安全员：撤退也要留出通道。','打野巡场：先看地图再问队友呢。','中路观察：等对手把按钮按完。','下路远程：在安全感边缘输出。','辅助接人：回来就有口热奶。'],
 reset:['上路续集：这一条线还没演完。','打野刷新：新路线下一局见。','中路转场：重开也要记得带队友。','下路重拍：镜头先别删。','辅助留人：说好最后一把，又齐了。']};
function linkTeam(team,augment,theme){const lines=theme==='basket'?['控卫串联：先让队友都能接到球。','分卫接火：有机会就投，没机会先传。','侧翼跑动：把这一段名场面接起来。','篮下协作：卡好位置，给队友留空间。','中锋护框：篮板和回防都得有人管。']:theme==='abstract'?['发言人开场：把五个人的故事讲清楚。','行动派开拍：先完成最容易的一小段。','军师编排：好点子也要有人把它做出来。','气氛组接梗：前奏一响，全队进入画面。','场控收尾：照顾边界，也别落下任何队友。']:(teamScripts[augment.kind]||teamScripts.chaos);return team.map(p=>Object.assign({},p,{teamLine:lines[p.slot]}));}
function buildTeam(vector,characters,identity,augment){
 let best=null;
 for(const myRole of identity.roles){
  let states=Array(32).fill(null);states[1<<myRole]={value:0,slots:Array(5).fill(null)};states[1<<myRole].slots[myRole]=identity;
  for(const p of characters.filter(p=>p.id!==identity.id)){
   const next=states.slice();for(let mask=0;mask<32;mask++){const prior=states[mask];if(!prior)continue;
    for(let role=0;role<5;role++){if(mask&(1<<role)||!p.roles.includes(role))continue;const match=similarity(vector,p.vector),affinity=p.roles[0]===role?12:p.roles.includes(role)?7:-18;const flavor=augment?augment.bias.reduce((s,w,i)=>s+w*(p.vector[i]-50)/10,0):0;const value=prior.value+match+affinity+flavor;
     const to=mask|(1<<role);if(!next[to]||value>next[to].value){const slots=prior.slots.slice();slots[role]=p;next[to]={value,slots};}}
   }states=next;
  }
  const full=states[31];if(full&&(!best||full.value>best.value))best=full;
 }
 if(!best)throw Error('角色池不足以组成五人队');return best.slots.map((p,i)=>Object.assign({},p,{slot:i,isYou:p.id===identity.id,match:p.match===undefined?similarity(vector,p.vector):p.match,naturalRole:p.roles.includes(i)}));
}

function squadError(ids,theme,data,free=false,partial=false){
 if(!Array.isArray(ids)||ids.length!==5)return '请选择五个位置';
 const chosen=ids.filter(Boolean);if(!partial&&chosen.length!==5)return '还没选满五个人';
 const people=[];for(let i=0;i<5;i++){if(!ids[i])continue;const p=enabledPeople(data,theme).find(p=>p.id===ids[i]);if(!p)return '只能选择当前主题的人物';if(people.includes(p.personId))return '同一个人不能重复出场';people.push(p.personId);if(!free&&!p.roles.includes(i))return '这个位置不合适，可开启自由整活';}return '';
}
function fillSquad(ids,theme,data,vector,free=false){
 const err=squadError(ids,theme,data,free,true);if(err)throw Error(err);
 const fixed=ids.map(id=>id?data.characters.find(p=>p.id===id):null),used=fixed.filter(Boolean).map(p=>p.personId);let mask=0;fixed.forEach((p,i)=>{if(p)mask|=1<<i;});
 let states=Array(32).fill(null);states[mask]={value:0,slots:fixed.slice()};
 for(const p of enabledPeople(data,theme).filter(p=>!used.includes(p.personId))){const next=states.slice();for(let m=0;m<32;m++){const prev=states[m];if(!prev)continue;for(let i=0;i<5;i++){if((m&(1<<i))||(!free&&!p.roles.includes(i)))continue;const val=prev.value+similarity(vector,p.vector)+(p.roles[0]===i?12:p.roles.includes(i)?7:-15),to=m|(1<<i);if(!next[to]||val>next[to].value){const slots=prev.slots.slice();slots[i]=p;next[to]={value:val,slots};}}}states=next;}
 if(!states[31])throw Error('当前选择无法补齐五个位置；请换人或开启自由整活');return states[31].slots.map(p=>p.id);
}
function customSquad(ids,theme,data,vector,identity,augment,free=false){
 const err=squadError(ids,theme,data,free);if(err)throw Error(err);
 return linkTeam(ids.map((id,slot)=>{const p=data.characters.find(p=>p.id===id);return Object.assign({},p,{slot,isYou:p.personId===identity.personId,match:similarity(vector,p.vector),naturalRole:p.roles.includes(slot),custom:true});}),augment,theme).map(p=>Object.assign({},p,{teamLine:(p.naturalRole?'':'跨位整活 / ')+(p.tags||[]).slice(0,2).join(' · ')+'。'+p.teamLine}));
}

const stories={
 jackeylove:['哥哥，这回向前一步走到了金色的雨。','在这条架空 S8 时间线，你化身阿水。最后一局的闪现没有换来灰屏，而是等到了四名队友同时到场。你找到侧面的空隙，输出、拉开、再次上前，把那个熟悉的“敢打”变成了所有人等着看的结局。','奖杯前大家又喊起哥哥。你笑着把四个人拉进合照：这次镜头里，一个队友都没少。'],
 rookie:['院长，这次把整个宇宙都救回来了。','你化身 Rookie，站进一场架空 S8 决赛。队友在语音里喊你，你把中路守成了全队的落脚点。最后一波控制接上，四个熟悉的身影一起向前，你的输出把最后一座基地打成了金色的雨。','你抱着奖杯，眼泪先于采访回答。观众喊着肉鸡，队友说今天院长终于可以下班了。'],
 dailanzi:['评论区还没开，你的平行宇宙已经有了开场白。','你化身带篮子，带着四位风格完全不同的队友开了一场平行宇宙直播。刀哥带了好果汁，峰哥讲起路上的故事，台下刚有点冷场，你用一句带文学把所有人拉回同一段里。','散场后，最热的一条弹幕不是谁赢了，而是“这五个人怎么凑一起的”。你把它置顶：下一期，还得人齐。'],
 xiaoxiao:['双声道里，终于播到了冠军谢幕。','你化身笑笑，和西卡坐在平行决赛的解说席。开场的笑声被你们接成一句句简明的提醒。最后一波五个人齐了，基地倒下，你们一边笑一边把每个队友的名字喊出来。','这个宇宙的冠军回放有两个声道：一个记住操作，一个记住大家为什么一起笑。'],
 xika:['搭档那句话，被你接成了整个宇宙的片尾。','你化身西卡，和笑笑主持一场平行宇宙冠军之夜。有人讲快了，你补一句；有人漏了细节，你再讲清一遍。最后一波打完，直播间的笑声和现场的金色纸片一起落下。','冠军采访结束，你还在替这局接尾句：先别关，五个人的合照还没拍。'],
 uzi:['平行 S8，轮到你改写结局。','在这条架空时间线，你变成了污渍。决胜局，对面的飞科锁下加里奥，镜头里所有人都以为这又是熟悉的剧本。你却在最后一波侧身躲开控制，和四位队友一起战胜 Faker，把输出打到了结算页面。','金色的雨落下。你抱着奖杯泪流满面，全场高喊“世界第一 ADC”。主持人还在问“历史第一 ADC”，你已经把问题推进到“英雄联盟的 GOAT”。收集者不是决定，敢不敢接下这场比赛才是。'],
 xiaohu:['这个宇宙，没有不属于你的季节。','你变成了销户，赛场的日历被你改成了“春一月”到“春十二月”。总决赛打到最后一局，你把边线、团战与笑容一起拉满。','奖杯旁边多了一块恒温器：全宇宙的春天，今天由中路负责。'],
 dasima:['从讲解席，走到冠军颁奖台。','你变成了大司马。架空决赛里，所有人还在质疑你的路线，你已经画出了第三条“正方形打野”轨迹。最后一波不是嘴上有说法，是地图真的照着你的说法走。','奖杯被你端成一件教学道具。冠军公开课第一句话：先别急，这波我慢慢讲。'],
 theshy:['上路这条线，通向另一个结局。','你化身 TheShy，在架空决赛把一条边线打成了自己的独立宇宙。对手终于凑齐五个人来围你，你的队友刚好把另一边的主场拆完。','赛后大家讨论阵型，你在战术板上画了一条线：这里，也是一种答案。'],
 faker:['这一次，时间站在你这一边。','你化身飞科。平行决赛进入最安静的十秒，你等到所有技能交错的缝隙，再把那个属于自己的窗口按了下去。','第五次、第六次都不再是问题。这个宇宙的传奇，是把每一个小回合认真打完。'],
 lebron:['勒邦詹氏，膝盖先于战术板反应。','平行总决赛最后一攻，你变成了勒邦詹氏。漏判出现，全场进入表情加载页，你用一个跪地默剧把节目效果拉满。随后你站起来，追帽、推进、压哨出手一气呵成。','球进灯亮。这个宇宙的“虎扑式”搞笑评分写着：10 分，建议把膝盖也算进首发。你拿走的是这条时间线的 GOAT 剧本。'],
 curry:['停车场，正式进入你的射程表。','你变成了库里。平行总决赛的三分线被搬到停车场，大家还在找停车位，你已经借掩护转身出手。篮球在空中待得像一趟跨省快递。','球落网，晚安手势安排上。这个宇宙规定：只要你站得稳，想象力就有出手权。'],
 kobe:['凌晨的第一盏灯，由你点亮。','你化身科比。平行总决赛最后一节，你把练过无数遍的动作放进那个最需要答案的回合。全场的声音很大，你听见的只有脚步和球落网。','镜头切到空荡的训练馆：这里，早就为这个结局留过灯。'],
 jokic:['马儿没来，但传球已经到了。','你化身约老师。平行总决赛开打前，大家发现战术板背面是一张木马旋转图。第三节开始，对手才意识到每个人都被你转到了正确的位置。','你拿着奖杯问能不能早点回去。这个宇宙的中锋，把轻描淡写打成了史诗。'],
 fengge:['你去过的地方，地图还没来得及加载。','你变成了峰哥，揣着一张平行宇宙通行证出发。路边一间小卖部卖的是“如果当年”，你没急着买，而是拉老板聊完了另一个人生。','最后你带回来五个人和一大串故事。宇宙没被你讲明白，但你的这一集已经够好看。'],
 huge:['来，整个宇宙先别关。','你变成了虎哥。平行东北的路灯突然集体熄灭，你一抬手，现场五个人自带开机音效。围观群众还没弄清第一幕，第二幕已经顺着街口开过去了。','城市把“节目效果维护员”奖章发给你。你问：奖章能不能再配一瓶好果汁？'],
 daoge:['好果汁，这回送到了银河边上。','你变成了刀哥。一封星际补给单把你带到银河边，你发现全宇宙都在排队等下一段名场面。你把好果汁放上桌，先把五个队友招呼齐。','这场没有既定台词，只有现场反应。你的平行身份，是让离谱故事继续发生的人。'],
 geyou:['你没拯救宇宙，你让它坐下休息了。','你变成了葛优。平行世界不停催进度，所有人都在找下一场大事。你先在沙发上挪出四个位置，把队友一个个招呼坐下。','宇宙最后没爆炸。它只是承认：有些重要的事，要坐稳了才能想明白。']
};
function narrative(identity,theme,profile,series='all',augment=null){
 if(Array.isArray(identity.parallelStory)&&identity.parallelStory.length===3)return identity.parallelStory.slice();
 if(theme==='lol'&&(augment&&augment.id)==='double-laugh')return [`${identity.nickname||identity.name}，把第二段笑留给金色的雨。`,'在这条架空时间线，你在开局前忍住了第一段笑。领先以后，队友已经准备庆祝，你却把手重新放回键盘：这次先把对局打完。决胜团结束，基地终于倒下，导播才切到你的笑脸。','第一段是开心，第二段是终于赢了。这个平行宇宙的表情包，连同奖杯一起由你签收。'];
 if(theme==='lol'&&(augment&&augment.id)==='tes-top')return [`${identity.nickname||identity.name}，这回陀螺转出了反打角度。`,'在这条架空时间线，你们连着两波被压在塔前，弹幕里又飘起陀螺梗。你没有再抢着接第三波，而是和四位队友等到对面的开团技能交空，再从侧面一起打回去。','赛后梗图还在，但这次的结尾多了一段反打集锦。你把图存进群里：能笑，也能把下一波打明白。'];
 if(theme==='lol'&&series==='hex'){
  if(identity.personId==='uzi')return ['平行 S8，嚎哭深渊也能下起金色的雨。','在这条架空时间线，S8 决赛开在海克斯大乱斗的桥上。你变成污渍，对面的飞科又锁下加里奥。全场以为结局早已写好，你却用一波天赋联动和极限走位，把输出打到了结算页。','金色的雨落下。历史第一 ADC 只是起点，这个宇宙的观众把英雄联盟 GOAT 的剧本交给了你。收集者先收好，奖杯也别落下。'];
  if(identity.personId==='dasima')return ['这座桥，终于听懂了你的说法。','你化身大司马，走进一场架空海克斯冠军赛。随机给出的天赋看起来不搭，你边讲边把它连成一套“正方形大乱斗”。全队从一脸疑惑，打到一起点头。','最后一波结束，你端着奖杯继续讲：先别急，这次真的不是失误，是教材。冠军席，被你办成了一间公开课堂。'];
  if(identity.personId==='xiaohu')return ['嚎哭深渊，今天全桥入春。','你化身销户，进入一条只过春天的海克斯时间线。桥上冰雪还没化，天赋组合已经被你运营到舒服的位置。决胜团开打，所有人终于明白谁在掌握季节。','这个宇宙的奖杯旁多了一台恒温器。不是每年春天很强，是今天由你宣布春天。'];
  return [identity.name+'，这一座桥由你改写。','你化身'+identity.name+'，站上平行宇宙的海克斯大乱斗冠军桥。随机天赋没有给你标准答案，你用'+profile.name+'的反应，把一次普通抽签变成了自己的打法。'+(augment?'这一局，'+augment.name+'也写进了你的名场面。':''),'对手记住的也许是连招，队友记住的是这一局有人敢把可能性试出来。奖杯旁边，还有一枚属于这个宇宙的 GOAT 彩蛋。'];
 }
 if(theme==='abstract'&&identity.personId==='shake-director')return ['前奏一响，另一个你已经站到镜头中间。','在这个虚构的平行宇宙，你成了摇摆导演。原本只想拍十秒，四位队友一到场，群舞、翻唱和笑场一起上线。你把最像自己的那一段留下，第一次用自己的节奏被大家记住。','成片不必全程整齐。有人记得舞步，有人记得笑声，这期终于有了你自己的味道。'];
 if(theme==='abstract'&&identity.personId==='liziqi')return ['慢一点，普通日常也有自己的主角镜头。','在这条架空时间线，你化身李子柒，和四位搭档把一件普通手作拍成了温柔的小故事。你没有急着追下一个热点，而是把材料、过程和做完后的笑容都留下。','视频有自己的呼吸，更新也有自己的节奏。这个宇宙的专属海克斯，是认真生活时一点点积累的光。'];
 if(theme==='basket'&&identity.personId==='wemby')return ['文班长臂服务区，今天正式营业。','平行总决赛里，你化身文班亚马。对手还在寻找上篮角度，你已经和四位队友把篮下照顾明白。一次干净封盖之后，你没有忙着庆祝，转身就把球传向跑起来的队友。','外星人梗可以接，位置还得认真站。这个宇宙的冠军合照里，五个人都在你的服务范围。'];
 if(theme==='basket'&&identity.personId==='edwards')return ['华子准备起飞，回防也在飞行计划里。','平行总决赛最后一节，你化身华子。队友传来一个舒服的球，你抓住合适机会完成上篮，笑着和传球的人击掌。镜头想留住你的庆祝，你已经回到防守的位置。','篮球梦之队把高光留给你，也把下一球继续交给你。这场比赛的节目效果，有冲劲，也有靠谱的下一步。'];
 if(theme==='basket'&&identity.roleType==='commentator')return [identity.name+'，这场比赛由你来讲。','你化身'+identity.name+'，坐进平行宇宙的解说席。朋友们在场上拼出一个精彩回合，你把前因后果讲成大家都听得懂的故事。暂停时球员喝水，你还在认真接住观众的问题。','五人队采用本作娱乐角色设定；这里的你是解说员，没有虚构球员履历。'];
 const own=stories[identity.personId];if(own)return own;const u=identity.universe;if(u)return [(identity.nickname||identity.name)+'，'+u.title+'正式上岗。',u.arrival+' 这条时间线交给你的任务是：'+u.mission,u.passive+' 队友给你的评价是：'+u.teamHook];return theme==='lol'?[`${identity.name}，这次由你接下决胜局。`,`你化身${identity.name}，走进一条结局尚未写下的平行赛道。对手准备好了熟悉的套路，你用${profile.name}的打法把这一局带到了新的节奏。`,'奖杯不是剧本的终点。五个人愿意再开一局，才是这个宇宙最好的彩蛋。']:theme==='basket'?[`${identity.name}，今天的名场面由你签收。`,`你化身${identity.name}。平行总决赛把所有戏剧性都留到了末节，你把熟悉的动作和没试过的选择拼成了自己的答案。`,'这个宇宙的虎扑式搞笑评分给出满分：有人负责数据，有人负责让整场值得重看。']:[`${identity.name}，你在另一个宇宙上线了。`,`你化身${identity.name}。普通的一天被平行宇宙拧开了一个口子，你用${profile.name}的方式，把五个看似不搭的人放进同一段故事。`,'故事没有标准答案。能把自己的那一集过得有声有色，也是一种隐藏天赋。'];}
function analyze(session,data){
 const vector=score(session,data),pool=data.characters.filter(p=>p.theme===session.theme),ranked=rankPeople(session,data,vector);
 const identity=ranked[0],code=[0,1,2].map(i=>vector[i]>=50?'1':'0').join('');let profile=data.profiles.find(p=>p.id===data.familyCodes[code]);
 if(session.theme==='lol'){const hi=vector.indexOf(Math.max(...vector));profile=Object.assign({},profile,{name:['上头编剧','金币合伙人','雪球发车人','全队保护伞','基本功信徒','桥上运营师'][hi]});}
 const recommendations=recommend(session,data,vector,identity),augment=recommendations[0],rows=selections(session,data);
 const evidence=dimsFor(session.theme).map((dim,di)=>{const choices=[].concat(...rows.map(({q,o})=>{if(session.theme!=='lol'&&q.dim!==dim)return [];return [{id:q.id,scene:q.scene,title:q.title,choice:o.text,value:session.theme==='lol'?o.signals[dim]:(o.value-1)/3*100}];}));choices.sort((a,b)=>Math.abs(b.value-50)-Math.abs(a.value-50));return Object.assign({dim,coordinate:vector[di]},choices[0]);});
 const bond=recommendations.find(a=>cardOwners(a).includes(identity.personId))||null;
 const representativeCards=(identity.signaturePerks||[]).map(id=>data.augments[session.theme].find(a=>a.id===id&&a.enabled!==false)).filter(Boolean),obtainedCards=augment?[augment]:[];
 return {representativeCards,obtainedCards,obtainedCardIds:obtainedCards.map(a=>a.id),inherentCards:data.version>=13?[]:representativeCards,triggeredPersonal:recommendations.filter(a=>a.exclusive&&a.personLink),vector,identity,ranked,profile,augment,recommendations,bond,team:linkTeam(buildTeam(vector,ranked,identity,augment),augment,session.theme),story:narrative(identity,session.theme,profile,session.series,augment),signature:Object.entries(rows.reduce((sum,{o})=>{sum[o.behavior]=(sum[o.behavior]||0)+1;return sum;},{})).sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0])).slice(0,3).map(([id,count])=>({id,count,label:data.behaviorLabels[id]})),evidence,coverage:dimsFor(session.theme).map(dim=>session.theme==='lol'?session.count:rows.filter(({q})=>q.dim===dim).length)};
}
function makeSquadName(theme,team,previous='',rng=random){
 if(!Array.isArray(team)||team.length!==5||new Set(team.map(p=>p.personId)).size!==5)throw Error('五位不同的队友到齐后才能起名');
 const heads={lol:['全员收集者','五楼拒绝补位','网费不够但嘴硬','最后一把不散伙','复活期间还在讲课','金色的雨先分期','今天全队都在解释','先别急着说稳了'],basket:['凌晨四点还在打铁','膝盖管理局','最后一投谁都想要','球没进先怪风','篮板全靠缘分','停车场射程施工中','赛后采访没人认输','全队申请暂停'],abstract:['吃饱喝足再上头','全员学士帽Plus','麦克风无人刹车','路费还没凑齐','先别急着解释','饭点比闹钟还准','五个群聊管理员','正片没开始先笑场']};
 const tails={lol:['包夜互助会','峡谷临时夺冠办','五黑售后服务部','没有前排股份公司','不愿透露战绩的五位市民','宇宙级复盘研究所'],basket:['篮球研究所','野球场团建小队','赛后嘴硬中心','夕阳红冠军分部','全员回防倡议会','篮筐维修筹备组'],abstract:['互联网临时工','宇宙级气氛组','节目效果售后部','饭后发布会筹备组','平行宇宙嘴替联盟','未获通知也要返场团']};
 if(!heads[theme])throw Error('不支持的战队主题');let title='',hi=0,ti=0;for(let k=0;k<6;k++){hi=Math.min(heads[theme].length-1,Math.floor(rng()*heads[theme].length));ti=Math.min(tails[theme].length-1,Math.floor(rng()*tails[theme].length));title=heads[theme][hi]+' · '+tails[theme][ti];if(title!==previous)break;}if(title===previous)title=heads[theme][(hi+1)%heads[theme].length]+' · '+tails[theme][ti];
 const motto={lol:'上不上分先不说，今晚五个人必须整整齐齐。',basket:'投进算大家的，打铁就当替篮筐做体检。',abstract:'节目可以随缘，人和饭必须按时到齐。'}[theme];
 return {title,motto,ids:team.map(p=>p.id),theme};
}
// Branch stories are pure replayable state machines. Cached rewards and flags are
// deliberately ignored: only validated seed cards and the recorded path are facts.
function branchStory(personId,data){return (data.branchStories||[]).find(s=>s.personId===personId)||null;}
function storyReplay(state,data){
 if(!state||state.version!==data.version||!Array.isArray(state.seedCards)||!Array.isArray(state.history)||typeof state.originKey!=='string'||state.originKey.length>256)throw Error('穿越故事存档已失效');
 const person=enabledPeople(data).find(p=>p.personId===state.personId),story=branchStory(state.personId,data);
 if(!person||!story||state.storyId!==story.id||!Array.isArray(story.nodes)||state.history.length>story.nodes.length)throw Error('找不到这段穿越故事');
 const cards=enabledCards(data,person.theme),byCard=new Map(cards.map(c=>[c.id,c]));
 if(new Set(state.seedCards).size!==state.seedCards.length||state.seedCards.some(id=>!byCard.has(id)))throw Error('故事中的海克斯不属于当前版本');
 const nodes=new Map(story.nodes.map(n=>[n.id,n]));
 let node=nodes.get(story.entry);if(!node)throw Error('故事入口不存在');
 const owned=new Set(state.seedCards),flags={},choices={},rewardLedger=[];
 for(const action of state.history){
  if(!action||action.nodeId!==node.id||node.type==='ending')throw Error('故事路线不完整');
  let next=node.next;
  if(node.type==='choice'){
   const choice=(node.choices||[]).find(c=>c.id===action.choiceId);if(!choice)throw Error('故事选项不存在');
   choices[node.id]=choice.id;
   Object.assign(flags,choice.flags||{});
   for(const id of choice.grantCardIds||[]){
    const card=byCard.get(id);if(!card)throw Error('故事奖励不属于当前版本');
    if(!owned.has(id)){owned.add(id);rewardLedger.push({cardId:id,name:card.name,nodeId:node.id,choiceId:choice.id,source:'story-choice'});}
   }
   next=choice.next;
  }else if(action.choiceId!==null)throw Error('请使用当前故事按钮');
  node=nodes.get(next);if(!node)throw Error('故事下一幕不存在');
 }
 return {story,person,node,flags,choices,ownedCardIds:Array.from(owned),rewardLedger};
}
function storySnapshot(base,data){const d=storyReplay(base,data);return Object.assign({},base,{seedCards:base.seedCards.slice(),history:base.history.map(a=>Object.assign({},a)),nodeId:d.node.id,flags:d.flags,choices:d.choices,ownedCardIds:d.ownedCardIds,rewardLedger:d.rewardLedger});}
function storyStart(personId,data,seedCardIds=[],originKey=''){
 const story=branchStory(personId,data);if(!story)throw Error('这个人物的穿越故事尚未开放');
 return storySnapshot({version:data.version,storyId:story.id,personId,originKey:String(originKey||''),seedCards:seedCardIds.slice(),history:[]},data);
}
function storyValid(state,data){try{storyReplay(state,data);return true;}catch(_){return false;}}
function storyView(state,data){
 const d=storyReplay(state,data),node=d.node;
 const variant=(node.variants||[]).find(v=>Object.keys(v.when||{}).every(k=>d.flags[k]===v.when[k]));
 const own=new Set(d.ownedCardIds);
 return {node:node.id,type:node.type,title:variant&&variant.title!==undefined?variant.title:node.title,
  text:variant&&variant.text!==undefined?variant.text:node.text,
  cardEvents:(node.cardEvents||[]).map(e=>({cardId:e.cardId,owned:own.has(e.cardId),text:own.has(e.cardId)?e.owned:e.unowned})),
  choices:(node.choices||[]).map(c=>({id:c.id,text:c.text,effect:c.effect})),
  ownedCardIds:d.ownedCardIds,rewardLedger:d.rewardLedger,canBack:state.history.length>0,
  isEnding:node.type==='ending',endingId:node.type==='ending'?(variant&&variant.endingId||node.endingId||node.id+':'+(d.flags.route2||'default')):null,
  progress:{current:state.history.length+1,total:d.story.nodes.length},flags:d.flags,storyId:d.story.id,personId:state.personId};
}
function storyChoose(state,nodeId,choiceId,data){
 const d=storyReplay(state,data);if(d.node.id!==nodeId||d.node.type!=='choice'||!(d.node.choices||[]).some(c=>c.id===choiceId))throw Error('这一幕已经切换，请重新选择');
 return storySnapshot(Object.assign({},state,{history:state.history.concat({nodeId,choiceId})}),data);
}
function storyAdvance(state,data){
 const d=storyReplay(state,data);if(d.node.type==='choice'||d.node.type==='ending')throw Error('请先完成当前故事选择');
 return storySnapshot(Object.assign({},state,{history:state.history.concat({nodeId:d.node.id,choiceId:null})}),data);
}
function storyBack(state,data){storyReplay(state,data);if(!state.history.length)return storySnapshot(state,data);return storySnapshot(Object.assign({},state,{history:state.history.slice(0,-1)}),data);}
return {storyStart,storyView,storyChoose,storyAdvance,storyBack,storyValid,branchStory,cardOwners,makeSquadName,enabledPeople,enabledCards,searchPeople,resolvePerson,applyExposure,exposureSample,dimIds,lolDimIds,dimsFor,shuffle,draw,valid,score,similarity,analyze,buildTeam,narrative,recommend,context,selections,questionAt,rankPeople,behaviorFit,artLayout,recordAnswer,squadError,fillSquad,customSquad};
});

(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.ShenrenEngine=factory();})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const dimIds=['social','explore','empathy','action','order','express'];
const lolDimIds=['tilt','greed','risk','team','craft','plan'];
const dimsFor=theme=>theme==='lol'?lolDimIds:dimIds;
function random(){if(typeof crypto!=='undefined'&&crypto.getRandomValues){const a=new Uint32Array(1);crypto.getRandomValues(a);return a[0]/4294967296;}return Math.random();}
function shuffle(list,rng=random){const a=list.slice();for(let i=a.length-1;i>0;i--){const j=Math.floor(rng()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
// One layout feeds both HTML and exported Canvas: the real icons and copy counts match.
function artLayout(a){
 const icons=a.visual?a.visual.icons:[],n=icons.length,l=a.visual?a.visual.layout:null;
 const points=n===1?[[.19,.19,.62,0]]:l==='grid'?icons.map((_,i)=>[.02+(i%3)*.33,.17+Math.floor(i/3)*.34,.30,0]):l==='square'?[[.07,.07,.36,-8],[.57,.07,.36,8],[.07,.57,.36,8],[.57,.57,.36,-8]]:l==='ring'?icons.map((_,i)=>{const t=-Math.PI/2+i*Math.PI*2/n;return [.33+Math.cos(t)*.28,.33+Math.sin(t)*.28,.34,i*15-15];}):l==='row'?icons.map((_,i)=>[.03+i*(.94-.40)/Math.max(1,n-1),.30+(i%2)*.1,.40,(i-(n-1)/2)*10]):n===2?[[.04,.28,.47,-15],[.49,.19,.47,15]]:n===3?[[.03,.35,.47,-17],[.51,.35,.47,17],[.27,.07,.47,0]]:n===4?[[.05,.14,.4,-15],[.55,.14,.4,15],[.05,.55,.4,-8],[.55,.55,.4,8]]:[[.03,.14,.37,-17],[.23,.04,.37,-8],[.43,.04,.37,8],[.62,.14,.37,17],[.29,.53,.43,0]];
 return icons.map((icon,i)=>({icon,x:points[i][0],y:points[i][1],size:points[i][2],rotation:points[i][3]}));
}
function enabledPeople(data,theme=null){return data.characters.filter(p=>p.enabled!==false&&(!theme||p.theme===theme)).sort((a,b)=>(a.rosterOrder||0)-(b.rosterOrder||0));}
function cardOwners(card){return Array.isArray(card.owners)?card.owners.slice():Array.isArray(card.signatureFor)&&card.signatureFor.length?card.signatureFor.slice():card.owner?[card.owner]:[];}
function enabledCards(data,theme=null){return [].concat(...Object.keys(data.augments).filter(t=>!theme||t===theme).map(t=>data.augments[t])).filter(a=>a.enabled!==false);}
function searchPeople(data,theme,query=''){const q=query.trim().toLowerCase();return enabledPeople(data,theme==='all'?null:theme).filter(p=>[p.name,p.nickname].concat(p.aliases||[],p.tags||[]).join(' ').toLowerCase().includes(q));}
function resolvePerson(data,value){const q=String(value).toLowerCase();return data.characters.find(p=>p.id===value||p.personId===value||(p.aliases||[p.name,p.nickname]).some(a=>a&&a.toLowerCase()===q))||null;}
function applyExposure(candidates,policy={}){
 if(!candidates.length)return [];
 const top=Math.max(...candidates.map(p=>p.rawMatch)),near=Math.max(0,Math.min(8,policy.nearTop===undefined?5:policy.nearTop)),bonus=Math.max(0,Math.min(6,policy.maxBonus===undefined?4:policy.maxBonus)),starNear=Math.max(0,Math.min(15,policy.flagshipNearTop===undefined?12:policy.flagshipNearTop)),starBonus=Math.max(0,Math.min(12,policy.flagshipBonus===undefined?9:policy.flagshipBonus));
 return candidates.map(p=>{const flagship=p.tier==='flagship',featured=p.tier==='featured',gap=top-p.rawMatch,add=flagship&&gap<=starNear?starBonus:featured&&gap<=near?bonus:0;return Object.assign({},p,{match:p.rawMatch,editorialBonus:add});}).sort((a,b)=>(b.rawMatch+b.editorialBonus)-(a.rawMatch+a.editorialBonus)||b.rawMatch-a.rawMatch||a.id.localeCompare(b.id));
}
function exposureSample(data,theme,n=1,rng=random){const pool=enabledPeople(data,theme).slice(),out=[];while(pool.length&&out.length<n){let x=rng()*pool.reduce((sum,p)=>sum+p.exposureWeight,0),i=0;for(;i<pool.length-1;i++){x-=pool[i].exposureWeight;if(x<0)break;}out.push(pool.splice(i,1)[0]);}return out;}
function draw(data,theme,count,previousFirst=null,rng=random,series='all'){
 if(!data.themes.some(t=>t.id===theme)||!data.modes.includes(count))throw Error('不支持的主题或题量');
 if(theme==='lol'&&!['all','hex','rift'].includes(series))throw Error('不支持的联盟系列');
 let chosen=[];
 if(theme==='lol'){
  const bank=data.questions.filter(q=>q.enabled!==false&&q.theme===theme&&(series==='all'||q.series===series));
  const chapters=shuffle([...new Set(bank.map(q=>q.series+':'+q.chapter))],rng);
  if(chapters.length<count/4)throw Error('章节题库不足');
  if(bank.some(q=>q.id===previousFirst&&chapters[0]===q.series+':'+q.chapter))[chapters[0],chapters[1]]=[chapters[1],chapters[0]];
  chosen=[].concat(...chapters.slice(0,count/4).map(c=>bank.filter(q=>q.series+':'+q.chapter===c).sort((a,b)=>a.stage-b.stage)));
 }else{
  const extra=new Set(shuffle(dimIds,rng).slice(0,count%6));
  dimIds.forEach(dim=>{const bank=data.questions.filter(q=>q.enabled!==false&&q.theme===theme&&q.dim===dim),n=Math.floor(count/6)+(extra.has(dim)?1:0);if(bank.length<n)throw Error('题库不足');chosen.push(...shuffle(bank,rng).slice(0,n));});
  chosen=shuffle(chosen,rng);if(chosen[0].id===previousFirst)[chosen[0],chosen[1]]=[chosen[1],chosen[0]];
 }
 return {version:data.version,theme,series:theme==='lol'?series:'all',count,deck:chosen.map(q=>({id:q.id,order:shuffle(q.options.map(o=>o.id),rng)})),answers:Array(count).fill(null),index:0,phase:'quiz',date:new Date().toISOString()};
}
function valid(s,data,complete=false){
 if(!s||s.version!==data.version||!data.themes.some(t=>t.id===s.theme)||!data.modes.includes(s.count)||!Array.isArray(s.deck)||s.deck.length!==s.count||!Array.isArray(s.answers)||s.answers.length!==s.count||!Number.isInteger(s.index)||s.index<0||s.index>=s.count)return false;
 if(s.theme==='lol'&&!['hex','rift','all'].includes(s.series))return false;
 if(new Set(s.deck.map(d=>d&&d.id)).size!==s.count)return false;
 const questions=s.deck.map(d=>data.questions.find(q=>q.id===(d&&d.id)&&q.theme===s.theme&&(s.theme!=='lol'||s.series==='all'||q.series===s.series)));
 if(questions.some(q=>!q))return false;
 if(s.theme==='lol'){
  for(let i=0;i<questions.length;i+=4){const group=questions.slice(i,i+4);if(group.some((q,j)=>q.chapter!==group[0].chapter||q.series!==group[0].series||q.stage!==j))return false;}
 }else if(!dimIds.every(dim=>questions.some(q=>q.dim===dim)))return false;
 return s.deck.every((d,i)=>Array.isArray(d.order)&&d.order.length===4&&new Set(d.order).size===4&&d.order.every(v=>questions[i].options.some(o=>o.id===v))&&((!complete&&s.answers[i]===null)||questions[i].options.some(o=>o.id===s.answers[i])));
}
// Commit against the question that was actually displayed; stale taps cannot answer another question.
function recordAnswer(s,data,questionId,optionId){
 if(!valid(s,data)||s.phase!=='quiz'||s.deck[s.index].id!==questionId)throw Error('这道题已经切换，请重新选择');
 const q=data.questions.find(q=>q.id===questionId);
 if(!q.options.some(o=>o.id===optionId))throw Error('这个选项不存在');
 const next=Object.assign({},s,{answers:s.answers.slice()});next.answers[s.index]=optionId;
 const complete=s.index===s.count-1;
 if(complete)next.phase='complete';else next.index=s.index+1;
 return {session:next,complete};
}
function selections(s,data){return s.deck.map((d,i)=>{const q=data.questions.find(q=>q.id===d.id);return {q,o:q.options.find(o=>o.id===s.answers[i])};});}
function score(s,data){
 if(!valid(s,data,true))throw Error('请完成本轮全部题目');const rows=selections(s,data);
 return dimsFor(s.theme).map(dim=>{if(s.theme==='lol'){const total=rows.reduce((sum,{o})=>sum+o.signals[dim],0),neutral=rows.reduce((sum,{q})=>sum+q.options.reduce((n,o)=>n+o.signals[dim],0)/4,0),lo=rows.reduce((sum,{q})=>sum+Math.min(...q.options.map(o=>o.signals[dim])),0),hi=rows.reduce((sum,{q})=>sum+Math.max(...q.options.map(o=>o.signals[dim])),0),delta=total-neutral;return Math.max(0,Math.min(100,Math.round(50+50*delta/Math.max(1,delta>=0?hi-neutral:neutral-lo))));}const values=rows.filter(({q})=>q.dim===dim).map(({o})=>o.value);return Math.round((values.reduce((a,b)=>a+b,0)/values.length-1)/3*100);});
}
function similarity(a,b){return Math.round(100*(1-a.reduce((s,v,i)=>s+Math.abs(v-b[i]),0)/600));}
function responseWeight(q){return q.importance||1;}
function behaviorFit(rows,weights={}){const total=rows.reduce((sum,{q})=>sum+responseWeight(q),0);return total?100*rows.reduce((sum,{q,o})=>sum+(weights[o.behavior]||0)*responseWeight(q),0)/(5*total):0;}
function cardEvidence(rows,card){return rows.map(({q,o},index)=>({id:q.id,scene:q.scene,choice:o.text,behavior:o.behavior,strength:((card.behaviorWeights&&card.behaviorWeights[o.behavior])||0)*responseWeight(q),index})).filter(e=>e.strength>0&&(!card.evidenceQuestionIds||!card.evidenceQuestionIds.length||card.evidenceQuestionIds.includes(e.id))&&(!Array.isArray(card.answerEvidence)||card.answerEvidence.some(a=>a.questionId===e.id&&a.optionId===rows[e.index].o.id))).sort((a,b)=>b.strength-a.strength||a.index-b.index);}
function rankPeople(s,data,vector){const rows=selections(s,data);return applyExposure(enabledPeople(data,s.theme).map(p=>{const v=similarity(vector,p.vector),b=behaviorFit(rows,p.behaviorWeights),scene=100*rows.reduce((sum,{q,o})=>sum+(p.optionAffinities?((p.optionAffinities[q.id]&&p.optionAffinities[q.id][String(o.id)])||0):((p.answerAffinities&&p.answerAffinities[q.id]&&p.answerAffinities[q.id][o.behavior])||0)),0)/(5*rows.length);return Object.assign({},p,{rawMatch:Math.round(.4*v+.35*b+.25*scene),matchBreakdown:{vector:v,behavior:b,scene}});}),data.rosterPolicy);}

function recommend(s,data,vector=score(s,data),identity=null){
 const rows=selections(s,data);if(!identity)identity=rankPeople(s,data,vector)[0];
 return enabledCards(data,s.theme).filter(a=>a.activationMode!=='identity').filter(a=>!a.personOnly||cardOwners(a).includes(identity.personId)).filter(a=>!(a.requires||[]).length||(a.requires||[]).some(b=>rows.some(({o})=>o.behavior===b))).map(a=>{
  const v=a.vector||a.bias.map(n=>Math.max(0,Math.min(100,50+n*40))),evidence=cardEvidence(rows,a);
  const behavior=behaviorFit(rows,a.behaviorWeights),bonus=(cardOwners(a).includes(identity.personId)||(a.affinities||[]).includes(identity.personId))?5:0;
  const match=Math.round(.42*similarity(vector,v)+.53*behavior+bonus);
  return Object.assign({},a,{match,evidence:evidence.slice(0,2),hitCount:evidence.length,personLink:bonus>0});
 }).filter(a=>a.hitCount>0).sort((a,b)=>Number(Boolean(b.exclusive&&b.personLink))-Number(Boolean(a.exclusive&&a.personLink))||b.match-a.match||b.hitCount-a.hitCount||a.id.localeCompare(b.id));
}
function questionAt(s,data,index=s.index){const q=data.questions.find(q=>q.id===(s.deck[index]&&s.deck[index].id));if(!q)return null;const prior=index>0?s.answers[index-1]:null;return Object.assign({},q,{title:q.branches&&prior!==null?(q.branches[String(prior)]||q.title):q.title});}
const reactions={afk:'你的镜头切到观战席，接下来由你决定这局怎么演。',int:'上一单已经送达，导播开始等你的下一次发车。',collector:'第五把收集者已在计划里，下一波还得看阵容。',protect:'你把队友留在镜头里，接下来看看这份售后怎么做。',heal:'桥头医务室已经开门，下一波挂号队伍也到了。',explain:'复活倒计时在走，你的讲解刚刚开始。',blame:'锅还在空中，下一幕先看看谁来接。',chaos:'节目效果已到账，故事还有下一幕。',plan:'计划先写在这里，接下来看看现场听不听安排。',engage:'车已经开了，接下来看乘客有没有跟上。',reset:'上一段剧本已翻篇，新的一幕还等你接梗。',laugh:'笑容先记一段，接下来手也要跟上。',calm:'你把庆祝留到了后面，先把眼前的对局打完。',spin:'抗压拉扯已经开始，下一步看看有没有反打空间。',stasis:'金身时机已经记下，结束之后还得接着操作。',flash:'闪现交了，接下来先把走位和退路找回来。',vision:'你先要信息，再决定下一步怎么打。'};
function context(s,data,index=s.index){const q=questionAt(s,data,index);if(q.theme!=='lol'||q.stage===0)return null;const previous=data.questions.find(p=>p.id===s.deck[index-1].id),o=previous.options.find(o=>o.id===s.answers[index-1]);return o?{chapter:q.chapterName,stage:q.stage,previousChoice:o.text,previousScene:previous.scene,reaction:reactions[o.behavior]||'上一个反应已经记下，同一场对局继续往下演。'}:null;}
const teamScripts={
 range:['上路卡位：把对手留在输出射程里。','打野盯人：绕后的人先报位置。','中路消耗：命中一轮再决定进退。','下路拉扯：边走边打，别只顾着后退。','辅助接应：控制留给贴脸的那个人。'],
 blame:['上路复盘：先说线权，再看有没有支援。','打野报点：刷野路线和到场时间说清楚。','中路看图：先确认信息，再问队友在哪。','下路回放：谁先吃控，拉进度条再说。','辅助提醒：复活时间和技能比问号更有用。'],
 economy:['上路承压：先站住，再给四个输出腾空间。','野区控图：该吃资源时吃，该到场时到。','中路游走：推完线再走，别两头都漏。','下路收尾：残血可以收，前排别硬穿。','辅助售后：全队唯一还看血条的人。'],
 chaos:['上路独演：先把边线变成个人舞台。','打野发车：路线直达下一段集锦。','中路配乐：这一波自带主角 BGM。','下路压轴：高光和灰屏只隔一帧。','辅助验票：上车前请签字。'],
 engage:['上路顶门：把第一波技能收下。','打野发车：开之前先数一遍乘客。','中路接戏：控制留给关键那个人。','下路输出：司机说到站再下车。','辅助导航：负责把人齐这件事讲明白。'],
 protect:['上路挡风：四个输出的移动掩体。','打野保安：巡逻到后排就上班。','中路调度：让技能替队友争取时间。','下路患者：请在医务室射程内营业。','辅助主治：这家没你真得关门。'],
 basic:['上路动作指导：细节交给手，不交给嘴。','打野解说：先把路线走成一个几何题。','中路编导：等到技能窗口再拍。','下路主演：金色的雨要自己走位接。','辅助控场：让高光背后有人接应。'],
 plan:['上路带线：看完小地图再过河。','打野路线：第四条边还没讲完。','中路恒温：今天几度由这里决定。','下路输出：等关键装备成型再接硬仗。','辅助复盘：把五个人留在同一张图上。'],
 retreat:['上路安全员：撤退也要留出通道。','打野巡场：先看地图再问队友呢。','中路观察：等对手把按钮按完。','下路远程：在安全感边缘输出。','辅助接人：回来就有口热奶。'],
 reset:['上路续集：这一条线还没演完。','打野刷新：新路线下一局见。','中路转场：重开也要记得带队友。','下路重拍：镜头先别删。','辅助留人：说好最后一把，又齐了。']};
function linkTeam(team,augment,theme){const lines=theme==='basket'?['控卫串联：先让队友都能接到球。','分卫接火：有机会就投，没机会先传。','侧翼跑动：把这一段名场面接起来。','篮下协作：卡好位置，给队友留空间。','中锋护框：篮板和回防都得有人管。']:theme==='abstract'?['发言人开场：把五个人的故事讲清楚。','行动派开拍：先完成最容易的一小段。','军师编排：好点子也要有人把它做出来。','气氛组接梗：前奏一响，全队进入画面。','场控收尾：照顾边界，也别落下任何队友。']:(teamScripts[augment.kind]||teamScripts.chaos);return team.map(p=>Object.assign({},p,{teamLine:lines[p.slot]}));}
function buildTeam(vector,characters,identity,augment){
 let best=null;
 for(const myRole of identity.roles){
  let states=Array(32).fill(null);states[1<<myRole]={value:0,slots:Array(5).fill(null)};states[1<<myRole].slots[myRole]=identity;
  for(const p of characters.filter(p=>p.id!==identity.id)){
   const next=states.slice();for(let mask=0;mask<32;mask++){const prior=states[mask];if(!prior)continue;
    for(let role=0;role<5;role++){if(mask&(1<<role)||!p.roles.includes(role))continue;const match=similarity(vector,p.vector),affinity=p.roles[0]===role?12:p.roles.includes(role)?7:-18;const flavor=augment?augment.bias.reduce((s,w,i)=>s+w*(p.vector[i]-50)/10,0):0;const value=prior.value+match+affinity+flavor;
     const to=mask|(1<<role);if(!next[to]||value>next[to].value){const slots=prior.slots.slice();slots[role]=p;next[to]={value,slots};}}
   }states=next;
  }
  const full=states[31];if(full&&(!best||full.value>best.value))best=full;
 }
 if(!best)throw Error('角色池不足以组成五人队');return best.slots.map((p,i)=>Object.assign({},p,{slot:i,isYou:p.id===identity.id,match:p.match===undefined?similarity(vector,p.vector):p.match,naturalRole:p.roles.includes(i)}));
}

function squadError(ids,theme,data,free=false,partial=false){
 if(!Array.isArray(ids)||ids.length!==5)return '请选择五个位置';
 const chosen=ids.filter(Boolean);if(!partial&&chosen.length!==5)return '还没选满五个人';
 const people=[];for(let i=0;i<5;i++){if(!ids[i])continue;const p=enabledPeople(data,theme).find(p=>p.id===ids[i]);if(!p)return '只能选择当前主题的人物';if(people.includes(p.personId))return '同一个人不能重复出场';people.push(p.personId);if(!free&&!p.roles.includes(i))return '这个位置不合适，可开启自由整活';}return '';
}
function fillSquad(ids,theme,data,vector,free=false){
 const err=squadError(ids,theme,data,free,true);if(err)throw Error(err);
 const fixed=ids.map(id=>id?data.characters.find(p=>p.id===id):null),used=fixed.filter(Boolean).map(p=>p.personId);let mask=0;fixed.forEach((p,i)=>{if(p)mask|=1<<i;});
 let states=Array(32).fill(null);states[mask]={value:0,slots:fixed.slice()};
 for(const p of enabledPeople(data,theme).filter(p=>!used.includes(p.personId))){const next=states.slice();for(let m=0;m<32;m++){const prev=states[m];if(!prev)continue;for(let i=0;i<5;i++){if((m&(1<<i))||(!free&&!p.roles.includes(i)))continue;const val=prev.value+similarity(vector,p.vector)+(p.roles[0]===i?12:p.roles.includes(i)?7:-15),to=m|(1<<i);if(!next[to]||val>next[to].value){const slots=prev.slots.slice();slots[i]=p;next[to]={value:val,slots};}}}states=next;}
 if(!states[31])throw Error('当前选择无法补齐五个位置；请换人或开启自由整活');return states[31].slots.map(p=>p.id);
}
function customSquad(ids,theme,data,vector,identity,augment,free=false){
 const err=squadError(ids,theme,data,free);if(err)throw Error(err);
 return linkTeam(ids.map((id,slot)=>{const p=data.characters.find(p=>p.id===id);return Object.assign({},p,{slot,isYou:p.personId===identity.personId,match:similarity(vector,p.vector),naturalRole:p.roles.includes(slot),custom:true});}),augment,theme).map(p=>Object.assign({},p,{teamLine:(p.naturalRole?'':'跨位整活 / ')+(p.tags||[]).slice(0,2).join(' · ')+'。'+p.teamLine}));
}

const stories={
 jackeylove:['哥哥，这回向前一步走到了金色的雨。','在这条架空 S8 时间线，你化身阿水。最后一局的闪现没有换来灰屏，而是等到了四名队友同时到场。你找到侧面的空隙，输出、拉开、再次上前，把那个熟悉的“敢打”变成了所有人等着看的结局。','奖杯前大家又喊起哥哥。你笑着把四个人拉进合照：这次镜头里，一个队友都没少。'],
 rookie:['院长，这次把整个宇宙都救回来了。','你化身 Rookie，站进一场架空 S8 决赛。队友在语音里喊你，你把中路守成了全队的落脚点。最后一波控制接上，四个熟悉的身影一起向前，你的输出把最后一座基地打成了金色的雨。','你抱着奖杯，眼泪先于采访回答。观众喊着肉鸡，队友说今天院长终于可以下班了。'],
 dailanzi:['评论区还没开，你的平行宇宙已经有了开场白。','你化身带篮子，带着四位风格完全不同的队友开了一场平行宇宙直播。刀哥带了好果汁，峰哥讲起路上的故事，台下刚有点冷场，你用一句带文学把所有人拉回同一段里。','散场后，最热的一条弹幕不是谁赢了，而是“这五个人怎么凑一起的”。你把它置顶：下一期，还得人齐。'],
 xiaoxiao:['双声道里，终于播到了冠军谢幕。','你化身笑笑，和西卡坐在平行决赛的解说席。开场的笑声被你们接成一句句简明的提醒。最后一波五个人齐了，基地倒下，你们一边笑一边把每个队友的名字喊出来。','这个宇宙的冠军回放有两个声道：一个记住操作，一个记住大家为什么一起笑。'],
 xika:['搭档那句话，被你接成了整个宇宙的片尾。','你化身西卡，和笑笑主持一场平行宇宙冠军之夜。有人讲快了，你补一句；有人漏了细节，你再讲清一遍。最后一波打完，直播间的笑声和现场的金色纸片一起落下。','冠军采访结束，你还在替这局接尾句：先别关，五个人的合照还没拍。'],
 uzi:['平行 S8，轮到你改写结局。','在这条架空时间线，你变成了污渍。决胜局，对面的飞科锁下加里奥，镜头里所有人都以为这又是熟悉的剧本。你却在最后一波侧身躲开控制，和四位队友一起战胜 Faker，把输出打到了结算页面。','金色的雨落下。你抱着奖杯泪流满面，全场高喊“世界第一 ADC”。主持人还在问“历史第一 ADC”，你已经把问题推进到“英雄联盟的 GOAT”。收集者不是决定，敢不敢接下这场比赛才是。'],
 xiaohu:['这个宇宙，没有不属于你的季节。','你变成了销户，赛场的日历被你改成了“春一月”到“春十二月”。总决赛打到最后一局，你把边线、团战与笑容一起拉满。','奖杯旁边多了一块恒温器：全宇宙的春天，今天由中路负责。'],
 dasima:['从讲解席，走到冠军颁奖台。','你变成了大司马。架空决赛里，所有人还在质疑你的路线，你已经画出了第三条“正方形打野”轨迹。最后一波不是嘴上有说法，是地图真的照着你的说法走。','奖杯被你端成一件教学道具。冠军公开课第一句话：先别急，这波我慢慢讲。'],
 theshy:['上路这条线，通向另一个结局。','你化身 TheShy，在架空决赛把一条边线打成了自己的独立宇宙。对手终于凑齐五个人来围你，你的队友刚好把另一边的主场拆完。','赛后大家讨论阵型，你在战术板上画了一条线：这里，也是一种答案。'],
 faker:['这一次，时间站在你这一边。','你化身飞科。平行决赛进入最安静的十秒，你等到所有技能交错的缝隙，再把那个属于自己的窗口按了下去。','第五次、第六次都不再是问题。这个宇宙的传奇，是把每一个小回合认真打完。'],
 lebron:['勒邦詹氏，膝盖先于战术板反应。','平行总决赛最后一攻，你变成了勒邦詹氏。漏判出现，全场进入表情加载页，你用一个跪地默剧把节目效果拉满。随后你站起来，追帽、推进、压哨出手一气呵成。','球进灯亮。这个宇宙的“虎扑式”搞笑评分写着：10 分，建议把膝盖也算进首发。你拿走的是这条时间线的 GOAT 剧本。'],
 curry:['停车场，正式进入你的射程表。','你变成了库里。平行总决赛的三分线被搬到停车场，大家还在找停车位，你已经借掩护转身出手。篮球在空中待得像一趟跨省快递。','球落网，晚安手势安排上。这个宇宙规定：只要你站得稳，想象力就有出手权。'],
 kobe:['凌晨的第一盏灯，由你点亮。','你化身科比。平行总决赛最后一节，你把练过无数遍的动作放进那个最需要答案的回合。全场的声音很大，你听见的只有脚步和球落网。','镜头切到空荡的训练馆：这里，早就为这个结局留过灯。'],
 jokic:['马儿没来，但传球已经到了。','你化身约老师。平行总决赛开打前，大家发现战术板背面是一张木马旋转图。第三节开始，对手才意识到每个人都被你转到了正确的位置。','你拿着奖杯问能不能早点回去。这个宇宙的中锋，把轻描淡写打成了史诗。'],
 fengge:['你去过的地方，地图还没来得及加载。','你变成了峰哥，揣着一张平行宇宙通行证出发。路边一间小卖部卖的是“如果当年”，你没急着买，而是拉老板聊完了另一个人生。','最后你带回来五个人和一大串故事。宇宙没被你讲明白，但你的这一集已经够好看。'],
 huge:['来，整个宇宙先别关。','你变成了虎哥。平行东北的路灯突然集体熄灭，你一抬手，现场五个人自带开机音效。围观群众还没弄清第一幕，第二幕已经顺着街口开过去了。','城市把“节目效果维护员”奖章发给你。你问：奖章能不能再配一瓶好果汁？'],
 daoge:['好果汁，这回送到了银河边上。','你变成了刀哥。一封星际补给单把你带到银河边，你发现全宇宙都在排队等下一段名场面。你把好果汁放上桌，先把五个队友招呼齐。','这场没有既定台词，只有现场反应。你的平行身份，是让离谱故事继续发生的人。'],
 geyou:['你没拯救宇宙，你让它坐下休息了。','你变成了葛优。平行世界不停催进度，所有人都在找下一场大事。你先在沙发上挪出四个位置，把队友一个个招呼坐下。','宇宙最后没爆炸。它只是承认：有些重要的事，要坐稳了才能想明白。']
};
function narrative(identity,theme,profile,series='all',augment=null){
 if(Array.isArray(identity.parallelStory)&&identity.parallelStory.length===3)return identity.parallelStory.slice();
 if(theme==='lol'&&(augment&&augment.id)==='double-laugh')return [`${identity.nickname||identity.name}，把第二段笑留给金色的雨。`,'在这条架空时间线，你在开局前忍住了第一段笑。领先以后，队友已经准备庆祝，你却把手重新放回键盘：这次先把对局打完。决胜团结束，基地终于倒下，导播才切到你的笑脸。','第一段是开心，第二段是终于赢了。这个平行宇宙的表情包，连同奖杯一起由你签收。'];
 if(theme==='lol'&&(augment&&augment.id)==='tes-top')return [`${identity.nickname||identity.name}，这回陀螺转出了反打角度。`,'在这条架空时间线，你们连着两波被压在塔前，弹幕里又飘起陀螺梗。你没有再抢着接第三波，而是和四位队友等到对面的开团技能交空，再从侧面一起打回去。','赛后梗图还在，但这次的结尾多了一段反打集锦。你把图存进群里：能笑，也能把下一波打明白。'];
 if(theme==='lol'&&series==='hex'){
  if(identity.personId==='uzi')return ['平行 S8，嚎哭深渊也能下起金色的雨。','在这条架空时间线，S8 决赛开在海克斯大乱斗的桥上。你变成污渍，对面的飞科又锁下加里奥。全场以为结局早已写好，你却用一波天赋联动和极限走位，把输出打到了结算页。','金色的雨落下。历史第一 ADC 只是起点，这个宇宙的观众把英雄联盟 GOAT 的剧本交给了你。收集者先收好，奖杯也别落下。'];
  if(identity.personId==='dasima')return ['这座桥，终于听懂了你的说法。','你化身大司马，走进一场架空海克斯冠军赛。随机给出的天赋看起来不搭，你边讲边把它连成一套“正方形大乱斗”。全队从一脸疑惑，打到一起点头。','最后一波结束，你端着奖杯继续讲：先别急，这次真的不是失误，是教材。冠军席，被你办成了一间公开课堂。'];
  if(identity.personId==='xiaohu')return ['嚎哭深渊，今天全桥入春。','你化身销户，进入一条只过春天的海克斯时间线。桥上冰雪还没化，天赋组合已经被你运营到舒服的位置。决胜团开打，所有人终于明白谁在掌握季节。','这个宇宙的奖杯旁多了一台恒温器。不是每年春天很强，是今天由你宣布春天。'];
  return [identity.name+'，这一座桥由你改写。','你化身'+identity.name+'，站上平行宇宙的海克斯大乱斗冠军桥。随机天赋没有给你标准答案，你用'+profile.name+'的反应，把一次普通抽签变成了自己的打法。'+(augment?'这一局，'+augment.name+'也写进了你的名场面。':''),'对手记住的也许是连招，队友记住的是这一局有人敢把可能性试出来。奖杯旁边，还有一枚属于这个宇宙的 GOAT 彩蛋。'];
 }
 if(theme==='abstract'&&identity.personId==='shake-director')return ['前奏一响，另一个你已经站到镜头中间。','在这个虚构的平行宇宙，你成了摇摆导演。原本只想拍十秒，四位队友一到场，群舞、翻唱和笑场一起上线。你把最像自己的那一段留下，第一次用自己的节奏被大家记住。','成片不必全程整齐。有人记得舞步，有人记得笑声，这期终于有了你自己的味道。'];
 if(theme==='abstract'&&identity.personId==='liziqi')return ['慢一点，普通日常也有自己的主角镜头。','在这条架空时间线，你化身李子柒，和四位搭档把一件普通手作拍成了温柔的小故事。你没有急着追下一个热点，而是把材料、过程和做完后的笑容都留下。','视频有自己的呼吸，更新也有自己的节奏。这个宇宙的专属海克斯，是认真生活时一点点积累的光。'];
 if(theme==='basket'&&identity.personId==='wemby')return ['文班长臂服务区，今天正式营业。','平行总决赛里，你化身文班亚马。对手还在寻找上篮角度，你已经和四位队友把篮下照顾明白。一次干净封盖之后，你没有忙着庆祝，转身就把球传向跑起来的队友。','外星人梗可以接，位置还得认真站。这个宇宙的冠军合照里，五个人都在你的服务范围。'];
 if(theme==='basket'&&identity.personId==='edwards')return ['华子准备起飞，回防也在飞行计划里。','平行总决赛最后一节，你化身华子。队友传来一个舒服的球，你抓住合适机会完成上篮，笑着和传球的人击掌。镜头想留住你的庆祝，你已经回到防守的位置。','篮球梦之队把高光留给你，也把下一球继续交给你。这场比赛的节目效果，有冲劲，也有靠谱的下一步。'];
 if(theme==='basket'&&identity.roleType==='commentator')return [identity.name+'，这场比赛由你来讲。','你化身'+identity.name+'，坐进平行宇宙的解说席。朋友们在场上拼出一个精彩回合，你把前因后果讲成大家都听得懂的故事。暂停时球员喝水，你还在认真接住观众的问题。','五人队采用本作娱乐角色设定；这里的你是解说员，没有虚构球员履历。'];
 const own=stories[identity.personId];if(own)return own;const u=identity.universe;if(u)return [(identity.nickname||identity.name)+'，'+u.title+'正式上岗。',u.arrival+' 这条时间线交给你的任务是：'+u.mission,u.passive+' 队友给你的评价是：'+u.teamHook];return theme==='lol'?[`${identity.name}，这次由你接下决胜局。`,`你化身${identity.name}，走进一条结局尚未写下的平行赛道。对手准备好了熟悉的套路，你用${profile.name}的打法把这一局带到了新的节奏。`,'奖杯不是剧本的终点。五个人愿意再开一局，才是这个宇宙最好的彩蛋。']:theme==='basket'?[`${identity.name}，今天的名场面由你签收。`,`你化身${identity.name}。平行总决赛把所有戏剧性都留到了末节，你把熟悉的动作和没试过的选择拼成了自己的答案。`,'这个宇宙的虎扑式搞笑评分给出满分：有人负责数据，有人负责让整场值得重看。']:[`${identity.name}，你在另一个宇宙上线了。`,`你化身${identity.name}。普通的一天被平行宇宙拧开了一个口子，你用${profile.name}的方式，把五个看似不搭的人放进同一段故事。`,'故事没有标准答案。能把自己的那一集过得有声有色，也是一种隐藏天赋。'];}
function analyze(session,data){
 const vector=score(session,data),pool=data.characters.filter(p=>p.theme===session.theme),ranked=rankPeople(session,data,vector);
 const identity=ranked[0],code=[0,1,2].map(i=>vector[i]>=50?'1':'0').join('');let profile=data.profiles.find(p=>p.id===data.familyCodes[code]);
 if(session.theme==='lol'){const hi=vector.indexOf(Math.max(...vector));profile=Object.assign({},profile,{name:['上头编剧','金币合伙人','雪球发车人','全队保护伞','基本功信徒','桥上运营师'][hi]});}
 const recommendations=recommend(session,data,vector,identity),augment=recommendations[0],rows=selections(session,data);
 const evidence=dimsFor(session.theme).map((dim,di)=>{const choices=[].concat(...rows.map(({q,o})=>{if(session.theme!=='lol'&&q.dim!==dim)return [];return [{id:q.id,scene:q.scene,title:q.title,choice:o.text,value:session.theme==='lol'?o.signals[dim]:(o.value-1)/3*100}];}));choices.sort((a,b)=>Math.abs(b.value-50)-Math.abs(a.value-50));return Object.assign({dim,coordinate:vector[di]},choices[0]);});
 const bond=recommendations.find(a=>cardOwners(a).includes(identity.personId))||null;
 const representativeCards=(identity.signaturePerks||[]).map(id=>data.augments[session.theme].find(a=>a.id===id&&a.enabled!==false)).filter(Boolean),obtainedCards=augment?[augment]:[];
 return {representativeCards,obtainedCards,obtainedCardIds:obtainedCards.map(a=>a.id),inherentCards:data.version>=13?[]:representativeCards,triggeredPersonal:recommendations.filter(a=>a.exclusive&&a.personLink),vector,identity,ranked,profile,augment,recommendations,bond,team:linkTeam(buildTeam(vector,ranked,identity,augment),augment,session.theme),story:narrative(identity,session.theme,profile,session.series,augment),signature:Object.entries(rows.reduce((sum,{o})=>{sum[o.behavior]=(sum[o.behavior]||0)+1;return sum;},{})).sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0])).slice(0,3).map(([id,count])=>({id,count,label:data.behaviorLabels[id]})),evidence,coverage:dimsFor(session.theme).map(dim=>session.theme==='lol'?session.count:rows.filter(({q})=>q.dim===dim).length)};
}
function makeSquadName(theme,team,previous='',rng=random){
 if(!Array.isArray(team)||team.length!==5||new Set(team.map(p=>p.personId)).size!==5)throw Error('五位不同的队友到齐后才能起名');
 const heads={lol:['全员收集者','五楼拒绝补位','网费不够但嘴硬','最后一把不散伙','复活期间还在讲课','金色的雨先分期','今天全队都在解释','先别急着说稳了'],basket:['凌晨四点还在打铁','膝盖管理局','最后一投谁都想要','球没进先怪风','篮板全靠缘分','停车场射程施工中','赛后采访没人认输','全队申请暂停'],abstract:['吃饱喝足再上头','全员学士帽Plus','麦克风无人刹车','路费还没凑齐','先别急着解释','饭点比闹钟还准','五个群聊管理员','正片没开始先笑场']};
 const tails={lol:['包夜互助会','峡谷临时夺冠办','五黑售后服务部','没有前排股份公司','不愿透露战绩的五位市民','宇宙级复盘研究所'],basket:['篮球研究所','野球场团建小队','赛后嘴硬中心','夕阳红冠军分部','全员回防倡议会','篮筐维修筹备组'],abstract:['互联网临时工','宇宙级气氛组','节目效果售后部','饭后发布会筹备组','平行宇宙嘴替联盟','未获通知也要返场团']};
 if(!heads[theme])throw Error('不支持的战队主题');let title='',hi=0,ti=0;for(let k=0;k<6;k++){hi=Math.min(heads[theme].length-1,Math.floor(rng()*heads[theme].length));ti=Math.min(tails[theme].length-1,Math.floor(rng()*tails[theme].length));title=heads[theme][hi]+' · '+tails[theme][ti];if(title!==previous)break;}if(title===previous)title=heads[theme][(hi+1)%heads[theme].length]+' · '+tails[theme][ti];
 const motto={lol:'上不上分先不说，今晚五个人必须整整齐齐。',basket:'投进算大家的，打铁就当替篮筐做体检。',abstract:'节目可以随缘，人和饭必须按时到齐。'}[theme];
 return {title,motto,ids:team.map(p=>p.id),theme};
}
// Branch stories are pure replayable state machines. Cached rewards and flags are
// deliberately ignored: only validated seed cards and the recorded path are facts.
function branchStory(personId,data){return (data.branchStories||[]).find(s=>s.personId===personId)||null;}
function storyReplay(state,data){
 if(!state||state.version!==data.version||!Array.isArray(state.seedCards)||!Array.isArray(state.history)||typeof state.originKey!=='string'||state.originKey.length>256)throw Error('穿越故事存档已失效');
 const person=enabledPeople(data).find(p=>p.personId===state.personId),story=branchStory(state.personId,data);
 if(!person||!story||state.storyId!==story.id||!Array.isArray(story.nodes)||state.history.length>story.nodes.length)throw Error('找不到这段穿越故事');
 const cards=enabledCards(data,person.theme),byCard=new Map(cards.map(c=>[c.id,c]));
 if(new Set(state.seedCards).size!==state.seedCards.length||state.seedCards.some(id=>!byCard.has(id)))throw Error('故事中的海克斯不属于当前版本');
 const nodes=new Map(story.nodes.map(n=>[n.id,n]));
 let node=nodes.get(story.entry);if(!node)throw Error('故事入口不存在');
 const owned=new Set(state.seedCards),flags={},choices={},rewardLedger=[];
 for(const action of state.history){
  if(!action||action.nodeId!==node.id||node.type==='ending')throw Error('故事路线不完整');
  let next=node.next;
  if(node.type==='choice'){
   const choice=(node.choices||[]).find(c=>c.id===action.choiceId);if(!choice)throw Error('故事选项不存在');
   choices[node.id]=choice.id;
   Object.assign(flags,choice.flags||{});
   for(const id of choice.grantCardIds||[]){
    const card=byCard.get(id);if(!card)throw Error('故事奖励不属于当前版本');
    if(!owned.has(id)){owned.add(id);rewardLedger.push({cardId:id,name:card.name,nodeId:node.id,choiceId:choice.id,source:'story-choice'});}
   }
   next=choice.next;
  }else if(action.choiceId!==null)throw Error('请使用当前故事按钮');
  node=nodes.get(next);if(!node)throw Error('故事下一幕不存在');
 }
 return {story,person,node,flags,choices,ownedCardIds:Array.from(owned),rewardLedger};
}
function storySnapshot(base,data){const d=storyReplay(base,data);return Object.assign({},base,{seedCards:base.seedCards.slice(),history:base.history.map(a=>Object.assign({},a)),nodeId:d.node.id,flags:d.flags,choices:d.choices,ownedCardIds:d.ownedCardIds,rewardLedger:d.rewardLedger});}
function storyStart(personId,data,seedCardIds=[],originKey=''){
 const story=branchStory(personId,data);if(!story)throw Error('这个人物的穿越故事尚未开放');
 return storySnapshot({version:data.version,storyId:story.id,personId,originKey:String(originKey||''),seedCards:seedCardIds.slice(),history:[]},data);
}
function storyValid(state,data){try{storyReplay(state,data);return true;}catch(_){return false;}}
function storyView(state,data){
 const d=storyReplay(state,data),node=d.node;
 const variant=(node.variants||[]).find(v=>Object.keys(v.when||{}).every(k=>d.flags[k]===v.when[k]));
 const own=new Set(d.ownedCardIds);
 return {node:node.id,type:node.type,title:variant&&variant.title!==undefined?variant.title:node.title,
  text:variant&&variant.text!==undefined?variant.text:node.text,
  cardEvents:(node.cardEvents||[]).map(e=>({cardId:e.cardId,owned:own.has(e.cardId),text:own.has(e.cardId)?e.owned:e.unowned})),
  choices:(node.choices||[]).map(c=>({id:c.id,text:c.text,effect:c.effect})),
  ownedCardIds:d.ownedCardIds,rewardLedger:d.rewardLedger,canBack:state.history.length>0,
  isEnding:node.type==='ending',endingId:node.type==='ending'?(variant&&variant.endingId||node.endingId||node.id+':'+(d.flags.route2||'default')):null,
  progress:{current:state.history.length+1,total:d.story.nodes.length},flags:d.flags,storyId:d.story.id,personId:state.personId};
}
function storyChoose(state,nodeId,choiceId,data){
 const d=storyReplay(state,data);if(d.node.id!==nodeId||d.node.type!=='choice'||!(d.node.choices||[]).some(c=>c.id===choiceId))throw Error('这一幕已经切换，请重新选择');
 return storySnapshot(Object.assign({},state,{history:state.history.concat({nodeId,choiceId})}),data);
}
function storyAdvance(state,data){
 const d=storyReplay(state,data);if(d.node.type==='choice'||d.node.type==='ending')throw Error('请先完成当前故事选择');
 return storySnapshot(Object.assign({},state,{history:state.history.concat({nodeId:d.node.id,choiceId:null})}),data);
}
function storyBack(state,data){storyReplay(state,data);if(!state.history.length)return storySnapshot(state,data);return storySnapshot(Object.assign({},state,{history:state.history.slice(0,-1)}),data);}
return {storyStart,storyView,storyChoose,storyAdvance,storyBack,storyValid,branchStory,cardOwners,makeSquadName,enabledPeople,enabledCards,searchPeople,resolvePerson,applyExposure,exposureSample,dimIds,lolDimIds,dimsFor,shuffle,draw,valid,score,similarity,analyze,buildTeam,narrative,recommend,context,selections,questionAt,rankPeople,behaviorFit,artLayout,recordAnswer,squadError,fillSquad,customSquad};
});
