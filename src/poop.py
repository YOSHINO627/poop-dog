from .hazard import Hazard
from .collision import Rect, horizontal_overlap
from . import config as C

class Poop(Hazard):
    def __init__(self, x, speed, y=C.POOP_START_Y, *, piercing=False):
        self.x, self.y, self.speed = x, y, speed
        self.piercing = piercing
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
                    if horizontal_overlap(self.x, C.POOP_SIZE, p)
                    and (not self.piercing or
                         (p.x == 0 and p.w == C.STAGE_WIDTH
                          and p.y == C.GROUND_Y and p.end_y is None))]
        impacts = [top for top in surfaces if bottom <= top <= self.y + C.POOP_SIZE]
        if impacts:
            self.impact = (self.x, min(impacts))
            self.alive = False
        elif self.y > C.HEIGHT + C.POOP_SIZE:
            self.alive = False

    def draw(self, renderer):
        renderer.poop(self.x, self.y, self.piercing)

def create_hazard(rng, settings, stage=None):
    piercing = rng.random() < settings.piercing_chance
    x = (stage.spawn_x(rng, C.PIERCING_OBJECT_BIAS) if piercing and stage
         else rng.uniform(0, C.STAGE_WIDTH - C.POOP_SIZE))
    return Poop(x,
                rng.uniform(settings.poop_min_speed, settings.poop_max_speed),
                piercing=piercing)
