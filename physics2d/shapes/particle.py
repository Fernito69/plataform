from abc import abstractmethod

from constants import ALMOST_ZERO
from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.model.shared import RenderInfo
from physics2d.shapes.circunference import Circunference
from physics2d.shapes.line import Line
from physics2d.shapes.model.shared import TransitionType
from utils import get_normal_unit_vector_from_line, random_offset, random_offset_vector


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
    parallel_noise: float
    normal_noise: float
    num_segments: int
    final_thickness: float | None

    source: Circunference

    segments: list[Line]

    def __init__(
        self,
        source: Circunference,
        end_point: PointF,
        start_point: PointF | None = None,
        life_time: int | None = 5,
        thickness: float = 1,
        parallel_noise: float = 2,
        normal_noise: float = 2,
        num_segments: int = 8,
        initial_color: RGB = RGB(255, 255, 255, 1),
        ending_color: RGB = RGB(0, 0, 0, 0),
        size_change_type: TransitionType = TransitionType.NONE,
        ending_color_fade_type: TransitionType = TransitionType.LINEAR_DECREASE,
        final_thickness: float | None = None,
    ):
        self.source = source
        self.points = (start_point or source.center, end_point)
        self.parallel_noise = parallel_noise
        self.normal_noise = normal_noise
        self.num_segments = num_segments
        self.initial_color = initial_color
        self.ending_color = ending_color
        self.life_time = life_time
        self._original_life_time = life_time
        self.initial_velocity = source.velocity
        self.thickness = thickness
        self.final_thickness = final_thickness

        super().__init__(
            initial_color=initial_color,
            ending_color=ending_color,
            ending_color_fade_type=ending_color_fade_type,
            life_time=life_time,
            size_change_type=size_change_type,
            floating_multi=source.floating_multi,
            initial_velocity=source.velocity,
        )
        Line.__init__(
            self,
            points=self.points,
            own_gravity=source._own_gravity_accel,
            initial_velocity=source.velocity,
            theme=Theme(color=initial_color),
            secondary_theme=Theme(color=ending_color),
            thickness=thickness,
        )
        self.segments = []
        self._gen_lightning()

    def get_render_info(self) -> list[RenderInfo]:
        return [info for line in self.segments for info in line.get_render_info()]

    def _apply_movement(self, engine) -> None:
        self._float_around()
        self.rotate()

        if not any(a != 0 for a in self.velocity):
            return

        def _get_new_points(p: tuple[PointF, PointF]) -> tuple[PointF, PointF]:
            return (
                (p[0] + self.source.velocity),
                (p[1] + self.source.velocity),
            )

        self.points = _get_new_points(self.points)

        for idx, _ in enumerate(self.segments):
            self.segments[idx]._apply_movement(engine)

        self.update_center_of_mass()

    # TODO: create recursive random branching
    def _gen_lightning(self) -> None:
        line_vector: VectorF = (self.points[0] - self.points[1]).as_vector()
        line_length = abs(line_vector)
        num_segments = self.num_segments

        avg_segment_length = line_length / (num_segments or ALMOST_ZERO)

        division_lenghts = [
            num_seg * avg_segment_length * self.parallel_noise
            for num_seg in range(self.num_segments)
        ]
        # if line_length > 8:
        #     raise NotImplementedError(
        #         # f"line: {line_vector}\nline_length:{line_length}\nnum_segments:{num_segments}\navg_seg_len: {avg_segment_length}\n"
        #         f"division_lengths {division_lenghts}"
        #     )

        def _rand_vector() -> VectorF:
            parallel_unit_vector = (1 / line_length) * line_vector
            normal_unit_vector = get_normal_unit_vector_from_line(*self.points)
            return (
                self.normal_noise * random_offset() * parallel_unit_vector
                + self.parallel_noise * random_offset() * normal_unit_vector
            ).as_vector()

        segment_points: list[PointF] = [
            self.points[0] + (x / (line_length or ALMOST_ZERO)) * line_vector + _rand_vector()
            for x in division_lenghts
        ]

        def _get_thickness(idx: int) -> float:
            if not self.final_thickness or self.final_thickness > self.thickness:
                return self.thickness
            _factor = idx / (len(self.segments) or 1)
            return (1 - _factor) * self.thickness + _factor * self.final_thickness

        lines: list[Line] = (
            [
                Line(
                    points=(segment_points[0], self.points[0]),
                    thickness=self.thickness,
                    theme=self.theme,
                    initial_velocity=self.velocity,
                )
            ]
            + [
                Line(
                    points=(
                        p,
                        segment_points[idx + 1],
                    ),
                    thickness=_get_thickness(idx),
                    theme=self.theme,
                    initial_velocity=self.velocity,
                )
                # if random_offset() < 0.4
                # else Lightning(
                #     source=Circunference(center=p, radius=1, theme=self.theme),
                #     end_point=p + random_offset_vector(5,5),
                #     initial_color=self.initial_color,
                #     ending_color=self.ending_color or self.initial_color,
                #     life_time=10,
                # )
                for idx, p in enumerate(segment_points[:-1])
            ]
            + [
                Line(
                    points=(segment_points[-1], self.points[1]),
                    thickness=self.final_thickness or self.thickness,
                    theme=self.theme,
                    initial_velocity=self.velocity,
                )
            ]
        )

        self.segments = lines

    def _handle_lifetime(self) -> None:
        if self.life_time is None or self._original_life_time is None:
            return
        self.life_time -= 1

        # TODO: unify in a method
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
            for idx in range(len(self.segments)):
                self.segments[idx].theme = self.theme

    def _act(self, engine) -> None:
        self._gen_lightning()
        self._apply_movement(engine)
