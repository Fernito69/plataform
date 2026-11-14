from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import BR, RGB
from physics2d.entities.base import PhysicsEntity
from physics2d.entities.model.spawner import Spawner
from physics2d.entities.spawners.utils import get_position
from physics2d.shape.particle.text_particle import TextParticle

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


def text_spawner(
    text: str,
    scale_factor: float = 1,
    final_scale_factor: float = 1,
    initial_color: RGB = RGB(),
    ending_color: RGB = RGB(),
    life_time: int = 30,
    thickness: int = 1,
    initial_velocity: VectorF = VectorF(0, 0),
    initial_angular_velocity: float = 0,
) -> Spawner:
    def _s(engine: "Physics2D", source: PhysicsEntity | PointF) -> None:

        # TODO: this should be somehow a Text/TextParticle thing, right?
        for row_idx, row_text in enumerate(text.split(BR)):
            # TODO: import these as constants please!
            char_height_plus_sep = (8 + 2) * scale_factor
            char_width_plus_sep = (6 + 2) * scale_factor
            position = get_position(source) - VectorF(
                x=char_width_plus_sep * (len(row_text) / 2),
                y=char_height_plus_sep * row_idx,
            )
            _t = TextParticle(
                engine=engine,
                position=position,
                text=row_text,
                initial_color=initial_color,
                ending_color=ending_color,
                thickness=thickness,
                life_time=life_time,
                scale_factor=scale_factor,
                final_scale_factor=final_scale_factor,
                initial_velocity=initial_velocity,
                changes_exponentially=True,
                initial_angular_velocity=initial_angular_velocity,
            )
            engine.scenario.fg_shapes[0:0] = [_t]

    return _s


####


def wave_started_text(
    text: str,
    subtitle: bool = False,
) -> Spawner:
    return text_spawner(
        text=text,
        scale_factor=0.75 if subtitle else 1,
        final_scale_factor=1 if subtitle else 1.5,
        initial_color=RGB(255, 0, 0),
        ending_color=RGB(0, 0, 255, opacity=0),
        life_time=75,
    )
