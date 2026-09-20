from typing import TYPE_CHECKING

from model.base import PointF
from model.theme import RGB, Theme
from physics2d.entities.base import PhysicsEntity
from physics2d.shape.line import Line
from physics2d.shape.model.shared import LineLifeStep, TransitionType
from physics2d.shape.particle.base import Particle

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


class LineParticle(Particle, Line):
    points: tuple[PointF, PointF]
    source: PhysicsEntity
    life_steps: list[LineLifeStep]

    _target: PhysicsEntity | None
    _initial_target_position: PointF | None

    def __init__(
        self,
        source: PhysicsEntity,
        end_point: PointF,
        engine: "Physics2D",
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
        render_behind_player: bool = False,
        target: PhysicsEntity | None = None,
        life_steps: list[LineLifeStep] = [],
        pulsate_freq: float = 0,
        pulsate_amplitude: float = 0,
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
        self.render_behind_player = render_behind_player
        self._target = target
        self._pulsate_freq = pulsate_freq
        self._pulsate_amplitude = pulsate_amplitude
        self._initial_target_position = (
            PointF(x=self._target.position.x, y=self._target.position.y) if self._target else None
        )
        self.life_steps = life_steps
        self._counter = 0
        self._engine = engine

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
            render_behind_player=render_behind_player,
            pulsate_amplitude=pulsate_amplitude,
            pulsate_freq=pulsate_freq,
            engine=engine,
        )

    def _handle_life_time(self) -> None:
        if len(self.life_steps) > 0:
            return self._handle_life_steps()

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

    ####################################################
    # TODO: test this with DeathRay
    _curr_step_idx: int = -1
    _thickness_at_start: float | None = None

    def _handle_life_steps(self) -> None:
        if self.life_time is None or self._original_life_time is None:
            return

        _curr_life_tick: int = self._original_life_time - self.life_time

        for index, step in enumerate(sorted(self.life_steps, key=lambda s: s.life_tick)):
            # Identify step
            if _curr_life_tick == step.life_tick:
                self._curr_step_idx = index

            # Act
            if self._curr_step_idx == index:
                _next_tick: int = (
                    self.life_steps[index + 1].life_tick
                    if index <= len(self.life_steps) - 1
                    else self._original_life_time
                )
                tick_relative_to_step = _curr_life_tick - step.life_tick + 1
                step_length = _curr_life_tick - _next_tick
                factor = tick_relative_to_step / step_length

                if step.thickness is not None and step.thickness != self.thickness:
                    if self._thickness_at_start is None:
                        self._thickness_at_start = self.thickness

                    self.thickness = (
                        factor * step.thickness + (1 - factor) * self._thickness_at_start
                    )

                    if tick_relative_to_step == step_length:
                        self._thickness_at_start = None

                # TODO: handle theme

    def _act(self) -> None:
        self._apply_movement()
