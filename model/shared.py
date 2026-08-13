from enum import StrEnum, auto

Number = int | float

Vector = tuple[Number, Number]
Coord = Vector


class Direction(StrEnum):
    HORIZONTAL = auto()
    VERTICAL = auto()
