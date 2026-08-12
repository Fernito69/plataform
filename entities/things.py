from entities.entity import Entity
from model.theme import Theme

_EXIT_COLOR = "yellow"
_EXIT_BG_COLOR = "red"
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


class Exit(Entity):
    def __init__(self, position: tuple[int, int]):
        Entity.__init__(self)
        self.position = position
        self._character_frames = _EXIT_FRAMES
        self.theme = Theme(color=_EXIT_COLOR, bg_color=_EXIT_BG_COLOR)

    def do_your_thing(self):
        self.advance_character_frame()
