from . import config as C

class Camera:
    def __init__(self):
        self.x = 0

    def update(self, player):
        self.x = max(0, min(C.STAGE_WIDTH - C.WIDTH, player.x + C.PLAYER_SIZE / 2 - C.WIDTH / 2))
