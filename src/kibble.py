"""Frequent food pickups on reachable field surfaces."""
from . import config as C
from .collision import Rect

class Kibble:
    def __init__(self, x, y):
        self.x, self.y, self.age = x, y, 0

    @property
    def hitbox(self):
        return Rect(self.x, self.y, C.KIBBLE_SIZE, C.KIBBLE_SIZE)

    def draw(self, renderer):
        renderer.kibble(self.x, self.y, self.age)

class KibbleField:
    def __init__(self):
        self.items = []
        self.spawn_ticks = C.KIBBLE_MIN_TICKS

    def update(self, rng, stage, camera, player):
        for item in self.items:
            item.age += 1
        self.items = [item for item in self.items if item.age < C.KIBBLE_LIFETIME_TICKS]
        self.spawn_ticks -= 1
        if self.spawn_ticks <= 0:
            if len(self.items) < C.KIBBLE_MAX_ITEMS:
                # New food appears in view, on the top surface at a random X.
                # Existing food remains in world coordinates when the camera moves.
                for _ in range(12):
                    x = rng.uniform(camera.x, camera.x + C.WIDTH - C.KIBBLE_SIZE)
                    center = x + C.KIBBLE_SIZE / 2
                    top = min(p.top_at(center) for p in stage.platforms
                              if p.x <= center <= p.x + p.w)
                    item = Kibble(x, top - C.KIBBLE_SIZE)
                    if not any(item.hitbox.overlaps(other.hitbox) for other in self.items):
                        self.items.append(item)
                        break
            self.spawn_ticks = rng.randint(C.KIBBLE_MIN_TICKS, C.KIBBLE_MAX_TICKS)
        picked = [item for item in self.items if item.hitbox.overlaps(player.hitbox)]
        self.items = [item for item in self.items if item not in picked]
        return len(picked)
