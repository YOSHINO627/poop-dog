from pathlib import Path
import os
import pyxel
from src import config as C
from src.bridge import Bridge
from src.game import Game, GameState
from src.renderer import Renderer

class App:
    def __init__(self):
        os.chdir(Path(__file__).resolve().parent)
        pyxel.init(C.WIDTH, C.HEIGHT, title='POOP DOG', fps=C.FPS, quit_key=pyxel.KEY_NONE)
        pyxel.colors.from_list(C.PALETTE)
        self.bridge = Bridge()
        self.game = Game(self.bridge, debug_enabled=self.bridge.debug_enabled)
        self.renderer = Renderer(web_controls=self.bridge.host is not None)
        self.previous_jump = False
        self.shared_sprite = None
        pyxel.run(self.update, self.draw)

    def update(self):
        web = self.bridge.input()
        keys = lambda *codes: any(pyxel.btn(key) for key in codes)
        left = keys(pyxel.KEY_A, pyxel.KEY_LEFT) or web.get('left', False)
        right = keys(pyxel.KEY_D, pyxel.KEY_RIGHT) or web.get('right', False)
        held = keys(pyxel.KEY_W, pyxel.KEY_UP, pyxel.KEY_SPACE) or web.get('jump', False)
        jump = (held and not self.previous_jump) or web.get('jumpPressed', False)
        self.previous_jump = held
        start = web.get('start', False) or pyxel.btnp(pyxel.KEY_RETURN) or jump
        if self.game.state != GameState.PLAYING and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            start = True
        self.game.update(int(right) - int(left), jump, start, web.get('paused', False), web.get('debugTarget'),
                         pyxel.btnp(pyxel.KEY_D) or web.get('dogSelect', False), web.get('selectStep', 0))
        sprite = self.bridge.sprite()
        if sprite is not None:
            self.renderer.set_custom_sprite(sprite, self.game)
        self.renderer.sync_dog(self.game)
        if self.shared_sprite is not self.renderer.current_rows:
            self.shared_sprite = self.renderer.current_rows
            self.bridge.publish_sprite(self.shared_sprite)
        self.bridge.publish(self.game)

    def draw(self):
        self.renderer.draw(self.game)

if __name__ == '__main__':
    App()
