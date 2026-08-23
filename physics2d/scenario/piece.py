import math
from abc import abstractmethod

from constants import HALF_PIXEL
from factories.theme import White
from model.base import Point2
from model.theme import Theme
from physics2d.model.base import RenderInfo
from utils import distance_from_line_to_point

R2 = 1.414


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
    vertices: tuple[Point2, Point2]

    def __init__(
        self,
        vertices: tuple[Point2, Point2],
        theme: Theme = Theme(),
        angle: float = 0,
        name: str | None = None,
    ):
        self.name = name or "Line"
        self.vertices = vertices
        ScenarioPiece.__init__(self, self.name, theme, angle)

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

        for x in range(math.floor(min_x), math.ceil(max_x)):
            for y in range(math.floor(min_y), math.ceil(max_y)):
                distance = distance_from_line_to_point(
                    self.vertices, (x + HALF_PIXEL, y + HALF_PIXEL)
                ).distance

                if distance > R2:
                    continue

                piece_info.append(
                    RenderInfo(
                        distance_to_pixel_center=distance,
                        color=self.theme.color or White(),
                        point=(x, y),
                    )
                )

        return piece_info


class Rectangle(Line):
    vertices: tuple[Point2, Point2]

    def __init__(self, vertices: tuple[Point2, Point2], theme: Theme = Theme(), angle: float = 0):
        Line.__init__(self, name="Rectangle", theme=theme, vertices=vertices, angle=angle)

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
