"""Small palette-native sprites; all breeds share the same physics and hitbox."""
import json
from pathlib import Path

BREEDS = ('KANINCHEN DACHSHUND', 'POMERANIAN', 'CHIHUAHUA', 'TOY POODLE', 'SCHNAUZER')

# Right-facing silhouettes, without dark outlines. Dark pixels are fur/eyes/nose.
# White ruff and curled tail; tall ears and white blaze; curls; brows and beard.
POSES = (
    (
        '................', '.........7...7..', '........777.777.',
        '.......77777777.', '......777777777.', '...77.777770777.',
        '..77777777777770', '.77777777777777.', '.7777777777777..',
        '..7777777777777.', '..7777777777777.', '..6777777777776.',
        '...67777777776..', '....77....77....', '....77....77....', '................',
    ),
    (
        '........0....00.', '........77...07.', '........7e..e77.',
        '........7e00e77.', '........0000000.', '........0070700.',
        '........0000000.', '..00.....070770.', '...70....0777700',
        '...07700007777..', '....0000000777..', '....0000000777..',
        '.....77700777...', '.....7....77....', '.....e....ee....', '................',
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


def sheet(index):
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
