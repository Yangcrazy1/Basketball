// V15 replay helper: read immutable V14 report and keep new diagnostics outside its archive.
'use strict';
// Run only AFTER the combined TAP process exits. A test must never parse the
// same log file to which its own still-running process is being redirected.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),log=process.argv[2]||'dist/qa/v14/unit-all.tap';
const text=fs.readFileSync(path.join(root,log),'utf8');
assert.match(text.trimEnd().split('\n').at(-1),/^# duration_ms [\d.]+$/,'TAP log is still incomplete; run this command after the suite exits');
const field=name=>{const match=text.match(new RegExp('^# '+name+' (\\d+)$','m'));assert.ok(match,'missing TAP '+name);return Number(match[1]);};
const tests=field('tests'),passed=field('pass'),failed=field('fail');
assert.equal(failed,0,'combined suite has actual failures');assert.equal(passed,tests,'not all tests passed');
const sha=file=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,file))).digest('hex');
const target=path.join(root,'docs/v14-unit-check.json'),report=JSON.parse(fs.readFileSync(target,'utf8'));
assert.equal(report.dataSha256,sha('src/legacy-v13/data.json'));assert.equal(report.engineSha256,sha('src/legacy-v13/engine.js'));
report.combinedSuiteRun={status:'passed',log,sha256:sha(log),tests,passed,failed,note:'Parsed after the combined test process exited; exact completed TAP log retained.'};
const out=path.join(root,'dist/qa/v15/v14-frozen-suite-report.json');fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report.combinedSuiteRun));
