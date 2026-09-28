from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.entities.three_dee_enemy import ThreeDeeEnemy
from physics2d.scenario.background import Background, BgLayer
from physics2d.scenario.backgrounds.starry_space import get_starry_space
from three_d_renderer.entities.polyhedra import Dodeca

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


class DodecaDyson(Background):
    """Dyson-Dodeca? Why not!"""

    def __init__(self, engine: "Physics2D") -> None:
        self._engine = engine
        # Borrow stars from starry space
        layers = self._init_layers() + get_starry_space(engine)._init_layers(depth_per_layer=10)[2:]
        super().__init__(
            engine,
            layers,
            scroll_vertically=False,
        )

    def _init_layers(self) -> list[BgLayer]:
        layers: list[BgLayer] = []

        # Dodeca lurking in the bg
        layers.append(
            BgLayer(
                depth=100,
                shapes=[
                    ThreeDeeEnemy(
                        engine=self._engine,
                        health=None,
                        position=PointF(150, 0),
                        polyhedron=Dodeca(
                            position=PointF(35, 92, 0),
                            size=18,
                            rot_vector=VectorF(-0.1, 0.2, 0.05),
                            # mov_vector=VectorF(-0.005, 0, -0.005),
                        ),
                        line_thickness=1.5,
                        theme=Theme(RGB(255, 0, 80)),
                        secondary_theme=Theme(RGB(0, 80, 255)),
                        color_cycling_factor=200,
                    ),
                ],
            )
        )

        return layers


def get_dodeca_dyson(engine: "Physics2D") -> DodecaDyson:
    return DodecaDyson(engine)
