import random
import unittest
from unittest.mock import patch
from src import config as C
from src.game import Game, GameState
from src.player import Player
from src.poop import Poop, create_hazard
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
        # Isolate score/timing assertions from random piercing damage.
        # Roof-piercing generation and damage are tested separately below.
        self.game.hazard_factory = lambda rng, settings: Poop(126, settings.poop_min_speed)
        self.game.player.x = 126
        # Base score excludes optional food points.
        with patch("src.kibble.KibbleField.update", return_value=0), patch("src.friend.Friend.update") :
            for _ in range(ticks):
                self.game.update()

    def test_title_start(self):
        self.assertEqual(self.game.state, GameState.TITLE)
        self.start()
        self.assertEqual(self.game.hp, 3)
        self.assertEqual(self.game.state, GameState.PLAYING)

    def test_kibble_heals_every_thirty_without_erasing_damage_or_score(self):
        g = self.start()
        g.damage()
        for _ in range(29):
            g.collect_kibble()
        self.assertEqual(g.hp, 2)
        g.collect_kibble()
        self.assertEqual((g.hp, g.kibble_heal_count), (3, 0))
        self.assertTrue(g.wave.wave_damaged)
        self.assertEqual(g.score.score, 30 * 30 + 6 * 100)
        self.assertEqual(g.heal_feedback_label, 'FOOD +1')
        for _ in range(30):
            g.collect_kibble()
        self.assertEqual((g.hp, g.kibble_heal_count), (3, 0))

    def test_kibble_heal_progress_survives_wave_and_resets_on_retry(self):
        g = self.start()
        for _ in range(29):
            g.collect_kibble()
        g.state = GameState.WAVE_CLEAR
        g.interval_ticks = C.INTERVAL_SECONDS * C.FPS - 1
        g.update()
        self.assertEqual(g.kibble_heal_count, 29)
        g.damage()
        with patch('src.kibble.KibbleField.update', return_value=1):
            g.update()
        self.assertEqual((g.hp, g.kibble_heal_count), (3, 0))
        g.collect_kibble()
        g.state = GameState.GAME_OVER
        g.update(start=True)
        self.assertEqual(g.kibble_heal_count, 0)

    def test_kibble_does_not_revive_dead_player(self):
        g = self.start()
        g.hp = 0
        g.kibble_heal_count = 29
        with patch('src.kibble.KibbleField.update', return_value=1):
            g.update()
        self.assertEqual(g.hp, 0)
        self.assertEqual(g.state, GameState.GAME_OVER)

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

    def test_perfect_clear_19500_and_retry(self):
        g = self.start()
        for wave in range(15):
            self.safe_run(900)
            self.assertEqual(g.score.score, (wave+1)*1300)
            if wave < 14:
                for _ in range(90):
                    g.update()
        self.assertEqual(g.state, GameState.GAME_CLEAR)
        self.assertEqual(g.score.score, 19500)
        self.assertEqual(self.storage.best, 19500)
        g.update(start=True)
        self.assertEqual(g.score.best, 19500)
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

    def test_piercing_mixture_starts_in_wave_two(self):
        rng = random.Random(42)
        for index, settings in enumerate(C.WAVES):
            hazards = [create_hazard(rng, settings) for _ in range(200)]
            count = sum(h.piercing for h in hazards)
            if index == 0:
                self.assertEqual(count, 0)
            else:
                self.assertGreater(count, 0)
                self.assertLess(count, len(hazards))

    def test_piercing_ignores_every_object_but_stops_at_ground(self):
        for platform in self.game.stage.platforms[:-1]:
            x = platform.x + platform.w / 2
            y = platform.top_at(x + C.POOP_SIZE / 2) - C.POOP_SIZE - 1
            strong = Poop(x, 2, y, piercing=True)
            normal = Poop(x, 2, y)
            strong.update([platform])
            normal.update([platform])
            self.assertTrue(strong.alive)
            self.assertIsNone(strong.impact)
            self.assertFalse(normal.alive)
        strong = Poop(128, 3, C.GROUND_Y - C.POOP_SIZE - 1, piercing=True)
        strong.update(self.game.stage.platforms)
        self.assertFalse(strong.alive)
        escaped = Poop(128, 3, C.HEIGHT + C.POOP_SIZE, piercing=True)
        escaped.update([])
        self.assertFalse(escaped.alive)

    def test_piercing_hits_under_bench_and_respects_invincibility(self):
        g = self.start()
        g.player.x = 126
        g.hazards = [Poop(128, 2, 90, piercing=True)]
        for _ in range(12):
            g.update()
        self.assertEqual(g.hp, 2)
        self.assertTrue(g.wave.wave_damaged)
        self.assertTrue(g.player.invincible)
        g.hazards = [Poop(128, 1, 114, piercing=True)]
        g.update()
        self.assertEqual(g.hp, 2)
        self.assertEqual(g.hazards, [])

class SpawnBiasTests(unittest.TestCase):
    def test_strong_prefers_objects_but_also_open_ground(self):
        from src.stage import Stage
        from dataclasses import replace
        stage, rng = Stage(), random.Random(732)
        covered, _ = stage.spawn_regions()
        settings = replace(C.WAVES[1], piercing_chance=1.0)
        hazards = [create_hazard(rng, settings, stage) for _ in range(10000)]
        hits = sum(any(a < h.x < b for a, b in covered) for h in hazards)
        self.assertTrue(all(h.piercing for h in hazards))
        self.assertTrue(0.68 < hits / len(hazards) < 0.72)
        self.assertTrue(all(0 <= h.x <= C.STAGE_WIDTH-C.POOP_SIZE for h in hazards))

    def test_normal_remains_uniform_and_empty_stage_is_safe(self):
        from src.stage import Stage
        stage, rng = Stage(), random.Random(912)
        covered, _ = stage.spawn_regions()
        hazards = [create_hazard(rng, C.WAVES[0], stage) for _ in range(10000)]
        ratio = sum(any(a < h.x < b for a, b in covered) for h in hazards) / len(hazards)
        expected = sum(b-a for a,b in covered) / (C.STAGE_WIDTH-C.POOP_SIZE)
        self.assertAlmostEqual(ratio, expected, delta=0.02)
        stage.objects = []
        self.assertTrue(0 <= stage.spawn_x(rng, 1) <= C.STAGE_WIDTH-C.POOP_SIZE)
        stage.objects = [{'kind':'platform', 'x':0, 'w':C.STAGE_WIDTH}]
        self.assertTrue(0 <= stage.spawn_x(rng, 0) <= C.STAGE_WIDTH-C.POOP_SIZE)

    def test_open_ground_never_overlaps_an_object(self):
        from src.stage import Stage
        from src.collision import horizontal_overlap
        stage, rng = Stage(), random.Random(45)
        for _ in range(500):
            x = stage.spawn_x(rng, 0)
            self.assertFalse(any(horizontal_overlap(x, C.POOP_SIZE, p)
                                 for p in stage.platforms[:-1]))

class FloralTests(unittest.TestCase):
    def make_game(self):
        g = Game(Storage(), random.Random(51))
        g.update(start=True)
        return g

    def touch(self, g):
        from src.floral import Floral
        g.florals = [Floral(g.player.x, g.player.y+5)]
        g.update()

    def test_heal_one_cap_and_no_damage_history_reset(self):
        g = self.make_game()
        g.hp = 1
        g.wave.wave_damaged = True
        self.touch(g)
        self.assertEqual(g.hp, 2)
        self.assertTrue(g.wave.wave_damaged)
        self.assertTrue(g.heal_feedback_ticks)
        self.assertEqual(g.florals, [])
        self.touch(g)
        self.touch(g)
        self.assertEqual(g.hp, 3)
        self.assertEqual(g.score.score, 0)

    def test_rare_spawn_in_view_and_item_cap(self):
        from src.floral import Floral
        g = self.make_game()
        self.assertTrue(C.FLORAL_MIN_TICKS <= g.floral_spawn_ticks <= C.FLORAL_MAX_TICKS)
        self.assertEqual(g.florals, [])
        g.floral_spawn_ticks = 1
        g.update()
        self.assertEqual(len(g.florals), 1)
        self.assertTrue(g.camera.x <= g.florals[0].x <= g.camera.x+C.WIDTH)
        g.floral_spawn_ticks = 1
        g.update()
        self.assertEqual(len(g.florals), 1)
        f = Floral(125)
        for _ in range(250):
            f.update()
        self.assertFalse(f.alive)

    def test_freeze_clear_and_retry(self):
        from src.floral import Floral
        g = self.make_game()
        g.florals = [Floral(150)]
        delay = g.floral_spawn_ticks
        g.update(paused=True)
        self.assertEqual(g.florals[0].age, 0)
        self.assertEqual(g.floral_spawn_ticks, delay)
        g.state = GameState.WAVE_CLEAR
        g.update()
        self.assertEqual(g.florals[0].age, 0)
        g.state = GameState.PLAYING
        g.wave.ticks = C.WAVE_SECONDS*C.FPS - 1
        g.update()
        self.assertEqual(g.florals, [])
        g.florals = [Floral(150)]
        g.heal_feedback_ticks = 20
        g.reset()
        self.assertEqual(g.florals, [])
        self.assertEqual(g.heal_feedback_ticks, 0)

    def test_floral_does_not_revive_lethal_hit(self):
        from src.floral import Floral
        g = self.make_game()
        g.hp = 1
        g.florals = [Floral(g.player.x, g.player.y+5)]
        g.hazards = [Poop(g.player.x+2, 1, g.player.y+5)]
        g.update()
        self.assertEqual(g.hp, 0)
        self.assertEqual(g.state, GameState.GAME_OVER)

if __name__ == '__main__':
    unittest.main()
