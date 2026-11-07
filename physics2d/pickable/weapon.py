from typing import TYPE_CHECKING

from model.base import PointF
from model.theme import RGB, Theme
from physics2d.constants import (
    HEAVY_ROCKET_LAUNCHER_COLOR,
    HOMING_MISSILE_LAUNCHER_COLOR,
    MICROMISSILES_LAUNCHER_COLOR,
    ROCKET_LAUNCHER_COLOR,
    SHOTGUN_COLOR,
)
from physics2d.entities.equipment.weapons.homing_missile_launcher import HomingMissileLauncher
from physics2d.entities.equipment.weapons.rocket_launcher import (
    HeavyRocketLauncher,
    MicroMissileLauncher,
    RocketLauncher,
)
from physics2d.entities.equipment.weapons.shotgun import Shotgun
from physics2d.pickable.base import Pickable
from physics2d.shape.factories.text import Text
from physics2d.shape.particle.circular_particle import CircularParticle
from utils import random_offset

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.entities.model.shared import ParticleGenerator
    from physics2d.physics2d import Physics2D
    from physics2d.shape.base import Shape


def _get_text(
    engine: "Physics2D",
    position: PointF,
    color: RGB,
) -> Text:
    return Text(
        engine=engine,
        position=position,
        text_color=color.get_gradient(RGB(255, 255, 255)),
        scale_factor=1,
        thickness=0.7,
        pulsate_freq=0.5,
        pulsate_amplitude=0.3,
        # initial_velocity=PointF(0.1, 0.12121221).as_vector(),
    )


def _weapon_pickup_flame(color: RGB) -> "ParticleGenerator":
    def _w(engine: "Physics2D", source: "PhysicsEntity") -> None:
        pieces: list[Shape] = []

        for _ in range(3):
            # little particles doing particle stuff
            sonic_challa = CircularParticle(
                origin=(source.center),
                size=(0.8 + random_offset()),
                initial_color=color,
                ending_color=color.copy(opacity=0.1),
                life_time=10,
                floating_multi=1,
                engine=engine,
            )
            pieces.append(sonic_challa)

        engine.scenario.bg_shapes[0:0] = pieces

    return _w


#################


class ShotgunPickup(Pickable):
    def __init__(
        self,
        engine: "Physics2D",
        position: PointF,
    ) -> None:
        text = _get_text(engine, position, SHOTGUN_COLOR)

        super().__init__(
            engine,
            theme=Theme(SHOTGUN_COLOR),
            secondary_theme=Theme(0.1 * SHOTGUN_COLOR),
            color_gradient_exponent_end=0,
            color_gradient_exponent=1,
            size=10,
            position=position,
            particle_generator=_weapon_pickup_flame(SHOTGUN_COLOR),
            extra_shapes=text.generate("s"),
        )

    def _grant_player_something(self) -> None:
        self.engine.player.grant_weapon(Shotgun(self.engine))


#############################################################


class HeavyRocketLauncherPickup(Pickable):
    def __init__(
        self,
        engine: "Physics2D",
        position: PointF,
    ) -> None:
        text = _get_text(engine, position, HEAVY_ROCKET_LAUNCHER_COLOR)

        super().__init__(
            engine,
            theme=Theme(HEAVY_ROCKET_LAUNCHER_COLOR),
            secondary_theme=Theme(0.1 * HEAVY_ROCKET_LAUNCHER_COLOR),
            color_gradient_exponent_end=0,
            color_gradient_exponent=1,
            size=10,
            position=position,
            particle_generator=_weapon_pickup_flame(HEAVY_ROCKET_LAUNCHER_COLOR),
            extra_shapes=text.generate("H"),
        )

    def _grant_player_something(self) -> None:
        self.engine.player.grant_weapon(RocketLauncher(self.engine))


#############################################################


class MicroMissilesLauncherPickup(Pickable):
    def __init__(
        self,
        engine: "Physics2D",
        position: PointF,
    ) -> None:
        text = _get_text(engine, position, MICROMISSILES_LAUNCHER_COLOR)

        super().__init__(
            engine,
            theme=Theme(MICROMISSILES_LAUNCHER_COLOR),
            secondary_theme=Theme(0.1 * MICROMISSILES_LAUNCHER_COLOR),
            color_gradient_exponent_end=0,
            color_gradient_exponent=1,
            size=10,
            position=position,
            particle_generator=_weapon_pickup_flame(MICROMISSILES_LAUNCHER_COLOR),
            extra_shapes=text.generate("m"),
        )

    def _grant_player_something(self) -> None:
        self.engine.player.grant_weapon(HeavyRocketLauncher(self.engine))


#############################################################


class HomingMissilesLauncherPickup(Pickable):
    def __init__(
        self,
        engine: "Physics2D",
        position: PointF,
    ) -> None:
        text = _get_text(engine, position, HOMING_MISSILE_LAUNCHER_COLOR)

        super().__init__(
            engine,
            theme=Theme(HOMING_MISSILE_LAUNCHER_COLOR),
            secondary_theme=Theme(0.1 * HOMING_MISSILE_LAUNCHER_COLOR),
            color_gradient_exponent_end=0,
            color_gradient_exponent=1,
            size=10,
            position=position,
            particle_generator=_weapon_pickup_flame(HOMING_MISSILE_LAUNCHER_COLOR),
            extra_shapes=text.generate("h"),
        )

    def _grant_player_something(self) -> None:
        self.engine.player.grant_weapon(MicroMissileLauncher(self.engine))


#############################################################


class RocketLauncherPickup(Pickable):
    def __init__(
        self,
        engine: "Physics2D",
        position: PointF,
    ) -> None:
        text = _get_text(engine, position, ROCKET_LAUNCHER_COLOR)

        super().__init__(
            engine,
            theme=Theme(ROCKET_LAUNCHER_COLOR),
            secondary_theme=Theme(0.1 * ROCKET_LAUNCHER_COLOR),
            color_gradient_exponent_end=0,
            color_gradient_exponent=1,
            size=10,
            position=position,
            particle_generator=_weapon_pickup_flame(ROCKET_LAUNCHER_COLOR),
            extra_shapes=text.generate("r"),
        )

    def _grant_player_something(self) -> None:
        self.engine.player.grant_weapon(HomingMissileLauncher(self.engine))
