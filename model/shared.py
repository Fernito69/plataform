from dataclasses import dataclass
from enum import StrEnum, auto

Number = int | float

Vector2 = tuple[Number, Number]
Point2 = Vector2

# Vector3 = tuple[Number, Number, Number]
# Point3 = tuple[Number, Number, Number]

# TODO: make the above work
Vector3 = list[Number]
Point3 = list[Number]


@dataclass
class DistCoordBase:
    distance: float


@dataclass
class DistVector2D(DistCoordBase):
    vector: Vector2


@dataclass
class DistVector3D(DistCoordBase):
    vector: Vector3
    distance_to_border: float | None = None


# TODO: unify this for 3D too
class Orientation(StrEnum):
    HORIZONTAL = auto()
    VERTICAL = auto()
