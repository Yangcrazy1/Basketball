/* Original low-poly meshes. A small offline software 3D renderer; no WebGL/CDN required. */
(function(root){'use strict';
const PI=Math.PI;
function hex(h){return [1,3,5].map(i=>parseInt(h.slice(i,i+2),16));}
function color(h,k){const c=hex(h);return `rgb(${c.map(v=>Math.min(255,Math.round(v*k))).join(',')})`;}
function model(cfg){
 const {theme,vector:v,identity:p,augment}=cfg,polys=[],ink='#222232',accent=theme==='basket'?'#ff944c':theme==='lol'?'#a089ff':'#c2df65';
 const darkSkin=['lebron','jordan','kobe','durant','westbrook','harden','shaq','duncan','garnett','butler','rodman'].includes(p.personId),skin=darkSkin?'#925f42':'#f1bf95',round=p.personId==='uzi',tall=p.personId==='dasima',headY=2.28,hw=round?.55:tall?.43:.48;
 function face(verts,c){polys.push({verts,color:c});}
 function box(x,y,z,w,h,d,c){const a=[[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]].map(t=>[x+t[0]*w/2,y+t[1]*h/2,z+t[2]*d/2]);[[0,1,2,3],[4,7,6,5],[0,4,5,1],[3,2,6,7],[1,5,6,2],[0,3,7,4]].forEach(f=>face(f.map(i=>a[i]),c));}
 function sphere(x,y,z,rx,ry,rz,c,segments=12,rings=8,end=PI){for(let i=0;i<rings;i++)for(let j=0;j<segments;j++){const point=(r,s)=>{const a=r/rings*end,b=s/segments*2*PI;return [x+rx*Math.sin(a)*Math.cos(b),y+ry*Math.cos(a),z+rz*Math.sin(a)*Math.sin(b)];};face([point(i,j),point(i+1,j),point(i+1,j+1),point(i,j+1)],c);}}
 function cylinder(x,y,z,r,h,c,n=16){for(let i=0;i<n;i++){const a=i/n*PI*2,b=(i+1)/n*PI*2;const p=[x+r*Math.cos(a),y-h/2,z+r*Math.sin(a)],q=[x+r*Math.cos(b),y-h/2,z+r*Math.sin(b)],s=[p[0],y+h/2,p[2]],t=[q[0],y+h/2,q[2]];face([p,q,t,s],c);face([[x,y+h/2,z],s,t],c);face([[x,y-h/2,z],q,p],c);}}
 cylinder(0,-.045,0,.91,.10,accent,32);cylinder(0,-.11,0,.84,.07,ink,32);
 const leg=theme==='basket'?.66:.57;
 box(-.22,.17,.10,.36,.20,.60,ink);box(.22,.17,.10,.36,.20,.60,ink);
 box(-.22,.38+leg/2,0,.27,leg,.31,theme==='basket'?skin:'#424057');box(.22,.38+leg/2,0,.27,leg,.31,theme==='basket'?skin:'#424057');
 box(0,1.08,0,.77,.38,.44,theme==='basket'?accent:'#343344');box(0,1.48,0,.88,.66,.47,accent);
 box(0,1.44,-.255,.88,.64,.04,ink); // back panel makes a real back view
 if(theme!=='basket'){box(0,1.43,.258,.055,.62,.025,ink);box(0,1.23,.28,.47,.12,.05,ink);}
 const armRaise=v[5]>=65;
 sphere(-.61,1.51,0,.17,.28,.18,accent,8,5);box(-.63,1.18,.04,.22,.43,.23,skin);
 sphere(.61,1.58,0,.17,.24,.18,accent,8,5);box(.66,armRaise?1.83:1.22,.05,.22,.46,.23,skin);sphere(.66,armRaise?2.11:1.02,.06,.14,.15,.14,skin,8,5);
 cylinder(0,1.90,0,.17,.23,skin,12);
 sphere(0,headY,0,hw,.53,.43,skin,16,10);
 sphere(-hw,headY-.015,0,.10,.14,.10,skin,8,5);sphere(hw,headY-.015,0,.10,.14,.10,skin,8,5);
 if(tall)box(0,2.78,-.025,.80,.38,.72,ink);else sphere(0,headY+.18,-.035,hw*1.03,.43,.45,p.personId==='rodman'?'#eab1fa':ink,16,6,PI*.52);
 if(!darkSkin&&p.personId!=='yaoming')box(0,2.52,.37,hw*1.65,.12,.08,ink);
 sphere(-.175,2.29,.409,.077,.072,.026,'#ffffff',8,5);sphere(.175,2.29,.409,.077,.072,.026,'#ffffff',8,5);
 sphere(-.175,2.285,.435,.032,.040,.018,ink,8,5);sphere(.175,2.285,.435,.032,.040,.018,ink,8,5);
 sphere(0,2.18,.436,.065,.08,.060,skin,8,5);box(0,2.03,.408,v[2]>55?.19:.12,.035,.03,'#874e45');
 const glasses=['dasima','xiaohu','sunxiaochuan'].includes(p.personId)||v[4]>=75||augment?.accessory.includes('镜');
 if(glasses){for(const x of [-.175,.175]){box(x,2.29,.46,.29,.028,.025,ink);box(x,2.17,.46,.29,.028,.025,ink);box(x-.14,2.23,.46,.028,.15,.025,ink);box(x+.14,2.23,.46,.028,.15,.025,ink);}box(0,2.25,.46,.08,.025,.025,ink);box(-.37,2.25,.1,.025,.025,.65,ink);box(.37,2.25,.1,.025,.025,.65,ink);}
 if(v[1]>=60||augment?.accessory.includes('背包')){box(0,1.48,-.43,.58,.60,.28,'#687d83');box(0,1.45,-.59,.35,.25,.08,accent);}
 if(theme==='basket'){
  sphere(-.78,1.08,.25,.30,.30,.30,'#e98135',14,9);
  for(let i=0;i<20;i++){const a=i/20*2*PI,b=(i+1)/20*2*PI;face([[-.78+.303*Math.cos(a),1.08+.303*Math.sin(a),.257],[-.78+.303*Math.cos(b),1.08+.303*Math.sin(b),.257],[-.78+.291*Math.cos(b),1.08+.291*Math.sin(b),.26],[-.78+.291*Math.cos(a),1.08+.291*Math.sin(a),.26]],ink);}
  box(-.78,1.08,.55,.022,.38,.012,ink);box(-.78,1.08,.55,.38,.022,.012,ink);
  if(augment?.id==='kneel'){box(-.22,.75,.20,.32,.19,.12,ink);box(.22,.75,.20,.32,.19,.12,ink);}
 }else if(theme==='lol'){
  box(-.69,1.12,.20,.07,1.30,.07,'#b3a3d4');sphere(-.69,1.85,.20,.19,.23,.19,accent,8,5);
  box(-.69,.62,.2,.35,.08,.08,'#e2c975');
 }else{
  cylinder(-.69,1.05,.18,.08,.45,ink,10);sphere(-.69,1.34,.18,.17,.18,.17,'#b9c1ba',10,6);
 }
 if(augment?.id==='lotus'||v[5]>=90){for(let i=0;i<3;i++)box((i-1)*.28,2.92,-.02,.12,.20+(i===1?.12:0),.12,'#efd47c');}
 if(v[2]>=70){sphere(-.08,1.59,.26,.09,.085,.045,'#e17b94',8,5);sphere(.08,1.59,.26,.09,.085,.045,'#e17b94',8,5);face([[-.16,1.57,.28],[.16,1.57,.28],[0,1.36,.28]],'#e17b94');}
 if(augment){
  const a=augment.id;
  if(a==='goliath'){box(-.61,1.66,0,.48,.32,.59,'#b8a0dc');box(.61,1.66,0,.48,.32,.59,'#b8a0dc');}
  if(a==='range'){box(0,2.34,.49,.70,.07,.10,'#d9e68b');}
  if(a==='missile'){for(const x of [-.23,.23]){cylinder(x,1.56,-.49,.13,.63,'#bdc4d1',10);sphere(x,1.91,-.49,.13,.16,.13,'#d8798b',10,5);}}
  if(a==='revive'){cylinder(0,3.05,0,.49,.05,'#ead696',24);}
  if(a==='snowball'){sphere(.68,armRaise?2.20:1.12,.12,.22,.22,.22,'#d4edf2',12,8);}
  if(a==='collector'){box(-.69,1.85,.40,.29,.045,.05,'#f5e798');box(-.69,1.85,.40,.045,.29,.05,'#f5e798');}
  if(a==='support'){box(0,1.50,-.65,.55,.51,.10,'#cedce2');face([[-.275,1.25,-.71],[.275,1.25,-.71],[0,1.04,-.71]],'#cedce2');}
  if(a==='spring'||a==='portal'){sphere(-hw-.10,2.17,0,.10,.14,.07,a==='portal'?'#df94d7':'#e5cb6c',10,6);sphere(hw+.10,2.17,0,.10,.14,.07,a==='portal'?'#df94d7':'#e5cb6c',10,6);}
  if(a==='flash'){box(-.22,.22,.11,.39,.24,.63,'#c6b4ff');box(.22,.22,.11,.39,.24,.63,'#c6b4ff');}
  if(a==='coffee'){cylinder(.68,armRaise?2.23:1.15,.1,.11,.30,'#9e6650',12);cylinder(.68,armRaise?2.40:1.32,.1,.13,.04,'#f2e7d3',12);}
  if(a==='meme'){box(.68,armRaise?2.22:1.24,.10,.06,.30,.07,ink);box(.68,armRaise?2.50:1.52,.10,.48,.34,.09,'#fff2d5');box(.56,armRaise?2.50:1.52,.16,.045,.20,.025,ink);box(.74,armRaise?2.50:1.52,.16,.11,.20,.025,ink);}
  if(a==='team'){box(.62,1.66,.14,.27,.10,.20,'#dfff75');}
  if(a==='board'){box(0,1.41,-.69,.12,.40,.14,ink);cylinder(0,1.80,-.44,.17,.12,'#bec9cb',12);}
  if(a==='juice'){sphere(0,1.52,-.65,.17,.19,.05,'#ee914c',10,6);box(0,1.82,-.44,.12,.12,.10,'#77ac69');}
  if(a==='sofa'){box(0,1.48,-.41,.68,.73,.32,'#a8b98e');box(0,1.48,-.59,.05,.62,.04,'#829768');}
  if(a==='micro'){sphere(-.69,1.40,.18,.23,.25,.23,'#b9c1ba',10,7);}
  if(a==='clipboard'||a==='quantum'){box(.69,1.35,.19,.42,.60,.08,'#d9bb8c');box(.69,1.64,.24,.20,.07,.05,ink);for(let i=0;i<3;i++)box(.69,1.45-i*.12,.24,.27,.025,.015,ink);}
 }
 return {polys,accent,number:theme==='basket'?p.number:theme==='lol'?'GG':'∞',glasses,backpack:v[1]>=60,raised:armRaise};
}
function create(canvas,cfg){
 const ctx=canvas.getContext('2d');if(!ctx)return null;const mesh=model(cfg);let yaw=-.28,pitch=.02,zoom=1,auto=false,dead=false,raf=0,last=0,drag=false,pointers=new Map(),pinch=null;
 canvas.dataset.renderer='software-3d-mesh';canvas.dataset.faces=mesh.polys.length;canvas.setAttribute('aria-label','可拖动360度旋转的原创三维分身');
 function transform(p){const cy=Math.cos(yaw),sy=Math.sin(yaw),cp=Math.cos(pitch),sp=Math.sin(pitch),x=p[0]*cy+p[2]*sy,z=-p[0]*sy+p[2]*cy,y=p[1]-1.40;return [x,y*cp-z*sp,y*sp+z*cp];}
 function render(){const rect=canvas.getBoundingClientRect(),w=rect.width||350,h=rect.height||380,dpr=Math.min(devicePixelRatio||1,1.5);if(canvas.width!==Math.round(w*dpr)||canvas.height!==Math.round(h*dpr)){canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);}ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,w,h);
  const scale=Math.min(w*.70,h*.245)*zoom,project=p=>{const f=5.2/(5.2-p[2]);return [w/2+p[0]*scale*f,h*.52-p[1]*scale*f];};
  ctx.fillStyle='#00000019';ctx.beginPath();ctx.ellipse(w/2,h*.88,w*.27,h*.035,0,0,PI*2);ctx.fill();
  const faces=mesh.polys.map(p=>{const verts=p.verts.map(transform),depth=verts.reduce((s,v)=>s+v[2],0)/verts.length;return {...p,verts,depth};}).sort((a,b)=>a.depth-b.depth);
  faces.forEach(f=>{const a=f.verts[0],b=f.verts[1],c=f.verts[2],u=b.map((v,i)=>v-a[i]),v=c.map((x,i)=>x-a[i]),n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]],len=Math.hypot(...n)||1,light=.68+.24*Math.abs((n[0]*-.4+n[1]*.8+n[2]*.6)/len);const points=f.verts.map(project);ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(p[0],p[1]):ctx.moveTo(p[0],p[1]));ctx.closePath();ctx.fillStyle=color(f.color,light);ctx.fill();ctx.strokeStyle=color(f.color,light);ctx.lineWidth=.35;ctx.stroke();});
  if(Math.cos(yaw)>.35){const p=project(transform([0,1.48,.285]));ctx.save();ctx.translate(p[0],p[1]);ctx.scale(Math.max(.35,Math.cos(yaw)),1);ctx.font=`900 ${scale*.25}px sans-serif`;ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillStyle='#242333';ctx.fillText(mesh.number,0,0);ctx.restore();}
  canvas.dataset.yaw=yaw.toFixed(3);
 }
 function frame(t){if(dead)return;if(t-last>32){const dt=last?Math.min(.05,(t-last)/1000):.033;last=t;if(auto&&!drag){yaw+=dt*.28;render();}}raf=requestAnimationFrame(frame);}
 function down(e){canvas.setPointerCapture(e.pointerId);pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});drag=true;auto=false;cfg.onAutoChange?.(false);pinch=null;}
 function move(e){const old=pointers.get(e.pointerId);if(!old)return;const next={x:e.clientX,y:e.clientY};if(pointers.size===1){yaw+=(next.x-old.x)*.012;pitch=Math.max(-.45,Math.min(.45,pitch+(next.y-old.y)*.006));}pointers.set(e.pointerId,next);if(pointers.size===2){const a=[...pointers.values()],d=Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y);if(pinch)zoom=Math.max(.7,Math.min(1.5,zoom*d/pinch));pinch=d;}render();}
 function up(e){pointers.delete(e.pointerId);drag=pointers.size>0;pinch=null;}
 function wheel(e){e.preventDefault();zoom=Math.max(.7,Math.min(1.5,zoom-e.deltaY*.001));render();}
 window.addEventListener('resize',render);canvas.addEventListener('pointerdown',down);canvas.addEventListener('pointermove',move);canvas.addEventListener('pointerup',up);canvas.addEventListener('pointercancel',up);canvas.addEventListener('wheel',wheel,{passive:false});raf=requestAnimationFrame(frame);render();
 return {rotate(d){auto=false;cfg.onAutoChange?.(false);yaw+=d;render();},toggle(){auto=!auto;cfg.onAutoChange?.(auto);return auto;},reset(){auto=false;cfg.onAutoChange?.(false);yaw=-.28;pitch=.02;zoom=1;render();},snapshot(){render();return canvas.toDataURL('image/png');},traits:mesh,destroy(){dead=true;cancelAnimationFrame(raf);window.removeEventListener('resize',render);canvas.removeEventListener('pointerdown',down);canvas.removeEventListener('pointermove',move);canvas.removeEventListener('pointerup',up);canvas.removeEventListener('pointercancel',up);canvas.removeEventListener('wheel',wheel);}};
}
root.Toy3D={create,model};
})(typeof window!=='undefined'?window:globalThis);
