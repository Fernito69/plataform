from model.base import PointF
from physics2d.entities.base import PhysicsEntity


# TODO: move to a more general place
def get_position(source: PhysicsEntity | PointF) -> PointF:
    return source if isinstance(source, PointF) else source.position
