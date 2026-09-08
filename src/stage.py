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
