from dataclasses import dataclass

from model.base import Point2
from model.theme import RGB


@dataclass
class RenderInfo:
    point: Point2
    distance_to_pixel_center: float
    color: RGB
