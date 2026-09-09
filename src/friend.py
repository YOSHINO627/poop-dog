"""Persistent ground enemies: a follower and a runner with a readable drift."""
from . import config as C
from .collision import Rect

class Friend:
    def __init__(self, kind, x):
        self.kind, self.x = kind, x
        self.y = C.GROUND_Y-C.FRIEND_HEIGHT
        self.facing = -1
        self.age = 0
        self.overshoot = 0
        self.drift = 0

    @property
    def hitbox(self):
        return Rect(self.x+1, self.y+5, C.FRIEND_WIDTH-2, C.FRIEND_HEIGHT-5)

    def update(self, player):
        self.age += 1
        target = player.x+C.PLAYER_SIZE/2
        center = self.x+C.FRIEND_WIDTH/2
        delta = target-center
        if self.kind == 'poodle':
            if abs(delta) > C.POODLE_SPEED:
                self.facing = 1 if delta > 0 else -1
                self.x += self.facing*C.POODLE_SPEED
        elif self.drift:
            self.x += self.facing*C.CORGI_SPEED*self.drift/C.CORGI_DRIFT_TICKS*0.4
            self.drift -= 1
            if not self.drift:
                self.facing = 1 if target > self.x+C.FRIEND_WIDTH/2 else -1
        else:
            self.x += self.facing*C.CORGI_SPEED
            if self.overshoot:
                self.overshoot = max(0, self.overshoot-C.CORGI_SPEED)
                if not self.overshoot:
                    self.drift = C.CORGI_DRIFT_TICKS
            elif delta*(target-(self.x+C.FRIEND_WIDTH/2)) <= 0 and not player.grounded:
                self.overshoot = C.CORGI_OVERSHOOT
        limit = C.STAGE_WIDTH-C.FRIEND_WIDTH
        if self.x <= 0 or self.x >= limit:
            self.x = max(0, min(limit, self.x))
            if (self.kind == 'corgi' and not self.drift
                    and ((self.x == 0 and self.facing < 0) or (self.x == limit and self.facing > 0))):
                self.overshoot = 0
                self.drift = C.CORGI_DRIFT_TICKS

    def draw(self, renderer):
        renderer.friend(self)
