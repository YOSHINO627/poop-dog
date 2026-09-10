from enum import Enum, auto
import random
from . import config as C
from .player import Player
from .stage import Stage
from .camera import Camera
from .wave_manager import WaveManager
from .score_manager import ScoreManager
from .poop import create_hazard
from .floral import Floral
from .kibble import KibbleField
from .friend import Friend
from .rain_events import RainEvents
from .legendary_stick import LegendaryStick

class GameState(Enum):
    TITLE = auto()
    PLAYING = auto()
    WAVE_CLEAR = auto()
    GAME_OVER = auto()
    GAME_CLEAR = auto()

class Game:
    def __init__(self, storage, rng=None, hazard_factory=None, debug_enabled=False):
        self.debug_enabled = debug_enabled
        self.debug_start = (0, 0)
        self.rng = rng or random.Random()
        self.stage = Stage()
        self.hazard_factory = hazard_factory or (
            lambda rng, settings: create_hazard(rng, settings, self.stage))
        self.score = ScoreManager(storage, persist_best=not debug_enabled)
        self.reset()
        self.state = GameState.TITLE

    def reset(self):
        self.player, self.camera, self.wave = Player(), Camera(), WaveManager()
        if self.debug_enabled:
            self.wave.level, self.wave.index = self.debug_start
        self.hp = C.MAX_HP
        self.hazards = []
        self.florals = []
        self.kibbles = KibbleField()
        self.floral_spawn_ticks = self.next_floral_delay()
        self.heal_feedback_ticks = 0
        self.splashes = []
        self.interval_ticks = 0
        self.last_bonus = 0
        self.score.reset()
        self.begin_encounters()
        self.state = GameState.PLAYING

    def begin_encounters(self):
        self.sticks = []
        self.stick_spawn_ticks = self.rng.randint(C.STICK_SPAWN_MIN_TICKS, C.STICK_SPAWN_MAX_TICKS)
        self.rain = RainEvents(self.rng)
        # Spawn well away from the dog, so a new wave never causes instant damage.
        edge = C.STAGE_WIDTH-C.FRIEND_WIDTH if self.player.x < C.STAGE_WIDTH/2 else 0
        near = self.player.x + (170 if self.player.x < C.STAGE_WIDTH/2 else -170)
        self.friends = [Friend(kind, near if kind == "poodle" else edge) for kind in C.LEVELS[self.wave.level].friends]

    def damage(self):
        if not self.player.invincible and not self.player.stick_ticks:
            self.hp -= 1
            self.wave.wave_damaged = True
            self.player.invincible = C.INVINCIBLE_TICKS

    def next_floral_delay(self):
        return self.rng.randint(C.FLORAL_MIN_TICKS, C.FLORAL_MAX_TICKS)

    def update_sticks(self):
        # None marks an already-used spawn, even after the item is collected/missed.
        if self.stick_spawn_ticks is not None:
            self.stick_spawn_ticks -= 1
            if self.stick_spawn_ticks <= 0:
                self.sticks.append(LegendaryStick(self.rng.uniform(
                    self.camera.x + C.STICK_SIZE,
                    self.camera.x + C.WIDTH - C.STICK_SIZE * 2)))
                self.stick_spawn_ticks = None
        for stick in self.sticks:
            stick.update()
            if stick.alive and stick.hitbox.overlaps(self.player.hitbox):
                stick.alive = False
                self.player.stick_ticks = C.STICK_DURATION_TICKS
        self.sticks = [stick for stick in self.sticks if stick.alive]

    def update_florals(self):
        self.heal_feedback_ticks = max(0, self.heal_feedback_ticks - 1)
        self.floral_spawn_ticks -= 1
        if self.floral_spawn_ticks <= 0:
            if len(self.florals) < C.FLORAL_MAX_ITEMS:
                margin = C.FLORAL_SIZE + C.FLORAL_DRIFT
                self.florals.append(Floral(self.rng.uniform(
                    self.camera.x + margin, self.camera.x + C.WIDTH - margin)))
            self.floral_spawn_ticks = self.next_floral_delay()
        for floral in self.florals:
            floral.update()
            if floral.alive and floral.hitbox.overlaps(self.player.hitbox):
                floral.alive = False
                if self.hp < C.MAX_HP:
                    self.hp = min(C.MAX_HP, self.hp + C.FLORAL_HEAL)
                    self.heal_feedback_ticks = C.FLORAL_FEEDBACK_TICKS
        self.florals = [f for f in self.florals if f.alive]

    def update(self, direction=0, jump=False, start=False, paused=False, debug_target=None):
        if self.debug_enabled and isinstance(debug_target, dict):
            level, wave = debug_target.get("level"), debug_target.get("wave")
            if (type(level) is int and type(wave) is int
                    and 1 <= level <= len(C.LEVELS) and 1 <= wave <= len(C.WAVES)):
                self.debug_start = (level-1, wave-1)
                self.reset()
                return
        if paused:
            return
        if self.state in (GameState.TITLE, GameState.GAME_OVER, GameState.GAME_CLEAR):
            if start:
                self.reset()
            return
        if self.state == GameState.WAVE_CLEAR:
            self.interval_ticks += 1
            if self.interval_ticks >= C.INTERVAL_SECONDS * C.FPS:
                self.wave.advance()
                self.begin_encounters()
                self.state = GameState.PLAYING
            return
        self.player.update(direction, jump, self.stage.platforms)
        self.camera.update(self.player)
        # Pickup protection applies before hazards touching the dog on this tick.
        self.update_sticks()
        self.splashes = [(x, y, age - 1) for x, y, age in self.splashes if age > 1]
        self.wave.tick(self.score)
        self.rain.update(self.rng, self.wave, self.camera, self.hazards)
        for friend in self.friends:
            friend.update(self.player)
            if friend.hitbox.overlaps(self.player.hitbox):
                self.damage()
        if self.wave.spawn_due() and len(self.hazards) < self.wave.settings.max_poops:
            self.hazards.append(self.hazard_factory(self.rng, self.wave.settings))
        for hazard in self.hazards:
            hazard.update(self.stage.platforms)
            impact = getattr(hazard, 'impact', None)
            if impact:
                self.splashes.append((*impact, C.SPLASH_TICKS))
            if hazard.alive and hazard.hitbox.overlaps(self.player.hitbox):
                hazard.alive = False
                self.damage()
        self.hazards = [h for h in self.hazards if h.alive]
        # A lethal hit remains lethal; healing does not erase wave damage history.
        if self.hp > 0:
            self.update_florals()
            self.score.tick_combo()
            for _ in range(self.kibbles.update(self.rng, self.stage, self.camera, self.player)):
                self.score.collect_kibble()
        if self.hp <= 0:
            self.state = GameState.GAME_OVER
        elif self.wave.complete:
            self.last_bonus = self.score.clear_wave(self.wave.wave_damaged)
            self.hazards.clear()
            self.florals.clear()
            self.sticks.clear()
            self.kibbles = KibbleField()
            self.score.reset_combo()
            self.floral_spawn_ticks = self.next_floral_delay()
            self.heal_feedback_ticks = 0
            self.splashes.clear()
            self.interval_ticks = 0
            self.state = (GameState.GAME_CLEAR if self.wave.final
                          else GameState.WAVE_CLEAR)
