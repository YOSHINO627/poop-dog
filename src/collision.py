from dataclasses import dataclass

@dataclass
class Rect:
    x: float
    y: float
    w: float
    h: float

    @property
    def bottom(self):
        return self.y + self.h

    def overlaps(self, other):
        return (self.x < other.x + other.w and self.x + self.w > other.x
                and self.y < other.bottom and self.bottom > other.y)

def horizontal_overlap(x, width, surface):
    return x < surface.x + surface.w and x + width > surface.x
