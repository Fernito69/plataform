from dataclasses import dataclass

from model.shared import Direction, Number


@dataclass
class Collision:
    x_at_target: int | None = None
    y_at_target: int | None = None
    distance: Number = 0
    direction: Direction = Direction.HORIZONTAL


@dataclass
class CollisionX(Collision):
    x_at_target: int = 0


@dataclass
class CollisionY(Collision):
    y_at_target: int = 0
