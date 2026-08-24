import math

from factories.theme import White
from model.base import Point2, Vector2
from model.theme import Theme
from physics2d.model.base import RenderInfo
from physics2d.scenario.piece import ScenarioPiece


class Rectangle(ScenarioPiece):
    vertices: tuple[Point2, Point2]

    def __init__(
        self,
        vertices: tuple[Point2, Point2],
        theme: Theme = Theme(),
        angle: float = 0,
        affected_by_gravity: bool = False,
        initial_velocity: Vector2 = (0, 0),
    ):
        super().__init__(
            name="Rectangle",
            theme=theme,
            angle=angle,
            affected_by_gravity=affected_by_gravity,
            initial_velocity=initial_velocity,
        )
        self.vertices = vertices

    def apply_movement(self) -> None:
        if not any(a != 0 for a in self.velocity):
            return
        self.vertices = (
            (self.vertices[0][0] + self.velocity[0], self.vertices[0][1] + self.velocity[1]),
            (self.vertices[1][0] + self.velocity[0], self.vertices[1][1] + self.velocity[1]),
        )

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
