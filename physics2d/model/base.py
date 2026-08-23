from dataclasses import dataclass

from model.base import Point2
from model.theme import RGB


@dataclass
class RenderInfo:
    point: Point2
    color: RGB
        
