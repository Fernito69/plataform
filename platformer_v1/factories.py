from factories.theme import Blue, Red, Yellow
from model.base import Point2, Vector2
from model.enemy import EnemyType
from model.theme import RGB, Theme
from platformer_v1.entities.enemy2d import Enemy2D

_DEFAULT_DUMB_BOUNCING_ENEMY_CHARACTER_FRAMES = ["@"]
_DEFAULT_DUMB_BOUNCING_ENEMY_CHARACTER_COLOR = Blue()


def DumbBouncingEnemy(
    position: Point2,
    movement_type: Vector2,
    speed: int = 1,
    health: int = 40,
    character_frames: list[str] = _DEFAULT_DUMB_BOUNCING_ENEMY_CHARACTER_FRAMES,
    color: RGB = _DEFAULT_DUMB_BOUNCING_ENEMY_CHARACTER_COLOR,
    bg_color: RGB | None = None,
) -> Enemy2D:
    return Enemy2D(
        EnemyType.DUMB_BOUNCING,
        speed=speed,
        movement_type=movement_type,
        position=position,
        character_frames=character_frames,
        theme=Theme(color=color, bg_color=bg_color),
        health=health,
    )


_DEFAULT_DUMB_FLOATING_ENEMY_CHARACTER_FRAMES = ["·", "-", "+", "x", "┼", "X", "o", "·"]
_DEFAULT_DUMB_FLOATING_ENEMY_CHARACTER_COLOR = Red()


def DumbFloatingEnemy(
    position: Point2,
    movement_type: Vector2,
    speed: int = 1,
    health: int = 50,
    character_frames: list[str] = _DEFAULT_DUMB_FLOATING_ENEMY_CHARACTER_FRAMES,
    color: RGB = _DEFAULT_DUMB_FLOATING_ENEMY_CHARACTER_COLOR,
    bg_color: RGB | None = None,
) -> Enemy2D:
    return Enemy2D(
        EnemyType.DUMB_FLOATING,
        speed=speed,
        movement_type=movement_type,
        position=position,
        character_frames=character_frames,
        theme=Theme(color=color, bg_color=bg_color),
        health=health,
    )


_DEFAULT_FIRE_FLOATING_ENEMY_CHARACTER_COLOR = Yellow()
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
    position: Point2,
    movement_type: Vector2,
    health: int = 60,
    speed: int = 4,
    character_frames: list[str] = _DEFAULT_FIRE_FLOATING_ENEMY_CHARACTER_FRAMES,
    color: RGB = _DEFAULT_FIRE_FLOATING_ENEMY_CHARACTER_COLOR,
    bg_color: RGB | None = None,
) -> Enemy2D:
    return DumbFloatingEnemy(
        speed=speed,
        movement_type=movement_type,
        position=position,
        character_frames=character_frames,
        color=color,
        bg_color=bg_color,
        health=health,
    )


_ROTATING_FLOATING_ENEMY_CHARACTER_FRAMES = ["|", "/", "-", "\\"]
