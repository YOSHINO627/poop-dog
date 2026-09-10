import random
import unittest
from src import config as C
from src.game import Game, GameState
from src.legendary_stick import LegendaryStick

class Storage:
    def load_best(self): return 0
    def save_best(self, value): pass

class StickTests(unittest.TestCase):
    def setUp(self):
        self.g = Game(Storage(), random.Random(12))
        self.g.update(start=True)

    def test_one_spawn_per_wave_and_new_wave(self):
        g = self.g
        g.stick_spawn_ticks = 1
        g.update_sticks()
        self.assertEqual(len(g.sticks), 1)
        self.assertIsNone(g.stick_spawn_ticks)
        for _ in range(C.WAVE_SECONDS * C.FPS): g.update_sticks()
        self.assertEqual(g.sticks, [])
        self.assertIsNone(g.stick_spawn_ticks)
        g.begin_encounters()
        self.assertIsNotNone(g.stick_spawn_ticks)

    def test_pickup_protection_expiry_and_reset(self):
        g = self.g
        g.sticks = [LegendaryStick(g.player.x, g.player.y + 6)]
        g.update_sticks()
        self.assertEqual(g.player.stick_ticks, C.STICK_DURATION_TICKS)
        self.assertEqual(g.sticks, [])
        g.damage()
        self.assertEqual(g.hp, 3)
        self.assertFalse(g.wave.wave_damaged)
        for _ in range(C.STICK_DURATION_TICKS):
            g.player.update(0, False, g.stage.platforms)
        g.damage()
        self.assertEqual(g.hp, 2)
        self.assertTrue(g.wave.wave_damaged)
        g.player.stick_ticks = 50
        g.reset()
        self.assertEqual(g.player.stick_ticks, 0)

    def test_pause_and_interval_freeze_effect(self):
        g = self.g
        g.player.stick_ticks = 50
        delay = g.stick_spawn_ticks
        g.update(paused=True)
        self.assertEqual(g.stick_spawn_ticks, delay)
        g.state = GameState.WAVE_CLEAR
        g.update()
        self.assertEqual(g.player.stick_ticks, 50)

    def test_missed_item_removed(self):
        stick = LegendaryStick(10, C.GROUND_Y - 0.1)
        stick.update()
        self.assertFalse(stick.alive)
