from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.shapes.circunference import Circunference
from physics2d.shapes.model.shared import TransitionType


class Particle(Circunference):
    origin: PointF
    initial_color: RGB

    ending_color: RGB | None
    ending_color_fade_type: TransitionType

    # numbers of "game ticks" that they will survive (None means they don't die out)
    life_time: int | None
    _original_life_time: int | None

    size_change_type: TransitionType

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
        self.life_time = life_time
        self._original_life_time = life_time
        self.initial_color = initial_color
        self.ending_color = ending_color
        self.ending_color_fade_type = ending_color_fade_type
        self.size_change_type = size_change_type

        super().__init__(
            theme=Theme(color=initial_color),
            secondary_theme=Theme(color=ending_color),
            center=origin,
            radius=size,
            initial_velocity=initial_velocity,
            own_gravity=gravity,
            affected_by_gravity=gravity is not None,
            floating_multi=floating_multi,
        )

    def do_your_thing(self, engine) -> None:
        self._apply_movement(engine)
        self._handle_lifetime()

    def _handle_lifetime(self) -> None:
        if self.life_time is None or self._original_life_time is None:
            return
        self.life_time -= 1

        match self.size_change_type:
            case TransitionType.LINEAR_DECREASE:
                self.radius -= self.radius / (self.life_time + 1)
            case TransitionType.EXPONENTIAL_DECREASE:
                self.radius *= self.life_time / self._original_life_time
            case TransitionType.LINEAR_INCREASE:
                self.radius += 1
            case TransitionType.NONE:
                ...

        if (
            self.ending_color
            and self.theme.color
            and self.ending_color_fade_type != TransitionType.NONE
        ):
            factor = (
                self.life_time / self._original_life_time
                if self.ending_color_fade_type == TransitionType.LINEAR_DECREASE
                else 1 - self.life_time / self._original_life_time
            )
            self.theme.color = RGB(
                r=self.initial_color.r * factor + self.ending_color.r * (1 - factor),
                g=self.initial_color.g * factor + self.ending_color.g * (1 - factor),
                b=self.initial_color.b * factor + self.ending_color.b * (1 - factor),
            )
