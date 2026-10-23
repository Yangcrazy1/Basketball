/* Xiaohongshu native adapter. Contract checked 2026-10-23 against online docs. */
window.WORLD_PLATFORM=(function(){
'use strict';
var prefix='world-otherme.v10.',values={},native=false,canPersist=true,version=0,queue=Promise.resolve(),posterData=null,known=['theme','count','style','intro-seen','session','history','first.lol','first.basket','first.abstract','squad.lol','squad.basket','squad.abstract'];
var mini=window.xhs&&window.xhs.miniTool;
function buildValue(options){return Number(options&&options.miniToolEnv&&options.miniToolEnv.buildVersion)||0;}
async function getVersion(){var v=buildValue(window.xhs&&window.xhs.launchOptions);if(v)return Math.floor(v/1000);if(mini&&typeof mini.getLaunchOptions==='function'){try{return Math.floor(buildValue(await mini.getLaunchOptions())/1000);}catch(e){return 0;}}return 0;}
function parse(s,f){try{return s===null||s===undefined?f:JSON.parse(s);}catch(e){return f;}}
function enqueue(op){queue=queue.then(op).catch(function(){canPersist=false;});return queue;}
async function initialize(){
 version=await getVersion();native=version>=9460&&!!mini&&typeof mini.getStorage==='function'&&typeof mini.setStorage==='function'&&typeof mini.removeStorage==='function';
 for(var i=0;i<known.length;i++){
  var key=known[i],raw=null,readOK=!native;
  if(native){try{var res=await mini.getStorage({key:prefix+key});raw=res&&res.data;readOK=true;}catch(e){canPersist=false;}}
  if(!native||(readOK&&(raw===null||raw===undefined))){try{var legacy=localStorage.getItem(prefix+key);if(legacy!==null){raw=legacy;if(native){await mini.setStorage({key:prefix+key,data:legacy});localStorage.removeItem(prefix+key);}}}catch(e){if(!native)canPersist=false;}}
  if(raw!==null&&raw!==undefined)values[key]=parse(raw,null);
 }
 await windowLayout();
}
async function windowLayout(){
 if(version<9490||!mini||typeof mini.getWindowInfo!=='function')return;
 try{var info=await mini.getWindowInfo(),safe=info.safeArea,buttons=info.menuButtons||{},top=0;
  if(safe){top=Math.max(0,safe.top);document.documentElement.style.setProperty('--safe-area-inset-bottom',Math.max(0,info.windowHeight-safe.bottom)+'px');document.documentElement.style.setProperty('--safe-area-inset-left',Math.max(0,safe.left)+'px');document.documentElement.style.setProperty('--safe-area-inset-right',Math.max(0,info.windowWidth-safe.right)+'px');}
  ['back','me','share'].forEach(function(k){var rect=buttons[k];if(rect)top=Math.max(top,rect.bottom+6);});document.documentElement.style.setProperty('--safe-area-inset-top',top+'px');
 }catch(e){/* Container variables / CSS env remain the fallback. */}
}
function read(k,f){return Object.prototype.hasOwnProperty.call(values,k)?values[k]:f;}
function write(k,v){values[k]=v;var data=JSON.stringify(v);if(native)enqueue(function(){return mini.setStorage({key:prefix+k,data:data});});else try{localStorage.setItem(prefix+k,data);}catch(e){canPersist=false;}}
function remove(k){delete values[k];if(native)enqueue(function(){return mini.removeStorage({key:prefix+k});});else try{localStorage.removeItem(prefix+k);}catch(e){canPersist=false;}}
async function savePoster(){if(!posterData)throw Error('请先生成海报');if(!mini||typeof mini.saveImageToPhotosAlbum!=='function')throw Error('请在支持存相册的小红书小工具中打开');var path=posterData;if(typeof mini.writeTempFile==='function'){var f=await mini.writeTempFile({data:posterData});if(!f||!f.filePath)throw Error('图片暂存失败，请重新生成');path=f.filePath;}await mini.saveImageToPhotosAlbum({filePath:path});}
var resizeTimer;window.addEventListener('resize',function(){clearTimeout(resizeTimer);resizeTimer=setTimeout(windowLayout,180);});
// Measure flex gap once; baseline margins apply only to actual flex containers.
var probe=document.createElement('div');probe.style.cssText='position:absolute;visibility:hidden;display:flex;flex-direction:column;row-gap:1px';probe.appendChild(document.createElement('div'));probe.appendChild(document.createElement('div'));document.body.appendChild(probe);var flexGap=probe.scrollHeight===1;probe.parentNode.removeChild(probe);
function afterRender(){if(flexGap)return;var changes=[];Array.prototype.forEach.call(document.querySelectorAll('#app *,#dialog *,header,header *,footer,footer *'),function(el){var st=getComputedStyle(el);if((st.display==='flex'||st.display==='inline-flex')&&el.children.length>1){var x=parseFloat(st.gridColumnGap)||0,y=parseFloat(st.gridRowGap)||0;if(x||y)changes.push({el:el,x:x,y:y,column:st.flexDirection.indexOf('column')===0,wrap:st.flexWrap!=='nowrap'});}});changes.forEach(function(c){Array.prototype.forEach.call(c.el.children,function(child,i){child.style.marginRight=(!c.column&&i<c.el.children.length-1?c.x:0)+'px';if(c.column||c.wrap)child.style.marginBottom=(i<c.el.children.length-1?c.y:0)+'px';});});}
var api={read:read,write:write,remove:remove,savePoster:savePoster,setPoster:function(data){posterData=data;},afterRender:afterRender,isPersistent:function(){return canPersist;}};api.ready=initialize();return api;
})();
