from . import config as C

class WaveManager:
    def __init__(self):
        self.index = 0
        self.begin()

    def begin(self):
        self.ticks = 0
        self.spawn_ticks = 0
        self.wave_damaged = False

    @property
    def settings(self):
        return C.WAVES[self.index]

    @property
    def remaining(self):
        return max(0, C.WAVE_SECONDS - self.ticks // C.FPS)

    @property
    def complete(self):
        return self.ticks >= C.WAVE_SECONDS * C.FPS

    def tick(self, score):
        self.ticks += 1
        self.spawn_ticks += 1
        if self.ticks % C.FPS == 0:
            score.survived_second()

    def spawn_due(self):
        if self.spawn_ticks >= self.settings.poop_spawn_interval:
            self.spawn_ticks = 0
            return True
        return False
