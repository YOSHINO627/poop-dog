import json
from pathlib import Path
import pyxel as p
from . import config as C
from .game import GameState

class Renderer:
    def __init__(self, web_controls=False):
        self.web_controls = web_controls
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

    def poop(self, x, y, piercing=False, size=C.POOP_SIZE, meteor=False):
        x, y = int(x), int(y)
        if size > C.POOP_SIZE:
            p.rect(x, y+size*2//3, size, size//3, 2)
            p.rect(x+3, y+size//3, size-6, size//2, 4)
            p.rect(x+size//2, y, size//3, size//2, 4)
            p.line(x+4, y+size//2, x+8, y+size//2, 14)
            return
        if meteor:
            p.line(x+3, y-2, x+3, y-12, 10)
            p.line(x+1, y-3, x+1, y-8, 9)
        p.rect(x, y+4, 7, 3, 8 if piercing else 2)
        p.rect(x+1, y+2, 5, 3, 9 if piercing else 4)
        p.rect(x+3, y, 2, 3, 10 if piercing else 4)
        p.pset(x+2, y+3, 7 if piercing else 14)
        if piercing:
            # Bright flames distinguish roof-piercing rain without changing hitboxes.
            p.line(x+1, y-2, x+1, y-5, 8)
            p.line(x+5, y-1, x+5, y-4, 10)

    def friend(self, dog):
        x, y = int(dog.x), int(dog.y)
        # Hand-drawn reference-inspired pixels: no outline, only eyes/nose are dark.
        # The poodle's rounded fringe and hanging ears stay distinct from corgi ears.
        if dog.kind == 'poodle':
            rows = (
                '...........77777',
                '..........7777777',
                '.........777777777',
                '........67777777776',
                '........67777777776',
                '........67770770776',
                '..77....67777777776',
                '.7777....667770776',
                '..77..77777777777',
                '...7777777777dd7',
                '..77777777777777',
                '..777777777777777',
                '...67777777777776',
                '....667766777766',
            )
        else:
            rows = (
                '...........e....e',
                '...........e7..7e',
                '...........e77e7e',
                '..77.......eeeeee',
                '.7ee......eeeeeee7',
                '.eee......eee0e777',
                '..ee.....eeeeee7770',
                '...eeeeeeeeeee77777',
                '...eeeeeeeeee777777',
                '..eeeeeeeeee7cc78',
                '..eeeeeeeeeee777',
                '..eeeeeeeeeee777',
                '...e77777777777',
                '....777.....777',
            )
        def pixel(dx, dy, color):
            p.pset(x+(dx if dog.facing > 0 else C.FRIEND_WIDTH-1-dx), y+dy, color)
        for dy, row in enumerate(rows):
            for dx, color in enumerate(row):
                if color != '.':
                    pixel(dx, dy, int(color, 16))
        # Two alternating short steps, with soft paws instead of black outlines.
        step = (dog.age // 5) % 2
        for dx in (4+step, 13-step):
            for offset in range(2):
                pixel(dx+offset, 14, 7)
                pixel(dx+offset, 15 if dx == 4+step else 14+1-step, 7)
        if dog.kind == 'corgi' and dog.drift:
            p.line(x-5, y+15, x-2, y+15, 7)
            p.line(x+22, y+14, x+25, y+14, 6)

    def kibble(self, x, y, age):
        x, y = int(x), int(y)
        # A flat golden pellet with a cream rim differs from stacked brown poop.
        p.rect(x+1, y, 4, 6, 14)
        p.rect(x, y+1, 6, 4, 14)
        p.rect(x+1, y+1, 4, 3, 9)
        p.line(x+1, y, x+4, y, 7)
        p.pset(x+1, y+1, 7)
        p.pset(x+3, y+3, 14)
        if (age // 10) % 2 == 0:
            p.pset(x+5, y-2, 10)

    def floral(self, x, y, age):
        x, y = int(x), int(y)
        # A rose-shaped spiral opens into narrowing wind rings below it.
        p.line(x+3, y, x+6, y, 13)
        p.line(x+1, y+1, x+2, y+1, 13)
        p.line(x+7, y+1, x+8, y+1, 13)
        p.line(x, y+2, x, y+3, 13)
        p.line(x+9, y+2, x+9, y+3, 13)
        p.line(x+1, y+4, x+7, y+4, 13)
        p.line(x+8, y+3, x+8, y+4, 13)
        p.line(x+3, y+1, x+6, y+1, 7)
        p.line(x+2, y+2, x+2, y+3, 7)
        p.line(x+3, y+3, x+6, y+3, 7)
        p.line(x+6, y+2, x+7, y+2, 13)
        p.pset(x+4, y+2, 13)
        p.line(x+1, y+5, x+3, y+6, 13)
        p.line(x+3, y+6, x+7, y+6, 13)
        p.pset(x+8, y+5, 13)
        p.line(x+3, y+7, x+4, y+8, 13)
        p.line(x+4, y+8, x+6, y+8, 13)
        p.pset(x+5, y+9, 13)
        # Moving highlights suggest rotation without changing the pickup bounds.
        shine = (age // 5) % 3
        p.line(x+3+shine, y+5, x+4+shine, y+5, 7)
        p.pset(x+6-shine, y+7, 7)
        if (age // 5) % 2:
            p.line(x-2, y, x, y, 7)
            p.line(x-1, y-1, x-1, y+1, 7)
        else:
            p.line(x+9, y+10, x+11, y+10, 13)
            p.line(x+10, y+9, x+10, y+11, 13)

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
        for floral in game.florals:
            floral.draw(self)
        for kibble in game.kibbles.items:
            kibble.draw(self)
        for hazard in game.hazards:
            hazard.draw(self)
        for friend in game.friends:
            friend.draw(self)
        for x, y, age in game.splashes:
            spread = C.SPLASH_TICKS-age
            p.line(x-spread, y-1, x+7+spread, y-1, 4)
        dog = game.player
        if not dog.invincible or (dog.invincible // C.BLINK_TICKS) % 2 == 0:
            p.blt(dog.x, dog.y, 0, dog.frame * 16, 0, 16 * dog.facing, 16, C.TRANSPARENT_COLOR)
        if game.heal_feedback_ticks:
            p.text(dog.x - 10, dog.y - 9, 'FLORAL +1', 13)
        if game.score.delicious_ticks:
            label_x = max(game.camera.x + 2, min(dog.x - 12, game.camera.x + C.WIDTH - 42))
            label_y = max(20, dog.y - (19 if game.heal_feedback_ticks else 10))
            p.text(label_x+1, label_y+1, 'Delicious!', 0)
            p.text(label_x, label_y, 'Delicious!', 10)
        p.camera()
        p.rect(0, 0, C.WIDTH, 18, 0)
        p.text(5, 6, 'HP', 7)
        for i in range(C.MAX_HP):
            self.heart(17 + i * 9, i < game.hp)
        p.text(52, 6, f'SCORE {game.score.score:04}', 10)
        p.text(123, 6, f'TIME 00:{game.wave.remaining:02}', 7)
        p.text(184, 3, f'LEVEL {game.wave.level+1}/{len(C.LEVELS)}', 13)
        p.text(184, 10, f'WAVE  {game.wave.index+1}/{len(C.WAVES)}', 11)
        if game.debug_enabled:
            p.text(176, 21, 'DEBUG / NO BEST', 8)
        if game.state == GameState.PLAYING:
            if game.rain.warning or game.rain.shower:
                self.center('DANGER! POOP METEOR SHOWER!', 38, 8)
            if game.score.combo_count:
                p.text(5, 21, f'FOOD {game.score.combo_count}/{C.KIBBLE_COMBO_COUNT}', 7)
            return
        p.rect(43, 27, 170, 99, 0)
        p.rectb(45, 29, 166, 95, 4)
        state = game.state
        if state == GameState.TITLE:
            p.blt(78, 39, 0, 0, 0, 16, 16, C.TRANSPARENT_COLOR, scale=2)
            p.text(105, 44, 'POOP DOG', 10)
            self.center('3 LEVELS / 5 WAVES EACH', 66, 6)
            self.center(f'BEST SCORE {game.score.best:04}', 79, 7)
            if not self.web_controls:
                self.center('[ START / SPACE ]', 101, 11)
        elif state == GameState.WAVE_CLEAR:
            self.center('WAVE CLEAR', 41, 10)
            self.center(f'CLEAR +{C.CLEAR_POINTS}', 57, 7)
            self.center('NO DAMAGE +500' if not game.wave.wave_damaged else 'KEEP GOING, LITTLE DOG!', 69, 11)
            label = 'NEXT LEVEL' if game.wave.index == len(C.WAVES)-1 else 'NEXT WAVE'
            self.center(f'{label}  {C.INTERVAL_SECONDS-game.interval_ticks//C.FPS}', 92, 7)
            p.rect(45, 111, 166, 10, 0)
            self.center('RED POOP PIERCES SHELTERS!', 114, 8)
        else:
            self.center('GAME CLEAR' if state == GameState.GAME_CLEAR else 'GAME OVER', 42, 10 if game.hp else 8)
            self.center(f'SCORE      {game.score.score:04}', 60)
            self.center(f'BEST SCORE {game.score.best:04}', 73, 10)
            if not self.web_controls:
                self.center('[ RETRY / SPACE ]', 101, 11)
