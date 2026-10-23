(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.ShenrenEngine=factory();})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const dimIds=['social','explore','empathy','action','order','express'];
function random(){if(typeof crypto!=='undefined'&&crypto.getRandomValues){const a=new Uint32Array(1);crypto.getRandomValues(a);return a[0]/4294967296;}return Math.random();}
function shuffle(list,rng=random){const a=list.slice();for(let i=a.length-1;i>0;i--){const j=Math.floor(rng()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
function draw(data,theme,count,previousFirst=null,rng=random,series='all'){
 if(!data.themes.some(t=>t.id===theme)||!data.modes.includes(count))throw Error('不支持的主题或题量');
 if(theme==='lol'&&!['all','hex','rift'].includes(series))throw Error('不支持的联盟系列');
 const extra=new Set(shuffle(dimIds,rng).slice(0,count%6));let chosen=[];
 dimIds.forEach(dim=>{const bank=data.questions.filter(q=>q.theme===theme&&q.dim===dim&&(theme!=='lol'||series==='all'||q.series===series)),n=Math.floor(count/6)+(extra.has(dim)?1:0);if(bank.length<n)throw Error('题库不足');chosen.push(...shuffle(bank,rng).slice(0,n));});
 chosen=shuffle(chosen,rng);if(chosen[0].id===previousFirst){[chosen[0],chosen[1]]=[chosen[1],chosen[0]];}
 return {version:data.version,theme,series:theme==='lol'?series:'all',count,augmentRerolls:0,deck:chosen.map(q=>({id:q.id,order:shuffle(q.options.map(o=>o.id),rng)})),answers:Array(count).fill(null),index:0,phase:'quiz',augmentOptions:shuffle(data.augments[theme],rng).slice(0,3).map(a=>a.id),date:new Date().toISOString()};
}
function valid(session,data,complete=false){
 if(!session||session.version!==data.version||!data.themes.some(t=>t.id===session.theme)||!data.modes.includes(session.count)||!Array.isArray(session.deck)||session.deck.length!==session.count||!Array.isArray(session.answers)||session.answers.length!==session.count)return false;
 if(new Set(session.deck.map(d=>d&&d.id)).size!==session.count)return false;
 if(!dimIds.every(dim=>session.deck.some(d=>data.questions.some(q=>q.id===d?.id&&q.dim===dim))))return false;
 if(!Array.isArray(session.augmentOptions)||session.augmentOptions.length!==3||new Set(session.augmentOptions).size!==3||!session.augmentOptions.every(id=>data.augments[session.theme].some(a=>a.id===id)))return false;
 return session.deck.every((item,i)=>{const q=data.questions.find(q=>q.id===item?.id&&q.theme===session.theme&&(session.theme!=='lol'||!session.series||session.series==='all'||q.series===session.series));return q&&Array.isArray(item.order)&&item.order.length===4&&new Set(item.order).size===4&&item.order.every(v=>q.options.some(o=>o.id===v))&&((!complete&&session.answers[i]===null)||q.options.some(o=>o.id===session.answers[i]));});
}
function score(session,data){if(!valid(session,data,true))throw Error('请完成本轮全部题目');return dimIds.map(dim=>{const values=session.deck.flatMap((d,i)=>{const q=data.questions.find(q=>q.id===d.id);return q.dim===dim?[q.options.find(o=>o.id===session.answers[i]).value]:[];});if(!values.length)throw Error('维度覆盖不足');return Math.round((values.reduce((a,b)=>a+b,0)/values.length-1)/3*100);});}
function similarity(a,b){return Math.round(100*(1-a.reduce((s,v,i)=>s+Math.abs(v-b[i]),0)/600));}
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
 if(!best)throw Error('角色池不足以组成五人队');return best.slots.map((p,i)=>({...p,slot:i,isYou:p.id===identity.id,match:similarity(vector,p.vector),naturalRole:p.roles.includes(i)}));
}
const stories={
 uzi:['平行 S8，轮到你改写结局。','在这条架空时间线，你变成了污渍。决胜局，对面的飞科锁下加里奥，镜头里所有人都以为这又是熟悉的剧本。你却在最后一波侧身躲开控制，把输出打到了结算页面。','金色的雨落下。主持人还在问“历史第一 ADC”，你已经把问题推进到“英雄联盟的 GOAT”。收集者不是决定，敢不敢接下这场比赛才是。'],
 xiaohu:['这个宇宙，没有不属于你的季节。','你变成了销户，赛场的日历被你改成了“春一月”到“春十二月”。总决赛打到最后一局，你把边线、团战与笑容一起拉满。','奖杯旁边多了一块恒温器：全宇宙的春天，今天由中路负责。'],
 dasima:['从讲解席，走到冠军颁奖台。','你变成了大司马。架空决赛里，所有人还在质疑你的路线，你已经画出了第三条“正方形打野”轨迹。最后一波不是嘴上有说法，是地图真的照着你的说法走。','奖杯被你端成一件教学道具。冠军公开课第一句话：先别急，这波我慢慢讲。'],
 theshy:['上路这条线，通向另一个结局。','你化身 TheShy，在架空决赛把一条边线打成了自己的独立宇宙。对手终于凑齐五个人来围你，你的队友刚好把另一边的主场拆完。','赛后大家讨论阵型，你在战术板上画了一条线：这里，也是一种答案。'],
 faker:['这一次，时间站在你这一边。','你化身飞科。平行决赛进入最安静的十秒，你等到所有技能交错的缝隙，再把那个属于自己的窗口按了下去。','第五次、第六次都不再是问题。这个宇宙的传奇，是把每一个小回合认真打完。'],
 lebron:['乐邦詹士，膝盖先于战术板反应。','平行总决赛最后一攻，你变成了乐邦詹士。漏判出现，全场进入表情加载页，你用一个跪地默剧把节目效果拉满。随后你站起来，追帽、推进、压哨出手一气呵成。','球进灯亮。这个宇宙的“虎扑式”搞笑评分写着：10 分，建议把膝盖也算进首发。你拿走的是这条时间线的 GOAT 剧本。'],
 curry:['停车场，正式进入你的射程表。','你变成了库里。平行总决赛的三分线被搬到停车场，大家还在找停车位，你已经借掩护转身出手。篮球在空中待得像一趟跨省快递。','球落网，晚安手势安排上。这个宇宙规定：只要你站得稳，想象力就有出手权。'],
 kobe:['凌晨的第一盏灯，由你点亮。','你化身科比。平行总决赛最后一节，你把练过无数遍的动作放进那个最需要答案的回合。全场的声音很大，你听见的只有脚步和球落网。','镜头切到空荡的训练馆：这里，早就为这个结局留过灯。'],
 jokic:['马儿没来，但传球已经到了。','你化身约老师。平行总决赛开打前，大家发现战术板背面是一张木马旋转图。第三节开始，对手才意识到每个人都被你转到了正确的位置。','你拿着奖杯问能不能早点回去。这个宇宙的中锋，把轻描淡写打成了史诗。'],
 fengge:['你去过的地方，地图还没来得及加载。','你变成了峰哥，揣着一张平行宇宙通行证出发。路边一间小卖部卖的是“如果当年”，你没急着买，而是拉老板聊完了另一个人生。','最后你带回来五个人和一大串故事。宇宙没被你讲明白，但你的这一集已经够好看。'],
 huge:['来，整个宇宙先别关。','你变成了虎哥。平行东北的路灯突然集体熄灭，你一抬手，现场五个人自带开机音效。围观群众还没弄清第一幕，第二幕已经顺着街口开过去了。','城市把“节目效果维护员”奖章发给你。你问：奖章能不能再配一瓶好果汁？'],
 daoge:['好果汁，这回送到了银河边上。','你变成了刀哥。一封星际补给单把你带到银河边，你发现全宇宙都在排队等下一段名场面。你把好果汁放上桌，先把五个队友招呼齐。','这场没有既定台词，只有现场反应。你的平行身份，是让离谱故事继续发生的人。'],
 lecturer:['讲台很小，宇宙很大。','你变成了美国讲师。平行世界里每条街都能临时开课，你把一次普通的绕路讲成了跨宇宙社会观察。五名队友听着听着，竟然真的找到了一条回家的路。','毕业证只有一句话：人生没有白走的路，有时候只是又加了一节课。'],
 geyou:['你没拯救宇宙，你让它坐下休息了。','你变成了葛优。平行世界不停催进度，所有人都在找下一场大事。你先在沙发上挪出四个位置，把队友一个个招呼坐下。','宇宙最后没爆炸。它只是承认：有些重要的事，要坐稳了才能想明白。']
};
function narrative(identity,theme,profile,series='all',augment=null){
 if(theme==='lol'&&series==='hex'){
  if(identity.personId==='uzi')return ['平行 S8，嚎哭深渊也能下起金色的雨。','在这条架空时间线，S8 决赛开在海克斯大乱斗的桥上。你变成污渍，对面的飞科又锁下加里奥。全场以为结局早已写好，你却用一波天赋联动和极限走位，把输出打到了结算页。','金色的雨落下。历史第一 ADC 只是起点，这个宇宙的观众把英雄联盟 GOAT 的剧本交给了你。收集者先收好，奖杯也别落下。'];
  if(identity.personId==='dasima')return ['这座桥，终于听懂了你的说法。','你化身大司马，走进一场架空海克斯冠军赛。随机给出的天赋看起来不搭，你边讲边把它连成一套“正方形大乱斗”。全队从一脸疑惑，打到一起点头。','最后一波结束，你端着奖杯继续讲：先别急，这次真的不是失误，是教材。冠军席，被你办成了一间公开课堂。'];
  if(identity.personId==='xiaohu')return ['嚎哭深渊，今天全桥入春。','你化身销户，进入一条只过春天的海克斯时间线。桥上冰雪还没化，天赋组合已经被你运营到舒服的位置。决胜团开打，所有人终于明白谁在掌握季节。','这个宇宙的奖杯旁多了一台恒温器。不是每年春天很强，是今天由你宣布春天。'];
  return [identity.name+'，这一座桥由你改写。','你化身'+identity.name+'，站上平行宇宙的海克斯大乱斗冠军桥。随机天赋没有给你标准答案，你用'+profile.name+'的反应，把一次普通抽签变成了自己的打法。'+(augment?'这一局，'+augment.name+'也写进了你的名场面。':''),'对手记住的也许是连招，队友记住的是这一局有人敢把可能性试出来。奖杯旁边，还有一枚属于这个宇宙的 GOAT 彩蛋。'];
 }
 const own=stories[identity.personId];if(own)return own;return theme==='lol'?[`${identity.name}，这次由你接下决胜局。`,`你化身${identity.name}，走进一条结局尚未写下的平行赛道。对手准备好了熟悉的套路，你用${profile.name}的打法把这一局带到了新的节奏。`,'奖杯不是剧本的终点。五个人愿意再开一局，才是这个宇宙最好的彩蛋。']:theme==='basket'?[`${identity.name}，今天的名场面由你签收。`,`你化身${identity.name}。平行总决赛把所有戏剧性都留到了末节，你把熟悉的动作和没试过的选择拼成了自己的答案。`,'这个宇宙的虎扑式搞笑评分给出满分：有人负责数据，有人负责让整场值得重看。']:[`${identity.name}，你在另一个宇宙上线了。`,`你化身${identity.name}。普通的一天被平行宇宙拧开了一个口子，你用${profile.name}的方式，把五个看似不搭的人放进同一段故事。`,'故事没有标准答案。能把自己的那一集过得有声有色，也是一种隐藏天赋。'];}
function analyze(session,data,augmentId=null){
 const vector=score(session,data),pool=data.characters.filter(p=>p.theme===session.theme),ranked=pool.map(p=>({...p,match:similarity(vector,p.vector)})).sort((a,b)=>b.match-a.match||a.id.localeCompare(b.id));
 const identity=ranked[0],code=[0,1,2].map(i=>vector[i]>=50?'1':'0').join(''),profile=data.profiles.find(p=>p.id===data.familyCodes[code]),augment=data.augments[session.theme].find(a=>a.id===augmentId)||null;
 const evidence=dimIds.map((dim,di)=>{const choices=session.deck.flatMap((d,i)=>{const q=data.questions.find(q=>q.id===d.id),o=q.options.find(o=>o.id===session.answers[i]);return q.dim===dim?[{id:q.id,scene:q.scene,title:q.title,choice:o.text,value:o.value}]:[];});choices.sort((a,b)=>Math.abs(b.value-2.5)-Math.abs(a.value-2.5));return {dim,coordinate:vector[di],...choices[0]};});
 return {vector,identity,ranked,profile,augment,team:buildTeam(vector,pool,identity,augment),story:narrative(identity,session.theme,profile,session.series,augment),evidence,coverage:dimIds.map(dim=>session.deck.filter(d=>data.questions.find(q=>q.id===d.id).dim===dim).length)};
}
return {dimIds,shuffle,draw,valid,score,similarity,analyze,buildTeam,narrative};
});
