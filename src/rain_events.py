from . import config as C
from .poop import Poop

class RainEvents:
    def __init__(self, rng):
        self.delay = rng.randint(C.METEOR_DELAY_MIN, C.METEOR_DELAY_MAX)
        self.warning = self.shower = 0
        self.giant_ticks = 0

    def update(self, rng, wave, camera, hazards):
        self.giant_ticks += 1
        if (wave.index+1 >= C.LEVELS[wave.level].giant_from_wave
                and self.giant_ticks >= C.GIANT_INTERVAL):
            self.giant_ticks = 0
            if len(hazards) < wave.settings.max_poops:
                hazards.append(Poop(rng.uniform(camera.x, camera.x+C.WIDTH-C.GIANT_SIZE),
                                    C.GIANT_SPEED, -C.GIANT_SIZE, size=C.GIANT_SIZE))
        if self.warning:
            self.warning -= 1
            if not self.warning:
                self.shower = C.METEOR_DURATION
        elif self.shower:
            self.shower -= 1
            if self.shower % C.METEOR_INTERVAL == 0 and len(hazards) < wave.settings.max_poops:
                hazards.append(Poop(rng.uniform(camera.x, camera.x+C.WIDTH-C.POOP_SIZE),
                                    C.METEOR_SPEED, meteor=True))
        else:
            self.delay -= 1
            if self.delay <= 0:
                self.delay = rng.randint(C.METEOR_DELAY_MIN, C.METEOR_DELAY_MAX)
                if rng.random() < C.METEOR_CHANCE:
                    self.warning = C.METEOR_WARNING_TICKS
