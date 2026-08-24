import math
from abc import abstractmethod
from dataclasses import dataclass
from typing import Callable

from constants import HALF_PIXEL
from factories.theme import White
from model.base import Point2
from model.theme import Theme
from physics2d.model.base import RenderInfo
from utils import distance_from_line_to_point


@dataclass
class GetCircunferenceEquationResponse:
    get_ys: Callable[[float], tuple[float, float] | tuple[None, None]]
    get_xs: Callable[[float], tuple[float, float] | tuple[None, None]]


class ScenarioPiece:
    theme: Theme
    name: str
    # in radians
    angle: float

    def __init__(self, name: str, theme: Theme = Theme(), angle: float = 0):
        self.theme = theme
        self.name = name
        self.angle = angle

    @abstractmethod
    def return_render_info(cls) -> list[RenderInfo]:
        # Each entity should do its thing
        raise NotImplementedError(
            f"{cls.name or 'UnknownPiece'} must have a return_render_info method"
        )


class Line(ScenarioPiece):
    points: tuple[Point2, Point2]
    thickness: int

    def __init__(
        self,
        vertices: tuple[Point2, Point2],
        theme: Theme = Theme(),
        angle: float = 0,
        thickness: int = 1,
    ):
        self.points = vertices
        self.thickness = thickness
        super().__init__("Line", theme, angle)

    def return_render_info(self) -> list[RenderInfo]:
        piece_info = []
        min_x, max_x = sorted(
            (
                self.points[0][0],
                self.points[1][0],
            )
        )
        min_y, max_y = sorted(
            (
                self.points[0][1],
                self.points[1][1],
            )
        )

        for x in range(math.floor(min_x - self.thickness), math.ceil(max_x + self.thickness)):
            for y in range(math.floor(min_y - self.thickness), math.ceil(max_y + self.thickness)):
                distance = distance_from_line_to_point(
                    self.points, (x + HALF_PIXEL, y + HALF_PIXEL)
                ).distance

                if distance > self.thickness:
                    continue

                piece_info.append(
                    RenderInfo(
                        distance_to_pixel_center=distance / self.thickness or 1,
                        color=self.theme.color or White(),
                        point=(x, y),
                    )
                )

        return piece_info


class Rectangle(ScenarioPiece):
    vertices: tuple[Point2, Point2]

    def __init__(self, vertices: tuple[Point2, Point2], theme: Theme = Theme(), angle: float = 0):
        super().__init__(name="Rectangle", theme=theme, angle=angle)
        self.vertices = vertices

    def return_render_info(self) -> list[RenderInfo]:
        piece_info = []
        min_x, max_x = sorted(
            (
                self.vertices[0][0],
                self.vertices[1][0],
            )
        )
        min_y, max_y = sorted(
            (
                self.vertices[0][1],
                self.vertices[1][1],
            )
        )

        # eqs_left_side = get_line_equations((min_x, min_y), (min_x, max_y))
        # eqs_right_side = get_line_equations((max_x, min_y), (max_x, max_y))
        # eqs_upper_side = get_line_equations((min_x, max_y), (max_x, max_y))
        # eqs_lower_side = get_line_equations((min_x, min_y), (max_x, min_y))

        for x in range(math.floor(min_x), math.ceil(max_x)):
            for y in range(math.floor(min_y), math.ceil(max_y)):
                # TODO: make this with angles, it gets a bit more tricky
                if max_x >= x >= min_x and max_y >= y >= min_y:
                    piece_info.append(
                        RenderInfo(
                            distance_to_pixel_center=0,
                            color=self.theme.color.with_intensity()
                            if self.theme.color
                            else White(),
                            point=(x, y),
                        )
                    )

        return piece_info


class Circunference(ScenarioPiece):
    center: Point2
    radius: float

    def __init__(self, center: Point2, radius: float, theme: Theme = Theme(), angle: float = 0):
        super().__init__(name="Circle", theme=theme, angle=angle)
        self.center = center
        self.radius = radius

    def get_circunference_equations(
        self,
    ) -> GetCircunferenceEquationResponse:
        def get_ys(x: float) -> tuple[float, float] | tuple[None, None]:
            root_arg = self.radius**2 - (x - self.center[0]) ** 2
            if root_arg < 0:
                return (None, None)
            root = root_arg**0.5
            return (self.center[1] - root, self.center[1] + root)

        def get_xs(y: float) -> tuple[float, float] | tuple[None, None]:
            root_arg = self.radius**2 - (y - self.center[1]) ** 2
            if root_arg < 0:
                return (None, None)
            root = root_arg**0.5
            return (self.center[0] - root, self.center[0] + root)

        return GetCircunferenceEquationResponse(get_xs=get_xs, get_ys=get_ys)

    def return_render_info(self) -> list[RenderInfo]:
        piece_info = []
        min_x, max_x = sorted(
            (
                self.center[0] + self.radius,
                self.center[0] - self.radius,
            )
        )
        min_y, max_y = sorted(
            (
                self.center[1] + self.radius,
                self.center[1] - self.radius,
            )
        )

        eq = self.get_circunference_equations()

        for x in range(math.floor(min_x - 1), math.ceil(max_x + 1)):
            y1, y2 = eq.get_ys(x)

            if y1 is None or y2 is None:
                continue

            for y in range(math.floor(min_y - 1), math.ceil(max_y + 1)):
                x1, x2 = eq.get_xs(y)

                if x1 is None or x2 is None:
                    continue

                distance = min(
                    1,
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
                piece_info.append(
                    RenderInfo(
                        distance_to_pixel_center=distance,
                        color=self.theme.color or White(),
                        point=(x, y),
                    )
                )

        return piece_info
