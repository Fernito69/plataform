from dataclasses import dataclass

from model.base import PointF
from model.theme import RGB


@dataclass
class RenderInfo:
    point: PointF
    distance_to_pixel_center: float
    color: RGB
