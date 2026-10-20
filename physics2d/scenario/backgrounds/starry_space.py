from random import random
from typing import TYPE_CHECKING

from model.base import PointF
from model.theme import RGB, Theme
from physics2d.scenario.background import Background, BgLayer
from physics2d.shape.circunference import Circunference
from physics2d.shape.line import Line
from utils import random_offset

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.physics2d import Physics2D
    from physics2d.shape.base import Shape

_NUM_LAYERS = 9
_STAR_DENSITY = 6
_STAR_COLOR = RGB(215, 210, 255)
_STAR_RADIUS = 0.6
_DEPTH_PER_LAYER = 10
_DIMMING_RATIO = 0.8


class StarrySpace(Background):
    """Equidistant layers of stars"""

    def __init__(self, engine: "Physics2D") -> None:
        self._engine = engine
        layers = self._init_layers()
        super().__init__(engine, layers)

    def _init_layers(self, depth_per_layer: float = _DEPTH_PER_LAYER) -> list[BgLayer]:
        layers: list[BgLayer] = []

        X_RES, Y_RES = self._engine.get_resolution()

        for layer_num in range(_NUM_LAYERS + 1):
            shapes: list["Shape | PhysicsEntity"] = []

            if layer_num > 0:
                for _ in range(_STAR_DENSITY * layer_num):
                    _factor = 1 / layer_num
                    shapes.append(
                        Circunference(
                            engine=self._engine,
                            radius=(_STAR_RADIUS + 0.4 * random_offset()) * (_factor),
                            center=PointF(
                                x=(X_RES) * random(),
                                y=+(Y_RES) * random(),
                            ),
                            theme=Theme(
                                (_factor**0.8) * _STAR_COLOR + RGB(random() * 4 * layer_num, 0, 0)
                            ),
                            secondary_theme=Theme((_factor * _DIMMING_RATIO) * _STAR_COLOR),
                            color_cycling_factor=(3 + random_offset()) / 2,
                        )
                    )

                layers.append(
                    BgLayer(
                        depth=layer_num * depth_per_layer,
                        shapes=shapes,
                    )
                )
            else:
                # Add big planet  in bg
                shapes = [
                    Line(
                        engine=self._engine,
                        points=(
                            PointF(
                                x=42,
                                y=52,
                            ),
                            PointF(
                                x=49,
                                y=49,
                            ),
                        ),
                        theme=Theme(RGB(160, 120, 80)),
                        secondary_theme=Theme(0.9 * RGB(160, 120, 80)),
                    ),
                    Line(
                        engine=self._engine,
                        points=(
                            PointF(
                                x=50,
                                y=48,
                            ),
                            PointF(
                                x=58,
                                y=48,
                            ),
                        ),
                        theme=Theme(RGB(160, 120, 80) * 0.9),
                        secondary_theme=Theme(0.8 * RGB(160, 120, 80)),
                    ),
                    Circunference(
                        engine=self._engine,
                        radius=4,
                        center=PointF(
                            x=50,
                            y=50,
                        ),
                        theme=Theme(RGB(255, 255, 220)),
                        secondary_theme=Theme(0.4 * RGB(255, 255, 220)),
                    ),
                    # simulate ring going back
                    Line(
                        engine=self._engine,
                        points=(
                            PointF(
                                x=42,
                                y=52,
                            ),
                            PointF(
                                x=49,
                                y=53,
                            ),
                        ),
                        theme=Theme(0.7 * RGB(160, 120, 80)),
                        secondary_theme=Theme(0.6 * RGB(160, 120, 80)),
                    ),
                    Line(
                        engine=self._engine,
                        points=(
                            PointF(
                                x=50,
                                y=53,
                            ),
                            PointF(
                                x=58,
                                y=48,
                            ),
                        ),
                        theme=Theme(0.6 * RGB(160, 120, 80)),
                        secondary_theme=Theme(0.5 * RGB(160, 120, 80)),
                    ),
                ]
                # TODO: planet looks dumb! make better
                shapes = []
                layers.append(
                    BgLayer(
                        depth=depth_per_layer * (layer_num + 1),
                        shapes=shapes,
                    )
                )

        return layers


def get_starry_space(engine: "Physics2D") -> StarrySpace:
    return StarrySpace(engine)
