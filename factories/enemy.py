from entities.enemy import Enemy
from factories.theme import Blue, Red, Yellow
from model.enemy import EnemyType
from model.shared import Coord, Vector
from model.theme import RGB, Theme

_DEFAULT_DUMB_BOUNCING_ENEMY_CHARACTER_FRAMES = ["@"]
_DEFAULT_DUMB_BOUNCING_ENEMY_CHARACTER_COLOR = Blue()


def DumbBouncingEnemy(
    position: Coord,
    movement_type: Vector,
    speed: int = 1,
    health: int = 40,
    character_frames: list[str] = _DEFAULT_DUMB_BOUNCING_ENEMY_CHARACTER_FRAMES,
    color: RGB = _DEFAULT_DUMB_BOUNCING_ENEMY_CHARACTER_COLOR,
    bg_color: RGB | None = None,
) -> Enemy:
    return Enemy(
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
    position: Coord,
    movement_type: Vector,
    speed: int = 1,
    health: int = 50,
    character_frames: list[str] = _DEFAULT_DUMB_FLOATING_ENEMY_CHARACTER_FRAMES,
    color: RGB = _DEFAULT_DUMB_FLOATING_ENEMY_CHARACTER_COLOR,
    bg_color: RGB | None = None,
) -> Enemy:
    return Enemy(
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
    position: Coord,
    movement_type: Vector,
    health: int = 60,
    speed: int = 4,
    character_frames: list[str] = _DEFAULT_FIRE_FLOATING_ENEMY_CHARACTER_FRAMES,
    color: RGB = _DEFAULT_FIRE_FLOATING_ENEMY_CHARACTER_COLOR,
    bg_color: RGB | None = None,
) -> Enemy:
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
