"""Reproducible, hand-authored 16px dachshund frames; Pillow is build-only."""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image
from src.config import PALETTE

base = [
'................',
'................',
'................',
'..........000...',
'.........00000..',
'.........00a070.',
'..0......002aa0.',
'..00.0000002aa0.',
'...00000000200..',
'...00000000aa...',
'...0aaaaaaaa0...',
'...0a00000aa0...',
'...aa.....aa....',
'...a0.....a0....',
'................',
'................',
]
frames = [base.copy() for _ in range(4)]
frames[1][12:14] = ['..aa.......aa...', '..a0.......a0...']
frames[2][12:14] = ['....aa...aa.....', '....a0...a0.....']
frames[3][11:14] = ['...0aa0000aa0...', '....a0...a0.....', '................']
im = Image.new('RGBA', (64, 16))
for frame, rows in enumerate(frames):
    for y, row in enumerate(rows):
        for x, c in enumerate(row):
            if c != '.':
                color = PALETTE[int(c, 16)]
                im.putpixel((frame*16+x, y), ((color>>16)&255, (color>>8)&255, color&255, 255))
im.save(Path(__file__).resolve().parents[1] / 'assets/default_player.png')
rows = [''.join(frame[y] for frame in frames).replace('.', 'f') for y in range(16)]
(Path(__file__).resolve().parents[1] / 'assets/default_player.json').write_text(json.dumps(rows))
