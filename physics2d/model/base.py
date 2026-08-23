from dataclasses import dataclass

from model.base import Point2
from model.theme import RGB


@dataclass
class RenderInfo:
    # TODO: should be already diggested distance
    point: Point2
    # in radians
    color: RGB
    angle: float = 0
