from dataclasses import dataclass

from model.base import PointF
from model.theme import RGB


@dataclass
class RenderInfo:
    point: PointF
    distance_to_pixel_center: float
    color: RGB


@dataclass
class BoundingBox:
    """World-space rectangle a shape can draw inside."""

    min_x: float
    min_y: float
    max_x: float
    max_y: float

    def union(self, other: "BoundingBox") -> "BoundingBox":
        return BoundingBox(
            min(self.min_x, other.min_x),
            min(self.min_y, other.min_y),
            max(self.max_x, other.max_x),
            max(self.max_y, other.max_y),
        )

    def overlaps(self, other: "BoundingBox") -> bool:
        return (
            self.min_x <= other.max_x
            and self.max_x >= other.min_x
            and self.min_y <= other.max_y
            and self.max_y >= other.min_y
        )
