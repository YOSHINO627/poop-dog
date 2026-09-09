import json
from pathlib import Path
from .platform import Platform
from . import config as C

class Stage:
    def __init__(self):
        path = Path(__file__).resolve().parent.parent / 'assets/stage.json'
        self.objects = json.loads(path.read_text(encoding='utf-8'))['objects']
        self.platforms = [Platform(o['x'], o['y'], o['w'], o.get('end_y'))
                          for o in self.objects if o['kind'] != 'tree']
        self.platforms.append(Platform(0, C.GROUND_Y, C.STAGE_WIDTH))

    def spawn_regions(self):
        """Valid left-edge ranges above objects, and their open-ground complement.

        Expand by hazard width so the open-ground branch never clips a roof.
        Merge overlaps so adjacent platforms do not receive duplicate weight.
        """
        limit = C.STAGE_WIDTH - C.POOP_SIZE
        spans = sorted((max(0, o['x'] - C.POOP_SIZE), min(limit, o['x'] + o['w']))
                       for o in self.objects if o['kind'] != 'tree' and o.get('w', 0) > 0)
        covered = []
        for left, right in spans:
            if right <= left:
                continue
            if covered and left <= covered[-1][1]:
                covered[-1] = (covered[-1][0], max(right, covered[-1][1]))
            else:
                covered.append((left, right))
        open_ground, cursor = [], 0
        for left, right in covered:
            if left > cursor:
                open_ground.append((cursor, left))
            cursor = right
        if cursor < limit:
            open_ground.append((cursor, limit))
        return covered, open_ground

    def spawn_x(self, rng, object_bias):
        covered, open_ground = self.spawn_regions()
        regions = covered if rng.random() < object_bias else open_ground
        regions = regions or covered or open_ground
        # Pick proportionally to horizontal width, not the number of platforms.
        offset = rng.random() * sum(right - left for left, right in regions)
        for left, right in regions:
            if offset < right - left:
                return left + offset
            offset -= right - left
        return C.STAGE_WIDTH - C.POOP_SIZE
