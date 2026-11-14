from typing import TYPE_CHECKING

from model.base import PointF
from physics2d.entities.base import PhysicsEntity
from physics2d.entities.model.spawner import Spawner
from physics2d.entities.spawners.utils import get_position
from physics2d.pickable.weapon import RocketLauncherPickup, ShotgunPickup, WeaponPickup
from physics2d.shape.factories.effects import teleport_in_particles

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D

from physics2d.pickable.health import HealthPickup

# HEALTH


def health_spawner(amount: int) -> Spawner:
    def _s(engine: "Physics2D", source: PhysicsEntity | PointF) -> None:
        pickup = HealthPickup(
            engine=engine,
            position=get_position(source),
            amount=amount,
        )
        engine.scenario.pickables.append(pickup)
        teleport_in_particles(engine, pickup)

    return _s


# WEAPONS


def _get_weapon_spawner(
    Weapon: type["WeaponPickup"],
    engine: "Physics2D",
    source: PhysicsEntity | PointF,
) -> None:
    pickup = Weapon(engine=engine, position=get_position(source))
    engine.scenario.pickables.append(pickup)
    teleport_in_particles(engine, pickup)


def shotgun_pickup_spawner(engine: "Physics2D", source: PhysicsEntity | PointF) -> None:
    return _get_weapon_spawner(engine=engine, source=source, Weapon=ShotgunPickup)


def rocket_launcher_pickup_spawner(engine: "Physics2D", source: PhysicsEntity | PointF) -> None:
    return _get_weapon_spawner(engine=engine, source=source, Weapon=RocketLauncherPickup)
