// V14 native reachability proof. Synthetic counts are not claimed as user probabilities.
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),D=require('../src/data.json'),E=require('../src/engine.js');
const root=path.resolve(__dirname,'..');function rng(seed){return()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;};}function complete(theme,n,random=rng(4)){const s=E.draw(D,theme,n,null,random);s.answers=s.deck.map(()=>Math.floor(random()*4));return s;}
function optionAppeal(p,q,o){
 const behavior=(p.behaviorWeights[o.behavior]||0)/5*35,scene=(p.optionAffinities?((p.optionAffinities[q.id]&&p.optionAffinities[q.id][String(o.id)])||0):((p.answerAffinities&&p.answerAffinities[q.id]&&p.answerAffinities[q.id][o.behavior])||0))/5*25;
 let fit=0;
 if(q.theme==='lol')fit=E.lolDimIds.reduce((n,dim,i)=>n+100-Math.abs(p.vector[i]-o.signals[dim]),0)/6;
 else fit=100-Math.abs(p.vector[E.dimIds.indexOf(q.dim)]-(o.value-1)*100/3);
 return behavior+scene+fit*.4;
}
function guidedDeck(p,count,variant,random){
 const bank=D.questions.filter(q=>q.enabled&&q.theme===p.theme),rivals=E.enabledPeople(D,p.theme).filter(x=>x.personId!==p.personId);
 const utility=q=>Math.max(...q.options.map(o=>optionAppeal(p,q,o)-.7*Math.max(...rivals.map(r=>optionAppeal(r,q,o)))));
 let qs=[];
 if(p.theme==='lol'){
  const groups=[...new Set(bank.map(q=>q.series+':'+q.chapter))].map(key=>bank.filter(q=>q.series+':'+q.chapter===key).sort((a,b)=>a.stage-b.stage)).map(items=>({items,value:items.reduce((n,q)=>n+utility(q),0)})).sort((a,b)=>b.value-a.value);
  const chosen=[];for(let i=0;i<count/4;i++){const pool=groups.filter(g=>!chosen.includes(g)),offset=variant===0?0:Math.floor(random()*Math.min(pool.length,variant<10?4:9));chosen.push(pool[offset]);}qs=[].concat(...chosen.map(g=>g.items));
 }else{
  const groups=E.dimIds.map(dim=>bank.filter(q=>q.dim===dim).map(q=>({q,value:utility(q)})).sort((a,b)=>b.value-a.value));
  const extras=E.dimIds.map((dim,i)=>({dim,value:(groups[i][1]||groups[i][0]).value})).sort((a,b)=>b.value-a.value).map(x=>x.dim);
  const order=variant>0?E.shuffle(extras,random):extras;
  for(let i=0;i<E.dimIds.length;i++){const pool=groups[i].slice(),n=Math.floor(count/6)+(order.slice(0,count%6).includes(E.dimIds[i])?1:0);for(let j=0;j<n;j++){const k=variant===0?0:Math.floor(random()*Math.min(pool.length,variant<12?3:7));qs.push(pool.splice(k,1)[0].q);}}
  qs=E.shuffle(qs,random);
 }
 const s={version:D.version,theme:p.theme,series:'all',count,deck:qs.map(q=>({id:q.id,order:E.shuffle(q.options.map(o=>o.id),random)})),answers:[],index:count-1,phase:'complete',date:'2026-10-24T00:00:00.000Z'};
 s.answers=qs.map(q=>q.options.slice().sort((a,b)=>optionAppeal(p,q,b)-optionAppeal(p,q,a))[0].id);
 assert.ok(E.valid(s,D,true));return s;
}
function inspectTarget(s,p){
 const ranked=E.rankPeople(s,D,E.score(s,D)),index=ranked.findIndex(x=>x.personId===p.personId),own=ranked[index],opponent=ranked.find(x=>x.personId!==p.personId),margin=own.rawMatch+own.editorialBonus-opponent.rawMatch-opponent.editorialBonus;
 return {quality:margin*100+own.rawMatch*.01-index*.00001,margin,rank:index+1,own,opponent,won:index===0};
}
function proveReachability(){
 const random=rng(1),examples={},randomCounts={},failures={},best={};
 function remember(s,ranked,method){const p=ranked[0];if(!examples[p.personId]){let replay=Object.assign({},JSON.parse(JSON.stringify(s)),{answers:Array(s.count).fill(null),index:0,phase:'quiz'});for(const answer of s.answers)replay=E.recordAnswer(replay,D,replay.deck[replay.index].id,answer).session;assert.equal(replay.phase,'complete');examples[p.personId]={person:p.personId,raw:p.rawMatch,bonus:p.editorialBonus,method,session:replay};}}
 for(const t of D.themes){randomCounts[t.id]={};for(let i=0;i<1500;i++){const s=complete(t.id,8,random),ranked=E.rankPeople(s,D,E.score(s,D)),id=ranked[0].personId;randomCounts[t.id][id]=(randomCounts[t.id][id]||0)+1;remember(s,ranked,'random-eight-question');}}
 for(const p of E.enabledPeople(D)){
  if(examples[p.personId])continue;
  let won=false;
  for(const count of [8,16,24]){
   for(let v=0;v<(count===8?32:12);v++){
    const s=guidedDeck(p,count,v,random);let state=inspectTarget(s,p);
    if(!best[p.personId]||state.quality>best[p.personId].quality)best[p.personId]=Object.assign({count},state);
    if(state.won){remember(s,E.rankPeople(s,D,E.score(s,D)),'target-evidence');won=true;break;}
    for(let pass=0;pass<3&&!state.won;pass++){
     let changed=false;
     for(const i of E.shuffle(Array.from({length:count},(_,i)=>i),random)){
      const q=D.questions.find(q=>q.id===s.deck[i].id),original=s.answers[i];let choice=original,choiceState=state;
      for(const o of q.options){if(o.id===original)continue;s.answers[i]=o.id;const trial=inspectTarget(s,p);if(trial.quality>choiceState.quality){choice=o.id;choiceState=trial;}if(trial.won){choice=o.id;choiceState=trial;break;}}
      s.answers[i]=choice;if(choice!==original)changed=true;state=choiceState;
      if(!best[p.personId]||state.quality>best[p.personId].quality)best[p.personId]=Object.assign({count},state);
      if(state.won){remember(s,E.rankPeople(s,D,E.score(s,D)),'target-evidence-answer-search');won=true;break;}
     }
     if(!changed)break;
    }
    if(won)break;
   }
   if(won)break;
  }
  if(!won){const b=best[p.personId];failures[p.personId]={bestRank:b.rank,raw:b.own.rawMatch,bonus:b.own.editorialBonus,weightedMargin:b.margin,blockedBy:b.opponent.personId,opponentRaw:b.opponent.rawMatch,opponentBonus:b.opponent.editorialBonus,count:b.count};}
 }
 const ids=E.enabledPeople(D).map(p=>p.personId),unreachable=ids.filter(id=>!examples[id]);
 // Keep a replayable, engine-validated witness for every successful identity.
 for(const [id,x] of Object.entries(examples)){assert.ok(E.valid(x.session,D,true),id);const winner=E.analyze(x.session,D).identity;assert.equal(winner.personId,id);assert.ok(x.session.deck.every(d=>D.questions.find(q=>q.id===d.id).enabled),id);}
 return {version:14,schema:D.version,dataSha256:require('node:crypto').createHash('sha256').update(fs.readFileSync(path.join(root,'src/data.json'))).digest('hex'),enabledPeople:ids.length,randomRunsPerTheme:1500,methodNote:'Seeded uniform-choice synthetic simulations plus guided valid evidence sessions; counts are not measured user probabilities.',randomCounts,unreachable,failures,examples};
}

const report=proveReachability();fs.writeFileSync(path.join(root,'docs/v14-reachability.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({people:report.enabledPeople,proved:Object.keys(report.examples).length,unreachable:report.unreachable,failures:report.failures,dataSha256:report.dataSha256}));if(report.unreachable.length)process.exitCode=1;
