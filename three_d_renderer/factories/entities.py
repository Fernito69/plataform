from dataclasses import dataclass

from model.shared import Number


@dataclass
class Collision3:
    distance: Number = 0
