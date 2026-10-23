"""Publish an immutable V11 round preview; never change production entry points."""
from pathlib import Path
import subprocess,os,tempfile,json,hashlib,argparse
R=Path(__file__).resolve().parents[3];A=R/'parallel-self/shenren';W=A/'dist/web'
p=argparse.ArgumentParser();p.add_argument('--round',type=int,required=True);n=p.parse_args().round
def git(*args,input=None,env=None):return subprocess.run(['git',*args],cwd=R,input=input,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True).stdout.decode().strip()
parent=git('rev-parse','refs/heads/codex/parallel-self-web');assert git('ls-remote','origin','refs/heads/gh-pages').split()[0]==parent
meta=json.loads((A/'dist/web-build.json').read_text());base=f'preview/v11/r{n}'
with tempfile.TemporaryDirectory() as tmp:
 env=os.environ.copy();env['GIT_INDEX_FILE']=tmp+'/index';git('read-tree',parent,env=env)
 def add(path,body):
  h=git('hash-object','-w','--stdin',input=body);git('update-index','--add','--cacheinfo','100644',h,path,env=env)
 for f in W.rglob('*'):
  if f.is_file():add(base+'/'+f.relative_to(W).as_posix(),f.read_bytes())
 qa=A/'dist/qa/v11'
 if qa.exists():
  for f in qa.glob(f'round{n}-*.png'):add(base+'/screenshots/'+f.name,f.read_bytes())
 meta.update(round=n,source_commit=git('rev-parse','HEAD'),production_unchanged=True);add(base+'/build-info.json',(json.dumps(meta,ensure_ascii=False,indent=2)+'\n').encode())
 tree=git('write-tree',env=env)
 # Prove production files were not changed by the preview deployment.
 for path in ['index.html','play/index.html','build-info.json','download/index.html']:
  assert git('rev-parse',parent+':'+path)==git('rev-parse',tree+':'+path),path
 commit=git('commit-tree',tree,'-p',parent,input=f'Preview V11 round {n}; retain V10 production\n'.encode());git('update-ref','refs/heads/codex/parallel-self-web',commit,parent);git('push','origin','codex/parallel-self-web','codex/parallel-self-web:refs/heads/gh-pages')
 print(json.dumps(dict(url='https://yangcrazy1.github.io/Basketball/'+base+'/',deployment=commit,**meta),ensure_ascii=False,indent=2))
