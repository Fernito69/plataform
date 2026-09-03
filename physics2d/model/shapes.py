import math
from abc import abstractmethod
from dataclasses import dataclass
from typing import Callable

from model.base import PointF
from model.theme import RGB, Theme
from physics2d.model.shared import RenderInfo


@dataclass
class GetCircunferenceEquationResponse:
    get_ys: Callable[[float], tuple[float, float] | tuple[None, None]]
    get_xs: Callable[[float], tuple[float, float] | tuple[None, None]]


class Shape:
    theme: Theme

    def __init__(self, theme: Theme = Theme()):
        self.theme = theme

    @abstractmethod
    def return_render_info(cls) -> list[RenderInfo]:
        # Each shape should do its thing
        raise NotImplementedError(f"Shape must have a return_render_info method")


class Circunference(Shape):
    center: PointF
    radius: float

    def __init__(self, center: PointF, radius: float, theme: Theme):
        super().__init__(theme=theme)
        self.center = center
        self.radius = radius

    def get_circunference_equations(
        self,
    ) -> GetCircunferenceEquationResponse:
        def get_ys(x: float) -> tuple[float, float] | tuple[None, None]:
            root_arg = self.radius**2 - (x - self.center.x) ** 2
            if root_arg < 0:
                return (None, None)
            root = root_arg**0.5
            return (self.center.y - root, self.center.y + root)

        def get_xs(y: float) -> tuple[float, float] | tuple[None, None]:
            root_arg = self.radius**2 - (y - self.center.y) ** 2
            if root_arg < 0:
                return (None, None)
            root = root_arg**0.5
            return (self.center.x - root, self.center.x + root)

        return GetCircunferenceEquationResponse(get_xs=get_xs, get_ys=get_ys)

    def return_render_info(self) -> list[RenderInfo]:
        piece_info = []
        min_x, max_x = sorted(
            (
                self.center.x + self.radius,
                self.center.x - self.radius,
            )
        )
        min_y, max_y = sorted(
            (
                self.center.y + self.radius,
                self.center.y - self.radius,
            )
        )

        eq = self.get_circunference_equations()

        for x in range(math.floor(min_x - 1), math.ceil(max_x + 1)):
            y1, y2 = eq.get_ys(x)

            # TODO: here we need to do something to make the upper border render
            if y1 is None or y2 is None:
                continue

            for y in range(math.floor(min_y - 1), math.ceil(max_y + 1)):
                x1, x2 = eq.get_xs(y)

                if x1 is None or x2 is None:
                    continue

                # TODO: good proxy with good performance, but maybe can be done better
                distance = min(
                    max(
                        0,
                        y - y2,
                        y1 - y,
                    ),
                    max(
                        0,
                        x - x2,
                        x1 - x,
                    ),
                )
                if distance > 1:
                    continue

                piece_info.append(
                    RenderInfo(
                        distance_to_pixel_center=distance,
                        color=self.theme.color or RGB(255, 255, 255),
                        point=PointF(x, y),
                    )
                )

        return piece_info
