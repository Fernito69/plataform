from typing import TYPE_CHECKING

from model.base import PointF
from model.theme import RGB, Theme
from physics2d.scenario.background import Background, BgLayer
from physics2d.shape.rectangle import Rectangle

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.physics2d import Physics2D
    from physics2d.shape.base import Shape

_NUM_LAYERS = 9

_DEPTH_PER_LAYER = 2


class SeaBackground(Background):
    """Performance is utter shit"""

    def __init__(self, engine: "Physics2D") -> None:
        self._engine = engine
        layers = self._init_layers()
        super().__init__(engine, layers)

    def _init_layers(self) -> list[BgLayer]:
        layers: list[BgLayer] = []

        X_RES, Y_RES = self._engine.get_resolution()
        safety_margin_x = 50
        safety_margin_y = 50

        for layer_num in range(1, _NUM_LAYERS + 1):
            shapes: list["Shape | PhysicsEntity"] = [
                Rectangle(
                    engine=self._engine,
                    theme=Theme(RGB(0, 0, 255 - 20 * layer_num)),
                    vertices=(
                        PointF(-safety_margin_x, -safety_margin_y + 3 * layer_num),
                        PointF(X_RES + safety_margin_x, 4 + 3 * layer_num),
                    ),
                )
            ]

            layers.append(
                BgLayer(
                    depth=layer_num * _DEPTH_PER_LAYER,
                    shapes=shapes,
                )
            )

        return layers


def get_sea_background(engine: "Physics2D") -> SeaBackground:
    return SeaBackground(engine)
