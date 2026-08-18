import math

from display import Display
from factories.theme import DEFAULT_CHAR, White
from model.base import Point2
from model.theme import RGB
from three_d_renderer.entities.player3d import Player3D
from three_d_renderer.model.base import PixelContribution, RenderData, SubpixelContribution, Vertex3
from three_d_renderer.scenario.level_3d import Level3D
from three_d_renderer.three_d_renderer import ThreeDeeRenderer
from utils import (
    colored,
    distance_between_points,
    distance_from_line_to_point,
    get_line_equations,
    mix_colors,
    subtract_triplet,
)

PIXEL = 1
HALF_PIXEL = 0.5
QUARTER_PIXEL = 0.25

PI = 3.14159265

DIRECTIONS = [
    (-1, 1),
    (0, 1),
    (1, 1),
    (-1, 0),
    (0, 0),
    (1, 0),
    (-1, -1),
    (0, -1),
    (1, -1),
]


# What's the max distance? from the middle to the corner -> sqrt(.25^2+.5^2) -> 0.559
# We take that as 0% contribution, and 0 as 100%
DISTANCE_FROM_SUBPIXEL_CENTER_TO_CORNER = 0.559


# TODO: move this function elsewhere or make it static method
def _get_contribution(distance: float, slope: float | None) -> float:
    # Corrected by the 2/1 ratio between real x and real y
    # TODO: I'm assuming it's a linear relationship with the angle, maybe it's not.
    distance /= (1 + math.atan(slope) / (PI / 2)) if slope is not None else 2

    return max(
        1 - distance / DISTANCE_FROM_SUBPIXEL_CENTER_TO_CORNER,
        0,
    )


class RendererV2(ThreeDeeRenderer):
    # TODO: this should be in display?
    screen_data: list[list[list[PixelContribution]]]

    def __init__(
        self,
        player: Player3D,
        display: Display,
        level: Level3D | None = None,
    ):
        ThreeDeeRenderer.__init__(self, player, display, level)
        self._empty_screen_data()

    def _get_render_v2_list(self) -> list[RenderData]:
        # Order vertices by closest to farthest and exclude those too far away to be rendered
        return [
            data
            for data in sorted(
                [
                    RenderData(
                        entity_idx=entity_idx,
                        entity=entity,
                        vertex=Vertex3(point=vertex, index=vertex_idx),
                        dist_vector=distance_between_points(
                            vertex, self.player.position, entity=entity
                        ),
                    )
                    for entity_idx, entity in enumerate(self._curr_level.entities)
                    for vertex_idx, vertex in enumerate(entity.vertices)
                ],
                key=lambda r: r.dist_vector.distance,
            )
            if data.dist_vector.distance < self.visibility_threshold
        ]

    def _empty_screen_data(self) -> None:
        self.screen_data = []
        for y in range(self.display.curr_y_resolution):
            self.screen_data.append([])
            for _ in range(self.display.curr_x_resolution):
                self.screen_data[y].append([])

    def render_v2(self):
        self._empty_screen_data()
        render_list: list[RenderData] = self._get_render_v2_list()

        # TODO: calculations should not be part of the rendering
        for entity in self._curr_level.entities:
            entity.calc_v2_vertexes(apply=True)
            entity.movement()
            entity.apply_rotations()

        for data in render_list:
            # 1) Take vertices and trace lines
            # 2) Figure out pixels the line goes through
            # 3) Figure out pixel_usage_ratio

            # Check all the other vertices this vertex is connected to
            connections = [c for c in data.entity.vertex_connections if c[0] == data.vertex.index]

            # Calc connecting lines
            for _, connecting_vertex_index in connections:
                curr_pixel_pos: Point2 = self._get_screen_projection(
                    subtract_triplet(data.vertex.point, self.player.position)
                )
                connecting_pixel_pos: Point2 = self._get_screen_projection(
                    subtract_triplet(
                        data.entity.vertices[connecting_vertex_index], self.player.position
                    )
                )

                # TODO: Wait, this doesn't necessarily mean the line it generates is not visible! This needs to be fixed
                if not self.display.is_in_screen(curr_pixel_pos) and not self.display.is_in_screen(
                    connecting_pixel_pos
                ):
                    continue

                self._compute_pixel_contributions(data, (curr_pixel_pos, connecting_pixel_pos))

        # Fill in screen data!!! TODO: we should involve the display class here, this is hacky
        new_screen_matrix = self.display._screen_matrix
        # for y in range(self.display.curr_y_resolution):
        #     new_screen_matrix.append([])
        #     for x in range(self.display.curr_x_resolution):
        #         new_screen_matrix[y].append(_DEFAULT_CHAR)

        for x in range(self.display.curr_x_resolution):
            for y in range(self.display.curr_y_resolution):
                data = self.screen_data[y][x]

                if len(data) == 0:
                    new_screen_matrix[y][x] = DEFAULT_CHAR
                    continue

                def _get_intensity(c: SubpixelContribution):
                    return c.pixel_usage_ratio * max(
                        min(
                            1 - c.distance_from_spec / self.visibility_threshold,
                            1,
                        ),
                        0,
                    )

                color = mix_colors(
                    [
                        (c.upper_subpixel.color or White()).with_intensity(
                            _get_intensity(c.upper_subpixel)
                        )
                        for c in data
                    ]
                )
                bg_color = mix_colors(
                    [
                        (c.lower_subpixel.color or White()).with_intensity(
                            _get_intensity(c.lower_subpixel)
                        )
                        for c in data
                    ]
                )
                # TODO: do properly
                new_screen_matrix[y][x] = colored("▀", color=color, bg_color=bg_color)

        self.display.put_screen_content(new_screen_matrix)
        self.display.print_curr_screen(self.player)

    def _compute_pixel_contributions(self, data: RenderData, line: tuple[Point2, Point2]) -> None:
        # Check the affected pixels:
        curr_pixel_pos, connecting_pixel_pos = line
        x1, y1 = curr_pixel_pos
        x2, y2 = connecting_pixel_pos

        # get the target area of the screen
        range_x_min = math.floor(max(min(x1, x2), 0))
        range_x_max = math.ceil(min(max(x1, x2), self.display.curr_x_resolution))
        range_y_min = math.floor(max(min(y1, y2), 0))
        range_y_max = math.ceil(min(max(y1, y2), self.display.curr_y_resolution))

        eq = get_line_equations(curr_pixel_pos, connecting_pixel_pos)

        for x in range(range_x_min, range_x_max):
            for y in range(range_y_min, range_y_max):
                if not self.display.is_in_screen((x, y)):
                    continue

                calculated_y = eq.get_y(x)
                calculated_x = eq.get_x(calculated_y)

                if y <= calculated_y <= (y + PIXEL) and x <= calculated_x <= (x + PIXEL):
                    # color hack
                    # color = data.entity.theme.color
                    color = self.colors[round(data.entity.size) % len(self.colors)]()

                    # check the bleeding in all directions:
                    for delta_x, delta_y in [
                        d
                        for d in DIRECTIONS
                        if x + d[0] <= range_x_max
                        and x + d[0] >= range_x_min
                        and y + d[1] <= range_y_max
                        and y + d[1] >= range_y_min
                    ]:
                        self._add_contribution_to_screen(
                            line=(curr_pixel_pos, connecting_pixel_pos),
                            curr_screen_pos=(x + delta_x, y + delta_y),
                            distance=data.dist_vector.distance,
                            color=color,
                        )

    def _add_contribution_to_screen(
        self,
        line: tuple[Point2, Point2],
        curr_screen_pos: Point2,
        color: RGB,
        distance: float,
    ):
        x, y = curr_screen_pos

        # Upper pixel limits -> (x,y) (x+1, y + .5)
        middle_upper_subpixel = (x + HALF_PIXEL, y + QUARTER_PIXEL)
        # Lower pixel limits -> (x,y+.5) (x+1, y + 1)
        middle_lower_subpixel = (x + HALF_PIXEL, y + (HALF_PIXEL + QUARTER_PIXEL))

        upper_res = distance_from_line_to_point(
            line,
            middle_upper_subpixel,
        )
        lower_res = distance_from_line_to_point(
            line,
            middle_lower_subpixel,
        )

        upper_contribution_ratio: float = _get_contribution(upper_res.distance, upper_res.slope)
        lower_contribution_ratio: float = _get_contribution(lower_res.distance, lower_res.slope)

        if upper_contribution_ratio <= 0 and lower_contribution_ratio <= 0:
            return

        upper_subpixel = SubpixelContribution(
            color=color,
            distance_from_spec=distance,
            pixel_usage_ratio=upper_contribution_ratio,
        )

        lower_subpixel = SubpixelContribution(
            color=color,
            distance_from_spec=distance,
            pixel_usage_ratio=lower_contribution_ratio,
        )

        contribution = PixelContribution(
            upper_subpixel=upper_subpixel, lower_subpixel=lower_subpixel
        )

        self.screen_data[round(curr_screen_pos[1])][round(curr_screen_pos[0])] += [contribution]
