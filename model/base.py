from dataclasses import dataclass
from enum import StrEnum, auto

type Tuple2[T: int | float] = tuple[T, T]

type Vector2F = Tuple2[float]
type Vector2I = Tuple2[int]
type Point2F = Tuple2[float]
type Point2I = Tuple2[int]

type Tuple3[T: int | float] = tuple[T, T, T]

type Vector3F = Tuple3[float]
type Point3F = Tuple3[float]


@dataclass
class DistCoordBase:
    distance: float


@dataclass
class DistVector2D(DistCoordBase):
    vector: Vector2F


@dataclass
class DistVector3D(DistCoordBase):
    vector: Vector3F
    distance_to_edge: float | None = None


# TODO: unify this for 3D too
class Orientation(StrEnum):
    HORIZONTAL = auto()
    VERTICAL = auto()
