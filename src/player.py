from . import config as C
from .collision import Rect, horizontal_overlap

class Player:
    def __init__(self):
        self.x, self.y = C.PLAYER_START_X, C.GROUND_Y - C.PLAYER_SIZE
        self.vy = 0.0
        self.grounded = True
        self.facing = 1
        self.walk_ticks = 0
        self.moving = False
        self.invincible = 0
        self.stick_ticks = 0

    @property
    def hitbox(self):
        return Rect(self.x + C.HITBOX_X, self.y + C.HITBOX_Y, C.HITBOX_W, C.HITBOX_H)

    @property
    def frame(self):
        if not self.grounded:
            return 3
        return 1 + (self.walk_ticks // C.ANIMATION_TICKS) % 2 if self.moving else 0

    def update(self, direction, jump, platforms):
        self.invincible = max(0, self.invincible - 1)
        self.stick_ticks = max(0, self.stick_ticks - 1)
        self.moving = direction != 0
        old_center = self.x + C.PLAYER_SIZE / 2
        old_bottom = self.y + C.PLAYER_SIZE
        self.x = max(0, min(C.STAGE_WIDTH - C.PLAYER_SIZE, self.x + direction * C.PLAYER_SPEED))
        if direction:
            self.facing = direction
            self.walk_ticks += 1
        else:
            self.walk_ticks = 0
        if jump and self.grounded:
            self.vy = C.JUMP_SPEED
            self.grounded = False
        was_grounded = self.grounded
        self.vy = min(C.MAX_FALL_SPEED, self.vy + C.GRAVITY)
        next_bottom = old_bottom + self.vy
        center = self.x + C.PLAYER_SIZE / 2
        landings = []
        if self.vy >= 0:
            for p in platforms:
                if not horizontal_overlap(self.x + 2, C.PLAYER_SIZE - 4, p):
                    continue
                top = p.top_at(center)
                crossed = old_bottom <= top + 0.01 and next_bottom >= top
                # Follow a slope already under our feet, without snapping onto roofs.
                follows_slope = (was_grounded and p.end_y is not None
                                 and p.x <= old_center <= p.x + p.w
                                 and abs(old_bottom - p.top_at(old_center)) < 0.1)
                if crossed or follows_slope:
                    landings.append(top)
        self.grounded = bool(landings)
        if landings:
            self.y = min(landings) - C.PLAYER_SIZE
            self.vy = 0
        else:
            self.y += self.vy
