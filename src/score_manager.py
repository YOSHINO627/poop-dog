from . import config as C

class ScoreManager:
    def __init__(self, storage):
        self.storage = storage
        self.best = max(0, int(storage.load_best()))
        self.reset()

    def reset(self):
        self.score = 0
        self.reset_combo()

    def reset_combo(self):
        self.combo_count = 0
        self.combo_clock = 0
        self.last_kibble_tick = None
        self.delicious_ticks = 0

    def tick_combo(self):
        self.combo_clock += 1
        self.delicious_ticks = max(0, self.delicious_ticks - 1)
        if (self.last_kibble_tick is not None
                and self.combo_clock - self.last_kibble_tick > C.KIBBLE_COMBO_TICKS):
            self.combo_count = 0
            self.last_kibble_tick = None

    def collect_kibble(self):
        self.add(C.KIBBLE_POINTS)
        self.combo_count += 1
        self.last_kibble_tick = self.combo_clock
        if self.combo_count == C.KIBBLE_COMBO_COUNT:
            self.add(C.KIBBLE_COMBO_POINTS)
            self.combo_count = 0
            self.delicious_ticks = C.KIBBLE_FEEDBACK_TICKS

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
