from typing import TYPE_CHECKING

from model.theme import RGB
from physics2d.entities.equipment.weapon import Weapon
from physics2d.shape.factories.projectile import get_lightning_bolts
from physics2d.shape.particle.lightning import Lightning

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.scenario.scenario import Scenario


class Zapper(Weapon):
    def __init__(
        self,
        scenario: "Scenario",
    ):
        super().__init__(
            name="Zapper",
            scenario=scenario,
            max_ammo=50,
            refractory_period=15,
            fire_particle_generator=lightning_nozzle,
            projectile_generator=zapper_bolt,
            ammo=50,
            color=RGB(100, 190, 255, 1),
        )

    def _spend_ammo(self) -> None:
        self._ammo -= 1

    def secondary_fire(self) -> None: ...


#################################################################
"""NOZZLE"""
#################################################################


def lightning_nozzle(scenario: "Scenario", source: "PhysicsEntity") -> None:
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


#################################################################
"""PROJECTILE"""
#################################################################


def zapper_bolt(scenario: "Scenario", source: "PhysicsEntity") -> None:
    from physics2d.entities.player_blob import PlayerBlob

    _DAMAGE = 500
    _LIFE_TIME = 7
    _SEGMENT_LENGTH = 4
    _NUM_SECONDARY_RAYS = 2

    _START_COLOR = RGB(180, 180, 255, 1)
    _END_COLOR = RGB(0, 0, 100, 1)

    # TODO: this doesn't work?
    start_point = source.get_weapon_position() if isinstance(source, PlayerBlob) else None
    # TODO: implement a method to get this more easily
    end_point = scenario.crosshair.center + scenario.engine.screen_corner
    num_segments = round(max(4, abs(source.center - end_point) / _SEGMENT_LENGTH))

    target: "PhysicsEntity | None" = next(
        (a for a in scenario.enemies if abs(a.position - end_point) < a.radius), None
    )
    if target:
        target.receive_damage(_DAMAGE)
    _life_time = round(_LIFE_TIME * (1.5 if target else 1))
    main_l = Lightning(
        source=source,
        start_point=start_point,
        end_point=end_point,
        initial_color=_START_COLOR,
        ending_color=_END_COLOR,
        normal_noise=2,
        parallel_noise=3,
        life_time=_life_time,
        num_segments=num_segments,
        thickness=1.5,
        final_thickness=0.5,
        render_behind_player=True,
        target=target,
    )
    scenario.fg_shapes.append(main_l)

    for index in range(_NUM_SECONDARY_RAYS):
        # TODO: horrible, do it well
        _color = RGB(255, 100, 100, 1) if index == 0 else RGB(100, 255, 100, 1)
        _ending_color = _color.with_intensity(0.3)
        sec_l = Lightning(
            source=source,
            start_point=start_point,
            end_point=end_point,
            initial_color=_color,
            ending_color=_ending_color,
            normal_noise=8,
            parallel_noise=8,
            life_time=_life_time,
            num_segments=num_segments,
            thickness=0.7,
            final_thickness=0.01,
            render_behind_player=True,
            target=target,
        )
        scenario.fg_shapes.append(sec_l)
