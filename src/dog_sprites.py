"""Small palette-native sprites; all breeds share the same physics and hitbox."""
import json
from pathlib import Path

BREEDS = ('KANINCHEN DACHSHUND', 'POMERANIAN', 'CHIHUAHUA', 'TOY POODLE', 'SCHNAUZER')

# Right-facing silhouettes, without dark outlines. Dark pixels are fur/eyes/nose.
# White ruff and curled tail; tall ears and white blaze; curls; brows and beard.
POSES = (
    (
        '................',
        '................',
        '.........7..7...',
        '........777777..',
        '........7e7777..',
        '.......77777777.',
        '..77...77770770.',
        '.7777.777777777.',
        '.7777777777777..',
        '..7e77777777777.',
        '.77777777777777.',
        '.7777777777777..',
        '..777777777777..',
        '...77e7777e77...',
        '....77....77....',
        '................',
    ),
    (
        # Approved nose-revised reference pose, grounded and facing right.
        '................',
        '................',
        '................',
        '......00.....0..',
        '......70....07..',
        '......7e0..0e7..',
        '......7e000007..',
        '......00700700..',
        '...00..000000...',
        '..77...077700...',
        '...700007070....',
        '....0000077.....',
        '....0000077.....',
        '....7067..7.....',
        '....e.4e..e.....',
        '................',
    ),
    (
        '..........999...', '.........99999..', '........9999999.',
        '.......499999994', '.......499999994', '.......499090994',
        '..99...499999994', '.9999...4999994.', '..99...9999909..',
        '...99999999999..', '..999999999999..', '..999999999999..',
        '...49999999994..', '....99....99....', '....99....99....', '................',
    ),
    (
        '.........55..55.', '.........555555.', '........5555555.',
        '........5555555.', '........5565565.', '........5505505.',
        '..55....5556666.', '...55...55677770', '...555..5577777.',
        '....5555555777..', '....5555555676..', '....5555555665..',
        '.....55555555...', '.....6....66....', '.....7....77....', '................',
    ),
)


# User-edited 64x16 PNG: preserve all four frames pixel-for-pixel.
CHIHUAHUA_SHEET = (
    'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff',
    'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff',
    'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff',
    'ffffff00fffff0ffffffff00fffff0ffffffff00fffff0ffffffff00fffff0ff',
    'ffffff70ffff07ffffffff70ffff07ffffffff70ffff07ffffffff70ffff07ff',
    'ffffff7e0ff0e7ffffffff7e0ff0e7ffffffff7e0ff0e7ffffffff7e0ff0e7ff',
    'ffffff7e000007ffffffff7e000007ffffffff7e000007ffffffff7e000007ff',
    'ffffff00700700ffffffff00700700ffffffff00700700ffffffff00700700ff',
    'fff00ff000000ffffff00ff000000ffffff00ff000000ffffff00ff000000fff',
    'ff70fff077070fffff70fff077070fffff70fff077070fffff70fff077070fff',
    'fff700007770fffffff700007770fffffff700007770fffffff700007770ffff',
    'ffff0000077fffffffff0000077fffffffff0000077fffffffff0000077fffff',
    'ffff0000077fffffffff0000077fffffffff0000077fffffffff0000077fffff',
    'ffff7f67ff7ffffffffff7f677fffffffff7f67ffff7ffffffff7f67ff7fffff',
    'ffffef4effeffffffffffef4eefffffffffef4effffeffffffffffffffffffff',
    'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff',
)

# User-edited Pomeranian sheet, preserving all four frames and transparency.
POMERANIAN_SHEET = (
    'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff',
    'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff',
    'fffffffff7ff7ffffffffffff7ff7ffffffffffff7ff7ffffffffffff7ff7fff',
    'ffffffff777777ffffffffff777777ffffffffff777777ffffffffff777777ff',
    'ffffffff7e7777ffffffffff7e7777ffffffffff7e7777ffffffffff7e7777ff',
    'fffffff77770777ffffffff77770777ffffffff77770777ffffffff77770777f',
    'ff77fff77777770fff77fff77777770fff77fff77777770fff77fff77777770f',
    'f7777f777777777ff7777f777777777ff7777f777777777ff7777f777777777f',
    'f7777777777777fff7777777777777fff7777777777777fff7777777777777ff',
    'ff7e77777777777fff7e77777777777fff7e77777777777fff7e77777777777f',
    'f77777777777777ff77777777777777ff77777777777777ff77777777777777f',
    'f7777777777777fff7777777777777fff7777777777777fff7777777777777ff',
    'ff777777777777ffff777777777777ffff777777777777ffff777777777777ff',
    'fff77e7777e77fffffff77e77e77ffffff77e77ff77e77fffff77e7777e77fff',
    'ffff77ffff77fffffffff77ff77ffffffff77ffffff77fffffffffffffffffff',
    'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff',
)

def sheet(index):
    if index == 1:
        return list(POMERANIAN_SHEET)
    if index == 2:
        return list(CHIHUAHUA_SHEET)
    if index == 0:
        return json.loads(Path('assets/default_player.json').read_text())
    idle = [row.replace('.', 'f').ljust(16, 'f') for row in POSES[index-1]]
    frames = [idle]
    # Move only paws for two steps; tuck them for the airborne frame.
    for step in (1, -1, 0):
        frame = idle.copy()
        for y in (13, 14):
            row = ['f'] * 16
            for x, color in enumerate(idle[y]):
                if color != 'f':
                    shift = step if x < 8 else -step
                    row[max(0, min(15, x + shift))] = color
            frame[y] = ''.join(row) if step or y == 13 else 'f' * 16
        frames.append(frame)
    return [''.join(frame[y] for frame in frames) for y in range(16)]
