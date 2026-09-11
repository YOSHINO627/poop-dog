import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { readFile } from 'node:fs/promises';
const source = await readFile(new URL('../app.js', import.meta.url), 'utf8');
const palette = JSON.parse(await readFile(new URL('../assets/palette.json', import.meta.url), 'utf8'));
class Element {
  constructor(action) { this.dataset = {action}; this.listeners = {}; this.textContent = ''; this.classList = {add(){},remove(){},toggle(){}}; }
  addEventListener(name, fn) { (this.listeners[name] ||= []).push(fn); }
  setPointerCapture() {}
  focus() {}
  setAttribute(name,value) { this[name]=value; }
  async emit(name, event={}) { for (const fn of this.listeners[name] || []) await fn({preventDefault(){}, ...event}); }
}
function fixture(blocked=false, stored='0', search='', saved=null) {
  const elements = Object.fromEntries(['dog-select','dog-prev','dog-next','best','game-action','game-status','sprite-status','screen','load','load-status','canvas','boot','sprite','debug-panel','debug-go','debug-level','debug-wave','view-toggle'].map(id => ['#'+id,new Element()]));
  elements['.arcade'] = new Element();
  const buttons = ['left','right','jump'].map(action=>new Element(action));
  const data = new Map([['poop_dog_best_score', stored]]);
  if (saved) for (const [key,value] of saved) data.set(key,value);
  const window = new Element();
  window.location = {search};
  const document = new Element();
  Object.assign(document, {body:new Element(),hidden:false, querySelector:q=>elements[q], querySelectorAll:q=>q==='[data-action]'?buttons:[],
    createElement:()=>({getContext:()=>({drawImage(){},getImageData:()=>({data:Uint8ClampedArray.from({length:4096},(_,i)=>i===3?0:255)})})})});
  const context = vm.createContext({window,document,console,URLSearchParams,Set,Array,JSON,Number,String,Math,Uint8Array,DataView,
    localStorage:{getItem:k=>{if(blocked)throw Error('blocked');return data.get(k)},setItem:(k,v)=>{if(blocked)throw Error('blocked');data.set(k,v)}},
    URL:{createObjectURL:()=> 'blob:test',revokeObjectURL(){}},
    Image:class {naturalWidth=64;naturalHeight=16;async decode(){}},
    fetch:async()=>({ok:true,json:async()=>palette})});
  vm.runInContext(source, context);
  return {host:window.poopDog,buttons,elements,data,window,document};
}
const poll = f => JSON.parse(f.host.pollInput());

test('custom art and selected breed survive reload, with independent breed slots', () => {
  const f = fixture(), a = Array(16).fill('7'.repeat(64)), b = Array(16).fill('0'.repeat(64));
  assert.equal(f.host.saveCustomSprite(1, JSON.stringify(a)), true);
  assert.equal(f.host.saveCustomSprite(2, JSON.stringify(b)), true);
  f.host.publish(JSON.stringify({state:'TITLE',selectedBreed:2}));
  const fresh = fixture(false,'0','',f.data);
  assert.deepEqual(JSON.parse(fresh.host.loadCustomSprites()), {'1':a,'2':b});
  assert.equal(fresh.host.loadDogChoice(), 2);
  assert.equal(fresh.host.saveCustomSprite(1, '["bad"]'), false);
  assert.deepEqual(JSON.parse(fresh.host.loadCustomSprites())['1'], a);
});

test('blocked or corrupt custom art storage is safe', () => {
  const f = fixture(true);
  assert.equal(f.host.saveCustomSprite(1, JSON.stringify(Array(16).fill('7'.repeat(64)))), false);
  assert.equal(f.host.loadCustomSprites(), '{}');
  assert.equal(f.host.loadDogChoice(), 0);
  for (const value of ['null','{bad','{"1":["bad"]}']) {
    const fresh = fixture(false,'0','',new Map([['poop_dog_custom_sprites_v1',value]]));
    assert.equal(fresh.host.loadCustomSprites(), '{}');
  }
});
test('localStorage BEST is monotonic and survives a new host', () => {
  const f=fixture(false,'1230');assert.equal(f.host.loadBest(),1230);
  f.host.saveBest(6500);f.host.saveBest(100);assert.equal(f.data.get('poop_dog_best_score'),'6500');
  assert.equal(fixture(false,f.data.get('poop_dog_best_score')).host.loadBest(),6500);
});
test('storage denial and corrupt values never stop gameplay',()=>{
  const f=fixture(true);f.host.saveBest(120);assert.equal(f.host.loadBest(),120);assert.equal(poll(f).left,false);
  assert.equal(fixture(false,'NaN').host.loadBest(),0);
});
test('RIGHT + JUMP / LEFT + JUMP, independent release, cancellation',async()=>{
  const f=fixture();const [left,right,jump]=f.buttons;
  await right.emit('pointerdown',{pointerId:1});await jump.emit('pointerdown',{pointerId:2});
  let input=poll(f);assert.equal(input.right,true);assert.equal(input.jump,true);assert.equal(input.jumpPressed,true);
  assert.equal(poll(f).jumpPressed,false);
  await jump.emit('pointerup',{pointerId:2});input=poll(f);assert.equal(input.right,true);assert.equal(input.jump,false);
  await right.emit('pointercancel',{pointerId:1});await left.emit('pointerdown',{pointerId:3});await jump.emit('pointerdown',{pointerId:4});
  input=poll(f);assert.equal(input.left,true);assert.equal(input.jump,true);
  await f.window.emit('blur');input=poll(f);assert.equal(input.left,false);assert.equal(input.jump,false);assert.equal(input.paused,true);
});
test('two fingers on same control preserve hold until both release',async()=>{
  const f=fixture(), right=f.buttons[1];await right.emit('pointerdown',{pointerId:1});await right.emit('pointerdown',{pointerId:2});
  await right.emit('pointerup',{pointerId:1});assert.equal(poll(f).right,true);
  await right.emit('lostpointercapture',{pointerId:2});assert.equal(poll(f).right,false);
});
function png(width=64,height=16){const bytes=new Uint8Array(24);bytes.set([137,80,78,71,13,10,26,10]);const view=new DataView(bytes.buffer);view.setUint32(16,width);view.setUint32(20,height);return {size:24,arrayBuffer:async()=>bytes.buffer}}
async function upload(f,file){await f.elements['#sprite'].emit('change',{target:{files:[file],value:''}})}
test('64x16 upload converts pixels and reserves transparent color',async()=>{
  const f=fixture();await upload(f,png());const rows=JSON.parse(f.host.takeSprite());
  assert.equal(rows.length,16);assert.equal(rows[0].length,64);assert.equal(rows[0][0],'f');assert.ok(!rows[0].slice(1).includes('f'));
  assert.equal(f.host.takeSprite(),'');
});
test('invalid PNG keeps pending good sprite and reports error',async()=>{
  const f=fixture();await upload(f,png());await upload(f,png(32,32));assert.match(f.elements['#sprite-status'].textContent,/64/);
  assert.equal(JSON.parse(f.host.takeSprite()).length,16);
  await upload(f,{size:4,arrayBuffer:async()=>new Uint8Array(4).buffer});assert.equal(f.host.takeSprite(),'');
});


test('debug is opt-in, suppresses BEST and sends a one-shot target', async()=>{
  const normal=fixture(); assert.equal(normal.host.debugEnabled,false);
  assert.equal(poll(normal).debugTarget,null);
  const f=fixture(false,'1230','?debug=1');
  assert.equal(f.host.debugEnabled,true);
  assert.equal(f.elements['#debug-panel'].hidden,false);
  f.host.saveBest(99999);assert.equal(f.data.get('poop_dog_best_score'),'1230');
  f.elements['#debug-level'].value='3'; f.elements['#debug-wave'].value='4';
  await f.elements['#debug-go'].emit('click');
  assert.deepEqual(poll(f).debugTarget,{level:3,wave:4});
  assert.equal(poll(f).debugTarget,null);
  assert.equal(fixture(false,'0','?debug=0').host.debugEnabled,false);
});


test('expanded fallback toggles without resetting game or BEST', async()=>{
 const f=fixture(false,'1230');
 await f.buttons[1].emit('pointerdown',{pointerId:1});
 await f.elements['#view-toggle'].emit('click');
 assert.equal(f.elements['#view-toggle']['aria-pressed'],'true');
 assert.equal(poll(f).right,false);assert.equal(poll(f).start,false);
 assert.equal(f.data.get('poop_dog_best_score'),'1230');
 await f.elements['#view-toggle'].emit('click');
 assert.equal(f.elements['#view-toggle']['aria-pressed'],'false');
});
test('fullscreen rejection falls back and native exit restores normal mode',async()=>{
 const f=fixture();
 f.elements['.arcade'].requestFullscreen=async()=>{throw Error('unsupported')};
 await f.elements['#view-toggle'].emit('click');
 assert.equal(f.elements['#view-toggle']['aria-pressed'],'true');
 await f.elements['#view-toggle'].emit('click');
 f.elements['.arcade'].requestFullscreen=async()=>{f.document.fullscreenElement=f.elements['.arcade']};
 await f.elements['#view-toggle'].emit('click');
 f.document.fullscreenElement=null;await f.document.emit('fullscreenchange');
 assert.equal(f.elements['#view-toggle']['aria-pressed'],'false');
});


test('iPhone touch release outside button and cancellation cannot leave movement held',async()=>{
 const f=fixture(),right=f.buttons[1],jump=f.buttons[2];
 await right.emit('pointerdown',{pointerType:'touch',pointerId:10});
 assert.equal(poll(f).right,false);
 await right.emit('touchstart',{changedTouches:[{identifier:10}]});
 await jump.emit('touchstart',{changedTouches:[{identifier:11}]});
 assert.equal(poll(f).right,true);assert.equal(poll(f).jump,true);
 await f.window.emit('touchend',{touches:[{identifier:11}]});
 assert.equal(poll(f).right,false);assert.equal(poll(f).jump,true);
 await f.window.emit('touchcancel',{touches:[]});assert.equal(poll(f).jump,false);
});
test('global pointer release, long press and rotation clear stale controls',async()=>{
 const f=fixture(),right=f.buttons[1];
 await right.emit('pointerdown',{pointerId:3});
 await f.window.emit('pointerup',{pointerId:3});assert.equal(poll(f).right,false);
 await right.emit('pointerdown',{pointerId:4});
 let prevented=false;
 await f.elements['.arcade'].emit('contextmenu',{preventDefault(){prevented=true}});
 assert.equal(prevented,true);assert.equal(poll(f).right,false);
 await right.emit('touchstart',{changedTouches:[{identifier:5}]});
 await f.window.emit('orientationchange');assert.equal(poll(f).right,false);
});
test('dragging a finger off a key releases only that finger',async()=>{
 const f=fixture(),right=f.buttons[1];
 right.getBoundingClientRect=()=>({left:0,right:60,top:0,bottom:60});
 await right.emit('touchstart',{changedTouches:[{identifier:1},{identifier:2}]});
 await right.emit('touchmove',{changedTouches:[{identifier:1,clientX:100,clientY:20}]});
 assert.equal(poll(f).right,true);
 await f.window.emit('touchend',{touches:[]});assert.equal(poll(f).right,false);
});


test('launch controls do not cancel touch clicks and in-screen start is one-shot',async()=>{
 const f=fixture();
 // The screen ancestor must not cancel a launch button touch and its synthetic click.
 let cancelled=false;
 await f.elements['#screen'].emit('touchstart',{preventDefault(){cancelled=true}});
 assert.equal(cancelled,false);
 await f.elements['#canvas'].emit('touchstart',{preventDefault(){cancelled=true}});
 assert.equal(cancelled,true);
 f.host.publish(JSON.stringify({state:'TITLE'}));
 assert.equal(f.elements['#game-action'].hidden,false);
 await f.elements['#game-action'].emit('click');
 assert.equal(poll(f).start,true);assert.equal(poll(f).start,false);
 f.host.publish(JSON.stringify({state:'PLAYING',level:1,wave:1}));
 assert.equal(f.elements['#game-action'].hidden,true);
 f.host.publish(JSON.stringify({state:'GAME_OVER'}));
 assert.equal(f.elements['#game-action'].hidden,false);
});

test('DOG selection controls are one-shot and only available on menus',async()=>{
 const f=fixture();
 f.host.publish(JSON.stringify({state:'TITLE',wave:1}));
 assert.equal(f.elements['#dog-select'].hidden,false);
 await f.elements['#dog-select'].emit('click');
 assert.equal(poll(f).dogSelect,true);assert.equal(poll(f).dogSelect,false);
 f.host.publish(JSON.stringify({state:'DOG_SELECT',wave:1}));
 assert.equal(f.elements['#game-action'].textContent,'OK');
 assert.equal(f.elements['#dog-next'].hidden,false);
 await f.elements['#dog-next'].emit('click');assert.equal(poll(f).selectStep,1);
 assert.equal(poll(f).selectStep,0);
 await f.elements['#dog-prev'].emit('click');assert.equal(poll(f).selectStep,-1);
 f.host.publish(JSON.stringify({state:'PLAYING',wave:1}));
 assert.equal(f.elements['#dog-select'].hidden,true);
 assert.equal(f.elements['#dog-next'].hidden,true);
 assert.equal(f.elements['#game-action'].hidden,true);
});

test('editor bridge validates sheets, pauses gameplay and sends a single update',()=>{
 const f=fixture(); const rows=Array(16).fill('f'.repeat(64));
 f.host.setEditing(true);assert.equal(poll(f).paused,true);
 assert.equal(f.host.applyEditorSprite(['bad']),false);assert.equal(f.host.takeSprite(),'');
 assert.equal(f.host.applyEditorSprite(rows),true);
 assert.deepEqual(JSON.parse(f.host.takeSprite()),rows);assert.equal(f.host.takeSprite(),'');
 assert.equal(f.host.getSpriteApplyStatus(),'pending');
 f.host.setCurrentSprite(JSON.stringify(rows));
 assert.equal(f.host.getSpriteApplyStatus(),'applied');
 assert.deepEqual(f.host.getCurrentSprite(),rows);
 f.host.setCurrentSprite(JSON.stringify(Array(16).fill('7'.repeat(64))));
 assert.equal(f.host.getCurrentSprite()[0],'7'.repeat(64));
 f.host.setEditing(false);assert.equal(poll(f).paused,false);
});
