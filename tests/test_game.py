import random
import unittest
from src import config as C
from src.game import Game, GameState
from src.player import Player
from src.poop import Poop
from src.platform import Platform
from src.camera import Camera

class Storage:
    def __init__(self):
        self.best = 0
    def load_best(self):
        return self.best
    def save_best(self, value):
        self.best = value

class GameTests(unittest.TestCase):
    def setUp(self):
        self.storage = Storage()
        self.game = Game(self.storage, random.Random(42))

    def start(self):
        self.game.update(start=True)
        return self.game

    def safe_run(self, ticks):
        # A real bench shields the dog. Keep the real hazard spawning active.
        self.game.player.x = 126
        for _ in range(ticks):
            self.game.update()

    def test_title_start(self):
        self.assertEqual(self.game.state, GameState.TITLE)
        self.start()
        self.assertEqual(self.game.hp, 3)
        self.assertEqual(self.game.state, GameState.PLAYING)

    def test_move_bounds_animation_and_facing(self):
        g = self.start()
        g.update(-1)
        self.assertEqual(g.player.facing, -1)
        frames = set()
        for _ in range(20):
            g.update(1)
            frames.add(g.player.frame)
        self.assertTrue({1, 2}.issubset(frames))
        g.update()
        self.assertEqual(g.player.frame, 0)
        p = Player()
        for direction in (-1, 1):
            for _ in range(700):
                p.update(direction, False, [Platform(0, C.GROUND_Y, C.STAGE_WIDTH)])
            self.assertEqual(p.x, 0 if direction < 0 else C.STAGE_WIDTH-16)

    def test_jump_no_double_and_landing(self):
        p = Player()
        floor = [Platform(0, C.GROUND_Y, C.STAGE_WIDTH)]
        p.update(0, True, floor)
        initial_vy = p.vy
        p.update(0, True, floor)
        self.assertGreater(p.vy, initial_vy)
        self.assertEqual(p.frame, 3)
        for _ in range(60):
            p.update(0, False, floor)
        self.assertTrue(p.grounded)
        self.assertEqual(p.y, C.GROUND_Y-16)

    def test_platform_and_slope(self):
        p = Player()
        p.x, p.y, p.vy, p.grounded = 125, 75, 3, False
        for _ in range(10):
            p.update(0, False, self.game.stage.platforms)
        self.assertEqual(p.y, 99-16)
        self.assertTrue(p.grounded)
        p.x, p.y = 464, 117-16
        p.y = self.game.stage.platforms[4].top_at(p.x+8)-16
        p.grounded = True
        old_y = p.y
        for _ in range(10):
            p.update(1, False, self.game.stage.platforms)
        self.assertLess(p.y, old_y)

    def test_camera_clamp(self):
        p, camera = Player(), Camera()
        p.x = 600
        camera.update(p)
        self.assertGreater(camera.x, 0)
        p.x = 99999
        camera.update(p)
        self.assertEqual(camera.x, C.STAGE_WIDTH-C.WIDTH)

    def test_poop_swept_roof_and_removal(self):
        poop = Poop(126, 50, 80)
        poop.update(self.game.stage.platforms)
        self.assertFalse(poop.alive)
        self.assertEqual(poop.impact[1], 99)
        g = self.start()
        g.player.x = 126
        g.hazards = [Poop(128, 50, 80)]
        g.update()
        self.assertEqual(g.hp, 3)
        self.assertEqual(g.hazards, [])
        self.assertTrue(g.splashes)
        for _ in range(C.SPLASH_TICKS):
            g.update()
        self.assertEqual(g.splashes, [])

    def hit(self):
        p = self.game.player
        self.game.hazards = [Poop(p.x+2, 1, p.y+5)]
        self.game.update()

    def test_damage_invincibility_game_over(self):
        g = self.start()
        self.hit()
        self.assertEqual(g.hp, 2)
        self.assertTrue(g.wave.wave_damaged)
        self.assertEqual(g.player.invincible, C.FPS)
        self.hit()
        self.assertEqual(g.hp, 2)
        self.assertEqual(g.hazards, [])
        for _ in range(28):
            g.update()
        self.assertEqual(g.player.invincible, 1)
        self.hit()
        self.assertEqual(g.hp, 1)
        for _ in range(30):
            g.update()
        self.hit()
        self.assertEqual(g.state, GameState.GAME_OVER)

    def test_one_second_timing_pause(self):
        g = self.start()
        for _ in range(29):
            g.update()
        self.assertEqual(g.score.score, 0)
        g.update(paused=True)
        self.assertEqual(g.wave.ticks, 29)
        g.update()
        self.assertEqual(g.score.score, 10)

    def test_wave_interval_freezes_and_carries_hp(self):
        g = self.start()
        self.hit()
        self.safe_run(899)
        self.assertEqual(g.state, GameState.WAVE_CLEAR)
        self.assertEqual(g.score.score, 800)
        self.assertEqual(g.hp, 2)
        x, y = g.player.x, g.player.y
        for _ in range(89):
            g.update(1, True)
        self.assertEqual((g.player.x, g.player.y), (x, y))
        self.assertEqual(g.state, GameState.WAVE_CLEAR)
        g.update()
        self.assertEqual(g.state, GameState.PLAYING)
        self.assertFalse(g.wave.wave_damaged)
        self.assertEqual(g.wave.ticks, 0)
        self.assertEqual(g.hp, 2)

    def test_perfect_clear_6500_and_retry(self):
        g = self.start()
        for wave in range(5):
            self.safe_run(900)
            self.assertEqual(g.score.score, (wave+1)*1300)
            if wave < 4:
                for _ in range(90):
                    g.update()
        self.assertEqual(g.state, GameState.GAME_CLEAR)
        self.assertEqual(g.score.score, 6500)
        self.assertEqual(self.storage.best, 6500)
        g.update(start=True)
        self.assertEqual(g.score.best, 6500)
        self.assertEqual(g.score.score, 0)
        self.assertEqual(g.hp, 3)
        self.assertEqual(g.hazards, [])
        self.assertEqual(g.player.invincible, 0)
        self.assertEqual(g.player.x, C.PLAYER_START_X)
        self.assertEqual(g.camera.x, 0)
        self.assertEqual(g.wave.index, 0)
        self.assertFalse(g.wave.wave_damaged)
        self.assertEqual(g.interval_ticks, 0)

    def test_difficulty(self):
        self.assertEqual(len(C.WAVES), 5)
        for a, b in zip(C.WAVES, C.WAVES[1:]):
            self.assertGreater(a.poop_spawn_interval, b.poop_spawn_interval)
            self.assertLess(a.poop_min_speed, b.poop_min_speed)
            self.assertLess(a.poop_max_speed, b.poop_max_speed)
            self.assertLess(a.max_poops, b.max_poops)

    def test_hazard_cap_and_cleanup(self):
        g = self.start()
        g.wave.index = 4
        for _ in range(899):
            g.player.x = 126
            g.update()
            self.assertLessEqual(len(g.hazards), g.wave.settings.max_poops)
            self.assertTrue(all(h.alive for h in g.hazards))

if __name__ == '__main__':
    unittest.main()
