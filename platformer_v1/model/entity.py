from dataclasses import dataclass

from model.base import Orientation


@dataclass
class Collision2:
    distance: float = 0
    orientation: Orientation = Orientation.HORIZONTAL


@dataclass
class Collision2X(Collision2):
    x_at_target: int = 0

# TODO: this is useless! get rid
@dataclass
class Collision2Y(Collision2):
    y_at_target: int = 0
