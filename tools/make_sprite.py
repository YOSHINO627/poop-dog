"""Reproducible, hand-authored 16px dachshund frames; Pillow is build-only."""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image
from src.config import PALETTE

# Approved B1: lower silhouette, long body and a slightly extended muzzle.
# All four frames preserve the 16x16 sprite and existing collision contract.
base = ['................', '................', '................', '................', '................', '................', '..........000...', '.........00700..', '.0.......0107770', '.00000000010777.', '00000000000077..', '00000000000077..', '.0eeeeeeeeee7...', '.77........77...', '.77........77...', '................']
frames = [base.copy() for _ in range(4)]
frames[1][13:15] = ['77..........77..', '77..........77..']
frames[2][13:15] = ['..77......77....', '..77......77....']
frames[3][13:15] = ['...77.....77....', '................']
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
