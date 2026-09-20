from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.physics2d import Physics2D


def is_out_of_sight(engine: "Physics2D", entity: "PhysicsEntity", grace_margin: int = 20):
    X_RES, Y_RES = engine.get_resolution()

    # curr visible rectangle
    x_min = engine.screen_corner.x - grace_margin
    x_max = engine.screen_corner.x + X_RES + grace_margin
    y_min = engine.screen_corner.y - grace_margin
    y_max = engine.screen_corner.y + Y_RES + grace_margin

    return (
        entity.position.x + entity.radius < x_min
        or entity.position.x - entity.radius > x_max
        or entity.position.y + entity.radius < y_min
        or entity.position.y - entity.radius > y_max
    )
