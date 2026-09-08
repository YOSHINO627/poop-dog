from .hazard import Hazard
from .collision import Rect, horizontal_overlap
from . import config as C

class Poop(Hazard):
    def __init__(self, x, speed, y=C.POOP_START_Y):
        self.x, self.y, self.speed = x, y, speed
        self.alive = True
        self.impact = None
        self.previous_y = y

    @property
    def hitbox(self):
        # Swept vertical box prevents tunnelling through the dog at high speeds.
        return Rect(self.x, self.previous_y, C.POOP_SIZE,
                    C.POOP_SIZE + self.y - self.previous_y)

    def update(self, platforms):
        self.previous_y = self.y
        bottom = self.y + C.POOP_SIZE
        self.y += self.speed
        surfaces = [p.top_at(self.x + C.POOP_SIZE / 2) for p in platforms
                    if horizontal_overlap(self.x, C.POOP_SIZE, p)]
        impacts = [top for top in surfaces if bottom <= top <= self.y + C.POOP_SIZE]
        if impacts:
            self.impact = (self.x, min(impacts))
            self.alive = False
        elif self.y > C.HEIGHT + C.POOP_SIZE:
            self.alive = False

    def draw(self, renderer):
        renderer.poop(self.x, self.y)

def create_hazard(rng, settings):
    return Poop(rng.uniform(0, C.STAGE_WIDTH - C.POOP_SIZE),
                rng.uniform(settings.poop_min_speed, settings.poop_max_speed))
