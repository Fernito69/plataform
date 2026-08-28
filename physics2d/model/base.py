from dataclasses import dataclass

from model.base import Point2F
from model.theme import RGB


@dataclass
class RenderInfo:
    point: Point2F
    distance_to_pixel_center: float
    color: RGB
