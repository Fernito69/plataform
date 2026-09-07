from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.shapes.circunference import Circunference
from physics2d.shapes.model.shared import TransitionType

# TODO: move to model


class Particle(Circunference):
    origin: PointF
    initial_color: RGB

    ending_color: RGB | None
    ending_color_fade_type: TransitionType

    # numbers of "game ticks" that they will survive (None means they don't die out)
    life_time: int | None
    _original_life_time: int | None

    size_decrease_type: TransitionType

    def __init__(
        self,
        origin: PointF,
        size: float,
        initial_color: RGB,
        initial_velocity: VectorF = VectorF(0, 0),
        gravity: float | None = None,
        ending_color: RGB | None = None,
        life_time: int | None = None,
        size_decrease_type: TransitionType = TransitionType.NONE,
        ending_color_fade_type: TransitionType = TransitionType.NONE,
    ):
        self.life_time = life_time
        self._original_life_time = life_time
        self.initial_color = initial_color
        self.ending_color = ending_color
        self.ending_color_fade_type = ending_color_fade_type
        self.size_decrease_type = size_decrease_type

        super().__init__(
            theme=Theme(color=initial_color),
            secondary_theme=Theme(color=ending_color),
            center=origin,
            radius=size,
            initial_velocity=initial_velocity,
            own_gravity=gravity,
            affected_by_gravity=gravity is not None,
        )

    def do_your_thing(self, engine) -> None:
        self._apply_movement(engine)
        self._handle_lifetime()

    def _handle_lifetime(self) -> None:
        if self.life_time is None or self._original_life_time is None:
            return
        self.life_time -= 1

        match self.size_decrease_type:
            case TransitionType.LINEAR:
                self.radius -= self.radius / (self.life_time + 1)
            case TransitionType.NONE:
                ...

        if self.ending_color and self.theme.color:
            # TODO: these are ending_colors for the factories
            # _smoke_like = RGB(100, 100, 100, intensity=0.1)
            # _ice_like = RGB(177, 255, 255).with_intensity(
            #     self.life_time / (self._original_life_time or 1)
            # )

            color_to_mix = self.ending_color

            match self.ending_color_fade_type:
                case TransitionType.LINEAR:
                    color_to_mix = self.ending_color.with_intensity(
                        self.life_time / (self._original_life_time or 1)
                    )
                case TransitionType.NONE:
                    ...

            self.theme.color = self.theme.color.mix_with([self.theme.color, color_to_mix])
