from abc import abstractmethod

from constants import ALMOST_ZERO
from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.model.shared import RenderInfo
from physics2d.shapes.circunference import Circunference
from physics2d.shapes.line import Line
from physics2d.shapes.model.shared import TransitionType
from utils import random_offset


class Particle:
    initial_color: RGB
    ending_color: RGB | None
    ending_color_fade_type: TransitionType

    # numbers of "game ticks" that they will survive (None means they don't die out)
    life_time: int | None
    _original_life_time: int | None

    size_change_type: TransitionType

    def __init__(
        self,
        initial_color: RGB,
        ending_color: RGB | None = None,
        initial_velocity: VectorF = VectorF(0, 0),
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
        self.initial_velocity = initial_velocity
        self.floating_multi = floating_multi

    # TODO: type this
    def do_your_thing(self, engine) -> None:
        self._act(engine)
        self._handle_lifetime()

    @abstractmethod
    def _act(cls, engine) -> None: ...

    @abstractmethod
    def _handle_lifetime(cls) -> None: ...


############################################################################################


class CircularParticle(Particle, Circunference):
    origin: PointF
    size: float

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
        self.theme = Theme(color=initial_color)
        self.secondary_theme = Theme(color=ending_color)
        self._own_gravity_accel = gravity
        self._affected_by_gravity = gravity is not None
        self.floating_multi = floating_multi
        self.velocity = initial_velocity
        self.radius = size
        self.center = origin

        super().__init__(
            initial_color=initial_color,
            ending_color=ending_color,
            ending_color_fade_type=ending_color_fade_type,
            life_time=life_time,
            size_change_type=size_change_type,
            floating_multi=floating_multi,
        )
        Circunference.__init__(
            self,
            theme=self.theme,
            secondary_theme=self.secondary_theme,
            affected_by_gravity=self._affected_by_gravity,
            own_gravity=gravity,
            floating_multi=floating_multi,
            initial_velocity=initial_velocity,
            radius=size,
            center=origin,
        )

    def _handle_lifetime(self) -> None:
        # basic stuff
        if self.life_time is None or self._original_life_time is None:
            return
        self.life_time -= 1

        # size changes
        match self.size_change_type:
            case TransitionType.LINEAR_DECREASE:
                self.radius -= self.radius / (self.life_time + 1)
            case TransitionType.EXPONENTIAL_DECREASE:
                self.radius *= self.life_time / self._original_life_time
            case TransitionType.LINEAR_INCREASE:
                self.radius += 1
            case TransitionType.NONE:
                ...

        # color changes
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
            # ending_factor = 1 - factor
            ending_factor = 1
            self.theme.color = RGB(
                r=self.initial_color.r * factor + self.ending_color.r * ending_factor,
                g=self.initial_color.g * factor + self.ending_color.g * ending_factor,
                b=self.initial_color.b * factor + self.ending_color.b * ending_factor,
            )

    def _act(self, engine) -> None:
        Circunference._apply_movement(self, engine)


#################################################################################################

# arbitrary value
_MIN_SEGMENT_LENGTH = 4


class Lightning(Particle, Line):
    points: tuple[PointF, PointF]
    segment_randomness: float
    point_randomness: float
    num_segments: int

    segments: list[Line]

    def __init__(
        self,
        point1: PointF,
        point2: PointF,
        life_time: int | None = 5,
        thickness: float = 1,
        segment_randomness: float = 2,
        point_randomness: float = 2,
        num_segments: int = 8,
        initial_color: RGB = RGB(255, 255, 255, 1),
        ending_color: RGB = RGB(0, 0, 0, 0),
        initial_velocity: VectorF = VectorF(0, 0),
        gravity: float | None = None,
        size_change_type: TransitionType = TransitionType.NONE,
        ending_color_fade_type: TransitionType = TransitionType.LINEAR_DECREASE,
        floating_multi: float = 0,
    ):
        self.points = (point1, point2)
        self.segment_randomness = segment_randomness
        self.point_randomness = point_randomness
        self.num_segments = num_segments
        self.initial_color = initial_color
        self.ending_color = ending_color
        self.life_time = life_time
        self._original_life_time = life_time
        self.initial_velocity = initial_velocity
        self.thickness = thickness

        super().__init__(
            initial_color=initial_color,
            ending_color=ending_color,
            ending_color_fade_type=ending_color_fade_type,
            life_time=life_time,
            size_change_type=size_change_type,
            floating_multi=floating_multi,
        )
        Line.__init__(
            self,
            points=self.points,
            own_gravity=gravity,
            initial_velocity=initial_velocity,
            theme=Theme(color=initial_color),
            secondary_theme=Theme(color=ending_color),
            thickness=thickness,
        )

        self.gen_lightning()

    def get_render_info(self) -> list[RenderInfo]:
        return [info for line in self.segments for info in line.get_render_info()]

    def gen_lightning(self) -> None:
        theme = Theme(color=self.initial_color)
        line_vector: VectorF = (self.points[0] - self.points[1]).as_vector()
        line_length = abs(line_vector)
        num_segments = min(self.num_segments, line_length / _MIN_SEGMENT_LENGTH)
        avg_segment_length = line_length / (num_segments or ALMOST_ZERO)

        division_lenghts = [
            max(
                0,
                min(
                    line_length,
                    num_seg * avg_segment_length + random_offset() * self.segment_randomness,
                ),
            )
            for num_seg in range(self.num_segments)
        ]

        def _rand_vector() -> VectorF:
            return VectorF(
                random_offset() * self.point_randomness, random_offset() * self.point_randomness
            )

        segment_points: list[PointF] = [
            self.points[0] + (x / (line_length or ALMOST_ZERO)) * line_vector + _rand_vector()
            for x in division_lenghts
        ]

        lines: list[Line] = (
            [
                Line(
                    points=(segment_points[0], self.points[0]),
                    thickness=self.thickness,
                    theme=theme,
                )
            ]
            + [
                Line(
                    points=(
                        p,
                        segment_points[idx + 1],
                    ),
                    thickness=self.thickness,
                    theme=theme,
                )
                for idx, p in enumerate(segment_points[:-1])
            ]
            + [
                Line(
                    points=(segment_points[-1], self.points[1]),
                    thickness=self.thickness,
                    theme=theme,
                )
            ]
        )

        self.segments = lines

    def _handle_lifetime(self) -> None:
        if self.life_time is None or self._original_life_time is None:
            return
        self.life_time -= 1

    def _act(self, _) -> None:
        self.gen_lightning()
