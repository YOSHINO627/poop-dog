from dataclasses import dataclass

@dataclass(frozen=True)
class Platform:
    """One-way walkable surface; rain always strikes the top."""
    x: float
    y: float
    w: float
    end_y: float | None = None

    def top_at(self, x):
        if self.end_y is None:
            return self.y
        fraction = max(0, min(1, (x - self.x) / self.w))
        return self.y + (self.end_y - self.y) * fraction
