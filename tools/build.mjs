import { mkdir, copyFile, readdir, readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
const root = fileURLToPath(new URL('../', import.meta.url));
const config = await readFile(path.join(root, 'src/config.py'), 'utf8');
const paletteMatch = config.match(/PALETTE\s*=\s*\[([\s\S]*?)\]/);
if (!paletteMatch) throw new Error('Missing PALETTE in config.py');
const palette = paletteMatch[1].match(/0x[0-9a-f]+/gi).map(value => Number(value));
if (palette.length !== 16) throw new Error('PALETTE must have 16 colors');
await writeFile(path.join(root, 'assets/palette.json'), JSON.stringify(palette));
const py = (await readdir(path.join(root, 'src'))).filter(f => f.endsWith('.py')).map(f => 'src/' + f);
const assets = ['assets/default_player.png', 'assets/default_player.json', 'assets/stage.json', 'assets/palette.json'];
const manifest = ['main.py', ...py, ...assets];
await writeFile(path.join(root, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n');
// Explicit allowlist: no venv, credentials, tests, or server functions are deployed.
for (const file of [...manifest, 'manifest.json', 'index.html', 'style.css', 'app.js', 'editor.js']) {
  const destination = path.join(root, 'dist', file);
  await mkdir(path.dirname(destination), { recursive: true });
  await copyFile(path.join(root, file), destination);
}
if (!config.includes('0xFF00FF')) throw new Error('Review transparency palette');
console.log(`Built dist/ (${manifest.length + 5} static files). Python executes in the browser only.`);
