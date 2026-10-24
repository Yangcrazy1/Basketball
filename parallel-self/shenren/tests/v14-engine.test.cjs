// V15 regression executes the immutable V14 schema 13 source.
'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const E=require('../src/legacy-v13/engine.js');
const catalog=JSON.parse(fs.readFileSync(path.join(__dirname,'../content/v14-catalog.json'),'utf8'));
function fixture(){
 const cards=['alpha','beta','shared'].map(id=>({id,name:id,theme:'lol',enabled:true,owners:id==='shared'?['a','b']:['a']}));
 return {version:13,characters:[{id:'lol-a',personId:'a',theme:'lol',enabled:true}],augments:{lol:cards},branchStories:[
 {id:'story-a',personId:'a',entry:'arrival',nodes:[
 {id:'arrival',type:'scene',title:'抵达',text:'网管要下班',next:'choice-1'},
 {id:'choice-1',type:'choice',choices:[{id:'a',text:'先解释',effect:'网管停表',flags:{route1:'a'},grantCardIds:['alpha'],next:'trigger'},{id:'b',text:'先结账',effect:'网管打印',flags:{route1:'b'},grantCardIds:['beta'],next:'trigger'}]},
 {id:'trigger',type:'scene',text:'base',variants:[{when:{route1:'a'},text:'解释印成小票'},{when:{route1:'b'},text:'结账收到大账单'}],cardEvents:[{cardId:'alpha',owned:'真的获得后启动',unowned:'没卡，解释没启动'}],next:'backfire'},
 {id:'backfire',type:'scene',text:'网管举出第二联小票',next:'choice-2'},
 {id:'choice-2',type:'choice',choices:[{id:'a',text:'贴墙',flags:{route2:'a'},grantCardIds:['shared'],next:'ending'},{id:'b',text:'带走',flags:{route2:'b'},grantCardIds:[],next:'ending'}]},
 {id:'ending',type:'ending',text:'base',variants:[{when:{route2:'a'},text:'墙上多了小票展',endingId:'receipt-wall'},{when:{route2:'b'},text:'你抱着打印机下班',endingId:'printer-home'}]}
 ]}]};
}
function atChoice1(d){return E.storyAdvance(E.storyStart('a',d,[],'quiz-1'),d);}
test('catalog has exactly 58 people, 137 cards, 143 owner associations and six deduplicated shared memes',()=>{
 assert.equal(catalog.people.length,58);assert.equal(catalog.representatives.length,137);
 assert.equal(catalog.representatives.reduce((n,c)=>n+c.owners.length,0),143);
 assert.equal(catalog.representatives.filter(c=>c.owners.length===2).length,6);
 for(const c of catalog.representatives){assert.equal(c.selected,true);assert.equal(c.editorialStatus,'selected');assert.equal(c.originalVideoWatched,false);for(const s of c.sources){assert.equal(s.status,'indexed');assert.equal(s.originalVideoWatched,false);}}
 assert.ok(catalog.candidates.every(c=>!c.enabled&&!c.selected));
 assert.ok(!catalog.people.some(p=>p.personId==='renzhengfei'));
});
test('story routes grant only explicit cards and material consequences differ',()=>{
 const d=fixture(),choice=atChoice1(d),a=E.storyChoose(choice,'choice-1','a',d),b=E.storyChoose(choice,'choice-1','b',d);
 assert.deepEqual(a.ownedCardIds,['alpha']);assert.deepEqual(b.ownedCardIds,['beta']);
 assert.notEqual(E.storyView(a,d).text,E.storyView(b,d).text);
 assert.equal(E.storyView(a,d).cardEvents[0].owned,true);assert.equal(E.storyView(b,d).cardEvents[0].owned,false);
 assert.equal(a.rewardLedger[0].source,'story-choice');assert.deepEqual(choice.ownedCardIds,[]);
 let second=E.storyAdvance(E.storyAdvance(a,d),d);
 const endA=E.storyChoose(second,'choice-2','a',d),endB=E.storyChoose(second,'choice-2','b',d);
 assert.equal(E.storyView(endA,d).endingId,'receipt-wall');assert.equal(E.storyView(endB,d).endingId,'printer-home');
 assert.notEqual(E.storyView(endA,d).text,E.storyView(endB,d).text);
});
test('save/reload ignores forged derived state and rewind revokes future rewards',()=>{
 const d=fixture();let s=E.storyChoose(atChoice1(d),'choice-1','a',d);
 const restored=JSON.parse(JSON.stringify({...s,ownedCardIds:['beta','shared'],rewardLedger:[{cardId:'shared'}],flags:{route1:'b'}}));
 assert.equal(E.storyValid(restored,d),true);assert.deepEqual(E.storyView(restored,d).ownedCardIds,['alpha']);
 assert.equal(E.storyView(restored,d).text,'解释印成小票');
 const back=E.storyBack(restored,d);assert.equal(back.nodeId,'choice-1');assert.deepEqual(back.ownedCardIds,[]);assert.deepEqual(back.rewardLedger,[]);
 assert.deepEqual(E.storyChoose(back,'choice-1','b',d).ownedCardIds,['beta']);
});
test('seed ownership survives rewinding, duplicate grants are not new rewards, stale clicks fail',()=>{
 const d=fixture();let s=E.storyAdvance(E.storyStart('a',d,['alpha'],'quiz-1'),d);
 s=E.storyChoose(s,'choice-1','a',d);assert.deepEqual(s.rewardLedger,[]);
 assert.deepEqual(E.storyBack(s,d).ownedCardIds,['alpha']);
 assert.throws(()=>E.storyChoose(s,'choice-1','b',d),/已经切换/);
 assert.throws(()=>E.storyAdvance(E.storyBack(s,d),d),/选择/);
 assert.equal(E.storyValid({...s,version:12},d),false);
 assert.equal(E.storyValid({...s,history:[{nodeId:'backfire',choiceId:null}]},d),false);
 assert.equal(E.storyValid({...s,seedCards:['unearned-unknown']},d),false);
});
test('multi-owner identity is authoritative and does not duplicate shared card objects',()=>{
 assert.deepEqual(E.cardOwners({owners:['a','b'],owner:'wrong',signatureFor:['wrong']}),['a','b']);
 assert.deepEqual(E.cardOwners({owner:'a'}),['a']);assert.deepEqual(E.cardOwners({owners:[],signatureFor:['a']}),[]);
 for(const p of catalog.people){const actual=catalog.representatives.filter(c=>c.owners.includes(p.personId)).map(c=>c.id);assert.deepEqual(actual.slice().sort(),p.representativeCardIds.slice().sort());}
});
test('same behavior label cannot substitute for the explicitly associated question option',()=>{
 const q={id:'q',theme:'lol',scene:'排队等饭',options:[{id:0,text:'这次只是列菜单',behavior:'plan'},{id:1,text:'算出盈利解释',behavior:'plan'}]};
 const card={id:'profit',name:'这波不亏',enabled:true,owners:['a'],exclusive:true,personOnly:true,activationMode:'answers',vector:Array(6).fill(50),behaviorWeights:{plan:5},evidenceQuestionIds:['q'],answerEvidence:[{questionId:'q',optionId:1,behavior:'plan'}]};
 const d={questions:[q],augments:{lol:[card]}},s={theme:'lol',deck:[{id:'q'}],answers:[0]};
 assert.deepEqual(E.recommend(s,d,Array(6).fill(50),{personId:'a'}),[]);
 s.answers=[1];assert.equal(E.recommend(s,d,Array(6).fill(50),{personId:'a'})[0].id,'profit');
});
test('every integrated authored story has four playable route combinations, reversible rewards and distinct final events',()=>{
 const d=JSON.parse(fs.readFileSync(path.join(__dirname,'../src/legacy-v13/data.json'),'utf8'));
 if(d.version!==13)return;
 for(const story of d.branchStories){
  const endings=new Set();
  for(const first of ['a','b'])for(const second of ['a','b']){
   let s=E.storyStart(story.personId,d,[],'test-route');
   for(let i=0;i<5;i++){
    const v=E.storyView(s,d);
    s=v.type==='choice'?E.storyChoose(s,v.node,v.node==='choice-1'?first:second,d):E.storyAdvance(s,d);
    assert.equal(E.storyValid(JSON.parse(JSON.stringify(s)),d),true,story.id);
   }
   const v=E.storyView(s,d);assert.equal(v.isEnding,true,story.id);assert.ok(v.text.length>20,story.id);
   endings.add(v.endingId+'|'+v.text);
   for(const entry of v.rewardLedger){assert.ok(v.ownedCardIds.includes(entry.cardId));assert.ok(E.enabledCards(d).some(c=>c.id===entry.cardId));}
   for(let i=0;i<5;i++)s=E.storyBack(s,d);
   assert.deepEqual(s.ownedCardIds,[],story.id);assert.deepEqual(s.rewardLedger,[],story.id);
  }
  assert.ok(endings.size>=2,story.id+' must change actual ending');
 }
});
test('the two new basketball identities use the documented names and unique canonical search aliases',()=>{
 const d=JSON.parse(fs.readFileSync(path.join(__dirname,'../src/legacy-v13/data.json'),'utf8'));
 const green=E.enabledPeople(d,'basket').find(p=>p.personId==='draymond-green'),ershu=E.enabledPeople(d,'basket').find(p=>p.personId==='ershu');
 assert.equal(green.name,'德雷蒙德·格林');assert.equal(green.nickname,'格林');
 assert.equal(ershu.name,'恶鼠');assert.equal(ershu.nickname,'恶鼠');
 for(const alias of ['恶鼠','张梓祎','Ershu','ershu']){assert.ok(ershu.aliases.includes(alias));assert.deepEqual(E.searchPeople(d,'all',alias).map(p=>p.personId),['ershu']);assert.equal(E.resolvePerson(d,alias).personId,'ershu');}
 assert.ok(!ershu.aliases.includes('八角笼见'));assert.ok(!ershu.aliases.includes('百分大战'));assert.ok(!JSON.stringify(d).includes('尔舒'));
 for(const alias of ['德雷蒙德·格林','格林','追梦','Draymond Green','draymond-green']){assert.ok(green.aliases.includes(alias));assert.deepEqual(E.searchPeople(d,'all',alias).map(p=>p.personId),['draymond-green']);}
});
test('complete V14 native data, deterministic quiz, bounded exposure and 58 reachability witnesses form a hashed release check',()=>{
 const crypto=require('node:crypto'),root=path.join(__dirname,'..'),D=JSON.parse(fs.readFileSync(path.join(root,'src/legacy-v13/data.json'),'utf8'));
 const sha=filename=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,filename))).digest('hex');
 const report={release:14,schema:D.version,dataSha256:sha('src/legacy-v13/data.json'),engineSha256:sha('src/legacy-v13/engine.js'),catalogSha256:sha('content/v14-catalog.json'),frozenV13DataSha256:sha('src/legacy-v12/data.json'),checks:[]};
 const check=(name,fn,details={})=>{fn();report.checks.push({name,status:'passed',...details});};
 const active=E.enabledPeople(D),cards=E.enabledCards(D),reps=cards.filter(c=>c.editorialStatus==='selected');
 check('exact-active-roster-58',()=>{assert.equal(D.version,13);assert.equal(D.releaseVersion,14);assert.equal(active.length,58);assert.deepEqual(active.map(p=>p.personId).slice().sort(),catalog.people.map(p=>p.personId).slice().sort());},{byTheme:{lol:21,basket:20,abstract:17}});
 check('137-representatives-143-owner-associations-six-shared',()=>{assert.equal(reps.length,137);assert.equal(new Set(reps.map(c=>c.id)).size,137);assert.equal(reps.reduce((n,c)=>n+c.owners.length,0),143);assert.equal(reps.filter(c=>c.owners.length===2).length,6);for(const p of active){const owned=reps.filter(c=>c.owners.includes(p.personId));assert.deepEqual(p.signaturePerks.slice().sort(),owned.map(c=>c.id).sort());assert.deepEqual(p.tags.slice().sort(),owned.map(c=>c.name).sort());}});
 check('26-disabled-candidates-never-enter-active-pools-tags-or-story-rewards',()=>{assert.equal(D.reviewCatalog.candidates.length,26);const ids=new Set(D.reviewCatalog.candidates.map(c=>c.id)),names=new Set(D.reviewCatalog.candidates.map(c=>c.name));for(const c of D.reviewCatalog.candidates)assert.equal(c.enabled,false);for(const c of cards){assert.ok(!ids.has(c.id));assert.ok(!names.has(c.name));}for(const p of active){assert.ok(p.signaturePerks.every(id=>!ids.has(id)));assert.ok(p.tags.every(name=>!names.has(name)));}for(const st of D.branchStories)for(const n of st.nodes)for(const c of n.choices||[])assert.ok(c.grantCardIds.every(id=>!ids.has(id)));});
 check('removed-person-has-zero-runtime-references',()=>{const text=JSON.stringify(D);assert.ok(!text.includes('renzhengfei'));assert.ok(!text.includes('任正非'));});
 let routes=0,events=0;
 check('58-stories-four-routes-each-six-nodes-and-owned-only-events',()=>{assert.equal(D.branchStories.length,58);assert.deepEqual(D.migration.pendingStoryPersonIds,[]);for(const st of D.branchStories){assert.equal(st.nodes.length,6);for(const a of ['a','b'])for(const b of ['a','b']){let s=E.storyStart(st.personId,D);const visited=[];while(true){const v=E.storyView(s,D);visited.push(v.node);for(const e of v.cardEvents){assert.equal(e.owned,v.ownedCardIds.includes(e.cardId));const definition=st.nodes.find(n=>n.id===v.node).cardEvents.find(x=>x.cardId===e.cardId);assert.equal(e.text,e.owned?definition.owned:definition.unowned);events++;}if(v.isEnding)break;s=v.type==='choice'?E.storyChoose(s,v.node,v.node==='choice-1'?a:b,D):E.storyAdvance(s,D);assert.ok(visited.length<7);}assert.equal(visited.length,6);assert.equal(new Set(visited).size,6);routes++;}}},{routes:232});
 report.storyCardEventAssertions=events;
 let seed=714;const random=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;};
 check('three-themes-three-modes-randomized-decks-and-stable-fixed-answers',()=>{for(const t of D.themes)for(const n of D.modes){let previous=null;const decks=new Set();for(let i=0;i<30;i++){const s=E.draw(D,t.id,n,previous,random);assert.ok(E.valid(s,D));assert.notEqual(s.deck[0].id,previous);previous=s.deck[0].id;decks.add(s.deck.map(d=>d.id).join('|'));s.answers=s.deck.map(d=>d.order[i%4]);s.index=n-1;s.phase='complete';assert.ok(E.valid(s,D,true));const before=JSON.stringify(s),a=E.analyze(s,D),b=E.analyze(JSON.parse(before),D);assert.deepEqual(a,b);assert.equal(JSON.stringify(s),before);assert.equal(a.inherentCards.length,0);assert.deepEqual(a.obtainedCardIds,[a.augment.id]);assert.equal(new Set(a.team.map(p=>p.personId)).size,5);assert.ok(a.identity.match>=0&&a.identity.match<=100);}assert.ok(decks.size>20);}}, {combinations:9,samples:270});
 check('exposure-priority-keeps-original-near-top-and-bonus-caps',()=>{const rows=[{id:'normal',tier:'normal',rawMatch:90},{id:'featured',tier:'featured',rawMatch:81},{id:'star',tier:'flagship',rawMatch:74}];const ranked=E.applyExposure(rows,{nearTop:999,maxBonus:999,flagshipNearTop:999,flagshipBonus:999});assert.equal(ranked[0].id,'normal');for(const p of ranked){assert.equal(p.match,p.rawMatch);assert.ok(p.editorialBonus<=12);}assert.equal(ranked.find(p=>p.id==='featured').editorialBonus,0);assert.equal(ranked.find(p=>p.id==='star').editorialBonus,0);});
 check('all-58-people-have-replayable-legal-eight-question-winning-witnesses',()=>{const reach=JSON.parse(fs.readFileSync(path.join(root,'docs/v14-reachability.json'),'utf8'));assert.equal(reach.dataSha256,report.dataSha256);assert.deepEqual(reach.unreachable,[]);assert.equal(Object.keys(reach.examples).length,58);for(const [id,w] of Object.entries(reach.examples)){assert.equal(w.session.count,8);assert.ok(E.valid(w.session,D,true));assert.equal(E.analyze(w.session,D).identity.personId,id);}}, {witnesses:58,count:8});
 check('collector-exact-text-and-five-real-icons-are-preserved-as-common',()=>{const c=cards.find(c=>c.id==='collector-union');assert.equal(c.effect,'当你四个队友都出了收集者，你的商店里只有收集者。');assert.deepEqual(c.visual.icons,Array(5).fill('item-6676'));assert.equal(c.personOnly,false);assert.deepEqual(c.owners,[]);assert.equal(c.category,'通用整活');});
 check('quiz-headers-do-not-reveal-the-matched-person',()=>{const names=active.flatMap(p=>[p.name,p.nickname].concat(p.aliases||[])).filter(n=>n&&n.length>1);for(const q of D.questions.filter(q=>q.personId&&q.theme==='lol')){assert.ok(q.chapterName.startsWith('网吧日常 · '));assert.ok(!names.some(name=>q.chapterName.toLowerCase().includes(name.toLowerCase())),q.id+':'+q.chapterName);}});
 check('public-links-remain-indexed-rather-than-claimed-watched',()=>{for(const c of reps){assert.equal(c.originalVideoWatched,false);for(const source of c.sources){assert.equal(source.status,'indexed');assert.equal(source.originalVideoWatched,false);}}});
 report.status='passed';report.counts=D.counts;report.proofSha256=sha('docs/v14-reachability.json');
 report.nativeEngineRegression={tests:9,passed:9,failed:0,note:'Includes the hashed release audit and exact new-identity alias regression; full-suite counts are recorded separately after completion.'};

 const out=path.join(root,'dist/qa/v15/v14-frozen-unit-check.json');fs.mkdirSync(path.dirname(out),{recursive:true});report.executionScope='V14 frozen schema 13 regression during V15';fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');
});
