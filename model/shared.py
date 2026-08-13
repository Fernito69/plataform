from enum import StrEnum, auto

Number = int | float

Vector2 = tuple[Number, Number]
Coord2 = Vector2

# Vector3 = tuple[Number, Number, Number]
# TODO: make the above work
Vector3 = list[Number] 
Coord3 = tuple[Number, Number, Number]


# TODO: unify this for 3D too
class Orientation(StrEnum):
    HORIZONTAL = auto()
    VERTICAL = auto()
