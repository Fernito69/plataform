from typing import TYPE_CHECKING

from model.theme import RGB
from physics2d.entities.equipment.weapon import Weapon
from physics2d.shapes.factories.projectile import get_lightning_bolts
from physics2d.shapes.particle import LineParticle

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.scenario.scenario import Scenario


class DeathRay(Weapon):
    def __init__(
        self,
        scenario: "Scenario",
    ):
        _START_COLOR = RGB(255, 220, 200, 1)
        _END_COLOR = RGB(0, 0, 100, 1)
        _DAMAGE = 3
        _DAMAGE_RANGE = 50

        super().__init__(
            name="DeathRay",
            scenario=scenario,
            max_ammo=30,
            refractory_period=30,
            fire_particle_generator=lightning_nozzle,
            projectile_generator=ray,
            ammo=30,
            color=RGB(255, 255, 50, 1),
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
        default_tendril_length=15,
        num_tendrils=2,
        life_time=8,
        num_segments=5,
    )
    _lightning(scenario, source)


################


#################################################################
"""RAY"""
#################################################################


# TODO: ideally should be aware of what we are shooting at
# TODO: make it like a non-targeted lightning weapon beam but less intense
def ray(scenario: "Scenario", source: "PhysicsEntity") -> None:
    _ending_color= RGB(255, 255, 200, 1)
    _initial_color  = RGB(255, 255, 10, 1)

    line = LineParticle(
        source=source,
        end_point=scenario.player.engine.screen_corner + scenario.crosshair.position,
        initial_color=_initial_color,
        ending_color=_ending_color,
        life_time=10,
        thickness=2,
        pulsate_amplitude=2,
        pulsate_freq=10
    )

    scenario.fg_pieces.append(line)


################
