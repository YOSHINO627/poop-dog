// Browser-only pixel authoring. Gameplay and breed selection remain in Python.
const panel = document.createElement('details');
panel.id = 'sprite-editor';
panel.innerHTML = `<summary>ドット絵エディター</summary>
<p>編集中はゲームが一時停止します。色を選び、クリック・ドラッグで描画。右クリックは消しゴムです。</p>
<div class="edit-toolbar"><button id="edit-current">現在の犬を読み込む</button><button id="edit-undo">元に戻す</button><button id="edit-redo">やり直す</button></div>
<div class="edit-toolbar"><label>フレーム <select id="edit-frame"><option>待機</option><option>歩行1</option><option>歩行2</option><option>ジャンプ</option></select></label><label>ツール <select id="edit-tool"><option value="pen">ペン</option><option value="erase">消しゴム</option><option value="fill">塗りつぶし</option><option value="pick">スポイト</option></select></label><button id="edit-copy">前フレームをコピー</button><button id="edit-flip">左右反転</button></div>
<div id="edit-palette" aria-label="描画色"></div><div class="edit-work"><canvas id="edit-grid" width="320" height="320" aria-label="16×16ドット編集領域"></canvas><div><p>アニメーションプレビュー</p><canvas id="edit-preview" width="16" height="16"></canvas><p>スプライトシート（64×16）</p><canvas id="edit-sheet" width="64" height="16"></canvas></div></div>
<div class="edit-toolbar"><button id="edit-apply">ゲームに反映</button><button id="edit-download">PNGをダウンロード</button></div><p id="edit-status" role="status">開くと読み込みます。</p><small>下書きはこのブラウザへ自動保存します。PNG保存もおすすめです。反映した画像は犬種ごとにこのブラウザへ保存し、次回も復元します。ブラウザのデータを削除すると消えるため、PNG保存もご利用ください。</small>`;
document.querySelector('.home-tip').before(panel);
const $ = id => panel.querySelector('#edit-'+id);
let pixels = null, palette = [], frame = 0, color = 0, tool = 'pen', undo = [], redo = [], pointer = null, last = null, ready = false, initializing = false;
const draftKey = 'poop_dog_sprite_draft';
const valid = rows => Array.isArray(rows) && rows.length === 16 && rows.every(r => typeof r === 'string' && /^[0-9a-f]{64}$/.test(r));
const rows = () => pixels.map(row => row.map(v=>v.toString(16)).join(''));
const decode = value => value.map(row=>[...row].map(v=>parseInt(v,16)));
const message = text => $('status').textContent = text;
function save() { try { localStorage.setItem(draftKey,JSON.stringify(rows())); } catch { /* PNG export remains available. */ } }
function checkpoint() { undo.push(rows()); if(undo.length>80)undo.shift(); redo=[]; }
function load(value) { if(!valid(value))throw Error('画像データが不正です。'); if(pixels)checkpoint(); pixels=decode(value); draw();save(); }
function rgba(ctx, width, offset=0) {
 const im=ctx.createImageData(width,16);
 for(let y=0;y<16;y++)for(let x=0;x<width;x++){
  const k=pixels[y][x+offset], i=(y*width+x)*4, rgb=palette[k];
  im.data[i]=rgb>>16&255;im.data[i+1]=rgb>>8&255;im.data[i+2]=rgb&255;im.data[i+3]=k===15?0:255;
 }ctx.putImageData(im,0,0);
}
function draw() {
 if(!pixels)return;
 const ctx=$('grid').getContext('2d');
 for(let y=0;y<16;y++)for(let x=0;x<16;x++){
  const k=pixels[y][frame*16+x];ctx.fillStyle=k===15?((x+y)%2?'#d8dee4':'#f3f5f7'):'#'+palette[k].toString(16).padStart(6,'0');ctx.fillRect(x*20,y*20,20,20);
 }
 ctx.strokeStyle='#00000033';ctx.lineWidth=1;
 for(let n=0;n<=16;n++){ctx.beginPath();ctx.moveTo(n*20+.5,0);ctx.lineTo(n*20+.5,320);ctx.moveTo(0,n*20+.5);ctx.lineTo(320,n*20+.5);ctx.stroke();}
 rgba($('sheet').getContext('2d'),64);
 $('undo').disabled=!undo.length;$('redo').disabled=!redo.length;$('copy').disabled=frame===0;
 [...$('palette').children].forEach((b,i)=>b.setAttribute('aria-pressed',String(i===color)));
}
async function init(){
 if(ready||initializing)return;initializing=true;
 try{
  const response=await fetch('assets/palette.json');if(!response.ok)throw Error('パレットを読み込めません。');palette=await response.json();
  palette.forEach((rgb,i)=>{const b=document.createElement('button');b.type='button';b.title=i===15?'透明':`色 ${i} #${rgb.toString(16).padStart(6,'0')}`;b.setAttribute('aria-label',b.title);b.textContent=i===15?'×':'';b.style.background=i===15?'repeating-conic-gradient(#ddd 0% 25%,white 0% 50%) 0/10px 10px':'#'+rgb.toString(16).padStart(6,'0');b.addEventListener('click',()=>{color=i;tool='pen';$('tool').value=tool;draw();});$('palette').append(b);});
  let value;try{value=JSON.parse(localStorage.getItem(draftKey));}catch{}
  if(!valid(value))value=window.poopDog.getCurrentSprite();
  if(!valid(value)){const res=await fetch('assets/default_player.json');if(!res.ok)throw Error('初期画像を読み込めません。');value=await res.json();}
  load(value);ready=true;message('編集できます。「現在の犬を読み込む」でゲームの画像を取り込めます。');
 }catch(e){$('palette').replaceChildren();message(e.message);}finally{initializing=false;}
}
panel.addEventListener('toggle',()=>{window.poopDog.setEditing(panel.open);if(panel.open)init();else{pointer=null;last=null;}});
$('frame').addEventListener('change',()=>{frame=$('frame').selectedIndex;draw();});
$('tool').addEventListener('change',()=>tool=$('tool').value);
$('current').addEventListener('click',async()=>{if(!ready)return;try{const value=window.poopDog.getCurrentSprite() || await (await fetch('assets/default_player.json')).json();load(value);message('現在の犬を読み込みました。');}catch(e){message(e.message);}});
$('undo').addEventListener('click',()=>{if(!undo.length)return;redo.push(rows());pixels=decode(undo.pop());draw();save();});
$('redo').addEventListener('click',()=>{if(!redo.length)return;undo.push(rows());pixels=decode(redo.pop());draw();save();});
$('copy').addEventListener('click',()=>{if(!ready||!frame)return;checkpoint();for(let y=0;y<16;y++)pixels[y].splice(frame*16,16,...pixels[y].slice((frame-1)*16,frame*16));draw();save();});
$('flip').addEventListener('click',()=>{if(!ready)return;checkpoint();for(let y=0;y<16;y++)pixels[y].splice(frame*16,16,...pixels[y].slice(frame*16,frame*16+16).reverse());draw();save();});
function position(e){const r=$('grid').getBoundingClientRect();return [Math.max(0,Math.min(15,Math.floor((e.clientX-r.left)*16/r.width))),Math.max(0,Math.min(15,Math.floor((e.clientY-r.top)*16/r.height)))];}
function paint(x,y,k){pixels[y][frame*16+x]=k;}
function fill(x,y,k){const old=pixels[y][frame*16+x];if(old===k)return;const stack=[[x,y]];while(stack.length){const [a,b]=stack.pop();if(a<0||a>=16||b<0||b>=16||pixels[b][frame*16+a]!==old)continue;paint(a,b,k);stack.push([a-1,b],[a+1,b],[a,b-1],[a,b+1]);}}
let strokeColor=0;
$('grid').addEventListener('pointerdown',e=>{
 if(!ready||pointer!==null||![0,2].includes(e.button))return;e.preventDefault();const [x,y]=position(e);
 if(tool==='pick'&&e.button!==2){color=pixels[y][frame*16+x];tool='pen';$('tool').value=tool;draw();return;}
 checkpoint();strokeColor=e.button===2||tool==='erase'?15:color;
 if(tool==='fill'&&e.button!==2){fill(x,y,strokeColor);draw();save();return;}
 pointer=e.pointerId;last=[x,y];$('grid').setPointerCapture(pointer);paint(x,y,strokeColor);draw();
});
$('grid').addEventListener('pointermove',e=>{
 if(e.pointerId!==pointer)return;const [x,y]=position(e),[a,b]=last;const steps=Math.max(Math.abs(x-a),Math.abs(y-b));
 for(let i=0;i<=steps;i++)paint(Math.round(a+(x-a)*i/(steps||1)),Math.round(b+(y-b)*i/(steps||1)),strokeColor);
 last=[x,y];draw();
});
function finish(){if(pointer!==null){pointer=null;last=null;save();}}
for(const event of ['pointerup','pointercancel','lostpointercapture'])$('grid').addEventListener(event,finish);
window.addEventListener('blur',finish);
$('grid').addEventListener('contextmenu',e=>e.preventDefault());
$('apply').addEventListener('click',()=>{
 if(ready&&window.poopDog.applyEditorSprite(rows())){
  save();message('反映を送信しました。未起動の場合はゲームを起動してください。');
  panel.open=false;window.poopDog.setEditing(false);
  document.querySelector('#screen').scrollIntoView({block:'center'});
  document.querySelector('#canvas').focus({preventScroll:true});
 }
});
let reportedStatus='';
setInterval(()=>{const status=window.poopDog.getSpriteApplyStatus();if(status!==reportedStatus){reportedStatus=status;if(status==='applied')message(window.poopDog.getSpritePersistenceStatus() ? 'ゲームへ反映し、このブラウザに保存しました。次回も復元されます。' : 'ゲームへ反映しましたが、ブラウザへの保存はできませんでした。PNGをダウンロードしてください。');}},200);
$('download').addEventListener('click',()=>{
 if(!ready)return;const c=document.createElement('canvas');c.width=64;c.height=16;rgba(c.getContext('2d'),64);
 c.toBlob(blob=>{if(!blob){message('PNGの生成に失敗しました。');return;}const a=document.createElement('a'),url=URL.createObjectURL(blob);a.href=url;a.download='poop-dog-sprite.png';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);message('64×16pxの透過PNGを保存しました。');},'image/png');
});
let tick=0;setInterval(()=>{if(ready&&panel.open)rgba($('preview').getContext('2d'),16,([0,1,2,1,2,3][tick++%6])*16);},180);
