class Hazard:
    """Minimal contract: update, hitbox and draw. Game only uses this contract."""
    alive = True

    def update(self, platforms):
        raise NotImplementedError

    @property
    def hitbox(self):
        raise NotImplementedError

    def draw(self, renderer):
        raise NotImplementedError
