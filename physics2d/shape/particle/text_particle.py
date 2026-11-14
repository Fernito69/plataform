from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.shape.model.shared import TransitionType
from physics2d.shape.particle.base import Particle
from physics2d.shape.text import Text

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


class TextParticle(Text, Particle):
    initial_thickness: float
    final_thickness: float | None = None

    initial_scale_factor: float
    final_scale_factor: float | None

    def __init__(
        self,
        engine: "Physics2D",
        position: PointF,
        initial_color: RGB,
        text: str,
        ending_color: RGB | None = None,
        life_time: int | None = None,
        floating_multi: float = 0,
        scale_factor: float = 1,
        thickness: float = 1,
        thickness_gradient_threshold: float = 0.5,
        initial_velocity: VectorF = VectorF(0, 0),
        pulsate_freq: float = 0,
        pulsate_amplitude: float = 0,
        final_thickness: float | None = None,
        final_scale_factor: float | None = None,
        changes_exponentially: bool = False,
        initial_angular_velocity: float = 0,
        angle: float = 0,
    ):
        self.text = text

        # Text
        super().__init__(
            engine=engine,
            text_color=initial_color,
            position=position,
            scale_factor=scale_factor,
            thickness=thickness,
            thickness_gradient_threshold=thickness_gradient_threshold,
            initial_velocity=initial_velocity,
            pulsate_amplitude=pulsate_amplitude,
            pulsate_freq=pulsate_freq,
            text=text,
            initial_angular_velocity=initial_angular_velocity,
            angle=angle,
        )
        self._engine = engine
        self.theme = Theme(initial_color)
        self.position = position
        self.engine = engine
        self.scale_factor = scale_factor
        self.final_scale_factor = final_scale_factor
        self.thickness = thickness
        self.final_thickness = final_thickness
        self.thickness_gradient_threshold = thickness_gradient_threshold
        self.velocity = initial_velocity
        self.pulsate_freq = pulsate_freq
        self.pulsate_amplitude = pulsate_amplitude
        self.angle = angle
        self.initial_angular_velocity = initial_angular_velocity

        # Particle
        self.life_time = life_time
        self._original_life_time = life_time
        self.initial_color = initial_color
        self.ending_color = ending_color

        self.initial_scale_factor = scale_factor
        self.initial_thickness = thickness

        self.floating_multi = floating_multi
        self.size_change_type = (
            TransitionType.EXPONENTIAL if changes_exponentially else TransitionType.LINEAR
        )
        Particle.__init__(
            self,
            initial_color=initial_color,
            ending_color=ending_color,
            life_time=life_time,
            floating_multi=floating_multi,
            size_change_type=self.size_change_type,
        )

    def do_your_thing(self) -> None:
        super().do_your_thing()
        self._handle_life_time()

    def _handle_life_time(self) -> None:
        if (
            self.life_time is None
            or self._original_life_time is None
            or (
                not self.ending_color
                and self.final_scale_factor is None
                and self.final_thickness is None
            )
        ):
            return

        elapsed_factor = 1 - (self.life_time / self._original_life_time)
        remaining_factor = 1 - elapsed_factor

        self.life_time -= 1

        if self.ending_color and self.theme.color:
            if self.initial_color.opacity != 1 or self.ending_color.opacity != 1:
                target_opacity = (
                    self.initial_color.opacity * remaining_factor
                    + self.ending_color.opacity * elapsed_factor
                )
                self.theme.color = (
                    self.initial_color.copy(opacity=1)
                    .get_gradient(self.ending_color.copy(opacity=1), elapsed_factor)
                    .copy(opacity=target_opacity)
                )
            else:
                self.theme.color = self.initial_color.get_gradient(
                    self.ending_color, elapsed_factor
                )

        if self.final_scale_factor is not None:
            exponent = 0.5 if self.size_change_type == TransitionType.EXPONENTIAL else 1
            factor = elapsed_factor**exponent
            self.scale_factor = (
                self.initial_scale_factor * (1 - factor) + self.final_scale_factor * factor
            )

        if self.final_thickness is not None:
            self.thickness = (
                self.initial_thickness * remaining_factor + self.final_thickness * elapsed_factor
            )
