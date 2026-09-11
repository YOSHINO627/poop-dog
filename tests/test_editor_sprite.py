import importlib.util
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from src.game import GameState
from src.dog_sprites import sheet

class EditorSpriteTests(unittest.TestCase):
    def setUp(self):
        spec=importlib.util.spec_from_file_location('src.renderer_under_test','src/renderer.py')
        module=importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'pyxel':SimpleNamespace(images=[Mock()])}):
            spec.loader.exec_module(module)
        self.r=module.Renderer(True)
        self.g=SimpleNamespace(state=GameState.DOG_SELECT,breed_cursor=2,selected_breed=0,breed_revision=0)
        self.custom=['8'*64]*16

    def test_apply_in_selection_survives_confirm_retry_and_reselection(self):
        r,g=self.r,self.g
        r.sync_dog(g)
        r.set_custom_sprite(self.custom,g);r.sync_dog(g)
        self.assertEqual(r.current_rows,self.custom)
        g.selected_breed=2;g.breed_revision+=1;g.state=GameState.TITLE
        r.sync_dog(g);self.assertEqual(r.current_rows,self.custom)
        g.state=GameState.PLAYING;r.sync_dog(g)
        self.assertEqual(r.current_rows,self.custom)
        g.state=GameState.DOG_SELECT;g.breed_cursor=1;r.sync_dog(g)
        self.assertEqual(r.current_rows,sheet(1))
        g.breed_cursor=2;r.sync_dog(g);self.assertEqual(r.current_rows,self.custom)

    def test_invalid_sheet_preserves_image(self):
        r,g=self.r,self.g
        r.sync_dog(g);previous=r.current_rows
        r.set_custom_sprite(['bad'],g);r.sync_dog(g)
        self.assertEqual(r.current_rows,previous)
