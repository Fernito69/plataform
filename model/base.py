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


# TODO: refactor using these vectors:
@dataclass
class VectorF:
    x: float
    y: float
    z: float | None = None

    def __neg__(self) -> "VectorF":
        return VectorF(x=-self.x, y=-self.y, z=-self.z if self.z else None)

    def __add__(self, other: "VectorF") -> "VectorF":
        return VectorF(
            x=self.x + other.x,
            y=self.y + other.y,
            z=(self.z + other.z if self.z is not None and other.z is not None else None),
        )

    def __sub__(self, other: "VectorF") -> "VectorF":
        return VectorF(
            x=self.x - other.x,
            y=self.y - other.y,
            z=(self.z - other.z if self.z is not None and other.z is not None else None),
        )

    def __mul__(self, scalar: float) -> "VectorF":
        return VectorF(
            self.x * scalar,
            self.y * scalar,
            None if self.z is None else self.z * scalar,
        )

    def __rmul__(self, scalar: float) -> "VectorF":
        return self * scalar

    def __abs__(self) -> float:
        """get magnitude"""
        return (self.x**2 + self.y**2 + (self.z**2 if self.z else 0)) ** 0.5


class PointF(VectorF): ...
