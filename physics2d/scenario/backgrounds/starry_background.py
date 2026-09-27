from random import random
from typing import TYPE_CHECKING

from model.base import PointF
from model.theme import RGB, Theme
from physics2d.scenario.background import Background, BgLayer
from physics2d.shape.circunference import Circunference
from utils import random_offset

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.physics2d import Physics2D
    from physics2d.shape.base import Shape

_NUM_LAYERS = 9
_STAR_DENSITY = 10
_STAR_COLOR = RGB(200, 210, 255)
_STAR_RADIUS = 0.8
_DEPTH_PER_LAYER = 10
_DIMMING_RATIO = 0.6


class StarryBackground(Background):
    """Equidistant layers of stars"""

    def __init__(self, engine: "Physics2D") -> None:
        self._engine = engine
        layers = self._init_layers()
        super().__init__(engine, layers)

    def _init_layers(self) -> list[BgLayer]:
        layers: list[BgLayer] = []

        X_RES, Y_RES = self._engine.get_resolution()

        for layer_num in range(1, _NUM_LAYERS + 1):
            shapes: list["Shape | PhysicsEntity"] = []

            for _ in range(_STAR_DENSITY * layer_num):
                _factor = 1 / layer_num
                shapes.append(
                    # TODO: I'll do it with little circles for now, but this should be Dot
                    Circunference(
                        engine=self._engine,
                        radius=(_STAR_RADIUS + 0.2 * random_offset()) * (_factor),
                        center=PointF(
                            x=(X_RES) * random(),
                            y=+(Y_RES) * random(),
                        ),
                        theme=Theme(
                            _STAR_COLOR.with_intensity(_factor)
                            + RGB(random() * 4 * layer_num, 0, 0)
                        ),
                        secondary_theme=Theme(_STAR_COLOR.with_intensity(_factor * _DIMMING_RATIO)),
                        color_cycling_factor=(3 + random_offset()) / 2,
                    )
                )

            layers.append(
                BgLayer(
                    depth=layer_num * _DEPTH_PER_LAYER,
                    shapes=shapes,
                )
            )

        # Add big star in bg
        layers[_NUM_LAYERS - 1].shapes.append(
            Circunference(
                engine=self._engine,
                radius=4,
                center=PointF(
                    x=50,
                    y=50,
                ),
                theme=Theme(RGB(255, 255, 220)),
                secondary_theme=Theme(RGB(255, 255, 180)),
                color_cycling_factor=(3 + random_offset()) / 2,
            )
        )

        return layers
