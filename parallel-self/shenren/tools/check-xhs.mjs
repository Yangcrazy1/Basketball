// Run using: node --expose-internals tools/check-xhs.mjs
// Uses the parser shipped inside this Node runtime; no build dependency is added.
import {createRequire} from 'node:module';import fs from 'node:fs';import path from 'node:path';
const require=createRequire(import.meta.url),acorn=require('internal/deps/acorn/acorn/dist/acorn'),root=path.resolve(path.dirname(new URL(import.meta.url).pathname),'..');
for(const file of ['data.js','engine.js','platform.js','app.js']){acorn.parse(fs.readFileSync(path.join(root,'dist/xhs',file),'utf8'),{ecmaVersion:2017,sourceType:'script'});console.log('PASS ES2017:',file);}
