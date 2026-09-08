import json
from pathlib import Path
import pyxel as p
from . import config as C
from .game import GameState

class Renderer:
    def __init__(self):
        # Explicit indexed data avoids PNG loader alpha/palette reassignment.
        self.apply_sprite(json.loads(Path('assets/default_player.json').read_text()))

    def apply_sprite(self, rows):
        if (not isinstance(rows, list) or len(rows) != 16
                or any(not isinstance(row, str) or len(row) != 64
                       or any(c not in '0123456789abcdef' for c in row) for row in rows)):
            return False
        p.images[0].set(0, 0, rows)
        return True

    def center(self, text, y, color=7):
        p.text((C.WIDTH - len(text) * 4) // 2, y, text, color)

    def poop(self, x, y):
        x, y = int(x), int(y)
        p.rect(x, y+4, 7, 3, 2)
        p.rect(x+1, y+2, 5, 3, 4)
        p.rect(x+3, y, 2, 3, 4)
        p.pset(x+2, y+3, 14)

    def scenery(self, camera):
        p.cls(12)
        # Distant scenery moves slower than the fenced play area.
        for x in range(-120, C.STAGE_WIDTH, 90):
            sx = int(x - camera * 0.3)
            p.rect(sx, 38, 24, 4, 7)
            p.rect(sx+5, 34, 13, 5, 7)
        for x in range(-80, C.STAGE_WIDTH, 38):
            sx = int(x - camera * 0.55)
            p.circ(sx, 92, 25 + x % 7, 3)
            p.circ(sx+12, 95, 17, 11)
        p.rect(0, 102, C.WIDTH, 42, 11)
        p.camera(camera, 0)
        for x in range(0, C.STAGE_WIDTH, 16):
            p.rect(x, 97, 3, 23, 14)
            p.pset(x+1, 96, 7)
        p.rect(0, 102, C.STAGE_WIDTH, 3, 7)
        p.rect(0, 112, C.STAGE_WIDTH, 2, 14)
        p.rect(0, C.GROUND_Y, C.STAGE_WIDTH, 20, 3)
        p.rect(0, C.GROUND_Y, C.STAGE_WIDTH, 2, 11)
        for x in range(0, C.STAGE_WIDTH, 11):
            y = 128 + (x * 7) % 13
            p.line(x, y, x+2, y+1, 11)

    def object(self, o):
        x, y, w = o['x'], o['y'], o.get('w', 0)
        kind = o['kind']
        if kind == 'tree':
            p.rect(x+10, y-26, 5, 45, 4)
            p.circ(x+12, y-35, 19, 3)
            p.circ(x+5, y-41, 12, 11)
            p.circ(x+23, y-32, 11, 3)
        elif kind == 'slope':
            end = o['end_y']
            p.line(x, y, x+w, end, 7)
            p.line(x, y+1, x+w, end+1, 4)
            p.line(x, y+2, x+w, end+2, 4)
            for n in range(8, w, 9):
                sy = y + (end-y) * n / w
                p.line(x+n, sy, x+n+1, sy+1, 9)
        elif kind == 'tire':
            p.elli(x, y, w, C.GROUND_Y-y, 0)
            p.elli(x+5, y+4, w-10, C.GROUND_Y-y-6, 11)
            p.line(x+5, y+1, x+w-5, y+1, 5)
        elif kind == 'crate':
            p.rect(x, y, w, C.GROUND_Y-y, 4)
            p.rectb(x, y, w, C.GROUND_Y-y, 14)
            p.line(x+2, y+2, x+w-3, C.GROUND_Y-3, 14)
            p.line(x+w-3, y+2, x+2, C.GROUND_Y-3, 14)
        else:
            p.rect(x+3, y+3, 3, C.GROUND_Y-y-3, 2)
            p.rect(x+w-6, y+3, 3, C.GROUND_Y-y-3, 2)
            p.rect(x, y, w, 4, 4)
            p.line(x, y, x+w-1, y, 7)
            if kind == 'bench':
                p.rect(x+2, y-10, w-4, 6, 4)
                p.line(x+2, y-10, x+w-3, y-10, 14)
                p.rect(x+4, y-4, 2, 4, 2)
                p.rect(x+w-6, y-4, 2, 4, 2)
            if kind == 'hurdle':
                for n in range(0, w, 8):
                    p.rect(x+n, y, 4, 4, 8)

    def heart(self, x, filled):
        color = 8 if filled else 5
        p.rect(x, 5, 3, 3, color)
        p.rect(x+4, 5, 3, 3, color)
        p.rect(x+1, 7, 5, 3, color)
        p.rect(x+2, 10, 3, 1, color)
        p.pset(x+3, 11, color)

    def draw(self, game):
        self.scenery(game.camera.x)
        for o in game.stage.objects:
            self.object(o)
        for hazard in game.hazards:
            hazard.draw(self)
        for x, y, age in game.splashes:
            spread = C.SPLASH_TICKS-age
            p.line(x-spread, y-1, x+7+spread, y-1, 4)
        dog = game.player
        if not dog.invincible or (dog.invincible // C.BLINK_TICKS) % 2 == 0:
            p.blt(dog.x, dog.y, 0, dog.frame * 16, 0, 16 * dog.facing, 16, C.TRANSPARENT_COLOR)
        p.camera()
        p.rect(0, 0, C.WIDTH, 18, 0)
        p.text(5, 6, 'HP', 7)
        for i in range(C.MAX_HP):
            self.heart(17 + i * 9, i < game.hp)
        p.text(52, 6, f'SCORE {game.score.score:04}', 10)
        p.text(123, 6, f'TIME 00:{game.wave.remaining:02}', 7)
        p.text(209, 6, f'WAVE {game.wave.index+1}/{len(C.WAVES)}', 11)
        if game.state == GameState.PLAYING:
            return
        p.rect(43, 27, 170, 82, 0)
        p.rectb(45, 29, 166, 78, 4)
        state = game.state
        if state == GameState.TITLE:
            p.blt(78, 39, 0, 0, 0, 16, 16, C.TRANSPARENT_COLOR, scale=2)
            p.text(105, 44, 'POOP DOG', 10)
            self.center('A LITTLE DOG. A BIG BAD SKY.', 66, 6)
            self.center(f'BEST SCORE {game.score.best:04}', 79, 7)
            self.center('[ START / SPACE ]', 94, 11)
        elif state == GameState.WAVE_CLEAR:
            self.center('WAVE CLEAR', 41, 10)
            self.center(f'CLEAR +{C.CLEAR_POINTS}', 57, 7)
            self.center('NO DAMAGE +500' if not game.wave.wave_damaged else 'KEEP GOING, LITTLE DOG!', 69, 11)
            self.center(f'NEXT WAVE  {C.INTERVAL_SECONDS-game.interval_ticks//C.FPS}', 92, 7)
        else:
            self.center('GAME CLEAR' if state == GameState.GAME_CLEAR else 'GAME OVER', 42, 10 if game.hp else 8)
            self.center(f'SCORE      {game.score.score:04}', 60)
            self.center(f'BEST SCORE {game.score.best:04}', 73, 10)
            self.center('[ RETRY / SPACE ]', 94, 11)
