'use strict';
const {test,after}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..'),D=require('../src/data.json'),E=require('../src/engine.js'),B=require('../src/legacy-v13/data.json'),BE=require('../src/legacy-v13/engine.js');
const patches=['kun','369'].map(id=>JSON.parse(fs.readFileSync(path.join(root,'content/v15-'+id+'.json'))));
const sha=file=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,file))).digest('hex'),checks=[];
function audit(name,fn){test(name,()=>{try{fn();checks.push({name,status:'passed'});}catch(error){checks.push({name,status:'failed',reason:error.message});throw error;}});}
function sameExisting(){
 assert.deepEqual(D.characters.slice(0,B.characters.length),B.characters);
 assert.deepEqual(D.questions.slice(0,B.questions.length),B.questions);
 assert.deepEqual(D.branchStories.slice(0,B.branchStories.length),B.branchStories);
 for(const theme of ['lol','basket','abstract'])assert.deepEqual(D.augments[theme].slice(0,B.augments[theme].length),B.augments[theme]);
 assert.deepEqual(D.rosterPolicy,B.rosterPolicy);assert.deepEqual(D.reviewCatalog,B.reviewCatalog);
 assert.equal(fs.readFileSync(path.join(root,'src/engine.js'),'utf8'),fs.readFileSync(path.join(root,'src/legacy-v13/engine.js'),'utf8'));
}
audit('V15 adds exactly Kun and 369 while all 58 previous scoring records, cards, questions, story actions and engine bytes remain frozen',()=>{
 assert.equal(D.version,14);assert.equal(D.releaseVersion,15);sameExisting();
 assert.equal(D.name,'平行宇宙的另一个我');assert.equal(D.description,fs.readFileSync(path.join(root,'content/v15-launch-copy.md'),'utf8').split('发布介绍：')[1].trim().split('\n\n')[0]);
 assert.equal(E.enabledPeople(D).length,60);assert.deepEqual(['lol','basket','abstract'].map(t=>E.enabledPeople(D,t).length),[22,21,17]);
 assert.equal(D.questions.length,340);assert.equal(E.enabledCards(D).length,180);assert.equal(D.branchStories.length,60);
 const reps=E.enabledCards(D).filter(c=>c.editorialStatus==='selected');assert.equal(reps.length,143);assert.equal(reps.reduce((n,c)=>n+c.owners.length,0),149);assert.equal(reps.filter(c=>c.owners.length===2).length,6);
 assert.equal(D.counts.people,60);assert.equal(D.counts.questions,340);assert.equal(D.counts.parodyCards,180);assert.equal(D.counts.representativeCards,143);assert.equal(D.counts.representativeAssociations,149);
});
audit('new identity aliases resolve uniquely, Kun is a cross-theme entertainer and both new people retain ordinary exposure',()=>{
 const kun=E.resolvePerson(D,'caixukun'),dice=E.resolvePerson(D,'369');
 assert.equal(kun.name,'蔡徐坤');assert.equal(kun.nickname,'坤坤');assert.equal(kun.basketballGroup,'跨界整活');assert.equal(kun.roleType,'entertainer');
 for(const alias of ['蔡徐坤','坤坤','KUN','Cai Xukun','caixukun'])assert.deepEqual(E.searchPeople(D,'all',alias).map(p=>p.personId),['caixukun']);
 assert.equal(typeof dice.personId,'string');assert.equal(dice.name,'369');assert.equal(dice.nickname,'369');assert.deepEqual(dice.roles,[0]);
 for(const alias of ['369','白家浩','Bai Jiahao','骰子上单'])assert.deepEqual(E.searchPeople(D,'all',alias).map(p=>p.personId),['369']);
 for(const p of [kun,dice]){assert.equal(p.tier,'normal');assert.equal(p.exposureWeight,1);assert.equal(p.spotlight,false);}
});
audit('six new representative cards have exact answer-option evidence, coherent ownership and the six dedicated V15 illustrations',()=>{
 const sheets=JSON.parse(fs.readFileSync(path.join(root,'assets/rich-perk-atlases.json')));assert.ok(sheets[6]);assert.ok(fs.statSync(path.join(root,'assets',sheets[6].asset)).size>1000);
 for(const [index,patch]of patches.entries()){
  const p=E.resolvePerson(D,patch.person.personId),cards=E.enabledCards(D).filter(c=>c.owners.includes(p.personId));
  assert.equal(cards.length,3);assert.deepEqual(p.signaturePerks,cards.map(c=>c.id));assert.deepEqual(p.tags,cards.map(c=>c.name));
  for(const [i,c]of cards.entries()){
   assert.deepEqual(c.owners,[p.personId]);assert.equal(c.activationMode,'answers');assert.ok(c.exclusive&&c.personOnly);assert.equal(c.preferClassic,true);assert.equal(c.visual,undefined);assert.deepEqual(c.classicSprite,{sheet:6,cell:index*3+i});
   assert.ok(c.evidenceQuestionIds.length>=2);assert.ok(c.answerEvidence.length>=2);
   for(const evidence of c.answerEvidence){const q=D.questions.find(q=>q.id===evidence.questionId),o=q.options.find(o=>o.id===evidence.optionId);assert.equal(q.personId,p.personId);assert.ok(o.cardNames.includes(c.name));assert.equal(o.behavior,evidence.behavior);assert.equal(c.behaviorWeights[o.behavior],5);assert.equal(p.optionAffinities[q.id][String(o.id)],5);}
  }
 }
 const dice=D.augments.lol.find(c=>c.id==='v15-369-1');assert.equal(dice.sourceStatus,'partial_context_only');assert.equal(dice.fanMade,true);assert.equal(dice.sources[0].contextOnly,true);assert.equal(dice.sources[0].originalVideoWatched,false);
 for(const id of ['v15-369-2','v15-369-3']){const card=D.augments.lol.find(c=>c.id===id);assert.equal(card.sourceStatus,'indexed');assert.ok(card.sources.length>0);assert.ok(card.sources.every(s=>s.status==='indexed'&&s.originalVideoWatched===false));}
 const qs=D.questions.slice(B.questions.length);assert.equal(qs.length,8);
 for(const q of qs){assert.equal(q.options.length,4);for(const o of q.options){assert.ok(!['蔡徐坤','坤坤','白家浩'].some(name=>q.title.includes(name)||o.text.includes(name)));if(q.theme==='lol'){assert.deepEqual(Object.keys(o.signals).sort(),E.lolDimIds.slice().sort());assert.ok(Object.values(o.signals).every(n=>n>=0&&n<=100));}else assert.ok(o.value>=1&&o.value<=4);}}
 assert.deepEqual(qs.filter(q=>q.theme==='lol').map(q=>q.stage),[0,1,2,3]);assert.ok(qs.filter(q=>q.theme==='lol').every(q=>!q.chapterName.includes('369')));
});
audit('both new stories have four complete reversible routes, genuinely different endings and only explicit earned cards',()=>{
 for(const pid of ['caixukun','369']){
  const story=D.branchStories.find(s=>s.personId===pid),endings=new Set();assert.equal(story.nodes.length,6);
  for(const first of ['a','b'])for(const second of ['a','b']){
   let s=E.storyStart(pid,D,[],'v15-story-test');assert.deepEqual(s.ownedCardIds,[]);
   const visited=[];
   while(true){const v=E.storyView(s,D);visited.push(v.node);for(const event of v.cardEvents){assert.equal(event.owned,v.ownedCardIds.includes(event.cardId));const definition=story.nodes.find(n=>n.id===v.node).cardEvents.find(e=>e.cardId===event.cardId);assert.equal(event.text,event.owned?definition.owned:definition.unowned);}if(v.isEnding){endings.add(v.endingId+'|'+v.text);break;}s=v.type==='choice'?E.storyChoose(s,v.node,v.node==='choice-1'?first:second,D):E.storyAdvance(s,D);assert.ok(E.storyValid(JSON.parse(JSON.stringify(s)),D));assert.ok(visited.length<7);}
   assert.equal(visited.length,6);assert.ok(s.ownedCardIds.length>=1&&s.ownedCardIds.length<=2);for(const reward of s.rewardLedger)assert.ok(s.ownedCardIds.includes(reward.cardId));
   for(let i=0;i<5;i++)s=E.storyBack(s,D);assert.deepEqual(s.ownedCardIds,[]);assert.deepEqual(s.rewardLedger,[]);
  }
  assert.ok(endings.size>=2);
 }
});
audit('all 58 historical schema13 fixed inputs replay through the exact frozen engine with original identities, raw scores and bonuses',()=>{
 const proof=JSON.parse(fs.readFileSync(path.join(root,'docs/v14-reachability.json')));assert.equal(proof.dataSha256,sha('src/legacy-v13/data.json'));assert.equal(Object.keys(proof.examples).length,58);
 for(const [id,w]of Object.entries(proof.examples)){assert.ok(BE.valid(w.session,B,true));assert.equal(E.valid(w.session,D,true),false);const r=BE.analyze(w.session,B);assert.equal(r.identity.personId,id);assert.equal(r.identity.rawMatch,w.raw);assert.equal(r.identity.editorialBonus,w.bonus);assert.equal(r.ranked.length,B.characters.filter(p=>p.enabled!==false&&p.theme===w.session.theme).length);assert.ok(!r.ranked.some(p=>p.personId==='caixukun'||p.personId==='369'));assert.deepEqual(BE.analyze(JSON.parse(JSON.stringify(w.session)),B),r);}
});
audit('all 60 current people, including separate legal eight-question Kun and 369 examples, can actually be returned by the native engine',()=>{
 const proof=JSON.parse(fs.readFileSync(path.join(root,'docs/v15-reachability.json')));assert.equal(proof.dataSha256,sha('src/data.json'));assert.deepEqual(proof.unreachable,[]);assert.equal(Object.keys(proof.examples).length,60);
 for(const [id,w]of Object.entries(proof.examples)){assert.ok(E.valid(w.session,D,true));assert.equal(E.analyze(w.session,D).identity.personId,id);}
 for(const id of ['caixukun','369']){const w=proof.examples[id];assert.equal(w.session.count,8);assert.ok(w.session.deck.some(d=>D.questions.find(q=>q.id===d.id).personId===id));}
});
audit('all nine native theme/mode combinations randomize, deterministic answers remain stable and common Collector wording stays intact',()=>{
 let seed=1515;const random=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;};
 for(const theme of D.themes)for(const count of D.modes){let previous=null;const decks=new Set();for(let k=0;k<20;k++){const s=E.draw(D,theme.id,count,previous,random);assert.ok(E.valid(s,D));assert.notEqual(s.deck[0].id,previous);previous=s.deck[0].id;decks.add(s.deck.map(d=>d.id).join('|'));s.answers=s.deck.map(d=>d.order[k%4]);s.index=count-1;s.phase='complete';assert.ok(E.valid(s,D,true));const r=E.analyze(s,D);assert.deepEqual(E.analyze(JSON.parse(JSON.stringify(s)),D),r);assert.deepEqual(r.obtainedCardIds,[r.augment.id]);assert.deepEqual(r.inherentCards,[]);assert.equal(new Set(r.team.map(p=>p.personId)).size,5);}assert.ok(decks.size>10);}
 const c=D.augments.lol.find(c=>c.id==='collector-union');assert.equal(c.category,'通用整活');assert.equal(c.effect,'当你四个队友都出了收集者，你的商店里只有收集者。');assert.deepEqual(c.visual.icons,Array(5).fill('item-6676'));
});
after(()=>{const report={release:15,schema:D.version,status:checks.length<7?'incomplete':checks.every(c=>c.status==='passed')?'passed':'failed',expectedChecks:7,completedChecks:checks.length,dataSha256:sha('src/data.json'),engineSha256:sha('src/engine.js'),frozenSchema13DataSha256:sha('src/legacy-v13/data.json'),frozenSchema13EngineSha256:sha('src/legacy-v13/engine.js'),reachabilitySha256:sha('docs/v15-reachability.json'),counts:D.counts,checks};fs.writeFileSync(path.join(root,'docs/v15-unit-check.json'),JSON.stringify(report,null,2)+'\n');});
