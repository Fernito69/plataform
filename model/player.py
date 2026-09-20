from abc import abstractmethod
from enum import StrEnum, auto

from model.shared import KeyboardHandler, MouseHandler


class PlayerStatus(StrEnum):
    PLAYING = auto()
    DEAD = auto()
    END_LEVEL = auto()


class Player(KeyboardHandler, MouseHandler):
    status: PlayerStatus
    lives: int
    points: int
    player_number: int
    health: float

    _immune_counter: int = 0

    def __init__(
        self,
        lives: int,
        points: int,
        player_number: int,
        health: float,
    ):
        self.status = PlayerStatus.PLAYING
        self.lives = lives
        self.points = points
        self.player_number = player_number
        self.health = health

        KeyboardHandler.__init__(self)
        MouseHandler.__init__(self)

    @abstractmethod
    def do_your_thing(self) -> None: ...
