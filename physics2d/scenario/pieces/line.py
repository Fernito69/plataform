import math

from constants import HALF_PIXEL
from factories.theme import White
from model.base import Point2, Vector2
from model.theme import Theme
from physics2d.model.base import RenderInfo
from physics2d.scenario.piece import ScenarioPiece
from utils import distance_from_line_to_point


class Line(ScenarioPiece):
    points: tuple[Point2, Point2]
    thickness: int

    def __init__(
        self,
        vertices: tuple[Point2, Point2],
        theme: Theme = Theme(),
        angle: float = 0,
        thickness: int = 1,
        affected_by_gravity: bool = False,
        initial_velocity: Vector2 = (0, 0),
        own_gravity: float | None = None,
        secondary_theme: Theme | None = None,
        floating_multi: float = 0,
    ):
        self.points = vertices
        self.thickness = thickness
        super().__init__(
            "Line",
            theme,
            angle,
            affected_by_gravity,
            initial_velocity,
            own_gravity,
            secondary_theme,
            floating_multi,
        )

    def apply_movement(self) -> None:
        self._float_around()

        if not any(a != 0 for a in self.velocity):
            return
        pass

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
