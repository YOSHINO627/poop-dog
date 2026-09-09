import unittest
from src.game import Game, GameState
from test_game import Storage

class DebugTests(unittest.TestCase):
    def test_normal_ignores_debug_and_saves_best(self):
        storage = Storage()
        g = Game(storage)
        g.update(debug_target={'level': 3, 'wave': 4})
        self.assertEqual(g.state, GameState.TITLE)
        self.assertEqual(g.wave.level, 0)
        g.score.add(30)
        self.assertEqual(storage.best, 30)

    def test_jump_resets_everything_and_retry_keeps_target_not_best(self):
        storage = Storage()
        storage.best = 100
        g = Game(storage, debug_enabled=True)
        g.hp = 1
        g.player.invincible = 30
        g.score.add(9999)
        g.update(debug_target={'level': 3, 'wave': 4})
        self.assertEqual((g.wave.level, g.wave.index), (2, 3))
        self.assertEqual(len(g.friends), 2)
        self.assertEqual(g.hp, 3)
        self.assertEqual(g.player.invincible, 0)
        self.assertEqual(g.score.score, 0)
        self.assertEqual(g.score.best, 100)
        self.assertEqual(storage.best, 100)
        self.assertEqual(g.wave.ticks, 0)
        self.assertEqual(g.hazards, [])
        self.assertEqual(g.kibbles.items, [])
        self.assertEqual(g.florals, [])
        self.assertEqual(g.camera.x, 0)
        g.state = GameState.GAME_OVER
        g.update(start=True)
        self.assertEqual((g.wave.level, g.wave.index), (2, 3))
        g.update(debug_target={'level': 1, 'wave': 1})
        self.assertEqual(g.friends, [])

    def test_all_targets_and_invalid_input(self):
        g = Game(Storage(), debug_enabled=True)
        for level in range(1, 4):
            for wave in range(1, 6):
                g.update(debug_target={'level': level, 'wave': wave})
                self.assertEqual((g.wave.level, g.wave.index), (level-1, wave-1))
        for target in ({'level': 4, 'wave': 1}, {'level': True, 'wave': 1},
                       {'level': 1, 'wave': 0}, {'level': '1', 'wave': 1}, {}, []):
            g.update(paused=True, debug_target=target)
            self.assertEqual((g.wave.level, g.wave.index), (2, 4))
