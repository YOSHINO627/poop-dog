"""Reproducible, hand-authored 16px dachshund frames; Pillow is build-only."""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image
from src.config import PALETTE

# Rounded head and soft cream markings match the companion dogs.
# The low, slightly elongated body stays within the original 16x16 contract.
base = [
'................',
'................',
'..........000...',
'.........00000..',
'.........00700..',
'.........010770.',
'.0.......0107770',
'.00.....0010777.',
'..00000000107e..',
'..000000000077..',
'..000000000077..',
'...0eeeeeee77...',
'...077....077...',
'...77.....77....',
'...77.....77....',
'................',
]
frames = [base.copy() for _ in range(4)]
frames[1][12:15] = ['..077......077..', '..77.......77...', '..77............']
frames[2][12:15] = ['....077..077....', '....77...77.....', '.........77.....']
frames[3][12:15] = ['...077....077...', '....77...77.....', '................']
assert all(len(rows) == 16 and all(len(row) == 16 for row in rows) for rows in frames)
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
