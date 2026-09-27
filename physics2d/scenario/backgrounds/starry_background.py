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
_STAR_RADIUS = 1
_DEPTH_PER_LAYER = 5
_DIMMING_RATIO = 0.6


class StarryBackground(Background):
    """Equidistant layers of stars"""

    def __init__(self, engine: "Physics2D") -> None:
        self._engine = engine
        layers = self._init_layers()
        super().__init__(engine, layers)

    def _init_layers(self) -> list[BgLayer]:
        layers: list[BgLayer] = []

        min_x, min_y, max_x, max_y = self._get_screen_borders()

        for layer_num in range(1, _NUM_LAYERS + 1):
            shapes: list["Shape | PhysicsEntity"] = []

            for _ in range(_STAR_DENSITY * layer_num):
                _factor = 1 / layer_num
                shapes.append(
                    # TODO: I'll do it with little circles for now, but this should be Dot
                    Circunference(
                        engine=self._engine,
                        radius=_STAR_RADIUS * (_factor**0.5),
                        center=PointF(
                            x=min_x + max_x * random(),
                            y=min_y + max_y * random(),
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

        return layers
