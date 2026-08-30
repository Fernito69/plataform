import math
from typing import TYPE_CHECKING

from constants import HALF_PIXEL, PI, PIXEL, QUARTER_PIXEL
from factories.theme import DEFAULT_CHAR, White
from model.base import Point2F
from model.theme import RGB
from three_d_renderer.model.base import PixelContribution, SubpixelContribution, Vertex3, WorldData
from three_d_renderer.three_d_renderer import ThreeDeeRenderer
from utils import (
    colored,
    distance_between_points,
    distance_from_line_to_point,
    get_line_equations,
    mix_colors,
    subtract_triplet,
)

if TYPE_CHECKING:
    from game import Game

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


# What's the max distance? from the middle to the corner -> √(.25^2+.5^2) -> 0.559
# We take that as 0% contribution, and 0 as 100%
DISTANCE_FROM_SUBPIXEL_CENTER_TO_CORNER = 0.559


# TODO: move this function elsewhere or make it static method
def _get_contribution(distance: float, slope: float | None) -> float:
    # Corrected by the 2/1 ratio between real x and real y
    # TODO: I'm assuming it's a linear relationship with the angle, maybe it's not.
    distance /= (1 + abs((math.atan(slope)) / (PI / 2))) if slope is not None else 2

    return max(
        1 - distance / DISTANCE_FROM_SUBPIXEL_CENTER_TO_CORNER,
        # (1 - distance),
        0,
    )


class LineRenderer(ThreeDeeRenderer):
    world_data: list[list[list[PixelContribution]]]

    def __init__(self, game: "Game"):
        ThreeDeeRenderer.__init__(self, game)
        self.reset_world_data()

    def _get_world_data(self) -> list[WorldData]:
        player = self.game.player3d

        if not player.curr_level:
            return []

        # Order vertices by closest to farthest and exclude those too far away to be rendered
        return [
            data
            for data in sorted(
                [
                    WorldData(
                        entity_idx=entity_idx,
                        entity=entity,
                        vertex=Vertex3(point=vertex, index=vertex_idx),
                        dist_vector=distance_between_points(vertex, player.position, entity=entity),
                    )
                    for entity_idx, entity in enumerate(player.curr_level.entities)
                    for vertex_idx, vertex in enumerate(entity.vertices)
                ],
                key=self._sort_vertices,
            )
            if data.dist_vector.distance < self.visibility_threshold
        ]

    def _sort_vertices(self, r: WorldData) -> float:
        # TODO: do right
        # connections = [
        #     c
        #     for c in self._curr_level.entities[r.entity_idx].vertex_connections
        #     if c[0] == r.vertex.index or c[1] == r.vertex.index
        # ]
        # sumaa: float = sum(self.screen_data[r.] for c1, c2 in connections)
        # divisor: float = len(connections) + 1
        # return (r.dist_vector.distance + sumaa) / divisor

        return r.dist_vector.distance

    def reset_world_data(self) -> None:
        self.world_data = []
        for y in range(self.display.curr_y_resolution):
            self.world_data.append([])
            for _ in range(self.display.curr_x_resolution):
                self.world_data[y].append([])

    def render(self):
        self.reset_world_data()
        world_data: list[WorldData] = self._get_world_data()

        if not (curr_level := self.game.player3d.curr_level):
            return

        # TODO: calculations should not be part of the rendering
        for entity in curr_level.entities:
            entity.calc_main_vertices(apply=True)
            entity.movement()

        for data in world_data:
            # 1) Take vertices and trace lines
            # 2) Figure out pixels the line goes through
            # 3) Figure out pixel_usage_ratio

            # Check all the other vertices this vertex is connected to
            connections = [c for c in data.entity.vertex_connections if c[0] == data.vertex.index]

            # Calc connecting lines
            for _, connecting_vertex_index in connections:
                curr_pixel_pos: Point2F = self._get_screen_projection(
                    subtract_triplet(data.vertex.point, self.game.player3d.position)
                )
                connecting_pixel_pos: Point2F = self._get_screen_projection(
                    subtract_triplet(
                        data.entity.vertices[connecting_vertex_index], self.game.player3d.position
                    )
                )

                # TODO: Wait, this doesn't necessarily mean the line it generates is not visible! This needs to be fixed
                if not self.display.is_in_screen(curr_pixel_pos) and not self.display.is_in_screen(
                    connecting_pixel_pos
                ):
                    continue

                self._compute_pixel_contributions(data, (curr_pixel_pos, connecting_pixel_pos))

        new_screen_matrix = self._screen_matrix_buffer

        # Fill in screen data!!!
        for x in range(self.display.curr_x_resolution):
            for y in range(self.display.curr_y_resolution):
                data = self.world_data[y][x]

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
        self.display.print_curr_screen(self.game.player3d)

    def _compute_pixel_contributions(self, data: WorldData, line: tuple[Point2F, Point2F]) -> None:
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
                    # color = data.entity.theme.color
                    # HACK: hardcoded colors
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
                            color=color,
                            data=data,
                        )

    def _add_contribution_to_screen(
        self, line: tuple[Point2F, Point2F], curr_screen_pos: Point2F, color: RGB, data: WorldData
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

        # TODO: this is cheap heuristics, do better
        upper_contribution_ratio: float = (
            _get_contribution(upper_res.distance, upper_res.slope)
            if not any(
                d.upper_subpixel.pixel_usage_ratio
                for d in self.world_data[round(y)][round(x)]
                if d.upper_subpixel.distance_from_spec > data.dist_vector.distance
                or d.upper_subpixel.vertex.index != data.vertex.index
                or d.upper_subpixel.entity_idx != data.entity_idx
            )
            else 0
        )
        lower_contribution_ratio: float = (
            _get_contribution(lower_res.distance, lower_res.slope)
            if not any(
                d.lower_subpixel.pixel_usage_ratio
                for d in self.world_data[round(y)][round(x)]
                if d.upper_subpixel.distance_from_spec > data.dist_vector.distance
                or d.upper_subpixel.vertex.index != data.vertex.index
                or d.lower_subpixel.entity_idx != data.entity_idx
            )
            else 0
        )

        if upper_contribution_ratio <= 0 and lower_contribution_ratio <= 0:
            return

        upper_subpixel = SubpixelContribution(
            color=color,
            distance_from_spec=data.dist_vector.distance,
            pixel_usage_ratio=upper_contribution_ratio,
            entity_idx=data.entity_idx,
            vertex=data.vertex,
        )

        lower_subpixel = SubpixelContribution(
            color=color,
            distance_from_spec=data.dist_vector.distance,
            pixel_usage_ratio=lower_contribution_ratio,
            entity_idx=data.entity_idx,
            vertex=data.vertex,
        )

        contribution = PixelContribution(
            upper_subpixel=upper_subpixel, lower_subpixel=lower_subpixel
        )

        self.world_data[round(curr_screen_pos[1])][round(curr_screen_pos[0])] += [contribution]
