from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.scenario.background import Background, BgLayer
from physics2d.scenario.backgrounds.starry_space import get_starry_space
from physics2d.shape.circunference import Circunference
from utils import random_offset

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.physics2d import Physics2D
    from physics2d.shape.base import Shape

_NUM_LAYERS = 10
_ASTEROID_DENSITY = 30
_ASTEROID_RADIUS = 2
_DEPTH_PER_LAYER = 4


class SaturnRings(Background):
    """The beloved planet"""

    def __init__(self, engine: "Physics2D") -> None:
        self._engine = engine
        # Borrow stars from starry space
        layers = self._init_layers() + get_starry_space(engine)._init_layers(depth_per_layer=20)[4:]
        super().__init__(
            engine,
            layers,
            scroll_vertically=False,
        )

    def _init_layers(self) -> list[BgLayer]:
        layers: list[BgLayer] = []

        X_RES, Y_RES = self._engine.get_resolution()

        for layer_num in range(1, _NUM_LAYERS + 1):
            shapes: list["Shape | PhysicsEntity"] = []

            if layer_num == _NUM_LAYERS:
                layers.append(
                    BgLayer(
                        depth=layer_num * 2 * _DEPTH_PER_LAYER,
                        shapes=[],
                    )
                )
                break

            num_asteroids_in_layer = _ASTEROID_DENSITY * layer_num
            for asteroid_num in range(num_asteroids_in_layer):
                _factor = 1 / layer_num
                _safety_factor_x = 1

                # Spread all along horizontally
                x = (
                    -_safety_factor_x * X_RES
                    + (2 * _safety_factor_x * X_RES) * asteroid_num / num_asteroids_in_layer
                    + 6 * random_offset()
                )
                # All at the same height, like proper planet rings
                y = Y_RES / 2 + 12 * random_offset()
                # Random at depths, for more realistic effect
                z = 1 + (((layer_num) * _DEPTH_PER_LAYER) + random_offset() * _DEPTH_PER_LAYER) / 8

                color_gradient_factor = _factor**0.9

                shapes.append(
                    Circunference(
                        engine=self._engine,
                        initial_velocity=VectorF(0.1 + 0.1 * random_offset(), 0),
                        radius=(_ASTEROID_RADIUS + random_offset()) * _factor,
                        center=PointF(
                            x=x,
                            y=y,
                            z=z,
                        ),
                        theme=Theme(
                            RGB(
                                200 + 20 * random_offset(),
                                170 + 40 * random_offset(),
                                60,
                            ).with_intensity(color_gradient_factor)
                        ),
                        secondary_theme=Theme(
                            0.6
                            * RGB(
                                200 + 20 * random_offset(),
                                170 + 40 * random_offset(),
                                60,
                            ).with_intensity(color_gradient_factor)
                        ),
                    )
                )

            layers.append(
                BgLayer(
                    depth=layer_num * _DEPTH_PER_LAYER,
                    shapes=shapes,
                )
            )

        # Add "Saturn"
        layers[_NUM_LAYERS - 1].shapes.extend(
            [
                Circunference(
                    engine=self._engine,
                    radius=25,
                    center=PointF(
                        x=50,
                        y=Y_RES / 2,
                    ),
                    theme=Theme(RGB(200, 100, 20)),
                    secondary_theme=Theme(RGB(0, 0, 255)),
                    color_gradient_exponent=0.5,
                    # color_gradient_exponent_end=0.35,
                    # color_gradient_exponent_cycling_factor=1,
                ),
            ]
        )

        return layers


def get_saturn_rings(engine: "Physics2D") -> SaturnRings:
    return SaturnRings(engine)
