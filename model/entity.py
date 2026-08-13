from dataclasses import dataclass

from model.shared import Number, Orientation


@dataclass
class Collision:
    distance: Number = 0
    direction: Orientation = Orientation.HORIZONTAL


@dataclass
class CollisionX(Collision):
    x_at_target: int = 0


@dataclass
class CollisionY(Collision):
    y_at_target: int = 0
