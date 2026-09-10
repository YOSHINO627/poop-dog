// This module owns browser I/O only. Every gameplay decision lives in Python.
const BEST_KEY = 'poop_dog_best_score';
const debugEnabled = new URLSearchParams(window.location.search).get('debug') === '1';
let debugTarget = null;
// Pyxel's WASM input driver reads this global even with a custom touch controller.
window._virtualGamepadStates = Array(10).fill(false);
const bestLabel = document.querySelector('#best');
const actionButton = document.querySelector('#game-action');
const statusLabel = document.querySelector('#game-status');
const spriteStatus = document.querySelector('#sprite-status');
const actions = { left: new Set(), right: new Set(), jump: new Set() };
let jumpPressed = false, startRequested = false, pendingSprite = '', state = 'TITLE';
let runtime, loading = false, best = 0, paused = document.hidden;
function loadBest() {
  try {
    const value = Number(localStorage.getItem(BEST_KEY));
    if (Number.isSafeInteger(value) && value >= 0) best = Math.max(best, value);
  } catch { /* Browser privacy settings must never stop a run. */ }
  bestLabel.textContent = String(best).padStart(4, '0');
  return best;
}
function saveBest(score) {
  if (debugEnabled) return;
  if (!Number.isSafeInteger(score) || score < 0) return;
  best = Math.max(loadBest(), score);
  bestLabel.textContent = String(best).padStart(4, '0');
  try { localStorage.setItem(BEST_KEY, String(best)); } catch { /* In-memory fallback. */ }
}
window.poopDog = {
  loadBest, saveBest, debugEnabled,
  pollInput() {
    const input = { left: actions.left.size > 0, right: actions.right.size > 0,
      jump: actions.jump.size > 0, jumpPressed, start: startRequested, paused, debugTarget };
    debugTarget = null;
    jumpPressed = startRequested = false;
    return JSON.stringify(input);
  },
  takeSprite() { const value = pendingSprite; pendingSprite = ''; return value; },
  publish(json) {
    const data = JSON.parse(json);
    state = data.state;
    if (debugEnabled) document.querySelector("#debug-go").disabled = false;
    const canStart = ['TITLE', 'GAME_OVER', 'GAME_CLEAR'].includes(state);
    actionButton.disabled = !canStart;
    actionButton.hidden = !canStart;
    actionButton.textContent = state === 'TITLE' ? 'START' : 'RETRY';
    statusLabel.textContent = state === 'PLAYING' ? `LEVEL ${data.level || 1} / 3 · WAVE ${data.wave} / 5 · STAY DRY, LITTLE DOG` : state.replaceAll('_', ' ');
  },
};
if (debugEnabled) {
  document.querySelector('#debug-panel').hidden = false;
  document.querySelector('#debug-go').addEventListener('click', () => {
    clearInput();
    debugTarget = {level: Number(document.querySelector('#debug-level').value),
                   wave: Number(document.querySelector('#debug-wave').value)};
    paused = false;
    document.querySelector('#canvas').focus();
  });
}
loadBest();
window.addEventListener('storage', loadBest);

function clearInput() {
  Object.values(actions).forEach(set => set.clear());
  document.querySelectorAll('.pressed').forEach(button => button.classList.remove('pressed'));
  jumpPressed = startRequested = false;
}
window.addEventListener('blur', () => { clearInput(); paused = true; });
window.addEventListener('focus', () => { paused = document.hidden; });
document.addEventListener('visibilitychange', () => { clearInput(); paused = document.hidden; });
window.addEventListener('pagehide', clearInput);
for (const button of document.querySelectorAll('[data-action]')) {
  const key = button.dataset.action;
  button.addEventListener('pointerdown', event => {
    if (event.pointerType === 'touch') return; // Touch Events own iPhone fingers.
    if (event.button !== undefined && event.button !== 0) return;
    event.preventDefault();
    paused = false;
    try { button.setPointerCapture(event.pointerId); } catch { /* Global release remains available. */ }
    if (key === 'jump' && actions.jump.size === 0) jumpPressed = true;
    actions[key].add(event.pointerId);
    button.classList.add('pressed');
  });
  const release = event => {
    actions[key].delete(event.pointerId);
    button.classList.toggle('pressed', actions[key].size > 0);
  };
  for (const type of ['pointerup', 'pointercancel', 'lostpointercapture']) button.addEventListener(type, release);
  button.addEventListener('touchstart', event => {
    event.preventDefault();
    paused = false;
    if (key === 'jump' && actions[key].size === 0) jumpPressed = true;
    for (const touch of event.changedTouches) actions[key].add(`touch:${touch.identifier}`);
    button.classList.add('pressed');
  }, {passive:false});
  button.addEventListener('touchmove', event => {
    event.preventDefault();
    const rect = button.getBoundingClientRect();
    for (const touch of event.changedTouches) {
      if (touch.clientX < rect.left || touch.clientX > rect.right ||
          touch.clientY < rect.top || touch.clientY > rect.bottom) {
        actions[key].delete(`touch:${touch.identifier}`);
      }
    }
    button.classList.toggle('pressed', actions[key].size > 0);
  }, {passive:false});
  button.addEventListener('pointermove', event => {
    if (event.pointerType !== 'touch' && event.buttons === 0) release(event);
  });
  button.addEventListener('contextmenu', event => {event.preventDefault();clearInput();});
}
// Release is captured at window level even if a finger ends outside its button.
function releasePointer(event) {
  for (const button of document.querySelectorAll('[data-action]')) {
    actions[button.dataset.action].delete(event.pointerId);
    button.classList.toggle('pressed', actions[button.dataset.action].size > 0);
  }
}
for (const name of ['pointerup','pointercancel']) window.addEventListener(name, releasePointer, true);
function reconcileTouches(event) {
  const live = new Set(Array.from(event.touches, touch => `touch:${touch.identifier}`));
  for (const button of document.querySelectorAll('[data-action]')) {
    const held = actions[button.dataset.action];
    for (const id of held) if (typeof id === 'string' && id.startsWith('touch:') && !live.has(id)) held.delete(id);
    button.classList.toggle('pressed', held.size > 0);
  }
}
for (const name of ['touchend','touchcancel']) window.addEventListener(name, reconcileTouches, {capture:true,passive:false});
for (const name of ['resize','orientationchange']) window.addEventListener(name, clearInput);
for (const name of ['contextmenu','selectstart','dragstart']) {
  document.querySelector('.arcade').addEventListener(name, event => {event.preventDefault();clearInput();});
}
const screen = document.querySelector('#screen');
// Suppress browser gestures only on the canvas, never on HTML launch buttons.
const gameCanvas = document.querySelector('#canvas');
for (const name of ['touchstart','touchmove']) gameCanvas.addEventListener(name, event => event.preventDefault(), {passive:false});
gameCanvas.addEventListener('touchend', event => {
  event.preventDefault();
  if (runtime && ['TITLE','GAME_OVER','GAME_CLEAR'].includes(state)) {
    startRequested = true;
    paused = false;
  }
}, {passive:false});
window.addEventListener('error', event => {
  if (!runtime) return;
  statusLabel.textContent = '実行エラーが発生しました。ページを再読み込みしてください。';
  statusLabel.classList.add('error');
  console.error(event.message);
});
for (const name of ['gesturestart', 'gesturechange', 'gestureend']) {
  document.querySelector('.arcade').addEventListener(name, event => event.preventDefault(), { passive: false });
}
window.addEventListener('keydown', event => {
  if (runtime && ['ArrowLeft', 'ArrowRight', 'ArrowUp', 'Space'].includes(event.code)) event.preventDefault();
});
actionButton.addEventListener('click', () => { startRequested = true; paused = false; document.querySelector('#canvas').focus(); });

async function fetchFile(path) {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`${path}: HTTP ${response.status}`);
  return new Uint8Array(await response.arrayBuffer());
}
document.querySelector('#load').addEventListener('click', async () => {
  if (loading) return;
  loading = true;
  const button = document.querySelector('#load');
  const label = document.querySelector('#load-status');
  button.disabled = true;
  label.classList.remove('error');
  label.textContent = 'ゲームを読み込み中… 初回は少し時間がかかります';
  try {
    if (!window.loadPyodide) throw new Error('起動ライブラリを読み込めません。通信を確認して再試行してください。');
    // Version pair and canvas setup match Pyxel 2.5.10's official Web loader.
    runtime = await window.loadPyodide();
    runtime._api._skip_unwind_fatal_error = true;
    runtime.canvas.setCanvas2D(document.querySelector('#canvas'));
    await runtime.loadPackage('https://cdn.jsdelivr.net/gh/kitao/pyxel@v2.5.10/wasm/pyxel-2.5.10-cp38-abi3-emscripten_4_0_9_wasm32.whl');
    const manifestResponse = await fetch('manifest.json');
    if (!manifestResponse.ok) throw new Error('manifest.jsonを読み込めません。');
    const files = await manifestResponse.json();
    const payloads = await Promise.all(files.map(async path => [path, await fetchFile(path)]));
    runtime.FS.mkdirTree('/poop-dog');
    for (const [path, bytes] of payloads) {
      const destination = `/poop-dog/${path}`;
      runtime.FS.mkdirTree(destination.slice(0, destination.lastIndexOf('/')));
      runtime.FS.writeFile(destination, bytes);
    }
    runtime.FS.chdir('/poop-dog');
    runtime.runPython("import sys\nsys.path.insert(0, '/poop-dog')\nfrom main import App\napp = App()");
    document.querySelector('#boot').hidden = true;
    document.body.classList.add('ready');
    document.querySelector('#canvas').focus();
    paused = false;
    // A cancelled file picker must not leave an input held down.
    document.querySelector('#sprite').addEventListener('cancel', clearInput);
  } catch (error) {
    console.error(error);
    label.textContent = `起動できませんでした: ${error.message} 再試行できます。`;
    label.classList.add('error');
    button.disabled = false;
    button.textContent = '再試行';
    loading = false;
  }
});

let uploadSequence = 0;
document.querySelector('#sprite').addEventListener('change', async event => {
  const file = event.target.files?.[0];
  if (!file) return;
  const sequence = ++uploadSequence;
  let url;
  try {
    if (file.size > 1024 * 1024) throw new Error('PNGは1MB以下にしてください。');
    const bytes = new Uint8Array(await file.arrayBuffer());
    const signature = [137, 80, 78, 71, 13, 10, 26, 10];
    if (!signature.every((value, index) => bytes[index] === value) || bytes.length < 24) throw new Error('PNG形式の画像を選択してください。');
    const view = new DataView(bytes.buffer);
    if (view.getUint32(16) !== 64 || view.getUint32(20) !== 16) throw new Error('画像サイズは64 × 16pxにしてください。現在の画像を維持します。');
    url = URL.createObjectURL(file);
    const image = new Image();
    image.src = url;
    await image.decode();
    if (image.naturalWidth !== 64 || image.naturalHeight !== 16) throw new Error('画像サイズが不正です。');
    const canvas = document.createElement('canvas');
    canvas.width = 64; canvas.height = 16;
    const context = canvas.getContext('2d', { willReadFrequently: true });
    context.drawImage(image, 0, 0);
    const pixels = context.getImageData(0, 0, 64, 16).data;
    const paletteResponse = await fetch('assets/palette.json');
    if (!paletteResponse.ok) throw new Error('パレットを読み込めません。');
    const palette = await paletteResponse.json();
    const rows = [];
    for (let y = 0; y < 16; y++) {
      let row = '';
      for (let x = 0; x < 64; x++) {
        const offset = (y * 64 + x) * 4;
        if (pixels[offset + 3] < 128) { row += 'f'; continue; }
        let nearest = 0, distance = Infinity;
        // Index 15 is reserved exclusively for transparency, even for opaque magenta.
        for (let index = 0; index < 15; index++) {
          const rgb = palette[index];
          const squared = (pixels[offset] - (rgb >> 16 & 255)) ** 2 +
            (pixels[offset+1] - (rgb >> 8 & 255)) ** 2 + (pixels[offset+2] - (rgb & 255)) ** 2;
          if (squared < distance) { distance = squared; nearest = index; }
        }
        row += nearest.toString(16);
      }
      rows.push(row);
    }
    if (sequence !== uploadSequence) return;
    pendingSprite = JSON.stringify(rows);
    spriteStatus.textContent = runtime ? '画像を読み込みました。ゲームへ反映します。' : '画像を読み込みました。ゲーム起動時に反映します。';
    spriteStatus.classList.remove('error');
  } catch (error) {
    if (sequence !== uploadSequence) return;
    spriteStatus.textContent = error.message;
    spriteStatus.classList.add('error');
  } finally {
    if (url) URL.revokeObjectURL(url);
    event.target.value = '';
  }
});


// Presentation-only: toggling never recreates the Python runtime or game state.
const viewToggle = document.querySelector('#view-toggle');
const arcade = document.querySelector('.arcade');
let expanded = false, viewBusy = false, nativeView = false;
function setExpanded(value) {
  expanded = value;
  document.body.classList.toggle('expanded', value);
  viewToggle.textContent = value ? '戻る ↙' : '拡大 ⛶';
  viewToggle.setAttribute('aria-pressed', String(value));
  clearInput();
  syncViewport();
}
viewToggle.addEventListener('click', async () => {
  if (viewBusy) return;
  viewBusy = true;
  try {
    if (expanded) {
      if (document.fullscreenElement && document.exitFullscreen) {
        try { await document.exitFullscreen(); } catch { /* Keep the visible return control usable. */ }
      }
      nativeView = false;
      setExpanded(false);
    } else {
      setExpanded(true);
      if (arcade.requestFullscreen) {
        try { await arcade.requestFullscreen(); nativeView = !!document.fullscreenElement; }
        catch { /* iPhone and denied requests keep the viewport-sized layout. */ }
      }
    }
  } finally {
    viewBusy = false;
    document.querySelector('#canvas').focus();
  }
});
document.addEventListener('fullscreenchange', () => {
  if (!document.fullscreenElement && nativeView) {
    nativeView = false;
    setExpanded(false);
  }
});
window.addEventListener('keydown', event => {
  if (event.key === 'Escape' && expanded && !document.fullscreenElement) setExpanded(false);
});


// Use the current visual viewport rather than stale pre-rotation layout heights.
function syncViewport() {
  const height = window.visualViewport?.height || window.innerHeight;
  if (Number.isFinite(height) && height > 0) document.documentElement.style.setProperty('--app-height', `${height}px`);
}
window.addEventListener('resize', syncViewport);
window.addEventListener('orientationchange', syncViewport);
window.visualViewport?.addEventListener('resize', syncViewport);
syncViewport();
