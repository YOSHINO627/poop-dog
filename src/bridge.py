import json

class Bridge:
    """Only this adapter knows about the optional browser host."""
    def __init__(self):
        try:
            from js import window
            self.host = window.poopDog
        except ImportError:
            self.host = None

    @property
    def debug_enabled(self):
        return bool(self.host.debugEnabled) if self.host else False

    def load_best(self):
        return int(self.host.loadBest()) if self.host else 0

    def save_best(self, score):
        if self.host:
            self.host.saveBest(score)

    def load_custom_sprites(self):
        try:
            return json.loads(str(self.host.loadCustomSprites())) if self.host else {}
        except Exception:
            return {}

    def load_dog_choice(self):
        try:
            return int(self.host.loadDogChoice()) if self.host else 0
        except Exception:
            return 0

    def save_custom_sprite(self, index, rows):
        try:
            return bool(self.host.saveCustomSprite(index, json.dumps(rows))) if self.host else False
        except Exception:
            return False

    def input(self):
        return json.loads(str(self.host.pollInput())) if self.host else {}

    def sprite(self):
        value = self.host.takeSprite() if self.host else ''
        return json.loads(str(value)) if value else None

    def publish_sprite(self, rows):
        if self.host:
            self.host.setCurrentSprite(json.dumps(rows))

    def publish(self, game):
        if self.host:
            self.host.publish(json.dumps({
                'state': game.state.name, 'hp': game.hp,
                'selectedBreed': game.selected_breed,
                'score': game.score.score, 'best': game.score.best,
                'level': game.wave.level + 1, 'wave': game.wave.index + 1, 'time': game.wave.remaining,
            }))
