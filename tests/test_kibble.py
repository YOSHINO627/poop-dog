import random
import unittest
from src import config as C
from src.game import Game, GameState
from src.kibble import Kibble
from src.score_manager import ScoreManager
from test_game import Storage

class KibbleTests(unittest.TestCase):
    def test_points_combo_boundary_repeat_and_best(self):
        storage = Storage()
        score = ScoreManager(storage)
        for _ in range(5):
            for _ in range(C.KIBBLE_COMBO_TICKS):
                score.tick_combo()
            score.collect_kibble()
        self.assertEqual(score.score, 250)
        self.assertEqual(score.combo_count, 0)
        self.assertEqual(score.delicious_ticks, C.KIBBLE_FEEDBACK_TICKS)
        for _ in range(5):
            score.collect_kibble()
        self.assertEqual(score.score, 500)
        self.assertEqual(storage.best, 500)
        score.reset()
        self.assertEqual(score.score, 0)
        self.assertEqual(score.best, 500)
        self.assertEqual(score.combo_count, 0)
        self.assertEqual(score.delicious_ticks, 0)

    def test_timeout_breaks_chain(self):
        score = ScoreManager(Storage())
        for _ in range(4):
            score.collect_kibble()
        for _ in range(C.KIBBLE_COMBO_TICKS + 1):
            score.tick_combo()
        score.collect_kibble()
        self.assertEqual(score.score, 150)
        self.assertEqual(score.combo_count, 1)
        self.assertEqual(score.delicious_ticks, 0)

    def game(self):
        g = Game(Storage(), random.Random(123))
        g.update(start=True)
        return g

    def test_pickup_only_once_and_pause(self):
        g = self.game()
        g.kibbles.items = [Kibble(g.player.x+3, C.GROUND_Y-C.KIBBLE_SIZE)]
        g.update(paused=True)
        self.assertEqual(g.score.score, 0)
        self.assertEqual(g.kibbles.items[0].age, 0)
        g.update()
        self.assertEqual(g.score.score, 30)
        self.assertEqual(g.kibbles.items, [])
        g.update()
        self.assertEqual(g.score.score, 30)

    def test_spawn_surface_randomness_cap_and_expiry(self):
        g = self.game()
        positions = set()
        for camera_x in (0, 450, C.STAGE_WIDTH-C.WIDTH):
            g.camera.x = camera_x
            for _ in range(40):
                g.kibbles.spawn_ticks = 1
                g.kibbles.update(g.rng, g.stage, g.camera, g.player)
                self.assertLessEqual(len(g.kibbles.items), C.KIBBLE_MAX_ITEMS)
                for item in g.kibbles.items:
                    center = item.x + C.KIBBLE_SIZE/2
                    self.assertTrue(0 <= item.x <= C.STAGE_WIDTH-C.KIBBLE_SIZE)
                    top = min(p.top_at(center) for p in g.stage.platforms
                              if p.x <= center <= p.x+p.w)
                    self.assertAlmostEqual(item.y+C.KIBBLE_SIZE, top)
                    positions.add(item.x)
            g.kibbles.items.clear()
        self.assertGreater(len(positions), 30)
        g.kibbles.items = [Kibble(800, 100)]
        g.kibbles.items[0].age = C.KIBBLE_LIFETIME_TICKS-1
        g.kibbles.spawn_ticks = 100
        g.kibbles.update(g.rng, g.stage, g.camera, g.player)
        self.assertEqual(g.kibbles.items, [])

    def test_wave_clear_and_retry_reset(self):
        g = self.game()
        g.score.collect_kibble()
        g.kibbles.items = [Kibble(800, 100)]
        g.wave.ticks = C.WAVE_SECONDS*C.FPS-1
        g.update()
        self.assertEqual(g.state, GameState.WAVE_CLEAR)
        self.assertEqual(g.kibbles.items, [])
        self.assertEqual(g.score.combo_count, 0)
        clock = g.score.combo_clock
        g.update()
        self.assertEqual(g.score.combo_clock, clock)
        g.reset()
        self.assertEqual(g.score.score, 0)
        self.assertGreater(g.score.best, 0)
        self.assertEqual(g.kibbles.items, [])
