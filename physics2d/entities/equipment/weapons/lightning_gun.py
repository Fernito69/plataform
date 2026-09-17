from typing import TYPE_CHECKING

from model.theme import RGB
from physics2d.entities.equipment.weapon import Weapon
from physics2d.shape.factories.projectile import get_lightning_bolts

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.scenario.scenario import Scenario


class LightningGun(Weapon):
    def __init__(
        self,
        scenario: "Scenario",
    ):
        _START_COLOR = RGB(255, 220, 200, 1)
        _END_COLOR = RGB(0, 0, 100, 1)
        _DAMAGE = 3
        _DAMAGE_RANGE = 50

        super().__init__(
            name="LightningGun",
            scenario=scenario,
            max_ammo=2000,
            refractory_period=0,
            fire_particle_generator=lightning_nozzle,
            projectile_generator=get_lightning_bolts(
                _START_COLOR,
                _END_COLOR,
                _DAMAGE,
                _DAMAGE_RANGE,
            ),
            ammo=2000,
            color=RGB(255, 190, 255, 1),
        )

    def _spend_ammo(self) -> None:
        self._ammo -= 1

    def _effect_on_player(self) -> None: ...

    def secondary_fire(self) -> None: ...


#################################################################
"""NOZZLE"""
#################################################################


# TODO: ideally should be aware of what we are shooting at
# TODO: make it like a non-targeted lightning weapon beam but less intense
def lightning_nozzle(scenario: "Scenario", source: "PhysicsEntity") -> None:
    # _initial_color = RGB(
    #     0 + (vel_magnitude * random()) * 80, 255 - (vel_magnitude * random()) * 10, 200, 1
    # )
    _initial_color = RGB(255, 220, 200, 1)
    _ending_color = RGB(0, 0, 100, 1)

    _lightning = get_lightning_bolts(
        _initial_color,
        _ending_color,
        damage=None,
        default_tendril_length=20,
        num_tendrils=2,
        life_time=8,
        num_segments=5,
    )
    _lightning(scenario, source)

    """
    _initial_color = RGB(255 - ((8) * random()), 255, 255, 1)

    sonic_boom_2 = CircularParticle(
        origin=(source.center - 0.2 * source.velocity)
        - VectorF(x=random_offset(), y=random_offset()),
        initial_velocity=(-0.4 * (source.velocity + VectorF.random_offset_vector())).as_vector(),
        size=source.radius * 0.8,
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=_initial_color,
        ending_color=RGB(200, 200, 255, 1),
        ending_color_fade_type=TransitionType.LINEAR_DECREASE,
        life_time=5,
        floating_multi=1,
    )
    pieces.append(sonic_boom_2)

    # MAIN BOOM
    sonic_boom = CircularParticle(
        origin=(source.center) - VectorF(x=random_offset(), y=random_offset()),
        initial_velocity=(1 * (source.velocity + VectorF.random_offset_vector())).as_vector(),
        size=source.radius * 1,
        size_change_type=TransitionType.EXPONENTIAL_DECREASE,
        initial_color=_initial_color,
        ending_color=RGB(127, 0, 255, 1),
        ending_color_fade_type=TransitionType.LINEAR_DECREASE,
        life_time=25,
        floating_multi=1,
    )
    pieces.append(sonic_boom)

    for _ in range(3):
        # little particles doing particle stuff
        sonic_challa = CircularParticle(
            origin=(source.center - source.velocity)
            - VectorF(x=random_offset(), y=random_offset()),
            initial_velocity=(
                1
                * VectorF(
                    x=source.velocity.x + random_offset(), y=source.velocity.y + random_offset()
                )
            ).as_vector(),
            size=(0.8 + random_offset()),
            size_change_type=TransitionType.EXPONENTIAL_DECREASE,
            initial_color=_initial_color,
            ending_color=RGB(127, 0, 255, 1),
            ending_color_fade_type=TransitionType.LINEAR_DECREASE,
            life_time=15,
            floating_multi=6,
        )
        pieces.append(sonic_challa)

    scenario.bg_pieces[0:0] = pieces
    """


################
