"""All gameplay tuning. Speeds are pixels per fixed 1/FPS tick."""
from dataclasses import dataclass

WIDTH, HEIGHT, FPS = 256, 144, 30
STAGE_WIDTH, GROUND_Y = 1152, 124
PLAYER_START_X = 36
PLAYER_SIZE = 16
PLAYER_SPEED, GRAVITY, JUMP_SPEED, MAX_FALL_SPEED = 2.0, 0.32, -4.8, 6.0
HITBOX_X, HITBOX_Y, HITBOX_W, HITBOX_H = 1, 6, 14, 9
ANIMATION_TICKS = 5
MAX_HP, INVINCIBLE_TICKS, BLINK_TICKS = 3, FPS, 3
WAVE_SECONDS, INTERVAL_SECONDS = 30, 3
SURVIVAL_POINTS, CLEAR_POINTS, NO_DAMAGE_POINTS = 10, 500, 500
POOP_SIZE, POOP_START_Y, SPLASH_TICKS = 7, -8, 7
PIERCING_OBJECT_BIAS = 0.70
TRANSPARENT_COLOR = 15
PALETTE = [0x181C28, 0x283449, 0x65443D, 0x28745B,
           0xAC7551, 0x647C85, 0xB5C2C1, 0xFFF1D2,
           0xF06B65, 0xEDAD64, 0xF8DC88, 0xA5CF72,
           0x82B5BD, 0x8798BD, 0xD4B591, 0xFF00FF]

@dataclass(frozen=True)
class WaveConfig:
    poop_spawn_interval: int
    poop_min_speed: float
    poop_max_speed: float
    max_poops: int
    piercing_chance: float = 0.0

WAVES = (
    WaveConfig(9, 1.0, 1.7, 45),
    WaveConfig(7, 1.3, 2.1, 55, 0.15),
    WaveConfig(5, 1.6, 2.6, 65, 0.20),
    WaveConfig(4, 1.9, 3.1, 75, 0.25),
    WaveConfig(3, 2.2, 3.7, 90, 0.30),
)
