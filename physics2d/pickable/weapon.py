from typing import TYPE_CHECKING

from model.base import PointF
from model.theme import Theme
from physics2d.constants import SHOTGUN_COLOR
from physics2d.entities.equipment.thrusters.sonic_thruster import sonic_wave
from physics2d.entities.equipment.weapons.shotgun import Shotgun
from physics2d.pickable.base import Pickable

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


class ShotgunPickup(Pickable):
    def __init__(
        self,
        engine: "Physics2D",
        position: PointF,
    ) -> None:
        super().__init__(
            engine,
            theme=Theme(SHOTGUN_COLOR),
            secondary_theme=Theme(0.4 * SHOTGUN_COLOR),
            size=5,
            position=position,
            particle_generator=sonic_wave,
        )

    def _grant_player_something(self) -> None:
        self.engine.player.grant_weapon(Shotgun(self.engine))
