"""Lossy format compression only; image artwork was generated with image_gen."""
from pathlib import Path
import shutil,json,base64,hashlib
from PIL import Image
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
files=['3476e45d-81c2-4f87-87ac-67271c2ed345','b2363383-8837-43c2-b5cf-261f2f74b2ce','cc74dc20-4760-4a15-8e11-0c68fa5d5d3d','a49fd950-2450-4996-97df-b0c062c04cbe','49294dcf-d077-4a0f-a43c-31caf7554595','fd48a3dd-2b21-4c9c-b89e-213025d3f5de','7d76110f-1303-4620-bfe2-8bf90550935e','ebe7a209-b08c-494b-9442-31803ce119a0','6740d4d6-4c88-4d36-aa2d-c8ce7c9d26cb','922841c4-e240-448e-8950-c8d0e639fd0f','74b29561-18ca-4623-930f-2d8583aeb470']
groups=[['uzi','dasima','xiaohu','theshy'],['faker','clearlove','jackeylove','doinb'],['pdd','ming','ning','knight'],['lebron','curry','jordan','kobe'],['durant','jokic','westbrook','harden'],['yaoming','shaq','duncan','garnett'],['doncic','butler','rodman','baolan'],['huchenfeng','huge','daoge','sunxiaochuan'],['geyou','jackie','wanglaoju','luobenwei'],['zhouyi','papi','baike','fengge'],['meiko','letme',None,'mascot']]
atlas={'sheets':[],'portraits':{}}
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=browser.new_page()
 for i,(uuid,ids) in enumerate(zip(files,groups)):
  original=Path('/workspace/generated_images')/('exec-'+uuid+'.png');asset=ROOT/'assets'/f'portraits-v6-{i}.webp'
  data='data:image/png;base64,'+base64.b64encode(original.read_bytes()).decode()
  out=page.evaluate('''async src=>{const im=new Image();im.src=src;await im.decode();const c=document.createElement('canvas');c.width=im.width;c.height=im.height;c.getContext('2d').drawImage(im,0,0);return c.toDataURL('image/webp',.85);}''',data)
  asset.write_bytes(base64.b64decode(out.split(',')[1]));w,h=Image.open(original).size;assert w%2==0 and h%2==0
  atlas['sheets'].append({'asset':asset.name,'width':w,'height':h,'sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'generatedOriginalName':original.name})
  for cell,ident in enumerate(ids):
   if ident:atlas['portraits'][ident]={'sheet':i,'cell':cell}
  print(i,ids,asset.stat().st_size,flush=True)
 browser.close()
(ROOT/'assets/portrait-atlas.json').write_text(json.dumps(atlas,ensure_ascii=False,indent=2)+'\n')
refs=json.loads(Path('/workspace/scratch/v6-research/portrait-results.json').read_text());missing={'meiko','letme','papi','baike','fengge'};records=[]
for ref in refs:
 ident=ref['id'];
 if ident not in atlas['portraits']:continue
 verified=ident not in missing
 if not verified:ref={k:v for k,v in ref.items() if k in ['id','name']}
 ref.update(verifiedReference=verified,kind='AI卡通重绘' if verified else 'AI角色示意',atlas=atlas['portraits'][ident],rights=ref.get('rights','AI示意图，无已核实本人照片参考；非官方头像或人物背书。'))
 if ident=='wanglaoju':ref['note']='参考账号使用的红发卡通形象，非本人照片。'
 if ident=='ming':ref['note']='参考图为两人合影，仅取左侧持扩音器的小明。'
 if ident=='daoge':ref['note']='参考图为虎刀合影，仅取右侧抬手的刀哥。'
 records.append(ref)
(ROOT/'image-sources.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
