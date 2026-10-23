// Popularity may break nearby evidence ties; it must not rewrite scores or old histories.
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const E=require('../src/engine.js'),D=require('../src/data.json'),OldE=require('../src/legacy-v11/engine.js'),OldD=require('../src/legacy-v11/data.json');
const root=path.resolve(__dirname,'..');
function rng(seed){return()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;};}

test('flagship priority beats ordinary featured status only inside configured raw-score eligibility',()=>{
 const policy=D.rosterPolicy,rows=[{id:'leader',tier:'normal',rawMatch:90},{id:'featured',tier:'featured',rawMatch:89},{id:'flagship',tier:'flagship',rawMatch:85},{id:'edge',tier:'flagship',rawMatch:78},{id:'far',tier:'flagship',rawMatch:77}],before=JSON.stringify(rows);
 assert.equal(policy.flagshipNearTop,12);assert.equal(policy.flagshipBonus,9);assert.equal(policy.nearTop,5);assert.equal(policy.maxBonus,4);
 const ranked=E.applyExposure(rows,policy);assert.equal(ranked[0].id,'flagship');assert.equal(ranked.find(p=>p.id==='edge').editorialBonus,9);assert.equal(ranked.find(p=>p.id==='far').editorialBonus,0);assert.equal(ranked.find(p=>p.id==='featured').editorialBonus,4);assert.equal(JSON.stringify(rows),before);
 for(const p of ranked){assert.equal(p.match,p.rawMatch);assert.ok(p.editorialBonus<=(p.tier==='flagship'?9:p.tier==='featured'?4:0));}
 const strong=E.applyExposure([{id:'evidence',tier:'normal',rawMatch:90},{id:'popular',tier:'flagship',rawMatch:80}],policy);assert.equal(strong[0].id,'evidence','a ten-point raw evidence advantage survives the nine-point popularity bonus');
 assert.deepEqual(E.applyExposure([],policy),[]);
});

test('the requested traffic stars have the highest exposure tier, and weighted sampling is distinct from score',()=>{
 for(const id of ['faker','uzi','xiaohu','theshy','xiaoxiao','rookie','luobenwei','dasima','fengge','leijun','trump','musk']){const p=E.enabledPeople(D).find(p=>p.personId===id);assert.ok(p,id);assert.equal(p.tier,'flagship',id);assert.equal(p.exposureWeight,D.rosterPolicy.flagshipWeight,id);}
 assert.ok(D.rosterPolicy.flagshipWeight>D.rosterPolicy.featuredWeight);assert.ok(D.rosterPolicy.featuredWeight>D.rosterPolicy.normalWeight);
 const tiny={characters:[{id:'a',personId:'a',enabled:true,theme:'lol',tier:'flagship',exposureWeight:12},{id:'b',personId:'b',enabled:true,theme:'lol',tier:'normal',exposureWeight:1}]},counts={a:0,b:0},random=rng(44),frozen=JSON.stringify(tiny);
 for(let i=0;i<13000;i++)counts[E.exposureSample(tiny,'lol',1,random)[0].id]++;
 assert.ok(counts.a/counts.b>10&&counts.a/counts.b<14,JSON.stringify(counts));assert.equal(JSON.stringify(tiny),frozen);
 assert.equal(new Set(E.exposureSample(tiny,'lol',2,rng(3)).map(p=>p.personId)).size,2);
});

test('schema 11 data and engine are exact frozen V12 source bytes',()=>{
 const hashes={'data.json':'920a24809b3d7e6f6859e9c73b65182d517dfb811a7f4dc858d56fcf64efc2e9','engine.js':'8da99987e320153b8ad80d51afb09be9f5ec3b8ae174eb7d3347348a62dabe2f'};
 for(const [name,want]of Object.entries(hashes)){const bytes=fs.readFileSync(path.join(root,'src/legacy-v11',name));assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'),want,name);}
 assert.equal(OldD.version,11);assert.equal(D.version,12);assert.equal(OldE.enabledPeople(OldD).length,40);
});

test('all archived V12 reachability witnesses replay the original identity and score through the frozen engine',()=>{
 const examples=require('../docs/v12-reachability.json');assert.equal(Object.keys(examples).length,40);
 for(const [id,record]of Object.entries(examples)){assert.ok(OldE.valid(record.session,OldD,true),id);assert.equal(E.valid(record.session,D,true),false,id);const result=OldE.analyze(record.session,OldD);assert.equal(result.identity.personId,id);assert.equal(result.identity.rawMatch,record.raw,id);assert.equal(result.identity.editorialBonus,record.bonus,id);assert.equal(result.team.length,5);}
});
