from model.base import PointF, VectorF
from model.theme import RGB
from physics2d.shapes.model.shared import TransitionType
from physics2d.shapes.particle import CircularParticle


class Projectile(CircularParticle):
    def __init__(
        self,
        origin: PointF,
        size: float,
        initial_color: RGB,
        initial_velocity: VectorF = VectorF(0, 0),
        gravity: float | None = None,
        ending_color: RGB | None = None,
        life_time: int | None = None,
        size_change_type: TransitionType = TransitionType.NONE,
        ending_color_fade_type: TransitionType = TransitionType.LINEAR_DECREASE,
        floating_multi: float = 0,
    ):
        super().__init__(
            origin,
            size,
            initial_color,
            initial_velocity,
            gravity,
            ending_color,
            life_time,
            size_change_type,
            ending_color_fade_type,
            floating_multi,
        )
