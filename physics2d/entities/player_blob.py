from model.base import Point2F
from model.theme import RGB, Theme
from physics2d.entities.base import Entity
from physics2d.model.shapes import Circunference

_PLAYER_RADIUS = 2
_PLAYER_THEME = Theme(color=RGB(0, 255, 0))


class PlayerBlob(Entity, Circunference):
    def __init__(self, position: Point2F):
        Entity().__init__(name="Player", position=position)
        Circunference.__init__(self, theme=_PLAYER_THEME, center=position, radius=_PLAYER_RADIUS)
