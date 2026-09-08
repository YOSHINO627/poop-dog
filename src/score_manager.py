from . import config as C

class ScoreManager:
    def __init__(self, storage):
        self.storage = storage
        self.best = max(0, int(storage.load_best()))
        self.reset()

    def reset(self):
        self.score = 0

    def add(self, points):
        self.score += points
        if self.score > self.best:
            self.best = self.score
            self.storage.save_best(self.best)

    def survived_second(self):
        self.add(C.SURVIVAL_POINTS)

    def clear_wave(self, damaged):
        bonus = C.CLEAR_POINTS + (0 if damaged else C.NO_DAMAGE_POINTS)
        self.add(bonus)
        return bonus
