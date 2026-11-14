from dataclasses import dataclass

from model.base import PointF
from physics2d.entities.model.spawner import Spawner


@dataclass
class Milestone:
    game_tick: int
    events: list[Event]


@dataclass
class Event:
    spawner: Spawner
    positions: list[PointF]
