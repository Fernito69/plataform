from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum, auto

from constants import ALMOST_ZERO, PI

# TODO: remove if unused
type Tuple2[T: int | float] = tuple[T, T]
type Tuple3[T: int | float] = tuple[T, T, T]


@dataclass
class DistCoordBase:
    distance: float


# TODO: unify this for 3D too
class Orientation(StrEnum):
    HORIZONTAL = auto()
    VERTICAL = auto()


@dataclass
class PointF:
    x: float | int
    y: float | int
    z: float | int = 0

    def as_vector(self) -> "VectorF":
        return VectorF(x=self.x, y=self.y, z=self.z)

    def as_point(self) -> "PointF":
        return PointF(x=self.x, y=self.y, z=self.z)

    def rotate(self, angle_in_radians: float, rotation_axis: PointF | None = None) -> "PointF":
        rotation_axis = rotation_axis or self
        if angle_in_radians == 0:
            return self.as_vector()
        new_x = (
            (self.x - rotation_axis.x) * math.cos(angle_in_radians)
            - (self.y - rotation_axis.y) * math.sin(angle_in_radians)
            + rotation_axis.x
        )
        new_y = (
            (self.x - rotation_axis.x) * math.sin(angle_in_radians)
            + (self.y - rotation_axis.y) * math.cos(angle_in_radians)
            + rotation_axis.y
        )
        return PointF(new_x, new_y)

    def __str__(self) -> str:
        DECIMALS = 1
        return f"({round(self.x, DECIMALS)},{round(self.y, DECIMALS)}{f',{round(self.z, DECIMALS)}' if self.z else ''})"

    def __neg__(self) -> "PointF":
        return PointF(x=-self.x, y=-self.y, z=-self.z)

    def __add__(self, other: "PointF | VectorF") -> "PointF":
        return PointF(
            x=self.x + other.x,
            y=self.y + other.y,
            z=self.z + other.z,
        )

    def __sub__(self, other: "PointF") -> "PointF":
        return PointF(
            x=self.x - other.x,
            y=self.y - other.y,
            z=self.z - other.z,
        )

    def __mul__(self, scalar: float) -> "PointF":
        return PointF(
            self.x * scalar,
            self.y * scalar,
            self.z * scalar,
        )

    def __rmul__(self, scalar: float) -> "PointF":
        return self * scalar

    def __len__(self) -> int:
        return 2 if not self.z else 3

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

    def __abs__(self) -> float:
        """Gets magnitude"""
        return (self.x**2 + self.y**2 + self.z**2) ** 0.5


@dataclass
class VectorF(PointF):
    def unit_vector(self) -> VectorF:
        magnitude = 1 / (abs(self) or ALMOST_ZERO)
        return (magnitude * self).as_vector()


@dataclass
class PointI(PointF):
    x: int
    y: int
    z: int | None = None


@dataclass
class VectorI(PointI): ...


@dataclass
class DistVector2D(DistCoordBase):
    vector: VectorF


@dataclass
class DistVector3D(DistCoordBase):
    vector: VectorF
    distance_to_edge: float | None = None


# TODO: refactor Physics2D angle with this
@dataclass
class Angle:
    # Always in radians
    value: float
    value_in_degrees: float

    _factor: float = PI / 180

    def __init__(self, value: float = 0):
        self.value = value
        self.value_in_degrees = value / self._factor

    def in_degrees(self) -> float:
        return self.value_in_degrees

    def in_radians(self) -> float:
        return self.value

    def __str__(self) -> str:
        return f"PI ({self.value / PI}); {self.value_in_degrees}º"

    def __neg__(self) -> Angle:
        return Angle(-self.value)

    def __add__(self, other: Angle | float) -> Angle:
        """If float, radians are always assumed"""
        return Angle(value=self.value + other if isinstance(other, float | int) else other.value)

    def __sub__(self, other: Angle | float) -> Angle:
        return Angle(value=self.value - other if isinstance(other, float | int) else other.value)

    def __mul__(self, scalar: float) -> Angle:
        return Angle(value=self.value * scalar)

    def __rmul__(self, scalar: float) -> Angle:
        return self * scalar

    def __iter__(self):
        yield self.value
        yield self.value_in_degrees
