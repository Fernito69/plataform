from typing import TYPE_CHECKING

from display import Display

if TYPE_CHECKING:
    from game import Game


class Physics2D:
    display: Display

    def __init__(
        self,
        game: "Game",
    ):
        self.game = game
        self.display = self.game.display
