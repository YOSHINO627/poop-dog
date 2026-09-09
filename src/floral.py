"""A rare healing breeze; separate from damaging hazards."""
import math
from . import config as C
from .collision import Rect

class Floral:
    def __init__(self, x, y=-C.FLORAL_SIZE):
        self.anchor_x = self.x = x
        self.y = self.previous_y = y
        self.age = 0
        self.alive = True

    @property
    def hitbox(self):
        return Rect(self.x, self.previous_y, C.FLORAL_SIZE,
                    C.FLORAL_SIZE + self.y - self.previous_y)

    def update(self):
        self.age += 1
        self.previous_y = self.y
        self.x = max(0, min(C.STAGE_WIDTH - C.FLORAL_SIZE,
                     self.anchor_x + math.sin(self.age / C.FLORAL_DRIFT_TICKS) * C.FLORAL_DRIFT))
        self.y += C.FLORAL_SPEED
        # Scent passes through shelters, but disappears once it reaches the grass.
        if self.y >= C.GROUND_Y:
            self.alive = False

    def draw(self, renderer):
        renderer.floral(self.x, self.y, self.age)
