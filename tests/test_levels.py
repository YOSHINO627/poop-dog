import random
import unittest
from unittest.mock import patch
from src import config as C
from src.game import Game, GameState
from src.friend import Friend
from src.player import Player
from src.poop import Poop
from src.rain_events import RainEvents
from test_game import Storage

class LevelTests(unittest.TestCase):
    def game(self, level=0):
        g = Game(Storage(), random.Random(8))
        g.update(start=True)
        g.wave.level = level
        g.begin_encounters()
        return g

    def test_level_transition_hp_and_counts(self):
        g = self.game()
        for level, count in enumerate((0, 1, 2)):
            self.assertEqual(g.wave.level, level)
            self.assertEqual(len(g.friends), count)
            g.hp = 2
            g.wave.index = 4
            g.wave.ticks = 899
            g.update()
            self.assertEqual(g.hp, 2)
            if level < 2:
                self.assertEqual(g.state, GameState.WAVE_CLEAR)
                for _ in range(90):
                    g.update()
                self.assertEqual(g.wave.index, 0)
            else:
                self.assertEqual(g.state, GameState.GAME_CLEAR)
        g.reset()
        self.assertEqual(g.wave.level, 0)
        self.assertEqual(g.friends, [])
        self.assertEqual(g.rain.shower, 0)

    def test_poodle_chases_damage_persists_and_jump_avoids(self):
        g = self.game(1)
        dog = g.friends[0]
        before = dog.x
        g.update()
        self.assertLess(dog.x, before)
        dog.x = g.player.x
        g.update()
        self.assertEqual(g.hp, 2)
        g.update()
        self.assertEqual(g.hp, 2)
        self.assertEqual(len(g.friends), 1)
        g.player.invincible = 0
        g.player.y -= 30
        g.player.grounded = False
        g.update()
        self.assertEqual(g.hp, 2)

    def test_runner_jump_overshoot_drift_and_turn(self):
        p = Player()
        p.x, p.y, p.grounded = 150, 70, False
        dog = Friend('corgi', 147)
        dog.facing = 1
        dog.update(p)
        self.assertGreater(dog.overshoot, 0)
        for _ in range(12):
            dog.update(p)
        self.assertGreater(dog.x, 175)
        self.assertGreater(dog.drift, 0)
        for _ in range(C.CORGI_DRIFT_TICKS):
            dog.update(p)
        self.assertEqual(dog.facing, -1)
        self.assertLess(dog.drift, 1)

    def test_runner_edges_and_pause(self):
        p = Player()
        dog = Friend('corgi', C.STAGE_WIDTH-C.FRIEND_WIDTH)
        dog.facing = 1
        for _ in range(40):
            dog.update(p)
        self.assertLess(dog.x, C.STAGE_WIDTH-C.FRIEND_WIDTH)
        g = self.game(2)
        x, delay = g.friends[0].x, g.rain.delay
        g.update(paused=True)
        self.assertEqual(g.friends[0].x, x)
        self.assertEqual(g.rain.delay, delay)

    def test_giant_only_late_level_three_and_roof(self):
        g = self.game()
        for level in range(3):
            for index in range(5):
                g.wave.level, g.wave.index = level, index
                rain = RainEvents(g.rng)
                rain.giant_ticks = C.GIANT_INTERVAL-1
                items = []
                rain.update(g.rng, g.wave, g.camera, items)
                self.assertEqual(bool(items), level == 2 and index >= 3)
        giant = Poop(125, 20, 65, size=C.GIANT_SIZE)
        giant.update(g.stage.platforms)
        self.assertFalse(giant.alive)
        self.assertEqual(giant.impact[1], 99)

    def test_meteor_warning_duration_and_cap(self):
        g = self.game()
        rain = g.rain
        rain.delay = 1
        with patch('src.config.METEOR_CHANCE', 1):
            rain.update(g.rng, g.wave, g.camera, g.hazards)
        self.assertEqual(rain.warning, C.METEOR_WARNING_TICKS)
        self.assertEqual(g.hazards, [])
        for _ in range(C.METEOR_WARNING_TICKS+C.METEOR_DURATION):
            rain.update(g.rng, g.wave, g.camera, g.hazards)
        self.assertEqual(rain.shower, 0)
        self.assertTrue(all(h.meteor for h in g.hazards))
        self.assertGreater(len(g.hazards), 0)
        g.hazards = [Poop(0, 1)]*g.wave.settings.max_poops
        rain.shower = 11
        rain.update(g.rng, g.wave, g.camera, g.hazards)
        self.assertEqual(len(g.hazards), g.wave.settings.max_poops)
