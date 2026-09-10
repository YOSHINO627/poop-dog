"""A once-per-wave pickup, independent of damaging hazards."""
from . import config as C
from .collision import Rect


class LegendaryStick:
    def __init__(self, x, y=-C.STICK_SIZE):
        self.x, self.y = x, y
        self.previous_y = y
        self.age = 0
        self.alive = True

    @property
    def hitbox(self):
        return Rect(self.x, self.previous_y, C.STICK_SIZE,
                    C.STICK_SIZE + self.y - self.previous_y)

    def update(self):
        self.age += 1
        self.previous_y = self.y
        self.y += C.STICK_SPEED
        # Magic reaches dogs under shelters too; missed pickups do not accumulate.
        if self.y >= C.GROUND_Y:
            self.alive = False

    def draw(self, renderer):
        renderer.legendary_stick(self.x, self.y, self.age)
