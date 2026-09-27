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

            min_x, min_y, max_x, max_y = self._get_screen_borders()

            for shape in layer.shapes:
                # TODO: this shouldn't happen here
                shape.do_your_thing()

                # TODO: do others
                if not isinstance(shape, Circunference):
                    continue

                # Correct shape position:
                _vector = _distance_factor * (
                    self._previous_screen_corner - self._engine.screen_corner
                )
                shape.center += _vector

                # TODO: stupid, do better... mayvbe with modulo?
                # TODO: WHY DOES THIS NOT WORK?=?=?
                # if shape.center.x >= max_x:
                #     shape.center.x = min_x

                # if shape.center.y >= max_y:
                #     shape.center.y = min_y

                # if shape.center.x < min_x:
                #     shape.center.x = max_x

                # if shape.center.y < min_y:
                #     shape.center.y = max_y

                render_info.extend(shape.get_render_info())

        return render_info

    @abstractmethod
    def _init_layers(self) -> list[BgLayer]: ...
