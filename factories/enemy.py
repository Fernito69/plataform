from constants import Color
from entities.enemy import Enemy
from model.enemy import EnemyType

_DEFAULT_DUMB_BOUNCING_ENEMY_CHARACTER_FRAMES = ["@"]
_DEFAULT_DUMB_BOUNCING_ENEMY_CHARACTER_COLOR = "blue"


def DumbBouncingEnemy(
    position: tuple[int, int],
    movement_type: tuple[int | float, int | float],
    speed: int = 1,
    character_frames: list[str] = _DEFAULT_DUMB_BOUNCING_ENEMY_CHARACTER_FRAMES,
    color: Color = _DEFAULT_DUMB_BOUNCING_ENEMY_CHARACTER_COLOR,
    health: int = 40,
) -> Enemy:
    return Enemy(
        EnemyType.DUMB_BOUNCING,
        speed=speed,
        movement_type=movement_type,
        position=position,
        character_frames=character_frames,
        color=color,
        health=health,
    )


_DEFAULT_DUMB_FLOATING_ENEMY_CHARACTER_FRAMES = ["·", "-", "+", "x", "┼", "X", "o", "·"]
_DEFAULT_DUMB_FLOATING_ENEMY_CHARACTER_COLOR = "red"


def DumbFloatingEnemy(
    position: tuple[int, int],
    movement_type: tuple[int, int],
    speed: int = 1,
    character_frames: list[str] = _DEFAULT_DUMB_FLOATING_ENEMY_CHARACTER_FRAMES,
    color: Color = _DEFAULT_DUMB_FLOATING_ENEMY_CHARACTER_COLOR,
    health: int = 50,
) -> Enemy:
    return Enemy(
        EnemyType.DUMB_FLOATING,
        speed=speed,
        movement_type=movement_type,
        position=position,
        character_frames=character_frames,
        color=color,
        health=health,
    )


_DEFAULT_FIRE_FLOATING_ENEMY_CHARACTER_COLOR = "yellow"
_DEFAULT_FIRE_FLOATING_ENEMY_CHARACTER_FRAMES = [
    "█",
    "▓",
    "▓",
    "▒",
    "▓",
    "▒",
    "░",
    "░",
    " ",
    "░",
    "▒",
    "▒",
    "▒",
    "▓",
    "▓",
    "█",
]


def DumbFireFloatingEnemy(
    position: tuple[int, int],
    movement_type: tuple[int, int],
    character_frames: list[str] = _DEFAULT_FIRE_FLOATING_ENEMY_CHARACTER_FRAMES,
    color: Color = _DEFAULT_FIRE_FLOATING_ENEMY_CHARACTER_COLOR,
    health: int = 60,
    speed: int = 4,
) -> Enemy:
    return DumbFloatingEnemy(
        speed=speed,
        movement_type=movement_type,
        position=position,
        character_frames=character_frames,
        color=color,
        health=health,
    )


_ROTATING_FLOATING_ENEMY_CHARACTER_FRAMES = ["|", "/", "-", "\\"]
