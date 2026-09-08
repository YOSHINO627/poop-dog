from enum import Enum, auto
import random
from . import config as C
from .player import Player
from .stage import Stage
from .camera import Camera
from .wave_manager import WaveManager
from .score_manager import ScoreManager
from .poop import create_hazard

class GameState(Enum):
    TITLE = auto()
    PLAYING = auto()
    WAVE_CLEAR = auto()
    GAME_OVER = auto()
    GAME_CLEAR = auto()

class Game:
    def __init__(self, storage, rng=None, hazard_factory=create_hazard):
        self.rng = rng or random.Random()
        self.hazard_factory = hazard_factory
        self.stage = Stage()
        self.score = ScoreManager(storage)
        self.reset()
        self.state = GameState.TITLE

    def reset(self):
        self.player, self.camera, self.wave = Player(), Camera(), WaveManager()
        self.hp = C.MAX_HP
        self.hazards = []
        self.splashes = []
        self.interval_ticks = 0
        self.last_bonus = 0
        self.score.reset()
        self.state = GameState.PLAYING

    def update(self, direction=0, jump=False, start=False, paused=False):
        if paused:
            return
        if self.state in (GameState.TITLE, GameState.GAME_OVER, GameState.GAME_CLEAR):
            if start:
                self.reset()
            return
        if self.state == GameState.WAVE_CLEAR:
            self.interval_ticks += 1
            if self.interval_ticks >= C.INTERVAL_SECONDS * C.FPS:
                self.wave.index += 1
                self.wave.begin()
                self.state = GameState.PLAYING
            return
        self.player.update(direction, jump, self.stage.platforms)
        self.camera.update(self.player)
        self.splashes = [(x, y, age - 1) for x, y, age in self.splashes if age > 1]
        self.wave.tick(self.score)
        if self.wave.spawn_due() and len(self.hazards) < self.wave.settings.max_poops:
            self.hazards.append(self.hazard_factory(self.rng, self.wave.settings))
        for hazard in self.hazards:
            hazard.update(self.stage.platforms)
            impact = getattr(hazard, 'impact', None)
            if impact:
                self.splashes.append((*impact, C.SPLASH_TICKS))
            if hazard.alive and hazard.hitbox.overlaps(self.player.hitbox):
                hazard.alive = False
                if not self.player.invincible:
                    self.hp -= 1
                    self.wave.wave_damaged = True
                    self.player.invincible = C.INVINCIBLE_TICKS
        self.hazards = [h for h in self.hazards if h.alive]
        if self.hp <= 0:
            self.state = GameState.GAME_OVER
        elif self.wave.complete:
            self.last_bonus = self.score.clear_wave(self.wave.wave_damaged)
            self.hazards.clear()
            self.splashes.clear()
            self.interval_ticks = 0
            self.state = (GameState.GAME_CLEAR if self.wave.index == len(C.WAVES) - 1
                          else GameState.WAVE_CLEAR)
