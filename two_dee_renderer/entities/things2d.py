from factories.theme import Red, Yellow
from model.base import Point2
from model.theme import Theme
from two_dee_renderer.entities.base import Entity2D

_EXIT_COLOR = Yellow()
_EXIT_BG_COLOR = Red()
_EXIT_FRAMES = [
    "E",
    "E",
    "E",
    "E",
    "X",
    "X",
    "X",
    "X",
    "I",
    "I",
    "I",
    "I",
    "T",
    "T",
    "T",
    "T",
]


class Exit2D(Entity2D):
    def __init__(self, position: Point2):
        Entity2D.__init__(self)
        self.position = position
        self._char_frames = _EXIT_FRAMES
        self.theme = Theme(color=_EXIT_COLOR, bg_color=_EXIT_BG_COLOR)

    def do_your_thing(self):
        self._advance_character_frame()
