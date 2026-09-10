import random
import unittest
from src.game import Game, GameState
from src.dog_sprites import BREEDS, sheet

class Storage:
    def load_best(self): return 50
    def save_best(self, value): pass

class DogSelectionTests(unittest.TestCase):
    def setUp(self):
        self.g = Game(Storage(), random.Random(1))

    def test_all_sheets_have_four_valid_distinct_frames(self):
        self.assertEqual(len(BREEDS), 5)
        for i in range(5):
            rows = sheet(i)
            self.assertEqual(len(rows), 16)
            self.assertTrue(all(len(row) == 64 for row in rows))
            self.assertTrue(all(set(row) <= set('0123456789abcdef') for row in rows))
            frames = [tuple(row[x:x+16] for row in rows) for x in (0,16,32,48)]
            self.assertGreaterEqual(len(set(frames)), 3)

    def test_d_open_does_not_skip_first_dog_and_hold_does_not_repeat(self):
        g = self.g
        g.update(direction=1, dog_select=True)
        g.update(direction=1)
        self.assertEqual(g.breed_cursor, 0)
        g.update()
        g.update(direction=1)
        g.update(direction=1)
        self.assertEqual(g.breed_cursor, 1)
        g.update(start=True)
        self.assertEqual(g.state, GameState.TITLE)
        self.assertEqual(g.selected_breed, 1)
        g.update(start=True)
        self.assertEqual(g.state, GameState.PLAYING)
        self.assertEqual(g.selected_breed, 1)

    def test_wrap_return_results_score_unchanged_and_retry(self):
        g = self.g
        for state in (GameState.GAME_OVER, GameState.GAME_CLEAR):
            g.state = state
            g.score.score = 1234
            g.update(dog_select=True)
            g.update(select_step=-1)
            self.assertEqual(g.breed_cursor, (g.selected_breed-1) % 5)
            g.update(start=True)
            self.assertEqual(g.state, state)
            self.assertEqual(g.score.score, 1234)
            selected = g.selected_breed
            g.update(start=True)
            self.assertEqual(g.selected_breed, selected)

    def test_gameplay_d_is_still_movement(self):
        g = self.g
        g.update(start=True)
        x = g.player.x
        g.update(direction=1, dog_select=True)
        self.assertEqual(g.state, GameState.PLAYING)
        self.assertGreater(g.player.x, x)
