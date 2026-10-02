from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.entities.three_dee_enemy import ThreeDeeEnemy
from physics2d.scenario.background import Background, BgLayer
from physics2d.scenario.backgrounds.starry_space import get_starry_space
from physics2d.shape.line import Line
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

        X_RES, Y_RES = self._engine.get_resolution()
        _safety_x_margin = 10
        _milkyway_thickness = 10
        _milkyway_intensity = 0.6
        _milkyway_end_intensity = 0.1
        _milkyway_color = RGB(100, 100, 225)

        # Dodeca lurking in the bg
        layers.append(
            BgLayer(
                depth=1000,
                shapes=[
                    ThreeDeeEnemy(
                        engine=self._engine,
                        health=None,
                        position=PointF(150, 0),
                        polyhedron=Dodeca(
                            position=PointF(30, 80, 0),
                            size=16,
                            rot_vector=VectorF(-0.1, 0.2, 0.05),
                        ),
                        line_thickness=1.5,
                        theme=Theme(RGB(255, 0, 0)),
                        secondary_theme=Theme(RGB(0, 0, 255)),
                        # theme=Theme(RGB(255, 0, 80)),
                        # secondary_theme=Theme(RGB(0, 80, 255)),
                        color_cycling_factor=200,
                        # Background layers are drawn in screen coordinates.
                        absolute_positioning=True,
                    ),
                    # "Milky way"
                    Line(
                        engine=self._engine,
                        points=(
                            PointF(
                                x=-_safety_x_margin,
                                y=Y_RES / 2,
                            ),
                            PointF(
                                x=X_RES / 2 - _milkyway_thickness,
                                y=Y_RES / 2,
                            ),
                        ),
                        theme=Theme(_milkyway_end_intensity * _milkyway_color),
                        secondary_theme=Theme(0.9 * _milkyway_intensity * _milkyway_color),
                        thickness=_milkyway_thickness,
                    ),
                    Line(
                        engine=self._engine,
                        points=(
                            PointF(
                                x=X_RES / 2 + _milkyway_thickness + 1,
                                y=Y_RES / 2,
                            ),
                            PointF(
                                x=X_RES + _safety_x_margin,
                                y=Y_RES / 2,
                            ),
                        ),
                        theme=Theme(_milkyway_intensity * _milkyway_color),
                        secondary_theme=Theme(_milkyway_end_intensity * _milkyway_color),
                        thickness=_milkyway_thickness,
                    ),
                ],
            )
        )

        return layers


def get_dodeca_dyson(engine: "Physics2D") -> DodecaDyson:
    return DodecaDyson(engine)
