from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from model.base import PointF
from physics2d.model.shared import RenderInfo
from physics2d.shape.circunference import Circunference

if TYPE_CHECKING:
    from physics2d.entities.base import PhysicsEntity
    from physics2d.physics2d import Physics2D
    from physics2d.shape.base import Shape


@dataclass
class BgLayer:
    # the higher the depth, the slower it moves (parallax effect)
    depth: float
    shapes: list["Shape | PhysicsEntity"]


class Background:
    _engine: "Physics2D"

    _layers: list[BgLayer]
    _previous_screen_corner: PointF

    def __init__(self, engine: "Physics2D", layers: list[BgLayer]) -> None:
        self._engine = engine
        self._layers = layers
        self._previous_screen_corner = engine.screen_corner

    def set_previous_screen_corner(self, screen_corner: PointF) -> None:
        self._previous_screen_corner = PointF(
            x=screen_corner.x,
            y=screen_corner.y,
        )

    def _get_screen_borders(
        self,
        safety_factor_x: float = 0.5,
        safety_factor_y: float = 0.5,
    ) -> tuple[float, float, float, float]:
        """Response shape: (min_x, min_y, max_x, max_y)"""

        screen_x, screen_y, _ = self._engine.screen_corner
        X_RES, Y_RES = self._engine.get_resolution()
        _safety_x = X_RES * safety_factor_x
        _safety_y = Y_RES * safety_factor_y

        min_x = screen_x - _safety_x
        min_y = screen_y - _safety_y
        max_x = screen_x + X_RES + _safety_x
        max_y = screen_y + Y_RES + _safety_y

        return (min_x, min_y, max_x, max_y)

    def get_render_info(self) -> list[RenderInfo]:
        render_info: list[RenderInfo] = []

        for layer in self._layers:
            _distance_factor = 1 / layer.depth

            # min_x, min_y, max_x, max_y = self._get_screen_borders()
            # diff_x = max_x - min_x
            # diff_y = max_y - min_y
            # X_RES, Y_RES = self._engine.get_resolution()

            for shape in layer.shapes:
                shape.do_your_thing()

                # We can override the layer set depth with a z-coord
                if isinstance(shape, Circunference) and shape.center.z:
                    _distance_factor = 1 / shape.center.z

                # Correct shape position:
                _vector = (
                    _distance_factor * (self._previous_screen_corner - self._engine.screen_corner)
                ).as_vector()

                shape._move_by(_vector)

                # #TODO: WHYYYYY THIS DOESN'T WORKKK??
                # _safety_factor = 0.5
                # x_safety = X_RES * _safety_factor
                # y_safety = Y_RES * _safety_factor

                # if shape.center.x < -x_safety:
                #     shape.center.x = X_RES + x_safety - 1
                # elif shape.center.x > X_RES + x_safety:
                #     shape.center.x = 1 - x_safety

                # if shape.center.y < -y_safety:
                #     shape.center.y = Y_RES + y_safety - 1
                # elif shape.center.y > Y_RES + y_safety:
                #     shape.center.y = 1 - y_safety

                render_info.extend(shape.get_render_info())

        return render_info

    @abstractmethod
    def _init_layers(self) -> list[BgLayer]: ...
